# Rapport Professionnel — Épreuve E5
## Mise en situation professionnelle 3 — Bloc 3 : Élaborer et maintenir un entrepôt de données

---

**Certification visée :** Titre à finalité professionnelle Data Engineer — RNCP 37638
**Bloc évalué :** Bloc 3 — Élaborer et maintenir un entrepôt de données (data warehouse)
**Épreuve :** E5 — Mise en situation professionnelle 3
**Compétences évaluées :** C13, C14, C15
**Candidat :** [Nom Prénom]
**Date de soutenance :** [Date]
**Organisme de formation :** Simplon

---

## Sommaire

1. [Contexte et besoin analytique](#1-contexte-et-besoin-analytique)
2. [Données nécessaires aux analyses envisagées](#2-données-nécessaires-aux-analyses-envisagées)
3. [Modélisation logique et physique de l'entrepôt de données](#3-modélisation-logique-et-physique-de-lentrepôt-de-données) — **C13**
4. [Création et configuration de l'entrepôt de données](#4-création-et-configuration-de-lentrepôt-de-données) — **C14**
5. [Configuration des accès aux données](#5-configuration-des-accès-aux-données) — **C14**
6. [Intégration des ETL en entrée et en sortie](#6-intégration-des-etl-en-entrée-et-en-sortie) — **C15**
7. [Traitements de nettoyage et formatage des données](#7-traitements-de-nettoyage-et-formatage-des-données) — **C15**
8. [Organisation de la phase de test et qualité des données](#8-organisation-de-la-phase-de-test-et-qualité-des-données)
9. [Documentation technique](#9-documentation-technique)
10. [Retour d'expérience](#10-retour-dexpérience)

---

## 1. Contexte et besoin analytique

### 1.1 Présentation du projet

Le projet **NYC Taxi Data Warehouse** a été réalisé dans le cadre de la certification RNCP 37638 Data Engineer. Il répond à un besoin analytique réel : exploiter les données de courses de taxis jaunes de New York (Yellow Taxi Trips) publiées mensuellement par la NYC Taxi & Limousine Commission (TLC), afin de soutenir l'analyse de l'activité et l'aide à la décision.

La source de données est publique et disponible à l'adresse officielle du NYC TLC, au format **Parquet**, avec une publication mensuelle. Le périmètre couvert par ce projet s'étend de **janvier 2024 à septembre 2025**, soit **23 mois** de données, représentant environ **50 à 52 millions de courses**.

### 1.2 Objectifs analytiques

L'entrepôt de données doit permettre de répondre aux questions métier suivantes :

- Quelle est l'évolution du volume de courses par jour, semaine et mois ?
- Quels sont les quartiers de New York les plus actifs en termes de prise en charge et de dépose ?
- Quelle est la répartition des modes de paiement et leur impact sur les pourboires ?
- Quelles sont les heures de pointe par zone géographique ?
- Quels sont les indicateurs financiers clés : revenu moyen par course, montant moyen des pourboires, tarifs appliqués ?

### 1.3 Stack technique retenue

| Composant | Technologie | Version |
|---|---|---|
| Entrepôt de données cloud | Snowflake | Dernier en date |
| Infrastructure as Code | Terraform + Terraform Cloud | 1.10.2 / Provider Snowflake 2.10.1 |
| Transformation et modélisation | dbt (data build tool) | dbt-core 1.10.13 / dbt-snowflake 1.10.2 |
| Langage ETL | Python | 3.11 |
| CI/CD | GitHub Actions | — |
| Visualisation | Metabase (Docker) | Dernier en date |

---

## 2. Données nécessaires aux analyses envisagées

### 2.1 Source de données

**Source :** NYC Taxi & Limousine Commission — fichiers Parquet mensuels
**URL pattern :** `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{YYYY}-{MM}.parquet`
**Couverture temporelle :** Janvier 2024 – Septembre 2025 (23 fichiers)
**Volume total :** ~1,27 Go de fichiers Parquet bruts

### 2.2 Inventaire des données brutes

Le tableau suivant liste les 19 colonnes du fichier source et leur rôle analytique :

| Colonne brute | Type | Description | Utilité analytique |
|---|---|---|---|
| `VendorID` | INTEGER | Identifiant du fournisseur taxi (1=Creative Mobile, 2=VeriFone) | Dimension fournisseur |
| `tpep_pickup_datetime` | TIMESTAMP | Horodatage de prise en charge | Axe temporel principal |
| `tpep_dropoff_datetime` | TIMESTAMP | Horodatage de dépose | Calcul de durée |
| `passenger_count` | INTEGER | Nombre de passagers | Indicateur d'occupation |
| `trip_distance` | FLOAT | Distance en miles | Indicateur de distance |
| `RatecodeID` | INTEGER | Code tarifaire appliqué | Dimension tarif |
| `PULocationID` | INTEGER | Zone TLC de prise en charge (1-263) | Dimension géographique |
| `DOLocationID` | INTEGER | Zone TLC de dépose (1-263) | Dimension géographique |
| `payment_type` | INTEGER | Mode de paiement (1-5) | Dimension paiement |
| `fare_amount` | FLOAT | Tarif de base | Indicateur financier |
| `extra` | FLOAT | Supplément heure de pointe / nuit | Indicateur financier |
| `mta_tax` | FLOAT | Taxe MTA | Indicateur fiscal |
| `tip_amount` | FLOAT | Pourboire | Indicateur comportemental |
| `tolls_amount` | FLOAT | Péages | Indicateur financier |
| `improvement_surcharge` | FLOAT | Supplément amélioration infrastructure | Indicateur financier |
| `total_amount` | FLOAT | Montant total payé | Indicateur financier clé |
| `congestion_surcharge` | FLOAT | Supplément congestion (NYC) | Indicateur réglementaire |
| `airport_fee` | FLOAT | Frais aéroport (JFK / LaGuardia) | Indicateur de destination |
| `store_and_fwd_flag` | VARCHAR | Indicateur de transmission différée | Technique |

### 2.3 Données de référence nécessaires

En complément des données transactionnelles, les analyses nécessitent des **données de référence** (dimensions) :

- **Calendrier** : attributs temporels dérivés (jour de semaine, semaine, mois, trimestre, week-end) pour les analyses chronologiques
- **Zones géographiques TLC** : correspondance entre les identifiants de zones (1-263) et les noms de quartiers / arrondissements de New York
- **Codes tarifaires** : libellés des 7 codes tarifaires TLC (Standard, JFK, Newark, Nassau, Négocié, Groupe, Inconnu)
- **Types de paiement** : libellés des 5 modes de paiement (Carte de crédit, Espèces, Sans frais, Litige, Inconnu)

---

## 3. Modélisation logique et physique de l'entrepôt de données

> **Compétence C13** — Modéliser la structure des données d'un entrepôt de données en s'appuyant sur les dimensions et les faits afin d'optimiser l'organisation des données pour les requêtes analytiques.

### 3.1 Choix du modèle : schéma en étoile

Le modèle retenu est le **schéma en étoile** (Star Schema), recommandé par Ralph Kimball pour les entrepôts de données analytiques. Ce choix est justifié par :

- La **simplicité des requêtes SQL** : jointures directes entre la table de faits et les dimensions, sans jointures en cascade
- Les **performances de lecture** : optimisé pour les agrégations analytiques sur Snowflake
- La **lisibilité** pour les équipes d'analyse utilisant Metabase

### 3.2 Modèle logique des données (MLD)

```
┌─────────────────────┐
│     DIM_DATE        │
│─────────────────────│
│ PK date_id (DATE)   │
│    year             │
│    month            │
│    day              │
│    day_of_week      │
│    day_name         │
│    month_name       │
│    week_of_year     │
│    quarter          │
│    is_weekend       │
└──────────┬──────────┘
           │ FK date_fk
           │
┌──────────┴──────────────────────────────────┐
│                  FCT__TRIPS                  │
│──────────────────────────────────────────────│
│ FK date_fk           → DIM_DATE.date_id      │
│ FK pu_location_fk    → DIM_LOCATION.loc_id   │
│ FK do_location_fk    → DIM_LOCATION.loc_id   │
│ FK payment_type_fk   → DIM_PAYMENT_TYPE.id   │
│ FK ratecode_fk       → DIM_RATE_CODE.id      │
│    vendor_id (dégénéré)                      │
│    pickup_datetime                           │
│    dropoff_datetime                          │
│    passenger_count                           │
│    trip_distance                             │
│    trip_duration_min                         │
│    fare_amount                               │
│    tip_amount                                │
│    tip_pct                                   │
│    total_amount                              │
│    mta_tax                                   │
│    extra                                     │
│    tolls_amount                              │
│    improvement_surcharge                     │
│    congestion_surcharge                      │
│    airport_fee                               │
└─────────┬──────┬──────────┬─────────────────┘
          │      │          │
          │      │    ┌─────┴──────────────────┐
          │      │    │   DIM_PAYMENT_TYPE      │
          │      │    │────────────────────────│
          │      │    │ PK payment_type_id      │
          │      │    │    payment_label        │
          │      │    └────────────────────────┘
          │      │
          │   ┌──┴─────────────────────────────┐
          │   │       DIM_RATE_CODE             │
          │   │────────────────────────────────│
          │   │ PK ratecode_id                  │
          │   │    rate_label                   │
          │   └────────────────────────────────┘
          │
┌─────────┴──────────────────────┐
│         DIM_LOCATION           │
│────────────────────────────────│
│ PK location_id (INTEGER)       │
│    zone_name                   │
│    borough                     │
└────────────────────────────────┘
```

### 3.3 Modèle physique des données (MPD)

#### Table de faits — `FINAL.FCT__TRIPS`

| Colonne | Type Snowflake | Contrainte | Description |
|---|---|---|---|
| `date_fk` | DATE | NOT NULL | FK → DIM_DATE |
| `pu_location_fk` | NUMBER | NOT NULL | FK → DIM_LOCATION (prise en charge) |
| `do_location_fk` | NUMBER | NOT NULL | FK → DIM_LOCATION (dépose) |
| `payment_type_fk` | VARCHAR | NOT NULL | FK → DIM_PAYMENT_TYPE |
| `ratecode_fk` | NUMBER | — | FK → DIM_RATE_CODE |
| `vendor_id` | NUMBER | — | Dimension dégénérée |
| `pickup_datetime` | TIMESTAMP_NTZ | — | Horodatage précis de départ |
| `dropoff_datetime` | TIMESTAMP_NTZ | — | Horodatage précis d'arrivée |
| `passenger_count` | NUMBER | — | Nombre de passagers |
| `trip_distance` | FLOAT | — | Distance en miles |
| `trip_duration_min` | FLOAT | — | Durée calculée en minutes |
| `fare_amount` | FLOAT | — | Tarif de base |
| `tip_amount` | FLOAT | — | Pourboire |
| `tip_pct` | FLOAT | — | Taux de pourboire (%) |
| `total_amount` | FLOAT | — | Montant total |
| `mta_tax` | FLOAT | — | Taxe MTA |
| `extra` | FLOAT | — | Supplément |
| `tolls_amount` | FLOAT | — | Péages |
| `improvement_surcharge` | FLOAT | — | Supplément infrastructure |
| `congestion_surcharge` | FLOAT | — | Supplément congestion |
| `airport_fee` | FLOAT | — | Frais aéroport |

**Volume estimé :** ~50 millions de lignes

#### Dimensions

| Table | PK | Colonnes clés | Volume |
|---|---|---|---|
| `FINAL.DIM_DATE` | `date_id DATE` | year, month, day, day_name, quarter, is_weekend | ~700 lignes |
| `FINAL.DIM_LOCATION` | `location_id NUMBER` | zone_name, borough | 263 lignes |
| `FINAL.DIM_PAYMENT_TYPE` | `payment_type_id VARCHAR` | payment_label | 5 lignes |
| `FINAL.DIM_RATE_CODE` | `ratecode_id NUMBER` | rate_label | 7 lignes |

#### Data marts pré-agrégés

En complément du schéma en étoile, trois **data marts** ont été créés pour optimiser les performances des requêtes analytiques courantes :

| Table | Grain | Usage | Volume |
|---|---|---|---|
| `FINAL.FCT__DAILY_SUMMARY` | 1 ligne / jour | Tableaux de bord temporels | ~700 lignes |
| `FINAL.FCT__ZONE_ANALYSIS` | 1 ligne / zone | Analyses géographiques | 263 lignes |
| `FINAL.FCT__HOURLY_PATTERNS` | 1 ligne / (heure × jour) | Analyses des heures de pointe | ~16 800 lignes |

### 3.4 Architecture des zones de données

L'entrepôt est organisé en **4 couches fonctionnelles** dans Snowflake :

```
┌─────────────────────────────────────────────────────────────┐
│                    NYC_TAXI_DB_RNCP                          │
│                                                             │
│  ┌──────────┐    ┌───────────┐    ┌───────────┐   ┌──────┐ │
│  │   RAW    │───▶│ STAGING   │───▶│   FINAL   │   │SNAP  │ │
│  │          │    │           │    │           │   │SHOTS │ │
│  │ Données  │    │ Nettoyage │    │ Schéma    │   │ SCD  │ │
│  │ brutes   │    │ Formatage │    │ en étoile │   │ T.2  │ │
│  │ Parquet  │    │ Filtrage  │    │ + data    │   │      │ │
│  │          │    │           │    │ marts     │   │      │ │
│  └──────────┘    └───────────┘    └───────────┘   └──────┘ │
│    ETL Python       dbt stg          dbt final   dbt snap   │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Création et configuration de l'entrepôt de données

> **Compétence C14** — Créer un entrepôt de données à partir des paramètres du projet, des contraintes techniques et matérielles et de la modélisation de la structure des données.

### 4.0 Paramètres du projet et contraintes techniques

Avant de détailler la mise en œuvre, il est nécessaire d'expliciter les **paramètres et contraintes** qui ont guidé les choix techniques :

| Contrainte | Impact sur les choix |
|---|---|
| Environnement 100 % cloud, sans infrastructure on-premise | Snowflake (DW cloud managé, sans serveur à administrer) |
| Volume de données élevé (~50 millions de lignes, 1,27 Go brut) | Warehouse Snowflake taille MEDIUM, auto-suspend pour optimiser les coûts |
| Équipe réduite, sans DBA dédié | Terraform (provisionnement automatisé), dbt (transformations déclaratives sans ETL serveur) |
| Données sources publiées mensuellement, format Parquet | ETL Python avec cache local et MERGE idempotent |
| Besoin de séparation des droits (producteurs vs analystes) | Deux rôles Snowflake distincts gérés par Terraform |
| Exigence de qualité et de traçabilité des données | dbt avec tests automatisés et génération de documentation |
| Reproductibilité et auditabilité | Infrastructure as Code + CI/CD GitHub Actions |

Ces contraintes ont déterminé le choix de chaque outil de la stack et sont prises en compte dans toutes les décisions de configuration décrites ci-dessous.

### 4.1 Provisionnement de l'infrastructure par Terraform

L'intégralité de l'infrastructure Snowflake est provisionnée via **Terraform**, garantissant la reproductibilité et la traçabilité de la configuration.

**Ressources Terraform créées :**

```hcl
# Base de données principale
resource "snowflake_database" "nyc_taxi_db" {
  name = "NYC_TAXI_DB_RNCP"
}

# 3 schémas fonctionnels
resource "snowflake_schema" "raw"     { name = "RAW"     }
resource "snowflake_schema" "staging" { name = "STAGING"  }
resource "snowflake_schema" "final"   { name = "FINAL"    }

# Entrepôt de calcul
resource "snowflake_warehouse" "transform_wh" {
  name             = "NYC_TAXI_WH_RNCP"
  warehouse_size   = "MEDIUM"   # 4 crédits Snowflake / heure
  auto_suspend     = 60         # Suspension automatique après 60s d'inactivité
  auto_resume      = true       # Reprise automatique à la demande
  initially_suspended = true    # Démarrage suspendu (optimisation des coûts)
}
```

**Backend Terraform Cloud :** organisation `nyc-taxi-project`, workspace `rncp-e5` — permet la gestion centralisée du state et l'exécution en CI/CD.

### 4.2 Configuration de dbt

dbt gère la création et le rafraîchissement de toutes les tables des schémas STAGING et FINAL.

**`dbt_project.yml` — configuration de matérialisation :**

```yaml
models:
  nyc_taxi_dbt_snowflake:
    staging:
      +schema: STAGING
      +materialized: table   # Tables permanentes (pas de vues)
    final:
      +schema: FINAL
      +materialized: table
```

Toutes les tables sont matérialisées en **tables permanentes** (non des vues), ce qui garantit des performances de lecture optimales pour les requêtes analytiques de Metabase.

### 4.3 Organisation de la phase de test

La phase de test est intégrée au pipeline CI/CD et s'exécute automatiquement à chaque déploiement. Elle est décrite en détail en [section 8](#8-organisation-de-la-phase-de-test-et-qualité-des-données).

---

## 5. Configuration des accès aux données

> **Compétence C14** — Configurer les accès aux données pour les équipes d'analyse et aux données opérationnelles sources.

### 5.1 Architecture des rôles Snowflake

Le principe du **moindre privilège** est appliqué via deux rôles distincts, entièrement gérés par Terraform :

```
ACCOUNTADMIN (LULU)
├── TRANSFORM (rôle dbt + ETL)
│   ├── USAGE + OPERATE sur NYC_TAXI_WH_RNCP
│   ├── USAGE + CREATE SCHEMA sur NYC_TAXI_DB_RNCP
│   ├── SELECT sur RAW (lecture des données brutes)
│   ├── ALL PRIVILEGES sur STAGING (création + modification)
│   └── ALL PRIVILEGES sur FINAL (création + modification)
│
└── ANALYST (rôle lecture seule — équipes BI)
    ├── USAGE sur NYC_TAXI_WH_RNCP
    ├── USAGE sur NYC_TAXI_DB_RNCP
    └── SELECT sur FINAL uniquement (pas d'accès RAW ni STAGING)
```

### 5.2 Matrice des accès

| Rôle | RAW | STAGING | FINAL | SNAPSHOTS | Warehouse |
|---|---|---|---|---|---|
| `ACCOUNTADMIN` | Tous | Tous | Tous | Tous | Tous |
| `TRANSFORM` | SELECT | Tous | Tous | Tous | USAGE + OPERATE |
| `ANALYST` | — | — | SELECT | — | USAGE |

### 5.3 Séparation des responsabilités

- Le rôle `TRANSFORM` est utilisé exclusivement par l'utilisateur `DBT` (compte technique Terraform) — les pipelines dbt et Python ETL s'exécutent sous ce rôle
- Le rôle `ANALYST` est assigné aux consommateurs de données (Metabase, équipes BI) — ils n'ont **aucune visibilité** sur les données brutes ni les données intermédiaires
- Les grants sont **forcés** à chaque déploiement Terraform via le flag `-replace`, garantissant la cohérence même si de nouvelles tables ont été créées par l'ETL Python

---

## 6. Intégration des ETL en entrée et en sortie

> **Compétence C15** — Intégrer les ETL nécessaires en entrée et en sortie d'un entrepôt de données afin de garantir la qualité et le bon formatage des données.

### 6.1 ETL en entrée — Python (RAW → Snowflake)

L'ETL d'ingestion est composé de deux scripts Python :

#### `extract/download_parquet.py` — Extraction

- Télécharge les fichiers Parquet mensuels depuis l'API NYC TLC
- Mécanisme de **cache local** : si le fichier existe déjà, le téléchargement est ignoré (idempotence)
- Gestion des erreurs HTTP 403 (fichier non encore publié)
- **23 fichiers téléchargés** : janvier 2024 → septembre 2025

#### `load/merge_dynamic.py` — Chargement

Le chargement utilise une stratégie **MERGE** pour garantir l'idempotence :

```python
# Clé de déduplication sur 8 colonnes métier
MERGE_KEY_COLUMNS = [
    "TPEP_PICKUP_DATETIME",
    "TPEP_DROPOFF_DATETIME",
    "VENDORID",
    "PULOCATIONID",
    "DOLOCATIONID",
    "PASSENGER_COUNT",
    "TOTAL_AMOUNT",
    "TRIP_DISTANCE"
]
```

**Fonctionnalités clés de l'ETL :**

| Fonctionnalité | Implémentation |
|---|---|
| Création automatique de la table | `create_table_if_not_exists()` — DDL généré depuis le schéma Pandas |
| Évolution de schéma | `update_table_schema()` — ajout des colonnes manquantes sans perte de données |
| Déduplication | Suppression des doublons sur les 8 colonnes-clé avant MERGE |
| Normalisation | Passage en majuscules de toutes les colonnes |
| MERGE idempotent | INSERT si nouvelle course, UPDATE si modification détectée |

### 6.1.3 Configuration de la zone de sortie de l'ETL Python

La **zone de sortie de l'ETL Python** est le schéma **RAW** de la base `NYC_TAXI_DB_RNCP`. Ce schéma constitue la couche d'atterrissage des données brutes : aucune transformation métier n'y est appliquée, seule la structure technique (noms de colonnes en majuscules, types Snowflake) est normalisée. Le schéma RAW est créé et versionné par Terraform ; les tables sont créées dynamiquement par l'ETL Python à la première exécution, puis mises à jour par MERGE lors des exécutions suivantes.

### 6.2 ETL en sortie — dbt (STAGING → FINAL)

dbt constitue l'ETL de sortie : il transforme les données de la couche STAGING vers la couche FINAL analytique.

**Séquence d'exécution dbt dans le pipeline CI/CD :**

```bash
dbt deps        # Téléchargement des packages (dbt_utils, dbt_expectations...)
dbt seed        # Chargement des données de référence
dbt run         # Matérialisation de tous les modèles (57 modèles)
dbt test        # Exécution des 87 tests de qualité
dbt snapshot    # Capture historique SCD Type 2
dbt docs generate # Génération de la documentation
```

**Configuration de la zone de sortie de l'ETL dbt :**

La **zone de sortie de l'ETL dbt** est le schéma **FINAL**, défini dans `dbt_project.yml` (`+schema: FINAL`). Ce schéma reçoit l'intégralité du schéma en étoile et des data marts tels que modélisés en section 3. Chaque modèle dbt correspond exactement à une table du modèle physique (MPD, section 3.3) : les noms de colonnes, types et contraintes définis dans le MPD sont respectés dans les instructions `SELECT` et `CAST` de chaque modèle.

**Lineage des transformations :**

```
RAW.YELLOW_TAXI_TRIPS_V2
        │
        ▼
STAGING.STG__CLEAN_TRIPS  (nettoyage + enrichissement)
        │
        ├──▶ FINAL.DIM_DATE
        ├──▶ FINAL.DIM_LOCATION
        ├──▶ FINAL.DIM_PAYMENT_TYPE (source statique)
        ├──▶ FINAL.DIM_RATE_CODE    (source statique)
        ├──▶ FINAL.FCT__TRIPS
        ├──▶ FINAL.FCT__DAILY_SUMMARY
        ├──▶ FINAL.FCT__ZONE_ANALYSIS
        └──▶ FINAL.FCT__HOURLY_PATTERNS
```

---

## 7. Traitements de nettoyage et formatage des données

> **Compétence C15** — Programmer les traitements appliqués aux données, nécessaires au nettoyage et au formatage en respect des schémas physiques de données des zones de sortie.

### 7.1 Problème identifié — Bug des timestamps

**Anomalie détectée :** les fichiers Parquet NYC TLC encodent les timestamps en **microsecondes** depuis l'epoch Unix, mais la bibliothèque `write_pandas` de Snowflake les interprète comme des **secondes**. Résultat : des dates aberrantes de l'an **54 millions** apparaissent dans la table RAW.

**Correction appliquée dans `stg__clean_trips.sql` :**

```sql
TO_TIMESTAMP_NTZ(
    DATE_PART('epoch_second', TPEP_PICKUP_DATETIME) / 1000000
) AS pickup_ts
```

Cette correction divise la valeur epoch par 1 000 000 pour obtenir les secondes réelles, puis reconvertit en `TIMESTAMP_NTZ`.

### 7.2 Règles de nettoyage et filtrage

Toutes les règles de nettoyage sont centralisées dans le modèle `stg__clean_trips.sql` :

| Règle | Condition SQL | Justification |
|---|---|---|
| Filtrage temporel | `DATE(pickup_ts) BETWEEN '2024-01-01' AND '2025-11-30'` | Cohérence avec le périmètre du projet |
| Durée valide | `trip_duration_min BETWEEN 1 AND 1440` | Exclut les courses impossibles (0 min ou +24h) |
| Distance valide | `TRIP_DISTANCE BETWEEN 0.1 AND 100` | Exclut les distances aberrantes |
| Montant positif | `TOTAL_AMOUNT >= 0` | Exclut les remboursements / erreurs de saisie |
| Dépose après prise en charge | `dropoff_ts > pickup_ts` | Cohérence temporelle |
| Passagers valides | `PASSENGER_COUNT BETWEEN 1 AND 6` | Capacité réelle d'un taxi |

### 7.3 Enrichissement des données

En plus du nettoyage, le modèle de staging calcule des **colonnes dérivées** nécessaires au schéma en étoile :

| Colonne calculée | Formule | Utilité |
|---|---|---|
| `trip_duration_min` | `DATEDIFF('minute', pickup_ts, dropoff_ts)` | Mesure de durée |
| `tip_pct` | `tip_amount / NULLIF(fare_amount, 0) * 100` | Taux de pourboire |
| `trip_date` | `DATE(pickup_ts)` | Clé vers DIM_DATE |
| `pickup_hour` | `HOUR(pickup_ts)` | Analyses horaires |
| `pickup_month` | `MONTH(pickup_ts)` | Analyses mensuelles |
| `ingestion_ts` | `CURRENT_TIMESTAMP()` | Traçabilité du chargement |

### 7.4 Formatage des types de données

| Colonne brute | Type RAW | Type STAGING | Transformation |
|---|---|---|---|
| `VENDORID` | FLOAT | NUMBER | `CAST(VENDORID AS INTEGER)` |
| `PULOCATIONID` | FLOAT | NUMBER | `CAST(... AS INTEGER)` |
| `PAYMENT_TYPE` | INTEGER | VARCHAR | `CAST(... AS VARCHAR)` |
| `PASSENGER_COUNT` | FLOAT | NUMBER | `CAST(... AS INTEGER)` |
| Timestamps | TIMESTAMP_NTZ (µs) | TIMESTAMP_NTZ (correct) | Division par 1 000 000 |

### 7.5 Conformité avec les modélisations logique et physique

L'ensemble des traitements décrits dans cette section (nettoyage, enrichissement, typage) a pour finalité de garantir que les données produites sont **strictement conformes au modèle physique défini en section 3.3** :

- Les **types de colonnes** dans les tables FINAL correspondent exactement aux types Snowflake définis dans le MPD (NUMBER, FLOAT, DATE, TIMESTAMP_NTZ, VARCHAR)
- Les **clés étrangères** de `FCT__TRIPS` (date_fk, pu_location_fk, do_location_fk, payment_type_fk, ratecode_fk) sont alimentées par les colonnes calculées dans `stg__clean_trips`, et leur intégrité est vérifiée par les tests dbt `not_null`
- Les **règles de filtrage** (durée, distance, montant, passagers) garantissent que les mesures de la table de faits se situent dans les plages de valeurs cohérentes avec le besoin analytique décrit dans la modélisation
- Le **modèle logique** (MLD, section 3.2) est respecté : chaque dimension possède sa clé primaire unique, la table de faits contient toutes les clés étrangères et mesures prévues, les data marts sont des agrégations conformes aux axes d'analyse définis

Cette conformité est vérifiée automatiquement à chaque exécution du pipeline par les 87 tests dbt (section 8).

---

## 8. Organisation de la phase de test et qualité des données

### 8.1 Stratégie de test

Les tests sont organisés en **3 niveaux** :

| Niveau | Outil | Type de test |
|---|---|---|
| Tests génériques | dbt built-in | not_null, unique, accepted_values, relationships |
| Tests avancés | dbt_expectations | Plages de valeurs, quantiles, distributions |
| Tests métier | SQL custom | Règles spécifiques NYC Taxi |

### 8.2 Résultats des tests

**Résultat du dernier pipeline CI/CD :**

```
dbt test : 80 PASS / 7 WARN / 0 ERROR
```

| Modèle | Tests PASS | Tests WARN | Exemples de tests |
|---|---|---|---|
| `stg__clean_trips` | 15 | 1 | Plage temporelle, durée, distance, passagers |
| `fct__trips` | 6 | 0 | FK not_null, distance in [0.1, 100] |
| `dim_date` | 5 | 0 | PK unique + not_null, attributs calendaires |
| `dim_location` | 3 | 0 | PK unique, borough in valeurs autorisées |
| `dim_payment_type` | 2 | 0 | PK unique + not_null |
| `dim_rate_code` | 2 | 0 | PK unique + not_null |
| `fct__daily_summary` | 2 | 0 | date not_null, revenue >= 0 |
| `fct__zone_analysis` | 1 | 0 | zone not_null |
| `fct__hourly_patterns` | 3 | 6 | (heure × date) unique, heure in [0-23] |

**Tests de régression temporelle critiques** (détection du bug des timestamps) :

```yaml
- dbt_expectations.expect_column_values_to_be_between:
    column_name: trip_date
    min_value: "'2024-01-01'::DATE"
    max_value: "'2026-12-31'::DATE"
```

### 8.3 Pipeline CI/CD automatisé

Le pipeline GitHub Actions s'exécute à chaque push sur les branches `dev` et `main`, selon la séquence suivante :

```
Push GitHub
    │
    ▼
[Stage 1] Terraform Apply
    │  Infrastructure Snowflake à jour
    ▼
[Stage 2] ETL Python
    │  23 fichiers Parquet → RAW.YELLOW_TAXI_TRIPS_V2
    ▼
[Stage 3] dbt Pipeline
    ├── dbt deps
    ├── dbt seed
    ├── dbt run  → 57/57 modèles ✅
    ├── dbt test → 80 PASS / 7 WARN ✅
    └── dbt snapshot → SCD Type 2 ✅
```

---

## 9. Documentation technique

### 9.1 Documentation générée automatiquement

dbt génère une **documentation interactive** (`dbt docs generate`) à chaque exécution du pipeline CI/CD. Elle inclut :

- Le **graphe de lignage** (lineage) de tous les modèles
- Les **descriptions** de chaque colonne (via `schema.yml`)
- Les **résultats des tests** de qualité
- Le **catalogue de données** complet

### 9.2 Documentation rédigée

Un ensemble de documents techniques accompagne le projet dans le dossier `docs/` :

| Document | Contenu |
|---|---|
| `architecture.md` | Flux de données, description des couches, stack technique |
| `data_dictionary.md` | Dictionnaire de données : toutes les colonnes RAW → FINAL |
| `star_schema.md` | Schémas MLD/MPD, description des dimensions et faits |
| `ingestion.md` | Détail du pipeline ETL Python, logique MERGE |
| `transformations.md` | Règles dbt couche par couche, exemples SQL |
| `data_quality.md` | Stratégie de qualité, packages utilisés, résultats |
| `time_travel.md` | Procédures de récupération via Snowflake Time Travel |
| `setup.md` | Installation de l'environnement de développement local |
| `setup_infrastructure_snowflake_terraform.md` | Provisionnement Terraform pas à pas |

### 9.3 Versioning et traçabilité

Tout le code est versionné via **Git** (GitHub), avec une stratégie de branches structurée :

- `main` : branche de production (déclenchement du CI/CD complet)
- `dev` : branche d'intégration
- `feature/*` : branches de développement par fonctionnalité

Les Pull Requests assurent la revue de code avant toute mise en production.

---

## 10. Retour d'expérience

### 10.1 Cohérence avec les paramètres du projet

L'ensemble de la stack technique retenue (Snowflake + dbt + Terraform + Python + GitHub Actions) est **parfaitement adapté** aux contraintes du projet :

- **Snowflake** : solution cloud entièrement managée, sans infrastructure à maintenir, idéale pour un projet data d'envergure moyenne (~50M de lignes)
- **dbt** : outil standard de l'industrie pour la transformation analytique, garantissant la qualité (tests intégrés) et la traçabilité (lineage)
- **Terraform** : reproductibilité totale de l'infrastructure, aucune configuration manuelle requise
- **GitHub Actions** : automatisation complète du déploiement, zéro intervention humaine une fois le pipeline configuré

### 10.2 Difficultés rencontrées et solutions apportées

#### Bug des timestamps microseconde

**Problème :** Les fichiers Parquet NYC TLC encodent les timestamps en microsecondes, mais `write_pandas` les injecte comme des secondes dans Snowflake → dates de l'an 54 000 000 dans la table RAW.

**Solution :** Correction dans `stg__clean_trips.sql` via `DATE_PART('epoch_second', col) / 1000000`. Des tests de régression temporels ont été ajoutés pour détecter toute récurrence.

#### Gestion du state Terraform avec les tables RAW

**Problème :** Le provider Snowflake v2.10.1 génère une erreur lors de l'import des ressources `snowflake_table` existantes créées par l'ETL Python.

**Solution :** Les ressources `snowflake_table` ont été exclues du state Terraform (`tables_raw.tf` commenté). L'ETL Python reste responsable de la création dynamique des tables RAW via `create_table_if_not_exists()`. Les grants sont forcés via le flag `-replace` à chaque `terraform apply`.

#### Évolution de schéma des fichiers Parquet

**Problème :** La NYC TLC a ajouté la colonne `airport_fee` en cours de projet ; les fichiers antérieurs ne la contiennent pas.

**Solution :** La fonction `update_table_schema()` de l'ETL détecte automatiquement les colonnes manquantes et les ajoute via `ALTER TABLE ADD COLUMN` sans perte de données.

### 10.3 Avantages de l'approche

| Avantage | Détail |
|---|---|
| **Infrastructure as Code** | L'environnement Snowflake complet est recréable en < 5 min depuis zero |
| **Idempotence** | Le pipeline peut être relancé autant de fois que nécessaire sans dupliquer les données |
| **Qualité automatisée** | 87 tests s'exécutent à chaque déploiement — aucun test manuel requis |
| **Séparation des couches** | RAW / STAGING / FINAL garantissent la traçabilité à chaque étape de la transformation |
| **Scalabilité** | Snowflake scale horizontalement ; l'ajout d'une nouvelle source de données nécessite uniquement un nouveau script ETL et un nouveau modèle stg__ |

### 10.4 Améliorations envisagées

- **Orchestration** : remplacement du CI/CD GitHub Actions par Apache Airflow pour une orchestration temporelle (déclenchement automatique mensuel à la publication des nouveaux fichiers TLC)
- **Partitionnement** : mise en place du clustering Snowflake sur `FCT__TRIPS.date_fk` pour accélérer les requêtes temporelles sur les gros volumes
- **Data observability** : intégration de dbt Cloud ou Elementary pour la surveillance continue de la qualité des données en production
- **Tests de performance** : mesure systématique des temps de réponse des requêtes Metabase et optimisation des data marts si nécessaire

---

## Éléments complémentaires — Au-delà des exigences E5

Dans le cadre de ce projet, et au-delà des exigences strictes de l'épreuve E5, plusieurs mécanismes relevant de la **gouvernance**, du **maintien en conditions opérationnelles** et de l'**historisation des données** ont été mis en place dès la conception de l'entrepôt. Ces éléments correspondent aux compétences C16 et C17 du référentiel, sans être requis pour cette épreuve.

### Maintien en conditions opérationnelles (C16)

**Supervision et journalisation :**
L'entrepôt dispose de deux niveaux de journalisation. Le pipeline CI/CD GitHub Actions produit un journal horodaté de chaque exécution (Terraform, ETL Python, dbt), avec statut de réussite ou d'échec de chaque étape. En parallèle, Snowflake enregistre nativement l'historique de toutes les requêtes exécutées via le `QUERY_HISTORY`, permettant d'auditer toute opération sur les données.

**Sauvegarde et récupération des données :**
Snowflake intègre nativement le mécanisme **Time Travel**, activé sur tous les schémas du projet. Il permet de restaurer n'importe quelle table dans son état antérieur jusqu'à 90 jours en arrière, sans aucune configuration supplémentaire. Ce mécanisme constitue la procédure de backup et de récupération en cas d'altération involontaire des données.

**Gestion des accès et évolutions structurelles :**
L'intégralité des rôles, utilisateurs et grants Snowflake est gérée par Terraform, versionné dans Git. Toute évolution d'accès (ajout d'un utilisateur, modification de droits) fait l'objet d'un commit, d'une Pull Request et d'une validation CI/CD avant d'être appliquée. Ce processus garantit la traçabilité et la conformité RGPD de toute modification d'accès.

### Historisation des variations de dimensions — SCD Type 2 (C17)

En anticipation des besoins d'analyse historique, un **snapshot SCD Type 2** a été implémenté via `dbt snapshot` sur la table `stg__clean_trips`. La table `SNAPSHOTS.SCD__CLEAN_TRIPS` enregistre automatiquement toute modification détectée sur cinq attributs clés d'une course (montant total, tarif de base, pourboire, distance, nombre de passagers), en conservant les valeurs historiques avec leurs horodatages de validité (`dbt_valid_from` / `dbt_valid_to`).

Cette implémentation correspond à la méthode **Type 2 de Ralph Kimball** : chaque modification génère une nouvelle ligne historique plutôt qu'un écrasement, permettant d'analyser l'évolution des données dans le temps.

| Mécanisme | Technologie | Correspondance RNCP |
|---|---|---|
| Journalisation pipeline | GitHub Actions logs | C16 — supervision et alertes |
| Journalisation requêtes | Snowflake Query History | C16 — supervision |
| Backup / récupération | Snowflake Time Travel (90 jours) | C16 — maintien en conditions opérationnelles |
| Gestion des accès versionnée | Terraform + Git + CI/CD | C16 — gestion des accès et évolutions structurelles |
| Historisation SCD Type 2 | dbt snapshot (scd__clean_trips) | C17 — implémentation des variations de dimensions |

---

## Tableau de synthèse — Couverture des critères RNCP E5

Le tableau ci-dessous récapitule la couverture de chaque critère obligatoire de l'épreuve E5 et de chaque compétence évaluée.

### Critères du référentiel d'évaluation

| Critère RNCP | Section du rapport | Compétence |
|---|---|---|
| Produire une liste des données nécessaires aux analyses envisagées | §2 — Inventaire des 19 colonnes RAW + 4 dimensions de référence + questions métier | C13 |
| Réaliser les modélisations logiques et physiques du DW et des datamarts | §3.2 MLD + §3.3 MPD + data marts (daily summary, zone analysis, hourly patterns) | C13 |
| Configurer les outils pour la mise en place du DW et des datamarts | §4 — Terraform (database, schémas, warehouse) + dbt (matérialisation, schémas cibles) | C14 |
| Configurer les accès aux données pour les équipes d'analyse | §5 — Rôle ANALYST avec SELECT sur FINAL uniquement, matrice des accès | C14 |
| Configurer les accès aux données opérationnelles sources | §5.1 — Rôle TRANSFORM avec SELECT sur RAW | C14 |
| Organiser la phase de test | §8 — 3 niveaux de tests (générique, avancé, métier), 80 PASS / 7 WARN / 0 ERROR, CI/CD automatisé | C14 |
| Rédiger la documentation technique | §9 — dbt docs generate (lineage, catalogue), 9 documents dans docs/, Git/branches | C14 |
| Formaliser un retour d'expérience (cohérence, avantages, difficultés) | §10 — 3 difficultés documentées avec solutions, avantages de la stack, améliorations envisagées | C14 |
| Intégrer les sources de données identifiées aux programmes d'ETL | §6.1 — download_parquet.py (extraction) + merge_dynamic.py (chargement MERGE) | C15 |
| Configurer les zones de sortie des ETL | §6.1.3 (zone sortie ETL Python = RAW) + §6.2 (zone sortie dbt = FINAL) | C15 |
| Programmer les traitements de nettoyage et formatage en respect des schémas physiques | §7 — 6 règles de filtrage, enrichissement (6 colonnes dérivées), typage, conformité MPD §3.3 | C15 |

### Compétences visées

| Compétence | Intitulé RNCP | Sections concernées | Couverture |
|---|---|---|---|
| **C13** | Modéliser la structure des données d'un entrepôt de données en s'appuyant sur les dimensions et les faits afin d'optimiser l'organisation des données pour les requêtes analytiques | §2, §3 | Complète |
| **C14** | Créer un entrepôt de données à partir des paramètres du projet, des contraintes techniques et matérielles et de la modélisation de la structure des données afin de soutenir l'analyse de l'activité et l'aide à la décision | §4.0 (contraintes), §4.1, §4.2, §5, §8, §9, §10 | Complète |
| **C15** | Intégrer les ETL nécessaires en entrée et en sortie d'un entrepôt de données afin de garantir la qualité et le bon formatage des données en respectant les modélisations logiques et physiques préalablement établies | §6, §7 | Complète |

---

## Conclusion

Ce projet démontre la mise en œuvre complète d'un entrepôt de données cloud, depuis l'ingestion des données brutes jusqu'à leur mise à disposition pour les équipes d'analyse, en passant par la modélisation en schéma en étoile, le nettoyage automatisé et la garantie de qualité par les tests.

Les compétences C13 (modélisation dimensionnelle), C14 (création et configuration du DW) et C15 (intégration des ETL) sont couvertes par une solution industrielle, reproductible et entièrement automatisée, conforme aux pratiques actuelles de l'ingénierie des données.

---

*Document rédigé dans le cadre de l'épreuve E5 — Certification RNCP 37638 Data Engineer*
*Organisme évaluateur : Simplon*
