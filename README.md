# Big Data — Kelompok 8

Repository tugas mata kuliah Big Data (Kelompok 8: Alif Akbar Arraiyan, Farid Yusron Syabani).
Studi kasus: **Analisis Kecelakaan Lalu Lintas Amerika Serikat (2020–2024)** dengan arsitektur
ETL klasik (Apache Airflow → Apache Beam / Pandas → Supabase PostgreSQL → Power BI).

## Struktur Folder

```
bigdata/
├── README.md
├── data/
│   ├── raw/                         # Sumber mentah / snapshot API (diabaikan git)
│   │   ├── nhtsa_api_live.json      # 8.798 kasus dari NHTSA Crash API
│   │   └── nhtsa_api_live_20XX.json # Respons per tahun (2020-2026)
│   └── processed/                   # Hasil data wrangling Minggu 3
│       ├── US_Accidents_Cleaned_NHTSA.csv
│       ├── US_Accidents_Cleaned_NHTSA_2020-2024.csv
│       └── US_Accidents_Cleaned_NHTSA_Recent.csv
├── src/                             # Skrip gathering, wrangling, & loader
│   ├── gather_nhtsa_api.py
│   ├── data_wrangling.py
│   ├── data_wrangling_2020_2024.py
│   ├── data_wrangling_recent.py
│   ├── load_supabase.py             # Script otomatis muat dataset ke Supabase PostgreSQL
│   └── test_api.py
├── docs/                            # Arsitektur & laporan
│   ├── Arsitektur_ETL_Klasik_NHTSA_revised.pdf
│   ├── Laporan_Progres_Minggu3.docx
│   └── Laporan_Progres_Minggu3.pdf
└── tugas/
    └── minggu10/
        ├── README_WINDOWS_POWERBI.md  # Petunjuk eksekusi & Power BI di Windows
        ├── Tugas_Minggu10_Kelompok8/  # Luaran tugas siap dikumpulkan
        │   ├── PANDUAN_POWERBI_WINDOWS.md
        │   ├── Source_Code/ETL_Pipeline.ipynb
        │   ├── Dataset/transformed_dataset.csv (266,656 baris)
        │   ├── Dataset/nhtsa_api_cases.csv     (8,779 baris)
        │   ├── Dataset/supabase_local.db       (SQLite staging)
        │   ├── Documentation/Dokumentasi_ETL.pdf
        │   ├── Documentation/Dokumentasi_ETL.docx
        │   ├── Documentation/etl_metrics.json
        │   └── Screenshots/01_extract.png ... 07_diagram_implementation.png
        └── Tugas_Minggu10_Kelompok8.zip
```

---

## Panduan untuk PC Windows (Git Pull & Power BI Desktop)

### 1. Menarik Pembaruan di Windows (PowerShell / CMD)
```powershell
cd C:\path\ke\folder\bigdata
git pull origin main
```

### 2. Kredensial Supabase PostgreSQL Cloud (Live)
- **Host (Session Pooler)**: `aws-0-ap-southeast-1.pooler.supabase.com`
- **Port**: `5432`
- **Database**: `postgres`
- **User Name**: `postgres.ywzjxhdulvltjmuohagu`
- **Tabel Target**: `public.nhtsa_crash_analytics` (atau `analytics.accidents`)
- **Project URL**: `https://ywzjxhdulvltjmuohagu.supabase.co`

### 3. Memuat Data ke Supabase Cloud (Opsional)
Jika tabel di Supabase belum terisi data:
```powershell
pip install pandas sqlalchemy psycopg2-binary
python src/load_supabase.py --password PASSWORD_DATABASE_SUPABASE_ANDA
```

### 4. Setup Power BI Desktop di Windows
1. Buka **Power BI Desktop** (unduh gratis dari Microsoft Store).
2. Klik **Get Data** $\rightarrow$ **PostgreSQL database** $\rightarrow$ **Connect**.
3. Masukkan Host: `aws-0-ap-southeast-1.pooler.supabase.com`, Database: `postgres`, Mode: `Import`.
4. Pada tab **Database**, masukkan User: `postgres.ywzjxhdulvltjmuohagu` dan password database Supabase Anda.
   *(Alternatif direct file: Klik Get Data $\rightarrow$ Text/CSV $\rightarrow$ pilih `Dataset/transformed_dataset.csv`)*.
5. Susun komponen dashboard:
   - **3 KPI Cards**: Total Kasus (Distinct ID), Rata-rata Durasi (Menit), Kasus Parah (Severity 4).
   - **Line Chart**: Tren kecelakaan bulanan/tahunan (`Accident_Date`).
   - **Bar Chart**: Sebaran kecelakaan per `NHTSA_Region` dan `State`.
   - **Donut Chart**: Pengaruh cuaca (`Weather_Group`).
   - **Slicers**: Filter Tahun, Wilayah, dan Tingkat Keparahan (`Severity_Label`).
6. Klik **Publish** di pojok kanan atas, masuk dengan akun Telkom University (`relyff@student.telkomuniversity.ac.id`), dan pilih **`My workspace`** untuk menayangkan dashboard di [https://app.powerbi.com](https://app.powerbi.com).

*Panduan visualisasi dan formula DAX lengkap tersedia di: `tugas/minggu10/Tugas_Minggu10_Kelompok8/PANDUAN_POWERBI_WINDOWS.md`.*

---

## Menjalankan Pipeline Lokal (Jupyter Notebook)

Butuh Python 3.11+ dengan dependensi: `pandas`, `numpy`, `nbformat`, `ipykernel`, `nbconvert`, dan `reportlab`.

```bash
jupyter nbconvert --to notebook --execute \
  tugas/minggu10/Tugas_Minggu10_Kelompok8/Source_Code/ETL_Pipeline.ipynb \
  --output ETL_Pipeline.ipynb --ExecutePreprocessor.timeout=1200
```

Pipeline melakukan:
1. **Extract**: Dataset Kaggle hasil wrangling, snapshot NHTSA Crash API (`GetCaseList`), dan referensi state (`GetStates`).
2. **Transform**: Konversi tipe tanggal, standardisasi cuaca (81 $\rightarrow$ 7 grup), validasi rentang, join referensi NHTSA, feature engineering.
3. **Load**: `analytics.accidents` (266.656 baris) dan `analytics.nhtsa_api_cases` (8.779 baris) dengan checksum verification.
4. **Integrasi & Testing**: Eksekusi end-to-end `run_pipeline()` dalam 16.97 detik.

---

## Catatan
- Semua metrik performa dan checksum pada dokumentasi berasal dari `etl_metrics.json` hasil eksekusi nyata.
