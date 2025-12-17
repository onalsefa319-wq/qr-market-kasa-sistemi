#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);   // Gerekirse 0x3F

#define BUZZER_PIN 8

int toplam = 0;

// ---------------- BUZZER ----------------
void bip_kisa() {
  tone(BUZZER_PIN, 2000);
  delay(100);
  noTone(BUZZER_PIN);
}

void bip_uzun() {
  tone(BUZZER_PIN, 1200);
  delay(600);
  noTone(BUZZER_PIN);
}

// ---------------- KAYAN YAZI ----------------
void scrollText(String text, int row, int speedMs) {
  text = "    " + text + "    ";
  for (int i = 0; i <= text.length() - 16; i++) {
    lcd.setCursor(0, row);
    lcd.print(text.substring(i, i + 16));
    delay(speedMs);
  }
}

// ---------------- TOPLAM GOSTER ----------------
void gosterToplam() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("TOPLAM:");
  lcd.setCursor(0, 1);
  lcd.print(toplam);
  lcd.print(" TL");
}

// ---------------- SETUP ----------------
void setup() {
  Serial.begin(9600);
  pinMode(BUZZER_PIN, OUTPUT);

  lcd.init();
  lcd.backlight();

  gosterToplam();
}

// ---------------- LOOP ----------------
void loop() {
  if (!Serial.available()) return;

  String gelen = Serial.readStringUntil('\n');
  gelen.trim();

  // ---------- TOPLAM ----------
  if (gelen.startsWith("TOTAL;")) {
    toplam = gelen.substring(6).toInt();
    gosterToplam();
    bip_kisa();
  }

  // ---------- ODEME BASLIYOR ----------
  else if (gelen == "PAYING") {
    bip_uzun();
    lcd.clear();
    scrollText("Odeme Aliniyor", 0, 250);
  }

  // ---------- ODEME BITTI ----------
  else if (gelen == "PAID") {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Odeme Alindi");
    delay(2000);
  }

  // ---------- FIS ----------
  else if (gelen == "RECEIPT") {
    lcd.clear();
    scrollText("Fisiniz Aliniz", 0, 250);
    toplam = 0;
    gosterToplam();
  }

  // ---------- HATALI URUN ----------
  else if (gelen == "ERR") {
    // MÜŞTERİYE GÖSTERME YOK
    bip_uzun();
  }
}