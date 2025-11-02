import os
import sys
import json
import requests

def get_env_variable(var_name: str) -> str:
    """Récupère une variable d'environnement ou quitte proprement si absente."""
    value = os.environ.get(var_name)
    if not value:
        print(f"❌ Erreur : la variable d'environnement {var_name} est manquante.", file=sys.stderr)
        sys.exit(1)
    return value


def get_snowflake_oauth_token():
    """Récupère un token OAuth Snowflake via l'API REST officielle."""
    # 1️⃣ Lecture des variables d'environnement
    account = get_env_variable("SNOWFLAKE_ACCOUNT")
    client_id = get_env_variable("SNOWFLAKE_OAUTH_CLIENT_ID")
    client_secret = get_env_variable("SNOWFLAKE_OAUTH_CLIENT_SECRET")

    # 2️⃣ URL du endpoint OAuth2 de Snowflake
    token_url = f"https://{account}.snowflakecomputing.com/oauth/token-request"

    # 3️⃣ Corps de la requête (grant_type = client_credentials)
    payload = {
        "grant_type": "client_credentials"
    }

    # 4️⃣ Authentification basique (client_id / client_secret)
    try:
        response = requests.post(
            token_url,
            data=payload,
            auth=(client_id, client_secret),
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion à Snowflake OAuth endpoint : {e}", file=sys.stderr)
        sys.exit(1)

    # 5️⃣ Vérification du code de statut HTTP
    if response.status_code != 200:
        print(f"❌ Requête OAuth échouée ({response.status_code}) : {response.text}", file=sys.stderr)
        sys.exit(1)

    # 6️⃣ Lecture du token JSON
    try:
        token_data = response.json()
        access_token = token_data.get("access_token")
        token_type = token_data.get("token_type", "Bearer")
        if not access_token:
            print(f"❌ Réponse invalide : pas de token trouvé ({token_data})", file=sys.stderr)
            sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Réponse non JSON : {response.text}", file=sys.stderr)
        sys.exit(1)

    print("✅ Token OAuth Snowflake récupéré avec succès.", file=sys.stderr)

    # 7️⃣ Impression du token pour redirection vers un fichier / variable GitHub
    print(access_token)


if __name__ == "__main__":
    get_snowflake_oauth_token()
