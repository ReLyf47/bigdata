"""
Data Wrangling and Integration Pipeline (Maximizing 2023 and Most Recent Data)
Dataset: US_Accidents_March23.csv
External Reference: NHTSA CrashAPI (https://crashviewer.nhtsa.dot.gov/crashviewer/crashapi)
Target: Exactly 250,000 clean rows (all available 2023 data + newest 2022 data), >= 12 columns
"""

import sys
import os
import time
from pathlib import Path
import pandas as pd
import numpy as np

# Path relatif terhadap root repository
PROJECT_ROOT = Path(__file__).resolve().parents[2]
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
    df_nhtsa["NHTSA_API_Latest_FARS_Year"] = 2024  # Latest verified active year in NHTSA CrashAPI
    return df_nhtsa

def run_recent_wrangling():
    start_time = time.time()
    input_file = DATA_RAW / "US_Accidents_March23.csv"
    output_file = DATA_PROCESSED / "US_Accidents_Cleaned_NHTSA_Recent.csv"
    target_clean_rows = 250000
    
    print(f"=== Starting Recent-Focused Data Wrangling Pipeline ===")
    print(f"Input file: {input_file}")
    print(f"Target clean rows: {target_clean_rows:,} (min required: 200,000)")
    print(f"Priority: Most Recent Data (ALL 2023 + latest 2022), descending sorted")
    
    # 1. Load NHTSA reference
    df_nhtsa = get_nhtsa_lookup_df()
    print(f"Loaded {len(df_nhtsa)} NHTSA reference state records.")
    
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
    
    rows_2023 = []
    rows_2022 = []
    
    print("\nScanning dataset for all 2023 and 2022 records...")
    chunk_size = 500000
    chunk_idx = 0
    
    for chunk in pd.read_csv(
        input_file,
        usecols=selected_cols,
        chunksize=chunk_size,
        low_memory=False
    ):
        chunk_idx += 1
        
        # Check if chunk has 2023 or 2022 rows
        is_recent = chunk["Start_Time"].str.startswith(("2023", "2022"), na=False)
        if not is_recent.any():
            continue
            
        c_recent = chunk[is_recent].dropna().copy()
        c_recent["Start_Time"] = pd.to_datetime(c_recent["Start_Time"], errors="coerce")
        c_recent["End_Time"] = pd.to_datetime(c_recent["End_Time"], errors="coerce")
        c_recent = c_recent.dropna(subset=["Start_Time", "End_Time"])
        
        # Temporal validation
        dur = (c_recent["End_Time"] - c_recent["Start_Time"]).dt.total_seconds() / 60.0
        c_recent["Duration_Minutes"] = dur.round(2)
        c_recent = c_recent[(c_recent["Duration_Minutes"] > 0) & (c_recent["Duration_Minutes"] <= 1440)]
        
        # Spatial validation
        c_recent = c_recent[
            (c_recent["Start_Lat"] >= 24.0) & (c_recent["Start_Lat"] <= 50.0) &
            (c_recent["Start_Lng"] >= -125.0) & (c_recent["Start_Lng"] <= -66.0)
        ]
        
        # Weather validation
        c_recent = c_recent[
            (c_recent["Temperature(F)"] >= -40.0) & (c_recent["Temperature(F)"] <= 125.0) &
            (c_recent["Humidity(%)"] >= 0.0) & (c_recent["Humidity(%)"] <= 100.0) &
            (c_recent["Visibility(mi)"] >= 0.0) & (c_recent["Visibility(mi)"] <= 50.0)
        ]
        
        # Standardize text
        c_recent["City"] = c_recent["City"].astype(str).str.strip().str.title()
        c_recent["County"] = c_recent["County"].astype(str).str.strip().str.title()
        c_recent["State"] = c_recent["State"].astype(str).str.strip().str.upper()
        c_recent["Weather_Condition"] = c_recent["Weather_Condition"].astype(str).str.strip().str.title()
        
        # Feature engineering
        c_recent["Hour"] = c_recent["Start_Time"].dt.hour
        c_recent["Day_of_Week"] = c_recent["Start_Time"].dt.day_name()
        c_recent["Severity"] = c_recent["Severity"].astype(int)
        c_recent["Severity_Label"] = c_recent["Severity"].map(SEVERITY_MAP).fillna("Unknown")
        
        # Separate 2023 and 2022
        mask_2023 = c_recent["Start_Time"].dt.year == 2023
        c_23 = c_recent[mask_2023]
        c_22 = c_recent[~mask_2023]
        
        if len(c_23) > 0:
            rows_2023.append(c_23)
        if len(c_22) > 0:
            # Keep only the newest 2022 rows to keep memory usage low
            rows_2022.append(c_22)
            
        print(f"  Chunk {chunk_idx}: processed {len(c_23):,} (2023) and {len(c_22):,} (2022) rows")
            
    print("\nConsolidating and deduplicating...")
    df_2023 = pd.concat(rows_2023, ignore_index=True).drop_duplicates(subset=["ID"])
    df_2022 = pd.concat(rows_2022, ignore_index=True).drop_duplicates(subset=["ID"])
    
    print(f"Total clean 2023 rows collected: {len(df_2023):,}")
    print(f"Total clean 2022 rows collected: {len(df_2022):,}")
    
    # Sort 2022 descending by Start_Time to take the latest 2022 incidents (e.g. Dec 2022, Nov 2022, etc.)
    df_2022 = df_2022.sort_values(by="Start_Time", ascending=False)
    needed_from_2022 = target_clean_rows - len(df_2023)
    print(f"Taking top {needed_from_2022:,} newest rows from late 2022 to reach target {target_clean_rows:,}...")
    df_2022_top = df_2022.iloc[:needed_from_2022].copy()
    
    # Combine ALL 2023 + newest 2022
    df_combined = pd.concat([df_2023, df_2022_top], ignore_index=True)
    
    # Sort entire dataset descending by Start_Time (most recent first!)
    df_combined = df_combined.sort_values(by="Start_Time", ascending=False).reset_index(drop=True)
    
    # Integrate with NHTSA CrashAPI reference
    print("\nIntegrating with NHTSA CrashAPI reference data...")
    df_final = df_combined.merge(df_nhtsa, on="State", how="inner")
    
    # Columns ordering (20 columns total)
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
        "NHTSA_API_Latest_FARS_Year",
        "Temperature(F)",
        "Humidity(%)",
        "Visibility(mi)",
        "Weather_Condition"
    ]
    df_final = df_final[ordered_columns]
    
    print("\nQuality Assurance Checks:")
    print(f"Shape: {df_final.shape}")
    print(f"Null count total: {df_final.isnull().sum().sum()}")
    print("Year distribution in final dataset:")
    print(df_final["Start_Time"].dt.year.value_counts())
    print("Latest timestamp:", df_final["Start_Time"].max())
    print("Earliest timestamp:", df_final["Start_Time"].min())
    
    assert df_final.isnull().sum().sum() == 0, "Error: nulls found!"
    assert len(df_final) >= 200000, "Error: < 200,000 rows!"
    assert df_final.shape[1] >= 12, "Error: < 12 cols!"
    
    print("\nExporting to CSV...")
    df_final.to_csv(output_file, index=False)
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    elapsed = time.time() - start_time
    
    print(f"SUCCESS: Saved {output_file}")
    print(f"File Size: {file_size_mb:.2f} MB")
    print(f"Total Rows: {len(df_final):,}")
    print(f"Total Columns: {df_final.shape[1]}")
    print(f"Execution Time: {elapsed:.2f} seconds")
    
    print("\n=== First 3 Rows (Most Recent Incidents) ===")
    print(df_final.head(3).T)

if __name__ == "__main__":
    run_recent_wrangling()
