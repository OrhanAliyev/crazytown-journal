import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==========================================
# 1. SAYFA YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="Crazytown Capital",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CORPORATE STEALTH CSS ---
st.markdown("""
    <style>
        /* GİZLİLİK */
        #MainMenu {visibility: hidden; display: none;}
        footer {visibility: hidden; display: none;}
        header {visibility: hidden; display: none;}
        .stDeployButton {display:none; visibility: hidden;}
        [data-testid="stToolbar"] {display: none; visibility: hidden;}
        [data-testid="stHeader"] {display: none; visibility: hidden;}
        
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }

        /* GENEL TASARIM */
        .stApp { background-color: #0b0c10; color: #c5c6c7; font-family: 'Inter', sans-serif; }
        h1, h2, h3, h4, h5 { color: #66fcf1; font-weight: 600; letter-spacing: 1px; }

        /* TABS */
        .stTabs [data-baseweb="tab-list"] { gap: 20px; background-color: transparent; border-bottom: 1px solid #1f2833; }
        .stTabs [data-baseweb="tab"] { height: 50px; border: none; color: #888; font-weight: 500; }
        .stTabs [data-baseweb="tab"]:hover { color: #66fcf1; }
        .stTabs [aria-selected="true"] { color: #66fcf1 !important; border-bottom: 2px solid #66fcf1 !important; }

        /* KPI KARTLARI */
        .metric-container {
            background-color: #1f2833; border-radius: 8px; padding: 20px; text-align: center;
            border: 1px solid #2d3845; transition: transform 0.2s ease;
        }
        .metric-container:hover { transform: translateY(-2px); border-color: #66fcf1; }
        .metric-value { font-size: 2rem; font-weight: 700; color: #fff; margin-bottom: 5px; }
        .metric-label { font-size: 0.8rem; color: #8892b0; text-transform: uppercase; letter-spacing: 1.5px; }

        /* FİYATLANDIRMA */
        .pricing-card {
            background-color: #1f2833; border-radius: 12px; padding: 40px 20px; text-align: center;
            border: 1px solid #2d3845; height: 100%; transition: all 0.3s ease;
        }
        .pricing-card:hover { border-color: #66fcf1; transform: translateY(-5px); }
        .plan-name { color: #66fcf1; font-size: 1.1rem; font-weight: 700; letter-spacing: 2px; margin-bottom: 15px; }
        .price-tag { font-size: 2.5rem; font-weight: 700; color: #fff; margin: 20px 0; }
        .price-period { font-size: 1rem; color: #888; }
        .feature-list { text-align: left; margin-left: 15%; color: #c5c6c7; font-size: 0.9rem; line-height: 2.2; margin-bottom: 30px; }
        
        /* BUTONLAR */
        .custom-btn {
            display: inline-block; padding: 12px 30px; color: #0b0c10; background-color: #66fcf1;
            border-radius: 4px; text-decoration: none; font-weight: 600; width: 100%; text-align: center;
        }
        .custom-btn:hover { background-color: #45a29e; color: #fff; }
        .custom-btn-outline { background-color: transparent; border: 1px solid #66fcf1; color: #66fcf1; }
        .custom-btn-outline:hover { background-color: #66fcf1; color: #0b0c10; }

        .stDataFrame { border: 1px solid #2d3845; }
        [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VERİ BAĞLANTISI (HATA KORUMALI)
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

tab1, tab2, tab3 = st.tabs(["PERFORMANCE", "MEMBERSHIP", "CONTACT"])

# --- TAB 1: PERFORMANCE ---
with tab1:
    if df.empty:
        st.info("System initializing. Waiting for data feed...")
    else:
        # --- GÜVENLİ FİLTRELEME (CRASH FIX) ---
        with st.expander("FILTER DATA"):
            c1, c2 = st.columns(2)
            
            # Coin Filtresi (Güvenli)
            coin_options = ["All Assets"]
            if 'Coin' in df.columns:
                coin_options += list(df['Coin'].unique())
            sel_coin = c1.selectbox("Asset", coin_options)

            # Setup Filtresi (Güvenli)
            setup_options = ["All Strategies"]
            if 'Setup' in df.columns:
                setup_options += list(df['Setup'].unique())
            sel_setup = c2.selectbox("Strategy", setup_options)
            
            # Filtreleri Uygula
            if sel_coin != "All Assets" and 'Coin' in df.columns:
                df = df[df['Coin'] == sel_coin]
            
            # BURADA HATA VARDI - DÜZELTİLDİ
            if sel_setup != "All Strategies" and 'Setup' in df.columns:
                df = df[df['Setup'] == sel_setup]

        st.write("")

        # KPI
        total = len(df)
        win = len(df[df['Sonuç'] == 'WIN'])
        rate = (win / total * 100) if total > 0 else 0
        net = df['R_Kazanc'].sum()
        pf = (df[df['R_Kazanc'] > 0]['R_Kazanc'].sum() / abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum())) if abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum()) > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f'<div class="metric-container"><div class="metric-value">{total}</div><div class="metric-label">TOTAL TRADES</div></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric-container"><div class="metric-value">{rate:.1f}%</div><div class="metric-label">WIN RATE</div></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="metric-container"><div class="metric-value" style="color:{"#66fcf1" if net>0 else "#ff4b4b"}">{net:.2f}R</div><div class="metric-label">NET RETURN</div></div>', unsafe_allow_html=True)
        col4.markdown(f'<div class="metric-container"><div class="metric-value">{pf:.2f}</div><div class="metric-label">PROFIT FACTOR</div></div>', unsafe_allow_html=True)

        st.write(""); st.write("")

        # Charts
        c_left, c_right = st.columns([2, 1])
        
        with c_left:
            st.markdown("##### EQUITY CURVE")
            df['Cum'] = df['R_Kazanc'].cumsum()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Tarih'], y=df['Cum'], mode='lines', fill='tozeroy', line=dict(color='#66fcf1', width=2), fillcolor='rgba(102, 252, 241, 0.1)'))
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=20, b=0), height=320, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1f2833'))
            st.plotly_chart(fig, use_container_width=True)

        with c_right:
            st.markdown("##### DISTRIBUTION")
            fig_pie = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.7, color='Sonuç', color_discrete_map={'WIN':'#66fcf1', 'LOSS':'#ff4b4b'})
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(l=20, r=20, t=20, b=20), height=320, annotations=[dict(text=f"{rate:.0f}%", x=0.5, y=0.5, font_size=24, showarrow=False, font_color="white", font_family="Arial")])
            st.plotly_chart(fig_pie, use_container_width=True)

        # Table
        st.markdown("##### TRADE LOG")
        def style_df(row):
            color = '#66fcf1' if row['Sonuç'] == 'WIN' else '#ff4b4b'
            return [f'color: {color}; font-weight: 600' if col == 'Sonuç' else 'color: #c5c6c7' for col in row.index]
        
        st.dataframe(
            df.style.apply(style_df, axis=1), 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Tarih": "DATE", "Coin": "ASSET", "Yön": "SIDE", 
                "Giriş": st.column_config.NumberColumn("ENTRY", format="$%.4f"),
                "R_Kazanc": st.column_config.NumberColumn("RETURN (R)", format="%.2f R"),
                "Sonuç": "RESULT"
            }
        )

# --- TAB 2: MEMBERSHIP ---
with tab2:
    st.write(""); st.write("")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <div class="plan-name">STARTER</div>
            <div class="plan-price">$30<span style="font-size:1rem;color:#888">/mo</span></div>
            <div class="feature-list">
                ✓ Telegram Channel Access<br>✓ 15m Elite Setups<br>✓ FVG & Fib Targets<br>✓ Support 24/7
            </div>
            <a href="https://t.me/Orhan1909" target="_blank" class="custom-btn custom-btn-outline">SELECT PLAN</a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="pricing-card" style="border-color: #66fcf1;">
            <div class="plan-name">PROFESSIONAL</div>
            <div class="plan-price">$75<span style="font-size:1rem;color:#888">/qtr</span></div>
            <div class="feature-list">
                ✓ <b>All Starter Features</b><br>✓ Real-time Signals<br>✓ Market Direction (USDT.D)<br>✓ Priority Support
            </div>
            <a href="https://t.me/Orhan1909" target="_blank" class="custom-btn">MOST POPULAR</a>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="pricing-card">
            <div class="plan-name">LIFETIME</div>
            <div class="plan-price">$250<span style="font-size:1rem;color:#888">/once</span></div>
            <div class="feature-list">
                ✓ <b>Lifetime Access</b><br>✓ Future Updates Included<br>✓ Bot Setup Assistance<br>✓ Private Group
            </div>
            <a href="https://t.me/Orhan1909" target="_blank" class="custom-btn custom-btn-outline">CONTACT SALES</a>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 3: CONTACT ---
with tab3:
    st.write(""); st.write("")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        #### TELEGRAM SUPPORT
        Direct line for membership inquiries and support.
        <br><br>
        <a href="https://t.me/Orhan1909" class="custom-btn">OPEN CHAT</a>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        #### EMAIL INQUIRIES
        For business partnerships and detailed questions.
        <br><br>
        <div style="background:#1f2833; padding:12px; border-radius:4px; text-align:center; color:#fff; border:1px solid #2d3845;">
        orhanaliyev02@gmail.com
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #45a29e; font-size: 0.8rem;'>© 2025 Crazytown Capital. All rights reserved.</p>", unsafe_allow_html=True)
