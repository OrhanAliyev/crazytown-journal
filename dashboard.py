import streamlit as st
import streamlit.components.v1 as components
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

# --- NÜKLEER GİZLİLİK CSS (FULL STEALTH) ---
st.markdown("""
    <style>
        /* GİZLİLİK */
        div[class^="viewerBadge_container"], .viewerBadge_container__1QSob {display: none !important;}
        #MainMenu, header, footer, .stDeployButton, [data-testid="stToolbar"] {display: none !important;}
        .block-container {padding-top: 0rem !important; padding-bottom: 2rem !important;}

        /* GENEL TASARIM */
        .stApp {background-color: #0b0c10; color: #c5c6c7; font-family: 'Inter', sans-serif;}
        
        /* TABS */
        .stTabs [data-baseweb="tab-list"] {gap: 20px; border-bottom: 1px solid #1f2833; padding-top: 10px;}
        .stTabs [data-baseweb="tab"] {height: 50px; color: #888; font-weight: 500; border: none;}
        .stTabs [data-baseweb="tab"]:hover {color: #66fcf1;}
        .stTabs [aria-selected="true"] {color: #66fcf1 !important; border-bottom: 2px solid #66fcf1 !important;}

        /* KARTLAR */
        .metric-container {background-color: #1f2833; border-radius: 8px; padding: 20px; text-align: center; border: 1px solid #2d3845; transition: transform 0.2s ease;}
        .metric-container:hover {transform: translateY(-2px); border-color: #66fcf1;}
        .metric-value {font-size: 2rem; font-weight: 700; color: #fff; margin-bottom: 5px;}
        .metric-label {font-size: 0.8rem; color: #8892b0; text-transform: uppercase; letter-spacing: 1.5px;}

        .pricing-card {background-color: #1f2833; border-radius: 12px; padding: 40px 20px; text-align: center; border: 1px solid #2d3845; height: 100%; transition: all 0.3s ease;}
        .pricing-card:hover {border-color: #66fcf1; transform: translateY(-5px);}
        .plan-name {color: #66fcf1; font-size: 1.1rem; font-weight: 700; letter-spacing: 2px; margin-bottom: 15px;}
        .plan-price {color: #fff; font-size: 2.5rem; font-weight: 700; margin-bottom: 30px;}
        
        /* ÖZEL BANNER */
        .promo-banner {
            background: linear-gradient(90deg, #1f2833 0%, #0b0c10 100%);
            border: 1px solid #66fcf1; color: #fff; padding: 15px; border-radius: 8px;
            text-align: center; margin-bottom: 20px; font-weight: bold;
        }

        .custom-btn {display: inline-block; padding: 12px 30px; color: #0b0c10; background-color: #66fcf1; border-radius: 4px; text-decoration: none; font-weight: 600; width: 100%; text-align: center;}
        .custom-btn:hover {background-color: #45a29e; color: #fff;}
        .custom-btn-outline {background-color: transparent; border: 1px solid #66fcf1; color: #66fcf1;}
        .custom-btn-outline:hover {background-color: #66fcf1; color: #0b0c10;}

        .stDataFrame {border: 1px solid #2d3845;}
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
# 3. HEADER & TICKER TAPE
# ==========================================
components.html("""
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {
  "symbols": [{"proName": "BINANCE:BTCUSDT", "title": "Bitcoin"}, {"proName": "BINANCE:ETHUSDT", "title": "Ethereum"}, {"proName": "BINANCE:SOLUSDT", "title": "Solana"}, {"description": "USDT.D", "proName": "CRYPTOCAP:USDT.D"}],
  "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": false, "displayMode": "adaptive", "locale": "en"
}
  </script>
</div>
""", height=50)

st.write("")
st.markdown("<h1 style='text-align: center; font-size: 3rem; color: #FFFFFF;'>CRAZYTOWN CAPITAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #66fcf1; margin-top: -15px; letter-spacing: 2px; font-size: 0.9rem;'>ALGORITHMIC TRADING SYSTEMS</p>", unsafe_allow_html=True)
st.write("")

tab1, tab2, tab3 = st.tabs(["PERFORMANCE", "MEMBERSHIP", "CONTACT"])

# ==========================================
# TAB 1: PERFORMANCE (DASHBOARD)
# ==========================================
with tab1:
    if df.empty:
        st.warning("System initializing...")
    else:
        # KPI & GRAFİKLER (Mevcut Kodlar)
        total = len(df)
        win = len(df[df['Sonuç'] == 'WIN'])
        rate = (win / total * 100) if total > 0 else 0
        net_r_total = df['R_Kazanc'].sum()
        pf = (df[df['R_Kazanc'] > 0]['R_Kazanc'].sum() / abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum())) if abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum()) > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f'<div class="metric-container"><div class="metric-value">{total}</div><div class="metric-label">TOTAL TRADES</div></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric-container"><div class="metric-value">{rate:.1f}%</div><div class="metric-label">WIN RATE</div></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="metric-container"><div class="metric-value" style="color:{"#66fcf1" if net_r_total>0 else "#ff4b4b"}">{net_r_total:.2f}R</div><div class="metric-label">NET RETURN</div></div>', unsafe_allow_html=True)
        col4.markdown(f'<div class="metric-container"><div class="metric-value">{pf:.2f}</div><div class="metric-label">PROFIT FACTOR</div></div>', unsafe_allow_html=True)

        st.write(""); st.write("")

        g1, g2 = st.columns([2, 1])
        with g1:
            df['Cum'] = df['R_Kazanc'].cumsum()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Tarih'], y=df['Cum'], mode='lines', fill='tozeroy', line=dict(color='#66fcf1', width=2), fillcolor='rgba(102, 252, 241, 0.1)'))
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=300, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1f2833'))
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            fig_pie = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.7, color='Sonuç', color_discrete_map={'WIN':'#66fcf1', 'LOSS':'#ff4b4b'})
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(l=20, r=20, t=10, b=20), height=300, annotations=[dict(text=f"{rate:.0f}%", x=0.5, y=0.5, font_size=24, showarrow=False, font_color="white")])
            st.plotly_chart(fig_pie, use_container_width=True)

        # --- YENİ BÖLÜM: MARKET INTELLIGENCE ---
        st.markdown("---")
        st.subheader("📡 MARKET INTELLIGENCE")
        
        mi1, mi2 = st.columns(2)
        
        with mi1:
            st.markdown("##### TECHNICAL GAUGE (BTC/USDT)")
            # TradingView Technical Analysis Widget
            components.html("""
            <div class="tradingview-widget-container">
              <div class="tradingview-widget-container__widget"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
              {
              "interval": "4h", "width": "100%", "isTransparent": true, "height": "400",
              "symbol": "BINANCE:BTCUSDT", "showIntervalTabs": true, "displayMode": "single", "locale": "en", "colorTheme": "dark"
            }
              </script>
            </div>
            """, height=400)
            
        with mi2:
            st.markdown("##### ECONOMIC CALENDAR")
            # TradingView Economic Calendar Widget
            components.html("""
            <div class="tradingview-widget-container">
              <div class="tradingview-widget-container__widget"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
              {
              "colorTheme": "dark", "isTransparent": true, "width": "100%", "height": "400", "locale": "en", "importanceFilter": "-1,0,1", "currencyFilter": "USD"
            }
              </script>
            </div>
            """, height=400)
            
        st.markdown("---")
        
        # TABLO
        st.markdown("##### TRADE LOG")
        def style_df(row):
            color = '#66fcf1' if row['Sonuç'] == 'WIN' else '#ff4b4b'
            return [f'color: {color}; font-weight: 600' if col == 'Sonuç' else 'color: #c5c6c7' for col in row.index]
        st.dataframe(df.style.apply(style_df, axis=1), use_container_width=True, hide_index=True)

# ==========================================
# TAB 2: MEMBERSHIP
# ==========================================
with tab2:
    st.write("")
    
    # PROMO BANNER (ACİLİYET HİSSİ)
    st.markdown("""
    <div class="promo-banner">
        🔥 LIMITED TIME OFFER: Get the LIFETIME access before prices increase on Monday!
    </div>
    """, unsafe_allow_html=True)
    
    st.write(""); st.write("")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <div class="plan-name">STARTER</div>
            <div class="plan-price">$30<span style="font-size:1rem;color:#888">/mo</span></div>
            <br>
            <div style="text-align:left; color:#ccc; line-height:2;">
            ✓ Telegram Access<br>✓ 15m Elite Setups<br>✓ FVG & Fib Targets<br>✓ Support 24/7
            </div>
            <br><br>
            <a href="https://t.me/Orhan1909" target="_blank" class="custom-btn custom-btn-outline">SELECT PLAN</a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="pricing-card" style="border-color: #66fcf1;">
            <div class="plan-name">PROFESSIONAL</div>
            <div class="plan-price">$75<span style="font-size:1rem;color:#888">/qtr</span></div>
            <br>
            <div style="text-align:left; color:#ccc; line-height:2;">
            ✓ <b>All Starter Features</b><br>✓ Real-time Signals<br>✓ Market Direction (USDT.D)<br>✓ Priority Support
            </div>
            <br><br>
            <a href="https://t.me/Orhan1909" target="_blank" class="custom-btn">MOST POPULAR</a>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="pricing-card">
            <div class="plan-name">LIFETIME</div>
            <div class="plan-price">$250<span style="font-size:1rem;color:#888">/once</span></div>
            <br>
            <div style="text-align:left; color:#ccc; line-height:2;">
            ✓ <b>Lifetime Access</b><br>✓ Future Updates Included<br>✓ Bot Setup Assistance<br>✓ Private Group
            </div>
            <br><br>
            <a href="https://t.me/Orhan1909" target="_blank" class="custom-btn custom-btn-outline">CONTACT SALES</a>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 3: CONTACT
# ==========================================
with tab3:
    st.write(""); st.write("")
    c1, c2 = st.columns(2)
    with c1: st.markdown("""### 📨 Telegram Support\nFor instant assistance:\n<a href="https://t.me/Orhan1909" class="custom-btn">OPEN TELEGRAM</a>""", unsafe_allow_html=True)
    with c2: st.markdown("""### 📧 Email\nFor business partnerships:\n**orhanaliyev02@gmail.com**""")
    st.write(""); st.divider()
    
    st.subheader("❓ FAQ")
    with st.expander("How do I get access?"): st.write("Contact us on Telegram after USDT (TRC20) payment.")
    with st.expander("Is my capital safe?"): st.write("We use strict risk management (max 2% risk per trade).")
    with st.expander("Can I cancel?"): st.write("Yes, subscriptions are non-binding.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #45a29e; font-size: 0.8rem;'>© 2025 Crazytown Capital. All rights reserved.</p>", unsafe_allow_html=True)
