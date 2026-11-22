import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parents[2])
DOCS_DIR = os.path.join(BASE_DIR, "docs")
IMG_DIR = os.path.join(DOCS_DIR, "assets", "screenshots")
if not os.path.exists(IMG_DIR):
    IMG_DIR = os.path.join(DOCS_DIR, "screenshots_production")
DOCX_OUT = os.path.join(DOCS_DIR, "reports", "Laporan_ETL_dan_Analisis_BigData_Kelompok8.docx")

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

def create_document():
    doc = docx.Document()
    
    # Page setup - A4
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
        # Header & Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Tugas Mata Kuliah Big Data — Kelompok 8 | Arsitektur ETL & Analitik Kecelakaan AS")
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

    # Styles
    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("LAPORAN TEKNIS AKHIR & DOKUMENTASI SISTEM\nDISTRIBUTED ETL PIPELINE & ANALISIS DATA")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(16)
    r_title.font.color.rgb = RGBColor(15, 23, 42) # Slate-900

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("Implementasi Apache Airflow, Apache Beam, Supabase PostgreSQL, dan Visualisasi Analitik Tren Kecelakaan AS (2020–2024)")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(71, 85, 105) # Slate-600

    # Meta Table
    tbl_meta = doc.add_table(rows=5, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [
        ("Mata Kuliah", "Big Data (S1 Sains Data — Telkom University)"),
        ("Kelompok", "Kelompok 8"),
        ("Anggota Tim", "1. Alif Akbar Arraiyan (NIM: 101032330121)\n2. Farid Yusron Syabani (NIM: 101032300192)"),
        ("Lingkungan Eksekusi", "Linux VM Production Server (100.110.57.7@seculab)"),
        ("Teknologi Utama", "Docker Compose, Apache Airflow 2.x, Apache Beam Python SDK, Supabase PostgreSQL, Kaggle API, NHTSA FARS API")
    ]
    for idx, (label, val) in enumerate(meta_info):
        row = tbl_meta.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.0)
        c1.width = Inches(4.6)
        
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
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)

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
        r.font.color.rgb = RGBColor(14, 116, 144) # Cyan-700
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
        r.font.color.rgb = RGBColor(30, 58, 138) # Blue-900
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

    def add_image_box(filename, caption_text):
        img_path = os.path.join(IMG_DIR, filename)
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(2)
            run = p_img.add_run()
            run.add_picture(img_path, width=Inches(6.2))
            
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

    # ==================== SECTION 1 ====================
    add_h1("1. Ringkasan Eksekutif & Gambaran Umum Sistem")
    add_body(
        "Proyek ini mengimplementasikan sebuah pipeline data engineering modern berskala enterprise untuk mengekstraksi, "
        "mentransformasi, dan memuat (ETL) data kecelakaan lalu lintas Amerika Serikat (periode 2020–2024). "
        "Sistem dibangun secara terdistribusi di lingkungan Linux server (100.110.57.7@seculab) dengan memanfaatkan "
        "kombinasi Apache Airflow sebagai orkestrator workflow terjadwal, Apache Beam sebagai framework pemrosesan batch data stream, "
        "serta Supabase PostgreSQL sebagai relational analytical data warehouse di cloud."
    )
    add_body(
        "Pendekatan yang diterapkan menyelesaikan dua tantangan utama dalam big data: (1) Menjaga integritas data multi-tahun "
        "dari sumber heterogen (National Highway Traffic Safety Administration FARS API dan Kaggle US Traffic Accident) melalui deduplikasi "
        "composite key dan data cleansing; (2) Mengoptimalkan throughput pemrosesan tanpa menimbulkan memory-leak dengan "
        "menerapkan streaming in-memory, batch chunking, serta checkpointing status unduhan lintas tahun."
    )

    # ==================== SECTION 2 ====================
    add_h1("2. Arsitektur Infrastruktur & Kontainerisasi (Docker Compose)")
    add_body(
        "Seluruh komponen backend dijalankan dalam kontainer Docker untuk menjamin reproduktifitas, isolasi dependensi, "
        "dan kemudahan deployment. File docker-compose.yaml mengorkestrasikan tiga layanan inti:"
    )
    add_bullet(" Menggunakan image postgres:15 sebagai backend metadata storage untuk mencatat riwayat eksekusi task Airflow, DAG state, dan variabel konfigurasi. Dilengkapi konfigurasi healthcheck otomatis (pg_isready) berinterval 10 detik.", "PostgreSQL 15 Container:")
    add_bullet(" Layanan inisialisasi transien yang menunggu database PostgreSQL sehat sebelum mengeksekusi migrasi skema (airflow db migrate) dan mendaftarkan kredensial akun administrator.", "Airflow Init Service:")
    add_bullet(" Kontainer utama yang menjalankan Airflow Webserver (port 8080) dan Airflow Scheduler secara berdampingan. Menggunakan LocalExecutor untuk eksekusi task paralel secara efisien pada CPU multi-core server host.", "Airflow Webserver & Scheduler:")

    add_image_box(
        "01_docker_compose_airflow.jpg",
        "Gambar 1. Konfigurasi orkestrasi kontainer docker-compose.yaml pada server Linux 100.110.57.7@seculab."
    )

    # ==================== SECTION 3 ====================
    add_h1("3. Orkestrasi Workflow dengan Apache Airflow (DAG Implementation)")
    add_body(
        "Untuk menjamin otomasi pemrosesan berkala tanpa intervensi manual, tim merancang dua Directed Acyclic Graph (DAG) "
        "dengan jadwal cron dan tanggung jawab yang terpisah secara modular:"
    )
    add_h2("3.1 DAG 1: nhtsa_kaggle_classic_etl (Eksekusi Harian Terjadwal)")
    add_body(
        "DAG ini didefinisikan dalam nhtsa_classic_etl_dag.py dengan jadwal eksekusi setiap hari pada pukul 02:00 AM UTC (0 2 * * *). "
        "DAG ini bertindak sebagai pipeline reguler yang memicu eksekusi Apache Beam classic script (etl_nhtsa_beam.py). "
        "Dikonfigurasi dengan toleransi retries sebanyak 3 kali dan jeda retry 5 menit guna mengantisipasi gangguan jaringan pada API NHTSA/Kaggle."
    )
    add_image_box(
        "02_dag_nhtsa_classic.png",
        "Gambar 2. Definisi DAG nhtsa_kaggle_classic_etl pada nhtsa_classic_etl_dag.py."
    )

    add_h2("3.2 DAG 2: nhtsa_2020_2025_sequential_etl (Eksekusi Inkremental Multi-Tahun)")
    add_body(
        "DAG kedua didefinisikan dalam nhtsa_2020_2025_dag.py dengan jadwal harian pukul 02:30 AM (30 2 * * *). "
        "DAG ini mengemban misi pemrosesan inkremental historis dari tahun 2020 hingga 2025. Dengan membatasi pemrosesan kuota harian, "
        "pipeline secara bertahap menyedot ratusan ribu rekor arsip FARS tahunan ke database Supabase tanpa membebani memori server."
    )
    add_image_box(
        "03_dag_nhtsa_sequential.jpg",
        "Gambar 3. Definisi DAG nhtsa_2020_2025_sequential_etl untuk ingestion beruntun FARS 2020–2025."
    )

    # ==================== SECTION 4 ====================
    add_h1("4. Implementasi Apache Beam ETL Pipeline — Pipeline Klasik (etl_nhtsa_beam.py)")
    add_body(
        "Apache Beam dipilih sebagai engine komputasi karena abstraksi pipeline-nya yang fleksibel dan portabel. "
        "Implementasi klasik terbagi menjadi tiga tahapan sekuensial yang terkoordinasi:"
    )

    add_h2("4.1 Tahap Extract: Fetching Arsip NHTSA FARS & Kaggle Lookup")
    add_body(
        "Fungsi fetch_nhtsa_all_states_to_memory() mengunduh file FARS National CSV ZIP langsung dari static repository NHTSA. "
        "File ZIP diekstrak langsung di dalam memori RAM (io.BytesIO) tanpa penulisan temporary file ke disk, sehingga "
        "menghemat I/O storage server. Pembacaan file accident.csv menerapkan limit PER_STATE_LIMIT = 1000 untuk menjamin representasi merata di 50+ negara bagian. "
        "Secara paralel, fungsi fetch_kaggle_lookup_to_memory() memanggil Kaggle API (dataset amer2040/usa-states-to-region) "
        "untuk membangun kamus referensi Region dan klasifikasi kode cuaca resmi FARS."
    )
    add_image_box(
        "04_beam_classic_extract.jpg",
        "Gambar 4. Modul inisialisasi dan fungsi ekstraksi in-memory FARS NHTSA & Kaggle API pada etl_nhtsa_beam.py."
    )

    add_h2("4.2 Tahap Transform: Data Cleansing, Sanitasi Tanggal, dan Pengayaan DoFn")
    add_body(
        "Tahap transformasi mengimplementasikan Beam DoFn (CleanAndJoinDoFn) dan fungsi sanitasi tanggal khusus:",
        bold_prefix="Logika Transformasi Terapan: "
    )
    add_bullet(" Data historis FARS seringkali memuat kode 98 atau 99 untuk tanggal/bulan yang tidak dicatat akurat oleh petugas kepolisian. Fungsi sanitize_crash_date() memvalidasi batas kalender (calendar.monthrange) dan mengonversi format tanggal menjadi ISO standar YYYY-MM-DD.", "Sanitasi Anomali Tanggal FARS:")
    add_bullet(" Karena nomor kasus (ST_CASE) dapat berulang di tahun berbeda atau state berbeda, pipeline membentuk composite key unique_case_id = f'{year}-{raw_case}' untuk menjamin keunikan mutlak di database.", "Pembentukan Unique Case ID:")
    add_bullet(" Nilai kode negara bagian dan kode cuaca numerik dihubungkan dengan lookup table Kaggle, menghasilkan enriched_state (e.g., 'California (West)') dan deskripsi tekstual cuaca yang bersih.", "Pengayaan Wilayah & Cuaca:")
    add_image_box(
        "05_beam_classic_transform.png",
        "Gambar 5. Logika sanitasi tanggal dan Apache Beam CleanAndJoinDoFn pada etl_nhtsa_beam.py."
    )

    add_h2("4.3 Tahap Load: Batch Upsert Idempotent ke Supabase PostgreSQL")
    add_body(
        "Kelas WriteToSupabaseDoFn menangani pemuatan data ke cloud database Supabase PostgreSQL. "
        "Untuk mencegah rekor ganda akibat re-run DAG, query SQL menggunakan klausul UPSERT (ON CONFLICT DO UPDATE SET). "
        "Eksekusi penulisan dilakukan secara bulk-batch menggunakan psycopg2.extras.execute_values dengan ukuran batch 50 hingga 300 elemen."
    )
    add_image_box(
        "06_beam_classic_load.png",
        "Gambar 6. Implementasi WriteToSupabaseDoFn dan definisi graf eksekusi Beam DirectRunner."
    )

    # ==================== SECTION 5 ====================
    add_h1("5. Implementasi Inkremental Multi-Tahun Lintas Periode (etl_nhtsa_2020_2025.py)")
    add_body(
        "Untuk menangani volume data kecelakaan multi-tahun yang masif dari rentang 2020 hingga 2025, tim mengembangkan "
        "skrip etl_nhtsa_2020_2025.py dengan kapabilitas checkpointing database yang canggih."
    )

    add_h2("5.1 State Verification & Checkpointing Berdasarkan Database")
    add_body(
        "Sebelum mengunduh arsip, fungsi get_row_counts_by_year(db_uri) mengeksekusi query agregasi ke Supabase: "
        "SELECT EXTRACT(YEAR FROM crash_date)::INT AS yr, COUNT(*) FROM public.nhtsa_crash_analytics GROUP BY yr. "
        "Hasil agregasi ini digunakan sebagai offset unduhan, sehingga eksekusi harian hanya memproses baris data baru yang belum tersimpan."
    )
    add_image_box(
        "07_beam_seq_init_check.jpg",
        "Gambar 7. Modul state verification get_row_counts_by_year dan pengecekan ketersediaan arsip FARS via HTTP HEAD."
    )

    add_h2("5.2 Ekstraksi Batch Berkelanjutan dengan Offset Skipping")
    add_body(
        "Saat membaca accident.csv dari arsip ZIP tahun tertentu, pembacaan melompati sejumlah baris sebanyak offset eksisting. "
        "Jika data suatu tahun telah seluruhnya termuat ke Supabase, skrip secara otomatis mencetak log penuntasan dan beralih "
        "ke arsip tahun berikutnya secara sekuensial."
    )
    add_image_box(
        "08_beam_seq_batch_extract.jpg",
        "Gambar 8. Mekanisme batch offset streaming dan ekstraksi Kaggle metadata pada etl_nhtsa_2020_2025.py."
    )

    add_h2("5.3 Transformasi & Pembersihan Lintas Tahun")
    add_body(
        "Proses pembersihan tetap mempertahankan standar sanitasi tanggal yang ketat dan penggabungan metadata Kaggle "
        "untuk memastikan struktur data antar-tahun seragam dan konsisten."
    )
    add_image_box(
        "09_beam_seq_transform.jpg",
        "Gambar 9. Logika CleanAndJoinDoFn pada skrip pemrosesan sekuensial 2020–2025."
    )

    add_h2("5.4 Batch Ingestion ke Database Cloud")
    add_body(
        "Tahap pemuatan data mengeksekusi pipeline Beam dengan DirectRunner, memastikan setiap kumpulan elemen (batch) "
        "tersimpan dengan aman di tabel public.nhtsa_crash_analytics Supabase PostgreSQL."
    )
    add_image_box(
        "10_beam_seq_load_supabase.png",
        "Gambar 10. WriteToSupabaseDoFn dan perakitan pipeline Beam run_pipeline() pada etl_nhtsa_2020_2025.py."
    )

    # ==================== SECTION 6 ====================
    add_h1("6. Analisis Hasil Eksplorasi Data (Exploratory Data Analysis / EDA)")
    add_body(
        "Dataset hasil pemrosesan ETL yang telah bersih kemudian dianalisis untuk mengungkap pola insiden kecelakaan lalu lintas "
        "di Amerika Serikat. Visualisasi menggunakan sampel 10% (sebanyak 26.635 baris) dan data tahunan agregat."
    )

    add_h2("6.1 Tren Jumlah Kecelakaan Tahunan (2020–2024)")
    add_body(
        "Grafik garis tren tahunan memperlihatkan dinamika volume kecelakaan fatal dan serius di Amerika Serikat:",
        bold_prefix="Observasi Metrik Tahunan: "
    )
    add_bullet(" Pada tahun 2020 dan 2021, volume kecelakaan tercatat stabil di angka 35.000 kejadian. Angka ini mencerminkan dampak pembatasan mobilitas fisik (lockdown) dan kebijakan kerja dari rumah (WFH) selama fase kritis pandemi COVID-19.", "2020–2021 (Fase Pandemi):")
    add_bullet(" Terjadi peningkatan signifikan sebesar +71,4% menjadi 60.000 kejadian seiring pemulihan penuh aktivitas ekonomi, pembukaan kembali sektor pendidikan, dan naiknya kepadatan jalan raya antar-negara bagian.", "2022 (Fase Pemulihan):")
    add_bullet(" Volume kejadian mencapai puncak rekor tertinggi sebesar 132.165 kejadian (kenaikan lebih dari 220% dibanding 2022). Hal ini dipicu oleh integrasi penuh seluruh basis data pelaporan insiden federal dan lokal pasca-pandemi.", "2023 (Puncak Insiden):")
    add_bullet(" Tercatat 4.491 kejadian, yang merupakan snapshot data parsial dari kuartal awal tahun berjalan saat dataset dikompilasi.", "2024 (Data Parsial):")
    add_image_box(
        "11_eda_tren_tahunan.png",
        "Gambar 11. Grafik garis Tren Jumlah Kecelakaan Tahunan Amerika Serikat (2020 – 2024)."
    )

    add_h2("6.2 Distribusi Tingkat Keparahan (Severity) dan Pengaruh Kondisi Cuaca")
    add_body(
        "Dua visualisasi analitik berikut membedah profil keparahan kecelakaan dan hubungannya dengan parameter meteorologi:"
    )
    add_bullet(" Mayoritas kecelakaan berada pada kategori Moderate (71,9%), diikuti oleh kecelakaan Serious sebesar 17,1%. Kategori Minor menyumbang 7,5%, sedangkan kategori Severe (sangat parah / fatal memakan korban jiwa) mencakup 3,5% dari keseluruhan insiden.", "Proporsi Keparahan (Pie Chart):")
    add_bullet(" Scatter plot memperlihatkan konsentrasi titik kecelakaan paling padat berada pada rentang temperatur 40°F hingga 80°F dengan kelembapan relatif 40% hingga 90%. Temuan ini membuktikan bahwa sebagian besar insiden terjadi pada kondisi suhu moderat harian di saat volume kendaraan tinggi, bukan semata-mata pada kondisi cuaca ekstrem bersalju/beku.", "Temperatur vs Kelembapan (Scatter Plot):")
    add_image_box(
        "12_eda_keparahan_cuaca.jpg",
        "Gambar 12. Visualisasi Persentase Tingkat Keparahan Kecelakaan (kiri) dan Hubungan Temperatur vs Kelembapan Saat Kejadian (kanan)."
    )

    add_h2("6.3 Analisis Spasial: Top 15 Negara Bagian dengan Insiden Tertinggi")
    add_body(
        "Berdasarkan analisis sampel representatif 10% (26.635 baris), California (CA) menempati peringkat teratas "
        "dengan selisih yang sangat mencolok (>6.000 kejadian atau ~22,7% dari total sampel). "
        "Posisi berikutnya ditempati oleh Florida (FL, ~2.500 kejadian) dan Texas (TX, ~2.300 kejadian)."
    )
    add_body(
        "Konsentrasi tinggi di ketiga negara bagian ini berkorelasi langsung dengan tiga faktor geografis dan demografis: "
        "(1) Populasi penduduk tertinggi di AS; (2) Ketergantungan ekstrem terhadap transportasi kendaraan pribadi roda empat; "
        "(3) Jaringan jalan tol Interstate Highway yang sangat panjang dan padat aktivitas logistik."
    )
    add_image_box(
        "13_eda_top15_states.png",
        "Gambar 13. Diagram batang Top 15 Negara Bagian dengan Jumlah Kecelakaan Tertinggi (10% Sample, 26.635 baris)."
    )

    add_h2("6.4 Analisis Temporal: Pola Jam Kejadian dan Hari dalam Seminggu")
    add_body(
        "Analisis waktu memberikan wawasan mendalam mengenai ritme sirkadian dan kebiasaan mobilitas masyarakat Amerika Serikat:"
    )
    add_bullet(" Grafik distribusi per jam menunjukkan pola bimodal (dua gelombang puncak) yang tegas. Puncak pertama (Morning Rush Hour) terjadi pada pukul 07:00 – 08:00 pagi (~2.400 kejadian) saat jam berangkat kerja. Puncak kedua (Evening Rush Hour) terjadi pada pukul 16:00 – 17:00 sore (~1.950 kejadian) saat arus pulang kantor. Jam siang (10:00 – 12:00) stabil di ~1.000 kejadian, dan dini hari (00:00 – 04:00) berada di titik terendah (<300 kejadian).", "Pola Jam Kejadian (Bimodal Distribution):")
    add_bullet(" Volume kecelakaan pada hari kerja (Senin s.d. Jumat) sangat tinggi dan konsisten di kisaran 4.100 hingga 4.750 kejadian, mencapai puncaknya pada hari Kamis (~4.750 kejadian). Sebaliknya, pada akhir pekan (Sabtu dan Minggu), angka kecelakaan merosot tajam lebih dari 55% ke kisaran ~2.000 hingga ~2.150 kejadian. Hal ini membuktikan bahwa arus komuter harian adalah pemicu utama tingginya probabilitas kecelakaan.", "Pola Hari dalam Seminggu:")
    add_image_box(
        "14_eda_distribusi_waktu.png",
        "Gambar 14. Distribusi Kecelakaan Berdasarkan Jam Kejadian (kiri) dan Jumlah Kecelakaan Berdasarkan Hari (kanan)."
    )

    # ==================== SECTION 7 ====================
    add_h1("7. Kesimpulan Teknis & Rekomendasi Manajerial")
    add_body(
        "Pembangunan sistem Distributed ETL Pipeline dan analisis data ini berhasil membuktikan:",
        bold_prefix="Poin Keberhasilan Arsitektur: "
    )
    add_bullet(" Kombinasi Docker Compose, Airflow LocalExecutor, dan Apache Beam DirectRunner berhasil mengeksekusi pipeline ekstraksi dan transformasi multi-tahun secara stabil tanpa menimbulkan memory-leak atau disk bottleneck pada server host.", "Efisiensi Pipeline:")
    add_bullet(" Strategi deduplikasi komposit (f'{year}-{raw_case}') dan klausul SQL UPSERT menjamin idempotensi penuh; re-run DAG berkali-kali tidak akan menimbulkan duplikasi baris di Supabase PostgreSQL.", "Integritas & Idempotensi Data:")
    add_bullet(" Rekayasa sanitasi tanggal berhasil menyelesaikan kelemahan bawaan format kode FARS (98/99), menghasilkan dataset bersih berstandar industri yang siap dikonsumsi langsung oleh Power BI Desktop.", "Kualitas Data Analitik:")

    add_body(
        "Rekomendasi Kebijakan Lalu Lintas Berbasis Data:",
        bold_prefix="Implikasi Downstream: "
    )
    add_bullet(" Departemen transportasi negara bagian CA, FL, dan TX disarankan meningkatkan patroli dan manajemen kecepatan dinamis terutama pada koridor Interstate Highway pada jam sibuk pagi (07:00–08:00) dan sore (16:00–17:00).", "Fokus Penanganan Jam Sibuk:")
    add_bullet(" Kampanye keselamatan jalan raya harus memprioritaskan hari kerja (khususnya hari Kamis) saat tingkat kelelahan komuter akumulatif berada di puncak tertinggi.", "Manajemen Risiko Hari Kerja:")

    # Save
    doc.save(DOCX_OUT)
    print(f"[*] Successfully created Word document: {DOCX_OUT}")

if __name__ == "__main__":
    create_document()
