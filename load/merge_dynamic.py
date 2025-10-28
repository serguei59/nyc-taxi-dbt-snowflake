import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import logging
from snowflake_utils import execute_sql
import csv
from datetime import datetime

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
# … (garde toutes tes fonctions déjà définies ici, inchangées) …

# 6️⃣ Traitement des fichiers parquet
def process_parquet_files():
    table_final = "YELLOW_TAXI_TRIPS"
    table_buffer = "BUFFER_YELLOW_TAXI_TRIPS"

    data_dir = Path(__file__).parent / "extract/data"
    files = list(data_dir.glob("*.parquet"))
    if not files:
        print("⚠️ Aucun fichier .parquet trouvé dans extract/data/")
        return

    for file in files:
        print(f"🚀 Fichier : {file.name}")
        df = pd.read_parquet(file)

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
            logging.info(f"{removed} duplicates removed from {file.name}")
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
            logging.info(f"{nrows} lignes insérées depuis {file.name}")
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
            logging.info(f"MERGE terminé pour {file.name}")
        except Exception:
            pass

        # Vidage du buffer
        execute_sql(f"TRUNCATE TABLE {table_buffer}")
        print("🔁 BUFFER vidé\n")

# 7️⃣ Sauvegarde du report
def save_ingestion_report(stats: dict):
    report_dir = Path(__file__).parent / "load/verifications"
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

    print(f"📊 Ingestion report saved to: {report_file}")

# 8️⃣ Lancement principal
if __name__ == "__main__":
    try:
        process_parquet_files()

        print("\n📊 Vérification post-ingestion Snowflake...")
        sql_checks = {
            "TOTAL_ROWS": "SELECT COUNT(*) AS TOTAL_ROWS FROM RAW.YELLOW_TAXI_TRIPS;",
            "DUPLICATE_GROUPS": """
                SELECT COUNT(*) AS DUPLICATE_GROUPS 
                FROM (
                    SELECT TPEP_PICKUP_DATETIME, TPEP_DROPOFF_DATETIME, VENDORID, PULOCATIONID, DOLOCATIONID,
                           COUNT(*) AS c
                    FROM RAW.YELLOW_TAXI_TRIPS
                    GROUP BY 1,2,3,4,5
                    HAVING COUNT(*) > 1
                );
            """,
            "BUFFER_ROWS": "SELECT COUNT(*) AS BUFFER_ROWS FROM RAW.BUFFER_YELLOW_TAXI_TRIPS;",
            "DISTANCE_STATS": """
                SELECT 
                    MIN(TRIP_DISTANCE) AS MIN_DISTANCE,
                    MAX(TRIP_DISTANCE) AS MAX_DISTANCE,
                    AVG(TRIP_DISTANCE) AS AVG_DISTANCE
                FROM RAW.YELLOW_TAXI_TRIPS;
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

        save_ingestion_report(results)

    except Exception as e:
        print(f"❌ Erreur pendant le processus d'ingestion: {e}")

    finally:
        cursor.close()
        conn.close()
        print("✅ Pipeline terminé proprement (Snowflake fermé, logs à jour).")
