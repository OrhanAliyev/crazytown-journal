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

# --- CSS TASARIM ---
st.markdown("""
    <style>
        /* 1. GİZLİLİK AYARLARI */
        /* DİKKAT: #MainMenu (3 Nokta) satırını sildik, artık görünecek. */
        
        footer {visibility: hidden;}    /* 'Made with Streamlit' gizle */
        header {visibility: hidden;}    /* Üst boşluğu kapat */
        .stDeployButton {display:none;} /* Deploy butonunu gizle */
        
        /* Yan Menü Çubuğunu tamamen yok et */
        [data-testid="stSidebar"] {display: none;}
        
        /* 2. GENEL TASARIM */
        .stApp {
            background-color: #0E1117;
            color: #E0E0E0;
            margin-top: -50px; /* Üstü yukarı çek */
        }
        
        h1, h2, h3 {
            font-weight: 600;
            color: #FFFFFF;
            letter-spacing: 0.5px;
        }
        
        /* KPI KUTULARI */
        .metric-card {
            background: #161920;
            border-left: 4px solid #00F2C3;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            text-align: center;
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

        /* TABLO */
        .stDataFrame {
            border: 1px solid #333;
        }
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
# 3. DASHBOARD İÇERİĞİ
# ==========================================

# Başlık
col_logo, col_text = st.columns([1, 5])
with col_text:
    st.markdown("# 🎯 CRAZYTOWN TRADER")
    st.markdown('#### *"Don\'t chase the market, let the market come to you. Sniper Mode: ON."*')

st.markdown("---")

if df.empty:
    st.warning("⚠️ Veri bekleniyor. Lütfen veritabanı bağlantısını kontrol edin.")
else:
    # --- FİLTRELER (ÜST KISIMDA GİZLİ) ---
    with st.expander("🔍 Filtreleme Seçenekleri (Coin / Setup)"):
        f1, f2 = st.columns(2)
        with f1:
            coin_list = ["Tümü"] + list(df['Coin'].unique())
            selected_coin = st.selectbox("Coin Seç:", coin_list)
        with f2:
            setup_list = ["Tümü"] + list(df['Setup'].unique()) if 'Setup' in df.columns else ["Tümü"]
            selected_setup = st.selectbox("Setup Tipi:", setup_list)
    
    # Filtre Uygulama
    if selected_coin != "Tümü":
        df = df[df['Coin'] == selected_coin]
    if selected_setup != "Tümü":
        df = df[df['Setup'] == selected_setup]

    st.write("") 

    # --- KPI ---
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

    # --- GRAFİKLER ---
    g1, g2 = st.columns([2, 1])

    with g1:
        st.markdown("### Equity Curve (R-Multiple)")
        df['Kümülatif'] = df['R_Kazanc'].cumsum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Tarih'], y=df['Kümülatif'],
            mode='lines', fill='tozeroy',
            line=dict(color='#00F2C3', width=2),
            fillcolor='rgba(0, 242, 195, 0.1)'
        ))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=350, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#333'))
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        st.markdown("### Performance Distribution")
        fig_pie = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.7, color='Sonuç', color_discrete_map={'WIN':'#00F2C3', 'LOSS':'#FF4B4B'})
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), margin=dict(l=20, r=20, t=20, b=20), height=350, annotations=[dict(text=f"{win_rate:.0f}%", x=0.5, y=0.5, font_size=28, showarrow=False, font_color="white", font_family="Arial Black")])
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- TABLO ---
    st.markdown("### Trade History")
    def style_dataframe(row):
        color = '#00F2C3' if row['Sonuç'] == 'WIN' else '#FF4B4B'
        return [f'color: {color}; font-weight: 600' if col == 'Sonuç' else 'color: #DDD' for col in row.index]

    st.dataframe(
        df.style.apply(style_dataframe, axis=1),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tarih": "Date",
            "Coin": "Asset",
            "Yön": "Direction",
            "Giriş": st.column_config.NumberColumn("Entry", format="$%.4f"),
            "R_Kazanc": st.column_config.NumberColumn("Return (R)", format="%.2f R"),
            "Sonuç": "Result"
        }
    )

st.markdown("---")
st.caption("© 2025 Crazytown Capital.")
