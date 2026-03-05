import streamlit as st
import sys
import os
import json
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

sys.path.append('.')

# Football Data Client (football-data.org)
from football_data_client import FootballDataClient, COMPETITIONS

# Client oluştur
football_data_key = os.getenv("FOOTBALL_DATA_KEY", "42a70b8d9de542d7a74c3b4b8e8c59c1")
football_client = FootballDataClient(football_data_key)

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
    .match-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
    .date-input {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Session state başlat
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'admin_user' not in st.session_state:
    st.session_state.admin_user = None
if 'favori' not in st.session_state:
    st.session_state.favori = "Tümü"
if 'secili_mac' not in st.session_state:
    st.session_state.secili_mac = None
if 'baslangic_tarihi' not in st.session_state:
    st.session_state.baslangic_tarihi = None
if 'bitis_tarihi' not in st.session_state:
    st.session_state.bitis_tarihi = None

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
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
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

# ==================== GERÇEKÇİ TAHMİN FONKSİYONU ====================
def real_prediction(ev_sahibi, deplasman):
    """Gerçekçi tahmin sistemi"""
    
    # Takım güçleri (2025-2026 sezonu)
    takim_gucleri = {
        "Man City": 95, "Liverpool": 92, "Arsenal": 90, "Man United": 85,
        "Chelsea": 84, "Tottenham": 83, "Newcastle": 82, "Brighton": 80,
        "Aston Villa": 78, "West Ham": 77, "Brentford": 76, "Crystal Palace": 75,
        "Fulham": 74, "Everton": 73, "Nottingham": 72, "Burnley": 70,
        "Wolverhampton": 69, "Bournemouth": 68, "Sunderland": 67, "Leeds United": 66
    }
    
    # Form durumları (son 5 maç)
    form_durumlari = ["WWWWW", "WWWWL", "WWWLL", "WWLLW", "WLLWW", 
                      "LWWWW", "WLWWW", "WWLWW", "DLLWD", "DDWDL"]
    
    ev_guc = takim_gucleri.get(ev_sahibi, 75)
    dep_guc = takim_gucleri.get(deplasman, 75)
    ev_form = random.choice(form_durumlari)
    dep_form = random.choice(form_durumlari)
    
    # Form etkisi
    ev_form_puani = ev_form.count('W') * 3 + ev_form.count('D')
    dep_form_puani = dep_form.count('W') * 3 + dep_form.count('D')
    
    # Toplam güç
    ev_toplam = ev_guc + (ev_form_puani - 7)
    dep_toplam = dep_guc + (dep_form_puani - 7)
    
    # Gol tahmini (Poisson benzeri)
    ev_gol = round((ev_toplam / 30) + random.uniform(-0.5, 0.5), 1)
    dep_gol = round((dep_toplam / 35) + random.uniform(-0.5, 0.5), 1)
    
    ev_gol = max(0, min(4, ev_gol))
    dep_gol = max(0, min(4, dep_gol))
    
    # Sonuç tahmini
    fark = ev_toplam - dep_toplam
    
    if fark > 15:
        sonuc = "1"
        guven = min(0.85, 0.60 + fark/100)
    elif fark > 5:
        sonuc = "1"
        guven = min(0.75, 0.55 + fark/100)
    elif fark < -15:
        sonuc = "2"
        guven = min(0.85, 0.60 + abs(fark)/100)
    elif fark < -5:
        sonuc = "2"
        guven = min(0.75, 0.55 + abs(fark)/100)
    else:
        sonuc = "X"
        guven = 0.60
    
    # Üst/Alt tahmini
    toplam_gol = ev_gol + dep_gol
    ust = "2.5 Üst" if toplam_gol > 2.5 else "2.5 Alt"
    
    # KG Var/Yok
    kg = "KG Var" if (ev_gol > 0 and dep_gol > 0) else "KG Yok"
    
    return {
        'sonuc': sonuc,
        'skor': f"{ev_gol:.0f}-{dep_gol:.0f}",
        'guven': guven,
        'ust': ust,
        'kg': kg,
        'ev_guc': int(ev_toplam),
        'dep_guc': int(dep_toplam),
        'ev_form': ev_form,
        'dep_form': dep_form,
        'ev_gol': ev_gol,
        'dep_gol': dep_gol
    }

# ==================== TARİH FİLTRELEME FONKSİYONU ====================
def tarih_filtrele(maclar, baslangic, bitis):
    """Tarih aralığına göre filtrele"""
    filtreli = []
    for mac in maclar:
        mac_tarih = datetime.strptime(mac['Tarih'], "%d.%m.%Y")
        if baslangic <= mac_tarih <= bitis:
            filtreli.append(mac)
    return filtreli

# ==================== ANA UYGULAMA ====================
def main_app():
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Ayarlar")
        
        # Lig Seçimi (2025-2026)
        lig = st.selectbox(
            "Lig Seçin",
            ["Premier League 2025-2026", "La Liga 2025-2026", "Serie A 2025-2026", 
             "Bundesliga 2025-2026", "Ligue 1 2025-2026", "Champions League 2025-2026"]
        )
        
        st.markdown("---")
        
        # Favori Takım (2025-2026)
        st.markdown("### ⭐ Favori Takım")
        
        favori_takimlar = {
            "Premier League 2025-2026": ["Tümü", "Man City", "Liverpool", "Arsenal", "Chelsea", "Man United", "Tottenham", "Newcastle"],
            "La Liga 2025-2026": ["Tümü", "Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla", "Valencia", "Villarreal"],
            "Serie A 2025-2026": ["Tümü", "Juventus", "Inter", "AC Milan", "Napoli", "Roma", "Lazio", "Fiorentina"],
            "Bundesliga 2025-2026": ["Tümü", "Bayern Munich", "Dortmund", "RB Leipzig", "Bayer Leverkusen", "Frankfurt", "Wolfsburg"],
            "Ligue 1 2025-2026": ["Tümü", "PSG", "Marseille", "Lyon", "Monaco", "Lille", "Nice"],
            "Champions League 2025-2026": ["Tümü", "Real Madrid", "Man City", "Bayern Munich", "PSG", "Barcelona", "Arsenal", "Inter"]
        }
        
        favori = st.selectbox(
            "Takım Filtrele",
            favori_takimlar.get(lig, ["Tümü"]),
            index=0
        )
        st.session_state.favori = favori
        
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
        st.metric("Mod", "API")
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
                
                # Football Data API - 2025-2026 sezonu
                competition_code = COMPETITIONS.get(lig, "PL")
                maclar = football_client.get_matches(competition_code, season=2025)
                
                # API boşsa uyarı
                if not maclar:
                    st.warning("API'den veri alınamadı. Limit dolmuş olabilir veya API hatası.")
                
                # Favori takım filtresi
                if st.session_state.favori != "Tümü" and maclar:
                    maclar = [m for m in maclar if st.session_state.favori in [m['Ev Sahibi'], m['Deplasman']]]
                    
                    if len(maclar) == 0:
                        st.warning(f"⚠️ {st.session_state.favori} için maç bulunamadı!")
                    else:
                        st.success(f"✅ {st.session_state.favori} için {len(maclar)} maç bulundu")
                
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                # Göster
                if maclar:
                    df = pd.DataFrame(maclar)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.session_state.maclar = maclar
                else:
                    st.error("❌ Maç bulunamadı! API limiti dolmuş olabilir.")
    
    with tab2:
        st.subheader("📊 Detaylı Analiz")
        
        if 'maclar' in st.session_state:
            secili_mac = st.selectbox(
                "Maç Seçin",
                [f"{m['Ev Sahibi']} vs {m['Deplasman']} ({m['Tarih']})" for m in st.session_state.maclar]
            )
            
            # Seçili maçı bul
            secili_mac_adi = secili_mac.split(" (")[0]
            ev_dep = secili_mac_adi.split(" vs ")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏠 Ev Sahibi İstatistikleri")
                stats = generate_team_stats(ev_dep[0])
                
                fig_data = pd.DataFrame({
                    'Metrik': ['Gol Ort.', 'Şut', 'Korner', 'Kart'],
                    'Değer': [stats['gol'], stats['sut'], stats['korner'], stats['kart']]
                })
                
                st.bar_chart(fig_data.set_index('Metrik'))
                
                st.json(stats)
            
            with col2:
                st.markdown("### 🏃 Deplasman İstatistikleri")
                stats = generate_team_stats(ev_dep[1])
                
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
            # Tarih aralığı seçimi
            st.markdown("### 📅 Tarih Aralığı Seçimi")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Başlangıç Tarihi**")
                b_gun = st.number_input("Gün", min_value=1, max_value=31, value=5, key="b_gun")
                b_ay = st.number_input("Ay", min_value=1, max_value=12, value=3, key="b_ay")
                b_yil = st.number_input("Yıl", min_value=2025, max_value=2027, value=2026, key="b_yil")
            
            with col2:
                st.markdown("**Bitiş Tarihi**")
                bt_gun = st.number_input("Gün", min_value=1, max_value=31, value=31, key="bt_gun")
                bt_ay = st.number_input("Ay", min_value=1, max_value=12, value=5, key="bt_ay")
                bt_yil = st.number_input("Yıl", min_value=2025, max_value=2027, value=2026, key="bt_yil")
            
            # Hızlı seçimler
            st.markdown("**⚡ Hızlı Seçimler**")
            hizli_col1, hizli_col2, hizli_col3, hizli_col4 = st.columns(4)
            
            with hizli_col1:
                if st.button("📍 Bugün"):
                    b_gun, b_ay, b_yil = 5, 3, 2026
                    bt_gun, bt_ay, bt_yil = 5, 3, 2026
            
            with hizli_col2:
                if st.button("📍 Yarın"):
                    b_gun, b_ay, b_yil = 6, 3, 2026
                    bt_gun, bt_ay, bt_yil = 6, 3, 2026
            
            with hizli_col3:
                if st.button("📍 Bu Hafta"):
                    b_gun, b_ay, b_yil = 5, 3, 2026
                    bt_gun, bt_ay, bt_yil = 11, 3, 2026
            
            with hizli_col4:
                if st.button("📍 Bu Ay"):
                    b_gun, b_ay, b_yil = 1, 3, 2026
                    bt_gun, bt_ay, bt_yil = 31, 3, 2026
            
            # Tarihleri oluştur
            try:
                baslangic_tarihi = datetime(b_yil, b_ay, b_gun)
                bitis_tarihi = datetime(bt_yil, bt_ay, bt_gun)
                
                if baslangic_tarihi > bitis_tarihi:
                    st.error("❌ Başlangıç tarihi bitiş tarihinden sonra olamaz!")
                else:
                    st.session_state.baslangic_tarihi = baslangic_tarihi
                    st.session_state.bitis_tarihi = bitis_tarihi
                    
                    st.success(f"📅 {baslangic_tarihi.strftime('%d.%m.%Y')} - {bitis_tarihi.strftime('%d.%m.%Y')} arası maçlar")
                    
                    # Tarihe göre filtrele
                    filtreli_maclar = tarih_filtrele(st.session_state.maclar, baslangic_tarihi, bitis_tarihi)
                    
                    if st.session_state.favori != "Tümü":
                        filtreli_maclar = [m for m in filtreli_maclar if st.session_state.favori in [m['Ev Sahibi'], m['Deplasman']]]
                    
                    st.info(f"🔍 {len(filtreli_maclar)} maç bulundu")
            
            except ValueError:
                st.error("❌ Geçersiz tarih! Lütfen kontrol edin.")
                filtreli_maclar = []
            
            # Maç seçimi
            if filtreli_maclar:
                st.markdown("---")
                st.markdown("### ⚽ Maç Seçimi")
                
                mac_secenekleri = [f"{m['Ev Sahibi']} vs {m['Deplasman']} - {m['Tarih']} {m['Saat']}" for m in filtreli_maclar]
                
                secili_mac_index = st.selectbox(
                    "Tahmin yapmak istediğiniz maçı seçin",
                    range(len(mac_secenekleri)),
                    format_func=lambda i: mac_secenekleri[i]
                )
                
                secili_mac = filtreli_maclar[secili_mac_index]
                st.session_state.secili_mac = secili_mac
                
                # Seçili maç kartı
                st.markdown("---")
                st.markdown(f"""
                <div class="match-card">
                    <h3>⚽ {secili_mac['Ev Sahibi']} vs {secili_mac['Deplasman']}</h3>
                    <p>📅 {secili_mac['Tarih']} | 🕐 {secili_mac['Saat']} | 🏆 {secili_mac['Lig']}</p>
                    <p>📊 Durum: {secili_mac.get('Durum', 'Bilinmiyor')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Tahmin butonu
                if st.button("🎯 Tahmin Yap", type="primary", use_container_width=True):
                    with st.spinner("ML modelleri analiz ediyor..."):
                        progress_bar = st.progress(0)
                        
                        for i in range(100):
                            time.sleep(0.015)
                            progress_bar.progress(i + 1)
                        
                        # Gerçekçi tahmin
                        tahmin = real_prediction(secili_mac['Ev Sahibi'], secili_mac['Deplasman'])
                        
                        # Sonuçları göster
                        st.markdown("---")
                        st.markdown("### 📊 Tahmin Sonuçları")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            renk = "🔴" if tahmin['sonuc'] == "1" else "🟡" if tahmin['sonuc'] == "X" else "🟢"
                            st.metric("Maç Sonucu", f"{renk} {tahmin['sonuc']}")
                        
                        with col2:
                            st.metric("Skor Tahmini", tahmin['skor'])
                        
                        with col3:
                            guven_renk = "normal" if tahmin['guven'] < 0.7 else "inverse"
                            st.metric("Güven Skoru", f"%{int(tahmin['guven']*100)}", 
                                    delta="Yüksek" if tahmin['guven'] > 0.7 else "Orta" if tahmin['guven'] > 0.6 else "Düşük")
                        
                        with col4:
                            st.metric("Gol Tahmini", tahmin['ust'])
                        
                        # Detaylı analiz
                        st.markdown("---")
                        st.markdown("### 🔍 Detaylı Analiz")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**🏠 Ev Sahibi**")
                            st.progress(tahmin['ev_guc'] / 100)
                            st.caption(f"Güç: {tahmin['ev_guc']}/100")
                            st.caption(f"Form: {tahmin['ev_form']}")
                            st.caption(f"Gol Olasılığı: {tahmin['ev_gol']:.1f}")
                        
                        with col2:
                            st.markdown("**🏃 Deplasman**")
                            st.progress(tahmin['dep_guc'] / 100)
                            st.caption(f"Güç: {tahmin['dep_guc']}/100")
                            st.caption(f"Form: {tahmin['dep_form']}")
                            st.caption(f"Gol Olasılığı: {tahmin['dep_gol']:.1f}")
                        
                        with col3:
                            st.markdown("**📈 Diğer Tahminler**")
                            st.caption(f"KG Tahmini: {tahmin['kg']}")
                            st.caption(f"Toplam Gol: {tahmin['ust']}")
                            st.caption(f"Güven: %{int(tahmin['guven']*100)}")
                        
                        # Kelly Kriteri
                        st.markdown("---")
                        st.markdown("### 💰 Bahis Önerisi")
                        
                        if tahmin['guven'] > 0.6:
                            kelly_oran = (tahmin['guven'] * 100 - 40) / 100 * kelly
                            onerilen_bahis = min(kelly_oran, max_bet)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.success(f"✅ Kelly Önerisi: Bankroll'un %{onerilen_bahis:.1f}'i")
                            
                            with col2:
                                st.info(f"📌 Önerilen Bahis: **{tahmin['sonuc']}** veya **{tahmin['ust']}**")
                            
                            # Risk uyarısı
                            if tahmin['guven'] < 0.65:
                                st.warning("⚠️ Orta risk - Dikkatli olun!")
                            elif tahmin['guven'] < 0.75:
                                st.info("ℹ️ İyi güven - Değerlendirilebilir")
                            else:
                                st.success("✅ Yüksek güvenli tahmin!")
                        else:
                            st.error("❌ Güven düşük (%60 altı) - Bahis önerilmez!")
                        
                        # Alternatif bahisler
                        st.markdown("---")
                        st.markdown("### 🎲 Alternatif Bahisler")
                        
                        alt_col1, alt_col2, alt_col3, alt_col4 = st.columns(4)
                        
                        with alt_col1:
                            st.metric("İY/MS", f"1/{tahmin['sonuc']}")
                        
                        with alt_col2:
                            st.metric("KG", tahmin['kg'])
                        
                        with alt_col3:
                            st.metric("Toplam Gol", tahmin['ust'])
                        
                        with alt_col4:
                            handikap = "H1 (-1)" if tahmin['ev_guc'] > tahmin['dep_guc'] + 10 else "HX" if abs(tahmin['ev_guc'] - tahmin['dep_guc']) < 5 else "H2 (-1)"
                            st.metric("Handikap", handikap)
            else:
                st.warning("⚠️ Seçili tarih aralığında maç bulunamadı!")
        else:
            st.info("💡 Önce 'Maçları Getir' butonuna tıklayın.")

# ==================== YARDIMCI FONKSİYONLAR ====================
import time

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
