# 🤖 Yapay Zeka Destekli SQL / Veri Analitiği Asistanı (Text-to-SQL)

Bu proje, kullanıcıların veritabanlarına doğal dilde (Türkçe) sorular sormasını sağlayan ve arka planda bu soruları geçerli SQL sorgularına dönüştürüp sonuçları interaktif bir web arayüzünde sunan açık kaynaklı bir yapay zeka asistanıdır.

## 🚀 Özellikler

* **Doğal Dil İşleme:** Kullanıcı karmaşık SQL komutları bilmek zorunda kalmadan günlük dilde sorular sorabilir.
* **Dinamik Şema Okuma:** Veritabanı şemasını (tablolar, kolonlar, ilişkiler) otomatik olarak analiz eder.
* **Modern Web Arayüzü:** Streamlit sayesinde kullanıcı dostu, hızlı ve şık bir deneyim sunar.
* **İnteraktif Veri Gösterimi:** Pandas entegrasyonu ile veritabanı çıktılarını düzenlenebilir ve incelenebilir DataFrame (tablo) formatında ekrana yansıtır.

## 🛠️ Kullanılan Teknolojiler

* **Dil / Ortam:** Python 3.11+
* **LLM (Büyük Dil Modeli):** Google Gemini 2.5 Flash
* **Orkestrasyon:** LangChain
* **Web Arayüzü:** Streamlit
* **Veri Analizi:** Pandas
* **Veritabanı:** SQLite

## ⚙️ Kurulum ve Çalıştırma

Projenin yerel bilgisayarınızda çalışabilmesi için aşağıdaki adımları takip edin:

**1. Depoyu Klonlayın**
```bash
git clone https://github.com/KULLANICI_ADINIZ/text-to-sql-assistant.git
cd text-to-sql-assistant
```

**2. Sanal Ortam Oluşturun ve Aktifleştirin**
```bash
python -m venv venv
# Windows için:
venv\Scripts\activate
# MacOS/Linux için:
source venv/bin/activate
```

**3. Gerekli Kütüphaneleri Yükleyin**
```bash
pip install -r requirements.txt
```

**4. Çevresel Değişkenleri Ayarlayın**
Depo ile birlikte gelen `.env.example` dosyasını kopyalayarak kendi `.env` dosyanızı oluşturun ve gizli API anahtarınızı girin:
```bash
cp .env.example .env
```
Ardından `.env` dosyasını açıp aşağıdaki satıra kendi Google Gemini API anahtarınızı yazın:
```env
GEMINI_API_KEY=buraya_kendi_keyinizi_girin
```

## 🗄️ Veritabanı Kurulumu

Veritabanı dosyaları (`.db`) güvenlik ve boyut nedeniyle `.gitignore` içinde yer aldığı için GitHub'a yüklenmez; yani depoyu indiren kişinin kendi bilgisayarında veritabanını oluşturması gerekir. Projeyi indirdikten sonra aşağıdaki komutu çalıştırarak örnek veritabanını (200+ sipariş içeren `eticaret_analiz.db`) oluşturabilirsiniz:

```bash
python src/database/seeder.py
```

Bu komut, `data/eticaret_analiz.db` dosyasını otomatik olarak oluşturur ve örnek kategori, ürün ile sipariş verilerini ekler. (Sohbet geçmişi veritabanı `data/sohbet_gecmisi.db` ilk çalıştırmada otomatik oluşturulur.)

**5. Uygulamayı Başlatın**
```bash
streamlit run src/frontend/app.py
```

## 📸 Ekran Görüntüleri

Kodu indirmeden arayüzün nasıl göründüğünü merak ediyorsanız, uygulamanın açık ve koyu tema (light / dark mode) örnek görünümleri aşağıdadır:

| 🌞 Açık Tema (Light Mode) | 🌙 Koyu Tema (Dark Mode) |
| :---: | :---: |
| ![Açık Tema](src/frontend/assets/ui_light_mode.svg) | ![Koyu Tema](src/frontend/assets/ui_dark_mode.svg) |

Arayüz, sol taraftaki sohbet geçmişi paneli, 🇹🇷 / EN dil seçimi ve 🌙 Dark Mode geçişi ile birlikte gelir; sağ tarafta ise üretilen SQL sorgusu ve sonuç tablosu gösterilir.

## 📂 Proje Yapısı

```
Text-to-SQL/
├── src/
│   ├── frontend/          # Streamlit arayüzü
│   │   ├── app.py
│   │   └── assets/         # Arayüz görselleri (ekran görüntüleri)
│   ├── backend/           # LLM ve LangChain mantığı
│   │   └── llm_manager.py
│   ├── database/          # Veritabanı işlemleri
│   │   ├── chat_db.py     # Sohbet geçmişi yönetimi
│   │   └── seeder.py      # Test verisi üreticisi
│   └── api/               # FastAPI REST servisi
│       └── main.py
├── data/                  # SQLite veritabanı dosyaları
│   ├── eticaret_analiz.db
│   └── sohbet_gecmisi.db
├── tests/                 # Birim testler
├── scripts/               # Yardımcı scriptler
├── .env.example          # Örnek çevresel değişken şablonu
├── .env                   # Gizli API anahtarları (gitignore'da)
├── DOCUMENTATION.md       # Ek dokümantasyon
├── README.md              # Proje açıklaması
└── requirements.txt       # Proje bağımlılıkları
```

## 🚀 API Sunucusu

Proje artık FastAPI ile REST API sunucusu da içerir. Scalar kullanarak API dokümantasyonunu `/docs` endpoint'inde sunar.

**API Sunucusunu Başlatmak için:**
```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Erişim:**
- API dokümantasyonu: `http://localhost:8000/docs`
- Sağlık kontrolü: `http://localhost:8000/health`
- Sorgu endpoint'i: `POST http://localhost:8000/ask`
- Şema endpoint'i: `GET http://localhost:8000/schema`

**Örnek kullanım:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Toplam kaç tane sipariş var?"}'
```

---
*Bu proje açık kaynak kodlu olarak geliştirilmiştir.*