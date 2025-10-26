# ✅ Ingestion Pipeline: NYC Yellow Taxi Data

This document outlines the complete ingestion pipeline for NYC Yellow Taxi data, from local source acquisition to secure loading into Snowflake.

---

## 🔁 Step 1 — From Source to Secured Data Directory

### 📥 Source Acquisition
The raw `.parquet` files are sourced from the NYC Yellow Taxi public datasets.

### 📁 Secure Storage
All ingested `.parquet` files are stored under a dedicated local directory:

```
ingestion/data/
```

This directory is excluded from version control via the `.gitignore` file to prevent sensitive or heavy data from being tracked.

### 📌 Environment Variable
The following environment variable is declared in `.env` to reference the data path:

```
DATA_DIR=ingestion/parquets/
```

This ensures reproducibility and avoids hardcoded paths.

---

## 🚀 Step 2 — Load Data to Snowflake

### 🔧 Python Script

A Python script is used to automate the loading of each `.parquet` file to the `RAW.yellow_taxi_trips` table in Snowflake using the `snowflake-connector-python` and `write_pandas` utilities.

Key script features:
- Reads `.env` for credentials (`SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, etc.)
- Connects to Snowflake using `snowflake.connector.connect(...)`
- Creates the table if not already present
- Loads all `.parquet` files from `DATA_DIR` using a loop

```python
import os
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
    role=os.getenv("SNOWFLAKE_ROLE"),
)

cur = conn.cursor()

cur.execute("""
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
        congestion_surcharge FLOAT
    )
""")

parquet_dir = "ingestion/parquets"
for file in os.listdir(parquet_dir):
    if file.endswith(".parquet"):
        print(f"Chargement de : {file}")
        df = pd.read_parquet(os.path.join(parquet_dir, file))
        write_pandas(conn, df, table_name="yellow_taxi_trips", schema="RAW")
```

---

## ⚙️ Why DDL First? (Pro Practice)

> Ingestion must follow a strict **DDL → DML** separation.

| Type | Purpose |
|------|---------|
| **DDL (Data Definition Language)** | Define structure (e.g., tables, schemas) |
| **DML (Data Manipulation Language)** | Manipulate content (e.g., INSERT, UPDATE) |

### ✅ Advantages of DDL-first approach:

- Ensures **clean structure before data**.
- Makes the project **reproducible** and compatible with **CI/CD pipelines**.
- Enables version control and **auditability** of schema changes.
- Prevents accidental writes into undefined targets.


The script also ensures idempotency and transparency via logging (`print(f"Chargement de : {file}")`).

---

## ✅ Summary

- ✔️ Raw data securely stored in `ingestion/data/`
- ✔️ Data excluded from Git for safety
- ✔️ Ingestion script loads `.parquet` files to `RAW.yellow_taxi_trips` in Snowflake
- ✔️ Secrets managed via `.env` file
- ✔️ DDL First approach
