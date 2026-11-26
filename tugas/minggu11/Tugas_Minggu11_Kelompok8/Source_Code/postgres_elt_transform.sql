-- =============================================================================
-- TUGAS MINGGU 11 — ELT IN-DATABASE SQL TRANSFORMATION (SUPABASE POSTGRESQL)
-- Kelompok 8: Alif Akbar Arraiyan (101032330121), Farid Yusron Syabani (101032300192)
-- Arsitektur Minggu 9: Airbyte -> Supabase (raw JSONB) -> dbt SQL -> Supabase (analytics)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;

-- 1. Model analytics.accidents (setara model dbt yang membaca raw.accidents_raw)
DROP TABLE IF EXISTS analytics.accidents;
CREATE TABLE analytics.accidents AS
WITH states_dim AS (
    SELECT
        UPPER(TRIM(_airbyte_data->>'State')) AS state_code,
        (_airbyte_data->>'NHTSA_State_ID')::INTEGER AS nhtsa_state_id_ref,
        TRIM(_airbyte_data->>'NHTSA_State_Name') AS nhtsa_state_name_ref,
        TRIM(_airbyte_data->>'NHTSA_Region') AS nhtsa_region_ref
    FROM raw.nhtsa_states_raw
),
parsed AS (
    SELECT
        _airbyte_raw_id,
        TRIM(_airbyte_data->>'ID') AS "ID",
        (_airbyte_data->>'Severity')::INTEGER AS "Severity",
        TRIM(_airbyte_data->>'Severity_Label') AS "Severity_Label",
        NULLIF(TRIM(_airbyte_data->>'Start_Time'), '')::TIMESTAMP AS "Start_Time",
        NULLIF(TRIM(_airbyte_data->>'End_Time'), '')::TIMESTAMP AS "End_Time",
        (_airbyte_data->>'Duration_Minutes')::DOUBLE PRECISION AS "Duration_Minutes",
        (_airbyte_data->>'Hour')::INTEGER AS "Hour",
        TRIM(_airbyte_data->>'Day_of_Week') AS "Day_of_Week",
        INITCAP(TRIM(_airbyte_data->>'City')) AS "City",
        INITCAP(TRIM(_airbyte_data->>'County')) AS "County",
        UPPER(TRIM(_airbyte_data->>'State')) AS "State",
        TRIM(_airbyte_data->>'NHTSA_Fatality_Risk_Tier') AS "NHTSA_Fatality_Risk_Tier",
        (_airbyte_data->>'NHTSA_API_Latest_FARS_Year')::INTEGER AS "NHTSA_API_Latest_FARS_Year",
        (_airbyte_data->>'Temperature(F)')::DOUBLE PRECISION AS "Temperature(F)",
        (_airbyte_data->>'Humidity(%)')::DOUBLE PRECISION AS "Humidity(%)",
        (_airbyte_data->>'Visibility(mi)')::DOUBLE PRECISION AS "Visibility(mi)",
        TRIM(_airbyte_data->>'Weather_Condition') AS "Weather_Condition",
        TRIM(_airbyte_data->>'Data_Source') AS "Data_Source"
    FROM raw.accidents_raw
),
dedup AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY "ID" ORDER BY _airbyte_raw_id) AS _rn
    FROM parsed
    WHERE "Start_Time" IS NOT NULL AND "End_Time" IS NOT NULL
),
validated AS (
    SELECT
        d."ID",
        d."Severity",
        d."Severity_Label",
        d."Start_Time",
        d."End_Time",
        d."Start_Time"::DATE AS "Accident_Date",
        EXTRACT(MONTH FROM d."Start_Time")::INTEGER AS "Month",
        d."Hour",
        d."Day_of_Week",
        CASE WHEN EXTRACT(ISODOW FROM d."Start_Time") IN (6, 7) THEN 1 ELSE 0 END AS "Is_Weekend",
        d."Duration_Minutes",
        CASE
            WHEN d."Duration_Minutes" < 30 THEN 'Short (<30m)'
            WHEN d."Duration_Minutes" <= 120 THEN 'Medium (30-120m)'
            ELSE 'Long (>120m)'
        END AS "Duration_Category",
        d."City",
        d."County",
        d."State",
        s.nhtsa_state_id_ref AS "NHTSA_State_ID",
        s.nhtsa_state_name_ref AS "NHTSA_State_Name",
        s.nhtsa_region_ref AS "NHTSA_Region",
        d."NHTSA_Fatality_Risk_Tier",
        d."NHTSA_API_Latest_FARS_Year",
        d."Temperature(F)",
        d."Humidity(%)",
        d."Visibility(mi)",
        d."Weather_Condition",
        CASE
            WHEN LOWER(d."Weather_Condition") LIKE 'n/a%' OR LOWER(d."Weather_Condition") IN ('nan', 'none', 'unknown') THEN 'Other'
            WHEN LOWER(d."Weather_Condition") ~ '(thunder|t-storm|storm|squall|hail)' THEN 'Storm'
            WHEN LOWER(d."Weather_Condition") ~ '(snow|sleet|freezing|wintry|ice)' THEN 'Snow/Ice'
            WHEN LOWER(d."Weather_Condition") ~ '(rain|drizzle|shower|precipitation)' THEN 'Rain'
            WHEN LOWER(d."Weather_Condition") ~ '(fog|mist|haze|smoke|dust)' THEN 'Fog/Haze'
            WHEN LOWER(d."Weather_Condition") ~ '(cloudy|overcast)' THEN 'Cloudy'
            WHEN LOWER(d."Weather_Condition") ~ '(fair|clear)' THEN 'Clear'
            ELSE 'Other'
        END AS "Weather_Group",
        d."Data_Source"
    FROM dedup d
    INNER JOIN states_dim s ON d."State" = s.state_code
    WHERE d._rn = 1
      AND d."Severity" BETWEEN 1 AND 4
      AND d."Duration_Minutes" BETWEEN 0 AND 1440
      AND d."Temperature(F)" BETWEEN -40 AND 125
      AND d."Humidity(%)" BETWEEN 0 AND 100
      AND d."Visibility(mi)" BETWEEN 0 AND 50
)
SELECT
    "ID", "Severity", "Severity_Label", "Start_Time", "End_Time",
    "Accident_Date", "Month", "Hour", "Day_of_Week", "Is_Weekend",
    "Duration_Minutes", "Duration_Category", "City", "County", "State",
    "NHTSA_State_ID", "NHTSA_State_Name", "NHTSA_Region",
    "NHTSA_Fatality_Risk_Tier", "NHTSA_API_Latest_FARS_Year",
    "Temperature(F)", "Humidity(%)", "Visibility(mi)",
    "Weather_Condition", "Weather_Group",
    CASE "Weather_Group"
        WHEN 'Clear' THEN 0 WHEN 'Cloudy' THEN 1 WHEN 'Fog/Haze' THEN 2
        WHEN 'Other' THEN 3 WHEN 'Rain' THEN 4 WHEN 'Snow/Ice' THEN 5
        WHEN 'Storm' THEN 6
    END AS "Weather_Code",
    "Data_Source"
FROM validated
ORDER BY "Start_Time" DESC, "ID" ASC;

-- 2. Model analytics.nhtsa_api_cases (setara model dbt yang membaca raw.nhtsa_api_cases_raw)
DROP TABLE IF EXISTS analytics.nhtsa_api_cases;
CREATE TABLE analytics.nhtsa_api_cases AS
WITH states_dim AS (
    SELECT
        (_airbyte_data->>'NHTSA_State_ID')::INTEGER AS state_id,
        UPPER(TRIM(_airbyte_data->>'State')) AS state_code,
        TRIM(_airbyte_data->>'NHTSA_Region') AS nhtsa_region
    FROM raw.nhtsa_states_raw
),
risk_dim AS (
    SELECT DISTINCT "State", "NHTSA_Fatality_Risk_Tier"
    FROM analytics.accidents
),
parsed AS (
    SELECT
        _airbyte_raw_id,
        (_airbyte_data->>'St_Case')::INTEGER AS "St_Case",
        (_airbyte_data->>'State')::INTEGER AS state_id,
        INITCAP(TRIM(_airbyte_data->>'StateName')) AS "StateName",
        INITCAP(TRIM(REGEXP_REPLACE(_airbyte_data->>'CountyName', '\s*\(\d+\)\s*$', ''))) AS "CountyName",
        (TIMESTAMP 'epoch' + (SUBSTRING(_airbyte_data->>'CrashDate' FROM '/Date\((-?\d+)')::BIGINT / 1000.0) * INTERVAL '1 second') AS "Crash_Date",
        (_airbyte_data->>'Fatals')::INTEGER AS "Fatals",
        (_airbyte_data->>'Peds')::INTEGER AS "Peds",
        (_airbyte_data->>'Persons')::INTEGER AS "Persons",
        (_airbyte_data->>'TotalVehicles')::INTEGER AS "TotalVehicles"
    FROM raw.nhtsa_api_cases_raw
),
valid_dates AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY state_id, "St_Case", "Crash_Date" ORDER BY _airbyte_raw_id) AS _rn
    FROM parsed
    WHERE "Crash_Date" IS NOT NULL
      AND EXTRACT(YEAR FROM "Crash_Date") BETWEEN 2020 AND 2026
)
SELECT
    v."St_Case",
    s.state_code AS "State",
    v."StateName",
    v."CountyName",
    v."Crash_Date",
    v."Fatals",
    v."Peds",
    v."Persons",
    v."TotalVehicles",
    s.nhtsa_region AS "NHTSA_Region",
    COALESCE(r."NHTSA_Fatality_Risk_Tier", 'Low') AS "Fatality_Risk_Tier",
    'NHTSA_CrashAPI_Live' AS "Data_Source"
FROM valid_dates v
INNER JOIN states_dim s ON v.state_id = s.state_id
LEFT JOIN risk_dim r ON s.state_code = r."State"
WHERE v._rn = 1
  AND v."Fatals" >= 1
  AND v."Persons" >= 1
  AND v."TotalVehicles" >= 1
  AND v."Peds" >= 0;
