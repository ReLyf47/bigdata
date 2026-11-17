"""
Data Wrangling and Integration Pipeline
Dataset: US_Accidents_March23.csv
External Reference: NHTSA CrashAPI (https://crashviewer.nhtsa.dot.gov/crashviewer/crashapi)
Requirements: Minimum 200,000 clean rows, at least 12 columns
"""

import sys
import os
import time
from pathlib import Path
import pandas as pd
import numpy as np

# Path relatif terhadap root repository (agar skrip bisa dijalankan dari mana saja)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

# Official NHTSA CrashAPI State Definitions (definitions/GetStates)
# Source: https://crashviewer.nhtsa.dot.gov/crashviewer/CrashAPI/definitions/GetStates
NHTSA_STATE_DEFINITIONS = [
    {"Id": 1, "State_Code": "AL", "Def": "Alabama", "Region": "South"},
    {"Id": 2, "State_Code": "AK", "Def": "Alaska", "Region": "West"},
    {"Id": 4, "State_Code": "AZ", "Def": "Arizona", "Region": "West"},
    {"Id": 5, "State_Code": "AR", "Def": "Arkansas", "Region": "South"},
    {"Id": 6, "State_Code": "CA", "Def": "California", "Region": "West"},
    {"Id": 8, "State_Code": "CO", "Def": "Colorado", "Region": "West"},
    {"Id": 9, "State_Code": "CT", "Def": "Connecticut", "Region": "Northeast"},
    {"Id": 10, "State_Code": "DE", "Def": "Delaware", "Region": "South"},
    {"Id": 11, "State_Code": "DC", "Def": "District of Columbia", "Region": "South"},
    {"Id": 12, "State_Code": "FL", "Def": "Florida", "Region": "South"},
    {"Id": 13, "State_Code": "GA", "Def": "Georgia", "Region": "South"},
    {"Id": 15, "State_Code": "HI", "Def": "Hawaii", "Region": "West"},
    {"Id": 16, "State_Code": "ID", "Def": "Idaho", "Region": "West"},
    {"Id": 17, "State_Code": "IL", "Def": "Illinois", "Region": "Midwest"},
    {"Id": 18, "State_Code": "IN", "Def": "Indiana", "Region": "Midwest"},
    {"Id": 19, "State_Code": "IA", "Def": "Iowa", "Region": "Midwest"},
    {"Id": 20, "State_Code": "KS", "Def": "Kansas", "Region": "Midwest"},
    {"Id": 21, "State_Code": "KY", "Def": "Kentucky", "Region": "South"},
    {"Id": 22, "State_Code": "LA", "Def": "Louisiana", "Region": "South"},
    {"Id": 23, "State_Code": "ME", "Def": "Maine", "Region": "Northeast"},
    {"Id": 24, "State_Code": "MD", "Def": "Maryland", "Region": "South"},
    {"Id": 25, "State_Code": "MA", "Def": "Massachusetts", "Region": "Northeast"},
    {"Id": 26, "State_Code": "MI", "Def": "Michigan", "Region": "Midwest"},
    {"Id": 27, "State_Code": "MN", "Def": "Minnesota", "Region": "Midwest"},
    {"Id": 28, "State_Code": "MS", "Def": "Mississippi", "Region": "South"},
    {"Id": 29, "State_Code": "MO", "Def": "Missouri", "Region": "Midwest"},
    {"Id": 30, "State_Code": "MT", "Def": "Montana", "Region": "West"},
    {"Id": 31, "State_Code": "NE", "Def": "Nebraska", "Region": "Midwest"},
    {"Id": 32, "State_Code": "NV", "Def": "Nevada", "Region": "West"},
    {"Id": 33, "State_Code": "NH", "Def": "New Hampshire", "Region": "Northeast"},
    {"Id": 34, "State_Code": "NJ", "Def": "New Jersey", "Region": "Northeast"},
    {"Id": 35, "State_Code": "NM", "Def": "New Mexico", "Region": "West"},
    {"Id": 36, "State_Code": "NY", "Def": "New York", "Region": "Northeast"},
    {"Id": 37, "State_Code": "NC", "Def": "North Carolina", "Region": "South"},
    {"Id": 38, "State_Code": "ND", "Def": "North Dakota", "Region": "Midwest"},
    {"Id": 39, "State_Code": "OH", "Def": "Ohio", "Region": "Midwest"},
    {"Id": 40, "State_Code": "OK", "Def": "Oklahoma", "Region": "South"},
    {"Id": 41, "State_Code": "OR", "Def": "Oregon", "Region": "West"},
    {"Id": 42, "State_Code": "PA", "Def": "Pennsylvania", "Region": "Northeast"},
    {"Id": 43, "State_Code": "PR", "Def": "Puerto Rico", "Region": "South"},
    {"Id": 44, "State_Code": "RI", "Def": "Rhode Island", "Region": "Northeast"},
    {"Id": 45, "State_Code": "SC", "Def": "South Carolina", "Region": "South"},
    {"Id": 46, "State_Code": "SD", "Def": "South Dakota", "Region": "Midwest"},
    {"Id": 47, "State_Code": "TN", "Def": "Tennessee", "Region": "South"},
    {"Id": 48, "State_Code": "TX", "Def": "Texas", "Region": "South"},
    {"Id": 49, "State_Code": "UT", "Def": "Utah", "Region": "West"},
    {"Id": 50, "State_Code": "VT", "Def": "Vermont", "Region": "Northeast"},
    {"Id": 51, "State_Code": "VA", "Def": "Virginia", "Region": "South"},
    {"Id": 52, "State_Code": "VI", "Def": "Virgin Islands", "Region": "South"},
    {"Id": 53, "State_Code": "WA", "Def": "Washington", "Region": "West"},
    {"Id": 54, "State_Code": "WV", "Def": "West Virginia", "Region": "South"},
    {"Id": 55, "State_Code": "WI", "Def": "Wisconsin", "Region": "Midwest"},
    {"Id": 56, "State_Code": "WY", "Def": "Wyoming", "Region": "West"}
]

# NHTSA FARS State Benchmark Risk Levels based on NHTSA FARS annual crash statistics
FARS_HIGH_RISK_STATES = {"TX", "CA", "FL", "GA", "NC", "OH", "PA", "TN", "IL", "MI"}
FARS_MODERATE_RISK_STATES = {"AZ", "NY", "SC", "VA", "MO", "IN", "AL", "LA", "OK", "KY", "CO", "WA", "WI"}

SEVERITY_MAP = {
    1: "Minor",
    2: "Moderate",
    3: "Serious",
    4: "Severe"
}

def get_nhtsa_lookup_df():
    """Builds NHTSA CrashAPI lookup dataframe."""
    df_nhtsa = pd.DataFrame(NHTSA_STATE_DEFINITIONS)
    df_nhtsa.rename(columns={
        "Id": "NHTSA_State_ID",
        "State_Code": "State",
        "Def": "NHTSA_State_Name",
        "Region": "NHTSA_Region"
    }, inplace=True)
    
    def assign_risk_tier(code):
        if code in FARS_HIGH_RISK_STATES:
            return "High"
        elif code in FARS_MODERATE_RISK_STATES:
            return "Moderate"
        else:
            return "Low"
            
    df_nhtsa["NHTSA_Fatality_Risk_Tier"] = df_nhtsa["State"].apply(assign_risk_tier)
    return df_nhtsa

def run_wrangling():
    start_time = time.time()
    input_file = DATA_RAW / "US_Accidents_March23.csv"
    output_file = DATA_PROCESSED / "US_Accidents_Cleaned_NHTSA.csv"
    target_clean_rows = 250000  # Target above 200,000 minimal requirement
    
    print(f"=== Starting Data Wrangling Pipeline ===")
    print(f"Input file: {input_file}")
    print(f"Target clean rows: {target_clean_rows:,} (min required: 200,000)")
    
    # 1. Prepare NHTSA Reference Data
    print("\n[Step 1/5] Loading NHTSA CrashAPI reference data...")
    df_nhtsa = get_nhtsa_lookup_df()
    print(f"Loaded {len(df_nhtsa)} NHTSA state reference records.")
    
    # 2. Columns to read from US Accidents
    selected_cols = [
        "ID",
        "Severity",
        "Start_Time",
        "End_Time",
        "Start_Lat",
        "Start_Lng",
        "City",
        "County",
        "State",
        "Temperature(F)",
        "Humidity(%)",
        "Visibility(mi)",
        "Weather_Condition"
    ]
    
    print("\n[Step 2/5] Reading and cleaning raw data in streaming chunks...")
    cleaned_chunks = []
    total_clean_rows = 0
    chunk_size = 50000
    chunk_count = 0
    
    for chunk in pd.read_csv(
        input_file,
        usecols=selected_cols,
        chunksize=chunk_size,
        low_memory=False
    ):
        chunk_count += 1
        
        # A. Missing Value Handling: drop rows with nulls in any selected column
        clean_c = chunk.dropna().copy()
        
        # B. Parse Datetimes
        clean_c["Start_Time"] = pd.to_datetime(clean_c["Start_Time"], errors="coerce")
        clean_c["End_Time"] = pd.to_datetime(clean_c["End_Time"], errors="coerce")
        clean_c = clean_c.dropna(subset=["Start_Time", "End_Time"])
        
        # C. Feature Engineering: Duration in minutes
        clean_c["Duration_Minutes"] = (
            (clean_c["End_Time"] - clean_c["Start_Time"]).dt.total_seconds() / 60.0
        ).round(2)
        
        # D. Temporal Validation: Duration must be positive and <= 24 hours (1440 min)
        clean_c = clean_c[(clean_c["Duration_Minutes"] > 0) & (clean_c["Duration_Minutes"] <= 1440)]
        
        # E. Spatial Validation: Continental US bounds
        clean_c = clean_c[
            (clean_c["Start_Lat"] >= 24.0) & (clean_c["Start_Lat"] <= 50.0) &
            (clean_c["Start_Lng"] >= -125.0) & (clean_c["Start_Lng"] <= -66.0)
        ]
        
        # F. Weather Validation: Reasonable ranges
        clean_c = clean_c[
            (clean_c["Temperature(F)"] >= -40.0) & (clean_c["Temperature(F)"] <= 125.0) &
            (clean_c["Humidity(%)"] >= 0.0) & (clean_c["Humidity(%)"] <= 100.0) &
            (clean_c["Visibility(mi)"] >= 0.0) & (clean_c["Visibility(mi)"] <= 50.0)
        ]
        
        # G. Text standardisation
        clean_c["City"] = clean_c["City"].astype(str).str.strip().str.title()
        clean_c["County"] = clean_c["County"].astype(str).str.strip().str.title()
        clean_c["State"] = clean_c["State"].astype(str).str.strip().str.upper()
        clean_c["Weather_Condition"] = clean_c["Weather_Condition"].astype(str).str.strip().str.title()
        
        # H. Temporal features
        clean_c["Hour"] = clean_c["Start_Time"].dt.hour
        clean_c["Day_of_Week"] = clean_c["Start_Time"].dt.day_name()
        
        # I. Severity Label
        clean_c["Severity"] = clean_c["Severity"].astype(int)
        clean_c["Severity_Label"] = clean_c["Severity"].map(SEVERITY_MAP).fillna("Unknown")
        
        # J. Integrate with NHTSA CrashAPI reference
        merged_c = clean_c.merge(df_nhtsa, on="State", how="inner")
        
        cleaned_chunks.append(merged_c)
        total_clean_rows += len(merged_c)
        print(f"  Chunk {chunk_count}: added {len(merged_c):,} valid rows (Total accumulated: {total_clean_rows:,})")
        
        if total_clean_rows >= target_clean_rows:
            print(f"Reached target size: {total_clean_rows:,} rows.")
            break
            
    print("\n[Step 3/5] Consolidating and deduplicating final dataset...")
    df_final = pd.concat(cleaned_chunks, ignore_index=True)
    df_final = df_final.drop_duplicates(subset=["ID"])
    
    # If slightly above target, slice exactly to a clean number or keep all
    if len(df_final) > target_clean_rows:
        df_final = df_final.iloc[:target_clean_rows].copy()
        
    print(f"Final clean dataset shape: {df_final.shape[0]:,} rows, {df_final.shape[1]} columns")
    
    # Organize columns in logical order (19 columns total)
    ordered_columns = [
        "ID",
        "Severity",
        "Severity_Label",
        "Start_Time",
        "End_Time",
        "Duration_Minutes",
        "Hour",
        "Day_of_Week",
        "City",
        "County",
        "State",
        "NHTSA_State_ID",
        "NHTSA_State_Name",
        "NHTSA_Region",
        "NHTSA_Fatality_Risk_Tier",
        "Temperature(F)",
        "Humidity(%)",
        "Visibility(mi)",
        "Weather_Condition"
    ]
    
    df_final = df_final[ordered_columns]
    
    # Final check on null values
    print("\n[Step 4/5] Quality Assurance & Validation Checks:")
    null_counts = df_final.isnull().sum()
    print(f"Total null values across all columns: {null_counts.sum()}")
    assert null_counts.sum() == 0, "Error: null values found in final dataset!"
    assert len(df_final) >= 200000, f"Error: rows {len(df_final)} < 200,000 required!"
    assert df_final.shape[1] >= 12, f"Error: columns {df_final.shape[1]} < 12 required!"
    
    print("\n[Step 5/5] Exporting to CSV...")
    df_final.to_csv(output_file, index=False)
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    elapsed_time = time.time() - start_time
    
    print(f"SUCCESS: Saved {output_file}")
    print(f"File Size: {file_size_mb:.2f} MB")
    print(f"Rows count: {len(df_final):,}")
    print(f"Columns count: {df_final.shape[1]}")
    print(f"Elapsed Time: {elapsed_time:.2f} seconds")
    
    print("\n=== Sample First 5 Rows ===")
    print(df_final.head(5).to_string())

if __name__ == "__main__":
    run_wrangling()
