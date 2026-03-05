# ⚽ 12 Adam - Türkiye Futbol Tahmin Sistemi

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://12adam-hc33rupjsxkbhjchpchywz.streamlit.app/)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Version](https://img.shields.io/badge/version-1.1.0-green.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

**Geliştirici:** Murat Mustafa Ciritçi  
**Web:** https://www.muratciritci.com.tr

---

## 🚀 Canlı Demo

**🔗 Hemen Dene:** https://12adam-hc33rupjsxkbhjchpchywz.streamlit.app/

Tarayıcıda çalışır, kurulum gerekmez!

---

## 🎯 Özellikler

### 🔐 Güvenlik
- Admin girişi (SHA-256 hash şifreleme)
- Session yönetimi

### 🤖 Yapay Zeka & ML
- **Random Forest** tahmin modeli
- **Poisson** dağılımı analizi
- **Ensemble** (birleşik) tahmin
- **Monte Carlo** simülasyonu (100-5000 iterasyon)

### 📊 Analiz & Grafikler
- Bar grafikler (gol, şut, korner, kart)
- Head-to-Head karşılaştırma
- Takım istatistikleri
- Form durumu analizi

### 💰 Bahis Stratejisi
- **Kelly Kriteri** ile optimum bahis hesaplama
- Güven skoru (%55-85)
- Value bet analizi

### ⚙️ Çalışma Modları
| Mod | Açıklama |
|-----|----------|
| 🔄 Otomatik | API çalışmazsa Mock'a geçer |
| 🌐 API | Gerçek veri (API anahtarı gerekli) |
| 🎲 Mock | Simülasyon verisi (limitsiz) |

### 🏆 Lig Desteği
- ✅ Süper Lig 2025-2026
- ✅ 1. Lig 2025-2026  
- ✅ 2. Lig 2025-2026

---

## 🖥️ Kurulum (Yerel)

```bash
# 1. İndir
git clone https://github.com/muratmustafaciritci/12adam.git

# 2. Klasöre gir
cd 12adam

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Çalıştır
streamlit run app.py
