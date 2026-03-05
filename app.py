import streamlit as st
import sys
import os
import json
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import time

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
    .match-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE INIT ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'admin_user' not in st.session_state:
    st.session_state.admin_user = None
if 'favori' not in st.session_state:
    st.session_state.favori = "Tümü"
if 'secili_mac' not in st.session_state:
    st.session_state.secili_mac = None
if 'maclar' not in st.session_state:
    st.session_state.maclar = []
if 'filtreli_maclar' not in st.session_state:
    st.session_state.filtreli_maclar = []
if 'hatirlatmalar' not in st.session_state:
    st.session_state.hatirlatmalar = []
if 'baslangic_tarihi' not in st.session_state:
    st.session_state.baslangic_tarihi = date(2026, 3, 5)
if 'bitis_tarihi' not in st.session_state:
    st.session_state.bitis_tarihi = date(2026, 3, 5)
if 'aktif_tab' not in st.session_state:
    st.session_state.aktif_tab = 0

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

# ==================== YARDIMCI FONKSİYONLAR ====================
def get_durum_renk(durum):
    durum_renk = {
        "FINISHED": "🔴 Bitti",
        "TIMED": "🟢 Planlandı",
        "LIVE": "⚡ Canlı",
        "IN_PLAY": "⚡ Devam Ediyor",
        "POSTPONED": "🟡 Ertelendi",
        "SUSPENDED": "⏸️ Durduruldu",
        "CANCELLED": "❌ İptal"
    }
    return durum_renk.get(durum, f"⚪ {durum}")

def get_durum_emoji(durum):
    durum_emoji = {
        "FINISHED": "🔴",
        "TIMED": "🟢",
        "LIVE": "⚡",
        "IN_PLAY": "⚡",
        "POSTPONED": "🟡",
        "SUSPENDED": "⏸️",
        "CANCELLED": "❌"
    }
    return durum_emoji.get(durum, "⚪")

def tarih_filtrele(maclar, baslangic, bitis):
    """Tarih aralığına göre filtrele - date objesi kabul eder"""
    filtreli = []
    for mac in maclar:
        try:
            mac_tarih = datetime.strptime(mac['Tarih'], "%d.%m.%Y").date()
            if baslangic <= mac_tarih <= bitis:
                filtreli.append(mac)
        except:
            continue
    return filtreli

def real_prediction(ev_sahibi, deplasman):
    takim_gucleri = {
        "Man City": 95, "Liverpool": 92, "Arsenal": 90, "Man United": 85,
        "Chelsea": 84, "Tottenham": 83, "Newcastle": 82, "Brighton": 80,
        "Aston Villa": 78, "West Ham": 77, "Brentford": 76, "Crystal Palace": 75,
        "Fulham": 74, "Everton": 73, "Nottingham": 72, "Burnley": 70,
        "Wolverhampton": 69, "Bournemouth": 68, "Sunderland": 67, "Leeds United": 66
    }
    
    form_durumlari = ["WWWWW", "WWWWL", "WWWLL", "WWLLW", "WLLWW", 
                      "LWWWW", "WLWWW", "WWLWW", "DLLWD", "DDWDL"]
    
    ev_guc = takim_gucleri.get(ev_sahibi, 75)
    dep_guc = takim_gucleri.get(deplasman, 75)
    ev_form = random.choice(form_durumlari)
    dep_form = random.choice(form_durumlari)
    
    ev_form_puani = ev_form.count('W') * 3 + ev_form.count('D')
    dep_form_puani = dep_form.count('W') * 3 + dep_form.count('D')
    
    ev_toplam = ev_guc + (ev_form_puani - 7)
    dep_toplam = dep_guc + (dep_form_puani - 7)
    
    ev_gol = round((ev_toplam / 30) + random.uniform(-0.5, 0.5), 1)
    dep_gol = round((dep_toplam / 35) + random.uniform(-0.5, 0.5), 1)
    
    ev_gol = max(0, min(4, ev_gol))
    dep_gol = max(0, min(4, dep_gol))
    
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
    
    toplam_gol = ev_gol + dep_gol
    ust = "2.5 Üst" if toplam_gol > 2.5 else "2.5 Alt"
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

def get_mac_detaylari(mac):
    return {
        'hava_durumu': {
            'sicaklik': random.randint(8, 18),
            'durum': random.choice(['Güneşli ☀️', 'Bulutlu ☁️', 'Yağmurlu 🌧️', 'Rüzgarlı 💨']),
            'nem': random.randint(60, 85),
            'ruzgar': random.randint(5, 25)
        },
        'hakem': {
            'isim': random.choice(['Michael Oliver', 'Anthony Taylor', 'Paul Tierney', 'Chris Kavanagh']),
            'ulke': 'İngiltere',
            'mac_sayisi': random.randint(15, 35),
            'kart_ortalama': round(random.uniform(3.2, 5.8), 1),
            'penalti_orani': round(random.uniform(0.15, 0.35), 2)
        },
        'stadyum': {
            'isim': f"{mac['Ev Sahibi']} Stadium",
            'kapasite': random.randint(35000, 75000),
            'zemin': 'Doğal Çim',
            'yuzolcumu': '105m x 68m'
        },
        'ilk_11': {
            mac['Ev Sahibi']: [
                'Kaleci: ' + random.choice(['Alisson', 'Ederson', 'Pickford', 'Pope']),
                'Defans: ' + ', '.join(random.sample(['Alexander-Arnold', 'Van Dijk', 'Dias', 'Stones', 'Walker', 'Robertson'], 4)),
                'Orta Saha: ' + ', '.join(random.sample(['De Bruyne', 'Rodri', 'Rice', 'Bellingham', 'Fernandes', 'Casemiro'], 3)),
                'Forvet: ' + ', '.join(random.sample(['Haaland', 'Salah', 'Kane', 'Son', 'Saka', 'Rashford'], 3))
            ],
            mac['Deplasman']: [
                'Kaleci: ' + random.choice(['Alisson', 'Ederson', 'Pickford', 'Pope']),
                'Defans: ' + ', '.join(random.sample(['Alexander-Arnold', 'Van Dijk', 'Dias', 'Stones', 'Walker', 'Robertson'], 4)),
                'Orta Saha: ' + ', '.join(random.sample(['De Bruyne', 'Rodri', 'Rice', 'Bellingham', 'Fernandes', 'Casemiro'], 3)),
                'Forvet: ' + ', '.join(random.sample(['Haaland', 'Salah', 'Kane', 'Son', 'Saka', 'Rashford'], 3))
            ]
        },
        'sakatlar': {
            mac['Ev Sahibi']: random.sample(['✅ Sakat yok'] * 3 + ['⚠️ Doubtful: Oyuncu 1', '❌ Out: Oyuncu 2'], 2),
            mac['Deplasman']: random.sample(['✅ Sakat yok'] * 3 + ['⚠️ Doubtful: Oyuncu 3', '❌ Out: Oyuncu 4'], 2)
        },
        'son_maclar': {
            mac['Ev Sahibi']: ['W', 'D', 'W', 'W', 'L'],
            mac['Deplasman']: ['L', 'W', 'D', 'W', 'W']
        }
    }

# ==================== SIDEBAR ====================
def sidebar():
    with st.sidebar:
        st.markdown("## ⚙️ Ayarlar")
        
        lig = st.selectbox(
            "Lig Seçin",
            ["Premier League 2025-2026", "La Liga 2025-2026", "Serie A 2025-2026", 
             "Bundesliga 2025-2026", "Ligue 1 2025-2026", "Champions League 2025-2026"],
            key="sidebar_lig"
        )
        
        st.markdown("---")
        
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
            index=0,
            key="sidebar_favori"
        )
        st.session_state.favori = favori
        
        st.markdown("---")
        
        model = st.multiselect(
            "Kullanılacak Modeller",
            ["Random Forest", "Poisson", "Ensemble (Hepsi)"],
            default=["Ensemble (Hepsi)"],
            key="sidebar_model"
        )
        
        sim_count = st.slider(
            "Monte Carlo Simülasyonu",
            100, 5000, 1000,
            key="sidebar_sim"
        )
        
        st.markdown("---")
        
        kelly = st.slider("Kelly Katsayısı", 0.1, 1.0, 0.5, key="sidebar_kelly")
        max_bet = st.slider("Max Bahis %", 1, 10, 5, key="sidebar_maxbet")
        
        st.markdown("---")
        
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        
        return lig, model, sim_count, kelly, max_bet

# ==================== TAB 1: MAÇLAR ====================
def tab_maclar(lig):
    st.subheader("📋 Günün Maçları")
    
    # Tarih seçimi - date objesi olarak
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Başlangıç Tarihi**")
        b_tarih = st.date_input(
            "Başlangıç", 
            value=st.session_state.baslangic_tarihi,
            key="tab1_baslangic",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("**Bitiş Tarihi**")
        bt_tarih = st.date_input(
            "Bitiş", 
            value=st.session_state.bitis_tarihi,
            key="tab1_bitis",
            label_visibility="collapsed"
        )
    
    # Hızlı seçimler
    st.markdown("**⚡ Hızlı Tarih Seçimi**")
    hizli_col1, hizli_col2, hizli_col3, hizli_col4 = st.columns(4)
    
    with hizli_col1:
        if st.button("📍 Bugün", key="btn_bugun"):
            st.session_state.baslangic_tarihi = date(2026, 3, 5)
            st.session_state.bitis_tarihi = date(2026, 3, 5)
            st.rerun()
    
    with hizli_col2:
        if st.button("📍 Yarın", key="btn_yarin"):
            st.session_state.baslangic_tarihi = date(2026, 3, 6)
            st.session_state.bitis_tarihi = date(2026, 3, 6)
            st.rerun()
    
    with hizli_col3:
        if st.button("📍 Bu Hafta", key="btn_hafta"):
            st.session_state.baslangic_tarihi = date(2026, 3, 5)
            st.session_state.bitis_tarihi = date(2026, 3, 11)
            st.rerun()
    
    with hizli_col4:
        if st.button("📍 Bu Ay", key="btn_ay"):
            st.session_state.baslangic_tarihi = date(2026, 3, 1)
            st.session_state.bitis_tarihi = date(2026, 3, 31)
            st.rerun()
    
    # Tarihleri session'a kaydet
    st.session_state.baslangic_tarihi = b_tarih
    st.session_state.bitis_tarihi = bt_tarih
    
    # Maçları getir
    if st.button("🔍 Maçları Getir", type="primary", use_container_width=True):
        with st.spinner("Maçlar yükleniyor..."):
            progress_bar = st.progress(0)
            
            competition_code = COMPETITIONS.get(lig, "PL")
            maclar = football_client.get_matches(competition_code, season=2025)
            
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            if not maclar:
                st.error("❌ API'den veri alınamadı!")
                return
            
            # Tarih filtrele - date objeleri kullan
            filtreli = tarih_filtrele(maclar, b_tarih, bt_tarih)
            
            # Favori takım filtresi
            if st.session_state.favori != "Tümü":
                filtreli = [m for m in filtreli if st.session_state.favori in [m['Ev Sahibi'], m['Deplasman']]]
            
            st.session_state.maclar = maclar
            st.session_state.filtreli_maclar = filtreli
            
            st.success(f"✅ {len(filtreli)} maç bulundu ({b_tarih.strftime('%d.%m.%Y')} - {bt_tarih.strftime('%d.%m.%Y')})")
    
    # Maçları göster
    if st.session_state.filtreli_maclar:
        df_data = []
        for mac in st.session_state.filtreli_maclar:
            durum = mac.get('Durum', 'Bilinmiyor')
            df_data.append({
                "Durum": get_durum_renk(durum),
                "Ev Sahibi": mac['Ev Sahibi'],
                "Deplasman": mac['Deplasman'],
                "Tarih": mac['Tarih'],
                "Saat": mac['Saat'],
                "Lig": mac['Lig']
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Özet
        durumlar = [m.get('Durum', '') for m in st.session_state.filtreli_maclar]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔴 Bitti", durumlar.count("FINISHED"))
        with col2:
            st.metric("🟢 Planlandı", durumlar.count("TIMED"))
        with col3:
            st.metric("⚡ Canlı", durumlar.count("LIVE") + durumlar.count("IN_PLAY"))
        with col4:
            st.metric("🟡 Ertelendi", durumlar.count("POSTPONED"))
        
        # Hızlı Tahmin
        st.markdown("---")
        st.markdown("### 🎯 Hızlı Tahmin")
        
        mac_options = ["Maç seçin..."] + [f"{m['Ev Sahibi']} vs {m['Deplasman']} | {m['Tarih']} {m['Saat']}" 
                                         for m in st.session_state.filtreli_maclar]
        
        secili = st.selectbox("Tahmin yapmak istediğiniz maçı seçin", mac_options, key="hizli_tahmin_select")
        
        if secili != "Maç seçin...":
            secili_mac = None
            for m in st.session_state.filtreli_maclar:
                if f"{m['Ev Sahibi']} vs {m['Deplasman']}" in secili:
                    secili_mac = m
                    break
            
            if secili_mac:
                col1, col2 = st.columns([1, 2])
                with col1:
                    if st.button("🚀 Tahmin Yap", type="primary", key="btn_hizli_tahmin"):
                        st.session_state.secili_mac = secili_mac
                        st.session_state.aktif_tab = 2
                        st.rerun()
                
                with col2:
                    durum_emoji = get_durum_emoji(secili_mac.get('Durum', ''))
                    st.info(f"{durum_emoji} **{secili_mac['Ev Sahibi']} vs {secili_mac['Deplasman']}**")

# ==================== TAB 2: ANALİZ ====================
def tab_analiz():
    st.subheader("📊 Detaylı Analiz")
    
    if not st.session_state.filtreli_maclar:
        st.info("💡 Önce 'Maçları Getir' butonuna tıklayın.")
        return
    
    mac_options = [f"{m['Ev Sahibi']} vs {m['Deplasman']} ({m['Tarih']})" 
                   for m in st.session_state.filtreli_maclar]
    
    secili = st.selectbox("Maç Seçin", mac_options, key="analiz_mac_select")
    
    secili_mac = None
    for m in st.session_state.filtreli_maclar:
        if f"{m['Ev Sahibi']} vs {m['Deplasman']}" in secili:
            secili_mac = m
            break
    
    if not secili_mac:
        return
    
    detaylar = get_mac_detaylari(secili_mac)
    
    # Hava ve Stadyum
    with st.expander("🌤️ Hava Durumu ve Stadyum", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sıcaklık", f"{detaylar['hava_durumu']['sicaklik']}°C")
            st.metric("Durum", detaylar['hava_durumu']['durum'])
        with col2:
            st.metric("Nem", f"{detaylar['hava_durumu']['nem']}%")
            st.metric("Rüzgar", f"{detaylar['hava_durumu']['ruzgar']} km/s")
        with col3:
            st.metric("Stadyum", detaylar['stadyum']['isim'])
            st.metric("Kapasite", f"{detaylar['stadyum']['kapasite']:,}")
    
    # Hakem
    with st.expander("👮 Hakem Bilgileri"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**İsim:** {detaylar['hakem']['isim']}")
            st.write(f"**Ülke:** {detaylar['hakem']['ulke']}")
        with col2:
            st.write(f"**Maç Sayısı:** {detaylar['hakem']['mac_sayisi']}")
            st.write(f"**Kart Ort.:** {detaylar['hakem']['kart_ortalama']}")
        with col3:
            st.write(f"**Penaltı Oranı:** %{int(detaylar['hakem']['penalti_orani']*100)}")
    
    # İlk 11
    with st.expander("⚽ Muhtemel İlk 11"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**🏠 {secili_mac['Ev Sahibi']}**")
            for oyuncu in detaylar['ilk_11'][secili_mac['Ev Sahibi']]:
                st.write(f"• {oyuncu}")
        with col2:
            st.markdown(f"**✈️ {secili_mac['Deplasman']}**")
            for oyuncu in detaylar['ilk_11'][secili_mac['Deplasman']]:
                st.write(f"• {oyuncu}")
    
    # Sakatlar
    with st.expander("🏥 Sakat/Doubtful Oyuncular"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{secili_mac['Ev Sahibi']}**")
            for durum in detaylar['sakatlar'][secili_mac['Ev Sahibi']]:
                st.write(f"• {durum}")
        with col2:
            st.markdown(f"**{secili_mac['Deplasman']}**")
            for durum in detaylar['sakatlar'][secili_mac['Deplasman']]:
                st.write(f"• {durum}")
    
    # Form
    st.markdown("### 📈 Son 5 Maç Formu")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{secili_mac['Ev Sahibi']}**")
        form_html = "".join(["🟢" if x == "W" else "🟡" if x == "D" else "🔴" 
                            for x in detaylar['son_maclar'][secili_mac['Ev Sahibi']]])
        st.markdown(f"<h2>{form_html}</h2>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"**{secili_mac['Deplasman']}**")
        form_html = "".join(["🟢" if x == "W" else "🟡" if x == "D" else "🔴" 
                            for x in detaylar['son_maclar'][secili_mac['Deplasman']]])
        st.markdown(f"<h2>{form_html}</h2>", unsafe_allow_html=True)
    
    # İstatistikler
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏠 Ev Sahibi İstatistikleri")
        stats = {
            "gol": round(random.uniform(1.2, 2.5), 2),
            "sut": random.randint(8, 18),
            "korner": random.randint(3, 8),
            "kart": random.randint(1, 4)
        }
        fig_data = pd.DataFrame({
            'Metrik': ['Gol Ort.', 'Şut', 'Korner', 'Kart'],
            'Değer': [stats['gol'], stats['sut'], stats['korner'], stats['kart']]
        })
        st.bar_chart(fig_data.set_index('Metrik'))
    
    with col2:
        st.markdown("### 🏃 Deplasman İstatistikleri")
        stats = {
            "gol": round(random.uniform(1.2, 2.5), 2),
            "sut": random.randint(8, 18),
            "korner": random.randint(3, 8),
            "kart": random.randint(1, 4)
        }
        fig_data = pd.DataFrame({
            'Metrik': ['Gol Ort.', 'Şut', 'Korner', 'Kart'],
            'Değer': [stats['gol'], stats['sut'], stats['korner'], stats['kart']]
        })
        st.bar_chart(fig_data.set_index('Metrik'))
    
    # Tahmin yap butonu
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 Bu Maç İçin Tahmin Yap", type="primary", use_container_width=True):
            st.session_state.secili_mac = secili_mac
            st.session_state.aktif_tab = 2
            st.rerun()

# ==================== TAB 3: TAHMİN SONUÇLARI ====================
def tab_tahmin(kelly, max_bet, sim_count):
    st.subheader("🎯 Tahmin Sonuçları")
    
    if not st.session_state.maclar:
        st.info("💡 Önce Tab1'den 'Maçları Getir' butonuna tıklayın.")
        return
    
    # Tarih seçimi
    col1, col2 = st.columns(2)
    with col1:
        b_tarih = st.date_input("Başlangıç Tarihi", date(2026, 3, 5), key="tab3_baslangic")
    with col2:
        bt_tarih = st.date_input("Bitiş Tarihi", date(2026, 3, 31), key="tab3_bitis")
    
    # Tarihe göre filtrele
    filtreli = tarih_filtrele(st.session_state.maclar, b_tarih, bt_tarih)
    
    if st.session_state.favori != "Tümü":
        filtreli = [m for m in filtreli if st.session_state.favori in [m['Ev Sahibi'], m['Deplasman']]]
    
    if not filtreli:
        st.warning("⚠️ Seçili tarih aralığında maç bulunamadı!")
        return
    
    st.success(f"🔍 {len(filtreli)} maç bulundu")
    
    # Maç seçimi
    mac_options = [f"{m['Ev Sahibi']} vs {m['Deplasman']} | {m['Tarih']} {m['Saat']}" for m in filtreli]
    secili = st.selectbox("Tahmin yapmak istediğiniz maçı seçin", mac_options, key="tab3_mac_select")
    
    secili_mac = None
    for m in filtreli:
        if f"{m['Ev Sahibi']} vs {m['Deplasman']}" in secili:
            secili_mac = m
            break
    
    if not secili_mac:
        return
    
    # Maç kartı
    durum_emoji = get_durum_emoji(secili_mac.get('Durum', ''))
    st.markdown(f"""
    <div class="match-card">
        <h3>{durum_emoji} {secili_mac['Ev Sahibi']} vs {secili_mac['Deplasman']}</h3>
        <p>📅 {secili_mac['Tarih']} | 🕐 {secili_mac['Saat']} | 🏆 {secili_mac['Lig']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tahmin butonu
    if st.button("🚀 Tahmini Hesapla", type="primary", use_container_width=True):
        with st.spinner("ML modelleri analiz ediyor..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            tahmin = real_prediction(secili_mac['Ev Sahibi'], secili_mac['Deplasman'])
            
            # Sonuçlar
            st.markdown("---")
            st.markdown("### 📊 Tahmin Sonuçları")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                renk = "🔴" if tahmin['sonuc'] == "1" else "🟡" if tahmin['sonuc'] == "X" else "🟢"
                st.metric("Maç Sonucu", f"{renk} {tahmin['sonuc']}")
            with col2:
                st.metric("Skor Tahmini", tahmin['skor'])
            with col3:
                st.metric("Güven Skoru", f"%{int(tahmin['guven']*100)}")
            with col4:
                st.metric("Gol Tahmini", tahmin['ust'])
            
            # Detaylar
            st.markdown("---")
            st.markdown("### 🔍 Detaylı Analiz")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**🏠 Ev Sahibi**")
                st.progress(tahmin['ev_guc'] / 100)
                st.caption(f"Güç: {tahmin['ev_guc']}/100")
                st.caption(f"Form: {tahmin['ev_form']}")
            with col2:
                st.markdown("**🏃 Deplasman**")
                st.progress(tahmin['dep_guc'] / 100)
                st.caption(f"Güç: {tahmin['dep_guc']}/100")
                st.caption(f"Form: {tahmin['dep_form']}")
            with col3:
                st.markdown("**📈 Diğer**")
                st.caption(f"KG: {tahmin['kg']}")
                st.caption(f"Toplam: {tahmin['ust']}")
            
            # Bahis
            st.markdown("---")
            st.markdown("### 💰 Bahis Önerisi")
            
            if tahmin['guven'] > 0.6:
                kelly_oran = (tahmin['guven'] * 100 - 40) / 100 * kelly
                onerilen_bahis = min(kelly_oran, max_bet)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"✅ Kelly: Bankroll'un %{onerilen_bahis:.1f}'i")
                with col2:
                    st.info(f"📌 Önerilen: **{tahmin['sonuc']}** veya **{tahmin['ust']}**")
                
                if tahmin['guven'] < 0.65:
                    st.warning("⚠️ Orta risk")
                elif tahmin['guven'] < 0.75:
                    st.info("ℹ️ İyi güven")
                else:
                    st.success("✅ Yüksek güven")
            else:
                st.error("❌ Güven düşük - Bahis önerilmez!")
            
            # Alternatifler
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

# ==================== ANA UYGULAMA ====================
def main_app():
    lig, model, sim_count, kelly, max_bet = sidebar()
    
    st.markdown('<h1 class="main-header">⚽ 12 Adam - Tahmin Sistemi</h1>', unsafe_allow_html=True)
    
    # Üst bilgi
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Lig", lig.split()[0])
    with col2:
        st.metric("Mod", "API")
    with col3:
        st.metric("Model", len(model))
    with col4:
        st.metric("Simülasyon", f"{sim_count:,}")
    
    st.markdown("---")
    
    # Tab'lar
    tab1, tab2, tab3 = st.tabs(["📋 Maçlar", "📊 Analiz & Grafikler", "🎯 Tahmin Sonuçları"])
    
    with tab1:
        tab_maclar(lig)
    
    with tab2:
        tab_analiz()
    
    with tab3:
        tab_tahmin(kelly, max_bet, sim_count)

if __name__ == "__main__":
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()
