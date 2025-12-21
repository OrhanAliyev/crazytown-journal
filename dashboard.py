import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import calendar
import numpy as np
import time
import requests

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
if 'legal_accepted' not in st.session_state: st.session_state.legal_accepted = False

# ==========================================
# 1. ORİJİNAL ÇEVİRİ VE İÇERİK
# ==========================================
TRANSLATIONS = {
    "EN": {
        "title_sub": "ALGORITHMIC TRADING SYSTEMS", "perf": "PERFORMANCE", "acad": "ACADEMY", "memb": "MEMBERSHIP", "cont": "CONTACT", "ai_lab": "AI LAB", "radar": "📡 RADAR",
        "total_trades": "TOTAL TRADES", "win_rate": "WIN RATE", "net_return": "NET RETURN", "profit_factor": "PROFIT FACTOR",
        "season_goal": "SEASON GOAL", "completed": "COMPLETED", "perf_cal": "🗓️ PERFORMANCE CALENDAR",
        "select_month": "Select Month", "total_monthly": "TOTAL MONTHLY PNL", "roi_sim": "🧮 ROI SIMULATOR", 
        "proj_bal": "PROJECTED BALANCE", "trade_log": "TRADE LOG", "download": "📥 DOWNLOAD CSV",
        "plan_starter": "STARTER", "plan_pro": "PROFESSIONAL", "plan_life": "LIFETIME", "sel_plan": "SELECT PLAN",
        "most_pop": "MOST POPULAR", "contact_sales": "CONTACT SALES", "lang_sel": "Language", "theme_sel": "Theme",
        "theme_dark": "Dark (Neon)", "theme_light": "Light (Corporate)", "settings": "⚙️ SETTINGS",
        "acad_title": "OA | TRADE SMC MASTERY", "acad_quote": "Not beating the market, but following it with discipline.",
        "lesson_1_title": "📌 PART 1: TIME & CONTEXT", "lesson_1_content": "#### 1. TIME FILTER\n* **LONDON:** `10:00 – 12:00` (UTC+3)\n* **NEW YORK:** `15:30 – 18:30` (UTC+3)",
        "lesson_2_title": "🛠️ PART 2: ENTRY SETUP", "lesson_2_content": "#### 1. FIBONACCI\n* **ENTRY:** `0.75` - `0.60`\n* **STOP:** `1.0`",
        "lesson_3_title": "⚠️ PART 3: RULES", "lesson_3_content": "<div class='rule-box'><h4>🚨 STRICT RULES</h4><ul><li><b>NO CHOCH</b></li><li><b>NO TRADING OUTSIDE HOURS</b></li></ul>",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "Real-time market scanning & AI Confidence Score.",
        "run_ai": "SCAN MARKET", "ai_analyzing": "Scanning Order Flow...", 
        "ai_input_label": "Enter Symbol (e.g. BTC, ETH, SOL, PEPE)", "ai_trend": "General Trend", "ai_rsi": "RSI Indicator", 
        "ai_supp": "Est. Support", "ai_res": "Est. Resistance", "ai_score": "Crazytown Confidence Score", "ai_dec": "AI DECISION",
        "bull": "BULLISH 🟢", "bear": "BEARISH 🔴", "neutral": "NEUTRAL ⚪", "s_buy": "STRONG BUY 🚀", "buy": "BUY 🟢", 
        "sell": "SELL 🔴", "s_sell": "STRONG SELL 🔻", "wait": "WAIT ✋", "data_source": "Data Source", "err_msg": "Coin not found.",
        "legal_title": "LEGAL DISCLAIMER", "legal_text": "Not investment advice.", "accept_terms": "I accept."
    },
    "TR": {
        "title_sub": "ALGORİTMİK İŞLEM SİSTEMLERİ", "perf": "PERFORMANS", "acad": "AKADEMİ", "memb": "ÜYELİK", "cont": "İLETİŞİM", "ai_lab": "YAPAY ZEKA", "radar": "📡 RADAR",
        "total_trades": "TOPLAM İŞLEM", "win_rate": "BAŞARI ORANI", "net_return": "NET GETİRİ", "profit_factor": "KÂR FAKTÖRÜ",
        "season_goal": "SEZON HEDEFİ", "completed": "TAMAMLANDI", "perf_cal": "🗓️ PERFORMANS TAKVİMİ",
        "select_month": "Ay Seçiniz", "total_monthly": "AYLIK TOPLAM PNL", "roi_sim": "🧮 ROI SİMÜLATÖRÜ", 
        "proj_bal": "TAHMİNİ BAKİYE", "trade_log": "İŞLEM GEÇMİŞİ", "download": "📥 CSV İNDİR",
        "plan_starter": "BAŞLANGIÇ", "plan_pro": "PROFESYONEL", "plan_life": "ÖMÜR BOYU", "sel_plan": "PLAN SEÇ",
        "most_pop": "EN POPÜLER", "contact_sales": "SATIŞA ULAŞ", "lang_sel": "Dil", "theme_sel": "Tema",
        "theme_dark": "Koyu Mod (Neon)", "theme_light": "Açık Mod (Kurumsal)", "settings": "⚙️ AYARLAR",
        "acad_title": "OA | TRADE SMC USTALIK SINIFI", "acad_quote": "Piyasayı yenmek değil, disiplinle takip etmek.",
        "lesson_1_title": "📌 BÖLÜM 1: ZAMAN VE BAĞLAM", "lesson_1_content": "#### 1. ZAMAN FİLTRESİ\n* **LONDRA:** `10:00 – 12:00` (TSİ)\n* **NEW YORK:** `15:30 – 18:30` (TSİ)\n#### 2. GÜNLÜK BAĞLAM\nTek şart **LİKİDİTE ALIMI (SWEEP)**.",
        "lesson_2_title": "🛠️ BÖLÜM 2: GİRİŞ STRATEJİSİ", "lesson_2_content": "#### 1. FIBONACCI\n* **GİRİŞ:** `0.75` - `0.60`\n* **STOP:** `1`\n#### 2. FVG ONAYI",
        "lesson_3_title": "⚠️ BÖLÜM 3: KURALLAR", "lesson_3_content": "<div class='rule-box'><h4>🚨 DEĞİŞMEZ KURALLAR</h4><ul><li><b>CHOCH YOK</b></li><li><b>SAAT DIŞI İŞLEM YOK</b></li></ul></div>",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "Gelişmiş Teknik Analiz & YZ Güven Skoru.",
        "run_ai": "TARA VE ANALİZ ET", "ai_analyzing": "Piyasa Yapısı Taranıyor...", 
        "ai_input_label": "Coin Sembolü (Örn: TAO, BTC, ETH, PEPE)", "ai_trend": "Genel Trend", "ai_rsi": "RSI Göstergesi", 
        "ai_supp": "Tahmini Destek", "ai_res": "Tahmini Direnç", "ai_score": "Crazytown Güven Skoru", "ai_dec": "YZ KARARI",
        "bull": "BOĞA (YÜKSELİŞ) 🟢", "bear": "AYI (DÜŞÜŞ) 🔴", "neutral": "NÖTR ⚪", "s_buy": "GÜÇLÜ AL 🚀", "buy": "AL 🟢", 
        "sell": "SAT 🔴", "s_sell": "GÜÇLÜ SAT 🔻", "wait": "BEKLE ✋", "data_source": "Veri Kaynağı", "err_msg": "Coin bulunamadı.",
        "legal_title": "YASAL UYARI", "legal_text": "Burada yer alan bilgi, yorum ve tavsiyeler yatırım danışmanlığı kapsamında değildir.", "accept_terms": "Okudum, onaylıyorum."
    },
    "RU": {
        "title_sub": "АЛГОРИТМИЧЕСКИЕ ТОРГОВЫЕ СИСТЕМЫ", "perf": "ЭФФЕКТИВНОСТЬ", "acad": "АКАДЕМИЯ", "memb": "ПОДПИСКА", "cont": "КОНТАКТЫ", "ai_lab": "ИИ ЛАБОРАТОРИЯ", "radar": "📡 РАДАР",
        "total_trades": "ВСЕГО СДЕЛОК", "win_rate": "ВИНРЕЙТ", "net_return": "ЧИСТАЯ ПРИБЫЛЬ", "profit_factor": "ПРОФИТ-ФАКТОР",
        "season_goal": "ЦЕЛЬ СЕЗОНА", "completed": "ЗАВЕРШЕНО", "perf_cal": "🗓️ КАЛЕНДАРЬ",
        "select_month": "Выберите месяц", "total_monthly": "ИТОГ МЕСЯЦА PNL", "roi_sim": "🧮 ROI СИМУЛЯТОР", 
        "proj_bal": "ПРОГНОЗ", "trade_log": "ЖУРНАЛ", "download": "📥 СКАЧАТЬ",
        "plan_starter": "СТАРТ", "plan_pro": "ПРОФИ", "plan_life": "LIFETIME", "sel_plan": "ВЫБРАТЬ",
        "most_pop": "ПОПУЛЯРНЫЙ", "contact_sales": "СВЯЗАТЬСЯ", "lang_sel": "Язык", "theme_sel": "Тема",
        "theme_dark": "Темная", "theme_light": "Светлая", "settings": "⚙️ НАСТРОЙКИ",
        "acad_title": "OA | TRADE SMC МАСТЕРСТВО", "acad_quote": "Дисциплина прежде всего.",
        "lesson_1_title": "📌 ЧАСТЬ 1: ВРЕМЯ", "lesson_1_content": "...",
        "lesson_2_title": "🛠️ ЧАСТЬ 2: ВХОД", "lesson_2_content": "...",
        "lesson_3_title": "⚠️ ЧАСТЬ 3: ПРАВИЛА", "lesson_3_content": "...",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "ИИ анализ.",
        "run_ai": "АНАЛИЗ", "ai_analyzing": "Сканирование...", 
        "ai_input_label": "Символ (BTC, ETH...)", "ai_trend": "Тренд", "ai_rsi": "RSI", 
        "ai_supp": "Поддержка", "ai_res": "Сопротивление", "ai_score": "Оценка уверенности", "ai_dec": "РЕШЕНИЕ",
        "bull": "БЫЧИЙ 🟢", "bear": "МЕДВЕЖИЙ 🔴", "neutral": "НЕЙТРАЛЬНО ⚪", "s_buy": "СИЛЬНАЯ ПОКУПКА 🚀", 
        "buy": "ПОКУПАТЬ 🟢", "sell": "ПРОДАВАТЬ 🔴", "s_sell": "СИЛЬНАЯ ПРОДАЖ 🔻", "wait": "ЖДАТЬ ✋", 
        "data_source": "Источник", "err_msg": "Монета не найдена.",
        "legal_title": "ОТКАЗ ОТ ОТВЕТСТВЕННОСТИ", "legal_text": "Не является инвестиционным советом.", "accept_terms": "Я принимаю."
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
# 2. DİNAMİK RENK VE TASARIM
# ==========================================
if st.session_state.theme == "Dark":
    col = {
        "bg": "#050505", "txt": "#e0e0e0", "card": "rgba(20, 20, 25, 0.9)", 
        "bd": "#333", "ac": "#00ffcc", "ac_h": "#00cca3", "sec": "#111", 
        "ttl": "#ffffff", "grd": "#aaaaaa", "ai_bg": "#0e0e0e"
    }
    anim_html = f"""<style>.orb-container {{position:fixed;top:0;left:0;width:100%;height:100%;overflow:hidden;z-index:-1;background:{col['bg']};}} .orb {{position:absolute;border-radius:50%;filter:blur(90px);opacity:0.6;animation:moveOrb 20s infinite alternate;}} .orb1 {{top:10%;left:10%;width:50vw;height:50vw;background:radial-gradient(circle,#00ffcc 0%,transparent 70%);}} .orb2 {{bottom:10%;right:10%;width:40vw;height:40vw;background:radial-gradient(circle,#9900ff 0%,transparent 70%);animation-duration:25s;animation-direction:alternate-reverse;}} @keyframes moveOrb {{0%{{transform:translate(0,0) scale(1);}}100%{{transform:translate(50px,50px) scale(1.1);}}}}</style><div class="orb-container"><div class="orb orb1"></div><div class="orb orb2"></div></div>"""
else:
    col = {
        "bg": "#f8f9fa", "txt": "#212529", "card": "rgba(255, 255, 255, 0.95)", 
        "bd": "#dee2e6", "ac": "#0d6efd", "ac_h": "#0b5ed7", "sec": "#ffffff", 
        "ttl": "#000000", "grd": "#6c757d", "ai_bg": "#ffffff"
    }
    anim_html = f"""<style>.orb-container {{position:fixed;top:0;left:0;width:100%;height:100%;overflow:hidden;z-index:-1;background:{col['bg']};}} .orb {{position:absolute;border-radius:50%;filter:blur(80px);opacity:0.2;animation:moveOrb 25s infinite alternate;}} .orb1 {{top:-10%;left:-10%;width:60vw;height:60vw;background:radial-gradient(circle,#0d6efd 0%,transparent 60%);}} .orb2 {{bottom:-10%;right:-10%;width:60vw;height:60vw;background:radial-gradient(circle,#6610f2 0%,transparent 60%);animation-duration:30s;}} @keyframes moveOrb {{0%{{transform:translate(0,0);}}100%{{transform:translate(30px,30px);}}}}</style><div class="orb-container"><div class="orb orb1"></div><div class="orb orb2"></div></div>"""

st.markdown(anim_html, unsafe_allow_html=True)

st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Inter:wght@400;600;800&display=swap');
        .stApp {{ background: transparent !important; }}
        header, footer, #MainMenu {{display: none !important;}}
        .block-container {{padding-top: 1.5rem; padding-bottom: 3rem;}}
        h1, h2, h3, h4, h5, h6, p, li, div, span, label {{ color: {col['txt']} !important; font-family: 'Inter', sans-serif; }}
        .calendar-container {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-top: 15px; }}
        .day-cell {{ background-color: {col['sec']}; border: 1px solid {col['bd']}; border-radius: 4px; height: 80px; padding: 4px; display: flex; flex-direction: column; justify-content: space-between; }}
        .day-number {{ font-weight: bold; font-size: 0.9rem; opacity: 0.7; }}
        .day-profit {{ font-size: 0.9rem; font-weight: 800; align-self: center; }}
        @media only screen and (max-width: 600px) {{
            .calendar-container {{ gap: 2px; }}
            .day-cell {{ height: 50px !important; padding: 2px !important; }}
            .day-number {{ font-size: 0.7rem !important; }}
            .day-profit {{ font-size: 0.6rem !important; }}
            .neon-title {{ font-size: 1.8rem !important; }}
        }}
        .neon-title {{ font-family: 'Orbitron', sans-serif; font-size: 3.5rem; text-align: center; color: {col['ttl']} !important; font-weight: 900; letter-spacing: 4px; margin: 0; {f"text-shadow: 0 0 20px {col['ac']};" if st.session_state.theme == "Dark" else ""} animation: pulse 3s infinite alternate; }}
        .metric-container {{ background-color: {col['card']}; border: 1px solid {col['bd']}; border-radius: 10px; padding: 15px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
        .metric-value {{ font-size: 2rem; font-weight: 700; color: {col['ttl']} !important; }}
        .metric-label {{ font-size: 0.8rem; color: {col['grd']} !important; font-weight: 600; letter-spacing: 1px; }}
        .ai-card {{ background-color: {col['ai_bg']}; border: 1px solid {col['bd']}; border-left-width: 6px; border-left-style: solid; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); }}
        .ai-header {{ font-size: 1.6rem; font-weight: 800; color: {col['ttl']} !important; margin-bottom: 5px; }}
        .ai-sub {{ font-size: 0.9rem; margin-bottom: 20px; font-weight: 600; }}
        .ai-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
        .ai-item {{ padding: 5px 0; }}
        .ai-label {{ font-size: 0.85rem; color: {col['grd']} !important; margin-bottom: 3px; }}
        .ai-val {{ font-size: 1.2rem; font-weight: 800; color: {col['ttl']} !important; }}
        .ai-decision {{ font-size: 1.8rem; font-weight: 900; text-align: left; margin-top: 15px; display: flex; align-items: center; gap: 10px; }}
        .day-win {{ background: rgba(0, 255, 204, 0.15); border-color: {col['ac']}; }}
        .day-win-light {{ background: rgba(13, 110, 253, 0.15); border-color: {col['ac']}; }}
        .day-loss {{ background: rgba(255, 75, 75, 0.15); border-color: #ff4b4b; }}
        .win-text {{ color: {col['ac']} !important; }} .loss-text {{ color: #ff4b4b !important; }} .empty-cell {{ background: transparent; border: none; }}
        .stTabs [data-baseweb="tab"] {{ color: {col['grd']} !important; }}
        .stTabs [aria-selected="true"] {{ color: {col['ac']} !important; border-bottom-color: {col['ac']} !important; }}
        .custom-btn {{ background-color: {col['ac']}; color: {col['bg']} !important; padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; display: block; text-align: center; }}
        .custom-btn-outline {{ border: 1px solid {col['ac']}; color: {col['ac']} !important; background: transparent; }}
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{ background-color: {col['sec']}; color: {col['txt']}; border-color: {col['bd']}; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. VERİ YÜKLEME (ORİJİNAL - BOZULMAMIŞ HALİ)
# ==========================================
@st.cache_data(ttl=60)
def load_data():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in st.secrets: creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        else: creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds); sheet = client.open("Crazytown_Journal").sheet1; data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            if 'R_Kazanc' in df.columns: df['R_Kazanc'] = df['R_Kazanc'].astype(str).str.replace(',', '.'); df['R_Kazanc'] = pd.to_numeric(df['R_Kazanc'], errors='coerce').fillna(0)
            return df
    except: pass
    
    # EĞER GSHEET BAĞLANTISI YOKSA
    dates = pd.date_range(end=datetime.today(), periods=20)
    demo_data = {
        'Tarih': dates.strftime("%d.%m.%Y"),
        'Parite': ['BTC/USDT', 'ETH/USDT'] * 10,
        'Yön': ['LONG', 'SHORT'] * 10,
        'Sonuç': ['WIN', 'LOSS', 'WIN', 'WIN', 'LOSS'] * 4,
        'R_Kazanc': [2.5, -1, 3.0, 2.0, -1] * 4
    }
    return pd.DataFrame(demo_data)

# >>> BURASI ÖNEMLİ: ESKİ SİSTEM GİBİ DİREKT YÜKLÜYORUZ <<<
df = load_data()

# --- VERİ MOTORU ---
def get_crypto_data(symbol, timeframe):
    symbol = symbol.upper().strip()
    try:
        cg_map = {"BTC":"bitcoin","ETH":"ethereum","SOL":"solana","AVAX":"avalanche-2","DOGE":"dogecoin","XRP":"ripple","BNB":"binancecoin","ADA":"cardano","PEPE":"pepe","SHIB":"shiba-inu","SUI":"sui","DOT":"polkadot","TAO":"bittensor","WIF":"dogwifhat"}
        cg_id = cg_map.get(symbol, symbol.lower())
        if symbol not in cg_map:
            search_url = f"https://api.coingecko.com/api/v3/search?query={symbol}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp_s = requests.get(search_url, headers=headers, timeout=2).json()
            if resp_s.get("coins"): cg_id = resp_s["coins"][0]["id"]
        
        days = "1" if timeframe == "15m" else ("30" if timeframe == "1d" else "7")
        url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/ohlc?vs_currency=usd&days={days}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close'])
                df['time'] = pd.to_datetime(df['time'], unit='ms')
                return df, "CoinGecko API"
    except: pass

    try:
        import ccxt
        exchange = ccxt.binance()
        symbol_ccxt = f"{symbol}/USDT" if "/" not in symbol else symbol
        ohlcv = exchange.fetch_ohlcv(symbol_ccxt, timeframe=timeframe, limit=100)
        if ohlcv:
            df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            return df, "Binance API"
    except: pass
    return pd.DataFrame(), "Data Error"

wt = "light" if st.session_state.theme == "Light" else "dark"
components.html(f"""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>{{"symbols": [{{"proName": "BINANCE:BTCUSDT", "title": "Bitcoin"}}, {{"proName": "BINANCE:ETHUSDT", "title": "Ethereum"}}, {{"proName": "BINANCE:SOLUSDT", "title": "Solana"}}], "showSymbolLogo": true, "colorTheme": "{wt}", "isTransparent": true, "displayMode": "adaptive", "locale": "en"}}</script></div>""", height=50)

st.write("")
st.markdown('<div class="neon-title">CRAZYTOWN CAPITAL</div>', unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: {col['ac']}; letter-spacing: 2px; font-size: 0.9rem; margin-top: -5px; font-weight:bold;'>{t('title_sub')}</p>", unsafe_allow_html=True)
st.write("")

tab1, tab2, tab5, tab6, tab3, tab4 = st.tabs([t('perf'), t('acad'), t('ai_lab'), t('radar'), t('memb'), t('cont')])

# ==========================================
# TAB 1: PERFORMANS (ESKİ HALİNE DÖNDÜ)
# ==========================================
with tab1:
    # BURADA ARTIK KARIŞIK SEÇİMLER YOK. DİREKT 'df' GÖSTERİLİYOR.
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
            hc = ['<div class="calendar-container">']; dn = ['Pt', 'Sa', 'Ça', 'Pe', 'Cu', 'Ct', 'Pa'] if st.session_state.lang == "TR" else (['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
            for d in dn: hc.append(f'<div class="calendar-header">{d}</div>')
            mt = 0
            for w in cm:
                for d in w:
                    if d == 0: hc.append('<div class="day-cell empty-cell"></div>')
                    else:
                        v = dp.get(d, 0); mt += v; cc, pc, pt = "day-cell", "", "-"
                        if d in dp:
                            if v > 0: cc += " day-win" if st.session_state.theme == "Dark" else " day-win-light"; pc = "win-text"; pt = f"+{v:.1f}"
                            elif v < 0: cc += " day-loss"; pc = "loss-text"; pt = f"{v:.1f}"
                        hc.append(f'<div class="{cc}"><div class="day-number">{d}</div><div class="day-profit {pc}">{pt}</div></div>')
            hc.append('</div>'); st.markdown("".join(hc), unsafe_allow_html=True); st.markdown(f"<div style='text-align:center; margin-top:15px; font-size:1.2rem; font-weight:bold; color:{col['ac'] if mt>0 else '#ff4b4b'} !important'>{t('total_monthly')}: {mt:.2f}R</div>", unsafe_allow_html=True)
    except Exception as e: st.error(str(e))

    st.markdown("---"); st.subheader(t("roi_sim")); r1, r2, r3 = st.columns([1,1,2])
    with r1: cap = st.number_input("Capital", min_value=100, value=1000)
    with r2: risk = st.slider("Risk %", 0.5, 5.0, 2.0)
    prof = cap * (risk / 100) * net_r; bal = cap + prof; perc = (prof / cap) * 100
    with r3: st.markdown(f"""<div style="background:{col['card']}; padding:15px; border-radius:10px; border:1px solid {col['ac']}; text-align:center;"><span style="color:{col['grd']} !important">{t('proj_bal')}</span><br><span style="color:{col['ttl']} !important; font-size:2rem; font-weight:bold;">${bal:,.2f}</span><br><span style="color:{col['ac']} !important">(+${prof:,.2f} / +{perc:.1f}%)</span></div>""", unsafe_allow_html=True)
    
    st.markdown("---"); h, d = st.columns([4, 1])
    with h: st.markdown(f"##### {t('trade_log')}")
    with d: st.download_button(label=t("download"), data=df.to_csv(index=False).encode('utf-8'), file_name='log.csv', mime='text/csv')
    def hwin(row):
        win_color = col['ac'] if row['Sonuç'] == 'WIN' else '#ff4b4b'
        return [f'color: {win_color}; font-weight:bold' if c_name == 'Sonuç' else f'color: {col["txt"]}' for c_name in row.index]
    st.dataframe(df.style.apply(hwin, axis=1), use_container_width=True, hide_index=True)

# ==========================================
# TAB 2: AKADEMİ (GELİŞMİŞ)
# ==========================================
with tab2:
    st.write(""); st.markdown(f"<h2 style='text-align: center; color: {col['ac']} !important;'>{t('acad_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-style:italic;'>{t('acad_quote')}</p>", unsafe_allow_html=True)
    tab_a1, tab_a2, tab_a3, tab_a4 = st.tabs(["TEKNİK", "STRATEJİ", "PSİKOLOJİ", "RİSK"])
    with tab_a1: st.markdown(t('lesson_1_content'), unsafe_allow_html=True); st.info("💡 **PRO TIP:** Londra açılışındaki (10:00 TSİ) fake hareketlere dikkat et.")
    with tab_a2: st.markdown(t('lesson_2_content'), unsafe_allow_html=True); st.markdown(t('lesson_3_content'), unsafe_allow_html=True)
    with tab_a3: st.subheader(t('acad_psych')); st.markdown("""* **FOMO Yok:** Fiyat kaçarsa kovalamıyoruz.\n* **İntikam Trade'i Yok:** Stop olduktan sonra hemen işlem açmıyoruz.\n* **Sabır:** Setup oluşana kadar eller cebe.""")
    with tab_a4: st.subheader(t('acad_risk')); st.markdown("""### %1 - %2 KURALI\n* Her işlemde kasanın en fazla %2'sini riske at.\n* 1000$ kasa için Stop olduğunda kayıp max 20$ olmalı.\n### R:R ORANI\n* Minimum hedef 1:2 olmalı.""")

# ==========================================
# TAB 5: AI LAB
# ==========================================
with tab5:
    st.write(""); st.markdown(f"<h2 style='text-align: center; color: {col['ac']} !important;'>{t('ai_title')}</h2>", unsafe_allow_html=True)
    ai_c1, ai_c2, ai_c3 = st.columns([2, 1, 1])
    with ai_c1: user_symbol = st.text_input(t('ai_input_label'), value="TAO")
    with ai_c2: tf = st.selectbox("Timeframe", ["1h", "4h", "1d"])
    with ai_c3: st.write(""); run_analysis = st.button(t('run_ai'), key="ai_btn", use_container_width=True)

    if run_analysis:
        dec_col = "#888"; trend_text = "NEUTRAL"; decision = "WAIT"; score = 50
        with st.spinner(t('ai_analyzing')):
            live_df, source = get_crypto_data(user_symbol, tf); time.sleep(0.5)
        
        if not live_df.empty and len(live_df) > 20:
            current_price = float(live_df['close'].iloc[-1]); sma_val = float(live_df['close'].rolling(20).mean().iloc[-1])
            delta = live_df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean().fillna(0); loss = (-delta.where(delta < 0, 0)).rolling(14).mean().fillna(0); rs = gain / (loss + 0.0001); rsi_val = 100 - (100 / (1 + rs)).iloc[-1]
            ema12 = live_df['close'].ewm(span=12).mean(); ema26 = live_df['close'].ewm(span=26).mean(); macd_val = (ema12 - ema26).iloc[-1]; sig_val = (ema12 - ema26).ewm(span=9).mean().iloc[-1]
            supp = live_df['low'].tail(50).min(); res = live_df['high'].tail(50).max()

            score = 50
            if current_price > sma_val: score += 15
            if rsi_val > 50: score += 10
            if macd_val > sig_val: score += 15
            score = max(0, min(100, score))
            
            if score >= 80: decision = t('s_buy'); dec_col = "#00ff00"; trend_text = t('bull'); direction = "BULL"
            elif score >= 60: decision = t('buy'); dec_col = "#00cc00"; trend_text = t('bull'); direction = "BULL"
            elif score <= 20: decision = t('s_sell'); dec_col = "#ff0000"; trend_text = t('bear'); direction = "BEAR"
            elif score <= 40: decision = t('sell'); dec_col = "#cc0000"; trend_text = t('bear'); direction = "BEAR"
            else: decision = t('wait'); dec_col = "#aaaaaa"; trend_text = t('neutral'); direction = "NEUTRAL"

            st.markdown(f"""<div class="ai-card" style="border-left-color: {dec_col} !important;"><div style="display:flex; justify-content:space-between;"><div><div class="ai-header">{user_symbol.upper()} / USD</div></div><div class="ai-header">${current_price:,.4f}</div></div><hr style="border-color:{col['bd']}; margin:15px 0;"><div class="ai-grid"><div class="ai-item"><div class="ai-label">{t('ai_trend')}</div><div class="ai-val" style="color:{dec_col} !important">{trend_text}</div></div><div class="ai-item"><div class="ai-label">{t('ai_rsi')}</div><div class="ai-val">{rsi_val:.2f}</div></div><div class="ai-item"><div class="ai-label">{t('ai_supp')}</div><div class="ai-val">${supp:,.4f}</div></div><div class="ai-item"><div class="ai-label">{t('ai_res')}</div><div class="ai-val">${res:,.4f}</div></div></div><div class="ai-label" style="margin-top:25px;">{t('ai_score')}: {score}/100</div><div style="background:#333; border-radius:10px; height:10px; width:100%; margin-top:5px;"><div style="background: linear-gradient(90deg, #ff4b4b, #ffff00, #00ffcc); width:{score}%; height:100%;"></div></div><div class="ai-decision" style="border: 2px solid {dec_col}; color: {dec_col} !important;">{t('ai_dec')}: {decision}</div></div>""", unsafe_allow_html=True)
            
            # CHART
            fig_ai = go.Figure()
            last_50 = live_df.tail(50).reset_index(drop=True)
            fig_ai.add_trace(go.Scatter(x=last_50.index, y=last_50['close'], mode='lines', name='Price', line=dict(color=col['txt'], width=2)))
            fig_ai.update_layout(template="plotly_dark" if st.session_state.theme=="Dark" else "plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, margin=dict(l=0,r=0,t=20,b=0), xaxis=dict(showgrid=False))
            st.plotly_chart(fig_ai, use_container_width=True)
        else: st.error(t("err_msg"))

# ==========================================
# TAB 6: PIYASA RADARI (YENİ - COKLU ANALİZ)
# ==========================================
with tab6:
    st.write(""); st.markdown(f"<h2 style='text-align: center; color: {col['ac']} !important;'>CANLI PIYASA RADARI 📡</h2>", unsafe_allow_html=True)
    if st.button("RADARI BAŞLAT 🚀", use_container_width=True):
        target_coins = ["BTC", "ETH", "SOL", "AVAX", "BNB", "DOGE", "PEPE", "XRP"]; radar_results = []
        p_bar = st.progress(0); status_txt = st.empty()
        for i, sym in enumerate(target_coins):
            status_txt.markdown(f"**{sym}** analiz ediliyor... ⏳")
            try:
                r_df, _ = get_crypto_data(sym, "4h")
                if not r_df.empty and len(r_df) > 30:
                    curr = r_df['close'].iloc[-1]; sma20 = r_df['close'].rolling(20).mean().iloc[-1]; rsi_now = (100 - (100 / (1 + (r_df['close'].diff().where(r_df['close'].diff() > 0, 0).rolling(14).mean() / (-r_df['close'].diff().where(r_df['close'].diff() < 0, 0).rolling(14).mean() + 0.0001))))).iloc[-1]
                    r_score = 50
                    if curr > sma20: r_score += 15
                    if rsi_now < 30: r_score += 20
                    elif rsi_now > 70: r_score -= 10
                    r_score = max(0, min(100, r_score))
                    r_status = "AL 🟢" if r_score >= 60 else ("SAT 🔴" if r_score <= 40 else "NÖTR ⚪")
                    r_color = "#00ff00" if r_score >= 60 else ("#ff0000" if r_score <= 40 else "#aaaaaa")
                    radar_results.append({"Symbol": sym, "Price": curr, "RSI": rsi_now, "Score": r_score, "Status": r_status, "Color": r_color})
            except: pass
            p_bar.progress((i + 1) / len(target_coins)); time.sleep(0.1)
        p_bar.empty(); status_txt.empty()
        radar_results.sort(key=lambda x: x['Score'], reverse=True)
        for res in radar_results:
            st.markdown(f"""<div style="background:{col['sec']}; border:1px solid {col['bd']}; border-left:5px solid {res['Color']}; border-radius:8px; padding:15px; margin-bottom:10px; display:flex; align-items:center; justify-content:space-between;"><div style="width:15%; font-weight:900; font-size:1.1rem; color:{col['ttl']}">{res['Symbol']}</div><div style="width:25%; font-family:monospace; font-size:1rem;">${res['Price']:,.3f}</div><div style="width:20%; font-size:0.9rem; color:{col['grd']}">RSI: {res['RSI']:.1f}</div><div style="width:25%; text-align:right; font-weight:bold; color:{res['Color']}">{res['Status']}</div><div style="width:15%; text-align:right;"><span style="background:{res['Color']}; color:black; padding:2px 8px; border-radius:10px; font-weight:bold; font-size:0.8rem;">{res['Score']}</span></div></div>""", unsafe_allow_html=True)

# ==========================================
# TAB 3: ÜYELİK (GLASSMORPHISM)
# ==========================================
with tab3:
    st.write("")
    st.markdown(f"<h2 style='text-align:center;'>{t('memb')}</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"""<div class="glass-card"><h3 style="color:{col['txt']}">{t('plan_starter')}</h3><div class="price-tag">$30</div><div class="plan-desc">{t('plan_starter_desc')}</div><a href="#" class="custom-btn custom-btn-outline">{t('sel_plan')}</a></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div class="glass-card" style="border-color:{col['ac']}; background:rgba(0, 255, 204, 0.05);"><h3 style="color:{col['txt']}">{t('plan_pro')}</h3><div class="price-tag">$75</div><div class="plan-desc">{t('plan_pro_desc')}</div><a href="#" class="custom-btn">{t('sel_plan')}</a></div>""", unsafe_allow_html=True)
    with c3: st.markdown(f"""<div class="glass-card"><h3 style="color:{col['txt']}">{t('plan_life')}</h3><div class="price-tag">$250</div><div class="plan-desc">{t('plan_life_desc')}</div><a href="#" class="custom-btn custom-btn-outline">{t('contact_sales')}</a></div>""", unsafe_allow_html=True)

# ==========================================
# TAB 4: İLETİŞİM
# ==========================================
with tab4:
    st.write(""); c1, c2 = st.columns(2)
    with c1: st.markdown(f"""### 📨 Telegram\n<a href="https://t.me/Orhan1909" class="custom-btn">OPEN TELEGRAM</a>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""### 📧 Email\n**orhanaliyev02@gmail.com**""")

# ==========================================
# FOOTER & YASAL UYARI
# ==========================================
st.markdown("---")
with st.expander(f"⚖️ {t('legal_title')}", expanded=False):
    st.markdown(f"""<div style="font-size: 0.8rem; color: {col['grd']}; text-align: justify;"><p><strong>YASAL UYARI:</strong> {t('legal_text')}</p><p><strong>KVKK:</strong> Kişisel veriler sadece eğitim amaçlı ve tarayıcı önbelleğinde tutulur.</p></div>""", unsafe_allow_html=True)

def accept_legal(): st.session_state.legal_accepted = True
if not st.session_state.legal_accepted:
    st.warning("⚠️ " + t('legal_title'))
    st.checkbox(t('accept_terms'), key="legal_cb", on_change=accept_legal)
    
st.markdown(f"<p style='text-align: center; color: {col['ac_h']} !important; font-size: 0.8rem; margin-top:20px;'>© 2025 Crazytown Capital. All rights reserved.</p>", unsafe_allow_html=True)
