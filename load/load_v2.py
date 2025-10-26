import os
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv

# 🔐 Chargement des variables d'environnement (.env)
load_dotenv()

# 📡 Connexion à Snowflake
conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
    role=os.getenv("SNOWFLAKE_ROLE"),
)
cursor = conn.cursor()

# 📌 Nom de la table finale et de la staging
table_finale = "yellow_taxi_trips"
table_staging = f"{table_finale}_staging"
schema = "RAW"

# 1️⃣ Création des tables si elles n'existent pas
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {schema}.{table_finale} (
    vendor_id STRING,
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    passenger_count INTEGER,
    trip_distance FLOAT,
    rate_code_id INTEGER,
    store_and_fwd_flag STRING,
    pu_location_id INTEGER,
    do_location_id INTEGER,
    payment_type INTEGER,
    fare_amount FLOAT,
    extra FLOAT,
    mta_tax FLOAT,
    tip_amount FLOAT,
    tolls_amount FLOAT,
    improvement_surcharge FLOAT,
    total_amount FLOAT,
    congestion_surcharge FLOAT,
    airport_fee FLOAT,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
""")
print(f"✅ Table {schema}.{table_finale} vérifiée ou créée.")

cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {schema}.{table_staging} LIKE {schema}.{table_finale}
""")
print(f"✅ Table {schema}.{table_staging} vérifiée ou créée.")

# 2️⃣ Parcours des fichiers Parquet
parquet_dir = "ingestion/data"
for file in os.listdir(parquet_dir):
    if not file.endswith(".parquet"):
        continue

    print(f"\n🚀 Traitement du fichier : {file}")
    df = pd.read_parquet(os.path.join(parquet_dir, file))

    # 3️⃣ Harmonisation des colonnes
    df.columns = [col.lower() for col in df.columns]
    df.rename(columns={
        "vendorid": "vendor_id",
        "tpep_pickup_datetime": "pickup_datetime",
        "tpep_dropoff_datetime": "dropoff_datetime",
        "ratecodeid": "rate_code_id",
        "pulocationid": "pu_location_id",
        "dolocationid": "do_location_id",
    }, inplace=True)

    # 4️⃣ Ajout de colonnes manquantes pour correspondre à la table cible
    colonnes_cibles = [
        "vendor_id", "pickup_datetime", "dropoff_datetime", "passenger_count",
        "trip_distance", "rate_code_id", "store_and_fwd_flag", "pu_location_id",
        "do_location_id", "payment_type", "fare_amount", "extra", "mta_tax",
        "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount",
        "congestion_surcharge", "airport_fee"
    ]
    for col in colonnes_cibles:
        if col not in df.columns:
            df[col] = pd.NA

    # ⚙️ Réorganisation des colonnes dans l’ordre
    df = df[colonnes_cibles]

    # 5️⃣ Envoi vers la table staging
    df.reset_index(drop=True, inplace=True)
    success, nchunks, nrows, _ = write_pandas(
        conn, df, table_name=table_staging, schema=schema, overwrite=True
    )
    if not success:
        raise RuntimeError("❌ write_pandas failed.")

    print(f"✅ {nrows} lignes chargées dans {schema}.{table_staging}")

    # 6️⃣ MERGE idempotent dans la table finale
    merge_sql = f"""
    MERGE INTO {schema}.{table_finale} AS target
    USING {schema}.{table_staging} AS source
    ON  target.vendor_id = source.vendor_id
        AND target.pickup_datetime = source.pickup_datetime
        AND target.pu_location_id = source.pu_location_id
        AND target.do_location_id = source.do_location_id
    WHEN NOT MATCHED THEN
        INSERT (
            vendor_id, pickup_datetime, dropoff_datetime, passenger_count,
            trip_distance, rate_code_id, store_and_fwd_flag, pu_location_id,
            do_location_id, payment_type, fare_amount, extra, mta_tax,
            tip_amount, tolls_amount, improvement_surcharge, total_amount,
            congestion_surcharge, airport_fee
        )
        VALUES (
            source.vendor_id, source.pickup_datetime, source.dropoff_datetime, source.passenger_count,
            source.trip_distance, source.rate_code_id, source.store_and_fwd_flag, source.pu_location_id,
            source.do_location_id, source.payment_type, source.fare_amount, source.extra, source.mta_tax,
            source.tip_amount, source.tolls_amount, source.improvement_surcharge, source.total_amount,
            source.congestion_surcharge, source.airport_fee
        );
    """
    cursor.execute(merge_sql)
    print("🔁 MERGE effectué avec succès (idempotent)")

    # 7️⃣ Optionnel : garder ou supprimer la table staging ?
    print(f"🧪 La table {schema}.{table_staging} est conservée pour débogage.")
    print(f"👉 Vous pouvez la supprimer avec : DROP TABLE {schema}.{table_staging};")

# ✅ Nettoyage final
cursor.close()
conn.close()
print("\n🎉 Tous les fichiers ont été traités avec succès.")
