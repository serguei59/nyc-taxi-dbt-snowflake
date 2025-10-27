# 🧩 Data Ingestion Pipeline – NYC Taxi Data (Snowflake + Python)

This module manages the **automated and incremental ingestion** of `.parquet` files into **Snowflake**, using data from the **NYC Taxi & Limousine Commission** public dataset.

---

## 🗂️ 1. General Architecture

```
📁 docs/
 ┣ 📘 setup.md
 ┗ 📘 ingestion.md             → this documentation
 📁 extract/
 ┣ 📁 data
 ┣ 📁 sql
 ┣ 📜 download_parquet.py      → data extraction from public source 
 📁 load/
 ┣ 📜 merge_dynamic.py         → main ingestion script
 ┣ 📜 snowflake_utils.py       → SQL and connection helpers
```

Data is stored in two Snowflake tables under the **RAW schema**:

- `RAW.YELLOW_TAXI_TRIPS` → main consolidated table  
- `RAW.BUFFER_YELLOW_TAXI_TRIPS` → temporary buffer table used for merges

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

## 🚀 2. Step 1: Extract `.parquet` Files

The monthly taxi trip data is hosted publicly at:

📦 **Base URL:**  
`https://d37ci6vzurychx.cloudfront.net/trip-data/`

**Example files:**
- `yellow_tripdata_2024-01.parquet`
- `yellow_tripdata_2024-02.parquet`
- `yellow_tripdata_2024-03.parquet`

### 🧠 Script: `download_parquet.py`
Automatically downloads `.parquet` files for a given date range and stores them in `data/`.

```bash
python extract/download_parquet.py --start 2024-01 --end 2025-10
```

**Features:**
- Parallel downloads (threaded)
- MD5 / file size verification
- Automatic duplicate handling
- Logs stored under `logs/download.log`

---

## ⚙️ 3. Step 2: Ingest into Snowflake

### 🎯 Objective
Load the `.parquet` files into Snowflake with **dynamic schema detection** and a **duplicate-safe MERGE** process.

### 🧩 Main script: `merge_dynamic.py`

**Script workflow:**
1. Reads `.parquet` files from the `data/` directory  
2. Creates Snowflake tables dynamically if they don’t exist  
3. Automatically adjusts schema (adds missing columns)  
4. Loads each file into the temporary buffer table  
5. Merges buffer into the main table using a multi-key business join:

   ```sql
   ON target.TPEP_PICKUP_DATETIME = source.TPEP_PICKUP_DATETIME
      AND target.TPEP_DROPOFF_DATETIME = source.TPEP_DROPOFF_DATETIME
      AND target.VENDORID = source.VENDORID
      AND target.PULOCATIONID = source.PULOCATIONID
      AND target.DOLOCATIONID = source.DOLOCATIONID
      AND target.PASSENGER_COUNT = source.PASSENGER_COUNT
      AND target.TRIP_DISTANCE = source.TRIP_DISTANCE
   ```

6. Updates existing records / inserts new ones  
7. **Cleans up the buffer table** after each merge

---

## 📊 4. Step 3: Post-Ingestion Data Quality Checks

After ingestion, a series of **data validation queries** are executed automatically to ensure data integrity:

| Check | Purpose | SQL Query |
|--------|----------|-----------|
| **TOTAL_ROWS** | Total number of rows in `RAW.YELLOW_TAXI_TRIPS` | `SELECT COUNT(*)` |
| **DUPLICATE_GROUPS** | Number of duplicate groups (same business key) | `HAVING COUNT(*) > 1` |
| **BUFFER_ROWS** | Ensures buffer table is empty after merge | `SELECT COUNT(*) FROM BUFFER` |
| **DISTANCE_STATS** | Monitors min/max/avg trip distance | `MIN, MAX, AVG(TRIP_DISTANCE)` |

**Example output:**
```
TOTAL_ROWS: 72726158
DUPLICATE_GROUPS: 1052627
BUFFER_ROWS: 0
DISTANCE_STATS: min=0, max=398608.6, avg=5.8
```

---

## 🧹 5. Cleanup and Resource Management

The `finally` block ensures that Snowflake resources are **always closed properly**, even if an exception occurs.

```python
finally:
    if cursor: cursor.close()
    if conn: conn.close()
    print("✅ Pipeline completed and connections closed.")
```

---

## 🧠 6. Best Practices Applied

| Aspect | Practice |
|---------|-----------|
| **Security** | Credentials stored in `.env` (never committed) |
| **Robustness** | Full exception handling (`try/except/finally`) |
| **Scalability** | Schema auto-adjustment on Snowflake |
| **Traceability** | SQL logs and validation checks after ingestion |
| **Performance** | Batch loading via `write_pandas` |
| **Quality** | Data integrity verified post-load |

---

## 🔍 7. Production Considerations

- Verify warehouse configuration (`NYC_TAXI_WH`)  
- Ensure the correct role (`ACCOUNTADMIN` / `SYSADMIN`) has access to `RAW` schema  
- Adjust warehouse size based on volume (`XSMALL` → `MEDIUM`)  
- Schedule automatic runs via **Airflow**, **Cron**, or **GitHub Actions**

---

## 🚀 8. Next Step: Data Transformation with DBT

After ingestion, transformations are managed using **DBT Core**.

**Model structure:**
- **staging/** → data cleaning (`stg_yellow_taxi_trips.sql`)
- **intermediate/** → business metrics and enrichments
- **marts/** → analytical aggregates (`daily_summary`, `zone_analysis`, `hourly_patterns`)

---

## 🧾 9. Full Pipeline Execution

### 🪄 Manual Run

```bash
# Step 1: download source data
python extract/download_parquet.py --start 2024-01 --end 2025-10

# Step 2: ingest to Snowflake
python load/merge_dynamic.py
```

### 🧰 Automated Run (Cron or GitHub Actions)

```bash
0 3 * * * cd /app/nyc-taxi-dbt-snowflake && python load/merge_dynamic.py >> logs/ingestion.log 2>&1
```

---

## 📚 10. Optional: Post-Ingestion CSV Report

An optional CSV report can be generated for ingestion quality history:

📄 `load/verifications/post_ingestion_report.csv`

| Date | Total Rows | Duplicates | Buffer | Min Dist | Max Dist | Avg Dist |
|------|-------------|-------------|---------|-----------|-----------|-----------|

---

## 🏁 Summary

| Step | Purpose | Status |
|------|----------|--------|
| Parquet Extraction | Automatic download from public dataset | ✅ |
| Snowflake Ingestion | Dynamic schema loading + safe merge | ✅ |
| Data Quality Checks | Volume and integrity validation | ✅ |
| Resource Cleanup | Always closes connections | ✅ |
| DBT Transformations | Cleaning, enrichment, aggregation | 🔜 (next phase) |

---

## 📌 Author & Maintenance

Maintained by **SBUASA**  
Project: *Data Engineering – Snowflake + DBT Core Pipeline*  
Current version: **v1.3.1**  
Last updated: *October 2025*
