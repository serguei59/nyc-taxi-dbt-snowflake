import os
import sys
import json
import requests

def get_env(var):
    val = os.getenv(var)
    if not val:
        print(f"❌ Missing environment variable: {var}", file=sys.stderr)
        sys.exit(1)
    return val

def main():
    account = get_env("SNOWFLAKE_ACCOUNT")
    client_id = get_env("SNOWFLAKE_OAUTH_CLIENT_ID")
    client_secret = get_env("SNOWFLAKE_OAUTH_CLIENT_SECRET")

    token_url = f"https://{account}.snowflakecomputing.com/oauth/token-request"
    payload = {"grant_type": "client_credentials"}

    print("🔹 Requesting OAuth token from Snowflake...")
    resp = requests.post(token_url, data=payload, auth=(client_id, client_secret))
    if resp.status_code != 200:
        print(f"❌ OAuth request failed: {resp.status_code} - {resp.text}", file=sys.stderr)
        sys.exit(1)

    token = resp.json().get("access_token")
    if not token:
        print(f"❌ No access_token in response: {resp.text}", file=sys.stderr)
        sys.exit(1)

    print(token)

if __name__ == "__main__":
    main()
