import os
import sys
import io
from PIL import Image as PILImage

# DOCX dependencies
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# ReportLab dependencies
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parents[2])
DOCS_DIR = os.path.join(BASE_DIR, "docs")
IMG_DIR = os.path.join(DOCS_DIR, "assets", "screenshots")
if not os.path.exists(IMG_DIR):
    IMG_DIR = os.path.join(DOCS_DIR, "screenshots_production")
DOCX_OUT = os.path.join(DOCS_DIR, "reports", "Laporan_ETL_dan_Analisis_BigData_Kelompok8.docx")
PDF_OUT = os.path.join(DOCS_DIR, "reports", "Laporan_ETL_dan_Analisis_BigData_Kelompok8.pdf")

def set_cell_background(cell, fill_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def generate_docx():
    print("[*] Generating Laporan_ETL_dan_Analisis_BigData_Kelompok8.docx ...")
    doc = docx.Document()
    
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Big Data — Kelompok 8 | Distributed ETL (Airflow, Beam, Supabase) & Analisis Kecelakaan AS")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(100, 116, 139)
        
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        frun1 = fp.add_run("Program Studi S1 Sains Data — Fakultas Informatika, Telkom University")
        frun1.font.name = "Arial"
        frun1.font.size = Pt(8.5)
        frun1.font.color.rgb = RGBColor(100, 116, 139)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("LAPORAN TEKNIS AKHIR & DOKUMENTASI SISTEM\nDISTRIBUTED ETL PIPELINE & ANALISIS BIG DATA")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(16)
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("Implementasi Apache Airflow, Apache Beam, Supabase PostgreSQL Cloud, dan Visualisasi Pola Kecelakaan AS (2020–2024)")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(10.5)
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    # Metadata Table
    tbl_meta = doc.add_table(rows=6, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [
        ("Mata Kuliah", "Big Data (S1 Sains Data — Fakultas Informatika, Telkom University)"),
        ("Kelompok", "Kelompok 8"),
        ("Anggota Tim", "1. Alif Akbar Arraiyan (NIM: 101032330121)\n2. Farid Yusron Syabani (NIM: 101032300192)"),
        ("Target Data Warehouse", "Supabase Cloud PostgreSQL (Host: aws-0-ap-southeast-1.pooler.supabase.com, Port: 5432, Table: public.nhtsa_crash_analytics)"),
        ("Lingkungan Deployment", "Linux Production Server VM (100.110.57.7@seculab, User: etl-nhtsa)"),
        ("Stack Teknologi", "Docker Compose, PostgreSQL 15, Apache Airflow 2.x, Apache Beam Python SDK, Psycopg2, Requests, Kaggle API, NHTSA FARS API")
    ]
    for idx, (label, val) in enumerate(meta_info):
        row = tbl_meta.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.1)
        c1.width = Inches(4.5)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(3)
        p0.paragraph_format.space_after = Pt(3)
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.name = "Arial"
        r0.font.size = Pt(9)
        r0.font.color.rgb = RGBColor(30, 41, 59)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(3)
        p1.paragraph_format.space_after = Pt(3)
        r1 = p1.add_run(val)
        r1.font.name = "Arial"
        r1.font.size = Pt(9)
        r1.font.color.rgb = RGBColor(51, 65, 85)
        
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "F8FAFC")
        set_cell_margins(c0, 50, 50, 90, 90)
        set_cell_margins(c1, 50, 50, 90, 90)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(13)
        r.font.color.rgb = RGBColor(14, 116, 144)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(30, 58, 138)
        return p

    def add_body(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.bold = True
            rb.font.name = "Arial"
            rb.font.size = Pt(9.5)
            rb.font.color.rgb = RGBColor(15, 23, 42)
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_bullet(text, bold_title=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        if bold_title:
            rb = p.add_run(bold_title)
            rb.bold = True
            rb.font.name = "Arial"
            rb.font.size = Pt(9.5)
            rb.font.color.rgb = RGBColor(15, 23, 42)
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(51, 65, 85)
        return p

    def add_image_box(filename, caption_text, width_inches=6.2):
        img_path = os.path.join(IMG_DIR, filename)
        if os.path.exists(img_path):
            with PILImage.open(img_path) as im:
                buf = io.BytesIO()
                im.save(buf, format='PNG')
                buf.seek(0)
                
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(6)
                p_img.paragraph_format.space_after = Pt(2)
                run = p_img.add_run()
                run.add_picture(buf, width=Inches(width_inches))
                
                p_cap = doc.add_paragraph()
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_cap.paragraph_format.space_before = Pt(2)
                p_cap.paragraph_format.space_after = Pt(8)
                rcap = p_cap.add_run(caption_text)
                rcap.italic = True
                rcap.font.name = "Arial"
                rcap.font.size = Pt(8.5)
                rcap.font.color.rgb = RGBColor(71, 85, 105)
        else:
            print(f"[!] Warning: Image not found {img_path}")

    # ==================== 1. RINGKASAN EKSEKUTIF ====================
    add_h1("1. Ringkasan Eksekutif & Gambaran Umum Arsitektur")
    add_body(
        "Laporan ini mendokumentasikan implementasi sistem Distributed ETL (Extract, Transform, Load) Pipeline skala enterprise "
        "yang dirancang untuk mengolah, membersihkan, dan menganalisis ratusan ribu rekor kecelakaan lalu lintas Amerika Serikat "
        "periode 2020 hingga 2024. Pipeline ini mengintegrasikan data dari dua sumber primer bereputasi: National Highway Traffic "
        "Safety Administration (NHTSA) FARS (Fatality Analysis Reporting System) API dan Kaggle US Traffic Accidents Dataset."
    )
    add_body(
        "Arsitektur dirancang dengan prinsip modern Data Engineering: kontainerisasi penuh menggunakan Docker Compose, "
        "orkestrasi workflow otomatis menggunakan Apache Airflow, komputasi transformasi data terdistribusi berbasis Apache Beam "
        "Python SDK, penyimpanan terpusat pada Supabase Cloud PostgreSQL, serta analisis eksploratif (EDA) yang mendalam "
        "untuk memberikan wawasan berbasis bukti bagi pemangku kepentingan transportasi jalan raya."
    )

    # ==================== 2. INFRASTRUKTUR & DOCKER ====================
    add_h1("2. Arsitektur Infrastruktur & Kontainerisasi (Docker Compose)")
    add_body(
        "Seluruh ekosistem pipeline berjalan pada mesin server produksi Linux (IP: 100.110.57.7@seculab) milik laboratorium. "
        "Untuk memastikan keandalan lingkungan, reproduktifitas, dan isolasi proses, seluruh layanan didefinisikan ke dalam file "
        "docker-compose.yaml:"
    )
    add_bullet(" Menggunakan image postgres:15 sebagai repository metadata Airflow untuk melacak DAG runs, task instances, koneksi, dan variabel sistem. Dilengkapi pemeriksaan kesiapan (pg_isready -U airflow -d airflow) dengan interval 10 detik.", "Service postgres:")
    add_bullet(" Service pembantu sekali jalan yang menunggu kesiapan kontainer PostgreSQL untuk mengeksekusi migrasi skema awal (airflow db migrate) dan membuat akun Administrator otomatis.", "Service airflow-init:")
    add_bullet(" Kontainer utama yang mengintegrasikan Airflow Webserver (berjalan pada port ekspos 8080) dan Airflow Scheduler. Menggunakan LocalExecutor untuk mendistribusikan eksekusi task secara paralel memanfaatkan thread CPU host.", "Service airflow:")
    add_bullet(" Direktori host (./dags, ./scripts, ./logs, ./plugins) dipetakan ke /opt/airflow/... di dalam kontainer, memungkinkan modifikasi skrip pipeline secara live tanpa perlu me-rebuild kontainer Docker.", "Volume Bind Mounts:")

    add_image_box(
        "01_docker_compose_airflow.jpg",
        "Gambar 1. Konfigurasi file docker-compose.yaml pada server Linux (100.110.57.7@seculab) yang mengorkestrasikan PostgreSQL dan Apache Airflow."
    )

    # ==================== 3. ORKESTRASI WORKFLOW ====================
    add_h1("3. Orkestrasi Workflow Terjadwal dengan Apache Airflow")
    add_body(
        "Apache Airflow bertindak sebagai konduktor utama yang mengendalikan jadwal dan dependensi eksekusi script ETL. "
        "Tim mengimplementasikan dua DAG independen untuk dua pola ingestion yang berbeda:"
    )
    add_h2("3.1 DAG 1: nhtsa_kaggle_classic_etl (Eksekusi Harian Terjadwal)")
    add_body(
        "Didefinisikan dalam dags/nhtsa_classic_etl_dag.py. Beroperasi secara berkala setiap hari pukul 02:00 AM UTC (cron: 0 2 * * *). "
        "DAG ini menjalankan operator BashOperator bertugas execute_apache_beam_etl yang mengeksekusi skrip python /opt/airflow/scripts/etl_nhtsa_beam.py. "
        "Dikonfigurasi dengan parameter toleransi kegagalan retries: 3 kali dan jeda retry_delay: 5 menit."
    )
    add_image_box(
        "02_dag_nhtsa_classic.png",
        "Gambar 2. Definisi DAG nhtsa_kaggle_classic_etl pada nhtsa_classic_etl_dag.py."
    )

    add_h2("3.2 DAG 2: nhtsa_2020_2025_sequential_etl (Ingestion Inkremental Multi-Tahun)")
    add_body(
        "Didefinisikan dalam dags/nhtsa_2020_2025_dag.py. Beroperasi setiap hari pukul 02:30 AM (cron: 30 2 * * *). "
        "Tujuan DAG ini adalah melakukan backfill dan ingestion berkelanjutan secara berurutan untuk arsip FARS 2020 hingga 2025. "
        "Dengan membatasi kuota batch per eksekusi, pipeline memproses rekor secara bertahap tanpa menguras memori RAM server."
    )
    add_image_box(
        "03_dag_nhtsa_sequential.jpg",
        "Gambar 3. Definisi DAG nhtsa_2020_2025_sequential_etl untuk ingestion inkremental FARS 2020–2025."
    )

    # ==================== 4. APACHE BEAM CLASSIC ====================
    add_h1("4. Implementasi Apache Beam ETL Pipeline — Versi Klasik (etl_nhtsa_beam.py)")
    add_body(
        "Skrip etl_nhtsa_beam.py merealisasikan arsitektur pemrosesan data stream dan batch dengan pustaka apache_beam. "
        "Pipeline ini menghubungkan sumber FARS NHTSA dengan dataset pengayaan Kaggle secara in-memory:"
    )

    add_h2("4.1 Tahap Extract: Fetching In-Memory NHTSA FARS & Kaggle Lookup")
    add_body(
        "Fungsi fetch_nhtsa_all_states_to_memory() mengunduh file FARS{SNAPSHOT_YEAR}NationalCSV.zip langsung dari repository statis NHTSA. "
        "Arsip ZIP dibaca langsung di dalam memori kerja (io.BytesIO) tanpa pernah disimpan ke hard disk lokal, sehingga meminimalkan latensi I/O. "
        "File accident.csv diparsing baris demi baris menggunakan csv.DictReader ber-encoding latin-1 dengan kuota PER_STATE_LIMIT = 1000 per negara bagian. "
        "Secara serentak, fetch_kaggle_lookup_to_memory() memanggil Kaggle API untuk mengunduh dataset amer2040/usa-states-to-region dan menyusun "
        "kamus pemetaan cuaca resmi FARS (Clear/Normal, Rain, Snow/Sleet, Fog/Smoke, Severe Crosswinds, dsb)."
    )
    add_image_box(
        "04_beam_classic_extract.jpg",
        "Gambar 4. Modul inisialisasi, fetch_nhtsa_all_states_to_memory, dan fetch_kaggle_lookup_to_memory pada etl_nhtsa_beam.py."
    )

    add_h2("4.2 Tahap Transform: Data Cleansing, Sanitasi Tanggal, dan CleanAndJoinDoFn")
    add_body(
        "Transformasi Apache Beam dijalankan menggunakan kelas CleanAndJoinDoFn(beam.DoFn). "
        "Tahap ini menangani beberapa anomali data kritis:",
        bold_prefix="Logika Transformasi Terapan: "
    )
    add_bullet(" Data historis NHTSA FARS menggunakan kode khusus 98 atau 99 untuk menyatakan hari atau bulan yang tidak diketahui. Fungsi sanitize_crash_date() memvalidasi hari terhadap bulan dan tahun (calendar.monthrange) serta memformat ulang string tanggal menjadi format ISO 8601 (YYYY-MM-DD).", "Sanitasi Anomali Tanggal FARS:")
    add_bullet(" Nomor kasus asli (ST_CASE) hanya unik per state per tahun. Untuk mencegah tabrakan primary key, pipeline menghasilkan unique_case_id = f'{year}-{raw_case}'.", "Pembentukan Composite Primary Key:")
    add_bullet(" Kode state dan nama county dibersihkan dari spasi ganda, digabungkan dengan referensi Region Kaggle (contoh: 'California (West)'), dan kode cuaca dipetakan ke label tekstual deskriptif.", "Pengayaan Wilayah & Klasifikasi Cuaca:")
    add_image_box(
        "05_beam_classic_transform.png",
        "Gambar 5. Logika parsing Kaggle lookup, fungsi sanitize_crash_date, dan deklarasi CleanAndJoinDoFn pada etl_nhtsa_beam.py."
    )

    add_h2("4.3 Tahap Load: Batch Upsert Idempotent ke Supabase PostgreSQL")
    add_body(
        "Pemuatan data ke cloud ditangani oleh WriteToSupabaseDoFn(beam.DoFn). "
        "Koneksi ke Supabase PostgreSQL menggunakan modul psycopg2. Query SQL menggunakan klausul UPSERT:",
        bold_prefix="Idempotensi Query SQL: "
    )
    add_body(
        "INSERT INTO public.nhtsa_crash_analytics (case_id, crash_date, state_name, county_name, total_vehicles, total_fatalities, weather_category) "
        "VALUES %s ON CONFLICT (case_id) DO UPDATE SET state_name = EXCLUDED.state_name, total_vehicles = EXCLUDED.total_vehicles, "
        "total_fatalities = EXCLUDED.total_fatalities, weather_category = EXCLUDED.weather_category, updated_at = CURRENT_TIMESTAMP;"
    )
    add_body(
        "Untuk memaksimalkan performa transfer jaringan ke Supabase, pemuatan dilakukan secara batch melalui beam.BatchElements(min_batch_size=50, max_batch_size=300) "
        "dan diproses dengan psycopg2.extras.execute_values. Konstruksi alur pipeline Beam dirakit dalam run_pipeline() menggunakan DirectRunner."
    )
    add_image_box(
        "06_beam_classic_load.png",
        "Gambar 6. Implementasi WriteToSupabaseDoFn dan perakitan eksekusi graf Apache Beam pada etl_nhtsa_beam.py."
    )

    # ==================== 5. INKREMENTAL MULTI-TAHUN ====================
    add_h1("5. Ingestion Inkremental Multi-Tahun (etl_nhtsa_2020_2025.py)")
    add_body(
        "Untuk memproses dataset berskala masif lintas tahun (2020–2025) tanpa membebani kapasitas RAM dan bandwidth jaringan, "
        "skrip etl_nhtsa_2020_2025.py dilengkapi kapabilitas checkpointing berbasis database."
    )

    add_h2("5.1 State Verification & Checkpointing Berdasarkan Database")
    add_body(
        "Fungsi get_row_counts_by_year(db_uri) mengirimkan query agregasi ke Supabase: "
        "SELECT EXTRACT(YEAR FROM crash_date)::INT AS yr, COUNT(*) FROM public.nhtsa_crash_analytics GROUP BY yr. "
        "Jumlah baris yang sudah tersimpan dijadikan nilai offset. Fungsi fetch_nhtsa_sequential_years() kemudian melakukan HTTP HEAD "
        "ke server NHTSA untuk memverifikasi apakah arsip FARS tahun target sudah tersedia (HTTP 200) atau belum (HTTP 404/skip)."
    )
    add_image_box(
        "07_beam_seq_init_check.jpg",
        "Gambar 7. Modul state verification get_row_counts_by_year dan pengecekan ketersediaan arsip via HTTP HEAD."
    )

    add_h2("5.2 Ekstraksi Batch Berkelanjutan dengan Offset Skipping")
    add_body(
        "Saat membaca accident.csv dari arsip ZIP tahun aktif, skrip mengabaikan baris yang indeksnya lebih kecil dari offset eksisting (if i < offset: continue). "
        "Skrip hanya membaca sejumlah BATCH_SIZE baris baru (20.000 atau kuota harian terkonfigurasi). "
        "Ketika seluruh baris pada suatu tahun telah selesai termuat, sistem secara otomatis mencetak log penuntasan dan melanjutkan ke tahun berikutnya."
    )
    add_image_box(
        "08_beam_seq_batch_extract.jpg",
        "Gambar 8. Mekanisme batch offset streaming dan penanganan tahun selesai pada etl_nhtsa_2020_2025.py."
    )

    add_h2("5.3 Transformasi & Pembersihan Lintas Tahun")
    add_body(
        "Tahap transformasi multi-tahun menerapkan logika CleanAndJoinDoFn yang identik untuk menjamin keseragaman skema kolom, "
        "penanganan missing values, dan penentuan format waktu baku di seluruh rentang tahun 2020 hingga 2025."
    )
    add_image_box(
        "09_beam_seq_transform.jpg",
        "Gambar 9. Logika CleanAndJoinDoFn pada pemrosesan sekuensial multi-tahun."
    )

    add_h2("5.4 Batch Ingestion ke Database Cloud Supabase")
    add_body(
        "Kumpulan batch data dialirkan ke Supabase Cloud melalui WriteToSupabaseDoFn. "
        "Log eksekusi mencatat jumlah record yang berhasil ter-commit secara berkala, memastikan setiap fase terpantau transparan."
    )
    add_image_box(
        "10_beam_seq_load_supabase.png",
        "Gambar 10. Implementasi WriteToSupabaseDoFn dan perakitan eksekusi pipeline Beam pada etl_nhtsa_2020_2025.py."
    )

    # ==================== 6. EXPLORATORY DATA ANALYSIS ====================
    add_h1("6. Analisis Hasil Eksplorasi Data (Exploratory Data Analysis / EDA)")
    add_body(
        "Setelah data berhasil dibersihkan dan distandarisasi melalui pipeline ETL, tahap visualisasi analitik "
        "dijalankan untuk mengungkap pola distribusi kecelakaan lalu lintas di Amerika Serikat. Visualisasi dilakukan "
        "menggunakan data agregat tahunan serta sampel representatif 10% (sebanyak 26.635 baris)."
    )

    add_h2("6.1 Tren Jumlah Kecelakaan Tahunan (2020–2024)")
    add_body(
        "Grafik garis tren tahunan memperlihatkan dinamika volume kecelakaan lalu lintas di AS:",
        bold_prefix="Observasi Metrik Tahunan: "
    )
    add_bullet(" Angka kecelakaan tercatat stabil di 35.000 kejadian. Periode ini bertepatan dengan pemberlakuan pembatasan sosial dan karantina wilayah (lockdown) akibat pandemi COVID-19, yang menekan frekuensi perjalanan jarak jauh.", "2020–2021 (Fase Pandemi):")
    add_bullet(" Angka kecelakaan melonjak drastis menjadi 60.000 kejadian (+71,4%). Kenaikan tajam ini dipicu oleh normalisasi mobilitas perkantoran, pembukaan sekolah luring, dan pemulihan aktivitas transportasi nasional.", "2022 (Fase Pemulihan Pasca-Pandemi):")
    add_bullet(" Terjadi lonjakan eksponensial mencapai rekor tertinggi 132.165 kejadian (>220% kenaikan). Hal ini merupakan hasil integrasi penuh dari pelaporan kepolisian lokal di seluruh 50 negara bagian yang tersinkronisasi ke sistem federal.", "2023 (Puncak Insiden):")
    add_bullet(" Tercatat 4.491 kejadian, yang mencerminkan data parsial dari kuartal awal tahun saat snapshot data diekstraksi.", "2024 (Data Parsial Berjalan):")
    add_image_box(
        "11_eda_tren_tahunan.png",
        "Gambar 11. Grafik garis Tren Jumlah Kecelakaan Tahunan Amerika Serikat (2020 – 2024)."
    )

    add_h2("6.2 Distribusi Tingkat Keparahan (Severity) dan Pengaruh Kondisi Cuaca")
    add_body(
        "Analisis keparahan dan faktor meteorologi menghasilkan temuan penting bagi keselamatan transportasi:"
    )
    add_bullet(" Mayoritas kecelakaan berada pada tingkat Moderate sebesar 71,9%. Kategori Serious menyumbang 17,1% kejadian yang memerlukan respon gawat darurat. Kategori Minor sebesar 7,5%, dan kategori Severe (kecelakaan fatal yang memakan korban jiwa) berada pada proporsi 3,5%.", "Proporsi Tingkat Keparahan (Pie Chart):")
    add_bullet(" Sebaran titik insiden sangat terkonsentrasi pada temperatur 40°F hingga 80°F dengan kelembapan relatif 40% hingga 90%. Hal ini membuktikan bahwa risiko kecelakaan tertinggi di AS bukan terjadi saat badai salju ekstrem (di mana masyarakat cenderung membatalkan perjalanan), melainkan pada kondisi jalanan lembap/basah bersuhu normal saat volume kendaraan berada pada tingkat tertinggi.", "Korelasi Suhu vs Kelembapan (Scatter Plot):")
    add_image_box(
        "12_eda_keparahan_cuaca.jpg",
        "Gambar 12. Diagram lingkaran Persentase Tingkat Keparahan Kecelakaan (kiri) dan Diagram tebar Hubungan Temperatur vs Kelembapan Saat Kejadian (kanan)."
    )

    add_h2("6.3 Analisis Spasial: Top 15 Negara Bagian dengan Insiden Tertinggi")
    add_body(
        "Berdasarkan visualisasi sampling 10% (26.635 baris data tervalidasi), California (CA) menempati posisi teratas "
        "dengan selisih yang sangat dominan dibanding negara bagian lain (>6.000 insiden atau menyumbang ~22,7% dari total sampel)."
    )
    add_body(
        "Florida (FL, ~2.500 kejadian) dan Texas (TX, ~2.300 kejadian) berada di peringkat kedua dan ketiga. "
        "Tingginya insiden di tiga negara bagian ini disebabkan oleh kombinasi tiga faktor kunci: jumlah populasi terbesar di AS, "
        "tingkat ketergantungan yang sangat tinggi terhadap kendaraan pribadi, serta jaringan jalan tol Interstate Highway yang sangat luas."
    )
    add_image_box(
        "13_eda_top15_states.png",
        "Gambar 13. Diagram batang Top 15 Negara Bagian dengan Jumlah Kecelakaan Tertinggi (Berdasarkan 10% Sampel / 26.635 baris)."
    )

    add_h2("6.4 Analisis Temporal: Pola Jam Kejadian dan Hari dalam Seminggu")
    add_body(
        "Analisis waktu kejadian mengungkap ritme sirkadian dan kebiasaan mobilitas masyarakat Amerika Serikat:"
    )
    add_bullet(" Kurva distribusi per jam menunjukkan pola bimodal (dua gelombang puncak). Puncak pagi (Morning Rush Hour) terjadi tepat pada pukul 07:00 – 08:00 (~2.400 kejadian) saat keberangkatan komuter kerja dan sekolah. Puncak sore (Evening Rush Hour) terjadi pada pukul 16:00 – 17:00 (~1.950 kejadian) saat kepulangan komuter. Waktu siang hari (10:00 – 12:00) relatif stabil di ~1.000 kejadian, dan dini hari (00:00 – 04:00) berada pada titik terendah (<300 kejadian).", "Pola Jam Kejadian (Bimodal Distribution):")
    add_bullet(" Angka kecelakaan pada hari kerja (Senin s.d. Jumat) konsisten tinggi di rentang 4.100 hingga 4.750 kejadian, mencapai puncaknya pada hari Kamis (~4.750 kejadian). Sebaliknya, pada akhir pekan (Sabtu dan Minggu), angka kecelakaan merosot tajam lebih dari 55% ke level ~2.000 dan ~2.150 kejadian. Hal ini membuktikan bahwa arus komuter rutin pada hari kerja adalah kontributor utama probabilitas kecelakaan.", "Pola Hari dalam Seminggu:")
    add_image_box(
        "14_eda_distribusi_waktu.png",
        "Gambar 14. Kurva Distribusi Kecelakaan Berdasarkan Jam Kejadian (kiri) dan Diagram batang Jumlah Kecelakaan Berdasarkan Hari (kanan)."
    )

    # ==================== 7. KESIMPULAN & REKOMENDASI ====================
    add_h1("7. Kesimpulan Teknis & Rekomendasi Manajerial")
    add_body(
        "Implementasi sistem ETL terdistribusi dan analisis data ini menghasilkan kesimpulan penting:",
        bold_prefix="Poin Evaluasi Teknis: "
    )
    add_bullet(" Integrasi Docker Compose, Apache Airflow, dan Apache Beam DirectRunner berhasil menangani pemrosesan data historis berukuran besar secara stabil tanpa menimbulkan beban disk I/O berlebih berkat teknik in-memory streaming.", "Keandalan Pipeline:")
    add_bullet(" Penggunaan composite primary key f'{year}-{raw_case}' yang dipadukan dengan klausul SQL ON CONFLICT DO UPDATE SET menjamin idempotensi penuh; eksekusi berulang tidak menghasilkan duplikasi rekor di Supabase.", "Integritas Data:")
    add_bullet(" Algoritma sanitasi tanggal berhasil mengoreksi kode anomali FARS 98/99 menjadi format ISO standar yang valid untuk analitik downstream.", "Kualitas Data:")

    add_body(
        "Rekomendasi Kebijakan Transportasi:",
        bold_prefix="Rekomendasi Manajerial Berbasis Bukti: "
    )
    add_bullet(" Departemen perhubungan di California, Florida, dan Texas disarankan mengalokasikan patroli lalu lintas dan pengaturan lampu rambu cerdas terutama pada jendela jam sibuk pagi (07:00–08:00) dan sore (16:00–17:00).", "Optimasi Manajemen Jam Sibuk:")
    add_bullet(" Fokus sosialisasi keselamatan pengemudi perlu ditingkatkan menjelang hari Kamis, di mana akumulasi kelelahan kerja mingguan berkorelasi dengan puncak insiden kecelakaan tertinggi.", "Antisipasi Kelelahan Pengemudi Hari Kerja:")

    doc.save(DOCX_OUT)
    print(f"[OK] Word document saved to: {DOCX_OUT}")


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4B5563"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 800, "Big Data — Kelompok 8 | Distributed ETL (Airflow, Beam, Supabase) & Analisis Kecelakaan")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 794, 541, 794)
            
        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 541, 45)
        self.drawString(54, 32, "Program Studi S1 Sains Data — Telkom University")
        page_str = f"Halaman {self._pageNumber} dari {page_count}"
        self.drawRightString(541, 32, page_str)
        self.restoreState()


def generate_pdf():
    print("[*] Generating Laporan_ETL_dan_Analisis_BigData_Kelompok8.pdf with ReportLab ...")
    doc = SimpleDocTemplate(
        PDF_OUT,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        alignment=1,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=12
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0E7490'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    caption_style = ParagraphStyle(
        'Caption',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceBefore=3,
        spaceAfter=8
    )

    tc_bold = ParagraphStyle('TCB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10.5, textColor=colors.HexColor('#0F172A'))
    tc_style = ParagraphStyle('TC', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10.5, textColor=colors.HexColor('#334155'))

    story = []

    # Title & Subtitle
    story.append(Paragraph("LAPORAN TEKNIS AKHIR & DOKUMENTASI SISTEM", title_style))
    story.append(Paragraph("<b>DISTRIBUTED ETL PIPELINE & ANALISIS DATA KECELAKAAN AS (2020–2024)</b>", title_style))
    story.append(Paragraph("Implementasi Apache Airflow, Apache Beam, Supabase PostgreSQL, dan Exploratory Data Analysis", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0E7490'), spaceBefore=2, spaceAfter=8))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Mata Kuliah</b>", tc_bold), Paragraph("Big Data (S1 Sains Data — Fakultas Informatika, Telkom University)", tc_style)],
        [Paragraph("<b>Kelompok</b>", tc_bold), Paragraph("Kelompok 8", tc_style)],
        [Paragraph("<b>Anggota Tim</b>", tc_bold), Paragraph("1. Alif Akbar Arraiyan (NIM: 101032330121)<br/>2. Farid Yusron Syabani (NIM: 101032300192)", tc_style)],
        [Paragraph("<b>Target Database</b>", tc_bold), Paragraph("Supabase Cloud PostgreSQL (<code>public.nhtsa_crash_analytics</code>)", tc_style)],
        [Paragraph("<b>Lingkungan Eksekusi</b>", tc_bold), Paragraph("Linux Production Server VM (<code>100.110.57.7@seculab</code>)", tc_style)],
        [Paragraph("<b>Stack Teknologi</b>", tc_bold), Paragraph("Docker Compose, PostgreSQL 15, Apache Airflow 2.x, Apache Beam Python SDK, Psycopg2, Kaggle & NHTSA API", tc_style)],
    ]
    t_meta = Table(meta_data, colWidths=[120, 367])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    def add_rl_image(filename, caption_text, width=470, height=240):
        img_path = os.path.join(IMG_DIR, filename)
        if os.path.exists(img_path):
            with PILImage.open(img_path) as im:
                buf = io.BytesIO()
                im.save(buf, format='PNG')
                buf.seek(0)
                story.append(KeepTogether([
                    RLImage(buf, width=width, height=height),
                    Paragraph(caption_text, caption_style)
                ]))
        else:
            print(f"[!] Warning: Image not found {img_path}")

    # Section 1
    story.append(Paragraph("1. Ringkasan Eksekutif & Arsitektur Solusi", h1_style))
    story.append(Paragraph(
        "Laporan teknis ini menguraikan pembangunan pipeline big data terdistribusi berskala produksi untuk memproses "
        "data kecelakaan lalu lintas di Amerika Serikat rentang 2020–2024. Pipeline ini mengintegrasikan data heterogen dari "
        "National Highway Traffic Safety Administration (NHTSA) FARS API serta dataset Kaggle. Sistem mengimplementasikan "
        "prinsip modularitas tinggi dengan mengombinasikan Docker Compose, Apache Airflow, Apache Beam, dan Supabase Cloud PostgreSQL.",
        body_style
    ))

    # Section 2
    story.append(Paragraph("2. Arsitektur Infrastruktur & Kontainerisasi (Docker Compose)", h1_style))
    story.append(Paragraph(
        "Seluruh ekosistem backend dikonfigurasikan di server Linux (100.110.57.7@seculab) menggunakan docker-compose.yaml. "
        "PostgreSQL 15 berperan sebagai repository metadata Airflow dengan healthcheck otomatis. Service airflow-init "
        "melakukan migrasi skema dan inisialisasi user Admin. Kontainer airflow menjalankan Webserver (port 8080) dan Scheduler "
        "secara berdampingan dengan LocalExecutor untuk pemrosesan paralel yang efisien.",
        body_style
    ))
    add_rl_image("01_docker_compose_airflow.jpg", "Gambar 1. Konfigurasi orkestrasi kontainer docker-compose.yaml pada server Linux 100.110.57.7@seculab.", 470, 240)

    # Section 3
    story.append(Paragraph("3. Orkestrasi Pipeline dengan Apache Airflow (DAGs)", h1_style))
    story.append(Paragraph("3.1 DAG Harian: nhtsa_kaggle_classic_etl", h2_style))
    story.append(Paragraph(
        "Didefinisikan dalam dags/nhtsa_classic_etl_dag.py dengan jadwal harian pukul 02:00 AM UTC (0 2 * * *). "
        "DAG ini mengeksekusi pipeline klasik Apache Beam melalui BashOperator dengan konfigurasi 3 kali retries dan delay 5 menit.",
        body_style
    ))
    add_rl_image("02_dag_nhtsa_classic.png", "Gambar 2. Definisi DAG nhtsa_kaggle_classic_etl pada nhtsa_classic_etl_dag.py.", 470, 240)

    story.append(Paragraph("3.2 DAG Inkremental: nhtsa_2020_2025_sequential_etl", h2_style))
    story.append(Paragraph(
        "Didefinisikan dalam dags/nhtsa_2020_2025_dag.py dengan jadwal harian pukul 02:30 AM (30 2 * * *). "
        "DAG ini memicu eksekusi pemrosesan inkremental historis FARS 2020–2025 secara berkala.",
        body_style
    ))
    add_rl_image("03_dag_nhtsa_sequential.jpg", "Gambar 3. Definisi DAG nhtsa_2020_2025_sequential_etl untuk ingestion beruntun FARS 2020–2025.", 470, 240)

    # Section 4
    story.append(Paragraph("4. Implementasi Apache Beam ETL Pipeline — Versi Klasik (etl_nhtsa_beam.py)", h1_style))
    story.append(Paragraph("4.1 Tahap Extract: Fetching In-Memory FARS & Kaggle Lookups", h2_style))
    story.append(Paragraph(
        "Fungsi fetch_nhtsa_all_states_to_memory() mengunduh arsip ZIP FARS langsung ke memori RAM (io.BytesIO) "
        "tanpa menyentuh disk fisik. Record accident.csv diparsing dengan batas PER_STATE_LIMIT = 1000 per negara bagian. "
        "Secara paralel, fetch_kaggle_lookup_to_memory() mengambil referensi region dan kamus kode cuaca resmi FARS.",
        body_style
    ))
    add_rl_image("04_beam_classic_extract.jpg", "Gambar 4. Modul ekstraksi in-memory FARS NHTSA & Kaggle API pada etl_nhtsa_beam.py.", 470, 240)

    story.append(Paragraph("4.2 Tahap Transform: Sanitasi Tanggal & CleanAndJoinDoFn", h2_style))
    story.append(Paragraph(
        "Fungsi sanitize_crash_date() menangani kode anomali tanggal FARS 98/99 dengan validasi kalender calendar.monthrange. "
        "CleanAndJoinDoFn membentuk primary key komposit unik f'{year}-{raw_case}', menautkan region geografis Kaggle, "
        "dan memetakan deskripsi cuaca numerik ke label tekstual.",
        body_style
    ))
    add_rl_image("05_beam_classic_transform.png", "Gambar 5. Logika sanitasi tanggal dan Apache Beam CleanAndJoinDoFn pada etl_nhtsa_beam.py.", 470, 240)

    story.append(Paragraph("4.3 Tahap Load: Batch Upsert ke Supabase PostgreSQL", h2_style))
    story.append(Paragraph(
        "WriteToSupabaseDoFn menggunakan klausul UPSERT (ON CONFLICT DO UPDATE SET) dengan psycopg2.extras.execute_values. "
        "Pipeline dirangkai dalam graf DirectRunner: ReadFromMemory >> CleanAndJoin >> BatchElements(50..300) >> LoadToSupabase.",
        body_style
    ))
    add_rl_image("06_beam_classic_load.png", "Gambar 6. Implementasi WriteToSupabaseDoFn dan perakitan eksekusi Beam DirectRunner.", 470, 240)

    # Section 5
    story.append(Paragraph("5. Ingestion Inkremental Multi-Tahun (etl_nhtsa_2020_2025.py)", h1_style))
    story.append(Paragraph("5.1 State Verification & Checkpointing Database", h2_style))
    story.append(Paragraph(
        "Fungsi get_row_counts_by_year(db_uri) menghitung rekor yang telah tersimpan di Supabase per tahun. "
        "HTTP HEAD dikirimkan ke server NHTSA untuk memastikan ketersediaan arsip FARS tahun target sebelum diunduh.",
        body_style
    ))
    add_rl_image("07_beam_seq_init_check.jpg", "Gambar 7. Modul state verification get_row_counts_by_year dan pengecekan arsip via HTTP HEAD.", 470, 240)

    story.append(Paragraph("5.2 Ekstraksi Batch Berkelanjutan dengan Offset Skipping", h2_style))
    story.append(Paragraph(
        "Pembacaan CSV melompati baris hingga mencapai offset eksisting (if i < offset: continue) dan memproses "
        "batch baru. Jika data tahun tersebut habis, sistem beralih ke tahun berikutnya secara otomatis.",
        body_style
    ))
    add_rl_image("08_beam_seq_batch_extract.jpg", "Gambar 8. Mekanisme batch offset streaming pada etl_nhtsa_2020_2025.py.", 470, 240)

    story.append(Paragraph("5.3 Transformasi & Ingestion Cloud Lintas Tahun", h2_style))
    story.append(Paragraph(
        "Transformasi DoFn dan pemuatan data ke Supabase menjamin konsistensi skema dan idempotensi seluruh tahun studi.",
        body_style
    ))
    add_rl_image("09_beam_seq_transform.jpg", "Gambar 9. Logika CleanAndJoinDoFn pada skrip sekuensial multi-tahun.", 470, 240)
    add_rl_image("10_beam_seq_load_supabase.png", "Gambar 10. WriteToSupabaseDoFn dan perakitan pipeline Beam run_pipeline() pada etl_nhtsa_2020_2025.py.", 470, 240)

    # Section 6
    story.append(Paragraph("6. Analisis Hasil Eksplorasi Data (Exploratory Data Analysis / EDA)", h1_style))
    story.append(Paragraph("6.1 Tren Jumlah Kecelakaan Tahunan (2020–2024)", h2_style))
    story.append(Paragraph(
        "Grafik garis tren tahunan menunjukkan stabilitas pada periode pandemi 2020–2021 (35.000 kejadian), "
        "kenaikan +71,4% pada fase pemulihan 2022 (60.000 kejadian), dan puncak tertinggi pada 2023 sebesar 132.165 kejadian "
        "seiring integrasi penuh data pelaporan kepolisian lokal. Tahun 2024 mencatat 4.491 kejadian sebagai snapshot parsial.",
        body_style
    ))
    add_rl_image("11_eda_tren_tahunan.png", "Gambar 11. Grafik garis Tren Jumlah Kecelakaan Tahunan Amerika Serikat (2020 – 2024).", 470, 240)

    story.append(Paragraph("6.2 Distribusi Tingkat Keparahan & Pengaruh Kondisi Cuaca", h2_style))
    story.append(Paragraph(
        "Sebagian besar kecelakaan berada pada kategori Moderate (71,9%), diikuti Serious (17,1%), Minor (7,5%), "
        "dan Severe (3,5%). Scatter plot memperlihatkan klaster densitas tertinggi berada pada rentang suhu 40°F–80°F "
        "dan kelembapan 40%–90%, membuktikan kecelakaan lebih banyak terjadi pada kondisi harian normal dengan volume kendaraan tinggi.",
        body_style
    ))
    add_rl_image("12_eda_keparahan_cuaca.jpg", "Gambar 12. Visualisasi Tingkat Keparahan (kiri) dan Temperatur vs Kelembapan (kanan).", 470, 180)

    story.append(Paragraph("6.3 Analisis Spasial: Top 15 Negara Bagian Rawan Kecelakaan", h2_style))
    story.append(Paragraph(
        "Berdasarkan visualisasi 10% sampel (26.635 baris), California (CA) menempati peringkat teratas (>6.000 kejadian), "
        "diikuti Florida (FL, ~2.500 kejadian) dan Texas (TX, ~2.300 kejadian), merefleksikan tingginya populasi dan intensitas mobilitas Interstate Highway.",
        body_style
    ))
    add_rl_image("13_eda_top15_states.png", "Gambar 13. Diagram batang Top 15 Negara Bagian dengan Kecelakaan Tertinggi (10% Sample, 26.635 baris).", 470, 210)

    story.append(Paragraph("6.4 Analisis Temporal: Pola Jam Kejadian dan Hari dalam Seminggu", h2_style))
    story.append(Paragraph(
        "Distribusi per jam menunjukkan kurva bimodal dengan puncak pagi pukul 07:00–08:00 (~2.400 kejadian) "
        "dan puncak sore pukul 16:00–17:00 (~1.950 kejadian). Hari kerja konsisten tinggi dan memuncak pada hari Kamis (~4.750 kejadian), "
        "sedangkan akhir pekan mengalami penurunan drastis lebih dari 55% (~2.000 kejadian pada Sabtu).",
        body_style
    ))
    add_rl_image("14_eda_distribusi_waktu.png", "Gambar 14. Distribusi Kecelakaan Berdasarkan Jam Kejadian (kiri) dan Hari dalam Seminggu (kanan).", 470, 190)

    # Section 7
    story.append(Paragraph("7. Kesimpulan Teknis & Rekomendasi Manajerial", h1_style))
    story.append(Paragraph(
        "Pipeline ETL terdistribusi berhasil memenuhi seluruh kriteria produksi: arsitektur kontainer Docker yang tangguh, "
        "orkestrasi Airflow andal, sanitasi kode FARS 98/99 yang akurat, serta idempotensi penulisan ke Supabase PostgreSQL. "
        "Hasil EDA memberikan dasar kuat bagi pembuat kebijakan untuk memfokuskan mitigasi lalu lintas pada jam sibuk komuter hari kerja "
        "dan koridor transportasi utama di California, Florida, dan Texas.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] PDF document saved to: {PDF_OUT}")


if __name__ == "__main__":
    generate_docx()
    generate_pdf()
