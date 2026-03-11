# Runbook — Metabase Docker : diagnostic et résolution du "connection reset"

> Référence technique interne.
> Incident résolu le 2026-03-11.

---

## Contexte

Metabase est utilisé comme couche BI pour exposer le schéma `FINAL` de Snowflake
via le rôle `ANALYST` (lecture seule). Il est déployé localement via Docker.

Commande de démarrage initiale (mode bridge, défaut Docker) :

```bash
docker run -d -p 3000:3000 --name metabase metabase/metabase
```

---

## Symptôme

Metabase initialise correctement (log `Initialization COMPLETE in 17.5 s`),
le container est en état `Up`, le port est mappé (`0.0.0.0:3000->3000/tcp`),
le firewall UFW est inactif — et pourtant :

- Chrome : `ERR_CONNECTION_RESET`
- Firefox : `La connexion a été réinitialisée`
- curl : `(56) Recv failure: Connexion ré-initialisée par le correspondant`

---

## Diagnostic pas à pas

### Étape 1 — Isoler le navigateur

```bash
curl -I http://localhost:3000
```

Résultat : même erreur que le navigateur.
**Conclusion : le navigateur n'est pas en cause.**

### Étape 2 — Vérifier que le port écoute sur l'hôte

```bash
ss -tlnp | grep 3000
```

Résultat :
```
LISTEN 0  4096  0.0.0.0:3000  0.0.0.0:*
LISTEN 0  4096     [::]:3000     [::]:*
```

Le port est bien ouvert côté hôte — c'est le docker-proxy qui écoute.
**Conclusion : le problème n'est pas l'absence d'écoute.**

### Étape 3 — Observer le comportement TCP précis

```bash
curl -v http://localhost:3000
```

Résultat critique :
```
* Trying [::1]:3000...
* Connected to localhost (::1) port 3000   ← connexion TCP établie
> GET / HTTP/1.1
...
* Recv failure: Connexion ré-initialisée par le correspondant  ← reset après connect
```

La connexion TCP s'établit (le `SYN/SYN-ACK/ACK` aboutit),
mais le serveur envoie immédiatement un `RST` sans transmettre de données HTTP.
**Conclusion : la couche TCP fonctionne, c'est la couche applicative ou le proxy qui rompt.**

### Étape 4 — Tester depuis l'intérieur du container

```bash
docker exec metabase wget -q -O- http://localhost:3000/api/health
```

Résultat : `{"status":"ok"}`

Metabase répond parfaitement depuis l'intérieur de son propre container.
**Conclusion : Metabase est sain. Le bug est entre le container et l'hôte.**

---

## Cause racine

En mode **bridge** (réseau Docker par défaut), Docker crée :

```
[navigateur / curl]
        |
    127.0.0.1:3000  (hôte)
        |
   docker-proxy  (processus sur l'hôte, fait le NAT)
        |
   172.17.0.x:3000  (IP interne du container)
        |
   Metabase (JVM, écoute :::3000 en IPv6 dans le container)
```

Le `docker-proxy` acceptait la connexion TCP entrante mais échouait
à la relayer vers le container — provoquant un `RST` immédiat.

Cause probable : incompatibilité entre le mode d'écoute IPv6-only de la JVM Metabase
(`:::3000` sans `0.0.0.0:3000`) et le proxy bridge Docker qui tentait
une connexion en IPv4 vers l'IP interne du container.

**Signal révélateur** : `docker exec ... wget http://localhost:3000` fonctionne
→ Metabase est vivant → le goulot est la couche réseau Docker entre hôte et container.

---

## Résolution

Supprimer le réseau bridge et passer en mode **host** :

```bash
docker stop metabase && docker rm metabase
docker run -d --network host --name metabase metabase/metabase
```

En mode `--network host`, le container partage directement les interfaces réseau
de la machine hôte. Plus de docker-proxy, plus de NAT :
Metabase bind sur `0.0.0.0:3000` de l'hôte directement.

Vérification :

```bash
curl -s http://localhost:3000/api/health
# → {"status":"ok"}
```

---

## Implications de sécurité

| Mode | Isolation réseau | Usage recommandé |
|---|---|---|
| `bridge` (défaut) | Oui — container isolé | Production, multi-containers |
| `host` | Non — partage l'interface hôte | Développement local, démo |

En mode `host`, le container voit tous les ports de la machine hôte et inversement.
Acceptable pour un poste de développement local.
**Ne pas utiliser en production ou sur un serveur multi-utilisateurs.**

---

## Connexion Metabase → Snowflake

Une fois Metabase accessible sur `http://localhost:3000`, configurer la connexion
dans Admin → Databases → Add database → Snowflake :

| Paramètre | Valeur |
|---|---|
| Display name | NYC Taxi DWH |
| Account | `CGSKXSB-JP35471` |
| Username | `LULU` |
| Password | (mot de passe du compte Snowflake) |
| Role | `ANALYST` |
| Warehouse | `NYC_TAXI_WH_RNCP` |
| Database | `NYC_TAXI_DB_RNCP` |
| Schema | `FINAL` |

Le rôle `ANALYST` est en lecture seule sur `FINAL` — il ne peut pas lire
`RAW` ni `STAGING`, conformément au principe de moindre privilège.

---

## Commandes de référence

```bash
# Vérifier si le container tourne déjà
docker ps --filter name=metabase

# Démarrer (si absent)
docker run -d --network host --name metabase metabase/metabase

# Relancer (si container arrêté)
docker start metabase

# Vérifier la santé
curl -s http://localhost:3000/api/health

# Logs en temps réel
docker logs -f metabase

# Arrêter proprement
docker stop metabase
```

---

## Leçons retenues

1. **`docker exec ... wget`** est la commande clé pour isoler un problème réseau Docker :
   si l'appli répond de l'intérieur mais pas de l'extérieur, le bug est dans le réseau Docker,
   pas dans l'application.

2. **`curl -v`** révèle si la connexion TCP s'établit avant le reset — information
   que le navigateur cache derrière un message générique.

3. Le mode `--network host` est un contournement rapide et efficace pour le développement local.
   Si le mode bridge doit être conservé, la solution propre est de forcer Metabase
   à écouter en IPv4 via la variable d'environnement :
   ```bash
   docker run -d -p 3000:3000 -e MB_JETTY_HOST=0.0.0.0 --name metabase metabase/metabase
   ```

4. **UFW inactif ne signifie pas iptables vide** — Docker gère ses propres règles
   iptables indépendamment d'UFW. Toujours vérifier la couche Docker avant de
   chercher côté firewall système.
