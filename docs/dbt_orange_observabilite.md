# 🧾 Restitution Meet-up Ippon x Orange – Implémentation de dbt Core et Observabilité des Données

**Date :** Octobre 2025  
**Lieu :** Lille  
**Organisateurs :** Ippon Technologies & Orange  
**Thématique :** dbt Core, CI/CD et Quality by Design dans les pipelines data industriels  
**Public :** Data Engineers, DataOps, Architectes et responsables qualité des données  

---

## 🎙️ Introduction orale (1 min)

> « Ce meet-up Ippon x Orange a mis en lumière la mise en œuvre concrète de dbt Core dans un environnement industriel complexe.  
L’objectif était d’intégrer la qualité, la traçabilité et l’observabilité des données au cœur du design des pipelines.  
Ce retour d’expérience d’Orange montre comment une démarche *Quality by Design* et un outillage open source bien orchestré permettent de transformer la culture data et de fiabiliser les livrables analytiques. »

---

## 1. 🎯 Contexte et enjeux

Orange a entrepris une **industrialisation de sa chaîne analytique** avec dbt Core pour unifier ses transformations SQL, réduire la dette technique et renforcer la confiance dans les données.  
Le principal enjeu : **garantir la qualité et la traçabilité des modèles de données** dans un contexte multi-équipes.  
Cette démarche s’inscrit dans une philosophie **Lean Data & Quality by Design** : chaque composant du pipeline contribue à la qualité globale.

🔗 [Documentation dbt Labs – Overview](https://docs.getdbt.com/docs/introduction)

---

## 2. 🧠 dbt Core : standardisation et gouvernance

dbt Core apporte une approche d’**ingénierie logicielle appliquée à la donnée** :
- Définition de modèles SQL versionnés dans Git.  
- Gestion des dépendances via `ref()` et packaging modulaire.  
- Documentation et lineage automatique (`dbt docs generate`).  
- Tests unitaires intégrés (`dbt test` + `dbt-utils`).  

Cette approche facilite la **reproductibilité et la collaboration** tout en rendant chaque modèle **auditable et testé**.

🔗 [dbt Core Documentation](https://docs.getdbt.com/docs/core)

---

## 3. ⚙️ CI/CD et automatisation continue

L’intégration de dbt dans une **chaîne CI/CD open source** permet de fiabiliser le cycle de livraison des données.

![dbt pipeline schema](A_flowchart_diagram_in_the_image_illustrates_an_au.png)

### Stack utilisée :
- **GitHub Actions / GitLab CI** pour le déclenchement automatique des builds et tests.  
- **Renovate** pour la mise à jour automatique des dépendances dbt.  
- **dbt-checkpoint** pour la conformité du code.  
- **dbt Project Evaluator** pour l’audit de la structure et des bonnes pratiques.  
- **Elementary** pour l’observabilité et la surveillance continue.

🔗 [Renovate Docs](https://docs.renovatebot.com/)  
🔗 [dbt-checkpoint GitHub](https://github.com/dbt-checkpoint/dbt-checkpoint)  
🔗 [dbt Project Evaluator Docs](https://github.com/dbt-labs/dbt-project-evaluator)  

---

## 4. 🧩 Outils de qualité et d’observabilité

### **a) dbt Project Evaluator**
Outil officiel dbt Labs permettant d’**évaluer la maturité d’un projet dbt**.  
Il détecte les mauvaises pratiques (absence de documentation, tests manquants, modèles non réutilisables, etc.) et fournit un **score global de qualité**.  
Son intégration dans la CI permet d’empêcher la fusion de code non conforme.

### **b) dbt-checkpoint**
Complément utile pour les revues automatiques : il vérifie le respect des conventions (nommage, tags, descriptions).  
Il joue un rôle de **linter SQL/YAML** pour garantir la cohérence du dépôt.

### **c) Elementary**
Outil open source d’**observabilité native pour dbt**.  
Il collecte les résultats de tests, surveille la fraîcheur et la volumétrie, détecte les anomalies et génère des **dashboards automatiques**.  
Elementary apporte une **visibilité transverse sur la santé du pipeline dbt**.

🔗 [Elementary Docs](https://docs.elementary-data.com/)  

---

## 5. 🧪 Tests unitaires et validation des modèles

### **Tests natifs dbt**
- Tests génériques (`unique`, `not_null`, `relationships`, `accepted_values`).  
- Tests personnalisés SQL dans le dossier `/tests`.

### **Tests unitaires (dbt 1.7+)**
- Nouveauté : `unit_tests:` avec fixtures YAML.  
- Problèmes rencontrés : difficulté à *mock* les macros complexes.  
- Solution : isoler les macros dépendantes de la base et simplifier le contexte d’exécution.  

### **Approche alternative : comparaison input/output**
Méthode historique et robuste :
```sql
select * from expected
except
select * from actual
union all
select * from actual
except
select * from expected
```
Cette approche permet de **valider la cohérence métier** indépendamment des macros, idéale pour les environnements complexes.

🔗 [dbt Testing Guide](https://docs.getdbt.com/docs/build/tests)

---

## 6. 🧭 Quality by Design et gouvernance

Orange adopte une approche **préventive** : la qualité est intégrée dès la conception.  
Les principes sont :
1. Définir des tests de qualité au même titre que les transformations.  
2. Documenter et tracer chaque dépendance.  
3. Automatiser le contrôle via CI/CD et observabilité.  

Ce modèle rapproche la data des pratiques de **Software Engineering**, avec un **cycle “To Be Continuous”** :  
- Continuous Integration  
- Continuous Delivery  
- Continuous Quality  
- Continuous Improvement  

🔗 [Quality by Design principles](https://docs.getdbt.com/best-practices)

---

## 7. 🏗️ Synthèse de la stack open source dbt

| Domaine | Outil | Fonction |
|----------|--------|-----------|
| Transformation | **dbt Core** | Modélisation SQL et lineage |
| Conformité code | **dbt-checkpoint** | Vérification des conventions |
| Évaluation projet | **dbt Project Evaluator** | Audit de la structure dbt |
| Observabilité | **Elementary** | Monitoring qualité et anomalies |
| CI/CD | **GitHub Actions / GitLab CI** | Automatisation des tests et déploiements |
| Mises à jour | **Renovate** | Gestion automatique des dépendances |

---

## 8. 🧩 Explication par partie (support oral)

### Partie 1 – Contexte
> dbt a été choisi pour apporter de la rigueur et de la traçabilité dans les transformations SQL.  
> L’enjeu principal est d’unifier les pratiques data tout en rendant chaque modèle contrôlable, versionné et documenté.

### Partie 2 – dbt Core
> dbt Core permet de penser la donnée comme du code : chaque modèle devient un artefact testable et traçable.  
> Cela favorise la collaboration entre data engineers et métiers, et garantit une cohérence dans le temps.

### Partie 3 – CI/CD
> L’automatisation CI/CD est la clé pour fiabiliser la chaîne analytique.  
> Les commits déclenchent automatiquement les tests dbt, les contrôles de qualité et les déploiements, sans intervention manuelle.

### Partie 4 – Outils qualité
> dbt Project Evaluator et dbt-checkpoint jouent le rôle de “code reviewers” automatiques.  
> Elementary complète ce trio en assurant la surveillance continue de la qualité et de la fraîcheur des données.

### Partie 5 – Tests
> Les tests unitaires et de validation renforcent la fiabilité des modèles.  
> Les mocks macros posent parfois problème, d’où l’intérêt de la méthode alternative “comparaison input/output” utilisée chez Orange.

### Partie 6 – Quality by Design
> Orange intègre la qualité dès le design du pipeline, selon les principes Lean et Six Sigma.  
> Cela garantit une culture commune de la qualité et un système auto-surveillé.

### Partie 7 – Enseignements
> L’adoption réussie de dbt repose sur trois piliers : CI/CD maîtrisé, observabilité intégrée, et culture qualité.  
> L’écosystème open source autour de dbt est aujourd’hui suffisamment mature pour un usage industriel.

---

## 🏁 Conclusion orale (1 min)

> « Ce retour d’expérience démontre que dbt Core n’est pas qu’un outil de transformation SQL, mais un véritable moteur de gouvernance et de fiabilité des données.  
> En combinant les pratiques CI/CD, les outils open source de qualité et l’observabilité continue, Orange a mis en place un modèle durable de “Data Reliability by Design”.  
> C’est une illustration concrète de la convergence entre Data Engineering et Software Engineering. »

---
