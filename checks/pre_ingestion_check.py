# verifications/pre_ingestion_check.py
import os
import sys
import snowflake.connector

# Récupération des variables sensibles depuis les secrets / env
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE", "TRANSFORM")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "NYC_TAXI_WH_V2")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "NYC_TAXI_DB_V2")

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
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            role=SNOWFLAKE_ROLE,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE
        )
        cs = conn.cursor()
    except Exception as e:
        log(f"❌ Connection failed: {e}")
        sys.exit(1)
    
    # Vérifier warehouse
    log(f"Checking warehouse {SNOWFLAKE_WAREHOUSE}...")
    cs.execute(f"SHOW WAREHOUSES LIKE '{SNOWFLAKE_WAREHOUSE}'")
    if not cs.fetchall():
        log(f"❌ Warehouse {SNOWFLAKE_WAREHOUSE} does not exist!")
        sys.exit(1)

    # Vérifier database
    log(f"Checking database {SNOWFLAKE_DATABASE}...")
    cs.execute(f"SHOW DATABASES LIKE '{SNOWFLAKE_DATABASE}'")
    if not cs.fetchall():
        log(f"❌ Database {SNOWFLAKE_DATABASE} does not exist!")
        sys.exit(1)
    
    # Vérifier schemas
    for schema in [RAW_SCHEMA, STAGING_SCHEMA, FINAL_SCHEMA]:
        log(f"Checking schema {schema}...")
        cs.execute(f"SHOW SCHEMAS LIKE '{schema}' IN DATABASE {SNOWFLAKE_DATABASE}")
        if not cs.fetchall():
            log(f"❌ Schema {schema} does not exist!")
            sys.exit(1)

    # Vérifier tables RAW
    for table in RAW_TABLES:
        log(f"Checking RAW table {table}...")
        cs.execute(f"SHOW TABLES LIKE '{table}' IN SCHEMA {SNOWFLAKE_DATABASE}.{RAW_SCHEMA}")
        if not cs.fetchall():
            log(f"❌ Table {table} does not exist in {RAW_SCHEMA}!")
            sys.exit(1)

    # Vérifier droits (simple check)
    log("Checking role privileges on warehouse...")
    cs.execute(f"SHOW GRANTS TO ROLE {SNOWFLAKE_ROLE}")
    grants = cs.fetchall()
    warehouse_grants = [g for g in grants if g[2] == SNOWFLAKE_WAREHOUSE]
    if not warehouse_grants:
        log(f"❌ Role {SNOWFLAKE_ROLE} has no grants on warehouse {SNOWFLAKE_WAREHOUSE}!")

    log("✅ Pre-ingestion checks passed! Environment ready for ingestion.")
    cs.close()
    conn.close()

if __name__ == "__main__":
    main()
