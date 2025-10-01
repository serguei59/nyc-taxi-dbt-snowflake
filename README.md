# 🚕 NYC Taxi Pipeline (Snowflake + dbt Core)

## 🚀 Présentation
Ce projet met en place un pipeline **ELT (Extract, Load, Transform)** complet sur les données publiques **NYC Taxi**.  
Il illustre l’usage de **Snowflake** comme data warehouse cloud et **dbt Core** comme outil de transformation moderne.  

Objectif : **Construire un projet portfolio** montrant une architecture professionnelle (RAW → STAGING → FINAL) et des transformations réutilisables, testées et documentées.

---

## 📊 Dataset
- **Source** : [NYC Taxi & Limousine Commission](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)  
- **Format** : Fichiers Parquet mensuels  
- **Période** : Janvier 2024 → Aujourd’hui  
- **Exemple** : `yellow_tripdata_2025-01.parquet`  

---

## 🏗️ Architecture
```
📁 RAW       → données brutes importées
📁 STAGING   → nettoyage et standardisation
📁 FINAL     → tables d'analyse (KPI, agrégations)
```

- **RAW** : ingestion brute des fichiers Parquet.  
- **STAGING** : nettoyage (dates, distances, montants négatifs, NULL).  
- **FINAL** : tables prêtes pour analyse et visualisation.  

---

## 🔧 Installation

### 1. Cloner le projet
```bash
git clone https://github.com/<serguei59/nyc-taxi-dbt-snowflake.git
cd nyc-taxi-dbt-snowflake
```

### 2. Créer un environnement Python
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Installer dbt Core (Snowflake)
```bash
pip install dbt-core dbt-snowflake
```

---

## ⚙️ Configuration Snowflake
Créer un fichier `profiles.yml` (⚠️ à mettre en `.gitignore`).

```yaml
nyc_taxi_project:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: <account_id>
      user: <username>
      password: <password>
      role: ACCOUNTADMIN
      database: NYC_TAXI_DB
      warehouse: NYC_TAXI_WH
      schema: STAGING
```

---

## 📂 Structure du projet
```
nyc_taxi_project/
├── models/
│   ├── staging/        → nettoyage des données brutes
│   ├── intermediate/   → enrichissements & calculs
│   └── marts/          → tables finales d'analyse
├── tests/              → tests de qualité (YAML)
├── dbt_project.yml
└── README.md
```

---

## ▶️ Exécution dbt

### Vérifier la connexion
```bash
dbt debug
```

### Lancer les modèles
```bash
dbt run
```

### Lancer les tests de qualité
```bash
dbt test
```

### Générer la documentation
```bash
dbt docs generate
dbt docs serve
```

---

## 📊 Tables créées

### STAGING
- `stg_yellow_taxi_trips` → nettoyage des trajets

### INTERMEDIATE
- `int_trip_metrics` → enrichissement (durée, vitesse, pourboire, dimensions temporelles)

### MARTS (FINAL)
- `daily_summary` → KPIs quotidiens (trajets, revenus, distances)  
- `zone_analysis` → analyses par zone géographique  
- `hourly_patterns` → patterns horaires de demande  

---

## ✅ KPIs
- Nombre de trajets par jour & mois  
- Distance moyenne  
- Revenu total & moyen  
- Top 10 zones de départ  
- Analyse par période (rush hours, weekend vs semaine)  

---

## 🎯 Résultats attendus
- Data warehouse Snowflake structuré (RAW, STAGING, FINAL)  
- Pipeline dbt Core documenté & testé  
- Résultats analytiques exploitables (SQL / Dashboard)  

---

## 📚 Ressources
- [Snowflake Docs](https://docs.snowflake.com)  
- [dbt Core Docs](https://docs.getdbt.com)  
- [NYC TLC Dataset](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)  

---
