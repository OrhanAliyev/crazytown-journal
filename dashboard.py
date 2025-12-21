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
import ccxt 

# ==========================================
# 0. AYARLAR VE KÜTÜPHANE KONTROLÜ
# ==========================================
st.set_page_config(
    page_title="Crazytown Capital",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SESSION STATE BAŞLATMA (Kişisel veriler için)
if 'personal_trades' not in st.session_state:
    st.session_state.personal_trades = pd.DataFrame(columns=['Tarih', 'Parite', 'Yön', 'Sonuç', 'R_Kazanc'])
if 'calendar_mode' not in st.session_state:
    st.session_state.calendar_mode = 'System'
if 'terms_accepted' not in st.session_state:
    st.session_state.terms_accepted = False
if 'lang' not in st.session_state: st.session_state.lang = "TR"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"

# ==========================================
# 1. ÇEVİRİ VE İÇERİK
# ==========================================
TRANSLATIONS = {
    "EN": {
        "title_sub": "ALGORITHMIC TRADING SYSTEMS", "perf": "PERFORMANCE", "acad": "ACADEMY", "memb": "MEMBERSHIP", "cont": "CONTACT", "ai_lab": "AI LAB",
        "total_trades": "TOTAL TRADES", "win_rate": "WIN RATE", "net_return": "NET RETURN", "profit_factor": "PROFIT FACTOR",
        "season_goal": "SEASON GOAL", "completed": "COMPLETED", "perf_cal": "🗓️ PERFORMANCE CALENDAR",
        "select_month": "Select Month", "total_monthly": "TOTAL MONTHLY PNL",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "Real-time market scanning with explainable AI logic.",
        "run_ai": "SCAN MARKET", "ai_analyzing": "Analyzing Order Flow...", 
        "ai_input_label": "Enter Symbol (e.g. BTC, ETH, SOL)",
        "ai_trend": "Trend", "ai_rsi": "RSI", "ai_supp": "Support", "ai_res": "Resistance",
        "ai_score": "Confidence", "ai_dec": "AI DECISION", "ai_explanation": "📝 AI LOGIC & EXPLANATION",
        "bull": "BULLISH 🟢", "bear": "BEARISH 🔴", "neutral": "NEUTRAL ⚪",
        "s_buy": "STRONG BUY 🚀", "buy": "BUY 🟢", "sell": "SELL 🔴", "s_sell": "STRONG SELL 🔻", "wait": "WAIT ✋",
        "cal_mode_sys": "SYSTEM DATA", "cal_mode_per": "MY TRADING JOURNAL", "add_trade": "➕ Add New Trade",
        "legal_title": "LEGAL DISCLAIMER & KVKK", "accept_terms": "I have read and accept the terms.",
        "acad_1": "1. MARKET STRUCTURE", "acad_1_text": "Market structure is the king...",
        "acad_2": "2. LIQUIDITY CONCEPTS", "acad_2_text": "Liquidity drives the market...",
        "acad_3": "3. ENTRY MODELS", "acad_3_text": "Golden pocket entries...",
        "memb_title": "CHOOSE YOUR PLAN", "memb_1": "STARTER", "memb_2": "PRO TRADER", "memb_3": "LIFETIME",
        "err_msg": "Coin not found."
    },
    "TR": {
        "title_sub": "ALGORİTMİK İŞLEM SİSTEMLERİ", "perf": "PERFORMANS", "acad": "AKADEMİ", "memb": "ÜYELİK", "cont": "İLETİŞİM", "ai_lab": "YAPAY ZEKA",
        "total_trades": "TOPLAM İŞLEM", "win_rate": "BAŞARI ORANI", "net_return": "NET GETİRİ", "profit_factor": "KÂR FAKTÖRÜ",
        "season_goal": "SEZON HEDEFİ", "completed": "TAMAMLANDI", "perf_cal": "🗓️ PERFORMANS TAKVİMİ",
        "select_month": "Ay Seçiniz", "total_monthly": "AYLIK TOPLAM PNL",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "Açıklamalı yapay zeka mantığı ile canlı analiz.",
        "run_ai": "TARA VE ANALİZ ET", "ai_analyzing": "Emir Defteri Taranıyor...", 
        "ai_input_label": "Coin Sembolü (Örn: BTC, ETH, TAO)",
        "ai_trend": "Genel Trend", "ai_rsi": "RSI Göstergesi", "ai_supp": "Tahmini Destek", "ai_res": "Tahmini Direnç",
        "ai_score": "Güven Skoru", "ai_dec": "YZ KARARI", "ai_explanation": "📝 ANALİZ NEDENİ & MANTIK",
        "bull": "BOĞA (YÜKSELİŞ) 🟢", "bear": "AYI (DÜŞÜŞ) 🔴", "neutral": "NÖTR ⚪",
        "s_buy": "GÜÇLÜ AL 🚀", "buy": "AL 🟢", "sell": "SAT 🔴", "s_sell": "GÜÇLÜ SAT 🔻", "wait": "BEKLE ✋",
        "cal_mode_sys": "SİSTEM VERİLERİ", "cal_mode_per": "KİŞİSEL GÜNLÜĞÜM", "add_trade": "➕ Yeni İşlem Ekle",
        "legal_title": "YASAL UYARI, SORUMLULUK BEYANI VE KVKK", "accept_terms": "Yukarıdaki yasal metni okudum, anladım ve kabul ediyorum.",
        "acad_1": "1. PİYASA YAPISI (MARKET STRUCTURE)", "acad_1_text": "**Piyasa Yapısı Kraldır.**\n\nFiyatın ne yaptığını anlamadan indikatör kullanmak kör uçuş yapmaktır.\n\n* **BOS (Break of Structure):** Trend yönünde kırılım.\n* **CHoCH (Change of Character):** Trendin değiştiğinin ilk sinyali.\n* **Strong High/Low:** Likidite alıp BOS yaptıran tepe/dip.",
        "acad_2": "2. LİKİDİTE KAVRAMLARI", "acad_2_text": "**Para Kaybedenlerin Stopları Bizim Yakıtımızdır.**\n\nKurumsal yapılar (Bankalar, Fonlar) işlem açmak için sizin stop emirlerinize ihtiyaç duyar.\n\n* **BSL (Buy Side Liquidity):** Tepelerin üzerindeki stoplar.\n* **SSL (Sell Side Liquidity):** Diplerin altındaki stoplar.\n* **Equal Highs/Lows:** Çift tepe/dip formasyonları birer tuzaktır.",
        "acad_3": "3. GİRİŞ MODELLERİ (ENTRY)", "acad_3_text": "**Sniper Giriş Stratejisi.**\n\n1.  Günlükte (HTF) likidite alımı bekle (Sweep).\n2.  Fiyatın tersine dönmesini bekleme, sadece likidite bölgesine tepki bekle.\n3.  **Fibonacci:** Swing hareketin tepesinden dibine çek.\n4.  **Golden Pocket:** 0.618 ile 0.786 arasına emir at.",
        "memb_title": "PLANINI SEÇ", "memb_1": "BAŞLANGIÇ", "memb_2": "PROFESYONEL", "memb_3": "ÖMÜR BOYU (VIP)",
        "err_msg": "Coin bulunamadı. Lütfen sembolü kontrol edin."
    },
    "RU": {
        "title_sub": "АЛГОРИТМИЧЕСКИЕ ТОРГОВЫЕ СИСТЕМЫ", "perf": "ЭФФЕКТИВНОСТЬ", "acad": "АКАДЕМИЯ", "memb": "ПОДПИСКА", "cont": "КОНТАКТЫ", "ai_lab": "ИИ ЛАБОРАТОРИЯ",
        "total_trades": "ВСЕГО СДЕЛОК", "win_rate": "ВИНРЕЙТ", "net_return": "ЧИСТАЯ ПРИБЫЛЬ", "profit_factor": "ПРОФИТ-ФАКТОР",
        "season_goal": "ЦЕЛЬ СЕЗОНА", "completed": "ЗАВЕРШЕНО", "perf_cal": "🗓️ КАЛЕНДАРЬ",
        "select_month": "Выберите месяц", "total_monthly": "ИТОГ МЕСЯЦА PNL",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "ИИ анализ в реальном времени.",
        "run_ai": "АНАЛИЗ", "ai_analyzing": "Сканирование...", 
        "ai_input_label": "Символ (BTC, ETH...)",
        "ai_trend": "Тренд", "ai_rsi": "RSI", "ai_supp": "Поддержка", "ai_res": "Сопротивление",
        "ai_score": "Оценка", "ai_dec": "РЕШЕНИЕ", "ai_explanation": "📝 ОБЪЯСНЕНИЕ",
        "bull": "БЫЧИЙ 🟢", "bear": "МЕДВЕЖИЙ 🔴", "neutral": "НЕЙТРАЛЬНО ⚪",
        "s_buy": "СИЛЬНАЯ ПОКУПКА 🚀", "buy": "ПОКУПАТЬ 🟢", "sell": "ПРОДАВАТЬ 🔴", "s_sell": "СИЛЬНАЯ ПРОДАЖ 🔻", "wait": "ЖДАТЬ ✋",
        "cal_mode_sys": "СИСТЕМА", "cal_mode_per": "МОЙ ЖУРНАЛ", "add_trade": "➕ Добавить",
        "legal_title": "ЮРИДИЧЕСКИЙ ОТКАЗ", "accept_terms": "Я принимаю условия.",
        "acad_1": "1. СТРУКТУРА РЫНКА", "acad_1_text": "Понимание структуры...",
        "acad_2": "2. ЛИКВИДНОСТЬ", "acad_2_text": "Ликвидность - это топливо...",
        "acad_3": "3. ВХОД", "acad_3_text": "Стратегия входа...",
        "memb_title": "ВЫБЕРИТЕ ПЛАН", "memb_1": "СТАРТ", "memb_2": "ПРОФИ", "memb_3": "LIFETIME",
        "err_msg": "Монета не найдена."
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
# 2. DİNAMİK RENK VE CSS
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
        .block-container {{padding-top: 1rem; padding-bottom: 3rem;}}
        
        /* MOBİL UYUM */
        @media only screen and (max-width: 600px) {{
            .calendar-container {{ gap: 2px !important; }}
            .day-cell {{ height: 50px !important; padding: 2px !important; }}
            .day-number {{ font-size: 0.7rem !important; }}
            .day-profit {{ font-size: 0.6rem !important; }}
            .neon-title {{ font-size: 1.8rem !important; }}
            .pro-grid, .ai-grid {{ grid-template-columns: 1fr !important; }}
            .membership-grid {{ grid-template-columns: 1fr !important; }}
        }}

        h1, h2, h3, h4, h5, h6, p, li, div, span, label {{ color: {col['txt']} !important; font-family: 'Inter', sans-serif; }}
        .neon-title {{ font-family: 'Orbitron', sans-serif; font-size: 3.5rem; text-align: center; color: {col['ttl']} !important; font-weight: 900; letter-spacing: 4px; margin: 0; {f"text-shadow: 0 0 20px {col['ac']};" if st.session_state.theme == "Dark" else ""} animation: pulse 3s infinite alternate; }}
        .metric-container {{ background-color: {col['card']}; border: 1px solid {col['bd']}; border-radius: 10px; padding: 15px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
        .metric-value {{ font-size: 2rem; font-weight: 700; color: {col['ttl']} !important; }}
        .metric-label {{ font-size: 0.8rem; color: {col['grd']} !important; font-weight: 600; letter-spacing: 1px; }}
        
        .ai-card {{ background-color: {col['ai_bg']}; border: 1px solid {col['bd']}; border-left-width: 6px; border-left-style: solid; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .ai-header {{ font-size: 1.6rem; font-weight: 800; color: {col['ttl']} !important; }}
        .ai-sub {{ font-size: 0.9rem; font-weight: 600; }}
        .ai-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
        .ai-label {{ font-size: 0.85rem; color: {col['grd']} !important; }}
        .ai-val {{ font-size: 1.2rem; font-weight: 800; color: {col['ttl']} !important; }}
        .ai-decision {{ font-size: 1.8rem; font-weight: 900; text-align: center; margin-top: 15px; padding: 10px; border-radius: 8px; }}
        
        .explanation-box {{ background: rgba(255, 255, 255, 0.05); border-left: 3px solid {col['ac']}; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 0.9rem; }}

        .membership-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 20px; }}
        .pricing-card {{ background-color: {col['card']}; border: 1px solid {col['bd']}; border-radius: 12px; padding: 30px; text-align: center; transition: transform 0.2s; }}
        .pricing-card:hover {{ transform: scale(1.02); border-color: {col['ac']}; }}
        
        .calendar-container {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-top: 15px; }}
        .day-cell {{ background-color: {col['sec']}; border: 1px solid {col['bd']}; border-radius: 4px; height: 80px; padding: 4px; display: flex; flex-direction: column; justify-content: space-between; }}
        .day-number {{ font-weight: bold; font-size: 0.9rem; opacity: 0.7; }}
        .day-profit {{ font-size: 0.9rem; font-weight: 800; align-self: center; }}
        .day-win {{ background: rgba(0, 255, 204, 0.15); border-color: {col['ac']}; }}
        .day-loss {{ background: rgba(255, 75, 75, 0.15); border-color: #ff4b4b; }}
        .win-text {{ color: {col['ac']} !important; }} .loss-text {{ color: #ff4b4b !important; }}
        
        .custom-btn {{ background-color: {col['ac']}; color: {col['bg']} !important; padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; display: block; text-align: center; }}
        .custom-btn-outline {{ border: 1px solid {col['ac']}; color: {col['ac']} !important; background: transparent; }}
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{ background-color: {col['sec']}; color: {col['txt']}; border-color: {col['bd']}; }}
        
        /* FOOTER LEGAL */
        .legal-footer {{ margin-top: 50px; padding: 20px; border-top: 1px solid {col['bd']}; font-size: 0.7rem; color: {col['grd']} !important; text-align: justify; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. VERİ YÜKLEME (SİSTEM VE KİŞİSEL)
# ==========================================
def load_system_data():
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
    return pd.DataFrame() # BOŞ DÖNER, DEMO YOK

def get_market_data(symbol, interval):
    symbol = symbol.upper().strip()
    try:
        cg_map = {"BTC":"bitcoin", "ETH":"ethereum", "SOL":"solana", "AVAX":"avalanche-2", "DOGE":"dogecoin", "XRP":"ripple", "BNB":"binancecoin", "ADA":"cardano", "PEPE":"pepe", "SHIB":"shiba-inu", "SUI":"sui", "DOT":"polkadot", "TAO":"bittensor", "WIF":"dogwifhat"}
        if symbol in cg_map: cg_id = cg_map[symbol]
        else:
            search = requests.get(f"https://api.coingecko.com/api/v3/search?query={symbol}", timeout=2).json()
            cg_id = search["coins"][0]["id"] if search.get("coins") else None
        
        if cg_id:
            days = "1" if interval == "15m" else ("30" if interval == "1d" else "7")
            data = requests.get(f"https://api.coingecko.com/api/v3/coins/{cg_id}/ohlc?vs_currency=usd&days={days}", timeout=3).json()
            if data:
                df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close'])
                df['time'] = pd.to_datetime(df['time'], unit='ms')
                return df, "CoinGecko"
    except: pass
    
    try:
        exchange = ccxt.binance()
        target = f"{symbol}/USDT" if "/" not in symbol else symbol
        ohlcv = exchange.fetch_ohlcv(target, timeframe='1h' if interval=='1h' else ('4h' if interval=='4h' else '1d'), limit=100)
        if ohlcv:
            df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            return df, "Binance"
    except: pass
    return pd.DataFrame(), None

# ==========================================
# 4. ARAYÜZ
# ==========================================
wt = "light" if st.session_state.theme == "Light" else "dark"
components.html(f"""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>{{"symbols": [{{"proName": "BINANCE:BTCUSDT", "title": "Bitcoin"}}, {{"proName": "BINANCE:ETHUSDT", "title": "Ethereum"}}, {{"proName": "BINANCE:SOLUSDT", "title": "Solana"}}], "showSymbolLogo": true, "colorTheme": "{wt}", "isTransparent": true, "displayMode": "adaptive", "locale": "en"}}</script></div>""", height=50)

st.write("")
st.markdown('<div class="neon-title">CRAZYTOWN CAPITAL</div>', unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: {col['ac']}; letter-spacing: 2px; font-size: 0.9rem; margin-top: -5px; font-weight:bold;'>{t('title_sub')}</p>", unsafe_allow_html=True)
st.write("")

tab1, tab2, tab5, tab3, tab4 = st.tabs([t('perf'), t('acad'), t('ai_lab'), t('memb'), t('cont')])

# TAB 1: PERFORMANS (ÇİFT MODLU)
with tab1:
    # MOD SEÇİMİ (BUTONLAR)
    c_btn1, c_btn2 = st.columns(2)
    if c_btn1.button(t('cal_mode_sys'), use_container_width=True, type="primary" if st.session_state.calendar_mode=='System' else "secondary"):
        st.session_state.calendar_mode = 'System'
        st.rerun()
    if c_btn2.button(t('cal_mode_per'), use_container_width=True, type="primary" if st.session_state.calendar_mode=='Personal' else "secondary"):
        st.session_state.calendar_mode = 'Personal'
        st.rerun()

    # VERİ SEÇİMİ
    if st.session_state.calendar_mode == 'System':
        df = load_system_data()
        if df.empty:
            st.warning("⚠️ Sistem verisi çekilemedi. Lütfen internet bağlantısını veya 'credentials.json' dosyasını kontrol edin. Demo veri gösterilmiyor.")
    else:
        # KİŞİSEL VERİ GİRİŞİ
        with st.expander(t('add_trade')):
            with st.form("trade_form"):
                d1, d2, d3, d4 = st.columns(4)
                t_date = d1.date_input("Tarih")
                t_pair = d2.text_input("Parite (BTC/USDT)")
                t_res = d3.selectbox("Sonuç", ["WIN", "LOSS"])
                t_r = d4.number_input("R Kazanç", value=0.0, step=0.1)
                if st.form_submit_button("KAYDET"):
                    new_trade = pd.DataFrame({'Tarih': [t_date.strftime("%d.%m.%Y")], 'Parite': [t_pair], 'Yön': ['-'], 'Sonuç': [t_res], 'R_Kazanc': [t_r]})
                    st.session_state.personal_trades = pd.concat([st.session_state.personal_trades, new_trade], ignore_index=True)
                    st.success("İşlem Eklendi!")
                    st.rerun()
        df = st.session_state.personal_trades

    # GÖSTERGE PANELİ (EĞER VERİ VARSA)
    if not df.empty:
        tot = len(df); win = len(df[df['Sonuç'] == 'WIN']); rate = (win / tot * 100) if tot > 0 else 0; net_r = df['R_Kazanc'].sum()
        gp = df[df['R_Kazanc'] > 0]['R_Kazanc'].sum(); gl = abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum()); pf = (gp / gl) if gl > 0 else 0
        nc = col['ac'] if net_r > 0 else "#ff4b4b"
        
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="metric-container"><div class="metric-value">{tot}</div><div class="metric-label">{t("total_trades")}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-container"><div class="metric-value">{rate:.1f}%</div><div class="metric-label">{t("win_rate")}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-container"><div class="metric-value" style="color:{nc} !important">{net_r:.2f}R</div><div class="metric-label">{t("net_return")}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-container"><div class="metric-value">{pf:.2f}</div><div class="metric-label">{t("profit_factor")}</div></div>', unsafe_allow_html=True)
        st.write(""); st.write("")
        
        # TAKVİM
        st.markdown("---"); st.subheader(t("perf_cal"))
        try:
            df['Tarih_Dt'] = pd.to_datetime(df['Tarih'], dayfirst=True, errors='coerce'); df.dropna(subset=['Tarih_Dt'], inplace=True)
            if not df.empty:
                df = df.sort_values('Tarih_Dt'); ms = df['Tarih_Dt'].dt.strftime('%Y-%m').unique(); sm = st.selectbox(t("select_month"), options=ms, index=len(ms)-1)
                y, m = map(int, sm.split('-')); md = df[df['Tarih_Dt'].dt.strftime('%Y-%m') == sm].copy(); dp = md.groupby(md['Tarih_Dt'].dt.day)['R_Kazanc'].sum().to_dict(); cm = calendar.monthcalendar(y, m)
                hc = ['<div class="calendar-container">']; dn = ['Pt', 'Sa', 'Ça', 'Pe', 'Cu', 'Ct', 'Pa']
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
        except Exception as e: st.error(f"Takvim Hatası: {e}")
    elif st.session_state.calendar_mode == 'Personal':
        st.info("Henüz işlem eklemediniz. Yukarıdan 'Yeni İşlem Ekle' butonunu kullanın.")

# TAB 2: AKADEMİ (DETAYLI & ÇOK DİLLİ)
with tab2:
    st.markdown(f"<h2 style='text-align: center; color: {col['ac']} !important;'>{t('acad_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"""<div style="text-align: center; font-style: italic; color: {col['grd']} !important; margin-bottom: 20px;">"{t('acad_quote')}"</div>""", unsafe_allow_html=True)
    with st.expander(t('acad_1'), expanded=True): st.markdown(t('acad_1_text'))
    with st.expander(t('acad_2')): st.markdown(t('acad_2_text'))
    with st.expander(t('acad_3')): st.markdown(t('acad_3_text'))

# TAB 5: AI LAB (AÇIKLAMALI & CANLI VERİ)
with tab5:
    st.write("")
    st.markdown(f"<h2 style='text-align: center; color: {col['ac']} !important;'>{t('ai_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"""<div style="text-align: center; font-style: italic; color: {col['grd']} !important; margin-bottom: 20px;">{t('ai_desc')}</div>""", unsafe_allow_html=True)
    
    ai_c1, ai_c2, ai_c3 = st.columns([2, 1, 1])
    with ai_c1: user_symbol = st.text_input(t('ai_input_label'), value="TAO")
    with ai_c2: tf = st.selectbox("Zaman Dilimi", ["1h", "4h", "1d"])
    with ai_c3:
        st.write("")
        run_analysis = st.button(t('run_ai'), key="ai_btn", use_container_width=True)

    if run_analysis:
        # DEFAULT DEĞERLER (Safety)
        dec_col = "#888"; trend_text = "-"; decision = "-"; score = 50; reason_list = []
        with st.spinner(t('ai_analyzing')):
            live_df, source = get_market_data(user_symbol, tf)
            time.sleep(0.5) 
        
        if not live_df.empty and len(live_df) > 20:
            current_price = float(live_df['close'].iloc[-1])
            live_df['SMA'] = live_df['close'].rolling(20).mean()
            sma_val = float(live_df['SMA'].iloc[-1])
            delta = live_df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / (loss + 0.0001); live_df['RSI'] = 100 - (100 / (1 + rs))
            rsi_val = float(live_df['RSI'].iloc[-1])
            
            # --- MANTIK VE AÇIKLAMA ---
            score = 50
            if current_price > sma_val:
                score += 20; reason_list.append(f"✅ Fiyat SMA20 üzerinde (Pozitif Trend).")
            else:
                score -= 20; reason_list.append(f"⚠️ Fiyat SMA20 altında (Negatif Trend).")
            
            if rsi_val > 55:
                score += 10; reason_list.append(f"✅ RSI {rsi_val:.1f} (Güçlü Momentum).")
            elif rsi_val < 45:
                score -= 10; reason_list.append(f"⚠️ RSI {rsi_val:.1f} (Zayıf Momentum).")
            else:
                reason_list.append(f"ℹ️ RSI {rsi_val:.1f} (Nötr Bölge).")
            
            score = max(0, min(100, score))
            if score >= 60: decision = t('buy'); dec_col = "#00ff00"; trend_text = t('bull')
            elif score <= 40: decision = t('sell'); dec_col = "#ff0000"; trend_text = t('bear')
            else: decision = t('wait'); dec_col = "#aaaaaa"; trend_text = t('neutral')
            
            explanation_html = "".join([f"<li>{r}</li>" for r in reason_list])

            # HTML OUTPUT
            html_card = f"""
            <div class="ai-card" style="border-left-color: {dec_col} !important;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><div class="ai-header">{user_symbol.upper()} / USD</div></div>
                    <div style="text-align:right;"><div class="ai-header">${current_price:,.2f}</div></div>
                </div>
                <hr style="border-color: {col['bd']}; margin: 15px 0;">
                <div class="ai-grid">
                    <div class="ai-item"><div class="ai-label">{t('ai_trend')}</div><div class="ai-val" style="color:{dec_col} !important">{trend_text}</div></div>
                    <div class="ai-item"><div class="ai-label">{t('ai_rsi')}</div><div class="ai-val">{rsi_val:.1f}</div></div>
                </div>
                <div class="ai-decision" style="border: 2px solid {dec_col}; color: {dec_col} !important;">{t('ai_dec')}: {decision}</div>
                <div class="explanation-box">
                    <div style="font-weight:bold; margin-bottom:5px; color:{col['ac']}">{t('ai_explanation')}</div>
                    <ul style="margin:0; padding-left:20px;">{explanation_html}</ul>
                </div>
            </div>
            """
            st.markdown(html_card, unsafe_allow_html=True)
            st.caption(f"{t('data_source')}: {source}")
        else:
            st.error(t("err_msg"))

# TAB 3: MEMBERSHIP (ŞIK TASARIM)
with tab3:
    st.write(""); st.markdown(f"<h2 style='text-align:center; color:{col['ttl']}'>{t('memb_title')}</h2>", unsafe_allow_html=True)
    st.markdown('<div class="membership-grid">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"""<div class="pricing-card"><div class="plan-name">{t('memb_1')}</div><div class="plan-price">$30<span style="font-size:1rem;color:{col['grd']} !important">/mo</span></div><a href="#" class="custom-btn custom-btn-outline">{t('sel_plan')}</a></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div class="pricing-card" style="border-color:{col['ac']}"><div class="plan-name">{t('memb_2')}</div><div class="plan-price">$75<span style="font-size:1rem;color:{col['grd']} !important">/qtr</span></div><a href="#" class="custom-btn">{t('most_pop')}</a></div>""", unsafe_allow_html=True)
    with c3: st.markdown(f"""<div class="pricing-card"><div class="plan-name">{t('memb_3')}</div><div class="plan-price">$250<span style="font-size:1rem;color:{col['grd']} !important">/once</span></div><a href="#" class="custom-btn custom-btn-outline">{t('contact_sales')}</a></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# FOOTER: YASAL UYARI & KVKK (TÜRKİYE MEVZUATI)
st.markdown("---")
st.markdown(f"""
<div class="legal-footer">
    <h4 style="color:{col['txt']}; text-align:center;">{t('legal_title')}</h4>
    <p>
    <b>1. YASAL UYARI (SPK MEVZUATI):</b> Bu platformda (Crazytown Capital) yer alan her türlü bilgi, analiz, grafik ve yorumlar sadece eğitim ve genel bilgilendirme amaçlıdır. 
    <b>Kesinlikle "Yatırım Tavsiyesi" (Al-Sat-Tut sinyali) değildir.</b> 6362 sayılı Sermaye Piyasası Kanunu uyarınca, yatırım danışmanlığı hizmeti sadece yetkili aracı kurumlar ve portföy yönetim şirketleri tarafından verilebilir. 
    Kullanıcıların bu platformdaki verilere dayanarak yaptıkları işlemlerden doğabilecek zarar ve kayıplardan "Crazytown Capital" ve geliştiricileri sorumlu tutulamaz.
    </p>
    <p>
    <b>2. RİSK BİLDİRİMİ:</b> Kripto para piyasaları yüksek volatiliteye sahiptir ve paranızın tamamını kaybetme riski taşır. Geçmiş performans, gelecek sonuçların garantisi değildir.
    </p>
    <p>
    <b>3. KVKK (KİŞİSEL VERİLER):</b> T.C. 6698 sayılı Kişisel Verilerin Korunması Kanunu (KVKK) uyarınca, bu platformda girdiğiniz kişisel veriler (işlem kayıtları vb.) sadece tarayıcınızın geçici belleğinde (session) tutulmakta olup, 
    herhangi bir sunucuda kalıcı olarak saklanmamakta veya üçüncü şahıslarla paylaşılmamaktadır.
    </p>
</div>
""", unsafe_allow_html=True)

# SÖZLEŞME ONAY KUTUSU
ack = st.checkbox(t('accept_terms'), value=st.session_state.terms_accepted)
if ack: st.session_state.terms_accepted = True

st.markdown(f"<p style='text-align: center; color: {col['ac_h']} !important; font-size: 0.8rem; margin-top:20px;'>© 2025 Crazytown Capital. Türkiye Cumhuriyeti Kanunlarına Uygundur.</p>", unsafe_allow_html=True)
