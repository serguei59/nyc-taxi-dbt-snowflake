# 📊 Data Quality – NYC Taxi ETL + dbt

**Navigation:**  
[Home](./index.md) • [Setup](./setup.md) • [Ingestion](./ingestion.md) • [Transformations](./transformations.md)

---

## 1️⃣ Data Quality Objectives (from the brief)

This page defines the **data quality objectives** for the NYC Taxi ETL + dbt project, aligned with the project brief:

| Objective | Description | Importance for future use |
|----------|------------|----------------------------|
| **Consistent TRIP_DISTANCE** | Ensure trip distances are positive and realistic | ML, analytics, anomaly detection |
| **TOTAL_AMOUNT ≥ 0** | Verify total fare amount is correct | Revenue, dashboards, KPI calculations |
| **Business key duplicates** | Detect duplicates on transaction keys (pickup/dropoff, vendor, timestamp, location) | Prevent bias in ML and reporting |
| **Temporal consistency** | Pickup < Dropoff and valid timestamps | Time series, hourly aggregations |
| **Geographical integrity** | Valid PULOCATIONID and DOLOCATIONID | Map visualizations, zoning, ZTC |
| **Plausible TIP %** | Tip percentage coherent with fare_amount | Analytics and behavioral studies |

---

## 2️⃣ dbt-based Solutions

### 🔹 Native dbt tests

- **`not_null`** and **`unique`** on critical columns (`TRIP_DISTANCE`, `TOTAL_AMOUNT`, `PULOCATIONID`, `DOLOCATIONID`)  
- **`accepted_range`** to validate numerical values (distance, amount)  
- Severity configuration:  
  - `error` → stop pipeline if critical violation  
  - `warn` → log warning but continue pipeline  
> Reference: [dbt severity](https://docs.getdbt.com/reference/resource-configs/severity)

### 🔹 dbt-utils tests

- Package dbt-utils ([GitHub](https://github.com/dbt-labs/dbt-utils)) for reusable tests:  
  - `unique_combination_of_columns` → ensure uniqueness across multiple columns (business key)  
  - `surrogate_key` → generate and validate unique keys for transformed tables  

### 🔹 dbt-expectations tests

- Package dbt-expectations ([GitHub](https://github.com/metaplane/dbt-expectations)) provides Great Expectations-style assertions:  
  - `expect_column_values_to_be_between`  
  - `expect_column_values_to_not_be_null`  
  - `expect_column_mean_to_be_between`  
- Allows **more complex and readable data quality checks**  

### 🔹 Singular / custom SQL tests

- Custom SQL tests for **business KPIs** and advanced controls:  
  - Plausible TIP_PCT (`TIP_AMOUNT / FARE_AMOUNT`)  
  - Maximum realistic trip distances (outlier detection)  
  - Trip volume by zone/hour → anomaly detection  

---

## 3️⃣ Reporting & Monitoring

- Each test result is **automatically collected** by dbt and can be exported to:  
  - CSV / Excel (`post_ingestion_report.xlsx`) for historical tracking  
  - Detailed logs by severity in `logs/`  
- GitHub Actions ensure tests run automatically after ingestion and transformations.  

---

## 4️⃣ Best Practices

| Aspect | Implementation |
|--------|----------------|
| Version control | All dbt tests are versioned with the project |
| Reproducibility | Automated tests and ETL pipelines via GitHub Actions |
| Extensibility | Add new metrics or tests in `schema.yml` or `tests/` |
| Auditability | Logs and reports with severity and timestamps |

---

## 5️⃣ References

- [dbt-expectations GitHub](https://github.com/metaplane/dbt-expectations)  
- [dbt-utils GitHub](https://github.com/dbt-labs/dbt-utils)  
- [dbt severity](https://docs.getdbt.com/reference/resource-configs/severity)  
- [dbt Data Tests](https://docs.getdbt.com/docs/build/data-tests)

---

**Navigation:**  
[Home](./index.md) • [Setup](./setup.md) • [Ingestion](./ingestion.md) • [Transformations](./transformations.md)
