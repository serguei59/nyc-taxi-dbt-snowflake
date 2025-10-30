# verifications/pre_ingestion_check.py
import os
import sys
import snowflake.connector

# Récupération des variables sensibles depuis les secrets / env
SNOW_USER = os.getenv("SNOW_USER")
SNOW_PASSWORD = os.getenv("SNOW_PASSWORD")
SNOW_ACCOUNT = os.getenv("SNOW_ACCOUNT")
SNOW_ROLE = os.getenv("SNOW_ROLE", "TRANSFORM")
SNOW_WAREHOUSE = os.getenv("SNOW_WAREHOUSE", "NYC_TAXI_WH_V2")
SNOW_DATABASE = os.getenv("SNOW_DATABASE", "NYC_TAXI_DB_V2")

# Tables RAW attendues
RAW_TABLES = ["BUFFER_YELLOW_TAXI_TRIPS_V2", "YELLOW_TAXI_TRIPS_V2"]
RAW_SCHEMA = "RAW"
STAGING_SCHEMA = "STAGING"
FINAL_SCHEMA = "FINAL"

def log(msg):
    print(f"[CHECK] {msg}")

def main():
    log("Connecting to Snowflake...")
    try:
        conn = snowflake.connector.connect(
            user=SNOW_USER,
            password=SNOW_PASSWORD,
            account=SNOW_ACCOUNT,
            role=SNOW_ROLE,
            warehouse=SNOW_WAREHOUSE,
            database=SNOW_DATABASE
        )
        cs = conn.cursor()
    except Exception as e:
        log(f"❌ Connection failed: {e}")
        sys.exit(1)
    
    # Vérifier warehouse
    log(f"Checking warehouse {SNOW_WAREHOUSE}...")
    cs.execute(f"SHOW WAREHOUSES LIKE '{SNOW_WAREHOUSE}'")
    if not cs.fetchall():
        log(f"❌ Warehouse {SNOW_WAREHOUSE} does not exist!")
        sys.exit(1)

    # Vérifier database
    log(f"Checking database {SNOW_DATABASE}...")
    cs.execute(f"SHOW DATABASES LIKE '{SNOW_DATABASE}'")
    if not cs.fetchall():
        log(f"❌ Database {SNOW_DATABASE} does not exist!")
        sys.exit(1)
    
    # Vérifier schemas
    for schema in [RAW_SCHEMA, STAGING_SCHEMA, FINAL_SCHEMA]:
        log(f"Checking schema {schema}...")
        cs.execute(f"SHOW SCHEMAS LIKE '{schema}' IN DATABASE {SNOW_DATABASE}")
        if not cs.fetchall():
            log(f"❌ Schema {schema} does not exist!")
            sys.exit(1)

    # Vérifier tables RAW
    for table in RAW_TABLES:
        log(f"Checking RAW table {table}...")
        cs.execute(f"SHOW TABLES LIKE '{table}' IN SCHEMA {SNOW_DATABASE}.{RAW_SCHEMA}")
        if not cs.fetchall():
            log(f"❌ Table {table} does not exist in {RAW_SCHEMA}!")
            sys.exit(1)

    # Vérifier droits (simple check)
    log("Checking role privileges on warehouse...")
    cs.execute(f"SHOW GRANTS TO ROLE {SNOW_ROLE}")
    grants = cs.fetchall()
    warehouse_grants = [g for g in grants if g[2] == SNOW_WAREHOUSE]
    if not warehouse_grants:
        log(f"❌ Role {SNOW_ROLE} has no grants on warehouse {SNOW_WAREHOUSE}!")

    log("✅ Pre-ingestion checks passed! Environment ready for ingestion.")
    cs.close()
    conn.close()

if __name__ == "__main__":
    main()
