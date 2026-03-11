# Plan de Soutenance Orale — Épreuve E5
## Bloc 3 — Élaborer et maintenir un entrepôt de données

**Durée totale : 10 minutes**
**Compétences évaluées : C13, C14, C15**

---

## Structure chronologique

| Temps | Partie | Contenu |
|---|---|---|
| 0:00 – 1:00 | Introduction | Contexte, objectif, stack |
| 1:00 – 3:00 | Modélisation (C13) | Schéma en étoile, choix de conception |
| 3:00 – 5:30 | Architecture & création (C14) | Snowflake, Terraform, accès |
| 5:30 – 8:30 | ETL & transformations (C15) | Python MERGE, dbt, nettoyage |
| 8:30 – 9:30 | Tests & qualité | 80 PASS / 7 WARN, CI/CD |
| 9:30 – 10:00 | Conclusion & REX | Difficultés, apprentissages |

---

## Script détaillé

### Slide 1 — Introduction (1 min)

> "Ce projet consiste à construire un entrepôt de données cloud pour analyser 50 millions de courses de taxis new-yorkais, sur 23 mois de données (janvier 2024 – septembre 2025).
>
> La stack retenue est : **Snowflake** pour le stockage, **dbt** pour les transformations, **Terraform** pour l'infrastructure as code, et **Python** pour l'ingestion ETL. Le tout est automatisé via un pipeline **GitHub Actions**.
>
> Je vais vous présenter les trois étapes clés : modélisation, création du DW, puis intégration des ETL."

**Ce qu'on montre :** Schéma d'architecture des 4 couches (RAW → STAGING → FINAL → SNAPSHOTS)

---

### Slide 2 — Modélisation en schéma en étoile (C13) — 2 min

> "Le modèle retenu est le **schéma en étoile de Ralph Kimball**, optimisé pour les requêtes analytiques.
>
> J'ai identifié **4 dimensions** et **1 table de faits** centrale :
> - `DIM_DATE` : attributs calendaires (jour, semaine, trimestre, week-end)
> - `DIM_LOCATION` : les 263 zones TLC de New York, regroupées par arrondissement
> - `DIM_PAYMENT_TYPE` : 5 modes de paiement
> - `DIM_RATE_CODE` : 7 codes tarifaires
> - `FCT__TRIPS` : table de faits à ~50 millions de lignes, avec toutes les mesures financières et temporelles
>
> En complément, 3 **data marts pré-agrégés** ont été créés pour Metabase : résumé journalier, analyse par zone, et patterns horaires."

**Ce qu'on montre :** Schéma en étoile avec les tables et leurs clés étrangères

---

### Slide 3 — Création et configuration du DW (C14) — 2 min 30

> "L'infrastructure est entièrement provisionnée par **Terraform**, ce qui garantit la reproductibilité : la base `NYC_TAXI_DB_RNCP`, les 3 schémas fonctionnels, et le warehouse `NYC_TAXI_WH_RNCP` taille MEDIUM, avec auto-suspend à 60 secondes pour l'optimisation des coûts.
>
> Concernant les **accès**, j'applique le principe du moindre privilège avec deux rôles :
> - Le rôle `TRANSFORM`, utilisé par dbt et l'ETL Python : droits complets sur STAGING et FINAL, lecture seule sur RAW
> - Le rôle `ANALYST`, pour les équipes BI et Metabase : SELECT uniquement sur le schéma FINAL
>
> Les équipes d'analyse n'ont aucune visibilité sur les données brutes ni intermédiaires."

**Ce qu'on montre :** Capture Snowflake — liste des schémas + roles, ou extrait Terraform

---

### Slide 4 — Intégration des ETL (C15) — 3 min

**ETL en entrée — Python (1 min 30)**

> "L'ETL d'ingestion est en Python. Le script `download_parquet.py` télécharge les fichiers mensuels depuis l'API NYSE TLC avec un mécanisme de cache — si le fichier existe, on ne le re-télécharge pas.
>
> Le chargement est assuré par `merge_dynamic.py` avec une logique **MERGE** idempotente : la clé de déduplication est composée de 8 colonnes métier — horodatages, vendeur, zones, passagers, montant et distance. Cela garantit qu'on peut relancer le pipeline sans dupliquer les données.
>
> L'ETL gère aussi l'évolution de schéma automatiquement : si Parquet ajoute une colonne (comme `airport_fee`), elle est détectée et ajoutée via `ALTER TABLE`."

**ETL en sortie — dbt (1 min 30)**

> "dbt constitue l'ETL de sortie. Le modèle clé est `stg__clean_trips` : il corrige un bug critique des timestamps — les fichiers Parquet encodent en microsecondes mais Snowflake interprète en secondes, ce qui génère des dates de l'an 54 millions. La correction : diviser l'epoch par 1 000 000.
>
> Ce modèle applique également les règles métier : durée entre 1 et 1440 minutes, distance entre 0,1 et 100 miles, montant positif, passagers entre 1 et 6. Il calcule les colonnes dérivées nécessaires au schéma en étoile : durée, taux de pourboire, heure de prise en charge."

**Ce qu'on montre :** Lineage dbt (graphe RAW → STAGING → FINAL) ou extrait SQL de stg__clean_trips

---

### Slide 5 — Tests et qualité (1 min)

> "La qualité est garantie par 87 tests automatisés organisés en 3 niveaux : tests génériques dbt (not_null, unique, accepted_values), tests avancés via le package `dbt_expectations` (plages de valeurs, distributions), et un test métier SQL custom sur le ratio des codes tarifaires atypiques.
>
> Résultat du dernier pipeline : **80 PASS, 7 WARN, 0 ERROR**. Les warnings concernent des seuils de volume configurés en mode tolérant. Tous les tests critiques sont en mode ERROR — aucune régression n'est acceptée en production."

**Ce qu'on montre :** Capture GitHub Actions — pipeline vert, ou output `dbt test`

---

### Slide 6 — Conclusion & REX (30 sec)

> "Ce projet couvre l'ensemble du cycle de vie d'un entrepôt de données : modélisation, provisionnement, ingestion, transformation et qualité. La principale difficulté a été le bug des timestamps microsecondes, résolu par une correction dans le modèle staging et des tests de régression temporels.
>
> La solution est entièrement automatisée, reproductible et conforme au principe de moindre privilège. Elle est prête pour la consultation analytique via Metabase."

---

## Conseils pour la soutenance

- **Préparez une démo live** : ouvrir Snowflake et montrer les schémas + les tables FINAL peuplées
- **Montrez le pipeline GitHub Actions** : un screenshot du CI/CD vert est très impactant
- **Ayez le lineage dbt** sous la main (`dbt docs serve` en local ou capture d'écran)
- **Anticipez les questions jury** :
  - *"Pourquoi Snowflake plutôt que Redshift ou BigQuery ?"* → Facilité d'intégration avec l'écosystème dbt, provider Terraform stable, Time Travel natif
  - *"Comment garantissez-vous l'idempotence ?"* → MERGE avec clé métier sur 8 colonnes
  - *"Que se passe-t-il si un fichier Parquet est republié avec des corrections ?"* → Le MERGE UPDATE écrase les valeurs modifiées
  - *"Pourquoi des tables permanentes et pas des vues ?"* → Performances de lecture pour Metabase sur 50M de lignes

---

## Slides suggérées (6 slides)

1. **Titre + contexte** — Logo NYC Taxi, chiffres clés (50M courses, 23 mois, 4 couches)
2. **Architecture** — Schéma des 4 zones + stack technique
3. **Schéma en étoile** — MLD avec FCT__TRIPS + 4 dimensions
4. **Infrastructure** — Terraform + rôles Snowflake (matrice accès)
5. **ETL + Transformations** — Lineage dbt + règles de nettoyage clés
6. **Qualité + CI/CD** — Screenshot pipeline GitHub Actions vert + résultats tests

---

*Plan de soutenance — Épreuve E5 — RNCP 37638 Data Engineer*
