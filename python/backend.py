import os
import pandas as pd
import qrcode

# -------------------------------
# Dosya / klasör ayarları
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # proje kökü
DATA_DIR = os.path.join(BASE_DIR, "data")
EXCEL_PATH = os.path.join(DATA_DIR, "urunler.xlsx")
QR_DIR = os.path.join(BASE_DIR, "qr_codes")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)

# -------------------------------
# Excel yoksa oluştur
# -------------------------------
def excel_kontrol():
    if not os.path.exists(EXCEL_PATH):
        df = pd.DataFrame(columns=["Kod", "Urun", "Fiyat"])
        df.to_excel(EXCEL_PATH, index=False)

def _load_df():
    excel_kontrol()
    return pd.read_excel(EXCEL_PATH)

def _save_df(df):
    df.to_excel(EXCEL_PATH, index=False)

excel_kontrol()

# -------------------------------
# Ürün listele
# -------------------------------
def liste_urunler():
    return _load_df()

# -------------------------------
# QR oluştur
# -------------------------------
def qr_olustur(kod):
    img = qrcode.make(str(kod))
    path = os.path.join(QR_DIR, f"{kod}.png")
    img.save(path)

# -------------------------------
# Ürün ekle
# -------------------------------
def urun_ekle(kod, urun, fiyat):
    kod = str(kod).strip()
    urun = str(urun).strip()

    if not kod or not urun:
        return False, "Kod ve ürün adı boş olamaz"

    try:
        fiyat = float(str(fiyat).replace(",", "."))
    except:
        return False, "Fiyat sayısal olmalı"

    df = _load_df()

    if kod in df["Kod"].astype(str).values:
        return False, "Bu ürün zaten kayıtlı"

    yeni = {"Kod": kod, "Urun": urun, "Fiyat": fiyat}
    df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
    _save_df(df)

    qr_olustur(kod)
    return True, "Ürün eklendi ve QR oluşturuldu"

# -------------------------------
# Ürün sil
# -------------------------------
def urun_sil(kod):
    kod = str(kod).strip()
    df = _load_df()

    if kod not in df["Kod"].astype(str).values:
        return False, "Ürün bulunamadı"

    df = df[df["Kod"].astype(str) != kod]
    _save_df(df)

    # QR dosyası varsa sil (opsiyonel)
    qr_path = os.path.join(QR_DIR, f"{kod}.png")
    if os.path.exists(qr_path):
        try:
            os.remove(qr_path)
        except:
            pass

    return True, "Ürün silindi"

# -------------------------------
# QR doğrula (ürün bul)
# -------------------------------
def urun_bul(kod):
    kod = str(kod).strip()
    df = _load_df()

    sonuc = df[df["Kod"].astype(str) == kod]
    if sonuc.empty:
        return False, None

    row = sonuc.iloc[0]
    return True, {
        "Kod": str(row["Kod"]),
        "Urun": str(row["Urun"]),
        "Fiyat": float(row["Fiyat"]),
    }