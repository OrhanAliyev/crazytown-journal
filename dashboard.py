import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import calendar
import numpy as np # AI hesaplamaları için
import time

# ==========================================
# 0. AYARLAR
# ==========================================
st.set_page_config(
    page_title="Crazytown Capital",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'lang' not in st.session_state: st.session_state.lang = "TR"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"

# ÇEVİRİ VE İÇERİK YÖNETİMİ
TRANSLATIONS = {
    "EN": {
        "title_sub": "ALGORITHMIC TRADING SYSTEMS", "perf": "PERFORMANCE", "acad": "ACADEMY", "memb": "MEMBERSHIP", "cont": "CONTACT", "ai_lab": "AI LAB",
        "total_trades": "TOTAL TRADES", "win_rate": "WIN RATE", "net_return": "NET RETURN", "profit_factor": "PROFIT FACTOR",
        "season_goal": "SEASON GOAL", "completed": "COMPLETED", "perf_cal": "🗓️ PERFORMANCE CALENDAR",
        "select_month": "Select Month", "total_monthly": "TOTAL MONTHLY PNL", "market_intel": "📡 MARKET INTELLIGENCE",
        "roi_sim": "🧮 ROI SIMULATOR", "roi_desc": "Calculate potential earnings.", "initial_cap": "Initial Capital ($)",
        "risk_trade": "Risk Per Trade (%)", "proj_bal": "PROJECTED BALANCE", "trade_log": "TRADE LOG", "download": "📥 DOWNLOAD CSV",
        "limited_offer": "🔥 LIMITED TIME OFFER: Get LIFETIME access!", "feedback": "💬 TRADER FEEDBACK",
        "plan_starter": "STARTER", "plan_pro": "PROFESSIONAL", "plan_life": "LIFETIME", "sel_plan": "SELECT PLAN",
        "most_pop": "MOST POPULAR", "contact_sales": "CONTACT SALES", "faq": "❓ FAQ", "settings": "⚙️ SETTINGS",
        "lang_sel": "Language", "theme_sel": "Theme", "theme_dark": "Dark (Neon)", "theme_light": "Light (Corporate)",
        "acad_title": "OA | TRADE SMC MASTERY", "acad_quote": "Not beating the market, but following it with discipline.",
        "lesson_1_title": "📌 PART 1: TIME & CONTEXT", "lesson_1_content": "#### 1. TIME FILTER...",
        "lesson_2_title": "🛠️ PART 2: ENTRY SETUP", "lesson_2_content": "#### 1. FIBONACCI...",
        "lesson_3_title": "⚠️ PART 3: RULES", "lesson_3_content": "NO CHOCH. NO TRADING OUTSIDE HOURS.",
        # AI BÖLÜMÜ
        "ai_title": "🤖 NEURAL NETWORK PREDICTION", "ai_desc": "Probabilistic price forecasting based on SMC logic & machine learning.",
        "run_ai": "INITIALIZE NEURAL NET", "ai_analyzing": "Analyzing Order Flow...", "ai_calc": "Calculating Probabilities...",
        "ai_pair": "Select Asset", "ai_tf": "Timeframe", "ai_conf": "AI Confidence", "ai_direction": "Predicted Direction",
        "ai_bull": "BULLISH", "ai_bear": "BEARISH", "ai_neutral": "NEUTRAL"
    },
    "TR": {
        "title_sub": "ALGORİTMİK İŞLEM SİSTEMLERİ", "perf": "PERFORMANS", "acad": "AKADEMİ", "memb": "ÜYELİK", "cont": "İLETİŞİM", "ai_lab": "YAPAY ZEKA",
        "total_trades": "TOPLAM İŞLEM", "win_rate": "BAŞARI ORANI", "net_return": "NET GETİRİ", "profit_factor": "KÂR FAKTÖRÜ",
        "season_goal": "SEZON HEDEFİ", "completed": "TAMAMLANDI", "perf_cal": "🗓️ PERFORMANS TAKVİMİ",
        "select_month": "Ay Seçiniz", "total_monthly": "AYLIK TOPLAM PNL", "market_intel": "📡 PİYASA İSTİHBARATI",
        "roi_sim": "🧮 ROI SİMÜLATÖRÜ", "roi_desc": "Geçmiş performansa dayalı kazanç hesapla.", "initial_cap": "Başlangıç Sermayesi ($)",
        "risk_trade": "İşlem Başı Risk (%)", "proj_bal": "TAHMİNİ BAKİYE", "trade_log": "İŞLEM GEÇMİŞİ", "download": "📥 CSV İNDİR",
        "limited_offer": "🔥 SINIRLI TEKLİF: Zam gelmeden ÖMÜR BOYU erişimi kap!", "feedback": "💬 YATIRIMCI YORUMLARI",
        "plan_starter": "BAŞLANGIÇ", "plan_pro": "PROFESYONEL", "plan_life": "ÖMÜR BOYU", "sel_plan": "PLAN SEÇ",
        "most_pop": "EN POPÜLER", "contact_sales": "SATIŞA ULAŞ", "faq": "❓ SIK SORULANLAR", "settings": "⚙️ AYARLAR",
        "lang_sel": "Dil", "theme_sel": "Tema", "theme_dark": "Koyu Mod (Neon)", "theme_light": "Açık Mod (Kurumsal)",
        "acad_title": "OA | TRADE SMC USTALIK SINIFI", "acad_quote": "Piyasayı yenmek değil, disiplinle takip etmek.",
        "lesson_1_title": "📌 BÖLÜM 1: ZAMAN VE BAĞLAM", "lesson_1_content": "#### 1. ZAMAN FİLTRESİ...",
        "lesson_2_title": "🛠️ BÖLÜM 2: GİRİŞ STRATEJİSİ", "lesson_2_content": "#### 1. FIBONACCI...",
        "lesson_3_title": "⚠️ BÖLÜM 3: KURALLAR", "lesson_3_content": "CHOCH YOK. SAAT DIŞI İŞLEM YOK.",
        # AI BÖLÜMÜ
        "ai_title": "🤖 SİNİR AĞI TAHMİNİ", "ai_desc": "SMC mantığı ve makine öğrenimi tabanlı olasılıksal fiyat tahmini.",
        "run_ai": "SİNİR AĞINI BAŞLAT", "ai_analyzing": "Emir Akışı Analiz Ediliyor...", "ai_calc": "Olasılıklar Hesaplanıyor...",
        "ai_pair": "Varlık Seç", "ai_tf": "Zaman Dilimi", "ai_conf": "YZ Güven Puanı", "ai_direction": "Tahmini Yön",
        "ai_bull": "YÜKSELİŞ (LONG)", "ai_bear": "DÜŞÜŞ (SHORT)", "ai_neutral": "NÖTR"
    },
    "RU": {
        "title_sub": "АЛГОРИТМИЧЕСКИЕ ТОРГОВЫЕ СИСТЕМЫ", "perf": "ЭФФЕКТИВНОСТЬ", "acad": "АКАДЕМИЯ", "memb": "ПОДПИСКА", "cont": "КОНТАКТЫ", "ai_lab": "ИИ ЛАБОРАТОРИЯ",
        "total_trades": "ВСЕГО СДЕЛОК", "win_rate": "ВИНРЕЙТ", "net_return": "ЧИСТАЯ ПРИБЫЛЬ", "profit_factor": "ПРОФИТ-ФАКТОР",
        "season_goal": "ЦЕЛЬ СЕЗОНА", "completed": "ЗАВЕРШЕНО", "perf_cal": "🗓️ КАЛЕНДАРЬ ДОХОДНОСТИ",
        "select_month": "Выберите месяц", "total_monthly": "ИТОГ МЕСЯЦА PNL", "market_intel": "📡 РЫНОЧНЫЙ ИНТЕЛЛЕКТ",
        "roi_sim": "🧮 ROI СИМУЛЯТОР", "roi_desc": "Рассчитайте прибыль.", "initial_cap": "Капитал ($)",
        "risk_trade": "Риск (%)", "proj_bal": "ПРОГНОЗ", "trade_log": "ЖУРНАЛ СДЕЛОК", "download": "📥 СКАЧАТЬ CSV",
        "limited_offer": "🔥 ОГРАНИЧЕННОЕ ПРЕДЛОЖЕНИЕ: Получите ПОЖИЗНЕННЫЙ доступ!", "feedback": "💬 ОТЗЫВЫ",
        "plan_starter": "СТАРТ", "plan_pro": "ПРОФИ", "plan_life": "LIFETIME", "sel_plan": "ВЫБРАТЬ",
        "most_pop": "ПОПУЛЯРНЫЙ", "contact_sales": "СВЯЗАТЬСЯ", "faq": "❓ FAQ", "settings": "⚙️ НАСТРОЙКИ",
        "lang_sel": "Язык", "theme_sel": "Тема", "theme_dark": "Темная", "theme_light": "Светлая",
        "acad_title": "OA | TRADE SMC МАСТЕРСТВО", "acad_quote": "Дисциплина прежде всего.",
        "lesson_1_title": "📌 ЧАСТЬ 1: ВРЕМЯ", "lesson_1_content": "### 1. ФИЛЬТР ВРЕМЕНИ...",
        "lesson_2_title": "🛠️ ЧАСТЬ 2: ВХОД", "lesson_2_content": "### 1. ФИБОНАЧЧИ...",
        "lesson_3_title": "⚠️ ЧАСТЬ 3: ПРАВИЛА", "lesson_3_content": "НЕТ CHOCH.",
        # AI BÖLÜMÜ
        "ai_title": "🤖 НЕЙРОСЕТЕВОЙ ПРОГНОЗ", "ai_desc": "Вероятностное прогнозирование цены на основе SMC.",
        "run_ai": "ЗАПУСТИТЬ НЕЙРОСЕТЬ", "ai_analyzing": "Анализ потока ордеров...", "ai_calc": "Расчет вероятностей...",
        "ai_pair": "Актив", "ai_tf": "Таймфрейм", "ai_conf": "Уверенность ИИ", "ai_direction": "Направление",
        "ai_bull": "БЫЧИЙ (LONG)", "ai_bear": "МЕДВЕЖИЙ (SHORT)", "ai_neutral": "НЕЙТРАЛЬНО"
    }
}

def t(key): return TRANSLATIONS[st.session_state.lang].get(key, key)

with st.expander(t('settings'), expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        sl = st.selectbox(t('lang_sel'), ["TR", "EN", "RU"], index=["TR", "EN", "RU"].index(st.session_state.lang))
        if sl != st.session_state.lang: st.session_state.lang = sl; st.rerun()
    with c2:
        thm = st.selectbox(t('theme_sel'), [t('theme_dark'), t('theme_light')], index=0 if st.session_state.theme == "Dark" else 1)
        nt = "Dark" if thm == t('theme_dark') else "Light"
        if nt != st.session_state.theme: st.session_state.theme = nt; st.rerun()

# ==========================================
# 1. DİNAMİK RENK PALETİ VE CSS
# ==========================================
if st.session_state.theme == "Dark":
    # KOYU MOD (NEON)
    col = {
        "bg": "#050505",
        "txt": "#e0e0e0",
        "card": "rgba(20, 20, 25, 0.7)", 
        "bd": "#333",
        "ac": "#00ffcc", # Neon Turkuaz
        "ac_h": "#00cca3",
        "sec": "#111",
        "ttl": "#ffffff",
        "grd": "#aaaaaa"
    }
    # Koyu Mod Animasyonu (Parlak Küreler)
    anim_html = f"""
    <style>
        .orb-container {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; z-index: -1; background: {col['bg']}; }}
        .orb {{ position: absolute; border-radius: 50%; filter: blur(90px); opacity: 0.6; animation: moveOrb 20s infinite alternate; }}
        .orb1 {{ top: 10%; left: 10%; width: 50vw; height: 50vw; background: radial-gradient(circle, #00ffcc 0%, transparent 70%); }}
        .orb2 {{ bottom: 10%; right: 10%; width: 40vw; height: 40vw; background: radial-gradient(circle, #9900ff 0%, transparent 70%); animation-duration: 25s; animation-direction: alternate-reverse; }}
        .orb3 {{ top: 40%; left: 40%; width: 30vw; height: 30vw; background: radial-gradient(circle, #ff007f 0%, transparent 70%); animation-duration: 18s; }}
        @keyframes moveOrb {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(50px, 50px) scale(1.1); }} }}
    </style>
    <div class="orb-container"><div class="orb orb1"></div><div class="orb orb2"></div><div class="orb orb3"></div></div>
    """
else:
    # AÇIK MOD (KURUMSAL)
    col = {
        "bg": "#f8f9fa",
        "txt": "#212529", 
        "card": "rgba(255, 255, 255, 0.95)",
        "bd": "#dee2e6",
        "ac": "#0d6efd", 
        "ac_h": "#0b5ed7",
        "sec": "#ffffff",
        "ttl": "#000000", 
        "grd": "#6c757d"
    }
    # Açık Mod Animasyonu (Hafif)
    anim_html = f"""
    <style>
        .orb-container {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; z-index: -1; background: {col['bg']}; }}
        .orb {{ position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.2; animation: moveOrb 25s infinite alternate; }}
        .orb1 {{ top: -10%; left: -10%; width: 60vw; height: 60vw; background: radial-gradient(circle, #0d6efd 0%, transparent 60%); }}
        .orb2 {{ bottom: -10%; right: -10%; width: 60vw; height: 60vw; background: radial-gradient(circle, #6610f2 0%, transparent 60%); animation-duration: 30s; }}
        @keyframes moveOrb {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(30px, 30px); }} }}
    </style>
    <div class="orb-container"><div class="orb orb1"></div><div class="orb orb2"></div></div>
    """

st.markdown(anim_html, unsafe_allow_html=True)

st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Inter:wght@400;600&display=swap');
        
        .stApp {{ background: transparent !important; }}
        header, footer, #MainMenu {{display: none !important;}}
        .block-container {{padding-top: 2rem;}}

        /* YAZI RENGİ ZORLAMA (Light mode hatası için) */
        h1, h2, h3, h4, h5, h6, p, li, div, span, label {{ 
            color: {col['txt']} !important; 
            font-family: 'Inter', sans-serif;
        }}

        .neon-title {{
            font-family: 'Orbitron', sans-serif; font-size: 3.5rem; text-align: center; color: {col['ttl']} !important;
            font-weight: 900; letter-spacing: 4px; margin: 0;
            {f"text-shadow: 0 0 20px {col['ac']};" if st.session_state.theme == "Dark" else ""}
            animation: pulse 3s infinite alternate;
        }}
        @keyframes pulse {{ 0% {{opacity: 1;}} 100% {{opacity: 0.9;}} }}

        .metric-container {{
            background-color: {col['card']}; border: 1px solid {col['bd']}; border-radius: 10px; padding: 20px;
            text-align: center; backdrop-filter: blur(10px); box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }}
        .metric-container:hover {{ transform: translateY(-5px); border-color: {col['ac']}; }}
        .metric-value {{ font-size: 2rem; font-weight: 700; color: {col['ttl']} !important; }}
        .metric-label {{ font-size: 0.8rem; color: {col['grd']} !important; font-weight: 600; letter-spacing: 1px; }}

        .custom-btn {{ background-color: {col['ac']}; color: {col['bg']} !important; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold; display: block; text-align: center; }}
        .custom-btn-outline {{ border: 1px solid {col['ac']}; color: {col['ac']} !important; background: transparent; }}
        
        .stDataFrame {{ border: 1px solid {col['bd']}; }}
        .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {{ background-color: {col['sec']}; color: {col['txt']}; border-color: {col['bd']}; }}
        
        .calendar-container {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-top: 15px; }}
        .calendar-header {{ text-align: center; color: {col['grd']} !important; font-weight: bold; padding-bottom: 5px; border-bottom: 1px solid {col['bd']}; }}
        .day-cell {{ background-color: {col['sec']}; border: 1px solid {col['bd']}; border-radius: 6px; height: 90px; padding: 8px; display: flex; flex-direction: column; transition: 0.2s; }}
        .day-cell:hover {{ border-color: {col['ac']}; transform: scale(1.03); z-index: 5; }}
        .day-number {{ font-weight: bold; color: {col['txt']} !important; opacity: 0.7; }}
        .day-profit {{ font-size: 1.1rem; font-weight: 800; margin-top: auto; align-self: center; }}
        
        .day-win {{ background: rgba(0, 255, 204, 0.15); border-color: {col['ac']}; }}
        .day-win-light {{ background: rgba(13, 110, 253, 0.15); border-color: {col['ac']}; }}
        .day-loss {{ background: rgba(255, 75, 75, 0.15); border-color: #ff4b4b; }}
        .win-text {{ color: {col['ac']} !important; }} .loss-text {{ color: #ff4b4b !important; }} .empty-cell {{ background: transparent; border: none; }}
        
        .stTabs [data-baseweb="tab"] {{ color: {col['grd']} !important; }}
        .stTabs [data-baseweb="tab"]:hover {{ color: {col['ac']} !important; }}
        .stTabs [aria-selected="true"] {{ color: {col['ac']} !important; border-bottom-color: {col['ac']} !important; }}
        
        .pricing-card {{ background-color: {col['card']}; border: 1px solid {col['bd']}; border-radius: 12px; padding: 30px; text-align: center; backdrop-filter: blur(10px); }}
        .plan-price {{ color: {col['ttl']} !important; font-size: 2.5rem; font-weight: bold; }}
        .plan-name {{ color: {col['ac']} !important; font-weight: bold; letter-spacing: 2px; }}
        
        .rule-box {{ background: rgba(0,0,0,0.05); border-left: 4px solid {col['ac']}; padding: 15px; margin: 10px 0; color: {col['txt']} !important; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VERİ VE UI
# ==========================================
@st.cache_data(ttl=60)
def load_data():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in st.secrets: creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        else: creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds); sheet = client.open("Crazytown_Journal").sheet1; data = sheet.get_all_records()
        if not data: return pd.DataFrame()
        df = pd.DataFrame(data)
        if 'R_Kazanc' in df.columns: df['R_Kazanc'] = df['R_Kazanc'].astype(str).str.replace(',', '.'); df['R_Kazanc'] = pd.to_numeric(df['R_Kazanc'], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()
df = load_data()

wt = "light" if st.session_state.theme == "Light" else "dark"
components.html(f"""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>{{"symbols": [{{"proName": "BINANCE:BTCUSDT", "title": "Bitcoin"}}, {{"proName": "BINANCE:ETHUSDT", "title": "Ethereum"}}, {{"proName": "BINANCE:SOLUSDT", "title": "Solana"}}], "showSymbolLogo": true, "colorTheme": "{wt}", "isTransparent": true, "displayMode": "adaptive", "locale": "en"}}</script></div>""", height=50)

st.write("")
st.markdown('<div class="neon-title">CRAZYTOWN CAPITAL</div>', unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: {col['ac']}; letter-spacing: 2px; font-size: 0.9rem; margin-top: -5px; font-weight:bold;'>{t('title_sub')}</p>", unsafe_allow_html=True)
st.write("")

# 5 SEKME: Yapay Zeka Eklendi
tab1, tab2, tab5, tab3, tab4 = st.tabs([t('perf'), t('acad'), t('ai_lab'), t('memb'), t('cont')])

# TAB 1: PERFORMANS
with tab1:
    if df.empty: st.warning("Data not found.")
    else:
        tot = len(df); win = len(df[df['Sonuç'] == 'WIN']); rate = (win / tot * 100) if tot > 0 else 0; net_r = df['R_Kazanc'].sum()
        gp = df[df['R_Kazanc'] > 0]['R_Kazanc'].sum(); gl = abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum()); pf = (gp / gl) if gl > 0 else 0
        nc = col['ac'] if net_r > 0 else "#ff4b4b"
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="metric-container"><div class="metric-value">{tot}</div><div class="metric-label">{t("total_trades")}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-container"><div class="metric-value">{rate:.1f}%</div><div class="metric-label">{t("win_rate")}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-container"><div class="metric-value" style="color:{nc} !important">{net_r:.2f}R</div><div class="metric-label">{t("net_return")}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-container"><div class="metric-value">{pf:.2f}</div><div class="metric-label">{t("profit_factor")}</div></div>', unsafe_allow_html=True)
        st.write(""); st.write(""); prog = min(max(net_r / 100.0, 0.0), 1.0)
        st.markdown(f"""<div style="display:flex; justify-content:space-between; font-size:0.8rem; color:{col['grd']} !important; margin-bottom:5px;"><span>{t('season_goal')} (100R)</span><span style="color:{col['ac']} !important">{int(prog*100)}% {t('completed')}</span></div>""", unsafe_allow_html=True)
        st.progress(prog); st.write("")
        
        pt = "plotly_white" if st.session_state.theme == "Light" else "plotly_dark"; bg = "rgba(0,0,0,0)"
        g1, g2 = st.columns([2, 1])
        with g1:
            df['Cum'] = df['R_Kazanc'].cumsum(); fig = go.Figure()
            fc = f"rgba(0, 255, 204, 0.2)" if st.session_state.theme == "Dark" else f"rgba(13, 110, 253, 0.2)"
            fig.add_trace(go.Scatter(x=df['Tarih'], y=df['Cum'], mode='lines', fill='tozeroy', line=dict(color=col['ac'], width=2), fillcolor=fc))
            fig.update_layout(template=pt, paper_bgcolor=bg, plot_bgcolor=bg, margin=dict(l=0, r=0, t=10, b=0), height=300, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=col['bd']))
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            fp = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.7, color='Sonuç', color_discrete_map={'WIN':col['ac'], 'LOSS':'#ff4b4b'})
            fp.update_layout(template=pt, paper_bgcolor=bg, showlegend=False, margin=dict(l=20, r=20, t=10, b=20), height=300, annotations=[dict(text=f"{rate:.0f}%", x=0.5, y=0.5, font_size=24, showarrow=False, font_color=col['ttl'])])
            st.plotly_chart(fp, use_container_width=True)

        st.markdown("---"); st.subheader(t("perf_cal"))
        try:
            df['Tarih_Dt'] = pd.to_datetime(df['Tarih'], dayfirst=True, errors='coerce'); df.dropna(subset=['Tarih_Dt'], inplace=True)
            if not df.empty:
                df = df.sort_values('Tarih_Dt'); ms = df['Tarih_Dt'].dt.strftime('%Y-%m').unique(); sm = st.selectbox(t("select_month"), options=ms, index=len(ms)-1)
                y, m = map(int, sm.split('-')); md = df[df['Tarih_Dt'].dt.strftime('%Y-%m') == sm].copy(); dp = md.groupby(md['Tarih_Dt'].dt.day)['R_Kazanc'].sum().to_dict(); cm = calendar.monthcalendar(y, m)
                hc = ['<div class="calendar-container">']; dn = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'] if st.session_state.lang == "TR" else (['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'] if st.session_state.lang == "RU" else ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
                for d in dn: hc.append(f'<div class="calendar-header">{d}</div>')
                mt = 0
                for w in cm:
                    for d in w:
                        if d == 0: hc.append('<div class="day-cell empty-cell"></div>')
                        else:
                            v = dp.get(d, 0); mt += v; cc, pc, pt = "day-cell", "", "0.00R"
                            if d in dp:
                                if v > 0: cc += " day-win" if st.session_state.theme == "Dark" else " day-win-light"; pc = "win-text"; pt = f"+{v:.2f}R"
                                elif v < 0: cc += " day-loss"; pc = "loss-text"; pt = f"{v:.2f}R"
                            hc.append(f'<div class="{cc}"><div class="day-number">{d}</div><div class="day-profit {pc}">{pt}</div></div>')
                hc.append('</div>'); st.markdown("".join(hc), unsafe_allow_html=True); st.markdown(f"<div style='text-align:center; margin-top:15px; font-size:1.2rem; font-weight:bold; color:{col['ac'] if mt>0 else '#ff4b4b'} !important'>{t('total_monthly')}: {mt:.2f}R</div>", unsafe_allow_html=True)
        except Exception as e: st.error(str(e))

        st.markdown("---"); st.subheader(t("roi_sim")); r1, r2, r3 = st.columns([1,1,2])
        with r1: cap = st.number_input(t("initial_cap"), min_value=100, value=1000)
        with r2: risk = st.slider(t("risk_trade"), 0.5, 5.0, 2.0)
        prof = cap * (risk / 100) * net_r; bal = cap + prof; perc = (prof / cap) * 100
        with r3: st.markdown(f"""<div style="background:{col['card']}; padding:15px; border-radius:10px; border:1px solid {col['ac']}; text-align:center;"><span style="color:{col['grd']} !important">{t('proj_bal')}</span><br><span style="color:{col['ttl']} !important; font-size:2rem; font-weight:bold;">${bal:,.2f}</span><br><span style="color:{col['ac']} !important">(+${prof:,.2f} / +{perc:.1f}%)</span></div>""", unsafe_allow_html=True)
        
        st.markdown("---"); h, d = st.columns([4, 1])
        with h: st.markdown(f"##### {t('trade_log')}")
        with d: st.download_button(label=t("download"), data=df.to_csv(index=False).encode('utf-8'), file_name='log.csv', mime='text/csv')
        def hwin(row):
            win_color = col['ac'] if row['Sonuç'] == 'WIN' else '#ff4b4b'
            return [f'color: {win_color}; font-weight:bold' if c_name == 'Sonuç' else f'color: {col["txt"]}' for c_name in row.index]
        st.dataframe(df.style.apply(hwin, axis=1), use_container_width=True, hide_index=True)

# TAB 2: AKADEMİ (PDF)
with tab2:
    st.write(""); st.markdown(f"<h2 style='text-align: center; color: {col['ac']} !important;'>{t('acad_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"""<div style="text-align: center; font-style: italic; color: {col['grd']} !important; margin-bottom: 20px;">"{t('acad_quote')}"</div>""", unsafe_allow_html=True)
    with st.expander(t('lesson_1_title'), expanded=True): st.markdown(t('lesson_1_content'))
    with st.expander(t('lesson_2_title')): st.markdown(t('lesson_2_content'))
    with st.expander(t('lesson_3_title')): st.markdown(t('lesson_3_content'), unsafe_allow_html=True)

# TAB 5: AI LAB (YENİ YAPAY ZEKA MODÜLÜ)
with tab5:
    st.write("")
    st.markdown(f"<h2 style='text-align: center; color: {col['ac']} !important;'>{t('ai_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"""<div style="text-align: center; font-style: italic; color: {col['grd']} !important; margin-bottom: 20px;">{t('ai_desc')}</div>""", unsafe_allow_html=True)
    
    ai_c1, ai_c2, ai_c3 = st.columns([1, 1, 2])
    with ai_c1:
        asset = st.selectbox(t('ai_pair'), ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
    with ai_c2:
        tf = st.selectbox(t('ai_tf'), ["15m", "1h", "4h", "1D"])
    with ai_c3:
        st.write("") # Spacer
        if st.button(t('run_ai'), key="ai_btn", use_container_width=True):
            with st.spinner(t('ai_analyzing')):
                time.sleep(1.5) # Simülasyon efekti
            with st.spinner(t('ai_calc')):
                time.sleep(1)
            
            # --- AI SIMULATION LOGIC ---
            # Rastgele bir yön belirle (Simülasyon)
            import random
            direction = random.choice(["BULL", "BEAR"])
            confidence = random.randint(75, 96)
            
            # Grafik Verisi Oluştur (Random Walk)
            steps = 50
            start_price = 95000 if "BTC" in asset else (3000 if "ETH" in asset else 150)
            x = np.arange(steps)
            # Rastgele yürüyüş (Trendli)
            trend = 0.5 if direction == "BULL" else -0.5
            noise = np.random.normal(0, 1, steps)
            y = start_price + np.cumsum(noise + trend) * (start_price * 0.002)
            
            # Güven Aralığı (Prediction Cone)
            y_upper = y + (np.arange(steps) * (start_price * 0.0005))
            y_lower = y - (np.arange(steps) * (start_price * 0.0005))
            
            # --- SONUÇLARI GÖSTER ---
            res_col1, res_col2 = st.columns(2)
            dir_text = t('ai_bull') if direction == "BULL" else t('ai_bear')
            dir_color = col['ac'] if direction == "BULL" else "#ff4b4b"
            
            with res_col1:
                st.markdown(f"""
                <div class="metric-container" style="border-color:{dir_color}">
                    <div class="metric-label">{t('ai_direction')}</div>
                    <div class="metric-value" style="color:{dir_color} !important">{dir_text}</div>
                </div>
                """, unsafe_allow_html=True)
            with res_col2:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">{t('ai_conf')}</div>
                    <div class="metric-value">{confidence}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            # --- AI GRAFİĞİ (Prediction Cone) ---
            st.write("")
            fig_ai = go.Figure()
            # Geçmiş (Simüle)
            fig_ai.add_trace(go.Scatter(x=np.arange(20), y=y[:20], mode='lines', name='History', line=dict(color=col['grd'], width=2)))
            # Tahmin
            fig_ai.add_trace(go.Scatter(x=np.arange(19, 50), y=y[19:], mode='lines', name='Forecast', line=dict(color=dir_color, width=3)))
            # Güven Aralığı
            fig_ai.add_trace(go.Scatter(x=np.concatenate([np.arange(19, 50), np.arange(19, 50)[::-1]]),
                                        y=np.concatenate([y_upper[19:], y_lower[19:][::-1]]),
                                        fill='toself', fillcolor=f"rgba({(0, 255, 204) if direction=='BULL' else (255, 75, 75)}, 0.1)",
                                        line=dict(color='rgba(255,255,255,0)'), hoverinfo="skip", showlegend=False))
            
            pt = "plotly_white" if st.session_state.theme == "Light" else "plotly_dark"
            fig_ai.update_layout(template=pt, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, margin=dict(l=0,r=0,t=20,b=0))
            st.plotly_chart(fig_ai, use_container_width=True)

# TAB 3: MEMBERSHIP
with tab3:
    st.write(""); st.markdown(f"""<div class="metric-container" style="background:linear-gradient(90deg, {col['card']}, {col['bg']}); border-color:{col['ac']}">{t('limited_offer')}</div>""", unsafe_allow_html=True); st.write("")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"""<div class="pricing-card"><div class="plan-name">{t('plan_starter')}</div><div class="plan-price">$30<span style="font-size:1rem;color:{col['grd']} !important">/mo</span></div><a href="#" class="custom-btn custom-btn-outline">{t('sel_plan')}</a></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div class="pricing-card" style="border-color:{col['ac']}"><div class="plan-name">{t('plan_pro')}</div><div class="plan-price">$75<span style="font-size:1rem;color:{col['grd']} !important">/qtr</span></div><a href="#" class="custom-btn">{t('most_pop')}</a></div>""", unsafe_allow_html=True)
    with c3: st.markdown(f"""<div class="pricing-card"><div class="plan-name">{t('plan_life')}</div><div class="plan-price">$250<span style="font-size:1rem;color:{col['grd']} !important">/once</span></div><a href="#" class="custom-btn custom-btn-outline">{t('contact_sales')}</a></div>""", unsafe_allow_html=True)

# TAB 4: CONTACT
with tab4:
    st.write(""); c1, c2 = st.columns(2)
    with c1: st.markdown(f"""### 📨 Telegram\n<a href="https://t.me/Orhan1909" class="custom-btn">OPEN TELEGRAM</a>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""### 📧 Email\n**orhanaliyev02@gmail.com**""")

st.markdown("---"); st.markdown(f"<p style='text-align: center; color: {col['ac_h']} !important; font-size: 0.8rem;'>© 2025 Crazytown Capital. All rights reserved.</p>", unsafe_allow_html=True)
