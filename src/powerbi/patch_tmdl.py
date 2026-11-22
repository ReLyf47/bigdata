import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
tmdl_path = str(PROJECT_ROOT / 'tugas' / 'minggu10' / 'powerbi_project' / 'BigData.SemanticModel' / 'definition' / 'tables' / 'public nhtsa_crash_analytics.tmdl')
with open(tmdl_path, 'r', encoding='utf-8') as f:
    content = f.read()

measures = (
    "\tmeasure 'Total Cases' = DISTINCTCOUNT('public nhtsa_crash_analytics'[case_id])\n"
    "\t\tformatString: #,##0\n"
    "\t\tlineageTag: 7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d\n\n"
    "\tmeasure 'Total Fatalities' = SUM('public nhtsa_crash_analytics'[total_fatalities])\n"
    "\t\tformatString: #,##0\n"
    "\t\tlineageTag: 8b9c0d1e-2f3a-4b5c-6d7e-8f9a0b1c2d3e\n\n"
    "\tmeasure 'Total Vehicles' = SUM('public nhtsa_crash_analytics'[total_vehicles])\n"
    "\t\tformatString: #,##0\n"
    "\t\tlineageTag: 9c0d1e2f-3a4b-5c6d-7e8f-9a0b1c2d3e4f\n\n"
    "\tmeasure 'Avg Fatalities' = AVERAGE('public nhtsa_crash_analytics'[total_fatalities])\n"
    "\t\tformatString: 0.00\n"
    "\t\tlineageTag: 0d1e2f3a-4b5c-6d7e-8f9a-0b1c2d3e4f5a\n\n"
)

target = "\tlineageTag: bb406ded-10ab-49a4-8568-389081555116\n"
if target in content and "measure 'Total Cases'" not in content:
    content = content.replace(target, target + "\n" + measures, 1)
    with open(tmdl_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Measures added successfully.")
else:
    print("Already present or target not found.")
