#!/usr/bin/env python3
# extract/run_snowflake_api.py
"""
Execute a SQL file against Snowflake using the SQL REST API (POST /api/v2/statements),
with polling for async status, robust logging and exit codes.
Requires:
  - env SNOWFLAKE_ACCOUNT (account identifier, e.g. "xyz123.europe-west-1.azure")
  - env SNOWFLAKE_BEARER_TOKEN (OAuth/JWT Bearer token with rights to execute SQL)
  - optionally SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA, SNOWFLAKE_ROLE
  - env SNOWFLAKE_SQL_FILE (path to SQL script)
"""

import os
import sys
import time
import json
import logging
from typing import Optional

import requests

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("snowflake_api")

# Config
ACCOUNT = os.environ.get("SNOWFLAKE_ACCOUNT")
TOKEN = os.environ.get("SNOWFLAKE_BEARER_TOKEN")
SQL_FILE = os.environ.get("SNOWFLAKE_SQL_FILE", "extract/sql/cleaninstall.sql")
WAREHOUSE = os.environ.get("SNOWFLAKE_WAREHOUSE")
DATABASE = os.environ.get("SNOWFLAKE_DATABASE")
SCHEMA = os.environ.get("SNOWFLAKE_SCHEMA")
ROLE = os.environ.get("SNOWFLAKE_ROLE")
TIMEOUT_SECONDS = int(os.environ.get("SNOWFLAKE_API_TIMEOUT", "600"))  # total timeout for execution
POLL_INTERVAL = float(os.environ.get("SNOWFLAKE_POLL_INTERVAL", "2.0"))  # seconds

if not ACCOUNT:
    logger.error("SNOWFLAKE_ACCOUNT not set")
    sys.exit(2)
if not TOKEN:
    logger.error("SNOWFLAKE_BEARER_TOKEN not set")
    sys.exit(2)
if not os.path.isfile(SQL_FILE):
    logger.error("SQL file not found: %s", SQL_FILE)
    sys.exit(2)

# Endpoint base
# Use https://<account>.snowflakecomputing.com/api/v2/statements
ENDPOINT = f"https://{ACCOUNT}.snowflakecomputing.com/api/v2/statements"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def post_statement(statement: str, timeout: int = 300) -> dict:
    payload = {
        "statement": statement,
        "timeout": timeout,
    }
    if WAREHOUSE:
        payload["warehouse"] = WAREHOUSE
    if DATABASE:
        payload["database"] = DATABASE
    if SCHEMA:
        payload["schema"] = SCHEMA
    if ROLE:
        payload["role"] = ROLE

    resp = requests.post(ENDPOINT, headers=HEADERS, data=json.dumps(payload))
    try:
        content = resp.json()
    except Exception:
        content = {"raw_text": resp.text}
    resp.raise_for_status()
    return content

def get_statement_status(handle: str) -> dict:
    url = f"{ENDPOINT}/{handle}"
    resp = requests.get(url, headers=HEADERS)
    try:
        content = resp.json()
    except Exception:
        content = {"raw_text": resp.text}
    resp.raise_for_status()
    return content

def pretty_print_result(result_json: dict):
    # print status + small summary
    logger.info("Statement response (summary): %s", json.dumps(result_json.get("status", {}), default=str))
    # if data present, print first rows up to N
    if "data" in result_json:
        rows = result_json["data"]
        sample = rows[:10]
        logger.info("Result sample (first %d rows):", len(sample))
        for r in sample:
            logger.info("  %s", r)

def main():
    logger.info("Starting REST API SQL execution. SQL file: %s", SQL_FILE)
    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql = f.read()

    try:
        start = time.time()
        resp = post_statement(sql, timeout=TIMEOUT_SECONDS)
        handle = resp.get("statementHandle")
        status = resp.get("status")
        logger.info("Initial POST returned status=%s, handle=%s", status, handle)

        # If synchronous success or failure
        if status and status.upper() in ("SUCCESS", "FAILED", "ABORTED", "TIMED_OUT"):
            # immediate result
            pretty_print_result(resp)
            if status.upper() == "SUCCESS":
                logger.info("SQL executed successfully (immediate).")
                sys.exit(0)
            else:
                logger.error("SQL execution returned status: %s", status)
                logger.error("Full response:\n%s", json.dumps(resp, indent=2, default=str))
                sys.exit(1)

        # Otherwise poll by handle
        if not handle:
            logger.error("No statement handle returned; full response: %s", json.dumps(resp, indent=2, default=str))
            sys.exit(1)

        # Poll loop
        elapsed = 0.0
        while elapsed < TIMEOUT_SECONDS:
            time.sleep(POLL_INTERVAL)
            elapsed = time.time() - start
            status_resp = get_statement_status(handle)
            s = status_resp.get("status", "").upper()
            logger.info("Polling handle=%s status=%s elapsed=%.1fs", handle, s, elapsed)
            if s == "RUNNING":
                continue
            if s == "SUCCESS":
                pretty_print_result(status_resp)
                logger.info("SQL executed successfully (polled).")
                sys.exit(0)
            else:
                logger.error("SQL execution failed with status: %s", s)
                logger.error("Full status response:\n%s", json.dumps(status_resp, indent=2, default=str))
                sys.exit(1)

        logger.error("Timeout reached while waiting for SQL execution (%.1fs)", TIMEOUT_SECONDS)
        sys.exit(1)

    except requests.HTTPError as he:
        logger.exception("HTTP error during request: %s", he)
        try:
            logger.error("Response content: %s", he.response.text)
        except Exception:
            pass
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected exception: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
