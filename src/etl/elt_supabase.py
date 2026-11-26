#!/usr/bin/env python3
"""
elt_supabase.py - Run the Week 11 ELT pipeline directly against Supabase PostgreSQL.

Follows the Week 9 ELT architecture:
  1. Extract raw data untouched from Kaggle CSV + NHTSA API snapshot + NHTSA state definitions.
  2. Load raw JSONB payloads into schema `raw` (`raw.accidents_raw`, `raw.nhtsa_api_cases_raw`, `raw.nhtsa_states_raw`).
  3. Transform entirely inside Supabase PostgreSQL via SQL (`postgres_elt_transform.sql`) into schema `analytics`.

Usage:
    python src/elt_supabase.py --password YOUR_SUPABASE_PASSWORD
    # or SUPABASE_PASSWORD=xxx python src/elt_supabase.py
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from psycopg2.extras import execute_values
from sqlalchemy import create_engine

DEFAULT_HOST = "aws-0-ap-southeast-1.pooler.supabase.com"
DEFAULT_PORT = 5432
DEFAULT_USER = "postgres.ywzjxhdulvltjmuohagu"
DEFAULT_DB = "postgres"

NHTSA_STATES = {
    "AK": (2, "Alaska", "West"), "AL": (1, "Alabama", "South"), "AR": (5, "Arkansas", "South"),
    "AZ": (4, "Arizona", "West"), "CA": (6, "California", "West"), "CO": (8, "Colorado", "West"),
    "CT": (9, "Connecticut", "Northeast"), "DC": (11, "District of Columbia", "South"),
    "DE": (10, "Delaware", "South"), "FL": (12, "Florida", "South"), "GA": (13, "Georgia", "South"),
    "HI": (15, "Hawaii", "West"), "IA": (19, "Iowa", "Midwest"), "ID": (16, "Idaho", "West"),
    "IL": (17, "Illinois", "Midwest"), "IN": (18, "Indiana", "Midwest"), "KS": (20, "Kansas", "Midwest"),
    "KY": (21, "Kentucky", "South"), "LA": (22, "Louisiana", "South"), "MA": (25, "Massachusetts", "Northeast"),
    "MD": (24, "Maryland", "South"), "ME": (23, "Maine", "Northeast"), "MI": (26, "Michigan", "Midwest"),
    "MN": (27, "Minnesota", "Midwest"), "MO": (29, "Missouri", "Midwest"), "MS": (28, "Mississippi", "South"),
    "MT": (30, "Montana", "West"), "NC": (37, "North Carolina", "South"), "ND": (38, "North Dakota", "Midwest"),
    "NE": (31, "Nebraska", "Midwest"), "NH": (33, "New Hampshire", "Northeast"),
    "NJ": (34, "New Jersey", "Northeast"), "NM": (35, "New Mexico", "West"), "NV": (32, "Nevada", "West"),
    "NY": (36, "New York", "Northeast"), "OH": (39, "Ohio", "Midwest"), "OK": (40, "Oklahoma", "South"),
    "OR": (41, "Oregon", "West"), "PA": (42, "Pennsylvania", "Northeast"), "PR": (43, "Puerto Rico", "South"),
    "RI": (44, "Rhode Island", "Northeast"), "SC": (45, "South Carolina", "South"),
    "SD": (46, "South Dakota", "Midwest"), "TN": (47, "Tennessee", "South"), "TX": (48, "Texas", "South"),
    "UT": (49, "Utah", "West"), "VA": (51, "Virginia", "South"), "VI": (52, "Virgin Islands", "South"),
    "VT": (50, "Vermont", "Northeast"), "WA": (53, "Washington", "West"), "WI": (55, "Wisconsin", "Midwest"),
    "WV": (54, "West Virginia", "South"), "WY": (56, "Wyoming", "West"),
}


def load_raw_jsonb(raw_conn, table_full_name, rows, source_tag, extracted_at, batch_size=5000):
    """Create raw JSONB landing table and bulk insert untouched records."""
    with raw_conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {table_full_name};")
        cur.execute(
            f"""
            CREATE TABLE {table_full_name} (
                _airbyte_raw_id BIGSERIAL PRIMARY KEY,
                _airbyte_extracted_at TIMESTAMPTZ NOT NULL,
                _airbyte_source TEXT NOT NULL,
                _airbyte_data JSONB NOT NULL
            );
            """
        )
        payload = [(extracted_at, source_tag, json.dumps(r)) for r in rows]
        for i in range(0, len(payload), batch_size):
            execute_values(
                cur,
                f"INSERT INTO {table_full_name} (_airbyte_extracted_at, _airbyte_source, _airbyte_data) VALUES %s",
                payload[i : i + batch_size],
            )
    raw_conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Execute Week 11 ELT pipeline directly on Supabase PostgreSQL.")
    parser.add_argument("--password", "-p", default=os.getenv("SUPABASE_PASSWORD"), help="Supabase database password")
    parser.add_argument("--host", default=os.getenv("SUPABASE_HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.getenv("SUPABASE_PORT", DEFAULT_PORT)))
    parser.add_argument("--user", default=os.getenv("SUPABASE_USER", DEFAULT_USER))
    parser.add_argument("--db", default=os.getenv("SUPABASE_DB", DEFAULT_DB))
    args = parser.parse_args()

    if not args.password:
        print("[-] Error: Database password is required (--password or SUPABASE_PASSWORD).")
        sys.exit(1)

    root = Path(__file__).resolve().parent.parent.parent
    source_csv = root / "data" / "processed" / "US_Accidents_Cleaned_NHTSA_2020-2024.csv"
    api_json = root / "data" / "raw" / "nhtsa_api_live.json"
    sql_path = root / "tugas" / "minggu11" / "Tugas_Minggu11_Kelompok8" / "Source_Code" / "postgres_elt_transform.sql"

    print("[1/3] EXTRACT: Reading raw sources without cleaning...")
    with open(source_csv, encoding="utf-8") as f:
        main_rows = list(csv.DictReader(f))
    api_payload = json.loads(api_json.read_text(encoding="utf-8"))
    api_rows = [item for group in api_payload.get("Results", []) for item in (group if isinstance(group, list) else [group])]
    state_rows = [
        {"State": k, "NHTSA_State_ID": v[0], "NHTSA_State_Name": v[1], "NHTSA_Region": v[2]}
        for k, v in NHTSA_STATES.items()
    ]
    print(f"    Extracted: main={len(main_rows):,}, api={len(api_rows):,}, states={len(state_rows)}")

    dsn = f"postgresql+psycopg2://{args.user}:{args.password}@{args.host}:{args.port}/{args.db}?sslmode=require"
    engine = create_engine(dsn)
    extracted_at = datetime.now(timezone.utc).isoformat()

    print("[2/3] LOAD RAW: Uploading raw JSONB tables to schema `raw`...")
    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
            cur.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
        raw_conn.commit()

        load_raw_jsonb(raw_conn, "raw.accidents_raw", main_rows, "kaggle_csv", extracted_at)
        load_raw_jsonb(raw_conn, "raw.nhtsa_api_cases_raw", api_rows, "nhtsa_crash_api", extracted_at)
        load_raw_jsonb(raw_conn, "raw.nhtsa_states_raw", state_rows, "nhtsa_get_states", extracted_at)

        print("[3/3] TRANSFORM IN-DB: Executing SQL models to populate schema `analytics`...")
        sql_text = sql_path.read_text(encoding="utf-8")
        with raw_conn.cursor() as cur:
            cur.execute(sql_text)
            cur.execute("ALTER TABLE analytics.accidents DISABLE ROW LEVEL SECURITY;")
            cur.execute("ALTER TABLE analytics.nhtsa_api_cases DISABLE ROW LEVEL SECURITY;")
            cur.execute("GRANT USAGE ON SCHEMA analytics TO postgres, anon, authenticated;")
            cur.execute("GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO postgres, anon, authenticated;")
        raw_conn.commit()

        with raw_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM raw.accidents_raw;")
            r_acc = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM raw.nhtsa_api_cases_raw;")
            r_api = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM analytics.accidents;")
            a_acc = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM analytics.nhtsa_api_cases;")
            a_api = cur.fetchone()[0]

        print(f"[+] raw.accidents_raw        : {r_acc:,} rows (preserved)")
        print(f"[+] raw.nhtsa_api_cases_raw  : {r_api:,} rows (preserved)")
        print(f"[+] analytics.accidents      : {a_acc:,} rows")
        print(f"[+] analytics.nhtsa_api_cases: {a_api:,} rows")
    finally:
        raw_conn.close()


if __name__ == "__main__":
    main()
