import pandas as pd
import urllib.request
import io
import os

# =============================================================================
# KONFIGURASI
# =============================================================================
# 1. File Kaggle yang sudah Anda download manual
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / 'data' / 'raw'
DATA_PROCESSED = PROJECT_ROOT / 'data' / 'processed'
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

KAGGLE_FILE_PATH = DATA_RAW / 'US_Accidents_March23.csv'

# 2. Endpoint API NHTSA
NHTSA_API_URL = 'https://crashviewer.nhtsa.dot.gov/crashviewer/CrashAPI/crashes/GetCaseList?format=csv'

# 3. Nama file output untuk hasil API
API_OUTPUT_FILE = DATA_RAW / 'nhtsa_api_data.csv'

def gather_nhtsa_api():
    """Fungsi untuk menarik data dari API NHTSA dan menyimpannya ke CSV."""
    print("🔄 Menghubungkan ke API NHTSA...")
    
    # Menggunakan header yang lebih lengkap untuk menghindari 403 Forbidden
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/csv'
    }
    
    try:
        req = urllib.request.Request(NHTSA_API_URL, headers=headers)
        with urllib.request.urlopen(req) as response:
            content = response.read()
            # Simpan hasil API langsung ke file CSV
            with open(API_OUTPUT_FILE, 'wb') as f:
                f.write(content)
            print(f"✅ Data API berhasil disimpan ke {API_OUTPUT_FILE}")
            return True
    except Exception as e:
        print(f"❌ Gagal mengambil data API: {e}")
        return False

def prepare_for_colab():
    """Fungsi untuk mengecek apakah kedua file sudah siap diupload ke Colab."""
    print("\n" + "="*30)
    print("VERIFIKASI FILE UNTUK COLAB")
    print("="*30)
    
    # Cek Kaggle File
    if os.path.exists(KAGGLE_FILE_PATH):
        print(f"✅ {KAGGLE_FILE_PATH} : TERSEDIA")
    else:
        print(f"❌ {KAGGLE_FILE_PATH} : TIDAK DITEMUKAN (Silakan download manual dari Kaggle)")
        
    # Cek API File
    if os.path.exists(API_OUTPUT_FILE):
        print(f"✅ {API_OUTPUT_FILE} : TERSEDIA")
    else:
        print(f"❌ {API_OUTPUT_FILE} : TIDAK DITEMUKAN")

if __name__ == "__main__":
    print("🚀 Memulai Proses Gathering Data...\n")
    
    # Jalankan penarikan API
    gather_nhtsa_api()
    
    # Cek kesiapan file
    prepare_for_colab()
    
    print("\n👉 Sekarang Anda bisa mengupload kedua file tersebut ke Google Colab.")