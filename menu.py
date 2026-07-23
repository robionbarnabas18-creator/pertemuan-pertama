def cek_ganjil_genap(angka):
    if angka % 2 == 0:
        print("Hasil: Angka GENAP")
    else:
        print("Hasil: Angka GANJIL")

def cek_prima(angka):
    if angka < 2:
        print("Hasil: BUKAN Prima")
        return

    jumlah_pembagi = 0
    for i in range(1, angka + 1):
        if angka % i == 0:
            jumlah_pembagi = jumlah_pembagi + 1

    if jumlah_pembagi == 2:
        print("Hasil: Bilangan PRIMA")
    else:
        print("Hasil: BUKAN Prima")

def hitung_luas(panjang, lebar):
    luas = panjang * lebar
    print("Hasil Luas:", luas)

def mainkan():
    while True:
        print("\n--- MENU PILIHAN ---")
        print("1. Cek Ganjil / Genap")
        print("2. Cek Bilangan Prima")
        print("3. Hitung Luas Persegi Panjang")
        print("4. Keluar")

        pilihan = input("Pilih menu (1-4): ")

        if pilihan == "1":
            angka = int(input("Masukkan angka: "))
            cek_ganjil_genap(angka)  

        elif pilihan == "2":
            angka = int(input("Masukkan angka: "))
            cek_prima(angka)
          
        elif pilihan == "3":
            p = float(input("Masukkan panjang: "))
            l = float(input("Masukkan lebar: "))
            hitung_luas(p, l)   

        elif pilihan == "4":
            print("Terima kasih, program selesai!")
            break

        else:
            print("Pilihan tidak ada, silakan coba lagi.")

mainkan()
