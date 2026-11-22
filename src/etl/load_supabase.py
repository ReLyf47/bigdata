#!/usr/bin/env python3
"""
load_supabase.py - Utility to load transformed datasets into Supabase PostgreSQL.

Usage:
    python src/load_supabase.py --password YOUR_SUPABASE_PASSWORD
    # or set environment variable SUPABASE_PASSWORD=your_password
    # SUPABASE_PASSWORD=xxx python src/load_supabase.py
"""

import os
import sys
import argparse
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

# Default configuration for Kelompok 8 Supabase project
DEFAULT_HOST = "aws-0-ap-southeast-1.pooler.supabase.com"
DEFAULT_PORT = 5432
DEFAULT_USER = "postgres.ywzjxhdulvltjmuohagu"
DEFAULT_DB = "postgres"
PROJECT_REF = "ywzjxhdulvltjmuohagu"

def main():
    parser = argparse.ArgumentParser(description="Upload transformed data to Supabase PostgreSQL.")
    parser.add_argument("--password", "-p", help="Supabase database password", default=os.getenv("SUPABASE_PASSWORD"))
    parser.add_argument("--host", default=os.getenv("SUPABASE_HOST", DEFAULT_HOST))
    parser.add_argument("--port", default=int(os.getenv("SUPABASE_PORT", DEFAULT_PORT)))
    parser.add_argument("--user", default=os.getenv("SUPABASE_USER", DEFAULT_USER))
    parser.add_argument("--db", default=os.getenv("SUPABASE_DB", DEFAULT_DB))
    parser.add_argument("--schema", default="public", help="Target schema (default: public)")
    parser.add_argument("--chunksize", type=int, default=5000)
    args = parser.parse_args()

    if not args.password:
        print("[-] Error: Database password is required.")
        print("    Pass --password <your_password> or set SUPABASE_PASSWORD environment variable.")
        sys.exit(1)

    # Locate dataset files
    base_dir = Path(__file__).resolve().parents[2]
    dataset_main = base_dir / "tugas" / "minggu10" / "Tugas_Minggu10_Kelompok8" / "Dataset" / "transformed_dataset.csv"
    dataset_api = base_dir / "tugas" / "minggu10" / "Tugas_Minggu10_Kelompok8" / "Dataset" / "nhtsa_api_cases.csv"

    if not dataset_main.exists():
        print(f"[-] Error: Main dataset not found at {dataset_main}")
        sys.exit(1)

    # Build connection URI (Session Pooler IPv4)
    db_uri = f"postgresql+psycopg2://{args.user}:{args.password}@{args.host}:{args.port}/{args.db}?sslmode=require"
    print(f"[*] Connecting to Supabase Session Pooler: {args.host}:{args.port} as {args.user}...")
    
    try:
        engine = create_engine(db_uri)
        with engine.connect() as conn:
            version = conn.exec_driver_sql("SELECT version()").scalar()
            print(f"[+] Successfully connected to database: {version.split(',')[0]}")
            
            # Ensure schema exists and permissions are configured
            if args.schema != "public":
                conn.exec_driver_sql(f"CREATE SCHEMA IF NOT EXISTS {args.schema};")
                print(f"[+] Schema '{args.schema}' verified/created.")

        # 1. Load Main Transformed Dataset
        print(f"[*] Reading {dataset_main.name}...")
        df_main = pd.read_csv(dataset_main)
        print(f"    Loaded {len(df_main):,} rows x {len(df_main.columns)} columns.")
        
        table_main = "nhtsa_crash_analytics" if args.schema == "public" else "accidents"
        print(f"[*] Uploading to {args.schema}.{table_main} (replace mode)...")
        df_main.to_sql(table_main, engine, schema=args.schema, if_exists="replace", index=False, chunksize=args.chunksize)
        
        # 2. Load API Cases Dataset
        if dataset_api.exists():
            print(f"[*] Reading {dataset_api.name}...")
            df_api = pd.read_csv(dataset_api)
            table_api = "nhtsa_api_cases"
            print(f"[*] Uploading to {args.schema}.{table_api} (replace mode)...")
            df_api.to_sql(table_api, engine, schema=args.schema, if_exists="replace", index=False, chunksize=args.chunksize)

        # 3. Disable RLS and grant read access so Power BI can query without permissions errors
        with engine.connect() as conn:
            conn.exec_driver_sql(f"ALTER TABLE {args.schema}.{table_main} DISABLE ROW LEVEL SECURITY;")
            conn.exec_driver_sql(f"GRANT ALL ON {args.schema}.{table_main} TO postgres, anon, authenticated;")
            if dataset_api.exists():
                conn.exec_driver_sql(f"ALTER TABLE {args.schema}.{table_api} DISABLE ROW LEVEL SECURITY;")
                conn.exec_driver_sql(f"GRANT ALL ON {args.schema}.{table_api} TO postgres, anon, authenticated;")
            conn.commit()
            
            count_main = conn.exec_driver_sql(f"SELECT COUNT(*) FROM {args.schema}.{table_main}").scalar()
            print(f"[+] Verified {count_main:,} rows in {args.schema}.{table_main}!")

        print("\n" + "=" * 60)
        print("[+] DATA LOAD SUCCESSFUL!")
        print(f"    Target Table: {args.schema}.{table_main} ({count_main:,} rows)")
        print(f"    Power BI Host: {args.host}")
        print(f"    Power BI User: {args.user}")
        print("=" * 60)

    except Exception as e:
        print(f"[-] Load failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
