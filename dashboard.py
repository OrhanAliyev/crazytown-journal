import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==========================================
# 1. SAYFA VE GİZLİLİK AYARLARI
# ==========================================
st.set_page_config(
    page_title="Crazytown Capital",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS: KODU GİZLE, MENÜYÜ GİZLE, TASARIMI YAP ---
st.markdown("""
    <style>
        /* 1. GİZLİLİK (KODU KİMSE GÖREMEZ) */
        #MainMenu {visibility: hidden; display: none;} /* Sağ üst 3 nokta */
        footer {visibility: hidden; display: none;}    /* Alt bilgi */
        header {visibility: hidden; display: none;}    /* Üst renkli şerit */
        .stDeployButton {display:none; visibility: hidden;} /* Deploy butonu */
        
        /* Yan Menüyü Tamamen Yok Et (Artık Üst Menü Var) */
        [data-testid="stSidebar"] {display: none;}
        
        /* 2. GENEL TASARIM */
        .stApp {
            background-color: #0E1117;
            color: #E0E0E0;
            margin-top: -50px;
        }
        
        /* Sekme (Tab) Tasarımı */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #0E1117;
            padding-top: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #161920;
            border-radius: 5px;
            color: #fff;
            font-weight: bold;
            border: 1px solid #333;
        }
        .stTabs [aria-selected="true"] {
            background-color: #00F2C3 !important;
            color: #000 !important;
            border: 1px solid #00F2C3 !important;
        }

        /* KPI Kartları */
        .metric-card {
            background: #161920;
            border-left: 4px solid #00F2C3;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .metric-value { font-size: 1.8rem; font-weight: 700; color: #FFFFFF; }
        .metric-label { font-size: 0.85rem; color: #A0A0A0; font-weight: 600; margin-top: 5px; }

        /* Fiyatlandırma Kartları */
        .pricing-card {
            background: #161920;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 30px;
            text-align: center;
            transition: transform 0.3s;
        }
        .pricing-card:hover { transform: scale(1.02); border-color: #00F2C3; }
        .price-tag { font-size: 2.5rem; font-weight: 800; color: #fff; margin: 15px 0; }
        
        /* Butonlar */
        .cta-button {
            display: block; width: 100%; padding: 12px;
            background: transparent; color: #00F2C3;
            border: 1px solid #00F2C3; border-radius: 4px;
            text-align: center; text-decoration: none; font-weight: bold;
        }
        .cta-button:hover { background: #00F2C3; color: #000; }
        
        .stDataFrame { border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VERİ BAĞLANTISI
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
    except: return pd.DataFrame()

df = load_data()

# ==========================================
# 3. ÜST MENÜ VE İÇERİK
# ==========================================

# Başlık
st.markdown("<h1 style='text-align: center; color: #00F2C3;'>🎯 CRAZYTOWN CAPITAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ccc; margin-top: -15px;'><i>\"Don't chase the market, let the market come to you. Sniper Mode: ON.\"</i></p>", unsafe_allow_html=True)
st.write("")

# ÜST MENÜ (TABS)
tab1, tab2, tab3 = st.tabs(["📊 PERFORMANCE", "💎 VIP ACCESS", "📞 CONTACT"])

# --- TAB 1: PERFORMANS DASHBOARD ---
with tab1:
    if df.empty:
        st.warning("⚠️ Veri bağlantısı bekleniyor...")
    else:
        # Filtreleme (Expander içinde gizli)
        with st.expander("🔍 Filtrele (Asset / Setup)"):
            c_fil, s_fil = st.columns(2)
            sel_coin = c_fil.selectbox("Coin:", ["All"] + list(df['Coin'].unique()))
            sel_setup = s_fil.selectbox("Setup:", ["All"] + list(df['Setup'].unique()) if 'Setup' in df.columns else ["All"])
            
            if sel_coin != "All": df = df[df['Coin'] == sel_coin]
            if sel_setup != "All": df = df[df['Setup'] == sel_setup]

        st.write("")

        # KPI
        total = len(df)
        win = len(df[df['Sonuç'] == 'WIN'])
        rate = (win / total * 100) if total > 0 else 0
        net = df['R_Kazanc'].sum()
        pf = (df[df['R_Kazanc'] > 0]['R_Kazanc'].sum() / abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum())) if abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum()) > 0 else 99

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">TOTAL TRADES</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="metric-value">{rate:.1f}%</div><div class="metric-label">WIN RATE</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{"#00F2C3" if net>0 else "#FF4B4B"}">{net:.2f}R</div><div class="metric-label">NET RETURN</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-card"><div class="metric-value">{pf:.2f}</div><div class="metric-label">PROFIT FACTOR</div></div>', unsafe_allow_html=True)

        st.write("")

        # Grafikler
        g1, g2 = st.columns([2, 1])
        with g1:
            st.markdown("##### Equity Curve")
            df['Cum'] = df['R_Kazanc'].cumsum()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Tarih'], y=df['Cum'], mode='lines', fill='tozeroy', line=dict(color='#00F2C3', width=2), fillcolor='rgba(0, 242, 195, 0.1)'))
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0), height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with g2:
            st.markdown("##### Win / Loss")
            fig_pie = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.7, color='Sonuç', color_discrete_map={'WIN':'#00F2C3', 'LOSS':'#FF4B4B'})
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=True, margin=dict(l=0, r=0, t=30, b=0), height=300, 
                                  annotations=[dict(text=f"{rate:.0f}%", x=0.5, y=0.5, font_size=20, showarrow=False, font_color="white")])
            st.plotly_chart(fig_pie, use_container_width=True)

        # Tablo
        st.markdown("##### Trade History")
        def style_df(row):
            color = '#00F2C3' if row['Sonuç'] == 'WIN' else '#FF4B4B'
            return [f'color: {color}; font-weight: bold' if col == 'Sonuç' else 'color: #DDD' for col in row.index]
        
        st.dataframe(df.style.apply(style_df, axis=1), use_container_width=True, hide_index=True)

# --- TAB 2: VIP ÜYELİK ---
with tab2:
    st.write(""); st.write("")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""<div class="pricing-card"><h3 style="color:#cfd8dc">STARTER</h3><div class="price-tag">$30</div><p style="color:#888">Monthly</p><hr style="border-color:#333"><p>✓ Telegram Signals</p><p>✓ 15m Elite Setups</p><p>✓ FVG Targets</p><br><a href="https://t.me/Orhan1909" target="_blank" class="cta-button">GET STARTED</a></div>""", unsafe_allow_html=True)
    
    with c2:
        st.markdown("""<div class="pricing-card" style="border: 2px solid #00F2C3"><h3 style="color:#00F2C3">PROFESSIONAL</h3><div class="price-tag">$75</div><p style="color:#888">Quarterly</p><hr style="border-color:#333"><p>✓ <b>All Features</b></p><p>✓ Real-time Signals</p><p>✓ USDT.D Analysis</p><br><a href="https://t.me/Orhan1909" target="_blank" class="cta-button" style="background:#00F2C3; color:black;">BECOME A PRO</a></div>""", unsafe_allow_html=True)
    
    with c3:
        st.markdown("""<div class="pricing-card"><h3 style="color:#cfd8dc">LIFETIME</h3><div class="price-tag">$250</div><p style="color:#888">One-time</p><hr style="border-color:#333"><p>✓ <b>Lifetime Access</b></p><p>✓ All Updates</p><p>✓ Private Group</p><br><a href="https://t.me/Orhan1909" target="_blank" class="cta-button">CONTACT SALES</a></div>""", unsafe_allow_html=True)

# --- TAB 3: İLETİŞİM ---
with tab3:
    st.write("")
    c1, c2 = st.columns(2)
    with c1: st.markdown("""### 📨 Telegram Support\nFor instant assistance:\n<a href="https://t.me/Orhan1909" class="cta-button">OPEN TELEGRAM</a>""", unsafe_allow_html=True)
    with c2: st.markdown("""### 📧 Email\nFor business partnerships:\n**orhanaliyev02@gmail.com**""")

st.markdown("---")
st.caption("© 2025 Crazytown Capital.")
