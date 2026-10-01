from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.metrics import dp

# Mengatur ukuran layar menyerupai ponsel untuk pengujian.
Window.size = (360, 640)
# Menggunakan latar abu-abu muda agar kartu putih terlihat menonjol.
Window.clearcolor = (0.95, 0.96, 0.98, 1)

# Bagian ini mendefinisikan susunan widget antarmuka menggunakan bahasa Kivy.
KV = '''
#:import hex kivy.utils.get_color_from_hex

<OutletCard@BoxLayout>:
    orientation: 'horizontal'
    padding: dp(10)
    spacing: dp(15)
    size_hint_y: None
    height: dp(110)
    
    # Latar belakang kartu.
    canvas.before:
        # Efek bayangan sederhana.
        Color:
            rgba: (0.85, 0.85, 0.85, 0.7)
        RoundedRectangle:
            size: (self.width, self.height - dp(2))
            pos: (self.x, self.y - dp(2))
            radius: [dp(12)]
            
        # Warna utama kartu (putih bersih).
        Color:
            rgba: (1, 1, 1, 1)
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [dp(12)]

    # Gambar outlet dari arsip ZIP.
    BoxLayout:
        size_hint_x: None
        width: dp(90)
        canvas.before:
            Color:
                rgba: (1, 1, 1, 1)
            # Membulatkan sudut gambar (opsional).
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: [dp(8)]
                source: root.image_source

    # Informasi Outlet
    BoxLayout:
        orientation: 'vertical'
        padding: [0, dp(2), 0, dp(2)]
        
        Label:
            text: root.outlet_name
            color: hex('#1E272E') # Hitam kebiruan yang elegan
            font_size: dp(15)
            bold: True
            text_size: self.size
            halign: 'left'
            valign: 'top'
            
        Label:
            text: root.outlet_address
            color: hex('#808E9B') # Abu-abu yang nyaman dibaca
            font_size: dp(12)
            text_size: self.size
            halign: 'left'
            valign: 'middle'

        # Status Buka/Tutup
        BoxLayout:
            size_hint_y: None
            height: dp(20)
            Label:
                text: root.outlet_status
                color: hex('#05C46B') if root.is_open else hex('#FF3F34')
                font_size: dp(12)
                bold: True
                text_size: self.size
                halign: 'left'
                valign: 'bottom'

<MainUI>:
    orientation: 'vertical'
    spacing: dp(15)
    padding: dp(15)

    # Bilah judul bagian atas.
    BoxLayout:
        size_hint_y: None
        height: dp(40)
        Label:
            text: "Temukan Outlet"
            color: hex('#1E272E')
            font_size: dp(22)
            bold: True
            text_size: self.size
            halign: 'left'
            valign: 'middle'

    # Bilah pencarian modern.
    BoxLayout:
        size_hint_y: None
        height: dp(48)
        canvas.before:
            Color:
                rgba: (1, 1, 1, 1) # Latar putih
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: [dp(24)] # Sangat membulat (Pill shape)
            # Border halus
            Color:
                rgba: hex('#D2DAE2')
            Line:
                rounded_rectangle: (self.x, self.y, self.width, self.height, dp(24))
                width: 1.2
                
        TextInput:
            hint_text: "Cari lokasi atau nama outlet..."
            background_color: (0,0,0,0)
            foreground_color: hex('#1E272E')
            cursor_color: hex('#0FB9B1')
            padding: [dp(20), dp(14)]
            multiline: False
            font_size: dp(14)

    # Area gulir untuk daftar outlet.
    ScrollView:
        do_scroll_x: False
        do_scroll_y: True
        bar_width: dp(4) # Scrollbar tipis ala iOS/Android modern
        
        GridLayout:
            id: outlet_container
            cols: 1
            spacing: dp(15)
            size_hint_y: None
            height: self.minimum_height
            padding: [0, dp(5), 0, dp(20)]
'''

# Bagian ini menjelaskan kelas MainUI dan tugasnya dalam aplikasi.
class MainUI(BoxLayout):
    # Bagian ini menjelaskan fungsi   init   dan tugasnya dalam aplikasi.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.populate_outlets()

    # Bagian ini menjelaskan fungsi populate outlets dan tugasnya dalam aplikasi.
    def populate_outlets(self):
        # Menggunakan sembilan gambar dari arsip ZIP (1.png sampai 9.png).
        # Sesuai dengan isi folder "New folder (2)".
        outlets_data = [
            {"name": "Outlet Pusat Kediri", "address": "Jl. Hayam Wuruk No. 12", "is_open": True, "status": "Buka - 0.8 km", "img": "New folder (2)/1.png"},
            {"name": "Outlet Cabang Pare", "address": "Jl. PB Sudirman", "is_open": False, "status": "Tutup - 5.2 km", "img": "New folder (2)/2.png"},
            {"name": "Outlet Kampung Inggris", "address": "Jl. Brawijaya", "is_open": True, "status": "Buka - 6.0 km", "img": "New folder (2)/3.png"},
            {"name": "Outlet Simpang Lima", "address": "Kawasan SLG", "is_open": True, "status": "Buka - 7.5 km", "img": "New folder (2)/4.png"},
            {"name": "Outlet Mojoroto", "address": "Jl. Veteran No. 45", "is_open": True, "status": "Buka - 2.1 km", "img": "New folder (2)/5.png"},
            {"name": "Outlet Pesantren", "address": "Jl. Letjend Suprapto", "is_open": False, "status": "Tutup - 3.4 km", "img": "New folder (2)/6.png"},
            {"name": "Outlet Ngasem", "address": "Jl. Pamenang", "is_open": True, "status": "Buka - 4.8 km", "img": "New folder (2)/7.png"},
            {"name": "Outlet Bandar", "address": "Jl. KH Wachid Hasyim", "is_open": True, "status": "Buka - 1.5 km", "img": "New folder (2)/8.png"},
            {"name": "Outlet Grogol", "address": "Jl. Raya Grogol", "is_open": True, "status": "Buka - 9.0 km", "img": "New folder (2)/9.png"},
        ]

        container = self.ids.outlet_container
        
        for data in outlets_data:
            # Memasukkan data 1 per 1 ke dalam template Kivy
            card = Builder.template('OutletCard', 
                                    outlet_name=data['name'], 
                                    outlet_address=data['address'],
                                    outlet_status=data['status'],
                                    is_open=data['is_open'],
                                    image_source=data['img']) # Memetakan gambar 1.png - 9.png
            container.add_widget(card)

# Bagian ini menjelaskan kelas OutletFinderApp dan tugasnya dalam aplikasi.
class OutletFinderApp(App):
    # Bagian ini menjelaskan fungsi build dan tugasnya dalam aplikasi.
    def build(self):
        Builder.load_string(KV)
        return MainUI()

if __name__ == '__main__':
    OutletFinderApp().run()