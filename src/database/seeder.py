import sqlite3
import random
import os
from faker import Faker


def database_kur():
    fake = Faker('tr_TR')

    db_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'eticaret_analiz.db'))
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Tablolar olusturuluyor...")

    # 1. Kategoriler Tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kategoriler (
        kategori_id INTEGER PRIMARY KEY AUTOINCREMENT,
        kategori_adi TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS urunler (
        urun_id INTEGER PRIMARY KEY AUTOINCREMENT,
        urun_adi TEXT NOT NULL,
        fiyat REAL NOT NULL,
        stok_adedi INTEGER NOT NULL,
        kategori_id INTEGER,
        FOREIGN KEY (kategori_id) REFERENCES kategoriler(kategori_id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS siparisler (
        siparis_id INTEGER PRIMARY KEY AUTOINCREMENT,
        urun_id INTEGER,
        adet INTEGER NOT NULL,
        toplam_tutar REAL NOT NULL,
        siparis_tarihi DATE NOT NULL,
        sehir TEXT NOT NULL,
        FOREIGN KEY (urun_id) REFERENCES urunler(urun_id)
    )''')

    print("Ornek veriler ekleniyor...")

    kategoriler = [('Elektronik',), ('Tekstil',), ('Kitap',), ('Kozmetik',), ('Ev & Yaşam',)]
    cursor.executemany("INSERT INTO kategoriler (kategori_adi) VALUES (?)", kategoriler)

    urunler = [
        ('Akıllı Telefon', 35000.0, 50, 1),
        ('Kablosuz Kulaklık', 4500.0, 120, 1),
        ('Deri Ceket', 8000.0, 30, 2),
        ('Pamuklu Tişört', 750.0, 200, 2),
        ('Python Programlama Kitabı', 450.0, 500, 3),
        ('Roman - Gece Yarısı Kütüphanesi', 280.0, 300, 3),
        ('Nemlendirici Krem', 650.0, 150, 4),
        ('Parfüm', 2200.0, 80, 4),
        ('Çalışma Masası', 3200.0, 40, 5),
        ('Kahve Makinesi', 5500.0, 60, 5)
    ]
    cursor.executemany("INSERT INTO urunler (urun_adi, fiyat, stok_adedi, kategori_id) VALUES (?, ?, ?, ?)", urunler)

    populer_sehirler = ['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana', 'Konya', 'Trabzon', 'Eskişehir']

    for _ in range(200):
        urun_secimi = random.randint(0, len(urunler) - 1)
        urun_id = urun_secimi + 1
        urun_fiyat = urunler[urun_secimi][1]

        adet = random.randint(1, 4)
        toplam_tutar = adet * urun_fiyat

        tarih = fake.date_between(start_date='-3M', end_date='today')
        sehir = random.choice(populer_sehirler)

        cursor.execute('''
        INSERT INTO siparisler (urun_id, adet, toplam_tutar, siparis_tarihi, sehir)
        VALUES (?, ?, ?, ?, ?)
        ''', (urun_id, adet, toplam_tutar, tarih, sehir))

    conn.commit()
    conn.close()
    print("İşlem tamamlandı! 'eticaret_analiz.db' başarıyla oluşturuldu ve 200+ sipariş eklendi.")


if __name__ == "__main__":
    database_kur()