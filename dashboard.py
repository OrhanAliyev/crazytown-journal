import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Crazytown Public Journal",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 🔒 GİZLİLİK MODU (GitHub Linki ve Menüyü Kaldır) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- CSS STİL ---
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        color: #00F2C3;
        text-align: center;
        margin-bottom: 0px;
    }
    .slogan {
        font-size: 1.2rem;
        color: #cfd8dc;
        text-align: center;
        font-style: italic;
        margin-bottom: 30px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #00F2C3;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE SHEETS BAĞLANTISI ---
@st.cache_data(ttl=60)
def load_data():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            return pd.DataFrame() 
            
        client = gspread.authorize(creds)
        sheet = client.open("Crazytown_Journal").sheet1
        data = sheet.get_all_records()
        
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        
        if 'R_Kazanc' in df.columns:
            df['R_Kazanc'] = df['R_Kazanc'].astype(str).str.replace(',', '.')
            df['R_Kazanc'] = pd.to_numeric(df['R_Kazanc'], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        return pd.DataFrame()

# --- VERİYİ ÇEK ---
df = load_data()

# --- GÖRSELLEŞTİRME ---
st.markdown('<p class="main-title">🎯 CRAZYTOWN TRADER</p>', unsafe_allow_html=True)
st.markdown('<p class="slogan">"Don\'t chase the market, let the market come to you. Sniper Mode: ON."</p>', unsafe_allow_html=True)

if df.empty:
    st.info("📭 Veri bekleniyor... (Bağlantı kuruluyor veya tablo boş)")
else:
    total_trades = len(df)
    win_count = len(df[df['Sonuç'] == 'WIN'])
    win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0
    total_r = df['R_Kazanc'].sum()
    avg_r = df[df['Sonuç'] == 'WIN']['R_Kazanc'].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Toplam İşlem", f"{total_trades}", delta="Adet")
    c2.metric("Win Rate (Başarı)", f"%{win_rate:.1f}", delta_color="normal")
    c3.metric("Net Kazanç (R)", f"{total_r:.2f}R", delta="Kasa Büyümesi")
    
    val = avg_r if pd.notna(avg_r) else 0
    c4.metric("Ortalama Kazanç", f"{val:.2f}R")

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📈 Kasa Büyümesi")
        df['Kümülatif'] = df['R_Kazanc'].cumsum()
        fig_area = px.area(df, x='Tarih', y='Kümülatif', markers=True, template="plotly_dark")
        fig_area.update_traces(line_color='#00F2C3', fill='tozeroy')
        st.plotly_chart(fig_area, use_container_width=True)

    with col_right:
        st.subheader("🎯 Win / Loss")
        fig_pie = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.5, 
                         color='Sonuç', color_discrete_map={'WIN':'#00cc96', 'LOSS':'#ef553b'}, 
                         template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📝 Son İşlemler Listesi")
    
    def highlight_win_loss(val):
        color = '#00F2C3' if val == 'WIN' else '#FF4B4B'
        return f'color: {color}; font-weight: bold'

    st.dataframe(
        df.style.applymap(highlight_win_loss, subset=['Sonuç']),
        use_container_width=True,
        hide_index=True 
    )

st.markdown("---")
st.caption("⚠️ **Yasal Uyarı:** *Burada paylaşılan veriler kişisel işlem günlüğüdür ve eğitim amaçlıdır. Kesinlikle yatırım tavsiyesi değildir (YTD).*")
