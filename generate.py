import pickle
import os
from datetime import datetime, timezone, timedelta
import ntplib

def get_ntp_time():
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org', version=3)
        return datetime.fromtimestamp(response.tx_time, timezone.utc)
    except Exception as e:
        print(f"Gagal ambil waktu NTP: {e}")
        return datetime.now(timezone.utc)

def generate_license():
    LICENSE_FILE = "license.pkl"
    trial_days = 7  # <--- Tentukan di sini!
    start_time = get_ntp_time()
    end_time = start_time + timedelta(days=trial_days)
    with open(LICENSE_FILE, "wb") as f:
        pickle.dump((start_time, trial_days), f)  # Simpan tuple
    print("=" * 60)
    print("✅ LICENSE FILE BERHASIL DIBUAT!")
    print("=" * 60)
    print(f"📁 File: {os.path.abspath(LICENSE_FILE)}")
    print(f"📅 Tanggal mulai trial: {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"⏰ Trial akan berakhir: {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')} ({trial_days} hari dari sekarang)")

if __name__ == "__main__":
    generate_license()