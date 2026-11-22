# PANDUAN EKSEKUSI & POWER BI DESKTOP DI WINDOWS
**Tugas Minggu 10 — Mata Kuliah Big Data**  
**Kelompok 8:**  
- Alif Akbar Arraiyan (101032330121)  
- Farid Yusron Syabani (101032300192)  

Panduan ini menjelaskan cara menarik (pull) file tugas dari repository GitHub ke PC Windows, memuat data ke Supabase cloud, dan mengonfigurasi dashboard analitik di Power BI Desktop.

---

## 1. Menarik Perubahan di PC Windows

Jalankan perintah berikut di PowerShell atau Command Prompt pada PC Windows:

```powershell
cd C:\path\ke\folder\bigdata
git pull origin main
```

File deliverable tugas Minggu 10 berada di:
`tugas/minggu10/Tugas_Minggu10_Kelompok8/`

---

## 2. Kredensial Supabase PostgreSQL Cloud

| Pengaturan | Nilai |
| :--- | :--- |
| **Host (Session Pooler)** | `aws-0-ap-southeast-1.pooler.supabase.com` |
| **Port** | `5432` |
| **Database** | `postgres` |
| **User Name** | `postgres.ywzjxhdulvltjmuohagu` |
| **Project URL** | `https://ywzjxhdulvltjmuohagu.supabase.co` |
| **Tabel Target** | `public.nhtsa_crash_analytics` (atau `analytics.accidents`) |

---

## 3. Upload Data ke Supabase (Jika Tabel Masih Kosong)

Jalankan skrip loader otomatis dari terminal Windows:
```powershell
pip install pandas sqlalchemy psycopg2-binary
python src/load_supabase.py --password PASSWORD_DATABASE_SUPABASE
```

---

## 4. Buka & Hubungkan di Power BI Desktop

1. Buka aplikasi **Power BI Desktop** (dapat diunduh gratis dari Microsoft Store).
2. Klik **Get Data** $\rightarrow$ **PostgreSQL database** $\rightarrow$ **Connect**.
3. Masukkan:
   - **Server**: `aws-0-ap-southeast-1.pooler.supabase.com`
   - **Database**: `postgres`
   - **Data connectivity mode**: `Import`
4. Pilih tab **Database**:
   - **User name**: `postgres.ywzjxhdulvltjmuohagu`
   - **Password**: *[Password Supabase Anda]*
5. *(Opsi Praktis)*: Anda juga bisa langsung memuat data offline via **Get Data $\rightarrow$ Text/CSV** $\rightarrow$ arahkan ke file `tugas/minggu10/Tugas_Minggu10_Kelompok8/Dataset/transformed_dataset.csv`.

---

## 5. Visualisasi Dashboard

Susun komponen visual berikut di kanvas Power BI:
1. **3 KPI Cards**:
   - Total Kecelakaan: `ID` (Count Distinct)
   - Rata-rata Durasi: `Duration_Minutes` (Average)
   - Kasus Tingkat Keparahan 4 (Severe): Filter `Severity = 4`
2. **Line Chart**: Tren kecelakaan berdasarkan `Accident_Date` / `Month`.
3. **Clustered Bar Chart / Map**: Sebaran kecelakaan per `NHTSA_Region` dan `State`.
4. **Donut Chart**: Distribusi kategori cuaca `Weather_Group` (7 grup standardisasi).
5. **Slicers**: Filter interaktif untuk Tahun, Wilayah, dan `Severity_Label`.

---

## 6. Publikasi ke Power BI Service (Web)

1. Klik tombol **Publish** di pojok kanan atas Power BI Desktop.
2. Masuk dengan akun kampus: `relyff@student.telkomuniversity.ac.id`.
3. Pilih **`My workspace`**.
4. Laporan akan otomatis tayang dan dapat diakses melalui browser di [https://app.powerbi.com](https://app.powerbi.com).

*Panduan lengkap dan formula DAX dapat dilihat pada file: `Tugas_Minggu10_Kelompok8/PANDUAN_POWERBI_WINDOWS.md`*
