# load/snowflake_utils.py
import os
import snowflake.connector
import pandas as pd

# ✅ 1. Connexion unique à Snowflake
def get_connection():
    """
    Initialise une connexion Snowflake à partir des variables d'environnement (.env).
    Variables requises :
      SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT,
      SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA, SNOWFLAKE_ROLE
    """
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE"),
        )
        return conn
    except Exception as e:
        raise RuntimeError(f"❌ Erreur de connexion Snowflake : {e}")

# ✅ 2. Exécution d'une requête SQL classique
def execute_sql(sql: str, verbose: bool = False):
    """
    Exécute une requête SQL et renvoie le résultat sous forme de liste.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if verbose:
            print(f"[SQL] {sql}")

        cursor.execute(sql)
        results = cursor.fetchall() if cursor.description else []

        conn.commit()
        return results

    except Exception as e:
        conn.rollback()
        print(f"⚠️ Erreur d'exécution SQL : {e}")
        raise

    finally:
        cursor.close()
        conn.close()

# ✅ 3. Exécution d'une requête SQL avec sortie en DataFrame Pandas
def execute_sql_df(sql: str, verbose: bool = False) -> pd.DataFrame:
    """
    Exécute une requête SQL et renvoie un DataFrame pandas.
    """
    conn = get_connection()

    try:
        if verbose:
            print(f"[SQL DF] {sql}")

        df = pd.read_sql(sql, conn)
        return df

    except Exception as e:
        print(f"⚠️ Erreur lors de la récupération du DataFrame : {e}")
        raise

    finally:
        conn.close()
