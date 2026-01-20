# Akıllı Varlık Takip ve Denetim Paneli 🛡️📱

Bu proje, fiziksel varlıkların (envanter) QR kod teknolojisi kullanılarak takip edilmesini ve siber güvenlik odaklı bir denetim izi (audit log) oluşturulmasını sağlar.

## 🚀 Özellikler
* **Dinamik QR Üretimi:** Her varlık için benzersiz ve IP tabanlı QR kodlar.
* **İlişkisel Veritabanı:** SQLite üzerinde 3NF normalizasyon ve LEFT JOIN sorguları ile performanslı veri yönetimi.
* **Güvenlik Günlüğü:** Her tarama işleminin IP adresi, cihaz bilgisi ve zaman damgası ile kaydedilmesi.
* **Modern Arayüz:** Tailwind CSS ve Glassmorphism tasarımı ile kullanıcı dostu yönetim paneli.

## 🛠️ Kullanılan Teknolojiler
* **Backend:** Python (Flask)
* **Veritabanı:** SQLite3
* **Frontend:** Jinja2, Tailwind CSS
* **Kütüphaneler:** qrcode, socket, sqlite3

## 💻 Kurulum
1. Projeyi klonlayın: `git clone [REPO_LINKIN]`
2. Sanal ortamı oluşturun: `python -m venv venv`
3. Kütüphaneleri kurun: `pip install -r requirements.txt`
4. Uygulamayı başlatın: `python app.py`

## 📊 Veritabanı Şeması
Proje; `users`, `items` ve `system_logs` olmak üzere 3 ana tablodan oluşmaktadır. Veri bütünlüğü `unique_code` anahtarı üzerinden sağlanan mantıksal ilişkilerle korunmaktadır.

---
**Geliştiren:** Yaren Daşpınar  
**Okul:** Amasya Üniversitesi - Bilgisayar Mühendisliği (2023-2026)