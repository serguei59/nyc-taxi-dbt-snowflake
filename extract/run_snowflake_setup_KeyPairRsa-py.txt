import os
import sys
import snowflake.connector
import logging
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# === Configuration du logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def load_private_key(key_path: str, passphrase: bytes):
    """Charge la clé privée RSA depuis le fichier .p8"""
    try:
        with open(key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=passphrase,
                backend=default_backend()
            )
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        logging.info("🔐 Clé privée chargée avec succès.")
        return private_key_bytes
    except Exception as e:
        logging.error(f"❌ Erreur de chargement de la clé privée : {e}")
        sys.exit(1)

def execute_sql_script(cursor, file_path):
    """Exécute un script SQL complet (séparé par ;)"""
    try:
        with open(file_path, "r") as sql_file:
            sql_script = sql_file.read()
        statements = [s.strip() for s in sql_script.split(";") if s.strip()]
        for stmt in statements:
            cursor.execute(stmt)
            logging.info(f"✅ Requête exécutée : {stmt.split()[0]} ...")
    except Exception as e:
        logging.error(f"❌ Erreur d'exécution SQL : {e}")
        sys.exit(1)

def main():
    # === Chargement des variables d'environnement ===
    account = os.environ.get("SNOWFLAKE_ACCOUNT")
    user = os.environ.get("SNOWFLAKE_USER")
    role = os.environ.get("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
    warehouse = os.environ.get("SNOWFLAKE_WAREHOUSE", "")
    database = os.environ.get("SNOWFLAKE_DATABASE", "")
    schema = os.environ.get("SNOWFLAKE_SCHEMA", "")
    private_key_path = os.environ.get("SNOWFLAKE_PRIVATE_KEY")
    private_key_passphrase = os.environ.get("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", "").encode()
    sql_file_path = os.environ.get("SNOWFLAKE_SQL_FILE", "sql/clean_install_nyc_taxi_db_v2.sql")

    # === Validation des entrées ===
    for var_name, var_value in [
        ("SNOWFLAKE_ACCOUNT", account),
        ("SNOWFLAKE_USER", user),
        ("SNOWFLAKE_PRIVATE_KEY", private_key_path)
    ]:
        if not var_value:
            logging.error(f"❌ Variable d'environnement manquante : {var_name}")
            sys.exit(1)

    # === Chargement de la clé privée ===
    private_key_bytes = load_private_key(private_key_path, private_key_passphrase)

    # === Connexion à Snowflake ===
    try:
        conn = snowflake.connector.connect(
            user=user,
            account=account,
            private_key=private_key_bytes,
            role=role,
            warehouse=warehouse or None,
            database=database or None,
            schema=schema or None
        )
        logging.info("✅ Connexion à Snowflake établie.")
    except Exception as e:
        logging.error(f"❌ Échec de la connexion à Snowflake : {e}")
        sys.exit(1)

    # === Exécution du script SQL ===
    try:
        cursor = conn.cursor()
        execute_sql_script(cursor, sql_file_path)
    finally:
        cursor.close()
        conn.close()
        logging.info("🔒 Connexion Snowflake fermée proprement.")

if __name__ == "__main__":
    main()
