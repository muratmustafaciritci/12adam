import streamlit as st
import sys
sys.path.append('.')

from main import main  # main.py'den fonksiyon import et

st.set_page_config(
    page_title="12 Adam - Futbol Tahmin",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ 12 Adam - Türkiye Futbol Tahmin Sistemi")

# Sidebar
st.sidebar.header("Ayarlar")
mod = st.sidebar.selectbox(
    "Çalışma Modu",
    ["Otomatik", "API Modu", "Mock Modu"]
)

lig = st.sidebar.selectbox(
    "Lig Seçin",
    ["Süper Lig 2025-2026", "1. Lig 2025-2026", "2. Lig 2025-2026"]
)

# Ana ekran
col1, col2 = st.columns(2)

with col1:
    st.subheader("Günün Maçları")
    if st.button("🔍 Maçları Getir", type="primary"):
        with st.spinner("Maçlar yükleniyor..."):
            # Burada main.py fonksiyonunu çağır
            st.success("Maçlar yüklendi! (Simülasyon)")
            st.json({
                "Ev Sahibi": "Galatasaray",
                "Deplasman": "Fenerbahçe",
                "Tahmin": "2.5 Üst"
            })

with col2:
    st.subheader("Tahmin Sonuçları")
    if st.button("🎯 Tahmin Yap"):
        st.info("Tahminler hesaplanıyor...")
        st.metric("Galibiyet Olasılığı", "%65")
        st.metric("Beraberlik", "%20")
        st.metric("Mağlubiyet", "%15")

# Footer
st.markdown("---")
st.caption("Geliştirici: Murat Mustafa Ciritçi | https://www.muratciritci.com.tr")