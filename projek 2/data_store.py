"""Penyimpanan data lokal berbasis CSV untuk OutletFinder."""

import csv
import os

# Bagian ini menentukan lokasi berkas CSV untuk akun, outlet, dan favorit.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNT_FILE = os.path.join(BASE_DIR, "akun.csv")
OUTLET_FILE = os.path.join(BASE_DIR, "outlet.csv")
FAVORITE_FILE = os.path.join(BASE_DIR, "favorit.csv")


# Bagian ini menjelaskan fungsi initialize data dan tugasnya dalam aplikasi.
def initialize_data():
    if not os.path.exists(ACCOUNT_FILE):
        with open(ACCOUNT_FILE, "w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerows([
                ["Username", "Password", "Role"],
                ["admin", "admin123", "admin"],
            ])
    if not os.path.exists(OUTLET_FILE):
        with open(OUTLET_FILE, "w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerows([
                ["Nama", "Latitude", "Longitude", "Kategori", "Deskripsi"],
                ["Outlet Pusat", "-7.8189", "112.0112", "Umum", "Outlet utama mitra kami."],
            ])
    if not os.path.exists(FAVORITE_FILE):
        with open(FAVORITE_FILE, "w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(["Username", "Nama", "Latitude", "Longitude"])
