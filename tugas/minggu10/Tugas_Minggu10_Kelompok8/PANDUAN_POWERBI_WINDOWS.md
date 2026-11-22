# PANDUAN INTEGRASI SUPABASE & POWER BI DESKTOP (WINDOWS)
**Tugas Minggu 10 — Mata Kuliah Big Data**  
**Kelompok 8:**  
- Alif Akbar Arraiyan (101032330121)  
- Farid Yusron Syabani (101032300192)  

Dokumen ini berisi panduan teknis lengkap untuk menarik (pull) repository di PC Windows, memuat data ke Supabase cloud, mengonfigurasi Power BI Desktop, menyusun dashboard analitik, dan mempublikasikannya ke Power BI Service (Web).

---

## 1. Menarik (Pull) Repository di PC Windows

Buka **PowerShell** atau **Command Prompt** (CMD) di PC Windows Anda:

```powershell
# 1. Jika belum pernah clone repository:
cd C:\Users\<NamaUser>\Projects
git clone https://github.com/ReLyf47/bigdata.git
cd bigdata

# 2. Jika repository sudah ada di PC, ambil pembaruan terbaru:
cd C:\path\ke\bigdata
git pull origin main
```

Pastikan struktur folder tugas Minggu 10 tersedia:
```
bigdata/
├── tugas/
│   └── minggu10/
│       ├── Tugas_Minggu10_Kelompok8/
│       │   ├── Dataset/
│       │   │   ├── transformed_dataset.csv     (266,656 baris)
│       │   │   ├── nhtsa_api_cases.csv         (8,779 baris)
│       │   │   └── supabase_local.db           (SQLite warehouse)
│       │   ├── Documentation/
│       │   ├── Screenshots/
│       │   └── Source_Code/
│       └── README_WINDOWS_POWERBI.md
└── src/
    └── load_supabase.py
```

---

## 2. Kredensial & Parameter Supabase Cloud (Live)

Proyek Supabase kelompok telah aktif dan terverifikasi dengan parameter berikut:

| Parameter | Nilai Konfigurasi |
| :--- | :--- |
| **Project Ref** | `ywzjxhdulvltjmuohagu` |
| **Region** | Southeast Asia (Singapore) / `ap-southeast-1` |
| **Tipe Koneksi** | **Session Pooler (IPv4)** *(Wajib untuk Power BI)* |
| **Host / Server** | `aws-0-ap-southeast-1.pooler.supabase.com` |
| **Port** | `5432` |
| **Database** | `postgres` |
| **User Name** | `postgres.ywzjxhdulvltjmuohagu` |
| **Password** | *[Password database Supabase Anda]* |
| **Project URL** | `https://ywzjxhdulvltjmuohagu.supabase.co` |
| **Tabel Tujuan** | `public.nhtsa_crash_analytics` atau `analytics.accidents` |

---

## 3. Memuat Data ke Supabase Cloud (Opsional)

Jika tabel di Supabase masih kosong (0 baris), jalankan skrip otomatis yang telah disediakan dari folder proyek di Windows:

```powershell
# Pastikan dependensi terpasang:
pip install pandas sqlalchemy psycopg2-binary

# Jalankan loader ke Supabase:
python src/load_supabase.py --password PASSWORD_DATABASE_SUPABASE_ANDA
```
Skrip ini akan:
1. Membaca `transformed_dataset.csv` (266.656 baris) dan `nhtsa_api_cases.csv` (8.779 baris).
2. Memuatnya ke Supabase PostgreSQL melalui koneksi Session Pooler.
3. Menonaktifkan Row Level Security (RLS) dan memberikan izin baca (`GRANT SELECT`) agar Power BI dapat membaca data tanpa error autentikasi.

---

## 4. Menghubungkan Supabase ke Power BI Desktop (Windows)

Power BI Desktop di Windows 100% gratis dan memiliki konektor basis data bawaan tanpa batasan lisensi.

### Langkah-langkah Koneksi:

1. **Buka Power BI Desktop** di PC Windows Anda.
2. Pada pita menu **Home**, klik **Get Data** $\rightarrow$ pilih **PostgreSQL database** $\rightarrow$ klik **Connect**.
3. Masukkan parameter koneksi:
   - **Server**: `aws-0-ap-southeast-1.pooler.supabase.com`
   - **Database**: `postgres`
   - **Data Connectivity mode**: Pilih **Import** *(Sangat disarankan agar visualisasi responsif dan cepat)*.
   - Klik **OK**.
4. Pada jendela kredensial autentikasi:
   - Pilih tab **Database** di sisi kiri.
   - **User name**: `postgres.ywzjxhdulvltjmuohagu` *(wajib lengkap dengan nama tenant setelah tanda titik)*.
   - **Password**: Masukkan password database Supabase Anda.
   - Klik **Connect**.
5. *Peringatan Sertifikat SSL (Jika Muncul)*:
   - Jika muncul dialog *"An error happened while reading data: remote certificate is invalid"*, klik tombol **Cancel/Edit** atau buka menu `File -> Options and settings -> Data source settings -> Edit Permissions`, lalu **hilangkan centang pada Encrypt connections**.
6. **Pilih Tabel**:
   - Centang tabel `nhtsa_crash_analytics` (atau `accidents`).
   - Klik **Load** (atau klik *Transform Data* jika ingin memverifikasi tipe data terlebih dahulu).

> **Alternatif Cepat (Direct CSV):**  
> Jika database Supabase sedang tidak aktif atau offline, Anda bisa langsung memilih **Get Data $\rightarrow$ Text/CSV**, arahkan ke file `Dataset/transformed_dataset.csv`, dan klik **Load**. Skema kolom dan seluruh visualisasi yang dihasilkan identik.

---

## 5. Merancang Dashboard Analitik di Power BI

Susun visualisasi pada lembar kanvas Power BI untuk memenuhi luaran analisis Big Data Kelompok 8:

### A. 3 KPI Summary Cards
- **Kartu 1 (Total Kasus Kecelakaan)**:
  - Kolom: `ID` $\rightarrow$ Agregasi: **Count (Distinct)**.
- **Kartu 2 (Total Kasus Parah / Severity 4)**:
  - Kolom: `Severity` $\rightarrow$ Agregasi: **Count**, tambahkan filter visual `Severity is 4`.
- **Kartu 3 (Rata-rata Durasi Kecelakaan)**:
  - Kolom: `Duration_Minutes` $\rightarrow$ Agregasi: **Average**.

### B. Grafik Tren Waktu (Line Chart)
- **Visual**: Line Chart
- **X-axis**: `Accident_Date` (atau hierarki `Start_Time`: Year, Month).
- **Y-axis**: Count (Distinct) of `ID`.
- **Tujuan**: Menganalisis fluktuasi jumlah insiden kecelakaan dari tahun 2020 hingga 2024.

### C. Sebaran Wilayah / Geografis (Clustered Bar Chart & Map)
- **Visual**: Clustered Bar Chart atau Filled Map
- **Y-axis / Location**: `NHTSA_Region` atau `State`
- **X-axis / Values**: Count of `ID`
- **Legend**: `Severity_Label` (Minor, Moderate, Severe)
- **Tujuan**: Mengidentifikasi wilayah negara bagian dengan tingkat kecelakaan tertinggi.

### D. Pengaruh Faktor Cuaca (Donut Chart)
- **Visual**: Donut Chart
- **Legend**: `Weather_Group` (7 kategori hasil transformasi: Clear, Rain, Snow, Fog, Severe, Other, Cloudy).
- **Values**: Count of `ID`
- **Tujuan**: Mengevaluasi korelasi kondisi cuaca terhadap risiko kecelakaan lalu lintas.

### E. Filter Interaktif (Slicers)
Tambahkan visual **Slicer** di bagian atas kanvas:
1. Slicer Tahun: `Accident_Date` (Year slider atau dropdown).
2. Slicer Wilayah: `NHTSA_Region`.
3. Slicer Tingkat Keparahan: `Severity_Label`.

### F. Formula DAX (Measures)
Klik **New measure** pada menu Home dan tambahkan rumus berikut untuk metrik lanjutan:

```dax
Total Kasus = DISTINCTCOUNT('transformed_dataset'[ID])

Rata-rata Durasi (Menit) = AVERAGE('transformed_dataset'[Duration_Minutes])

Persentase Kasus Parah = 
DIVIDE(
    CALCULATE(DISTINCTCOUNT('transformed_dataset'[ID]), 'transformed_dataset'[Severity] = 4),
    [Total Kasus],
    0
)
```

---

## 6. Publikasi ke Power BI Service (Web)

Agar dashboard dapat diakses via tautan web dan dipresentasikan:

1. Di Power BI Desktop, klik menu **File $\rightarrow$ Save** (beri nama misalnya `Dashboard_Kecelakaan_Kelompok8.pbix`).
2. Klik tombol **Publish** di pojok kanan atas pita menu Home.
3. Masuk dengan akun Microsoft Telkom University (`relyff@student.telkomuniversity.ac.id`).
4. Pilih destinasi: **`My workspace`**.
5. Setelah muncul dialog *"Publishing to Power BI succeeded"*, buka peramban web dan masuk ke:
   [`https://app.powerbi.com`](https://app.powerbi.com)
6. Buka **My workspace** $\rightarrow$ klik laporan `Dashboard_Kecelakaan_Kelompok8`.
7. Dashboard Anda kini aktif di web secara penuh dengan seluruh kemampuan filter dan interaktivitas!
