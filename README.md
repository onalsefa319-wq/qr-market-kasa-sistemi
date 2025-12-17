# QR Kod Tabanlı Market Kasa Sistemi
Bu proje, QR kod ile ürün okutma prensibiyle çalışan bir market kasa sistemidir.  
Sistem; kamera ile QR kod okuma, ürün doğrulama, sepet ve toplam hesaplama, Arduino tabanlı LCD ve buzzer ile kullanıcı bilgilendirme ve ödeme sonrası otomatik fiş oluşturma işlemlerini gerçekleştirmektedir.

## Kullanılan Teknolojiler
- Python
- Arduino UNO
- 16x2 I2C LCD
- Buzzer

## Kullanılan Kütüphaneler
- tkinter : Grafik kullanıcı arayüzü oluşturmak için
- OpenCV (cv2) : Kamera görüntüsünü almak için
- pyzbar : QR kodları okumak ve çözmek için
- PIL (Pillow) : Kamera görüntüsünü arayüzde göstermek için
- pyserial : Python ile Arduino arasında seri haberleşme sağlamak için
- os : Dosya ve klasör işlemleri için
- time : Zamanlama ve gecikmeler için
- datetime : Fiş dosyasında tarih bilgisi oluşturmak için

## Özellikler
- QR kod ile hızlı ürün okuma
- Ürün doğrulama ve sepete ekleme
- Anlık toplam tutar hesaplama
- Arduino LCD üzerinden müşteri bilgilendirme
- Buzzer ile sesli geri bildirim
- Ödeme sonrası otomatik fiş oluşturma

## Proje Yapısı
- kasa_gui.py : Grafik kullanıcı arayüzü, kamera ve QR kod okuma işlemleri
- backend.py  : Ürün ekleme, silme ve ürün doğrulama işlemleri
- main.py     : Uygulamanın başlangıç dosyasıdır, grafik arayüzü başlatır
- Arduino kodu : LCD ekran ve buzzer kontrolü
- fisler/     : Oluşturulan fiş dosyalarının tutulduğu klasör
- qr_codes/   : Ürünlere ait QR kodların bulunduğu klasör

## Çalışma Mantığı (Özet)
- Kamera açılır ve QR kod okunur
- Okunan QR kod ürün veritabanında kontrol edilir
- Ürün geçerliyse sepete eklenir ve toplam hesaplanır
- Toplam tutar Arduino’ya gönderilir
- Ödeme alındığında fiş oluşturulur ve sistem sıfırlanır

## Arduino – Python Haberleşmesi
Python ve Arduino, USB üzerinden seri haberleşme (UART) ile iletişim kurmaktadır.  
Python, Arduino’ya toplam tutar ve ödeme komutlarını gönderir; Arduino ise LCD ve buzzer ile kullanıcıya geri bildirim sağlar.

## Lisans
Bu proje eğitim amaçlı geliştirilmiştir.
## Kurulum
- Python 3.9 yüklü olmalıdır
- Gerekli kütüphaneler: opencv-python, pyzbar, pillow, pyserial
- Arduino tarafı için LiquidCrystal_I2C kütüphanesi kullanılmaktadır
