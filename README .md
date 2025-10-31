# ❄️ Full Snowflake + dbt Data Pipeline

## 🧭 Overview
This repository provides a complete **end-to-end data engineering workflow** built around **Snowflake**, **Python ETL**, and **dbt** transformations — fully automated via **GitHub Actions**.

The pipeline covers:
1. 🔧 **Snowflake setup** – initializes database, schema, roles, and warehouses.
2. 🚀 **Python ETL** – downloads and ingests data dynamically.
3. 🧩 **dbt transformations** – executes data models, tests, and documentation generation.

The workflow can be **manually triggered** or run on each push to `dev` or `main`.

---

## ⚙️ Workflow Execution

### 🔹 Trigger
You can launch the pipeline manually from **GitHub Actions → Full ETL + dbt Pipeline → Run workflow**.

It will:
1. Create/refresh your Snowflake environment (`clean_install_nyc_taxi_db_v2.sql`).
2. Run the ETL scripts (download + merge dynamic).
3. Execute dbt transformations and generate documentation.

---

## 🧱 Repository Structure

```
├── extract/
│   ├── sql/
│   │   └── clean_install_nyc_taxi_db_v2.sql
│   ├── data/
│   └── download_parquet.py
├── load/
│   └── merge_dynamic.py
├── verifications/
│   ├── pre_ingestion_check.py
│   └── writer_report_xslx.py
├── nyc_taxi_dbt_snowflake/
│   ├── models/
│   ├── seeds/
│   ├── tests/
│   └── dbt_project.yml
├── .github/
│   └── workflows/
│       └── full_etl_dbt_pipeline.yml
└── README.md
```

---

## 🔑 Environment Variables and GitHub Secrets

The workflow relies on **8 environment variables** securely stored as **GitHub Secrets**.

| Environment Variable | Description | Example | GitHub Secret |
|----------------------|--------------|----------|----------------|
| `SNOWFLAKE_ACCOUNT` | Snowflake account name | `CAHMYND-AO09940` | ✅ Yes |
| `SNOWFLAKE_USER` | Admin user for setup | `PY52096` | ✅ Yes |
| `SNOWFLAKE_PASSWORD` | Admin password | `********` | ✅ Yes |
| `SNOWFLAKE_ROLE` | Role for setup | `ACCOUNTADMIN` | ✅ Yes |
| `SNOWFLAKE_WAREHOUSE` | Warehouse name | `NYC_TAXI_WH_V2` | ✅ Yes |
| `SNOWFLAKE_DATABASE` | Database name | `NYC_TAXI_DB_V2` | ✅ Yes |
| `SNOWFLAKE_SCHEMA` | Default schema | `PUBLIC` | ✅ Yes |
| `DBT_PASSWORD` | Password for DBT user (from SQL script) | `Password123!` | ✅ Yes |

👉 You can define these in **Repository → Settings → Secrets and variables → Actions → New repository secret**.

---

## 🧰 Manual SnowSQL Connection (for debugging)

You can connect to your Snowflake instance using **SnowSQL CLI**:

```bash
snowsql -a CAHMYND-AO09940         -u PY52096         -r ACCOUNTADMIN         -w NYC_TAXI_WH_V2         -d NYC_TAXI_DB_V2
```

To test the dbt user connection:

```bash
snowsql -a CAHMYND-AO09940         -u DBT         -p 'Password123!'         -r TRANSFORM         -w NYC_TAXI_WH_V2         -d NYC_TAXI_DB_V2
```

---

## 🔄 GitHub Actions Workflow Summary

| Step | Description | Role Used |
|------|--------------|------------|
| 🧱 `snowflake_setup` | Initializes Snowflake (roles, DB, schema) | `ACCOUNTADMIN` |
| 🚀 `python_etl` | Executes ETL scripts (download, merge, verify) | `TRANSFORM` |
| 🧩 `dbt` | Runs dbt models, tests, and generates documentation | `TRANSFORM` |

The workflow YAML is stored in:  
[`/.github/workflows/full_etl_dbt_pipeline.yml`](./.github/workflows/full_etl_dbt_pipeline.yml)

---

## 📊 Outputs & Artifacts

After a successful run, you’ll find:

| Artifact | Location | Description |
|-----------|-----------|--------------|
| ETL logs | `/logs/` | Ingestion diagnostics |
| Reports | `/verifications/` | Excel-based quality reports |
| dbt docs | `/artifacts/dbt_docs/` | Auto-generated HTML documentation (published via GitHub Pages) |

---

## 🌐 Publishing Documentation (GitHub Pages)

To publish your dbt or project documentation:

1. Go to **Settings → Pages**
2. Select source: `main` branch
3. Choose folder: `/docs`

You can copy your dbt docs to this folder automatically:

```bash
mkdir -p docs/dbt_docs
cp -r target/* docs/dbt_docs/
```

Then, your docs will be available at:
```
https://<your-org>.github.io/<your-repo>/dbt_docs/
```

---

## 🧠 Best Practices
- Use **least privilege principle**: `ACCOUNTADMIN` only for setup, `TRANSFORM` for runtime.
- Rotate all secrets regularly.
- Never hardcode credentials — use GitHub Secrets.
- Validate ETL steps locally before CI/CD execution.

---

## 🧾 License
This project is released under the [MIT License](LICENSE).

---

## 📬 Contact
For issues or improvements:
- Open a [GitHub Issue](../../issues)
- Fork and submit a Pull Request

---
✨ Built with **Snowflake**, **dbt**, **Python**, and **GitHub Actions**.
