import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Crazytown Trader",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS İLE MODERN TASARIM ---
st.markdown("""
    <style>
    /* Genel ayarlar */
    .main-title {font-size: 3rem; font-weight: 800; color: #00F2C3; text-align: center; margin-bottom: 0px;}
    .slogan {font-size: 1.2rem; color: #cfd8dc; text-align: center; font-style: italic; margin-bottom: 30px;}
    
    /* Fiyatlandırma Kartları */
    .price-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #333;
        text-align: center;
        transition: transform 0.3s;
    }
    .price-card:hover {
        transform: scale(1.05);
        border: 1px solid #00F2C3;
    }
    .price-title { color: #00F2C3; font-size: 1.5rem; font-weight: bold; }
    .price-amount { color: #ffffff; font-size: 2.5rem; font-weight: 800; }
    .price-features { color: #cfd8dc; font-size: 1rem; line-height: 1.6; margin: 20px 0; }
    
    /* Metrikler */
    div[data-testid="stMetricValue"] {font-size: 1.8rem; color: #00F2C3;}
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ÇEKME FONKSİYONU ---
@st.cache_data(ttl=60)
def load_data():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Cloud Secrets veya Yerel Dosya Kontrolü
        if "gcp_service_account" in st.secrets:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
            
        client = gspread.authorize(creds)
        sheet = client.open("Crazytown_Journal").sheet1
        data = sheet.get_all_records()
        
        if not data: return pd.DataFrame()
        df = pd.DataFrame(data)
        
        if 'R_Kazanc' in df.columns:
            df['R_Kazanc'] = df['R_Kazanc'].astype(str).str.replace(',', '.')
            df['R_Kazanc'] = pd.to_numeric(df['R_Kazanc'], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

df = load_data()

# --- YAN MENÜ (NAVIGASYON) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
st.sidebar.title("Menü")
page = st.sidebar.radio("Sayfalar", ["📊 Canlı Performans", "💎 VIP Üyelik & Sinyaller", "📞 İletişim"])

st.sidebar.markdown("---")
st.sidebar.info("🚀 **Crazytown Bot** tarafından 7/24 taranan işlemler.")

# ==========================================
# SAYFA 1: CANLI PERFORMANS (JOURNAL)
# ==========================================
if page == "📊 Canlı Performans":
    st.markdown('<p class="main-title">🎯 CRAZYTOWN TRADER</p>', unsafe_allow_html=True)
    st.markdown('<p class="slogan">"Don\'t chase the market, let the market come to you. Sniper Mode: ON."</p>', unsafe_allow_html=True)

    if df.empty:
        st.info("📭 Veri bekleniyor...")
    else:
        # KPI
        total_trades = len(df)
        win_count = len(df[df['Sonuç'] == 'WIN'])
        win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0
        total_r = df['R_Kazanc'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam İşlem", f"{total_trades}")
        c2.metric("Win Rate (Başarı)", f"%{win_rate:.1f}")
        c3.metric("Net Kazanç (R)", f"{total_r:.2f}R")
        
        st.markdown("---")
        
        # Grafikler
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("📈 Kasa Büyümesi")
            df['Kümülatif'] = df['R_Kazanc'].cumsum()
            fig = px.area(df, x='Tarih', y='Kümülatif', markers=True, template="plotly_dark")
            fig.update_traces(line_color='#00F2C3', fill='tozeroy')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("🎯 Sonuç Dağılımı")
            fig_pie = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.5, 
                             color='Sonuç', color_discrete_map={'WIN':'#00cc96', 'LOSS':'#ef553b'}, template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)

        # Tablo
        st.subheader("📝 Şeffaf İşlem Listesi")
        def highlight(val):
            color = '#00F2C3' if val == 'WIN' else '#FF4B4B'
            return f'color: {color}; font-weight: bold'
        st.dataframe(df.style.applymap(highlight, subset=['Sonuç']), use_container_width=True, hide_index=True)

# ==========================================
# SAYFA 2: VIP ÜYELİK (SATIŞ SAYFASI)
# ==========================================
elif page == "💎 VIP Üyelik & Sinyaller":
    st.markdown('<p class="main-title">💎 VIP CLUB</p>', unsafe_allow_html=True)
    st.markdown('<p class="slogan">Grafik başında yaşlanma. Sinyal cebine gelsin, sen hayatını yaşa.</p>', unsafe_allow_html=True)
    
    st.write("")
    
    # Fiyatlandırma Kartları
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="price-card">
            <div class="price-title">BAŞLANGIÇ</div>
            <div class="price-amount">$30 <span style="font-size:1rem">/ay</span></div>
            <div class="price-features">
                ✅ Anlık Telegram Sinyalleri<br>
                ✅ 15dk Elite Setup<br>
                ✅ FVG & Fib Hedefleri<br>
                ❌ USDT.D Analizi
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("SATIN AL (Telegram)", "https://t.me/Orhan1909", use_container_width=True)

    with col2:
        st.markdown("""
        <div class="price-card" style="border: 2px solid #00F2C3;">
            <div class="price-title">🔥 PRO TRADER (Popüler)</div>
            <div class="price-amount">$75 <span style="font-size:1rem">/3 ay</span></div>
            <div class="price-features">
                ✅ <b>Her Şey Dahil</b><br>
                ✅ Anlık Sinyaller (Long/Short)<br>
                ✅ USDT.D Piyasa Yönü<br>
                ✅ Özel Destek
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("🔥 PRO OL (Telegram)", "https://t.me/Orhan1909", use_container_width=True)

    with col3:
        st.markdown("""
        <div class="price-card">
            <div class="price-title">LIFETIME</div>
            <div class="price-amount">$250</div>
            <div class="price-features">
                ✅ Ömür Boyu Erişim<br>
                ✅ Tüm Gelecek Güncellemeler<br>
                ✅ Bot Kurulum Desteği<br>
                ✅ VIP Grup Erişimi
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("İLETİŞİME GEÇ", "https://t.me/Orhan1909", use_container_width=True)

    st.divider()
    st.info("💡 **Nasıl Çalışır?** Ödeme yaptıktan sonra dekontu Telegram üzerinden iletin. Sizi anında VIP kanalına ve Sinyal Botuna ekleyelim.")

# ==========================================
# SAYFA 3: İLETİŞİM
# ==========================================
elif page == "📞 İletişim":
    st.header("📞 İletişim & Destek")
    st.write("Aklına takılan bir soru mu var? Veya ödeme yöntemleri hakkında bilgi mi almak istiyorsun?")
    
    st.markdown("""
    - **Telegram (Admin):** [@Orhan1909](https://t.me/Orhan1909)
    - **E-Posta:** orhanaliyev02@gmail.com
    """)
    
    st.success("Mesajlarına en geç 2 saat içinde dönüş yapılır.")
