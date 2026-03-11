# Guide d'évaluation opérationnelle — NYC Taxi DWH

## Prérequis évaluateur

- Accès au dépôt GitHub (lien fourni par le candidat)
- Compte Snowflake communiqué par le candidat (rôle ANALYST)
- Power BI Desktop installé (optionnel)

---

## ÉTAPE 1 — Vérifier le pipeline CI/CD

1. Ouvrir l'onglet **Actions** du dépôt GitHub
2. Sélectionner le dernier run sur `main`
3. Vérifier que les 3 jobs sont verts :
   - `terraform` → provisioning infrastructure Snowflake
   - `etl` → chargement des données
   - `dbt` → transformations + tests qualité

Indicateur de succès : 3 jobs avec statut ✓ (vert)

---

## ÉTAPE 2 — Vérifier l'infrastructure Snowflake (C16)

Se connecter à Snowflake avec le rôle ACCOUNTADMIN et exécuter :

    -- Vérifier les schémas créés
    SHOW SCHEMAS IN DATABASE NYC_TAXI_DB_RNCP;
    -- Attendu : RAW, STAGING, FINAL, SNAPSHOTS

    -- Vérifier les rôles
    SHOW ROLES;
    -- Attendu : TRANSFORM, ANALYST

    -- Vérifier les grants du rôle ANALYST
    SHOW GRANTS TO ROLE ANALYST;
    -- Attendu : SELECT sur toutes les tables de FINAL

---

## ÉTAPE 3 — Vérifier les données brutes (ETL)

    -- Volume chargé
    SELECT COUNT(*) FROM NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2;
    -- Attendu : ~50 millions de trajets

    -- Couverture temporelle
    SELECT
        MIN(TPEP_PICKUP_DATETIME) AS premier_trajet,
        MAX(TPEP_PICKUP_DATETIME) AS dernier_trajet,
        COUNT(DISTINCT DATE_TRUNC('month', TPEP_PICKUP_DATETIME)) AS nb_mois
    FROM NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2;
    -- Attendu : jan 2024 → nov 2025, 23 mois

---

## ÉTAPE 4 — Vérifier le schéma en étoile (C13)

    -- Tables du schéma FINAL
    SHOW TABLES IN SCHEMA NYC_TAXI_DB_RNCP.FINAL;
    -- Attendu : DIM_DATE, DIM_LOCATION, DIM_PAYMENT_TYPE,
    --           DIM_RATE_CODE, FCT__TRIPS,
    --           FCT__DAILY_SUMMARY, FCT__ZONE_ANALYSIS, FCT__HOURLY_PATTERNS

    -- Dimension calendaire
    SELECT * FROM NYC_TAXI_DB_RNCP.FINAL.DIM_DATE LIMIT 5;

    -- Dimension géographique
    SELECT borough, COUNT(*) AS nb_zones
    FROM NYC_TAXI_DB_RNCP.FINAL.DIM_LOCATION
    GROUP BY borough ORDER BY nb_zones DESC;

    -- Table de faits (grain : 1 trajet)
    SELECT COUNT(*) FROM NYC_TAXI_DB_RNCP.FINAL.FCT__TRIPS;

    -- Jointure étoile : top 10 zones par revenue
    SELECT
        l.borough,
        d.month_name,
        SUM(f.total_amount) AS revenue_total,
        COUNT(*) AS nb_trajets
    FROM NYC_TAXI_DB_RNCP.FINAL.FCT__TRIPS f
    JOIN NYC_TAXI_DB_RNCP.FINAL.DIM_DATE d ON f.date_fk = d.date_id
    JOIN NYC_TAXI_DB_RNCP.FINAL.DIM_LOCATION l ON f.pu_location_fk = l.location_id
    GROUP BY l.borough, d.month_name
    ORDER BY revenue_total DESC
    LIMIT 10;

---

## ÉTAPE 5 — Vérifier la qualité des données (C14)

Dans le dépôt GitHub, Actions → dernier run dbt → logs du job `dbt` :

    dbt run   → 57/57 PASS (0 ERROR)
    dbt test  → PASS / WARN / 0 ERROR

Ou en local :

    cd nyc_taxi_dbt_snowflake
    dbt test --select final
    dbt source freshness

---

## ÉTAPE 6 — Vérifier l'historisation SCD Type 2 (C17)

    -- Table de snapshot
    SELECT * FROM NYC_TAXI_DB_RNCP.SNAPSHOTS.SCD__CLEAN_TRIPS
    WHERE dbt_valid_to IS NOT NULL
    LIMIT 10;
    -- Les lignes avec dbt_valid_to non NULL = historique des changements

    -- Compter les versions historisées
    SELECT
        COUNT(*) AS total_lignes,
        COUNT(CASE WHEN dbt_valid_to IS NULL THEN 1 END) AS lignes_actives,
        COUNT(CASE WHEN dbt_valid_to IS NOT NULL THEN 1 END) AS lignes_historisees
    FROM NYC_TAXI_DB_RNCP.SNAPSHOTS.SCD__CLEAN_TRIPS;

---

## ÉTAPE 7 — Démontrer le Time Travel (C16)

    -- Comparer l'état de la table hier vs aujourd'hui
    SELECT
        (SELECT COUNT(*) FROM NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2
         AT (OFFSET => -86400)) AS nb_hier,
        (SELECT COUNT(*) FROM NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2) AS nb_auj;

    -- Période de rétention configurée
    SHOW TABLES LIKE 'YELLOW_TAXI_TRIPS_V2' IN SCHEMA NYC_TAXI_DB_RNCP.RAW;
    -- Colonne retention_time = 7

---

## ÉTAPE 8 — Vérifier l'accès rôle ANALYST (C16)

Se connecter avec le rôle ANALYST :

    -- Doit fonctionner
    SELECT COUNT(*) FROM NYC_TAXI_DB_RNCP.FINAL.FCT__TRIPS;

    -- Doit échouer (pas de droits sur RAW)
    SELECT COUNT(*) FROM NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2;
    -- Erreur attendue : "Insufficient privileges"

---

## ÉTAPE 9 — Power BI (C15)

Ouvrir le fichier `.pbix` fourni par le candidat.
Vérifier les visuels :
- Évolution du chiffre d'affaires mensuel
- Répartition des trajets par borough
- Heatmap des heures de pointe
- KPIs : revenue total, distance moyenne, tip moyen

---

## Correspondance compétences / livrables

| Compétence | Livrable | Étape |
|---|---|---|
| C13 — Modélisation DWH | Schéma en étoile FINAL | 4 |
| C14 — Qualité données | dbt tests + source freshness | 5 |
| C15 — Restitution BI | Power BI connecté à FINAL | 9 |
| C16 — Gouvernance | Rôles TRANSFORM/ANALYST + Time Travel | 2, 7, 8 |
| C17 — Historisation | Snapshots SCD Type 2 | 6 |
