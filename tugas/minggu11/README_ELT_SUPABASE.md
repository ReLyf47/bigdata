# PANDUAN EKSEKUSI ELT PIPELINE & SUPABASE (MINGGU 11)
**Tugas Minggu 11 — Mata Kuliah Big Data**  
**Kelompok 8:**  
- Alif Akbar Arraiyan (101032330121)  
- Farid Yusron Syabani (101032300192)  

Panduan ini melengkapi tugas Minggu 11 dengan langkah menjalankan ELT Pipeline baik secara lokal (SQLite) maupun langsung ke **Supabase PostgreSQL Cloud** (skema `raw` JSONB $\rightarrow$ skema `analytics`).

---

## 1. Struktur Deliverable Minggu 11

```
tugas/minggu11/
├── README_ELT_SUPABASE.md
├── Tugas_Minggu11_Kelompok8/
│   ├── Source_Code/
│   │   ├── ELT_Pipeline.ipynb
│   │   └── postgres_elt_transform.sql
│   ├── Dataset/
│   │   ├── raw_dataset.csv               (266,656 baris x 21 kolom raw)
│   │   ├── raw_nhtsa_api_cases.csv       (8,798 kasus JSON mentah)
│   │   ├── transformed_dataset.csv       (266,656 baris x 27 kolom analytics)
│   │   ├── nhtsa_api_cases.csv           (8,779 kasus x 12 kolom analytics)
│   │   └── supabase_local.db             (SQLite berisi raw_* dan analytics_*)
│   ├── Documentation/
│   │   ├── Dokumentasi_ELT.pdf
│   │   ├── Dokumentasi_ELT.docx
│   │   └── elt_metrics.json
│   └── Screenshots/
│       ├── 01_extract.png ... 07_diagram_implementation.png
│       └── pipeline_log.txt
└── Tugas_Minggu11_Kelompok8.zip
```

---

## 2. Eksekusi ELT Langsung ke Supabase Cloud (PostgreSQL)

Proyek Supabase Kelompok 8 (`ywzjxhdulvltjmuohagu`) mendukung eksekusi native skema `raw` (JSONB) $\rightarrow$ `analytics` lewat skrip:

```bash
pip install pandas sqlalchemy psycopg2-binary
python src/etl/elt_supabase.py --password PASSWORD_DATABASE_SUPABASE_ANDA
```

Skrip `src/etl/elt_supabase.py` melakukan:
1. **Extract (Raw)**: membaca `US_Accidents_Cleaned_NHTSA_2020-2024.csv` (266.656 baris) dan `nhtsa_api_live.json` (8.798 baris) tanpa cleaning.
2. **Load (Skema `raw`)**: memuat payload mentah ke `raw.accidents_raw`, `raw.nhtsa_api_cases_raw`, dan `raw.nhtsa_states_raw` dalam kolom `JSONB`.
3. **Transform (In-Database SQL)**: menjalankan `postgres_elt_transform.sql` langsung di dalam mesin PostgreSQL Supabase untuk membentuk `analytics.accidents` (266.656 baris) dan `analytics.nhtsa_api_cases` (8.779 baris), serta mempertahankan skema `raw` tetap utuh dan terpisah.

---

## 3. Menjalankan Notebook ELT Secara Lokal

```bash
jupyter nbconvert --to notebook --execute \
  tugas/minggu11/Tugas_Minggu11_Kelompok8/Source_Code/ELT_Pipeline.ipynb \
  --output ELT_Pipeline.ipynb --ExecutePreprocessor.timeout=1200
```
