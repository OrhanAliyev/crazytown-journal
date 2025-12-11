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
    page_title="Crazytown Capital",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- NÜKLEER GİZLİLİK CSS (EN GÜÇLÜ SÜRÜM) ---
st.markdown("""
    <style>
        /* 1. Ana Menü ve Header Gizleme */
        #MainMenu {visibility: hidden; display: none !important;}
        header {visibility: hidden; display: none !important;}
        [data-testid="stHeader"] {display: none !important;}
        
        /* 2. Alt Bilgi (Footer) ve 'Created by' Gizleme */
        footer {visibility: hidden; display: none !important;}
        .stFooter {display: none !important;}
        
        /* 3. 'Manage App' Butonunu Gizleme */
        .viewerBadge_container__1QSob {display: none !important;}
        .stApp > header {display: none !important;}
        
        /* 4. Toolbar ve Deploy Butonları */
        [data-testid="stToolbar"] {display: none !important;}
        .stDeployButton {display:none !important;}
        
        /* 5. Sayfa Üst Boşluğunu Kapat */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
        }

        /* 6. GENEL TASARIM */
        .stApp {
            background-color: #0E1117;
            color: #E0E0E0;
            font-family: 'Segoe UI', sans-serif;
        }
        
        /* Geriye kalan tasarım kodları... */
        .metric-card {
            background: #161920;
            border-left: 4px solid #00F2C3;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            text-align: center;
        }
        .metric-value { font-size: 1.8rem; font-weight: 700; color: #FFFFFF; }
        .metric-label { font-size: 0.85rem; color: #A0A0A0; font-weight: 600; margin-top: 5px; }

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
        .pricing-header { font-size: 1.2rem; color: #00F2C3; font-weight: 700; margin-bottom: 10px; }
        .price-period { font-size: 1rem; color: #888; }
        .feature-list { text-align: left; margin: 20px 0; color: #CCC; font-size: 0.95rem; line-height: 1.8; }
        
        .cta-button {
            display: block; width: 100%; padding: 12px;
            background: transparent; color: #00F2C3;
            border: 1px solid #00F2C3; border-radius: 4px;
            text-align: center; text-decoration: none; font-weight: bold;
        }
        .cta-button:hover { background: #00F2C3; color: #0E1117; }
        .cta-button-primary { background: #00F2C3; color: #0E1117; border: none; }
        .cta-button-primary:hover { background: #00D2A8; }
        
        .stDataFrame { border: 1px solid #333; }
        
        /* Yan menü gizli kalsın */
        [data-testid="stSidebar"] {display: none;}
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
# 3. İÇERİK
# ==========================================
st.markdown("<h1 style='text-align: center; font-size: 2.5rem; color: #FFFFFF;'>CRAZYTOWN CAPITAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8892b0; margin-top: -10px; font-style: italic;'>Proprietary Trading & Analytics</p>", unsafe_allow_html=True)
st.write(""); st.write("")

# ÜST MENÜ (TABS)
tab1, tab2, tab3 = st.tabs(["PERFORMANCE", "MEMBERSHIP", "CONTACT"])

# --- TAB 1: PERFORMANCE ---
with tab1:
    if df.empty:
        st.warning("System initializing...")
    else:
        # FİLTRELER
        with st.expander("FILTER DATA"):
            c1, c2 = st.columns(2)
            coin_options = ["All Assets"]; setup_options = ["All Strategies"]
            if 'Coin' in df.columns: coin_options += list(df['Coin'].unique())
            if 'Setup' in df.columns: setup_options += list(df['Setup'].unique())
            
            sel_coin = c1.selectbox("Asset", coin_options)
            sel_setup = c2.selectbox("Strategy", setup_options)
            
            if sel_coin != "All Assets" and 'Coin' in df.columns: df = df[df['Coin'] == sel_coin]
            if sel_setup != "All Strategies" and 'Setup' in df.columns: df = df[df['Setup'] == sel_setup]

        st.write("")

        # KPI
        total = len(df)
        win = len(df[df['Sonuç'] == 'WIN'])
        rate = (win / total * 100) if total > 0 else 0
        net = df['R_Kazanc'].sum()
        pf = (df[df['R_Kazanc'] > 0]['R_Kazanc'].sum() / abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum())) if abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum()) > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">TOTAL TRADES</div></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric-card"><div class="metric-value">{rate:.1f}%</div><div class="metric-label">WIN RATE</div></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{"#00F2C3" if net>0 else "#ff4b4b"}">{net:.2f}R</div><div class="metric-label">NET RETURN</div></div>', unsafe_allow_html=True)
        col4.markdown(f'<div class="metric-card"><div class="metric-value">{pf:.2f}</div><div class="metric-label">PROFIT FACTOR</div></div>', unsafe_allow_html=True)

        st.write(""); st.write("")

        g1, g2 = st.columns([2, 1])
        with g1:
            st.markdown("##### EQUITY CURVE")
            df['Cum'] = df['R_Kazanc'].cumsum()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Tarih'], y=df['Cum'], mode='lines', fill='tozeroy', line=dict(color='#00F2C3', width=2), fillcolor='rgba(0, 242, 195, 0.1)'))
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=20, b=0), height=320, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1f2833'))
            st.plotly_chart(fig, use_container_width=True)

        with g2:
            st.markdown("##### DISTRIBUTION")
            fig_pie = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.7, color='Sonuç', color_discrete_map={'WIN':'#00F2C3', 'LOSS':'#FF4B4B'})
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(l=20, r=20, t=20, b=20), height=320, annotations=[dict(text=f"{rate:.0f}%", x=0.5, y=0.5, font_size=24, showarrow=False, font_color="white", font_family="Arial")])
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("##### TRADE LOG")
        def style_df(row):
            color = '#00F2C3' if row['Sonuç'] == 'WIN' else '#FF4B4B'
            return [f'color: {color}; font-weight: 600' if col == 'Sonuç' else 'color: #c5c6c7' for col in row.index]
        
        st.dataframe(df.style.apply(style_df, axis=1), use_container_width=True, hide_index=True, column_config={"Tarih": "DATE", "Coin": "ASSET", "Yön": "SIDE", "Giriş": st.column_config.NumberColumn("ENTRY", format="$%.4f"), "R_Kazanc": st.column_config.NumberColumn("RETURN (R)", format="%.2f R"), "Sonuç": "RESULT"})

# --- TAB 2: MEMBERSHIP ---
with tab2:
    st.write(""); st.write("")
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown("""<div class="pricing-card"><div class="pricing-header">STARTER</div><div class="price-tag">$30</div><div class="price-period">Monthly Billed</div><div class="feature-list">✓ Telegram Signal Access<br>✓ 15m Elite Setups<br>✓ FVG & Fib Targets<br><span style="color:#555">✕ USDT.D Analysis</span></div><a href="https://t.me/Orhan1909" target="_blank" class="cta-button">GET STARTED</a></div>""", unsafe_allow_html=True)
    with col2: st.markdown("""<div class="pricing-card featured"><div class="pricing-header">PROFESSIONAL</div><div class="price-tag">$75</div><div class="price-period">Quarterly Billed</div><div class="feature-list">✓ <b>All Starter Features</b><br>✓ Real-time Signals<br>✓ Market Direction (USDT.D)<br>✓ Priority Support</div><a href="https://t.me/Orhan1909" target="_blank" class="cta-button cta-button-primary">BECOME A PRO</a></div>""", unsafe_allow_html=True)
    with col3: st.markdown("""<div class="pricing-card"><div class="pricing-header">LIFETIME</div><div class="price-tag">$250</div><div class="price-period">One-time Payment</div><div class="feature-list">✓ <b>Lifetime Access</b><br>✓ All Future Updates<br>✓ Bot Setup Assistance<br>✓ Private Group Access</div><a href="https://t.me/Orhan1909" target="_blank" class="cta-button">CONTACT SALES</a></div>""", unsafe_allow_html=True)

# --- TAB 3: CONTACT ---
with tab3:
    st.write(""); st.write("")
    c1, c2 = st.columns(2)
    with c1: st.markdown("""### 📨 Telegram Support\nFor instant assistance:\n<a href="https://t.me/Orhan1909" class="cta-button">OPEN TELEGRAM</a>""", unsafe_allow_html=True)
    with c2: st.markdown("""### 📧 Email\nFor business partnerships:\n**orhanaliyev02@gmail.com**""")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #45a29e; font-size: 0.8rem;'>© 2025 Crazytown Capital. All rights reserved.</p>", unsafe_allow_html=True)
