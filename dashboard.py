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

# SESSION STATE BAŞLATMA (Kişisel Veriler İçin)
if 'personal_trades' not in st.session_state:
    st.session_state.personal_trades = pd.DataFrame(columns=['Tarih', 'Parite', 'Yön', 'Sonuç', 'R_Kazanc'])
if 'calendar_mode' not in st.session_state:
    st.session_state.calendar_mode = 'System' # 'System' veya 'Personal'
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
        "select_month": "Select Month", "total_monthly": "TOTAL MONTHLY PNL", "market_intel": "📡 MARKET INTELLIGENCE",
        "roi_sim": "🧮 ROI SIMULATOR", "roi_desc": "Calculate potential earnings.", "initial_cap": "Initial Capital ($)",
        "risk_trade": "Risk Per Trade (%)", "proj_bal": "PROJECTED BALANCE", "trade_log": "TRADE LOG", "download": "📥 DOWNLOAD CSV",
        "limited_offer": "🔥 LIMITED TIME OFFER: Get LIFETIME access!", "feedback": "💬 TRADER FEEDBACK",
        "plan_starter": "STARTER", "plan_pro": "PROFESSIONAL", "plan_life": "LIFETIME", "sel_plan": "SELECT PLAN",
        "most_pop": "MOST POPULAR", "contact_sales": "CONTACT SALES", "faq": "❓ FAQ", "settings": "⚙️ SETTINGS",
        "lang_sel": "Language", "theme_sel": "Theme", "theme_dark": "Dark (Neon)", "theme_light": "Light (Corporate)",
        "acad_title": "OA | TRADE SMC MASTERY", "acad_quote": "Not beating the market, but following it with discipline.",
        "lesson_1_title": "📌 PART 1: TIME & CONTEXT", 
        "lesson_1_content": "#### 1. TIME FILTER\n* **LONDON:** `10:00 – 12:00` (UTC+3)\n* **NEW YORK:** `15:30 – 18:30` (UTC+3)\n#### 2. DAILY CONTEXT\nOnly condition: **LIQUIDITY SWEEP**.",
        "lesson_2_title": "🛠️ PART 2: ENTRY SETUP", 
        "lesson_2_content": "#### 1. FIBONACCI\n* **ENTRY:** `0.75` - `0.60`\n* **STOP:** `1.0`",
        "lesson_3_title": "⚠️ PART 3: RULES", 
        "lesson_3_content": "<div class='rule-box'><h4>🚨 STRICT RULES</h4><ul><li><b>NO CHOCH</b></li><li><b>NO TRADING OUTSIDE HOURS</b></li></ul></div>",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "Real-time analysis with explainable logic.",
        "run_ai": "SCAN MARKET", "ai_analyzing": "Analyzing Market Structure...", 
        "ai_input_label": "Enter Symbol (e.g. BTC, ETH, SOL, PEPE)",
        "ai_trend": "General Trend", "ai_rsi": "RSI Indicator", "ai_supp": "Est. Support", "ai_res": "Est. Resistance",
        "ai_score": "Confidence Score", "ai_dec": "AI DECISION", "ai_exp_title": "📝 LOGIC & EXPLANATION",
        "bull": "BULLISH 🟢", "bear": "BEARISH 🔴", "neutral": "NEUTRAL ⚪",
        "s_buy": "STRONG BUY 🚀", "buy": "BUY 🟢", "sell": "SELL 🔴", "s_sell": "STRONG SELL 🔻", "wait": "WAIT ✋",
        "data_source": "Data Source", "err_msg": "Coin not found.",
        "cal_sys": "SYSTEM DATA", "cal_per": "MY JOURNAL", "add_trade": "➕ Add Trade",
        "legal_head": "LEGAL DISCLAIMER & RISK WARNING",
        "accept_terms": "I have read and accept the terms and conditions."
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
        "lesson_1_title": "📌 BÖLÜM 1: ZAMAN VE BAĞLAM",
        "lesson_1_content": """
        #### 1. ZAMAN FİLTRESİ (KRİTİK)
        Sadece hacimli seanslarda işlem aranır.
        * **LONDRA:** `10:00 – 12:00` (TSİ)
        * **NEW YORK:** `15:30 – 18:30` (TSİ)
        #### 2. GÜNLÜK BAĞLAM (PDH/PDL)
        İşlem aramak için tek şart **LİKİDİTE ALIMI (SWEEP)**.
        * **PDH İhlali:** Sadece **SHORT**.
        * **PDL İhlali:** Sadece **LONG**.
        """,
        "lesson_2_title": "🛠️ BÖLÜM 2: GİRİŞ STRATEJİSİ",
        "lesson_2_content": """
        #### 1. FIBONACCI AYARLARI
        Likidite alımından sonra oluşan sert harekete (Impulse) Fibonacci çekilir.
        * **GİRİŞ:** `0.75` - `0.60` (Golden Pocket)
        * **STOP:** `1`
        * **TP-1:** `0.25`
        * **TP-2:** `-0.18`
        #### 2. FVG ONAYI
        * Fiyat, `0.6-0.75` aralığındaki bir **FVG** alanına temas etmelidir.
        """,
        "lesson_3_title": "⚠️ BÖLÜM 3: KURALLAR",
        "lesson_3_content": "<div class='rule-box'><h4>🚨 DEĞİŞMEZ KURALLAR</h4><ul><li><b>CHOCH YOK:</b> LTF kırılımı bekleme.</li><li><b>SAAT DIŞI İŞLEM YOK:</b> Disiplin her şeydir.</li></ul></div>",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "Gerekçeli Yapay Zeka Analizi ve Canlı Piyasa Taraması.",
        "run_ai": "TARA VE ANALİZ ET", "ai_analyzing": "Piyasa Yapısı Taranıyor...", 
        "ai_input_label": "Coin Sembolü Girin (Örn: TAO, BTC, ETH, PEPE)",
        "ai_trend": "Genel Trend", "ai_rsi": "RSI Göstergesi", "ai_supp": "Tahmini Destek", "ai_res": "Tahmini Direnç",
        "ai_score": "Crazytown Güven Skoru", "ai_dec": "YZ KARARI", "ai_exp_title": "📝 ANALİZ MANTIĞI & NEDENLER",
        "bull": "BOĞA (YÜKSELİŞ) 🟢", "bear": "AYI (DÜŞÜŞ) 🔴", "neutral": "NÖTR ⚪",
        "s_buy": "GÜÇLÜ AL 🚀", "buy": "AL 🟢", "sell": "SAT 🔴", "s_sell": "GÜÇLÜ SAT 🔻", "wait": "BEKLE ✋",
        "data_source": "Veri Kaynağı", "err_msg": "Coin bulunamadı. USDT eklemeyi dene (Örn: PEPEUSDT)",
        "cal_sys": "SİSTEM VERİLERİ", "cal_per": "KİŞİSEL GÜNLÜĞÜM", "add_trade": "➕ Yeni İşlem Ekle",
        "legal_head": "YASAL UYARI, SORUMLULUK BEYANI VE KVKK AYDINLATMA METNİ",
        "accept_terms": "Yukarıdaki yasal uyarı metnini, risk bildirimini ve KVKK aydınlatma metnini okudum, anladım ve kabul ediyorum."
    },
    "RU": {
        "title_sub": "АЛГОРИТМИЧЕСКИЕ ТОРГОВЫЕ СИСТЕМЫ", "perf": "ЭФФЕКТИВНОСТЬ", "acad": "АКАДЕМИЯ", "memb": "ПОДПИСКА", "cont": "КОНТАКТЫ", "ai_lab": "ИИ ЛАБОРАТОРИЯ",
        "total_trades": "ВСЕГО СДЕЛОК", "win_rate": "ВИНРЕЙТ", "net_return": "ЧИСТАЯ ПРИБЫЛЬ", "profit_factor": "ПРОФИТ-ФАКТОР",
        "season_goal": "ЦЕЛЬ СЕЗОНА", "completed": "ЗАВЕРШЕНО", "perf_cal": "🗓️ КАЛЕНДАРЬ",
        "select_month": "Выберите месяц", "total_monthly": "ИТОГ МЕСЯЦА PNL", "market_intel": "📡 РЫНОК",
        "roi_sim": "🧮 ROI СИМУЛЯТОР", "roi_desc": "Рассчитайте прибыль.", "initial_cap": "Капитал", "risk_trade": "Риск", "proj_bal": "ПРОГНОЗ", "trade_log": "ЖУРНАЛ", "download": "📥 СКАЧАТЬ",
        "limited_offer": "🔥 ПРЕДЛОЖЕНИЕ: LIFETIME доступ!", "feedback": "💬 ОТЗЫВЫ",
        "plan_starter": "СТАРТ", "plan_pro": "ПРОФИ", "plan_life": "LIFETIME", "sel_plan": "ВЫБРАТЬ",
        "most_pop": "ПОПУЛЯРНЫЙ", "contact_sales": "СВЯЗАТЬСЯ", "faq": "❓ FAQ", "settings": "⚙️ НАСТРОЙКИ",
        "lang_sel": "Язык", "theme_sel": "Тема", "theme_dark": "Темная", "theme_light": "Светлая",
        "acad_title": "OA | TRADE SMC МАСТЕРСТВО", "acad_quote": "Дисциплина прежде всего.",
        "lesson_1_title": "📌 ЧАСТЬ 1: ВРЕМЯ", "lesson_1_content": "...",
        "lesson_2_title": "🛠️ ЧАСТЬ 2: ВХОД", "lesson_2_content": "...",
        "lesson_3_title": "⚠️ ЧАСТЬ 3: ПРАВИЛА", "lesson_3_content": "...",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "ИИ анализ с объяснением.",
        "run_ai": "АНАЛИЗ", "ai_analyzing": "Сканирование...", 
        "ai_input_label": "Символ (BTC, ETH...)",
        "ai_trend": "Тренд", "ai_rsi": "RSI", "ai_supp": "Поддержка", "ai_res": "Сопротивление",
        "ai_score": "Оценка", "ai_dec": "РЕШЕНИЕ", "ai_exp_title": "📝 ОБЪЯСНЕНИЕ",
        "bull": "БЫЧИЙ 🟢", "bear": "МЕДВЕЖИЙ 🔴", "neutral": "НЕЙТРАЛЬНО ⚪",
        "s_buy": "СИЛЬНАЯ ПОКУПКА 🚀", "buy": "ПОКУПАТЬ 🟢", "sell": "ПРОДАВАТЬ 🔴", "s_sell": "СИЛЬНАЯ ПРОДАЖ 🔻", "wait": "ЖДАТЬ ✋",
        "data_source": "Источник", "err_msg": "Монета не найдена.",
        "cal_sys": "СИСТЕМА", "cal_per": "МОЙ ЖУРНАЛ", "add_trade": "➕ Добавить",
        "legal_head": "ЮРИДИЧЕСКИЙ ОТКАЗ",
        "accept_terms": "Я принимаю условия."
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

        /* MOBİL UYUMLU TAKVİM */
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
            .metric-value {{ font-size: 1.2rem !important; }}
            .ai-header {{ font-size: 1.2rem !important; }}
            .ai-decision {{ font-size: 1.4rem !important; }}
            .pro-grid {{ grid-template-columns: 1fr !important; }}
            .ai-grid {{ grid-template-columns: 1fr !important; gap: 10px !important; }}
            .memb-grid {{ grid-template-columns: 1fr !important; }}
        }}

        .neon-title {{ font-family: 'Orbitron', sans-serif; font-size: 3.5rem; text-align: center; color: {col['ttl']} !important; font-weight: 900; letter-spacing: 4px; margin: 0; {f"text-shadow: 0 0 20px {col['ac']};" if st.session_state.theme == "Dark" else ""} animation: pulse 3s infinite alternate; }}
        .metric-container {{ background-color: {col['card']}; border: 1px solid {col['bd']}; border-radius: 10px; padding: 15px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
        .metric-value {{ font-size: 2rem; font-weight: 700; color: {col['ttl']} !important; }}
        .metric-label {{ font-size: 0.8rem; color: {col['grd']} !important; font-weight: 600; letter-spacing: 1px; }}
        
        /* AI CARD STYLING */
        .ai-card {{ background-color: {col['ai_bg']}; border: 1px solid {col['bd']}; border-left-width: 6px; border-left-style: solid; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); }}
        .ai-header {{ font-size: 1.6rem; font-weight: 800; color: {col['ttl']} !important; margin-bottom: 5px; }}
        .ai-sub {{ font-size: 0.9rem; margin-bottom: 20px; font-weight: 600; }}
        .ai-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
        .ai-item {{ padding: 5px 0; }}
        .ai-label {{ font-size: 0.85rem; color: {col['grd']} !important; margin-bottom: 3px; }}
        .ai-val {{ font-size: 1.2rem; font-weight: 800; color: {col['ttl']} !important; }}
        .ai-decision {{ font-size: 1.8rem; font-weight: 900; text-align: left; margin-top: 15px; display: flex; align-items: center; gap: 10px; }}
        .explanation-box {{ background: rgba(255, 255, 255, 0.05); border-left: 3px solid {col['ac']}; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 0.9rem; }}

        /* PRO TOOLKIT */
        .pro-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 20px; }}
        .pro-item {{ background: {col['sec']}; border: 1px solid {col['bd']}; border-radius: 8px; padding: 10px; text-align: left; }}
        .pro-name {{ font-weight: 800; color: {col['ttl']} !important; font-size: 0.8rem; margin-bottom: 3px; }}
        .pro-status {{ font-weight: bold; font-size: 0.9rem; }}

        /* MEMBERSHIP */
        .memb-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 20px; }}
        .memb-card {{ background: {col['card']}; border: 1px solid {col['bd']}; border-radius: 12px; padding: 25px; text-align: center; transition: 0.3s; }}
        .memb-card:hover {{ transform: translateY(-5px); border-color: {col['ac']}; }}
        .plan-price {{ font-size: 2rem; font-weight: bold; color: {col['ttl']} !important; }}

        .day-win {{ background: rgba(0, 255, 204, 0.15); border-color: {col['ac']}; }}
        .day-win-light {{ background: rgba(13, 110, 253, 0.15); border-color: {col['ac']}; }}
        .day-loss {{ background: rgba(255, 75, 75, 0.15); border-color: #ff4b4b; }}
        .win-text {{ color: {col['ac']} !important; }} .loss-text {{ color: #ff4b4b !important; }} .empty-cell {{ background: transparent; border: none; }}
        
        .stTabs [data-baseweb="tab"] {{ color: {col['grd']} !important; }}
        .stTabs [aria-selected="true"] {{ color: {col['ac']} !important; border-bottom-color: {col['ac']} !important; }}
        .custom-btn {{ background-color: {col['ac']}; color: {col['bg']} !important; padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; display: block; text-align: center; }}
        .custom-btn-outline {{ border: 1px solid {col['ac']}; color: {col['ac']} !important; background: transparent; padding: 8px 16px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block; }}
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{ background-color: {col['sec']}; color: {col['txt']}; border-color: {col['bd']}; }}
        
        /* LEGAL */
        .legal-box {{ margin-top: 50px; padding: 20px; border-top: 1px solid {col['bd']}; font-size: 0.75rem; color: {col['grd']} !important; text-align: justify; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. VERİ YÜKLEME
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
    return pd.DataFrame() # Boş döner

def get_market_data(symbol, interval):
    symbol = symbol.upper().strip()
    try:
        cg_map = {"TAO":"bittensor", "BTC":"bitcoin", "ETH":"ethereum", "SOL":"solana", "AVAX":"avalanche-2", "PEPE":"pepe", "SHIB":"shiba-inu", "WIF":"dogwifhat"}
        cid = cg_map.get(symbol)
        if not cid: # Ara
            s = requests.get(f"https://api.coingecko.com/api/v3/search?query={symbol}", timeout=2).json()
            if s.get("coins"): cid = s["coins"][0]["id"]
        
        if cid:
            days = "1" if interval=="15m" else ("30" if interval=="1d" else "7")
            r = requests.get(f"https://api.coingecko.com/api/v3/coins/{cid}/ohlc?vs_currency=usd&days={days}", timeout=3).json()
            if r:
                df = pd.DataFrame(r, columns=['time','open','high','low','close'])
                df['time'] = pd.to_datetime(df['time'], unit='ms')
                return df, f"CoinGecko ({cid})"
    except: pass
    
    try:
        ex = ccxt.binance()
        t = f"{symbol}/USDT" if "/" not in symbol else symbol
        tf = "1h" if interval=="1h" else ("4h" if interval=="4h" else "1d")
        o = ex.fetch_ohlcv(t, timeframe=tf, limit=100)
        if o:
            df = pd.DataFrame(o, columns=['time','open','high','low','close','vol'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            return df, "Binance API"
    except: pass
    return pd.DataFrame(), None

# ==========================================
# 4. ARAYÜZ
# ==========================================
st.markdown('<div class="neon-title">CRAZYTOWN CAPITAL</div>', unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: {col['ac']}; letter-spacing: 2px; font-weight:bold;'>{t('title_sub')}</p>", unsafe_allow_html=True)

tab1, tab2, tab5, tab3, tab4 = st.tabs([t('perf'), t('acad'), t('ai_lab'), t('memb'), t('cont')])

# TAB 1: PERFORMANS (ÇİFT MODLU)
with tab1:
    col_b1, col_b2 = st.columns(2)
    if col_b1.button(t('cal_sys'), use_container_width=True): st.session_state.calendar_mode = 'System'; st.rerun()
    if col_b2.button(t('cal_per'), use_container_width=True): st.session_state.calendar_mode = 'Personal'; st.rerun()
    
    if st.session_state.calendar_mode == 'System':
        df = load_system_data()
        st.caption(f"📢 {t('cal_sys')} Modu Aktif")
    else:
        st.caption(f"👤 {t('cal_per')} Modu Aktif")
        with st.expander(t('add_trade')):
            with st.form("add_t"):
                c1, c2, c3, c4 = st.columns(4)
                dt = c1.date_input("Tarih")
                pr = c2.text_input("Parite (BTC)")
                res = c3.selectbox("Sonuç", ["WIN", "LOSS"])
                rr = c4.number_input("R Kazanç", step=0.1)
                if st.form_submit_button("KAYDET"):
                    new = pd.DataFrame({'Tarih': [dt.strftime("%d.%m.%Y")], 'Parite': [pr], 'Sonuç': [res], 'R_Kazanc': [rr]})
                    st.session_state.personal_trades = pd.concat([st.session_state.personal_trades, new], ignore_index=True)
                    st.rerun()
        df = st.session_state.personal_trades

    if not df.empty:
        # Metrikler
        tot=len(df); win=len(df[df['Sonuç']=='WIN']); rate=(win/tot*100) if tot>0 else 0; net=df['R_Kazanc'].sum()
        pf_val = abs(df[df['R_Kazanc']>0]['R_Kazanc'].sum() / df[df['R_Kazanc']<0]['R_Kazanc'].sum()) if len(df[df['R_Kazanc']<0]) > 0 else 0
        
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-container"><div class="metric-value">{tot}</div><div class="metric-label">{t("total_trades")}</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-container"><div class="metric-value">{rate:.1f}%</div><div class="metric-label">{t("win_rate")}</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-container"><div class="metric-value" style="color:{col["ac"] if net>0 else "#ff4b4b"} !important">{net:.2f}R</div><div class="metric-label">{t("net_return")}</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-container"><div class="metric-value">{pf_val:.2f}</div><div class="metric-label">{t("profit_factor")}</div></div>', unsafe_allow_html=True)
        
        # Takvim
        st.markdown("---")
        df['Tarih_Dt'] = pd.to_datetime(df['Tarih'], dayfirst=True, errors='coerce'); df.dropna(subset=['Tarih_Dt'], inplace=True)
        if not df.empty:
            ms = df['Tarih_Dt'].dt.strftime('%Y-%m').unique(); sm = st.selectbox(t("select_month"), ms, index=len(ms)-1)
            y, m = map(int, sm.split('-')); daily_pnl = df[df['Tarih_Dt'].dt.strftime('%Y-%m') == sm].groupby(df['Tarih_Dt'].dt.day)['R_Kazanc'].sum().to_dict()
            cal = calendar.monthcalendar(y, m)
            
            html_cal = ['<div class="calendar-container">']
            for dname in ['Pzt','Sal','Çar','Per','Cum','Cmt','Paz']: html_cal.append(f'<div class="calendar-header">{dname}</div>')
            for week in cal:
                for day in week:
                    if day == 0: html_cal.append('<div class="day-cell" style="background:transparent; border:none;"></div>')
                    else:
                        pnl = daily_pnl.get(day, 0)
                        cls = "day-win" if pnl > 0 else ("day-loss" if pnl < 0 else "")
                        p_txt = "win-txt" if pnl > 0 else ("loss-txt" if pnl < 0 else "")
                        val = f"{pnl:+.1f}R" if pnl != 0 else "-"
                        html_cal.append(f'<div class="day-cell {cls}"><div class="day-num">{day}</div><div class="day-pnl {p_txt}">{val}</div></div>')
            html_cal.append('</div>')
            st.markdown("".join(html_cal), unsafe_allow_html=True)
    else:
        st.info("Veri yok.")

# TAB 2: AKADEMİ (GELİŞMİŞ)
with tab2:
    st.markdown(f"<h2 style='text-align:center;color:{col['ac']}'>{t('acad_title')}</h2>", unsafe_allow_html=True)
    with st.expander(t('acad_1')): st.markdown(t('acad_1_text'))
    with st.expander(t('acad_2')): st.markdown(t('acad_2_text'))
    with st.expander(t('acad_3')): st.markdown(t('acad_3_text'))

# TAB 5: AI LAB (AÇIKLAMALI & CANLI)
with tab5:
    st.markdown(f"<h2 style='text-align:center;color:{col['ac']}'>{t('ai_title')}</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 1])
    sym = c1.text_input(t('ai_input_label'), value="TAO")
    tf = c2.selectbox("TF", ["1h", "4h", "1d"])
    if c3.button(t('run_ai'), key="btn_ai", use_container_width=True):
        # DEFAULT (Safety First)
        dec_col = "#888"; trend_text = "-"; decision = "-"; score = 50; reason_list = []
        rsi_val = 50.0; current_price = 0.0; change_24h = 0.0; supp = 0.0; res = 0.0
        wave_status = "-"; wave_col = "#888"; core_status = "-"; core_col = "#888"
        beluga_status = "-"; macd_status = "-"; macd_col = "#888"; div_status = "-"; div_col = "#888"
        src = "N/A"

        with st.spinner(t('ai_analyzing')):
            df_ai, src = get_market_data(sym, tf)
            time.sleep(0.5)
        
        if not df_ai.empty and len(df_ai) > 20:
            current_price = float(df_ai['close'].iloc[-1])
            open_price = float(df_ai['open'].iloc[-1])
            change_24h = ((current_price - open_price) / open_price) * 100
            
            df_ai['SMA'] = df_ai['close'].rolling(20).mean()
            sma_val = float(df_ai['SMA'].iloc[-1])
            delta = df_ai['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / (loss + 0.0001)
            rsi = 100 - (100 / (1 + rs))
            rsi_val = float(rsi.iloc[-1])
            
            supp = df_ai['low'].tail(50).min()
            res = df_ai['high'].tail(50).max()

            # --- MANTIK MOTORU ---
            score = 50
            if current_price > sma_val:
                score += 20; reason_list.append("✅ Fiyat > SMA20 (Trend Pozitif)")
            else:
                score -= 20; reason_list.append("⚠️ Fiyat < SMA20 (Trend Negatif)")
            
            if rsi_val > 55:
                score += 10; reason_list.append(f"✅ RSI {rsi_val:.1f} > 55 (Momentum Güçlü)")
            elif rsi_val < 45:
                score -= 10; reason_list.append(f"⚠️ RSI {rsi_val:.1f} < 45 (Momentum Zayıf)")
            else:
                reason_list.append(f"ℹ️ RSI {rsi_val:.1f} (Nötr Bölge)")
            
            score = max(0, min(100, score))
            if score >= 60: decision = t('buy'); dec_col = "#00ff00"; trend_text = t('bull')
            elif score <= 40: decision = t('sell'); dec_col = "#ff0000"; trend_text = t('bear')
            else: decision = t('wait'); dec_col = "#aaaaaa"; trend_text = t('neutral')
            
            # --- PRO TOOLKIT ---
            wave_status = "BULLISH 🌊" if current_price > sma_val else "BEARISH 🌊"
            wave_col = "#00ff00" if current_price > sma_val else "#ff0000"
            std = df_ai['close'].rolling(20).std().iloc[-1]
            core_status = "HIGH VOLATILITY ⚡" if std > (current_price * 0.02) else "STABLE 🛡️"
            core_col = "#ffcc00" if "HIGH" in core_status else "#00ccff"
            beluga_status = f"{((rsi_val-30)/40)*100:.1f} (OSC)"
            
            ema12 = df_ai['close'].ewm(span=12).mean(); ema26 = df_ai['close'].ewm(span=26).mean()
            macd = ema12 - ema26; signal = macd.ewm(span=9).mean()
            macd_val = macd.iloc[-1]; sig_val = signal.iloc[-1]
            macd_status = "BUY 🟢" if macd_val > sig_val else "SELL 🔴"
            macd_col = "#00ff00" if macd_val > sig_val else "#ff0000"
            
            pt = df_ai['close'].iloc[-1] > df_ai['close'].iloc[-5]
            rt = rsi.iloc[-1] > rsi.iloc[-5]
            if pt and not rt: div_status = "BEARISH DIV 📉"; div_col = "#ff0000"
            elif not pt and rt: div_status = "BULLISH DIV 📈"; div_col = "#00ff00"
            else: div_status = "NONE"; div_col = "#888"

            expl_html = "".join([f"<li>{r}</li>" for r in reason_list])
            
            st.markdown(f"""
            <div class="ai-card" style="border-left-color: {dec_col};">
                <div style="display:flex; justify-content:space-between;">
                    <div class="ai-header">{sym.upper()} / USD</div>
                    <div class="ai-header">${current_price:,.2f} <span style="font-size:0.8rem; color:{dec_col}">({change_24h:+.2f}%)</span></div>
                </div>
                <hr style="border-color:{col['bd']}; margin:15px 0;">
                <div class="ai-grid">
                    <div><div class="ai-label">{t('ai_trend')}</div><div class="ai-val" style="color:{dec_col}">{trend_text}</div></div>
                    <div><div class="ai-label">{t('ai_rsi')}</div><div class="ai-val">{rsi_val:.1f}</div></div>
                    <div><div class="ai-label">{t('ai_supp')}</div><div class="ai-val">${supp:,.2f}</div></div>
                    <div><div class="ai-label">{t('ai_res')}</div><div class="ai-val">${res:,.2f}</div></div>
                </div>
                
                <div style="margin-top:20px; font-weight:800; color:{col['ac']}; letter-spacing:1px;">PRO TOOLKIT 🛠️</div>
                <div class="pro-grid">
                    <div class="pro-item"><div class="pro-name">Market Waves</div><div class="pro-status" style="color:{wave_col}">{wave_status}</div></div>
                    <div class="pro-item"><div class="pro-name">Market Core</div><div class="pro-status" style="color:{core_col}">{core_status}</div></div>
                    <div class="pro-item"><div class="pro-name">Beluga Nautilus</div><div class="pro-status">{beluga_status}</div></div>
                    <div class="pro-item"><div class="pro-name">Ultimate MACD</div><div class="pro-status" style="color:{macd_col}">{macd_status}</div></div>
                    <div class="pro-item"><div class="pro-name">Ultimate RSI</div><div class="pro-status">{rsi_val:.1f}</div></div>
                    <div class="pro-item"><div class="pro-name">Div. Scanner</div><div class="pro-status" style="color:{div_col}">{div_status}</div></div>
                </div>

                <div class="ai-decision" style="border: 2px solid {dec_col}; color:{dec_col};">{t('ai_dec')}: {decision}</div>
                
                <div class="explanation-box">
                    <div style="font-weight:bold; color:{col['ac']}">{t('ai_exp_title')}</div>
                    <ul>{expl_html}</ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"{t('data_source')}: {src}")
            
            # GRAFİK
            fig_ai = go.Figure()
            last_50 = df_ai.tail(50)
            fig_ai.add_trace(go.Scatter(x=last_50.index, y=last_50['close'], mode='lines', line=dict(color=col['txt'], width=2)))
            # Projection
            lx = last_50.index[-1]; vol = last_50['close'].std()
            fx = np.arange(lx, lx+10)
            slp = vol*0.1 if direction == "BULL" else (-vol*0.1 if direction == "BEAR" else 0)
            mid = [current_price + (i*slp) for i in range(10)]
            fig_ai.add_trace(go.Scatter(x=fx, y=mid, mode='lines', line=dict(color=dec_col, width=2, dash='dot')))
            
            fig_ai.update_layout(template="plotly_dark" if st.session_state.theme=="Dark" else "plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350, margin=dict(l=0,r=0,t=10,b=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=col['bd']))
            st.plotly_chart(fig_ai, use_container_width=True)

        else:
            st.error(t("err_msg"))

# TAB 3: ÜYELİK (ŞIK)
with tab3:
    st.markdown(f"<h2 style='text-align:center; color:{col['ttl']}'>{t('memb_title')}</h2>", unsafe_allow_html=True)
    st.markdown('<div class="memb-grid">', unsafe_allow_html=True)
    for p, pr in [(t('m_1'), "$30"), (t('m_2'), "$75"), (t('m_3'), "$250")]:
        bcol = col['ac'] if p == t('m_2') else col['bd']
        st.markdown(f"""
        <div class="memb-card" style="border-color:{bcol}">
            <div style="color:{col['ac']}; font-weight:bold; letter-spacing:2px;">{p}</div>
            <div class="plan-price">{pr}</div>
            <br><a href="#" class="custom-btn">SEÇ</a>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 4: İLETİŞİM
with tab4:
    st.markdown(f"### 📨 Telegram\n<a href='https://t.me/Orhan1909' class='custom-btn'>TELEGRAM</a>", unsafe_allow_html=True)

# FOOTER: YASAL & KVKK
st.markdown("---")
st.markdown(f"""
<div class="legal-box">
    <h4 style="text-align:center; color:{col['txt']}">{t('legal_head')}</h4>
    <p><b>1. YASAL UYARI (SPK MEVZUATI):</b> Bu platformda (Crazytown Capital) yer alan her türlü bilgi, analiz, grafik ve yorumlar sadece eğitim ve genel bilgilendirme amaçlıdır. 
    <b>Kesinlikle "Yatırım Tavsiyesi" (Al-Sat-Tut sinyali) değildir.</b> 6362 sayılı Sermaye Piyasası Kanunu uyarınca, yatırım danışmanlığı hizmeti sadece yetkili aracı kurumlar ve portföy yönetim şirketleri tarafından verilebilir. 
    Kullanıcıların bu platformdaki verilere dayanarak yaptıkları işlemlerden doğabilecek zarar ve kayıplardan "Crazytown Capital" ve geliştiricileri sorumlu tutulamaz.</p>
    <p><b>2. RİSK BİLDİRİMİ:</b> Kripto para piyasaları yüksek volatiliteye sahiptir ve paranızın tamamını kaybetme riski taşır. Geçmiş performans, gelecek sonuçların garantisi değildir.</p>
    <p><b>3. KVKK AYDINLATMA METNİ:</b> T.C. 6698 sayılı Kişisel Verilerin Korunması Kanunu (KVKK) uyarınca, bu platformda girdiğiniz kişisel veriler (işlem kayıtları vb.) sadece tarayıcınızın geçici belleğinde (session) tutulmakta olup, 
    herhangi bir sunucuda kalıcı olarak saklanmamakta, işlenmemekte veya üçüncü şahıslarla paylaşılmamaktadır.</p>
</div>
""", unsafe_allow_html=True)

ack = st.checkbox(t('accept_terms'), value=st.session_state.terms_accepted)
if ack: st.session_state.terms_accepted = True

st.markdown(f"<div style='text-align:center; font-size:0.8rem; margin-top:20px; color:{col['ac_h']}'>© 2025 Crazytown Capital.</div>", unsafe_allow_html=True)
