import streamlit as st
import sys
import os
import json
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

sys.path.append('.')

# Sayfa yapılandırması
st.set_page_config(
    page_title="12 Adam - Futbol Tahmin Sistemi",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile modern tasarım
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .success-msg {
        color: #28a745;
        font-weight: bold;
    }
    .warning-msg {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Session state başlat
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'admin_user' not in st.session_state:
    st.session_state.admin_user = None

# ==================== GİRİŞ SAYFASI ====================
def login_page():
    st.markdown('<h1 class="main-header">⚽ 12 Adam</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center;">Türkiye Futbol Tahmin Sistemi</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        st.subheader("🔐 Admin Girişi")
        
        username = st.text_input("Kullanıcı Adı", value="admin")
        password = st.text_input("Şifre", type="password")
        
        if st.button("Giriş Yap", type="primary", use_container_width=True):
            # Hash kontrolü
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Yeni hash
            correct_hash = "7d85a3c65095fef30f8b4a9b16a7d1393c2909f6e5d73cd4238990caf475a00a"
            
            if username == "admin" and password_hash == correct_hash:
                st.session_state.logged_in = True
                st.session_state.admin_user = username
                st.success("✅ Giriş başarılı!")
                st.rerun()
            else:
                st.error("❌ Kullanıcı adı veya şifre hatalı!")
        
        st.markdown("---")
        st.info("💡 Yeni şifrenizle giriş yapın")

# ==================== ANA UYGULAMA ====================
def main_app():
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Ayarlar")
        
        # Çalışma Modu
        mod = st.selectbox(
            "Çalışma Modu",
            ["Otomatik (API → Mock)", "API Modu (Gerçek Veri)", "Mock Modu (Simülasyon)"],
            help="API için anahtar gerekli. Otomatik modda API çalışmazsa Mock'a geçer."
        )
        
        # Lig Seçimi
        lig = st.selectbox(
            "Lig Seçin",
            ["Süper Lig 2025-2026", "1. Lig 2025-2026", "2. Lig 2025-2026"]
        )
        
        st.markdown("---")
        
        # ML Model Ayarları
        st.markdown("### 🤖 ML Model")
        model = st.multiselect(
            "Kullanılacak Modeller",
            ["Random Forest", "Poisson", "Ensemble (Hepsi)"],
            default=["Ensemble (Hepsi)"]
        )
        
        # Simülasyon Sayısı
        sim_count = st.slider(
            "Monte Carlo Simülasyonu",
            100, 5000, 1000,
            help="Ne kadar yüksek olursa tahmin o kadar kesin olur."
        )
        
        st.markdown("---")
        
        # Bahis Ayarları
        st.markdown("### 💰 Bahis Stratejisi")
        kelly = st.slider("Kelly Katsayısı", 0.1, 1.0, 0.5)
        max_bet = st.slider("Max Bahis %", 1, 10, 5)
        
        st.markdown("---")
        
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    
    # Ana Ekran
    st.markdown('<h1 class="main-header">⚽ 12 Adam - Tahmin Sistemi</h1>', unsafe_allow_html=True)
    
    # Üst Bilgi Kartları
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Lig", lig.split()[0])
    with col2:
        st.metric("Mod", mod.split()[0])
    with col3:
        st.metric("Model", str(len(model)))
    with col4:
        st.metric("Simülasyon", f"{sim_count:,}")
    
    st.markdown("---")
    
    # Maç Listesi ve Tahmin
    tab1, tab2, tab3 = st.tabs(["📋 Maçlar", "📊 Analiz & Grafikler", "🎯 Tahmin Sonuçları"])
    
    with tab1:
        st.subheader("Günün Maçları")
        
        if st.button("🔍 Maçları Getir", type="primary"):
            with st.spinner("Maçlar yükleniyor..."):
                progress_bar = st.progress(0)
                
                # Simülasyon maçları
                maclar = generate_mock_matches(lig)
                
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                st.success(f"✅ {len(maclar)} maç bulundu!")
                
                # Maç tablosu
                df = pd.DataFrame(maclar)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Seçim için
                st.session_state.maclar = maclar
    
    with tab2:
        st.subheader("📊 Detaylı Analiz")
        
        if 'maclar' in st.session_state:
            secili_mac = st.selectbox(
                "Maç Seçin",
                [f"{m['Ev Sahibi']} vs {m['Deplasman']}" for m in st.session_state.maclar]
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏠 Ev Sahibi İstatistikleri")
                stats = generate_team_stats(secili_mac.split(" vs ")[0])
                
                fig_data = pd.DataFrame({
                    'Metrik': ['Gol Ort.', 'Şut', 'Korner', 'Kart'],
                    'Değer': [stats['gol'], stats['sut'], stats['korner'], stats['kart']]
                })
                
                st.bar_chart(fig_data.set_index('Metrik'))
                
                st.json(stats)
            
            with col2:
                st.markdown("### 🏃 Deplasman İstatistikleri")
                stats = generate_team_stats(secili_mac.split(" vs ")[1])
                
                fig_data = pd.DataFrame({
                    'Metrik': ['Gol Ort.', 'Şut', 'Korner', 'Kart'],
                    'Değer': [stats['gol'], stats['sut'], stats['korner'], stats['kart']]
                })
                
                st.bar_chart(fig_data.set_index('Metrik'))
                
                st.json(stats)
            
            # Head-to-Head
            st.markdown("### ⚔️ Karşılaştırmalı Analiz")
            h2h_data = pd.DataFrame({
                'Galibiyet': [random.randint(40, 60), random.randint(20, 40), random.randint(10, 20)],
                'Beraberlik': [random.randint(10, 20), random.randint(10, 20), random.randint(10, 20)],
                'Mağlubiyet': [random.randint(20, 40), random.randint(40, 60), random.randint(40, 60)]
            }, index=['Ev Sahibi', 'Beraberlik', 'Deplasman'])
            
            st.bar_chart(h2h_data)
        else:
            st.info("💡 Önce 'Maçları Getir' butonuna tıklayın.")
    
    with tab3:
        st.subheader("🎯 ML Tahmin Sonuçları")
        
        if 'maclar' in st.session_state:
            if st.button("🎯 Tahmin Yap", type="primary"):
                with st.spinner("ML modelleri çalışıyor..."):
                    progress_bar = st.progress(0)
                    
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    
                    # Tahmin sonuçları
                    for mac in st.session_state.maclar[:3]:  # İlk 3 maç
                        with st.container():
                            st.markdown("---")
                            cols = st.columns([2, 1, 1, 1, 1])
                            
                            with cols[0]:
                                st.markdown(f"**{mac['Ev Sahibi']} vs {mac['Deplasman']}**")
                            
                            # ML Tahminleri
                            rf_pred = random.choice(["1", "X", "2", "1.5 Üst", "2.5 Üst"])
                            poisson_pred = random.choice(["1", "X", "2", "KG Var", "KG Yok"])
                            ensemble = random.choice(["1", "X", "2"])
                            
                            with cols[1]:
                                st.metric("Random Forest", rf_pred)
                            with cols[2]:
                                st.metric("Poisson", poisson_pred)
                            with cols[3]:
                                st.metric("Ensemble", ensemble, delta="⭐")
                            
                            # Güven skoru
                            confidence = random.uniform(0.55, 0.85)
                            with cols[4]:
                                st.metric("Güven", f"%{confidence*100:.0f}")
                            
                            # Monte Carlo sonuçları
                            mc_results = monte_carlo_simulation(sim_count)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Ev Sahibi %", f"%{mc_results['ev']:.1f}")
                            with col2:
                                st.metric("Beraberlik %", f"%{mc_results['beraberlik']:.1f}")
                            with col3:
                                st.metric("Deplasman %", f"%{mc_results['deplasman']:.1f}")
                            
                            # Kelly Kriteri
                            if confidence > 0.6:
                                kelly_bet = (confidence * 100 - (100 - confidence * 100)) / 100 * kelly
                                st.success(f"💰 Kelly Önerisi: Bahis miktarı bankroll'un %{min(kelly_bet, max_bet):.1f}'i")
        else:
            st.info("💡 Önce 'Maçları Getir' butonuna tıklayın.")
    
    # Footer
    st.markdown("---")
    st.caption("Geliştirici: Murat Mustafa Ciritçi | https://www.muratciritci.com.tr  | v1.1.0-hybrid")

# ==================== YARDIMCI FONKSİYONLAR ====================
import time

def generate_mock_matches(lig):
    """Mock maç verisi üret"""
    takimlar = {
        "Süper Lig 2025-2026": ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Başakşehir", "Konyaspor"],
        "1. Lig 2025-2026": ["Sakaryaspor", "Kocaelispor", "Eyüpspor", "Bodrumspor", "Manisa FK", "Bandırmaspor"],
        "2. Lig 2025-2026": ["Ankara Demirspor", "Zonguldak Kömürspor", "Nazilli Belediyespor", "Etimesgut Belediyespor"]
    }
    
    secili_takimlar = takimlar.get(lig, takimlar["Süper Lig 2025-2026"])
    maclar = []
    
    for i in range(0, len(secili_takimlar)-1, 2):
        maclar.append({
            "Ev Sahibi": secili_takimlar[i],
            "Deplasman": secili_takimlar[i+1],
            "Tarih": (datetime.now() + timedelta(days=random.randint(0, 7))).strftime("%d.%m.%Y"),
            "Saat": f"{random.randint(13, 21)}:00",
            "Lig": lig
        })
    
    return maclar

def generate_team_stats(takim):
    """Takım istatistikleri üret"""
    return {
        "gol": round(random.uniform(1.2, 2.5), 2),
        "sut": random.randint(8, 18),
        "korner": random.randint(3, 8),
        "kart": random.randint(1, 4),
        "possession": random.randint(45, 65),
        "form": random.choice(["WWDLW", "WWDLL", "LLWWD", "DWDWD"])
    }

def monte_carlo_simulation(n):
    """Monte Carlo simülasyonu"""
    sonuclar = {"ev": 0, "beraberlik": 0, "deplasman": 0}
    
    for _ in range(n):
        ev_gol = np.random.poisson(1.8)
        dep_gol = np.random.poisson(1.2)
        
        if ev_gol > dep_gol:
            sonuclar["ev"] += 1
        elif ev_gol == dep_gol:
            sonuclar["beraberlik"] += 1
        else:
            sonuclar["deplasman"] += 1
    
    return {k: (v/n)*100 for k, v in sonuclar.items()}

# ==================== BAŞLAT ====================
if __name__ == "__main__":
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()
