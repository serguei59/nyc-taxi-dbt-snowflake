
# 🚀 Setup Infrastructure Snowflake avec Terraform

## 1. Objectif
Ce projet provisionne une infrastructure **Snowflake** complète pour le pipeline NYC Taxi, comprenant :
- Un **warehouse** Snowflake (`NYC_TAXI_WH_V2`)
- Une **base de données** (`NYC_TAXI_DB_V2`)
- Trois **schemas** : `RAW`, `STAGING`, `FINAL`
- Deux **tables RAW**
- Un **rôle** `TRANSFORM`
- Un **utilisateur** `DBT`
- Des **grants complets** gérant les privilèges sur les objets existants et futurs.

---

## 2. Structure des fichiers Terraform

```
.
├── main.tf                # Création du warehouse, database et schemas
├── tables-raw.tf          # Création des tables RAW
├── roles_users.tf         # Rôle TRANSFORM et utilisateur DBT
├── grants.tf              # Attribution des privilèges
├── variables.tf           # Variables sensibles (ex: mot de passe DBT)
└── terraform.tfvars       # Valeurs des variables
```

---

## 3. Étapes de déploiement

### 3.1 Initialisation du projet Terraform
```bash
terraform init
```

### 3.2 Vérification du plan d'exécution
```bash
terraform plan
```

### 3.3 Application du déploiement
```bash
terraform apply
```

### 3.4 Suppression complète des ressources
```bash
terraform destroy
```

---

## 4. Points clés de configuration

### 4.1 Dépendances inter-fichiers
L’ordre de création est automatiquement géré par Terraform via les références :
- `roles_users.tf` dépend de `main.tf`
- `grants.tf` dépend de `roles_users.tf` et `main.tf`
- `tables-raw.tf` dépend de `main.tf`

### 4.2 Schémas
Les schémas créés dans `main.tf` sont :
```hcl
resource "snowflake_schema" "raw"     { name = "RAW" }
resource "snowflake_schema" "staging" { name = "STAGING" }
resource "snowflake_schema" "final"   { name = "FINAL" }
```

### 4.3 Tables RAW
Définies dans `tables-raw.tf`, les tables `BUFFER_YELLOW_TAXI_TRIPS_V2` et `YELLOW_TAXI_TRIPS_V2` sont créées avec leurs colonnes dynamiques (via `dynamic "column"`).

### 4.4 Rôle et utilisateur DBT
```hcl
resource "snowflake_account_role" "transform" { name = "TRANSFORM" }
resource "snowflake_user" "dbt_user" {
  name                  = "DBT"
  password              = var.dbt_user_password
  default_role          = snowflake_account_role.transform.name
  default_warehouse     = snowflake_warehouse.transform_wh.name
}
```

### 4.5 Grants
Les privilèges sont accordés via `grants.tf` :
- USAGE/OPERATE sur le warehouse
- USAGE sur la base et les schémas.
- ALL PRIVILEGES sur les tables existantes et futures

---

## 5. Prochaines étapes : Automatisation CI/CD

### 5.1 Objectif
Automatiser le déploiement Terraform via GitHub Actions :
- Validation (`terraform fmt`, `terraform validate`)
- Planification (`terraform plan`)
- Application sur merge (`terraform apply`)

### 5.2 Exemple de workflow YAML à venir
Le fichier `.github/workflows/terraform.yml` sera ajouté ensuite.

---

## 6. Documentation et partage

- Ce document `setup.md` peut être intégré directement dans **MkDocs / GitHub Pages**.
- Une version `.pdf` peut être générée pour la distribution interne.

---

✅ **Jalon atteint :** l’infrastructure Snowflake complète est désormais provisionnée et prête pour l’intégration avec **dbt** et **l’automatisation CI/CD**.
