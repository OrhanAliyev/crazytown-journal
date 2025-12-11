import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==========================================
# 1. SAYFA VE STİL YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="Crazytown Public Journal",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ULTRA PRO CSS (GÖRSEL MAKYAJ) ---
st.markdown("""
    <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        h1, h2, h3 {
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 800;
            color: #FFFFFF;
        }
        .metric-card {
            background: #191c24;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: #00F2C3;
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #00F2C3;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #cfd8dc;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .pricing-card {
            background: linear-gradient(145deg, #1e232e, #161920);
            border-radius: 16px;
            padding: 30px;
            margin: 10px;
            border: 1px solid #333;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .pricing-card.featured {
            border: 2px solid #00F2C3;
            box-shadow: 0 0 20px rgba(0, 242, 195, 0.2);
        }
        .price-tag {
            font-size: 2.5rem;
            font-weight: 800;
            color: #fff;
            margin: 15px 0;
        }
        .price-period {
            font-size: 1rem;
            color: #888;
        }
        .stDataFrame {
            border: 1px solid #333;
            border-radius: 10px;
        }
        /* Gizlilik */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VERİ BAĞLANTISI (GOOGLE SHEETS)
# ==========================================
@st.cache_data(ttl=60)
def load_data():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
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
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# ==========================================
# 3. YAN MENÜ VE FİLTRELER
# ==========================================
st.sidebar.markdown("## ⚡ KONTROL PANELİ")
page = st.sidebar.radio("Navigasyon", ["📊 Dashboard (Canlı)", "💎 VIP Club", "📞 İletişim"], index=0)

st.sidebar.markdown("---")

if page == "📊 Dashboard (Canlı)" and not df.empty:
    st.sidebar.markdown("### 🔍 Filtreler")
    coin_list = ["Tümü"] + list(df['Coin'].unique())
    selected_coin = st.sidebar.selectbox("Coin Seç:", coin_list)
    
    setup_list = ["Tümü"] + list(df['Setup'].unique()) if 'Setup' in df.columns else ["Tümü"]
    selected_setup = st.sidebar.selectbox("Setup Tipi:", setup_list)
    
    if selected_coin != "Tümü":
        df = df[df['Coin'] == selected_coin]
    if selected_setup != "Tümü":
        df = df[df['Setup'] == selected_setup]

# ==========================================
# SAYFA 1: DASHBOARD
# ==========================================
if page == "📊 Dashboard (Canlı)":
    
    col_logo, col_text = st.columns([1, 5])
    with col_text:
        st.markdown("# 🎯 CRAZYTOWN TRADER")
        st.markdown('#### *"Don\'t chase the market, let the market come to you. Sniper Mode: ON."*')
    
    st.markdown("---")

    if df.empty:
        st.warning("⚠️ Veri bekleniyor. Lütfen veritabanı bağlantısını kontrol edin.")
    else:
        # KPI
        total_trades = len(df)
        win_trades = len(df[df['Sonuç'] == 'WIN'])
        loss_trades = len(df[df['Sonuç'] == 'LOSS'])
        win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0
        net_r = df['R_Kazanc'].sum()
        
        gross_profit = df[df['R_Kazanc'] > 0]['R_Kazanc'].sum()
        gross_loss = abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum())
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 99.9

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="metric-card"><div class="metric-value">{total_trades}</div><div class="metric-label">TOPLAM İŞLEM</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="metric-value">%{win_rate:.1f}</div><div class="metric-label">BAŞARI ORANI</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><div class="metric-value" style="color: {"#00F2C3" if net_r > 0 else "#FF4B4B"}">{net_r:.2f}R</div><div class="metric-label">NET KAZANÇ</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-card"><div class="metric-value">{profit_factor:.2f}</div><div class="metric-label">PROFIT FACTOR</div></div>', unsafe_allow_html=True)

        st.write("")
        st.write("")

        g1, g2 = st.columns([2, 1])

        with g1:
            st.subheader("📈 Kasa Büyümesi (R Eğrisi)")
            df['Kümülatif'] = df['R_Kazanc'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['Tarih'], y=df['Kümülatif'],
                mode='lines+markers',
                fill='tozeroy',
                line=dict(color='#00F2C3', width=3),
                marker=dict(size=8, color='#131722', line=dict(color='#00F2C3', width=2))
            ))
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=20),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)

        with g2:
            st.subheader("🎯 Performans Dağılımı")
            # DÜZELTME BURADA YAPILDI: px.donut yerine px.pie
            fig_pie = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.6,
                               color='Sonuç', color_discrete_map={'WIN':'#00F2C3', 'LOSS':'#FF4B4B'})
            
            fig_pie.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                annotations=[dict(text=f"%{win_rate:.0f}", x=0.5, y=0.5, font_size=24, showarrow=False, font_color="white")],
                margin=dict(l=20, r=20, t=20, b=20),
                height=350
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("📋 Son İşlem Detayları")
        
        def style_dataframe(row):
            color = '#00F2C3' if row['Sonuç'] == 'WIN' else '#FF4B4B'
            return [f'color: {color}; font-weight: bold' if col == 'Sonuç' else '' for col in row.index]

        st.dataframe(
            df.style.apply(style_dataframe, axis=1),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Tarih": "📅 Tarih",
                "Coin": "🪙 Sembol",
                "Yön": "↕️ Yön",
                "Giriş": st.column_config.NumberColumn("Giriş", format="$%.4f"),
                "R_Kazanc": st.column_config.NumberColumn("Kazanılan R", format="%.2f R"),
                "Sonuç": "Sonuç"
            }
        )

# ==========================================
# SAYFA 2: VIP ÜYELİK
# ==========================================
elif page == "💎 VIP Club":
    st.markdown("<h1 style='text-align: center; color: #00F2C3;'>💎 CRAZYTOWN VIP CLUB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Analizle vakit kaybetme. Profesyonel sinyalleri cebine al.</p>", unsafe_allow_html=True)
    
    st.write("")
    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="pricing-card">
            <h3 style="color:#cfd8dc">BAŞLANGIÇ</h3>
            <div class="price-tag">$30</div>
            <div class="price-period">Aylık</div>
            <hr style="border-color: #333;">
            <p>✅ Telegram Sinyal Kanalı</p>
            <p>✅ 15dk Elite Setup'lar</p>
            <p>✅ FVG & Fib Hedefleri</p>
            <p style="color:#666">❌ USDT.D Analizi</p>
            <br>
            <a href="https://t.me/Orhan1909" target="_blank" style="text-decoration: none;">
                <div style="background:#333; color:white; padding:10px; border-radius:5px; font-weight:bold;">SEÇ & İLETİŞİME GEÇ</div>
            </a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="pricing-card featured">
            <div style="position:absolute; top:0; right:0; background:#00F2C3; color:black; padding:5px 15px; font-weight:bold; font-size:0.8rem; border-bottom-left-radius:10px;">POPÜLER</div>
            <h3 style="color:#00F2C3">PRO TRADER</h3>
            <div class="price-tag">$75</div>
            <div class="price-period">3 Aylık</div>
            <hr style="border-color: #333;">
            <p>✅ <b>HER ŞEY DAHİL</b></p>
            <p>✅ Anlık Sinyaller (L/S)</p>
            <p>✅ USDT.D Piyasa Yönü</p>
            <p>✅ Özel Destek Hattı</p>
            <br>
            <a href="https://t.me/Orhan1909" target="_blank" style="text-decoration: none;">
                <div style="background:#00F2C3; color:black; padding:10px; border-radius:5px; font-weight:bold;">🔥 HEMEN KATIL</div>
            </a>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="pricing-card">
            <h3 style="color:#cfd8dc">LIFETIME</h3>
            <div class="price-tag">$250</div>
            <div class="price-period">Tek Seferlik</div>
            <hr style="border-color: #333;">
            <p>✅ <b>ÖMÜR BOYU ERİŞİM</b></p>
            <p>✅ Gelecek Tüm Güncellemeler</p>
            <p>✅ Bot Kurulum Desteği</p>
            <p>✅ VIP Gruba Doğrudan Giriş</p>
            <br>
            <a href="https://t.me/Orhan1909" target="_blank" style="text-decoration: none;">
                <div style="background:#333; color:white; padding:10px; border-radius:5px; font-weight:bold;">İLETİŞİME GEÇ</div>
            </a>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# SAYFA 3: İLETİŞİM
# ==========================================
elif page == "📞 İletişim":
    st.header("📞 Bizimle İletişime Geçin")
    st.info("Aklına takılan bir soru mu var? Ödeme yöntemleri hakkında bilgi mi almak istiyorsun?")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### 📨 Telegram Destek
        En hızlı dönüş için Telegram'dan yazabilirsin.
        **👉 [@Orhan1909](https://t.me/Orhan1909)**
        """)
    with c2:
        st.markdown("""
        ### 📧 E-Posta
        Kurumsal veya detaylı soruların için:
        **👉 orhanaliyev02@gmail.com**
        """)

# Alt Bilgi
st.sidebar.markdown("---")
st.sidebar.caption("© 2025 Crazytown Trader. All rights reserved.")
