# Big Data — Kelompok 8

Repository tugas mata kuliah Big Data (Kelompok 8: Alif Akbar Arraiyan, Farid Yusron Syabani).
Studi kasus: **Analisis Kecelakaan Lalu Lintas Amerika Serikat (2020–2024)** dengan arsitektur
ETL klasik (Apache Airflow → Apache Beam → Supabase PostgreSQL → Power BI).

## Struktur folder

```
bigdata/
├── README.md
├── data/
│   ├── raw/                         # sumber mentah / snapshot API (diabaikan git)
│   │   ├── nhtsa_api_live.json      # 8.798 kasus dari NHTSA Crash API (diambil via browser)
│   │   └── nhtsa_api_live_20XX.json # respons per tahun
│   └── processed/                   # hasil data wrangling Minggu 3
│       ├── US_Accidents_Cleaned_NHTSA.csv
│       ├── US_Accidents_Cleaned_NHTSA_2020-2024.csv
│       └── US_Accidents_Cleaned_NHTSA_Recent.csv
├── src/                             # skrip gathering & wrangling (path relatif terhadap repo)
│   ├── gather_nhtsa_api.py
│   ├── data_wrangling.py
│   ├── data_wrangling_2020_2024.py
│   ├── data_wrangling_recent.py
│   └── test_api.py
├── docs/                            # arsitektur & laporan minggu sebelumnya
│   ├── Arsitektur_ETL_Klasik_NHTSA_revised.pdf
│   ├── Laporan_Progres_Minggu3.docx
│   └── Laporan_Progres_Minggu3.pdf
└── tugas/
    └── minggu10/
        ├── Tugas_Minggu10_Kelompok8/   # luaran siap dikumpulkan
        │   ├── Source_Code/ETL_Pipeline.ipynb
        │   ├── Dataset/transformed_dataset.csv
        │   ├── Dataset/nhtsa_api_cases.csv
        │   ├── Dataset/supabase_local.db
        │   ├── Documentation/Dokumentasi_ETL.pdf
        │   ├── Documentation/etl_metrics.json
        │   └── Screenshots/01_extract.png ... 07_diagram_implementation.png
        └── Tugas_Minggu10_Kelompok8.zip
```

## Menjalankan pipeline

Butuh Python 3.11+ dengan `pandas`, `numpy`, `nbformat`, `ipykernel`, `nbconvert` dan `reportlab`.

```bash
jupyter nbconvert --to notebook --execute \
  tugas/minggu10/Tugas_Minggu10_Kelompok8/Source_Code/ETL_Pipeline.ipynb \
  --output ETL_Pipeline.ipynb --ExecutePreprocessor.timeout=1200
```

Notebook melakukan otomatis:
1. **Extract** — dataset Kaggle hasil wrangling, snapshot NHTSA Crash API (`GetCaseList`),
   dan referensi state (`GetStates`).
2. **Transform** — konversi tipe tanggal, standardisasi cuaca (81 → 7 grup), validasi nilai,
   join referensi NHTSA, feature engineering, serta transformasi khusus data API.
3. **Load** — `analytics.accidents` dan `analytics.nhtsa_api_cases` ke target storage,
   dengan verifikasi jumlah baris dan checksum.
4. **Integrasi & testing** — satu `run_pipeline()` dengan logging dan tabel pengujian.

Secara default target storage disimulasikan dengan SQLite (`supabase_local.db`) karena
kredensial Supabase tidak tersedia. Untuk koneksi Supabase sungguhan, isi `SUPABASE_DB_URL`
dan panggil `load_to_supabase()` di notebook.

## Catatan

- Endpoint NHTSA Crash API menolak `urllib`/`curl` (HTTP 403) dari environment ini;
  data diambil lewat browser per tahun lalu disimpan sebagai snapshot di `data/raw/`.
- File CSV mentah `US_Accidents_March23.csv` tidak disimpan di repo (ukuran besar);
  letakkan di `data/raw/` jika ingin menjalankan ulang skrip di `src/`.
- Semua angka pada dokumentasi berasal dari `etl_metrics.json` hasil eksekusi nyata.
