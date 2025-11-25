import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import logging
import csv
from datetime import datetime

# --- allow root-level imports when executed from GitHub Actions ---
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from checks.writer_report_xlsx import save_ingestion_report_xlsx
from snowflake_utils import execute_sql


# 1️⃣ Chargement des variables d'environnement
load_dotenv()

# 2️⃣ Création du dossier logs si nécessaire
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "merge_pipeline.log"

# 3️⃣ Setup du logging
try:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
except Exception as e:
    print(f"⚠️ Logging setup failed: {e}")

# 4️⃣ Connexion à Snowflake
conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)
cursor = conn.cursor()

# 5️⃣ Fonctions auxiliaires (map_dtype, create_table_if_not_exists, update_table_schema...)

# Mapping type pandas -> Snowflake
def map_dtype(dtype: str, verbose: bool =False) -> str:
    """
    Mappe un type pandas en type Snowflake compatible.
    Affiche un log si verbose=True.
    """
    dtype_original = dtype  # pour log
    dtype = dtype.lower()

    # Mapping générique
    if any(kw in dtype for kw in ["object", "string"]):
        sf_type = "VARCHAR"
    elif any(kw in dtype for kw in ["int64", "int"]):
        sf_type = "NUMBER"
    elif any(kw in dtype for kw in ["float64", "float"]):
        sf_type = "FLOAT"
    elif "bool" in dtype:
        sf_type = "BOOLEAN"
    elif dtype.startswith("datetime"):
        sf_type = "TIMESTAMP_NTZ"
    else:
        sf_type = "VARCHAR"

    if verbose:
        print(f"[🔍 Mapping] Pandas dtype '{dtype_original}' ➝ Snowflake type '{sf_type}'")

    return sf_type

# Création de la table si elle n'existe pas
def create_table_if_not_exists(df, table_name, verbose: bool =False):
    cols = []
    for col in df.columns:
        pandas_dtype = str(df[col].dtype)
        snowflake_type = map_dtype(pandas_dtype, verbose=verbose)
        cols.append(f'"{col.upper()}" {snowflake_type}')

    columns_definition = ", ".join(cols)
    sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})'

    if verbose:
        print(f"[🛠️ SQL] {sql}")

    execute_sql(sql)

# Mise à jour du schéma si colonnes manquantes
#def update_table_schema(df: pd.DataFrame, table_name: str, verbose: bool = False):
#    try:
#        existing_cols = [row[0].upper() for row in execute_sql(f"DESC TABLE {table_name}")]
#    except:
#        existing_cols = []
#    for col in df.columns:
#        if col.upper() not in existing_cols:
#            pandas_dtype = str(df[col].dtype)
#            snowflake_type = map_dtype(pandas_dtype, verbose=verbose)
#            sql = f'ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {col.upper()} {snowflake_type}'
#            execute_sql(sql)
# Assure-toi que map_dtype(dtype, verbose=False) est définie plus haut
# Assure-toi que execute_sql(sql) est définie et renvoie cursor.fetchall()

def get_existing_columns_and_types(table_name: str):
    """
    Retourne un dict {COLUMN_NAME: DATA_TYPE} pour la table donnée (nom TABLE_SCHEMA.TABLE_NAME attendu
    ou juste TABLE_NAME si le schema par défaut est correctement configuré dans la connexion).
    """

    # Normalisation SCHEMA + TABLE
    if '.' not in table_name:
        schema = os.getenv('SNOWFLAKE_SCHEMA').upper()
        table = table_name.upper()
    else:
        parts = table_name.split('.')
        if len(parts) == 2:
            schema, table = parts[0].upper(), parts[1].upper()
        else:
            raise ValueError("table_name doit être 'TABLE' ou 'SCHEMA.TABLE'")
        
    # On interroge INFORMATION_SCHEMA pour avoir le type exact stocké en Snowflake
    sql = f"""
    SELECT COLUMN_NAME, DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = '{table_name.split('.')[-1].upper()}'
      AND TABLE_SCHEMA = '{os.getenv('SNOWFLAKE_SCHEMA').upper()}'
    """
    try:
        rows = execute_sql(sql)
        return {row[0].upper(): row[1].upper() for row in rows}
    except Exception as e:
        # Si la table n'existe pas ou autre, renvoie dict vide
        print(f"⚠️ Warning getting columns for {table_name}: {e}")
        return {}

def update_table_schema(df: pd.DataFrame, table_name: str, verbose: bool = False):
    """
    Compare les colonnes du DataFrame à la table Snowflake et ajoute les colonnes manquantes.
    - df: pandas.DataFrame (colonnes en lower_case recommandées)
    - table_name: chaîne, ex: "RAW.YELLOW_TAXI_TRIPS" ou "YELLOW_TAXI_TRIPS"
    - verbose: affiche des logs détaillés si True
    """
    # Normaliser le nom de la table en majuscules si nécessaire
    if '.' in table_name:
        table_name_sql = table_name.upper()
    else:
        table_name_sql = f"{os.getenv('SNOWFLAKE_SCHEMA').upper()}.{table_name.upper()}"


    existing = get_existing_columns_and_types(table_name_sql)

    if verbose:
        print(f"[INFO] Columns existing in {table_name_sql}: {list(existing.keys())}")

    to_add = []
    type_mismatches = []

    for col in df.columns:
        col_up = col.upper()
        pandas_dtype = str(df[col].dtype)
        target_type = map_dtype(pandas_dtype, verbose=False).upper()

        if col_up not in existing:
            to_add.append((col_up, target_type))
        else:
            snow_type = existing[col_up].upper()
            # On compare simplement et on logge la mismatch, on n'essaie pas de modifier automatiquement
            if snow_type != target_type:
                type_mismatches.append((col_up, snow_type, target_type))

    # Ajout des colonnes manquantes
    for col_name, sf_type in to_add:
        sql = f'ALTER TABLE {table_name_sql} ADD COLUMN IF NOT EXISTS "{col_name}" {sf_type}'
        if verbose:
            print(f"[SQL] {sql}")
        execute_sql(sql)
        print(f"➕ Added column {col_name} {sf_type} to {table_name_sql}")

    # Signaler les mismatches de type
    if type_mismatches:
        print("⚠️ Type mismatches detected (Snowflake_type vs detected_pandas_type):")
        for col_name, snow_type, detected in type_mismatches:
            print(f"   - {col_name}: {snow_type} (Snowflake)  |  {detected} (detected)")
        print("➡️ No automatic type conversion performed; review and alter types manually if needed.")

    if not to_add and not type_mismatches and verbose:
        print(f"[INFO] No schema changes required for {table_name_sql}")


# 6️⃣ Traitement des fichiers parquet
def process_parquet_files():
    table_final = "YELLOW_TAXI_TRIPS_V2"
    table_buffer = "BUFFER_YELLOW_TAXI_TRIPS_V2"

    # Récupère le chemin du dossier racine du projet (2 niveaux au-dessus de ce fichier)
    project_root = Path(__file__).resolve().parents[1]

    # Chemin absolu vers le dossier extract/data
    data_dir = project_root / "extract" / "data"

    print("📂 Fichier actuel :", __file__)
    print("📂 Racine projet  :", project_root)
    print("📂 Dossier data   :", data_dir)

    # Vérifie l'existence du dossier
    if not data_dir.exists():
        raise FileNotFoundError(f"❌ Le dossier {data_dir} n'existe pas.")

    # Recherche des fichiers .parquet
    files = list(data_dir.glob("*.parquet"))
    if not files:
        print("⚠️ Aucun fichier .parquet trouvé dans", data_dir)
        return
    
    print(f"✅ {len(files)} fichier(s) trouvé(s) :")
    for f in files:
        print("   -", f.name)
        df = pd.read_parquet(f)
        # Harmonisation colonnes
        df.columns = [col.upper() for col in df.columns]          

        # Suppression doublons
        before = len(df)
        df = df.drop_duplicates(
            subset=[
                "TPEP_PICKUP_DATETIME",
                "TPEP_DROPOFF_DATETIME",
                "VENDORID",
                "PULOCATIONID",
                "DOLOCATIONID",
                "PASSENGER_COUNT",
                "TOTAL_AMOUNT",
                "TRIP_DISTANCE"
            ],
            keep="first"
        )
        removed = before - len(df)
        print(f"🧹 {removed} duplicate rows removed before upload.")
        try:
            logging.info(f"{removed} duplicates removed from {f.name}")
        except Exception:
            pass

        # Création/mise à jour des tables
        create_table_if_not_exists(df, table_final)
        update_table_schema(df, table_final, verbose=True)
        create_table_if_not_exists(df, table_buffer)
        update_table_schema(df, table_buffer, verbose=True)

        # Insertion dans buffer
        success, _, nrows, _ = write_pandas(conn, df, table_buffer)
        if not success:
            print("❌ Échec insertion")
            continue
        print(f"✅ {nrows} lignes dans {table_buffer}")
        try:
            logging.info(f"{nrows} lignes insérées depuis {f.name}")
        except Exception:
            pass

        # MERGE dynamique
        cols_upper = [col.upper() for col in df.columns]
        merge_sql = f"""
        MERGE INTO {table_final} AS target
        USING {table_buffer} AS source
        ON target.TPEP_PICKUP_DATETIME = source.TPEP_PICKUP_DATETIME 
            AND target.TPEP_DROPOFF_DATETIME = source.TPEP_DROPOFF_DATETIME
            AND target.VENDORID = source.VENDORID
            AND target.PULOCATIONID = source.PULOCATIONID
            AND target.DOLOCATIONID = source.DOLOCATIONID
            AND target.PASSENGER_COUNT = source.PASSENGER_COUNT
            AND target.TOTAL_AMOUNT = source.TOTAL_AMOUNT
            AND target.TRIP_DISTANCE = source.TRIP_DISTANCE
        WHEN MATCHED THEN UPDATE SET {', '.join([f'target.{col} = source.{col}' for col in cols_upper])}
        WHEN NOT MATCHED THEN INSERT ({', '.join(cols_upper)})
        VALUES ({', '.join([f'source.{col}' for col in cols_upper])});
        """
        execute_sql(merge_sql)
        print("🔁 MERGE terminé\n")
        try:
            logging.info(f"MERGE terminé pour {f.name}")
        except Exception:
            pass

        # Vidage du buffer
        execute_sql(f"TRUNCATE TABLE {table_buffer}")
        print("🔁 BUFFER vidé\n")

""" # 7️⃣ Sauvegarde du report
def save_ingestion_report(stats: dict):
    report_dir = Path(__file__).parent / "verifications"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "post_ingestion_report.csv"

    headers = [
        "timestamp",
        "total_rows",
        "duplicate_groups",
        "buffer_rows",
        "min_distance",
        "max_distance",
        "avg_distance"
    ]

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        stats.get("TOTAL_ROWS", "N/A"),
        stats.get("DUPLICATE_GROUPS", "N/A"),
        stats.get("BUFFER_ROWS", "N/A"),
        stats.get("MIN_DISTANCE", "N/A"),
        stats.get("MAX_DISTANCE", "N/A"),
        stats.get("AVG_DISTANCE", "N/A"),
    ]

    write_header = not report_file.exists()
    with open(report_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(headers)
        writer.writerow(row)

    print(f"📊 Ingestion report saved to: {report_file}") """

# 8️⃣ Lancement principal
if __name__ == "__main__":
    try:
        process_parquet_files()

        print("\n📊 Vérification post-ingestion Snowflake...")
        sql_checks = {
            "TOTAL_ROWS": "SELECT COUNT(*) AS TOTAL_ROWS FROM RAW.YELLOW_TAXI_TRIPS_V2;",
            "DUPLICATE_GROUPS": """
                SELECT COUNT(*) AS DUPLICATE_GROUPS 
                FROM (
                    SELECT TPEP_PICKUP_DATETIME, TPEP_DROPOFF_DATETIME, VENDORID, PULOCATIONID, DOLOCATIONID,
                           COUNT(*) AS c
                    FROM RAW.YELLOW_TAXI_TRIPS_V2
                    GROUP BY 1,2,3,4,5
                    HAVING COUNT(*) > 1
                );
            """,
            "BUFFER_ROWS": "SELECT COUNT(*) AS BUFFER_ROWS FROM RAW.BUFFER_YELLOW_TAXI_TRIPS_V2;",
            "DISTANCE_STATS": """
                SELECT 
                    MIN(TRIP_DISTANCE) AS MIN_DISTANCE,
                    MAX(TRIP_DISTANCE) AS MAX_DISTANCE,
                    AVG(TRIP_DISTANCE) AS AVG_DISTANCE
                FROM RAW.YELLOW_TAXI_TRIPS_V2;
            """
        }

        results = {}
        for check_name, sql in sql_checks.items():
            result = execute_sql(sql)
            if check_name == "DISTANCE_STATS":
                results["MIN_DISTANCE"] = result[0][0] if result else None
                results["MAX_DISTANCE"] = result[0][1] if result else None
                results["AVG_DISTANCE"] = result[0][2] if result else None
            else:
                results[check_name] = result[0][0] if result else None
            print(f"{check_name}: {result[0][0] if result else 'N/A'}")

        save_ingestion_report_xlsx(results)

    except Exception as e:
        print(f"❌ Erreur pendant le processus d'ingestion: {e}")

    finally:
        cursor.close()
        conn.close()
        print("✅ Pipeline terminé proprement (Snowflake fermé, logs à jour).")
