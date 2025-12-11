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
    initial_sidebar_state="expanded"
)

# --- GİZLİLİK VE TEMİZLİK (CSS) ---
st.markdown("""
    <style>
        /* 1. GEREKSİZLERİ GİZLE */
        #MainMenu {visibility: hidden;} /* Sağ üst 3 nokta */
        footer {visibility: hidden;}    /* Sağ alt 'Manage app' ve 'Made with Streamlit' */
        header {visibility: hidden;}    /* Üst boşluk (Bunu gizleyince menü oku da gidebilir, altta düzeltiyoruz) */
        
        /* 2. MENÜYÜ KURTARMA OPERASYONU */
        /* Üst barı gizlesek bile, sidebar butonunun olduğu alanı görünür yap */
        [data-testid="stSidebarNav"] {
            display: block !important;
            visibility: visible !important;
        }
        
        /* Deploy butonunu kesin yok et */
        .stDeployButton {display:none;}
        
        /* 3. GENEL TASARIM */
        .stApp {
            background-color: #0E1117;
            color: #E0E0E0;
            margin-top: -80px; /* Üstteki boşluğu kapat */
        }
        
        /* KPI KUTULARI */
        .metric-card {
            background: #161920;
            border-left: 4px solid #00F2C3;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #FFFFFF;
        }
        .metric-label {
            font-size: 0.85rem;
            color: #A0A0A0;
            text-transform: uppercase;
            font-weight: 600;
            margin-top: 5px;
        }

        /* FİYATLANDIRMA KARTLARI */
        .pricing-card {
            background: #161920;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .pricing-card:hover {
            border-color: #00F2C3;
            transform: translateY(-5px);
        }
        .pricing-header {
            font-size: 1.2rem;
            color: #00F2C3;
            font-weight: 700;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        .price-tag {
            font-size: 3rem;
            font-weight: 700;
            color: #FFFFFF;
            margin: 20px 0;
        }
        .price-period {
            font-size: 1rem;
            color: #888;
        }
        
        /* BUTONLAR */
        .cta-button {
            display: block;
            width: 100%;
            padding: 12px;
            background: transparent;
            color: #00F2C3;
            border: 1px solid #00F2C3;
            border-radius: 4px;
            text-align: center;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
        }
        .cta-button:hover {
            background: #00F2C3;
            color: #0E1117;
        }
        .cta-button-primary {
            background: #00F2C3;
            color: #0E1117;
            border: none;
        }
        .cta-button-primary:hover {
            background: #00D2A8;
        }
        
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
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# ==========================================
# 3. YAN MENÜ
# ==========================================
st.sidebar.markdown("### CRAZYTOWN CAPITAL")
st.sidebar.markdown("---")
page = st.sidebar.radio("MENU", ["Performance Dashboard", "Membership Access", "Contact Support"], index=0)
st.sidebar.markdown("---")

if page == "Performance Dashboard" and not df.empty:
    st.sidebar.markdown("#### FILTERS")
    coin_list = ["All Assets"] + list(df['Coin'].unique())
    selected_coin = st.sidebar.selectbox("Asset:", coin_list)
    if selected_coin != "All Assets":
        df = df[df['Coin'] == selected_coin]

# ==========================================
# SAYFA 1: DASHBOARD
# ==========================================
if page == "Performance Dashboard":
    st.markdown("# LIVE PERFORMANCE MONITOR")
    st.markdown('<p style="color:#888; margin-top:-15px;">Real-time trading data powered by Crazytown Algorithm.</p>', unsafe_allow_html=True)
    st.markdown("---")

    if df.empty:
        st.warning("No data available. Establishing connection...")
    else:
        total_trades = len(df)
        win_trades = len(df[df['Sonuç'] == 'WIN'])
        loss_trades = len(df[df['Sonuç'] == 'LOSS'])
        win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0
        net_r = df['R_Kazanc'].sum()
        
        gross_profit = df[df['R_Kazanc'] > 0]['R_Kazanc'].sum()
        gross_loss = abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum())
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 99.9

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="metric-card"><div class="metric-value">{total_trades}</div><div class="metric-label">TOTAL TRADES</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="metric-value">{win_rate:.1f}%</div><div class="metric-label">WIN RATE</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><div class="metric-value" style="color: {"#00F2C3" if net_r > 0 else "#FF4B4B"}">{net_r:.2f}R</div><div class="metric-label">NET RETURN</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-card"><div class="metric-value">{profit_factor:.2f}</div><div class="metric-label">PROFIT FACTOR</div></div>', unsafe_allow_html=True)

        st.write(""); st.write("")

        g1, g2 = st.columns([2, 1])
        with g1:
            st.markdown("### Equity Curve (R-Multiple)")
            df['Kümülatif'] = df['R_Kazanc'].cumsum()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Tarih'], y=df['Kümülatif'], mode='lines', fill='tozeroy', line=dict(color='#00F2C3', width=2), fillcolor='rgba(0, 242, 195, 0.1)'))
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=350, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#333'))
            st.plotly_chart(fig, use_container_width=True)

        with g2:
            st.markdown("### Performance Distribution")
            fig_pie = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.7, color='Sonuç', color_discrete_map={'WIN':'#00F2C3', 'LOSS':'#FF4B4B'})
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), margin=dict(l=20, r=20, t=20, b=20), height=350, annotations=[dict(text=f"{win_rate:.0f}%", x=0.5, y=0.5, font_size=28, showarrow=False, font_color="white", font_family="Arial Black")])
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("### Trade History")
        def style_dataframe(row):
            color = '#00F2C3' if row['Sonuç'] == 'WIN' else '#FF4B4B'
            return [f'color: {color}; font-weight: 600' if col == 'Sonuç' else 'color: #DDD' for col in row.index]

        st.dataframe(df.style.apply(style_dataframe, axis=1), use_container_width=True, hide_index=True, column_config={"Tarih": "Date", "Coin": "Asset", "Yön": "Direction", "Giriş": st.column_config.NumberColumn("Entry", format="$%.4f"), "R_Kazanc": st.column_config.NumberColumn("Return (R)", format="%.2f R"), "Sonuç": "Result"})

# ==========================================
# SAYFA 2: VIP ÜYELİK
# ==========================================
elif page == "Membership Access":
    st.markdown("<h1 style='text-align: center;'>MEMBERSHIP PLANS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Select a plan to access real-time institutional signals.</p>", unsafe_allow_html=True)
    st.write(""); st.write("")
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown("""<div class="pricing-card"><div class="pricing-header">STARTER</div><div class="price-tag">$30</div><div class="price-period">Monthly Billed</div><div class="feature-list">✓ Telegram Signal Access<br>✓ 15m Elite Setups<br>✓ FVG & Fib Targets<br><span style="color:#555">✕ USDT.D Analysis</span></div><a href="https://t.me/Orhan1909" target="_blank" class="cta-button">GET STARTED</a></div>""", unsafe_allow_html=True)
    with col2: st.markdown("""<div class="pricing-card featured"><div class="pricing-header">PROFESSIONAL</div><div class="price-tag">$75</div><div class="price-period">Quarterly Billed</div><div class="feature-list">✓ <b>All Starter Features</b><br>✓ Real-time L/S Signals<br>✓ Market Direction (USDT.D)<br>✓ Priority Support</div><a href="https://t.me/Orhan1909" target="_blank" class="cta-button cta-button-primary">BECOME A PRO</a></div>""", unsafe_allow_html=True)
    with col3: st.markdown("""<div class="pricing-card"><div class="pricing-header">LIFETIME</div><div class="price-tag">$250</div><div class="price-period">One-time Payment</div><div class="feature-list">✓ <b>Lifetime Access</b><br>✓ All Future Updates<br>✓ Bot Setup Assistance<br>✓ Private Group Access</div><a href="https://t.me/Orhan1909" target="_blank" class="cta-button">CONTACT SALES</a></div>""", unsafe_allow_html=True)

# ==========================================
# SAYFA 3: İLETİŞİM
# ==========================================
elif page == "Contact Support":
    st.markdown("## CONTACT US"); st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: st.markdown("""### Telegram Support\nFor instant assistance and membership inquiries.\n<a href="https://t.me/Orhan1909" class="cta-button">OPEN TELEGRAM</a>""", unsafe_allow_html=True)
    with c2: st.markdown("""### Email Inquiries\nFor business partnerships and detailed questions.\n**orhanaliyev02@gmail.com**""")

st.sidebar.markdown("---")
st.sidebar.caption("© 2025 Crazytown Capital.")
