"""
Aplikasi Kasir Sederhana
========================
Dibuat menggunakan Python + Kivy sebagai projek UI/UX.

Fitur:
- Menampilkan daftar produk berdasarkan kategori
- Menambahkan produk ke keranjang belanja
- Mengubah jumlah (qty) produk di keranjang
- Menghitung total belanja otomatis
- Proses checkout dan menyimpan ke riwayat transaksi
- Melihat riwayat transaksi yang sudah dilakukan

Struktur file:
- main.py            -> entry point aplikasi & logic
- data.py             -> data produk contoh
- screens/kasir.kv    -> layout / tampilan (UI) dengan KV language
"""

from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp

from data import PRODUCTS, KATEGORI

Window.size = (400, 700)  # simulasi ukuran layar smartphone


def format_rupiah(angka):
    """Format angka menjadi format mata uang Rupiah, contoh: 15000 -> Rp15.000"""
    return "Rp{:,.0f}".format(angka).replace(",", ".")


class ProductCard(BoxLayout):
    """Widget kartu produk yang ditampilkan di grid katalog."""
    nama = StringProperty("")
    harga = NumericProperty(0)
    product_id = NumericProperty(0)
    harga_text = StringProperty("")

    def on_harga(self, instance, value):
        self.harga_text = format_rupiah(value)


class CartItem(BoxLayout):
    """Widget baris item di dalam keranjang belanja."""
    nama = StringProperty("")
    harga = NumericProperty(0)
    qty = NumericProperty(1)
    product_id = NumericProperty(0)
    subtotal_text = StringProperty("")

    def update_subtotal(self):
        self.subtotal_text = format_rupiah(self.harga * self.qty)


class POSScreen(Screen):
    """Layar utama kasir: katalog produk + keranjang belanja."""

    total_text = StringProperty("Rp0")
    kategori_aktif = StringProperty("Semua")

    def on_pre_enter(self, *args):
        self.cart = {}  # {product_id: {"nama":.., "harga":.., "qty":..}}
        self.render_products()
        self.render_cart()

    def render_products(self, kategori=None):
        if kategori is None:
            kategori = self.kategori_aktif
        self.kategori_aktif = kategori

        grid = self.ids.product_grid
        grid.clear_widgets()

        for p in PRODUCTS:
            if kategori != "Semua" and p["kategori"] != kategori:
                continue
            card = ProductCard(
                nama=p["nama"],
                harga=p["harga"],
                product_id=p["id"],
            )
            grid.add_widget(card)

    def tambah_ke_keranjang(self, product_id, nama, harga):
        if product_id in self.cart:
            self.cart[product_id]["qty"] += 1
        else:
            self.cart[product_id] = {"nama": nama, "harga": harga, "qty": 1}
        self.render_cart()

    def ubah_qty(self, product_id, delta):
        if product_id not in self.cart:
            return
        self.cart[product_id]["qty"] += delta
        if self.cart[product_id]["qty"] <= 0:
            del self.cart[product_id]
        self.render_cart()

    def render_cart(self):
        cart_box = self.ids.cart_list
        cart_box.clear_widgets()

        total = 0
        for pid, item in self.cart.items():
            row = CartItem(
                nama=item["nama"],
                harga=item["harga"],
                qty=item["qty"],
                product_id=pid,
            )
            row.update_subtotal()
            cart_box.add_widget(row)
            total += item["harga"] * item["qty"]

        self.total_text = format_rupiah(total)
        self.ids.checkout_btn.disabled = total == 0

    def checkout(self):
        if not self.cart:
            return

        total = sum(i["harga"] * i["qty"] for i in self.cart.values())
        item_count = sum(i["qty"] for i in self.cart.values())
        waktu = datetime.now().strftime("%d-%m-%Y %H:%M")

        app = App.get_running_app()
        app.riwayat.insert(0, {
            "waktu": waktu,
            "items": dict(self.cart),
            "total": total,
            "item_count": item_count,
        })

        self.tampilkan_struk(waktu, total, item_count)

        # reset keranjang setelah checkout
        self.cart = {}
        self.render_cart()

    def tampilkan_struk(self, waktu, total, item_count):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(16))
        content.add_widget(Label(text="Transaksi Berhasil!", bold=True, font_size="18sp"))
        content.add_widget(Label(text=waktu, font_size="13sp"))
        content.add_widget(Label(text=f"{item_count} item", font_size="13sp"))
        content.add_widget(Label(text=f"Total: {format_rupiah(total)}", font_size="16sp", bold=True))
        close_btn = Button(text="Tutup", size_hint_y=None, height=dp(44))
        content.add_widget(close_btn)

        popup = Popup(title="Struk Belanja", content=content,
                       size_hint=(0.85, 0.5), auto_dismiss=False)
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def buka_riwayat(self):
        self.manager.current = "riwayat"


class RiwayatScreen(Screen):
    """Layar untuk melihat riwayat transaksi yang sudah di-checkout."""

    def on_pre_enter(self, *args):
        self.render_riwayat()

    def render_riwayat(self):
        box = self.ids.riwayat_list
        box.clear_widgets()

        app = App.get_running_app()
        if not app.riwayat:
            box.add_widget(Label(
                text="Belum ada transaksi.",
                size_hint_y=None, height=dp(40)
            ))
            return

        for trx in app.riwayat:
            row = BoxLayout(orientation="vertical", size_hint_y=None,
                             height=dp(64), padding=(dp(12), dp(6)))
            row.add_widget(Label(
                text=f"[b]{trx['waktu']}[/b]  -  {trx['item_count']} item",
                markup=True, size_hint_y=None, height=dp(24),
                halign="left", valign="middle"
            ))
            row.add_widget(Label(
                text=format_rupiah(trx["total"]),
                size_hint_y=None, height=dp(24),
                halign="left", valign="middle", color=(0.2, 0.6, 0.2, 1)
            ))
            box.add_widget(row)

    def kembali(self):
        self.manager.current = "kasir"


class KasirApp(App):
    riwayat = ListProperty([])

    def build(self):
        self.title = "Aplikasi Kasir Sederhana"
        Builder.load_file("screens/kasir.kv")

        sm = ScreenManager()
        sm.add_widget(POSScreen(name="kasir"))
        sm.add_widget(RiwayatScreen(name="riwayat"))
        return sm


if __name__ == "__main__":
    KasirApp().run()
