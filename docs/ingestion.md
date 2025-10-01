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
for file in os.listdir(parquet_dir):
    if file.endswith(".parquet"):
        df = pd.read_parquet(os.path.join(parquet_dir, file))
        write_pandas(conn, df, table_name="yellow_taxi_trips", schema="RAW")
```

The script ensures idempotency and transparency via logging (`print(f"Chargement de : {file}")`).

---

## ✅ Summary

- ✔️ Raw data securely stored in `ingestion/data/`
- ✔️ Data excluded from Git for safety
- ✔️ Ingestion script loads `.parquet` files to `RAW.yellow_taxi_trips` in Snowflake
- ✔️ Secrets managed via `.env` file