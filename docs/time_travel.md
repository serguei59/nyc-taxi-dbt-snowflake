# Time Travel Snowflake — Sauvegarde et restauration

## Principe

Snowflake conserve une copie historique des données pendant une période configurable
(par défaut 1 jour, jusqu'à 90 jours selon l'édition). Cela permet de :
- Interroger des données à un instant T passé
- Restaurer une table après suppression accidentelle
- Comparer l'état d'une table avant/après un chargement

## Période de rétention configurée

```sql
-- Vérifier la rétention d'une table
SHOW TABLES LIKE 'YELLOW_TAXI_TRIPS_V2' IN SCHEMA NYC_TAXI_DB_RNCP.RAW;# Time Travel Snowflake — Sauvegarde et restauration

## Principe

Snowflake conserve une copie historique des données pendant une période configurable
(par défaut 1 jour, jusqu'à 90 jours selon l'édition). Cela permet de :
- Interroger des données à un instant T passé
- Restaurer une table après suppression accidentelle
- Comparer l'état d'une table avant/après un chargement

## Période de rétention configurée

```sql
-- Vérifier la rétention d'une table
SHOW TABLES LIKE 'YELLOW_TAXI_TRIPS_V2' IN SCHEMA NYC_TAXI_DB_RNCP.RAW;

-- Modifier la rétention (nécessite ACCOUNTADMIN)
ALTER TABLE NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2
  SET DATA_RETENTION_TIME_IN_DAYS = 7;


-- Modifier la rétention (nécessite ACCOUNTADMIN)
ALTER TABLE NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2
  SET DATA_RETENTION_TIME_IN_DAYS = 7;```

## Requêtes de démonstration

### 1. Interroger les données à un instant passé (OFFSET en secondes)

    -- État de la table il y a 1 heure
    SELECT COUNT(*)
    FROM NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2
    AT (OFFSET => -3600);

### 2. Interroger à un timestamp précis

    -- État avant un chargement ETL
    SELECT COUNT(*)
    FROM NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2
    AT (TIMESTAMP => '2025-11-01 08:00:00'::TIMESTAMP_NTZ);

### 3. Comparer avant/après chargement

    SELECT
        (SELECT COUNT(*) FROM NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2
         AT (OFFSET => -86400)) AS nb_hier,
        (SELECT COUNT(*) FROM NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2) AS nb_auj;

### 4. Restaurer une table supprimée accidentellement

    -- Si la table a été droppée dans les dernières 24h
    UNDROP TABLE NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2;

### 5. Créer une sauvegarde avant opération risquée

    CREATE TABLE NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2_BACKUP
    CLONE NYC_TAXI_DB_RNCP.RAW.YELLOW_TAXI_TRIPS_V2;

## Usage en soutenance (C16)

Le Time Travel démontre la capacité à assurer la **continuité de service** et la
**récupérabilité des données** sans infrastructure de backup externe.
Combiné aux snapshots dbt (SCD Type 2), il couvre l'ensemble des exigences C16/C17.