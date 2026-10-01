"""OutletFinder - perancangan ulang antarmuka yang terinspirasi dari contoh tampilan ponsel.
Python dan Kivy tanpa ketergantungan antarmuka tambahan.
"""
import csv
from importlib import import_module
import math
import webbrowser

from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex, platform

from theme import (
    BLUE, BLUE_DARK, ERROR, INK, LINE, NAVY, PALE, SLATE, SOFT_BLUE,
    SOFT_GREEN, SOFT_RED, SUCCESS, WHITE,
)
from data_store import ACCOUNT_FILE, FAVORITE_FILE, OUTLET_FILE, initialize_data

# Bagian ini mengatur ukuran jendela dan latar aplikasi pada komputer desktop.
if platform not in ("android", "ios"):
    Window.size = (420, 800)
    Window.clearcolor = PALE


# Bagian ini membuat label teks dengan ukuran, warna, dan perataan yang dapat diatur.
def make_label(text="", size=13, color=INK, bold=False, height=None, align="left"):
    w = Label(
        text=text, font_size=f"{size}sp", color=color, bold=bold,
        halign=align, valign="middle", shorten=False
    )
    w.bind(size=lambda widget, value: setattr(widget, "text_size", (value[0], None)))
    if height is not None:
        w.size_hint_y = None
        w.height = dp(height)
    return w


# Bagian ini menjelaskan fungsi rounded dan tugasnya dalam aplikasi.
def rounded(widget, fill=WHITE, radius=14, border=None):
    with widget.canvas.before:
        Color(*fill)
        shape = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(radius)])
        outline = None
        if border:
            Color(*border)
            outline = Line(
                rounded_rectangle=(widget.x, widget.y, widget.width, widget.height, dp(radius)),
                width=1
            )
    widget.bind(pos=lambda w, v: setattr(shape, "pos", v))
    widget.bind(size=lambda w, v: setattr(shape, "size", v))
    if outline:
        widget.bind(
            pos=lambda w, v: setattr(outline, "rounded_rectangle",
                                     (w.x, w.y, w.width, w.height, dp(radius)))
        )
        widget.bind(
            size=lambda w, v: setattr(outline, "rounded_rectangle",
                                      (w.x, w.y, w.width, w.height, dp(radius)))
        )
    return widget


# Bagian ini membuat tombol utama dan menghubungkannya dengan fungsi aksi.
def action_button(text, callback, fill=BLUE, text_color=WHITE, height=44, radius=10):
    b = Button(
        text=text, background_normal="", background_down="",
        background_color=fill, color=text_color, bold=True, font_size="12sp",
        size_hint_y=None, height=dp(height), halign="center", valign="middle"
    )
    b.bind(on_release=lambda *_: callback())
    # Membuat tombol dengan sudut membulat.
    rounded(b, fill, radius)
    return b


# Bagian ini membuat tombol sederhana untuk menjalankan aksi tambahan.
def ghost_button(text, callback, height=40):
    return action_button(text, callback, WHITE, INK, height, 10)


# Bagian ini menjelaskan fungsi field dan tugasnya dalam aplikasi.
def field(hint, value="", password=False, height=46):
    # Mengatur latar kolom input agar pekat. Jangan bergantung pada tekstur TextInput dari Kivy,
    # karena pada beberapa kombinasi Windows dan Kivy, latarnya dapat terlihat tembus pandang.
    w = TextInput(
        hint_text=hint,
        text=value,
        password=password,
        multiline=False,
        background_normal="",
        background_active="",
        background_disabled_normal="",
        background_color=(1, 1, 1, 1),
        foreground_color=NAVY,
        hint_text_color=(0.42, 0.48, 0.58, 1),
        padding=(dp(13), dp(12)),
        font_size="14sp",
        size_hint_y=None,
        height=dp(height),
        cursor_color=BLUE,
        selection_color=SOFT_BLUE,
    )

    # Menggambar bidang putih pekat di belakang kolom TextInput.
    with w.canvas.before:
        Color(1, 1, 1, 1)
        bg = RoundedRectangle(
            pos=w.pos,
            size=w.size,
            radius=[dp(10)]
        )
        border_color = Color(*LINE)
        border = Line(
            rounded_rectangle=(w.x, w.y, w.width, w.height, dp(10)),
            width=1
        )

    # Bagian ini menjelaskan fungsi sync bg dan tugasnya dalam aplikasi.
    def sync_bg(*_):
        bg.pos = w.pos
        bg.size = w.size
        border.rounded_rectangle = (
            w.x, w.y, w.width, w.height, dp(10)
        )

    w.bind(pos=sync_bg, size=sync_bg)

    # Menjaga teks nama pengguna dan kata sandi tetap jelas dengan warna biru tua.
    # Menerapkan kembali warna saat kolom dipilih karena beberapa tema Kivy dan Windows
    # dapat mengganti warna TextInput ketika kolom mulai aktif.
    # Bagian ini menjaga warna teks dan kursor tetap jelas saat kolom dipilih.
    def keep_text_color(widget, focused):
        widget.foreground_color = NAVY
        widget.cursor_color = BLUE
        border_color.rgb = BLUE_DARK[:3] if focused else LINE[:3]
        border_color.a = 1

    w.bind(focus=keep_text_color)
    keep_text_color(w, False)
    w.foreground_color = NAVY
    return w


# Bagian ini menjelaskan fungsi password row dan tugasnya dalam aplikasi.
def password_row(hint):
    row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(6))
    password_input = field(hint, password=True)
    row.add_widget(password_input)

    # Bagian ini menjelaskan fungsi toggle password dan tugasnya dalam aplikasi.
    def toggle_password():
        password_input.password = not password_input.password
        toggle.text = "LIHAT" if password_input.password else "SEMBUNYIKAN"

    toggle = action_button("LIHAT", toggle_password, PALE, INK, 46, 10)
    toggle.size_hint_x = None
    toggle.width = dp(82)
    row.add_widget(toggle)
    return row, password_input


# Bagian ini menjelaskan kelas BaseScreen dan tugasnya dalam aplikasi.
class BaseScreen(Screen):
    # Bagian ini menjelaskan fungsi page dan tugasnya dalam aplikasi.
    def page(self, padding=16, spacing=10):
        root = BoxLayout(orientation="vertical", padding=dp(padding), spacing=dp(spacing))
        self.add_widget(root)
        return root

    # Bagian ini menjelaskan fungsi title bar dan tugasnya dalam aplikasi.
    def title_bar(self, parent, title, back=None, right=""):
        bar = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        if back:
            b = ghost_button("KEMBALI", back, 38)
            b.size_hint_x = None
            b.width = dp(92)
            bar.add_widget(b)
        else:
            bar.add_widget(make_label("", 1, WHITE, False, 1))
        title_box = BoxLayout(orientation="vertical")
        title_box.add_widget(make_label(title, 17, INK, True, 26))
        bar.add_widget(title_box)
        if right:
            r = make_label(right, 11, BLUE, True, 36, "right")
            r.size_hint_x = .7
            bar.add_widget(r)
        parent.add_widget(bar)

    # Bagian ini menjelaskan fungsi heading dan tugasnya dalam aplikasi.
    def heading(self, parent, title, subtitle=""):
        parent.add_widget(make_label(title, 22, INK, True, 34))
        # Garis biru dekoratif di bawah judul.
        line = BoxLayout(size_hint_y=None, height=dp(3))
        with line.canvas.before:
            Color(*BLUE)
            rect = RoundedRectangle(pos=line.pos, size=line.size, radius=[dp(2)])
        line.bind(pos=lambda w, v: setattr(rect, "pos", v))
        line.bind(size=lambda w, v: setattr(rect, "size", v))
        parent.add_widget(line)
        if subtitle:
            parent.add_widget(make_label(subtitle, 11, SLATE, False, 34))


# Bagian ini menjelaskan kelas WelcomeScreen dan tugasnya dalam aplikasi.
class WelcomeScreen(BaseScreen):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(name="welcome", **kwargs)
        root = self.page(18, 9)
        top = BoxLayout(size_hint_y=None, height=dp(44))
        top.add_widget(make_label("OUTLETLOCATOR", 14, BLUE, True, 40))
        profile = make_label("", 20, BLUE, True, 40, "right")
        top.add_widget(profile)
        root.add_widget(top)

        root.add_widget(make_label("PENCARIAN OUTLET", 10, BLUE, True, 22))
        root.add_widget(make_label("Temukan outlet\ndi sekitar Anda.", 25, INK, True, 70))
        root.add_widget(make_label(
            "Cari outlet di sekitar Anda, lihat detail, simpan favorit,\n"
            "dan dapatkan rute dengan cepat.", 12, SLATE, False, 46
        ))

        map_card = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6),
                             size_hint_y=None, height=dp(190))
        rounded(map_card, SOFT_BLUE, 16)
        map_card.add_widget(make_label("MULAI DARI SINI", 10, BLUE, True, 24))
        map_card.add_widget(make_label("Cari berdasarkan nama\natau kategori outlet", 20, NAVY, True, 72, "center"))
        map_card.add_widget(make_label("Lokasi dapat digunakan untuk mengurutkan jarak.", 10, SLATE, False, 24, "center"))
        root.add_widget(map_card)

        tips = BoxLayout(orientation="vertical", padding=dp(13), spacing=4,
                         size_hint_y=None, height=dp(130))
        rounded(tips, NAVY, 14)
        tips.add_widget(make_label("KENAPA OUTLETLOCATOR?", 10, SOFT_BLUE, True, 22))
        tips.add_widget(make_label("Pencarian outlet berdasarkan nama & kategori", 11, WHITE, False, 24))
        tips.add_widget(make_label("Simpan outlet favorit", 11, WHITE, False, 24))
        tips.add_widget(make_label("Buka rute Google Maps", 11, WHITE, False, 24))
        root.add_widget(tips)
        root.add_widget(Label())
        root.add_widget(action_button("MULAI CARI OUTLET", self.start, BLUE, WHITE, 48))
        root.add_widget(action_button("Belum punya akun? Daftar", self.register_user,
                                      WHITE, BLUE, 40, 8))

    # Bagian ini menjelaskan fungsi start dan tugasnya dalam aplikasi.
    def start(self):
        app = App.get_running_app()
        app.go("role" if not app.logged_in else "main")

    # Bagian ini menjelaskan fungsi register user dan tugasnya dalam aplikasi.
    def register_user(self):
        app = App.get_running_app()
        app.target_role = "user"
        app.go("register")


# Bagian ini menjelaskan kelas RoleScreen dan tugasnya dalam aplikasi.
class RoleScreen(BaseScreen):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(name="role", **kwargs)
        root = self.page(16, 10)
        self.title_bar(root, "Pilih Peran", lambda: App.get_running_app().go("welcome", "right"), "OutletLocator")
        root.add_widget(make_label("PILIH AKSES MASUK", 10, BLUE, True, 20))
        root.add_widget(make_label("Gunakan fitur sesuai peran Anda di OutletFinder.", 12, SLATE, False, 34))

        user = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(5),
                         size_hint_y=None, height=dp(170))
        rounded(user, WHITE, 14, LINE)
        user.add_widget(make_label("PENGGUNA / PENGUNJUNG", 15, BLUE, True, 28))
        user.add_widget(make_label("Cari outlet, lihat detail, simpan favorit,\ndan buka rute menuju outlet.", 11, SLATE, False, 42))
        user.add_widget(action_button("LANJUT SEBAGAI PENGGUNA",
                                      lambda: self.choose("user"), BLUE, WHITE, 44))
        root.add_widget(user)

        admin = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(5),
                          size_hint_y=None, height=dp(170))
        rounded(admin, WHITE, 14, LINE)
        admin.add_widget(make_label("ADMIN OUTLET", 15, NAVY, True, 28))
        admin.add_widget(make_label("Kelola data outlet, kategori, lokasi,\ndan informasi yang tampil ke pengguna.", 11, SLATE, False, 42))
        admin.add_widget(action_button("MASUK SEBAGAI ADMIN",
                                        lambda: self.choose("admin"), NAVY, WHITE, 44))
        root.add_widget(admin)
        root.add_widget(Label())
        root.add_widget(make_label("Akses admin membutuhkan akun admin.", 10, SLATE, False, 24, "center"))

    # Bagian ini menjelaskan fungsi choose dan tugasnya dalam aplikasi.
    def choose(self, role):
        app = App.get_running_app()
        app.target_role = role
        app.go("login")


# Bagian ini menjelaskan kelas LoginScreen dan tugasnya dalam aplikasi.
class LoginScreen(BaseScreen):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(name="login", **kwargs)
        root = self.page(18, 10)
        self.title_bar(root, "Masuk", lambda: App.get_running_app().go("role", "right"), "")
        root.add_widget(make_label("Selamat Datang Kembali", 22, INK, True, 34))
        root.add_widget(make_label(
            "Masuk ke akun Anda untuk mengakses pencarian outlet\ndan fitur sesuai peran.", 11, SLATE, False, 42
        ))

        tabs = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(6))
        tabs.add_widget(action_button("  Masuk", lambda: None, SOFT_BLUE, BLUE, 36))
        tabs.add_widget(action_button("DAFTAR BARU", self.register, WHITE, SLATE, 36))
        root.add_widget(tabs)

        root.add_widget(make_label("USERNAME / ID PENGGUNA", 10, SLATE, True, 20))
        self.username = field("Masukkan username (min. 3 karakter)")
        root.add_widget(self.username)
        root.add_widget(make_label("KATA SANDI", 10, SLATE, True, 20))
        password_box, self.password = password_row("Masukkan password")
        root.add_widget(password_box)
        self.message = make_label("", 11, ERROR, True, 28)
        root.add_widget(self.message)
        root.add_widget(action_button("MASUK SEKARANG", self.login, BLUE, WHITE, 48))
        root.add_widget(make_label("ATAU MASUK SEBAGAI", 10, SLATE, False, 24, "center"))
        root.add_widget(action_button("MODE PENJELAJAH (TAMU)", self.guest, SOFT_BLUE, BLUE, 42))
        root.add_widget(Label())
        root.add_widget(make_label("Belum punya akun OutletFinder?", 10, SLATE, False, 20, "center"))
        root.add_widget(action_button("BUAT AKUN BARU", self.register, SOFT_BLUE, BLUE, 40))

    # Bagian ini menjelaskan fungsi login dan tugasnya dalam aplikasi.
    def login(self):
        app = App.get_running_app()
        username, password = self.username.text.strip(), self.password.text.strip()
        if len(username) < 1 or len(password) < 1:
            self.message.text = "Username dan password wajib diisi."
            return
        with open(ACCOUNT_FILE, encoding="utf-8") as file:
            account = next((r for r in csv.DictReader(file)
                            if r["Username"].strip().lower() == username.lower()), None)
        if not account:
            self.message.text = "Akun tidak ditemukan. Silakan daftar terlebih dahulu."
            return
        if account["Password"].strip() != password:
            self.message.text = "Password tidak sesuai."
            return
        is_admin = account["Role"].strip().lower() == "admin"
        if (app.target_role == "admin") != is_admin:
            self.message.text = "Gunakan jalur akses sesuai role akun."
            return
        app.current_user, app.is_admin, app.logged_in = username, is_admin, True
        self.password.text = ""
        self.message.text = ""
        app.go("main")

    # Bagian ini menjelaskan fungsi guest dan tugasnya dalam aplikasi.
    def guest(self):
        app = App.get_running_app()
        app.current_user, app.is_admin, app.logged_in = "Tamu", False, True
        app.go("main")

    # Bagian ini menjelaskan fungsi register dan tugasnya dalam aplikasi.
    def register(self):
        App.get_running_app().go("register")


# Bagian ini menjelaskan kelas RegisterScreen dan tugasnya dalam aplikasi.
class RegisterScreen(BaseScreen):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(name="register", **kwargs)
        root = self.page(18, 10)
        self.title_bar(root, "Daftar", lambda: App.get_running_app().go("login", "right"), "OutletLocator")
        self.heading(root, "Buat Akun Baru", "Username dan password minimal 3 karakter.")
        root.add_widget(make_label("USERNAME", 10, SLATE, True, 20))
        self.username = field("Buat username")
        root.add_widget(self.username)
        root.add_widget(make_label("PASSWORD", 10, SLATE, True, 20))
        password_box, self.password = password_row("Buat password")
        root.add_widget(password_box)
        self.message = make_label("", 11, ERROR, True, 28)
        root.add_widget(self.message)
        root.add_widget(action_button("BUAT AKUN", self.create, BLUE, WHITE, 48))
        root.add_widget(Label())

    # Bagian ini menjelaskan fungsi create dan tugasnya dalam aplikasi.
    def create(self):
        username, password = self.username.text.strip(), self.password.text.strip()
        if len(username) < 3 or len(password) < 3:
            self.message.text = "Username dan password minimal 3 karakter."
            return
        with open(ACCOUNT_FILE, encoding="utf8") as file:
            if any(r["Username"].strip().lower() == username.lower() for r in csv.DictReader(file)):
                self.message.text = "Username sudah digunakan."
                return
        app = App.get_running_app()
        with open(ACCOUNT_FILE, "a", newline="", encoding="utf8") as file:
            csv.writer(file).writerow([username, password, "admin" if app.target_role == "admin" else "user"])
        app.popup("Akun berhasil dibuat", "Silakan masuk menggunakan akun baru Anda.")
        app.go("login", "right")


# Bagian ini menjelaskan kelas BottomNav dan tugasnya dalam aplikasi.
class BottomNav(BoxLayout):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, active="home", **kwargs):
        super().__init__(size_hint_y=None, height=dp(56), spacing=dp(5), padding=(dp(4), dp(4)), **kwargs)
        self.active = active
        self.update_items()

    # Bagian ini menjelaskan fungsi update items dan tugasnya dalam aplikasi.
    def update_items(self):
        self.clear_widgets()
        app = App.get_running_app()
        items = [("Cari", "main", "home"), ("Favorit", "favorites", "fav")]
        if app.is_admin:
            items.append(("Kelola", "admin", "admin"))
        items.append(("Profil", "profile", "profile"))
        for text, screen, key in items:
            fill = BLUE if key == self.active else WHITE
            color = WHITE if key == self.active else SLATE
            callback = lambda s=screen: app.go(s, "left")
            b = action_button(text, callback, fill, color, 48, 9)
            self.add_widget(b)


# Bagian ini menjelaskan kelas MainScreen dan tugasnya dalam aplikasi.
class MainScreen(BaseScreen):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(name="main", **kwargs)
        self.user_lat = self.user_lon = None
        self.only_favorites = False
        self.selected_category = "Semua kategori"
        root = self.page(12, 7)

        top = BoxLayout(size_hint_y=None, height=dp(48))
        left = BoxLayout(orientation="vertical")
        left.add_widget(make_label("Halo, " + "Pengguna", 10, SLATE, False, 17))
        self.greeting = make_label("Temukan Outlet", 18, INK, True, 28)
        left.add_widget(self.greeting)
        top.add_widget(left)
        profile = action_button("PROFIL", lambda: App.get_running_app().go("profile"), SOFT_BLUE, BLUE, 40)
        profile.size_hint_x = None
        profile.width = dp(44)
        top.add_widget(profile)
        root.add_widget(top)

        search_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        self.search = field("Cari nama, kategori, atau deskripsi...", height=44)
        self.search.bind(text=lambda *_: self.render())
        search_row.add_widget(self.search)
        filter_btn = action_button("KATEGORI", self.toggle_filter, SOFT_BLUE, BLUE, 44)
        filter_btn.size_hint_x = None
        filter_btn.width = dp(82)
        search_row.add_widget(filter_btn)
        root.add_widget(search_row)

        self.filter_box = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(5))
        self.filter_box.add_widget(action_button("Semua", self.all_outlets, BLUE, WHITE, 34))
        self.filter_box.add_widget(action_button("Terdekat", self.locate, WHITE, SLATE, 34))
        self.filter_box.add_widget(action_button("Favorit", self.show_favorites, WHITE, SLATE, 34))
        root.add_widget(self.filter_box)

        self.category_box = BoxLayout(size_hint_y=None, height=dp(0), spacing=dp(5), opacity=0)
        self.category_spinner = Spinner(text="Semua kategori", values=("Semua kategori",),
                                        size_hint_y=None, height=dp(36), font_size="12sp",
                                        background_normal="", background_color=WHITE, color=INK)
        self.category_spinner.bind(text=self.apply_category)
        self.category_box.add_widget(self.category_spinner)
        root.add_widget(self.category_box)

        self.result_summary = make_label("Semua kategori", 10, SLATE, False, 22)
        root.add_widget(self.result_summary)

        location_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(6))
        self.status = make_label("GPS belum diaktifkan.", 10, SLATE, False, 34)
        location_row.add_widget(self.status)
        self.gps_button = action_button("AKTIFKAN GPS", self.toggle_gps, SOFT_BLUE, BLUE, 34, 8)
        self.gps_button.size_hint_x = None
        self.gps_button.width = dp(112)
        location_row.add_widget(self.gps_button)
        root.add_widget(location_row)

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        self.results = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=(0, dp(2)))
        self.results.bind(minimum_height=self.results.setter("height"))
        scroll.add_widget(self.results)
        root.add_widget(scroll)

        self.bottom_nav = BottomNav("home")
        root.add_widget(self.bottom_nav)

    # Bagian ini menjelaskan fungsi toggle filter dan tugasnya dalam aplikasi.
    def toggle_filter(self):
        opened = self.category_box.height < dp(10)
        self.category_box.height = dp(38) if opened else dp(0)
        self.category_box.opacity = 1 if opened else 0

    # Bagian ini menjelaskan fungsi on pre enter dan tugasnya dalam aplikasi.
    def on_pre_enter(self, *_):
        app = App.get_running_app()
        self.bottom_nav.update_items()
        self.user_lat, self.user_lon = app.user_lat, app.user_lon
        self.only_favorites = False
        self.greeting.text = "Temukan Outlet" if app.current_user in ("", "Tamu") else f"Halo, {app.current_user}"
        self.load_categories()
        self.render()
        self.update_gps_button()

    # Bagian ini menjelaskan fungsi load categories dan tugasnya dalam aplikasi.
    def load_categories(self):
        cats = ["Semua kategori"]
        with open(OUTLET_FILE, encoding="utf8") as file:
            for row in csv.DictReader(file):
                c = (row.get("Kategori") or "Umum").strip().title()
                if c not in cats:
                    cats.append(c)
        self.category_spinner.values = tuple(cats)
        if self.selected_category not in cats:
            self.selected_category = "Semua kategori"
        if self.category_spinner.text != self.selected_category:
            self.category_spinner.text = self.selected_category

    # Bagian ini menjelaskan fungsi apply category dan tugasnya dalam aplikasi.
    def apply_category(self, spinner, category):
        self.selected_category = category or "Semua kategori"
        self.render()

    # Bagian ini menjelaskan fungsi locate dan tugasnya dalam aplikasi.
    def locate(self):
        App.get_running_app().go("nearby", "left")

    # Bagian ini menjelaskan fungsi toggle gps dan tugasnya dalam aplikasi.
    def toggle_gps(self):
        app = App.get_running_app()
        if app.gps_active:
            app.stop_gps()
        else:
            app.start_gps()

    # Bagian ini memperbarui tombol GPS sesuai status lokasi perangkat.
    def update_gps_button(self):
        app = App.get_running_app()
        self.gps_button.text = "MATIKAN GPS" if app.gps_active else "AKTIFKAN GPS"
        if app.gps_active and app.user_lat is not None:
            self.status.text = f"Lokasi: {app.user_lat:.5f}, {app.user_lon:.5f}"
        elif app.gps_active:
            self.status.text = "Mencari sinyal GPS..."
        elif self.name == "nearby":
            self.status.text = "Aktifkan GPS untuk melihat jarak dari posisi Anda."
        else:
            self.status.text = "GPS belum diaktifkan."

    # Bagian ini menjelaskan fungsi all outlets dan tugasnya dalam aplikasi.
    def all_outlets(self):
        self.only_favorites = False
        self.selected_category = "Semua kategori"
        self.category_spinner.text = self.selected_category
        self.render()

    # Bagian ini menjelaskan fungsi show favorites dan tugasnya dalam aplikasi.
    def show_favorites(self):
        self.only_favorites = True
        self.render()

    # Bagian ini menjelaskan fungsi distance dan tugasnya dalam aplikasi.
    @staticmethod
    def distance(lat1, lon1, lat2, lon2):
        dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
        return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # Bagian ini menjelaskan fungsi render dan tugasnya dalam aplikasi.
    def render(self):
        if not hasattr(self, "results"):
            return
        app = App.get_running_app()
        saved = app.favorite_keys()
        query = self.search.text.lower().strip()
        items = []
        with open(OUTLET_FILE, encoding="utf8") as file:
            for row in csv.DictReader(file):
                try:
                    name = row["Nama"].strip()
                    lat, lon = float(row["Latitude"]), float(row["Longitude"])
                except (KeyError, ValueError):
                    continue
                category = (row.get("Kategori") or "Umum").strip().title()
                key = (name, f"{lat:.6f}", f"{lon:.6f}")
                description = (row.get("Deskripsi") or "").strip()
                if query and not any(query in value.lower() for value in (name, category, description)):
                    continue
                if (self.selected_category.strip().casefold() != "semua kategori"
                        and category.strip().casefold() != self.selected_category.strip().casefold()):
                    continue
                if self.only_favorites and key not in saved:
                    continue
                distance = self.distance(self.user_lat, self.user_lon, lat, lon) if self.user_lat is not None else None
                items.append((distance, name, lat, lon, category, description, key in saved))
        if self.name == "nearby" and self.user_lat is not None:
            items.sort(key=lambda x: (x[0] is None, x[0] if x[0] is not None else x[1].lower()))
        else:
            items.sort(key=lambda x: x[1].lower())
        self.results.clear_widgets()
        if not items:
            empty = BoxLayout(orientation="vertical", padding=dp(18), size_hint_y=None, height=dp(130))
            rounded(empty, WHITE, 14, LINE)
            empty_title = (f"Belum ada outlet kategori {self.selected_category}"
                           if self.selected_category != "Semua kategori" else "Belum ada outlet")
            empty.add_widget(make_label(empty_title, 16, INK, True, 30, "center"))
            empty.add_widget(make_label("Pilih kategori lain atau ubah kata pencarian.", 11, SLATE, False, 40, "center"))
            self.results.add_widget(empty)
        else:
            for item in items:
                self.results.add_widget(OutletCard(*item, source_screen=self.name))
        prefix = "Favorit | " if self.only_favorites else ""
        category_summary = ("Semua kategori" if self.selected_category == "Semua kategori"
                            else f"Kategori: {self.selected_category}")
        self.result_summary.text = f"{category_summary}  ·  {len(items)} outlet"
        if self.name == "nearby" and self.user_lat is not None:
            self.status.text = f"{len(items)} outlet | diurutkan berdasarkan jarak GPS"
        elif self.name == "nearby":
            self.status.text = "Aktifkan GPS untuk melihat jarak dari posisi Anda."
        elif self.user_lat is not None:
            self.status.text = f"{prefix}{len(items)} outlet ditemukan | jarak dari GPS tersedia"
        else:
            self.status.text = f"{prefix}{len(items)} outlet ditemukan | aktifkan lokasi untuk jarak"


# Bagian ini menjelaskan kelas FavoritesScreen dan tugasnya dalam aplikasi.
class FavoritesScreen(MainScreen):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "favorites"
        self.bottom_nav.active = "fav"
        self.bottom_nav.update_items()

    # Bagian ini menjelaskan fungsi on pre enter dan tugasnya dalam aplikasi.
    def on_pre_enter(self, *_):
        self.only_favorites = True
        app = App.get_running_app()
        self.bottom_nav.update_items()
        self.greeting.text = "Outlet Favorit"
        self.render()


# Bagian ini menjelaskan kelas NearbyScreen dan tugasnya dalam aplikasi.
class NearbyScreen(MainScreen):
    """Layar untuk menampilkan outlet yang diurutkan berdasarkan posisi GPS perangkat."""
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "nearby"
        self.bottom_nav.active = "home"
        self.bottom_nav.update_items()

    # Bagian ini menjelaskan fungsi on pre enter dan tugasnya dalam aplikasi.
    def on_pre_enter(self, *_):
        app = App.get_running_app()
        self.bottom_nav.active = "home"
        self.bottom_nav.update_items()
        self.user_lat, self.user_lon = app.user_lat, app.user_lon
        self.only_favorites = False
        self.greeting.text = "Outlet Terdekat"
        self.load_categories()
        self.render()
        self.update_gps_button()


# Bagian ini menjelaskan kelas OutletCard dan tugasnya dalam aplikasi.
class OutletCard(BoxLayout):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, distance, name, lat, lon, category, description, saved,
                 source_screen="main", **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(5),
                         size_hint_y=None, height=dp(190) if App.get_running_app().is_admin else dp(154), **kwargs)
        rounded(self, WHITE, 14, LINE)
        self.name, self.lat, self.lon, self.saved = name, lat, lon, saved
        self.category, self.description = category, description
        self.source_screen = source_screen

        top = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        thumb = BoxLayout(size_hint_x=None, width=dp(54), padding=dp(4))
        rounded(thumb, SOFT_BLUE, 10)
        initials = "".join(part[0] for part in name.split()[:2]).upper() or "OF"
        thumb.add_widget(make_label(initials, 16, BLUE, True, 34, "center"))
        top.add_widget(thumb)

        text = BoxLayout(orientation="vertical")
        text.add_widget(make_label(name, 14, INK, True, 22))
        dist = f"{distance:.1f} km" if distance is not None else "Jarak belum aktif"
        text.add_widget(make_label(f"{category} | {dist}", 10, SLATE, False, 18))
        top.add_widget(text)
        save = action_button("SIMPAN" if not saved else "TERSIMPAN", self.toggle,
                             SOFT_BLUE if saved else WHITE, BLUE if saved else SLATE, 32)
        save.size_hint_x = None
        save.width = dp(84)
        top.add_widget(save)
        self.add_widget(top)

        self.add_widget(make_label(description or "Belum ada deskripsi outlet.", 10, SLATE, False, 30))

        actions = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(5))
        actions.add_widget(action_button("Detail", self.details, SOFT_BLUE, BLUE, 32, 8))
        actions.add_widget(action_button("Salin", self.copy_location, PALE, INK, 32, 8))
        actions.add_widget(action_button("RUTE", self.directions, BLUE, WHITE, 32, 8))
        self.add_widget(actions)
        if App.get_running_app().is_admin:
            self.add_widget(action_button("HAPUS OUTLET", self.confirm_delete, SOFT_RED, ERROR, 32, 8))

    # Bagian ini menjelaskan fungsi toggle dan tugasnya dalam aplikasi.
    def toggle(self):
        app = App.get_running_app()
        if app.current_user == "Tamu":
            app.popup("Masuk untuk menyimpan", "Favorit tersimpan di akun Anda. Masuk atau buat akun untuk menggunakan fitur ini.")
            return
        rows = app.favorites()
        key = (app.current_user, self.name, f"{self.lat:.6f}", f"{self.lon:.6f}")
        existing = {(r["Username"], r["Nama"], r["Latitude"], r["Longitude"]) for r in rows}
        if key in existing:
            rows = [r for r in rows if (r["Username"], r["Nama"], r["Latitude"], r["Longitude"]) != key]
            msg = "Outlet dihapus dari favorit."
        else:
            rows.append(dict(zip(["Username", "Nama", "Latitude", "Longitude"], key)))
            msg = "Outlet ditambahkan ke favorit."
        app.write_favorites(rows)
        app.root.get_screen("main").render()
        if "favorites" in app.root.screen_names:
            app.root.get_screen("favorites").render()
        app.toast(msg)

    # Bagian ini menjelaskan fungsi directions dan tugasnya dalam aplikasi.
    def directions(self):
        webbrowser.open(f"https://www.google.com/maps/dir/?api=1&destination={self.lat},{self.lon}")

    # Bagian ini menjelaskan fungsi copy location dan tugasnya dalam aplikasi.
    def copy_location(self):
        Clipboard.copy(f"{self.lat:.6f}, {self.lon:.6f}")
        App.get_running_app().toast("Koordinat berhasil disalin.")

    # Bagian ini menjelaskan fungsi details dan tugasnya dalam aplikasi.
    def details(self):
        app = App.get_running_app()
        detail = app.root.get_screen("detail")
        detail.set_outlet(self, self.source_screen)
        app.go("detail")

    # Bagian ini menjelaskan fungsi edit dan tugasnya dalam aplikasi.
    def edit(self):
        edit = App.get_running_app().root.get_screen("edit")
        edit.original = (self.name, self.lat, self.lon)
        edit.outlet_name.text = self.name
        edit.category.text = self.category
        edit.description.text = self.description
        App.get_running_app().go("edit")

    # Bagian ini menjelaskan fungsi confirm delete dan tugasnya dalam aplikasi.
    def confirm_delete(self):
        App.get_running_app().confirm(
            "Hapus Outlet",
            f'Yakin ingin menghapus "{self.name}"?',
            self.delete
        )

    # Bagian ini menjelaskan fungsi delete dan tugasnya dalam aplikasi.
    def delete(self):
        app = App.get_running_app()
        rows = []
        with open(OUTLET_FILE, encoding="utf8") as file:
            for row in csv.DictReader(file):
                same = (row.get("Nama", "").strip() == self.name and
                        abs(float(row["Latitude"]) - self.lat) < .00001 and
                        abs(float(row["Longitude"]) - self.lon) < .00001)
                if not same:
                    rows.append(row)
        with open(OUTLET_FILE, "w", newline="", encoding="utf8") as file:
            writer = csv.DictWriter(file, fieldnames=["Nama", "Latitude", "Longitude", "Kategori", "Deskripsi"])
            writer.writeheader()
            writer.writerows(rows)

        favorites = [
            row for row in app.favorites()
            if not (row.get("Nama", "").strip() == self.name and
                    abs(float(row["Latitude"]) - self.lat) < .00001 and
                    abs(float(row["Longitude"]) - self.lon) < .00001)
        ]
        app.write_favorites(favorites)
        app.root.get_screen("admin").render()
        app.root.get_screen("main").render()
        app.root.get_screen("favorites").render()
        app.toast("Outlet berhasil dihapus.")


# Bagian ini menjelaskan kelas DetailScreen dan tugasnya dalam aplikasi.
class DetailScreen(BaseScreen):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(name="detail", **kwargs)
        self.data = None
        self.return_screen = "main"
        self.rootbox = self.page(14, 8)
        self.title_bar(self.rootbox, "Detail Outlet", self.go_back, "OutletLocator")
        self.content = BoxLayout(orientation="vertical", spacing=dp(8))
        self.rootbox.add_widget(self.content)

    # Bagian ini menjelaskan fungsi go back dan tugasnya dalam aplikasi.
    def go_back(self):
        App.get_running_app().go(self.return_screen, "right")

    # Bagian ini menjelaskan fungsi set outlet dan tugasnya dalam aplikasi.
    def set_outlet(self, card, source_screen="main"):
        self.data = card
        self.return_screen = source_screen
        self.content.clear_widgets()
        hero = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(4),
                         size_hint_y=None, height=dp(155))
        rounded(hero, SOFT_BLUE, 16)
        hero.add_widget(make_label("OUTLET", 34, BLUE, True, 46, "center"))
        hero.add_widget(make_label(card.name, 20, INK, True, 32, "center"))
        hero.add_widget(make_label(card.category.upper(), 10, BLUE, True, 22, "center"))
        self.content.add_widget(hero)

        info = BoxLayout(orientation="vertical", padding=dp(13), spacing=dp(3),
                         size_hint_y=None, height=dp(170))
        rounded(info, WHITE, 14, LINE)
        info.add_widget(make_label("INFORMASI OUTLET", 10, BLUE, True, 22))
        info.add_widget(make_label(card.description or "Belum ada deskripsi.", 11, SLATE, False, 40))
        info.add_widget(make_label(f"Koordinat: {card.lat:.6f}, {card.lon:.6f}", 11, INK, True, 28))
        info.add_widget(make_label("Status: informasi tersedia", 10, SUCCESS, True, 22))
        self.content.add_widget(info)

        actions = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        actions.add_widget(action_button("Salin Koordinat", card.copy_location, SOFT_BLUE, BLUE, 44))
        actions.add_widget(action_button("Buka Rute", card.directions, BLUE, WHITE, 44))
        self.content.add_widget(actions)
        self.content.add_widget(Label())


# Bagian ini menjelaskan kelas ProfileScreen dan tugasnya dalam aplikasi.
class ProfileScreen(BaseScreen):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(name="profile", **kwargs)
        self.rootbox = self.page(14, 8)
        self.title_bar(self.rootbox, "Profil Akun", lambda: App.get_running_app().go("main", "right"), "")
        self.card = BoxLayout(orientation="horizontal", padding=dp(14), spacing=dp(12),
                              size_hint_y=None, height=dp(104))
        rounded(self.card, WHITE, 15, LINE)
        self.avatar = BoxLayout(size_hint_x=None, width=dp(58), padding=dp(4))
        rounded(self.avatar, SOFT_BLUE, 12)
        self.avatar_initials = make_label("", 18, BLUE, True, 50, "center")
        self.avatar.add_widget(self.avatar_initials)
        self.card.add_widget(self.avatar)
        details = BoxLayout(orientation="vertical", spacing=dp(2))
        self.name_label = make_label("", 17, INK, True, 28)
        self.role_label = make_label("", 11, SLATE, False, 22)
        details.add_widget(self.name_label)
        details.add_widget(self.role_label)
        self.card.add_widget(details)
        self.rootbox.add_widget(self.card)
        self.stats = make_label("", 10, SLATE, False, 25)
        self.rootbox.add_widget(self.stats)

        self.rootbox.add_widget(self.section("AKUN SAYA"))
        self.rootbox.add_widget(action_button("Lihat outlet favorit", self.favorites, WHITE, INK, 44))
        self.rootbox.add_widget(action_button("Bantuan penggunaan", self.help, WHITE, INK, 44))
        self.add_btn = action_button("TAMBAH OUTLET BARU", lambda: App.get_running_app().go("add"), SOFT_BLUE, BLUE, 44)
        self.admin_section = self.section("ADMINISTRASI")
        self.rootbox.add_widget(self.admin_section)
        self.rootbox.add_widget(self.add_btn)
        self.rootbox.add_widget(Label())
        self.session_btn = action_button("Keluar dari akun", self.logout, SOFT_RED, ERROR, 44)
        self.rootbox.add_widget(self.session_btn)
        self.bottom_nav = BottomNav("profile")
        self.rootbox.add_widget(self.bottom_nav)

    # Bagian ini menjelaskan fungsi section dan tugasnya dalam aplikasi.
    def section(self, text):
        return make_label(text, 10, SLATE, True, 22)

    # Bagian ini menjelaskan fungsi on pre enter dan tugasnya dalam aplikasi.
    def on_pre_enter(self, *_):
        app = App.get_running_app()
        self.bottom_nav.update_items()
        is_guest = app.current_user == "Tamu"
        role = "Administrator" if app.is_admin else ("Tamu" if is_guest else "Pengguna")
        display_name = app.current_user if app.current_user else "Pengguna"
        self.name_label.text = display_name
        self.role_label.text = f"{role} · OutletFinder"
        self.avatar_initials.text = "".join(part[0] for part in display_name.split()[:2]).upper()
        count = len(app.favorite_keys())
        self.stats.text = f"{count} outlet tersimpan di favorit"
        self.add_btn.disabled = False
        self.add_btn.opacity = 1 if app.is_admin else 0
        self.add_btn.height = dp(44) if app.is_admin else 0
        self.admin_section.opacity = 1 if app.is_admin else 0
        self.admin_section.height = dp(22) if app.is_admin else 0
        self.session_btn.text = "Masuk ke akun" if is_guest else "Keluar dari akun"

    # Bagian ini menjelaskan fungsi favorites dan tugasnya dalam aplikasi.
    def favorites(self):
        app = App.get_running_app()
        app.root.get_screen("favorites").on_pre_enter()
        app.go("favorites", "left")

    # Bagian ini menjelaskan fungsi help dan tugasnya dalam aplikasi.
    def help(self):
        App.get_running_app().popup(
            "Bantuan penggunaan",
            "Cari outlet berdasarkan nama, kategori, atau deskripsi.\n"
            "Aktifkan GPS untuk mengurutkan outlet berdasarkan jarak perangkat.\n"
            "Masuk ke akun untuk menyimpan outlet favorit."
        )

    # Bagian ini menjelaskan fungsi logout dan tugasnya dalam aplikasi.
    def logout(self):
        app = App.get_running_app()
        if app.current_user == "Tamu":
            app.target_role = "user"
            app.go("login", "right")
            return
        app.logged_in = app.is_admin = False
        app.current_user = ""
        app.go("welcome", "right")


# Bagian ini menjelaskan kelas AddScreen dan tugasnya dalam aplikasi.
class AddScreen(BaseScreen):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(name="add", **kwargs)
        root = self.page(16, 8)
        self.title_bar(root, "Tambah Outlet", lambda: App.get_running_app().go("main", "right"))
        self.form(root)

    # Bagian ini menjelaskan fungsi form dan tugasnya dalam aplikasi.
    def form(self, root):
        self.heading(root, "Informasi Dasar Outlet", "Isi data agar outlet mudah ditemukan.")
        root.add_widget(make_label("NAMA OUTLET", 10, SLATE, True, 19))
        self.outlet_name = field("Contoh: Outlet Pusat")
        root.add_widget(self.outlet_name)
        root.add_widget(make_label("KATEGORI", 10, SLATE, True, 19))
        self.category = field("Contoh: Kuliner / Retail")
        root.add_widget(self.category)
        root.add_widget(make_label("LATITUDE, LONGITUDE", 10, SLATE, True, 19))
        self.location = field("-7.8200, 112.0120")
        root.add_widget(self.location)
        root.add_widget(make_label("DESKRIPSI", 10, SLATE, True, 19))
        self.description = field("Deskripsi singkat outlet")
        root.add_widget(self.description)
        self.message = make_label("", 10, ERROR, True, 25)
        root.add_widget(self.message)
        root.add_widget(action_button("SIMPAN OUTLET", self.save, BLUE, WHITE, 48))
        root.add_widget(Label())

    # Bagian ini menjelaskan fungsi save dan tugasnya dalam aplikasi.
    def save(self):
        try:
            lat, lon = [float(v.strip()) for v in self.location.text.split(",")]
        except ValueError:
            self.message.text = "Format lokasi harus: latitude, longitude."
            return
        if not self.outlet_name.text.strip():
            self.message.text = "Nama outlet wajib diisi."
            return
        with open(OUTLET_FILE, "a", newline="", encoding="utf8") as file:
            csv.writer(file).writerow([
                self.outlet_name.text.strip(), lat, lon,
                self.category.text.strip().title() or "Umum", self.description.text.strip()
            ])
        App.get_running_app().popup("Outlet berhasil ditambahkan", "Data siap dicari di halaman utama.")
        App.get_running_app().go("main", "right")


# Bagian ini menjelaskan kelas EditScreen dan tugasnya dalam aplikasi.
class EditScreen(AddScreen):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "edit"
        self.original = None

    # Bagian ini menjelaskan fungsi form dan tugasnya dalam aplikasi.
    def form(self, root):
        self.heading(root, "Edit Informasi Outlet", "Perbarui informasi outlet.")
        root.add_widget(make_label("NAMA OUTLET", 10, SLATE, True, 19))
        self.outlet_name = field("Nama outlet")
        root.add_widget(self.outlet_name)
        root.add_widget(make_label("KATEGORI", 10, SLATE, True, 19))
        self.category = field("Kategori")
        root.add_widget(self.category)
        root.add_widget(make_label("DESKRIPSI", 10, SLATE, True, 19))
        self.description = field("Deskripsi")
        root.add_widget(self.description)
        self.message = make_label("", 10, ERROR, True, 25)
        root.add_widget(self.message)
        root.add_widget(action_button("SIMPAN PERUBAHAN", self.save_edit, BLUE, WHITE, 48))
        root.add_widget(Label())

    # Bagian ini menjelaskan fungsi save edit dan tugasnya dalam aplikasi.
    def save_edit(self):
        if not self.original or not self.outlet_name.text.strip():
            self.message.text = "Nama outlet wajib diisi."
            return
        rows = []
        with open(OUTLET_FILE, encoding="utf8") as file:
            for row in csv.DictReader(file):
                same = (row["Nama"] == self.original[0] and
                        abs(float(row["Latitude"]) - self.original[1]) < .00001 and
                        abs(float(row["Longitude"]) - self.original[2]) < .00001)
                if same:
                    row["Nama"] = self.outlet_name.text.strip()
                    row["Kategori"] = self.category.text.strip().title() or "Umum"
                    row["Deskripsi"] = self.description.text.strip()
                rows.append(row)
        with open(OUTLET_FILE, "w", newline="", encoding="utf8") as file:
            writer = csv.DictWriter(file, fieldnames=["Nama", "Latitude", "Longitude", "Kategori", "Deskripsi"])
            writer.writeheader()
            writer.writerows(rows)
        App.get_running_app().popup("Perubahan tersimpan", "Informasi outlet berhasil diperbarui.")
        App.get_running_app().go("main", "right")


# Bagian ini menjelaskan kelas AdminScreen dan tugasnya dalam aplikasi.
class AdminScreen(MainScreen):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "admin"
        self.bottom_nav.active = "admin"
        self.bottom_nav.update_items()

    # Bagian ini menjelaskan fungsi on pre enter dan tugasnya dalam aplikasi.
    def on_pre_enter(self, *_):
        self.only_favorites = False
        app = App.get_running_app()
        self.bottom_nav.update_items()
        self.greeting.text = "Panel Manajemen"
        self.render()


# Bagian ini menjelaskan kelas OutletLocatorApp dan tugasnya dalam aplikasi.
class OutletLocatorApp(App):
    current_user = StringProperty("")

    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gps_active = False
        self.user_lat = None
        self.user_lon = None
        self._gps_provider = None
        self._gps_configured = False

    # Bagian ini menjelaskan fungsi build dan tugasnya dalam aplikasi.
    def build(self):
        initialize_data()
        self.logged_in = False
        self.is_admin = False
        self.target_role = "user"

        manager = ScreenManager()
        screens = [
            WelcomeScreen(), RoleScreen(), LoginScreen(), RegisterScreen(),
            MainScreen(), NearbyScreen(), FavoritesScreen(), DetailScreen(), ProfileScreen(),
            AddScreen(), EditScreen(), AdminScreen()
        ]
        for screen in screens:
            manager.add_widget(screen)
        return manager

    # Bagian ini menjelaskan fungsi go dan tugasnya dalam aplikasi.
    def go(self, screen, direction="left"):
        self.root.transition = SlideTransition(direction=direction, duration=.18)
        self.root.current = screen

    # Bagian ini menjelaskan fungsi start gps dan tugasnya dalam aplikasi.
    def start_gps(self):
        if platform != "android":
            self.popup(
                "GPS perangkat tidak tersedia",
                "GPS langsung memerlukan aplikasi Android dan izin lokasi. Jalankan APK di perangkat untuk menggunakan GPS.",
            )
            return
        try:
            android_permissions = import_module("android.permissions")
            android_permissions.request_permissions(
                [android_permissions.Permission.ACCESS_COARSE_LOCATION,
                 android_permissions.Permission.ACCESS_FINE_LOCATION],
                self._on_location_permission,
            )
        except ImportError:
            self.popup("Izin lokasi tidak tersedia", "Jalankan aplikasi ini sebagai aplikasi Android.")
        except Exception as exc:
            self.popup("Tidak dapat meminta izin", str(exc))

    # Bagian ini menjelaskan fungsi  on location permission dan tugasnya dalam aplikasi.
    def _on_location_permission(self, permissions, grants):
        if not grants or not all(grants):
            self.popup("Izin lokasi ditolak", "Izinkan akses lokasi agar aplikasi dapat membaca GPS perangkat.")
            return
        self._start_gps_provider()

    # Bagian ini menjelaskan fungsi  start gps provider dan tugasnya dalam aplikasi.
    def _start_gps_provider(self):
        try:
            gps = import_module("plyer").gps
            self._gps_provider = gps
            if not self._gps_configured:
                gps.configure(on_location=self._on_gps_location, on_status=self._on_gps_status)
                self._gps_configured = True
            gps.start(1000, 0)
            self.gps_active = True
            self._refresh_location_screens()
        except Exception as exc:
            self.gps_active = False
            self.popup("GPS tidak dapat diaktifkan", f"Periksa dukungan GPS dan paket Plyer.\n{exc}")

    # Bagian ini menjelaskan fungsi stop gps dan tugasnya dalam aplikasi.
    def stop_gps(self):
        if self._gps_provider is not None:
            try:
                self._gps_provider.stop()
            except Exception:
                pass
        self.gps_active = False
        self.user_lat = self.user_lon = None
        self._refresh_location_screens()

    # Bagian ini menjelaskan fungsi  on gps location dan tugasnya dalam aplikasi.
    @mainthread
    def _on_gps_location(self, **location):
        try:
            self.user_lat = float(location["lat"])
            self.user_lon = float(location["lon"])
        except (KeyError, TypeError, ValueError):
            return
        self.gps_active = True
        self._refresh_location_screens()

    # Bagian ini menjelaskan fungsi  on gps status dan tugasnya dalam aplikasi.
    @mainthread
    def _on_gps_status(self, status_type, status):
        if status_type == "provider-disabled":
            self.gps_active = False
            self.user_lat = self.user_lon = None
            self._refresh_location_screens()

    # Bagian ini menjelaskan fungsi  refresh location screens dan tugasnya dalam aplikasi.
    def _refresh_location_screens(self):
        if not self.root:
            return
        for screen_name in ("main", "nearby"):
            screen = self.root.get_screen(screen_name)
            screen.user_lat, screen.user_lon = self.user_lat, self.user_lon
            screen.render()
            screen.update_gps_button()

    # Bagian ini menjelaskan fungsi on pause dan tugasnya dalam aplikasi.
    def on_pause(self):
        if self.gps_active and self._gps_provider is not None:
            self._gps_provider.stop()
        return True

    # Bagian ini menjelaskan fungsi on resume dan tugasnya dalam aplikasi.
    def on_resume(self):
        if self.gps_active:
            self._start_gps_provider()

    # Bagian ini menjelaskan fungsi favorites dan tugasnya dalam aplikasi.
    def favorites(self):
        with open(FAVORITE_FILE, encoding="utf8") as file:
            return list(csv.DictReader(file))

    # Bagian ini menjelaskan fungsi write favorites dan tugasnya dalam aplikasi.
    def write_favorites(self, rows):
        with open(FAVORITE_FILE, "w", newline="", encoding="utf8") as file:
            writer = csv.DictWriter(file, fieldnames=["Username", "Nama", "Latitude", "Longitude"])
            writer.writeheader()
            writer.writerows(rows)

    # Bagian ini menjelaskan fungsi favorite keys dan tugasnya dalam aplikasi.
    def favorite_keys(self):
        if self.current_user == "Tamu":
            return set()
        return {(r["Nama"], r["Latitude"], r["Longitude"])
                for r in self.favorites() if r["Username"] == self.current_user}

    # Bagian ini menjelaskan fungsi popup dan tugasnya dalam aplikasi.
    def popup(self, title, message):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        content.add_widget(make_label(message, 12, WHITE, False, 70, "center"))
        popup = Popup(title=title, content=content, size_hint=(.86, None), height=dp(200), auto_dismiss=False)
        content.add_widget(action_button("OK", popup.dismiss, BLUE, WHITE, 42))
        popup.open()

    # Bagian ini menjelaskan fungsi confirm dan tugasnya dalam aplikasi.
    def confirm(self, title, message, callback):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        content.add_widget(make_label(message, 12, INK, False, 70, "center"))
        popup = Popup(title=title, content=content, size_hint=(.86, None), height=dp(200), auto_dismiss=False)
        buttons = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        buttons.add_widget(action_button("BATAL", popup.dismiss, PALE, INK, 42))

        # Bagian ini menjelaskan fungsi accept dan tugasnya dalam aplikasi.
        def accept():
            popup.dismiss()
            callback()

        buttons.add_widget(action_button("HAPUS", accept, ERROR, WHITE, 42))
        content.add_widget(buttons)
        popup.open()

    # Bagian ini menjelaskan fungsi toast dan tugasnya dalam aplikasi.
    def toast(self, message):
        content = BoxLayout(padding=dp(10))
        rounded(content, NAVY, 12)
        content.add_widget(make_label(message, 11, WHITE, True, 38, "center"))
        popup = Popup(content=content, size_hint=(.82, None), height=dp(70), auto_dismiss=True,
                      separator_height=0, background_color=(0, 0, 0, 0))
        popup.open()


if __name__ == "__main__":
    OutletLocatorApp().run()
