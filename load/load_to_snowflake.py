import os
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Connexion à Snowflake (identifiants fournis par .env)
conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
    role=os.getenv("SNOWFLAKE_ROLE"),
)

# DDL FIRST : Création explicite de la table staging AVANT l'écriture
# Justification : on évite que write_pandas essaie d'inférer les types ou noms de colonnes (source de bugs).
create_staging_sql = """
CREATE TABLE IF NOT EXISTS RAW.yellow_taxi_trips_staging (
    vendor_id INTEGER,
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
conn.cursor().execute(create_staging_sql)

# Répertoire contenant les fichiers parquet
parquet_dir = "ingestion/data"

for file in os.listdir(parquet_dir):
    if file.endswith(".parquet"):
        print(f"🚀 Loading: {file}")
        df = pd.read_parquet(os.path.join(parquet_dir, file))
        print("Colonnes :", df.columns.tolist())

        # Nettoyage et standardisation
        df.columns = [col.lower() for col in df.columns]  # standardise pour renommage
        print("Colonnes  nettoyées:", df.columns.tolist())

        # Dédoublonnage sur les clés métiers pertinentes
        df.drop_duplicates(
            subset=["vendorid", "tpep_pickup_datetime", "pulocationid", "dolocationid"],
            inplace=True
        )

        # reset index pour éviter le warning Snowflake
        df.reset_index(drop=True, inplace=True)

        # Renommage des colonnes pour correspondre au DDL Snowflake
        df.rename(columns={
            "vendorid": "vendor_id",
            "tpep_pickup_datetime": "pickup_datetime",
            "tpep_dropoff_datetime": "dropoff_datetime",
            "ratecodeid": "rate_code_id",
            "pulocationid": "pu_location_id",
            "dolocationid": "do_location_id",
            "airport_fee": "airport_fee"
        }, inplace=True)
        print("Colonnes renommées Snowflake:", df.columns.tolist())

        # WRITE_PANDAS avec auto_create_table=False
        # Justification technique :
        #    - La table a été définie en SQL (DDL first) avec des noms **en minuscules non quotés**
        #    - Si auto_create_table=True (par défaut), Snowflake tente de créer une nouvelle table
        #      avec des noms **quotés et sensibles à la casse** ("vendor_id" ≠ VENDOR_ID)
        #    - Cela provoque une erreur SQL (invalid identifier)
        #    - On force donc auto_create_table=False pour respecter le DDL défini
        success, nchunks, nrows, _ = write_pandas(
            conn,
            df,
            table_name="yellow_taxi_trips_staging",
            schema="RAW",
            overwrite=True,
            auto_create_table=False  # ← 🔒 Sécurise l’exécution et évite les erreurs de casse
        )

        if not success:
            raise RuntimeError("❌ write_pandas failed: staging table not written.")

        print(f"✅ {nrows} rows written to staging from {file}")

        # Requête MERGE pour ingestion incrémentale dans la table cible
        # Justification : évite les doublons en insérant uniquement les nouvelles lignes
        merge_query = """
        MERGE INTO RAW.yellow_taxi_trips AS target
        USING RAW.yellow_taxi_trips_staging AS source
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
        conn.cursor().execute(merge_query)
        print("✅ MERGE completed successfully.")
