import os
import tkinter as tk
from tkinter import Listbox, Scrollbar
import cv2
from PIL import Image, ImageTk
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
import serial
import time
from datetime import datetime

from backend import urun_ekle, urun_sil, liste_urunler, urun_bul

# ----------------- Arduino -----------------
SERI_PORT = "COM5"
BAUDRATE = 9600


class MarketGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Market Kasiyer Sistemi")
        self.root.geometry("1980x1080")
        self.root.configure(bg="#1e1e1e")

        self.sepet = {}
        self.toplam = 0
        self.qr_last = {}
        self.debounce = 3

        self.cap = None
        self.seri = None

        self.ok_color = "#00ff00"
        self.bad_color = "#ff3333"
        self.default_border = "#2b2b2b"

        # ---------------- BAŞLIK ----------------
        tk.Label(
            root, text="Market Kasiyer Sistemi",
            font=("Arial", 22, "bold"),
            fg="white", bg="#1e1e1e"
        ).pack(pady=6)

        self.lbl_arduino = tk.Label(
            root, text="Arduino kontrol ediliyor...",
            fg="gray", bg="#1e1e1e"
        )
        self.lbl_arduino.pack()

        main = tk.Frame(root, bg="#1e1e1e")
        main.pack(fill="both", expand=True, padx=8, pady=8)

        # =====================================================
        # SOL PANEL – ÜRÜN KONTROL
        # =====================================================
        panel = tk.Frame(main, bg="#222222", width=220)
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)

        tk.Label(panel, text="Ürün Kontrol",
                 fg="white", bg="#222222",
                 font=("Arial", 14, "bold")).pack(pady=8)

        tk.Label(panel, text="Kod", fg="white", bg="#222222").pack(anchor="w", padx=10)
        self.e_kod = tk.Entry(panel)
        self.e_kod.pack(fill="x", padx=10)

        tk.Label(panel, text="Ürün", fg="white", bg="#222222").pack(anchor="w", padx=10, pady=(6, 0))
        self.e_urun = tk.Entry(panel)
        self.e_urun.pack(fill="x", padx=10)

        tk.Label(panel, text="Fiyat", fg="white", bg="#222222").pack(anchor="w", padx=10, pady=(6, 0))
        self.e_fiyat = tk.Entry(panel)
        self.e_fiyat.pack(fill="x", padx=10)

        tk.Button(
            panel, text="ÜRÜN EKLE",
            command=self.panel_urun_ekle,
            bg="#3a86ff", fg="white", height=2
        ).pack(fill="x", padx=10, pady=8)

        tk.Label(panel, text="Ürün Listesi",
                 fg="white", bg="#222222",
                 font=("Arial", 12, "bold")).pack(pady=(6, 4))

        list_frame = tk.Frame(panel, bg="#222222")
        list_frame.pack(fill="both", expand=True, padx=8)

        self.urun_list = Listbox(list_frame)
        sb = Scrollbar(list_frame, orient="vertical", command=self.urun_list.yview)
        self.urun_list.config(yscrollcommand=sb.set)

        self.urun_list.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        tk.Button(
            panel, text="SEÇİLİ ÜRÜNÜ SİL",
            command=self.panel_urun_sil,
            bg="#aa3333", fg="white", height=2
        ).pack(fill="x", padx=10, pady=6)

        self.panel_info = tk.Label(
            panel, text="Hazır.",
            fg=self.ok_color, bg="#222222",
            wraplength=200, anchor="w"
        )
        self.panel_info.pack(fill="x", padx=10, pady=6)

        # =====================================================
        # ORTA – KAMERA
        # =====================================================
        cam = tk.Frame(main, bg="#1e1e1e")
        cam.pack(side="left", fill="both", expand=True)

        self.cam_frame = tk.Frame(
            cam, bg="#2b2b2b",
            highlightthickness=6,
            highlightbackground=self.default_border
        )
        self.cam_frame.pack(expand=True, pady=6)

        self.video_label = tk.Label(self.cam_frame, bg="#2b2b2b")
        self.video_label.pack(expand=True)

        self.status_label = tk.Label(
            cam, text="QR bekleniyor...",
            fg="white", bg="#1e1e1e",
            font=("Arial", 14, "bold")
        )
        self.status_label.pack(pady=6)

        btns = tk.Frame(cam, bg="#1e1e1e")
        btns.pack()

        tk.Button(btns, text="QR Okumayı Başlat",
                  command=self.kamera_baslat,
                  bg="#3a86ff", fg="white",
                  width=18, height=2).pack(side="left", padx=5)

        tk.Button(btns, text="Kamerayı Durdur",
                  command=self.kamera_durdur,
                  bg="#444", fg="white",
                  width=18, height=2).pack(side="left", padx=5)

        # =====================================================
        # SAĞ – SEPET
        # =====================================================
        sepet = tk.Frame(main, bg="#222222", width=360)
        sepet.pack(side="right", fill="y")
        sepet.pack_propagate(False)

        tk.Label(sepet, text="Sepet",
                 fg="white", bg="#222222",
                 font=("Arial", 14, "bold")).pack(pady=10)

        self.sepet_list = Listbox(sepet)
        self.sepet_list.pack(fill="both", expand=True, padx=10)

        self.lbl_toplam = tk.Label(
            sepet, text="TOPLAM: 0 TL",
            fg=self.ok_color, bg="#222222",
            font=("Arial", 16, "bold")
        )
        self.lbl_toplam.pack(pady=10)

        tk.Button(
            sepet, text="ÖDEME AL",
            command=self.odeme_al,
            bg="#00aa00", fg="white", height=2
        ).pack(fill="x", padx=10)

        # ------------------
        self.arduino_baglan()
        self.listeyi_yukle()
        self.root.protocol("WM_DELETE_WINDOW", self.kapat)

    # =====================================================
    # PANEL MESAJ (otomatik silinir)
    # =====================================================
    def panel_mesaj(self, text, renk, sure=2500):
        self.panel_info.config(text=text, fg=renk)
        if hasattr(self, "_panel_after"):
            self.root.after_cancel(self._panel_after)
        self._panel_after = self.root.after(
            sure, lambda: self.panel_info.config(text="Hazır.", fg=self.ok_color)
        )

    # =====================================================
    # Arduino
    # =====================================================
    def arduino_baglan(self):
        try:
            self.seri = serial.Serial(SERI_PORT, BAUDRATE, timeout=1)
            time.sleep(2)
            self.lbl_arduino.config(text="Arduino bağlı", fg="#4caf50")
        except:
            self.seri = None
            self.lbl_arduino.config(text="Arduino yok", fg="red")

    # =====================================================
    # Kamera
    # =====================================================
    def kamera_baslat(self):
        if self.cap:
            return
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.qr_last.clear()
        self.kamera_loop()

    def kamera_durdur(self):
        if self.cap:
            self.cap.release()
        self.cap = None

    def kamera_loop(self):
        if not self.cap:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.root.after(20, self.kamera_loop)
            return

        for qr in pyzbar.decode(frame, symbols=[ZBarSymbol.QRCODE]):
            kod = qr.data.decode("utf-8")
            now = time.time()
            if kod in self.qr_last and now - self.qr_last[kod] < self.debounce:
                continue
            self.qr_last[kod] = now
            self.qr_isle(kod)

        img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        self.video_label.config(image=img)
        self.video_label.image = img

        self.root.after(20, self.kamera_loop)

    # =====================================================
    # QR
    # =====================================================
    def qr_isle(self, kod):
        ok, urun = urun_bul(kod)

        if not ok:
            self.cam_frame.config(highlightbackground=self.bad_color)
            self.status_label.config(text="✖ Kayıtsız ürün", fg=self.bad_color)
            if self.seri:
                self.seri.write(b"ERR\n")
            self.root.after(1200, self.reset_kamera)
            return

        self.cam_frame.config(highlightbackground=self.ok_color)

        if kod not in self.sepet:
            self.sepet[kod] = {"urun": urun["Urun"], "fiyat": urun["Fiyat"], "adet": 1}
        else:
            self.sepet[kod]["adet"] += 1

        self.sepet_guncelle()
        self.status_label.config(text=f"✔ {urun['Urun']} eklendi", fg=self.ok_color)

        if self.seri:
            self.seri.write(f"TOTAL;{self.toplam}\n".encode())

        self.root.after(1200, self.reset_kamera)

    def reset_kamera(self):
        self.cam_frame.config(highlightbackground=self.default_border)
        self.status_label.config(text="QR bekleniyor...", fg="white")

    # =====================================================
    # Sepet
    # =====================================================
    def sepet_guncelle(self):
        self.sepet_list.delete(0, tk.END)
        self.toplam = 0
        for i in self.sepet.values():
            ara = i["adet"] * i["fiyat"]
            self.toplam += ara
            self.sepet_list.insert(tk.END, f"{i['urun']} x{i['adet']} = {ara} TL")
        self.lbl_toplam.config(text=f"TOPLAM: {self.toplam} TL")

    # =====================================================
    # Panel işlemleri
    # =====================================================
    def listeyi_yukle(self):
        self.urun_list.delete(0, tk.END)
        for _, r in liste_urunler().iterrows():
            self.urun_list.insert(tk.END, f"{r['Kod']} - {r['Urun']}")

    def panel_urun_ekle(self):
        ok, msg = urun_ekle(self.e_kod.get(), self.e_urun.get(), self.e_fiyat.get())
        self.panel_mesaj(msg, self.ok_color if ok else self.bad_color)
        if ok:
            self.e_kod.delete(0, tk.END)
            self.e_urun.delete(0, tk.END)
            self.e_fiyat.delete(0, tk.END)
            self.listeyi_yukle()

    def panel_urun_sil(self):
        sec = self.urun_list.curselection()
        if not sec:
            self.panel_mesaj("Listeden ürün seç.", self.bad_color)
            return
        kod = self.urun_list.get(sec[0]).split(" - ")[0]
        ok, msg = urun_sil(kod)
        self.panel_mesaj(msg, self.ok_color if ok else self.bad_color)
        self.listeyi_yukle()

    # =====================================================
    # FİŞ + ÖDEME (LCD SENKRON)
    # =====================================================
    def fis_yaz(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fis_dir = os.path.join(base_dir, "fisler")
        os.makedirs(fis_dir, exist_ok=True)

        fname = f"fis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = os.path.join(fis_dir, fname)

        with open(path, "w", encoding="utf-8") as f:
            f.write("MARKET FİŞİ\n")
            f.write("------------------\n")
            for i in self.sepet.values():
                f.write(f"{i['urun']} x{i['adet']} = {i['adet']*i['fiyat']} TL\n")
            f.write("------------------\n")
            f.write(f"TOPLAM: {self.toplam} TL\n")
            f.write(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")

        return fname

    def odeme_al(self):
        if not self.sepet:
            return

        if self.seri:
            self.seri.write(b"PAYING\n")
        self.panel_mesaj("Ödeme alınıyor...", self.ok_color, 3000)
        time.sleep(3)

        fis = self.fis_yaz()

        if self.seri:
            self.seri.write(b"PAID\n")
            time.sleep(2)
            self.seri.write(b"RECEIPT\n")
            time.sleep(3)
            self.seri.write(b"TOTAL;0\n")

        self.sepet.clear()
        self.sepet_list.delete(0, tk.END)
        self.toplam = 0
        self.lbl_toplam.config(text="TOPLAM: 0 TL")

        self.panel_mesaj(f"Ödeme alındı. Fiş oluşturuldu: {fis}", self.ok_color, 4000)

    def kapat(self):
        if self.cap:
            self.cap.release()
        if self.seri:
            self.seri.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MarketGUI(root)
    root.mainloop()