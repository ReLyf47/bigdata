import urllib.request
import csv
import io

def test_api():
    url = 'https://crashviewer.nhtsa.dot.gov/crashviewer/CrashAPI/crashes/GetCaseList?format=csv'
    print(f"Testing connection to: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
            reader = csv.reader(io.StringIO(content))
            header = next(reader)
            print("✅ Connection Successful!")
            print("Header found:", header)
            return True
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return False

if __name__ == "__main__":
    test_api()
