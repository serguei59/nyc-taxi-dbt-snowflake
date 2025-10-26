import os
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

# Connexion Snowflake
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

# 1. Créer la table RAW si elle n’existe pas
create_table_sql = """
CREATE TABLE IF NOT EXISTS RAW.yellow_taxi_trips (
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
);
"""
cursor.execute(create_table_sql)
print("🛠️ Table RAW.yellow_taxi_trips créée (si elle n'existait pas)")


# 1.b Créer la table STAGING si elle n’existe pas
create_staging_sql = """
CREATE TABLE IF NOT EXISTS RAW.yellow_taxi_trips_staging (
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
    airport_fee FLOAT
);
"""
cursor.execute(create_staging_sql)
print("🛠️ Table RAW.yellow_taxi_trips_staging créée (si elle n'existait pas)")


# 2. Parcours des fichiers Parquet
parquet_dir = "ingestion/data"
for file in os.listdir(parquet_dir):
    if file.endswith(".parquet"):
        print(f"\n🚀 Traitement du fichier : {file}")
        df = pd.read_parquet(os.path.join(parquet_dir, file))

        # Harmonisation des colonnes
        df.columns = [col.lower() for col in df.columns]
        df.rename(columns={
            "vendorid": "vendor_id",
            "tpep_pickup_datetime": "pickup_datetime",
            "tpep_dropoff_datetime": "dropoff_datetime",
            "ratecodeid": "rate_code_id",
            "pulocationid": "pu_location_id",
            "dolocationid": "do_location_id",
            "airport_fee": "airport_fee"  # au cas où présent
        }, inplace=True)

        # Si 'airport_fee' manquant, on l’ajoute avec NaN
        if 'airport_fee' not in df.columns:
            df['airport_fee'] = pd.NA

        # Ajout colonne ingestion_timestamp
        #df["ingestion_timestamp"] = datetime.now(timezone.utc)

        # Reset index pour write_pandas
        df.reset_index(drop=True, inplace=True)

        print("🧱 Colonnes prêtes :", df.columns.tolist())

        # 3. Charger dans la table tampon RAW.yellow_taxi_trips_staging
        temp_table = "yellow_taxi_trips_staging"
        success, nchunks, nrows, _ = write_pandas(
            conn, df, table_name=temp_table, schema="RAW", overwrite=True
        )
        if not success:
            raise RuntimeError("❌ write_pandas failed: staging table not written.")
        print(f"✅ {nrows} lignes chargées dans RAW.{temp_table}")

        # 4. MERGE idempotent dans RAW.yellow_taxi_trips
        merge_sql = f"""
        MERGE INTO RAW.yellow_taxi_trips AS target
        USING RAW.{temp_table} AS source
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

        # 5. Journalisation : combien ont été insérés ?
        print("✅ MERGE terminé avec succès — lignes nouvelles insérées si non déjà présentes (idempotent)")

        # count_inserted = cursor.execute("SELECT row_count FROM table(result_scan(last_query_id()))").fetchone()[0]
        #print(f"📊 MERGE terminé : {count_inserted} lignes insérées depuis {file}")
        #lignes_ignorees = nrows - count_inserted
        #print(f"⚠️ {lignes_ignorees} lignes ignorées (déjà présentes)") """

        # 6. Table staging : garder ou supprimer ?
        print(f"🧪 La table RAW.{temp_table} a été conservée pour débogage.")
        print(f"👉 Vous pouvez la supprimer manuellement avec : DROP TABLE RAW.{temp_table};")

cursor.close()
conn.close()
print("\n🎉 Tous les fichiers ont été traités avec succès.")
