# OutletFinder — UI/UX Redesign

Versi ini mempertahankan aplikasi **Python + Kivy** tetapi mengubah tampilan agar mengikuti referensi `New folder (2)`:
- mobile-first blue/white UI
- header dan search bar modern
- outlet card dengan thumbnail, kategori, jarak, favorit, Detail/Salin/Rute
- bottom navigation
- onboarding
- pilihan role User/Admin
- login & register
- halaman favorit
- detail outlet
- profil akun
- panel/form admin untuk tambah dan edit outlet
- rounded card, chip, soft blue background, navy admin action, dan soft-red logout

## Jalankan

```powershell
python outlet.py
```

## GPS perangkat (Android)

Tombol **Aktifkan GPS** meminta izin lokasi saat aplikasi dibuka, lalu memperbarui koordinat selama aplikasi aktif. Untuk APK Buildozer, tambahkan Plyer dan izin lokasi pada `buildozer.spec`:

```ini
requirements = python3,kivy,plyer
android.permissions = ACCESS_COARSE_LOCATION,ACCESS_FINE_LOCATION
```

Jalankan APK di perangkat Android dan izinkan akses lokasi. Saat dijalankan di Windows, tombol menjelaskan bahwa provider GPS perangkat belum tersedia di build desktop ini.

## Akun admin bawaan

- Username: `admin`
- Password: `admin123`

## Struktur

- `outlet.py` — entry point
- `app.py` — UI, navigasi, dan interaksi
- `theme.py` — warna/design system
- `data_store.py` — CSV storage
- `akun.csv` — akun lokal
- `outlet.csv` — data outlet
- `favorit.csv` — data favorit
- `logo.png` — aset logo

> Catatan: mode lokasi desktop masih memakai koordinat demo, seperti versi sebelumnya. Google Maps dibuka melalui browser untuk tombol Rute.
