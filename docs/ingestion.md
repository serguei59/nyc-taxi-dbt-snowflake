# 🧩 Data Ingestion Pipeline – NYC Taxi Data (Snowflake + Python)

This module handles the **automated and incremental ingestion** of `.parquet` files into **Snowflake**, using public NYC Taxi & Limousine Commission data.

---

## 🗂️ 1. General Architecture

```
📁 docs/
 ┣ 📘 index.md                → Home / Overview
 ┣ 📘 setup.md                → Snowflake & Workstation Setup
 ┗ 📘 ingestion.md            → this file
📁 extract/
 ┣ 📁 data
 ┣ 📁 sql
 ┣ 📜 download_parquet.py     → data extraction
📁 load/
 ┣ 📜 merge_dynamic.py        → ingestion & merge
 ┣ 📜 snowflake_utils.py      → SQL helpers
 ┗ 📜 verifications/
   ┗ 📜 writer_report_xlsx.py → ingestion report
```

Data is stored in **RAW schema tables**:

* `RAW.YELLOW_TAXI_TRIPS_V2` → main table
* `RAW.BUFFER_YELLOW_TAXI_TRIPS_V2` → temporary buffer table

---

## ⚙️ 2. DDL Before DML (Pro Practice)

> Strict **DDL → DML** separation is enforced.

| Type    | Purpose                       |
| ------- | ----------------------------- |
| **DDL** | Define table/schema structure |
| **DML** | Insert / update data          |

✅ Advantages:

* Clean and reproducible structure
* CI/CD friendly
* Auditable schema changes
* Prevents accidental writes

---

## 🚀 3. Step 1: Download `.parquet` Files

Base URL:
`https://d37ci6vzurychx.cloudfront.net/trip-data/`

Example:

* `yellow_tripdata_2024-01.parquet`
* `yellow_tripdata_2024-02.parquet`

Run script:

```bash
python extract/download_parquet.py --start 2024-01 --end 2025-10
```

**Features:**

* Parallel downloads
* MD5 / file size verification
* Duplicate handling
* Logs in `logs/download.log`

---

## ⚙️ 4. Step 2: Ingest into Snowflake

### 🧩 Script: `merge_dynamic.py`

Workflow:

1. Reads `.parquet` from `data/`
2. Creates tables dynamically if missing
3. Adjusts schema (adds missing columns)
4. Loads data to buffer table
5. Merges buffer → main table with multi-key join:

```sql
ON target.TPEP_PICKUP_DATETIME = source.TPEP_PICKUP_DATETIME
   AND target.TPEP_DROPOFF_DATETIME = source.TPEP_DROPOFF_DATETIME
   AND target.VENDORID = source.VENDORID
   AND target.PULOCATIONID = source.PULOCATIONID
   AND target.DOLOCATIONID = source.DOLOCATIONID
   AND target.PASSENGER_COUNT = source.PASSENGER_COUNT
   AND target.TRIP_DISTANCE = source.TRIP_DISTANCE
```

6. Updates existing rows / inserts new ones
7. Cleans buffer table after merge

---

## 📊 5. Step 3: Post-Ingestion Data Quality Checks

SQL checks executed automatically:

| Check                | Purpose                                  |
| -------------------- | ---------------------------------------- |
| **TOTAL_ROWS**       | Total rows in `RAW.YELLOW_TAXI_TRIPS_V2` |
| **DUPLICATE_GROUPS** | Duplicate business keys                  |
| **BUFFER_ROWS**      | Buffer table should be empty             |
| **DISTANCE_STATS**   | Min / Max / Avg trip distance            |

Results are **saved in Excel**:

```python
from verifications.writer_report_xlsx import write_merge_report
write_merge_report(file_name, rows_merged, status)
```

Each ingestion creates a **new row in `merge_report.xlsx`** for traceability.

---

## 🧹 6. Cleanup

```python
finally:
    cursor.close()
    conn.close()
    print("✅ Pipeline finished cleanly.")
```

---

## 🧠 7. Best Practices

* Credentials in `.env` (never committed)
* Full exception handling
* Auto schema adjustment
* SQL logs and verification
* Batch loading via `write_pandas`
* Post-load data integrity check

---

## 🔍 8. Production Considerations

* Verify warehouse & role access
* Adjust warehouse size (`XSMALL` → `MEDIUM`)
* Schedule automated runs via **GitHub Actions** or **Cron**

---

## 🚀 9. Next Step: DBT Transformations

After ingestion, **DBT Core** handles transformations:

* `staging/` → cleaning (`stg_yellow_taxi_trips.sql`)
* `intermediate/` → business metrics
* `marts/` → analytical aggregates (`daily_summary`, `zone_analysis`)

---

## 🏁 10. Execution Examples

### Manual Run

```bash
python extract/download_parquet.py --start 2024-01 --end 2025-10
python load/merge_dynamic.py
```

### Automated Run (GitHub Actions / Cron)

```bash
0 3 * * * cd /app/nyc-taxi-dbt-snowflake && python load/merge_dynamic.py >> logs/ingestion.log 2>&1
```

---
### Navigation
- [Home](./index.md)
- [3. Data Transformations (dbt)](./transformation.md)


## 📌 Author & Maintenance

Maintained by **SBUASA**
Project: *Data Engineering – Snowflake + DBT Pipeline*
Current version: **v1.3.2**
Last updated: *October 2025*
