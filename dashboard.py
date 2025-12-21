import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import calendar

# ==========================================
# 0. AYARLAR VE VERİTABANI
# ==========================================
st.set_page_config(
    page_title="Crazytown Capital",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session State
if 'lang' not in st.session_state:
    st.session_state.lang = "TR"
if 'theme' not in st.session_state:
    st.session_state.theme = "Dark"

# Çeviri Sözlüğü (EKSİKLER GİDERİLDİ)
TRANSLATIONS = {
    "EN": {
        "title_sub": "ALGORITHMIC TRADING SYSTEMS",
        "perf": "PERFORMANCE",
        "acad": "ACADEMY",
        "memb": "MEMBERSHIP",
        "cont": "CONTACT",
        "total_trades": "TOTAL TRADES",
        "win_rate": "WIN RATE",
        "net_return": "NET RETURN",
        "profit_factor": "PROFIT FACTOR",
        "season_goal": "SEASON GOAL",
        "completed": "COMPLETED",
        "perf_cal": "🗓️ PERFORMANCE CALENDAR",
        "select_month": "Select Month",
        "total_monthly": "TOTAL MONTHLY PNL",
        "market_intel": "📡 MARKET INTELLIGENCE",
        "roi_sim": "🧮 ROI SIMULATOR",
        "roi_desc": "Calculate potential earnings based on historical performance.",
        "initial_cap": "Initial Capital ($)",
        "risk_trade": "Risk Per Trade (%)",
        "proj_bal": "PROJECTED BALANCE",
        "trade_log": "TRADE LOG",
        "download": "📥 DOWNLOAD CSV",
        "limited_offer": "🔥 LIMITED TIME OFFER: Get the LIFETIME access before prices increase!",
        "feedback": "💬 TRADER FEEDBACK",
        "plan_starter": "STARTER",
        "plan_pro": "PROFESSIONAL",
        "plan_life": "LIFETIME",
        "sel_plan": "SELECT PLAN",
        "most_pop": "MOST POPULAR",
        "contact_sales": "CONTACT SALES",
        "faq": "❓ FAQ",
        "settings": "⚙️ SETTINGS",
        "lang_sel": "Language",
        "theme_sel": "Theme",
        "theme_dark": "Dark (Neon)",
        "theme_light": "Light (Clean)",
        "acad_title": "OA | TRADE SMC MASTERY",
        "acad_quote": "Not beating the market, but following it with discipline.",
        "lesson_1_title": "📌 PART 1: TIME & CONTEXT",
        "lesson_1_content": """
        ### 1. TIME FILTER (CRITICAL)
        We only trade during high-volume sessions. Charts are closed otherwise.
        * **LONDON:** `10:00 – 12:00` (UTC+3)
        * **NEW YORK:** `15:30 – 18:30` (UTC+3)
        
        ### 2. DAILY CONTEXT (PDH/PDL)
        The only condition to look for a trade is **LIQUIDITY SWEEP**.
        * **PDH (Previous Day High) Raid:** Look for **SHORT**.
        * **PDL (Previous Day Low) Raid:** Look for **LONG**.
        """,
        "lesson_2_title": "🛠️ PART 2: ENTRY SETUP",
        "lesson_2_content": """
        ### 1. FIBONACCI RETRACEMENT
        Draw Fib on the impulse leg created after the liquidity sweep.
        * **ENTRY ZONE:** `0.75` - `0.60` (Golden Pocket)
        * **STOP LOSS:** `1` (Start of the impulse)
        * **TP-1:** `0.25`
        * **TP-2:** `-0.18`
        
        ### 2. FVG REJECTION
        * Price must tap into a **Fair Value Gap (FVG)** inside the Golden Zone.
        """,
        "lesson_3_title": "⚠️ PART 3: RULES & EXECUTION",
        "lesson_3_content": """
        <div class="rule-box">
        <h4>🚨 CORE RULES</h4>
        <ul>
            <li><b>NO CHOCH:</b> We do not wait for Change of Character on LTF. It's often too late.</li>
            <li><b>NO TRADING OUTSIDE HOURS:</b> Discipline is key.</li>
            <li><b>MANAGEMENT:</b> Move SL to Breakeven (BE) only after TP-1 is hit.</li>
        </ul>
        </div>
        """
    },
    "TR": {
        "title_sub": "ALGORİTMİK İŞLEM SİSTEMLERİ",
        "perf": "PERFORMANS",
        "acad": "AKADEMİ",
        "memb": "ÜYELİK",
        "cont": "İLETİŞİM",
        "total_trades": "TOPLAM İŞLEM",
        "win_rate": "BAŞARI ORANI",
        "net_return": "NET GETİRİ",
        "profit_factor": "KÂR FAKTÖRÜ",
        "season_goal": "SEZON HEDEFİ",
        "completed": "TAMAMLANDI",
        "perf_cal": "🗓️ PERFORMANS TAKVİMİ",
        "select_month": "Ay Seçiniz",
        "total_monthly": "AYLIK TOPLAM PNL",
        "market_intel": "📡 PİYASA İSTİHBARATI",
        "roi_sim": "🧮 ROI SİMÜLATÖRÜ",
        "roi_desc": "Geçmiş performansa dayalı potansiyel kazanç hesapla.",
        "initial_cap": "Başlangıç Sermayesi ($)",
        "risk_trade": "İşlem Başı Risk (%)",
        "proj_bal": "TAHMİNİ BAKİYE",
        "trade_log": "İŞLEM GEÇMİŞİ",
        "download": "📥 CSV İNDİR",
        "limited_offer": "🔥 SINIRLI TEKLİF: Zam gelmeden ÖMÜR BOYU erişimi kap!",
        "feedback": "💬 YATIRIMCI YORUMLARI",
        "plan_starter": "BAŞLANGIÇ",
        "plan_pro": "PROFESYONEL",
        "plan_life": "ÖMÜR BOYU",
        "sel_plan": "PLAN SEÇ",
        "most_pop": "EN POPÜLER",
        "contact_sales": "SATIŞA ULAŞ",
        "faq": "❓ SIK SORULANLAR",
        "settings": "⚙️ AYARLAR",
        "lang_sel": "Dil",
        "theme_sel": "Tema",
        "theme_dark": "Koyu Mod (Neon)",
        "theme_light": "Açık Mod (Temiz)",
        "acad_title": "OA | TRADE SMC USTALIK SINIFI",
        "acad_quote": "Piyasayı yenmek değil, disiplinle takip etmek.",
        "lesson_1_title": "📌 BÖLÜM 1: ZAMAN VE BAĞLAM",
        "lesson_1_content": """
        ### 1. ZAMAN FİLTRESİ (KRİTİK)
        Sadece hacimli seanslarda işlem aranır. Diğer saatlerde ekran kapatılır.
        * **LONDRA:** `10:00 – 12:00` (TSİ)
        * **NEW YORK:** `15:30 – 18:30` (TSİ)
        
        ### 2. GÜNLÜK BAĞLAM (PDH/PDL)
        İşlem aramak için tek şart **LİKİDİTE ALIMI (SWEEP)**'dır.
        * **PDH (Önceki Gün Yükseği) İhlali:** Sadece **SHORT** ara.
        * **PDL (Önceki Gün Düşüğü) İhlali:** Sadece **LONG** ara.
        """,
        "lesson_2_title": "🛠️ BÖLÜM 2: GİRİŞ STRATEJİSİ",
        "lesson_2_content": """
        ### 1. FIBONACCI AYARLARI
        Likidite alımından sonra oluşan sert harekete (Impulse) Fibonacci çekilir.
        * **GİRİŞ BÖLGESİ:** `0.75` - `0.60` (Golden Pocket)
        * **STOP:** `1` (Hareket başlangıcı)
        * **TP-1:** `0.25`
        * **TP-2:** `-0.18`
        
        ### 2. FVG ONAYI
        * Fiyat, `0.6-0.75` aralığındaki bir **FVG (Dengesizlik)** alanına temas etmelidir.
        * Oradan reddedilme (rejection) beklenir.
        """,
        "lesson_3_title": "⚠️ BÖLÜM 3: KURALLAR VE YÖNETİM",
        "lesson_3_content": """
        <div class="rule-box">
        <h4>🚨 DEĞİŞMEZ KURALLAR</h4>
        <ul>
            <li><b>CHOCH YOK:</b> Düşük zaman diliminde kırılım (Choch) beklenmez.</li>
            <li><b>SAAT DIŞI İŞLEM YOK:</b> Disiplin her şeydir.</li>
            <li><b>YÖNETİM:</b> Stop sadece TP-1 alındıktan sonra Girişe (BE) çekilir.</li>
        </ul>
        </div>
        """
    },
    "RU": {
        "title_sub": "АЛГОРИТМИЧЕСКИЕ ТОРГОВЫЕ СИСТЕМЫ",
        "perf": "ЭФФЕКТИВНОСТЬ",
        "acad": "АКАДЕМИЯ",
        "memb": "ПОДПИСКА",
        "cont": "КОНТАКТЫ",
        "total_trades": "ВСЕГО СДЕЛОК",
        "win_rate": "ВИНРЕЙТ",
        "net_return": "ЧИСТАЯ ПРИБЫЛЬ",
        "profit_factor": "ПРОФИТ-ФАКТОР",
        "season_goal": "ЦЕЛЬ СЕЗОНА",
        "completed": "ЗАВЕРШЕНО",
        "perf_cal": "🗓️ КАЛЕНДАРЬ ДОХОДНОСТИ",
        "select_month": "Выберите месяц",
        "total_monthly": "ИТОГ МЕСЯЦА PNL",
        "market_intel": "📡 РЫНОЧНЫЙ ИНТЕЛЛЕКТ",
        "roi_sim": "🧮 ROI СИМУЛЯТОР",
        "roi_desc": "Рассчитайте потенциальную прибыль на основе истории.",
        "initial_cap": "Начальный капитал ($)",
        "risk_trade": "Риск на сделку (%)",
        "proj_bal": "ПРОГНОЗ БАЛАНСА",
        "trade_log": "ЖУРНАЛ СДЕЛОК",
        "download": "📥 СКАЧАТЬ CSV",
        "limited_offer": "🔥 ОГРАНИЧЕННОЕ ПРЕДЛОЖЕНИЕ: Получите ПОЖИЗНЕННЫЙ доступ!",
        "feedback": "💬 ОТЗЫВЫ ТРЕЙДЕРОВ",
        "plan_starter": "СТАРТ",
        "plan_pro": "ПРОФИ",
        "plan_life": "LIFETIME",
        "sel_plan": "ВЫБРАТЬ",
        "most_pop": "ПОПУЛЯРНЫЙ",
        "contact_sales": "СВЯЗАТЬСЯ",
        "faq": "❓ FAQ",
        "settings": "⚙️ НАСТРОЙКИ",
        "lang_sel": "Язык",
        "theme_sel": "Тема",
        "theme_dark": "Темная тема",
        "theme_light": "Светлая тема",
        "acad_title": "OA | TRADE SMC МАСТЕРСТВО",
        "acad_quote": "Не побеждать рынок, а дисциплинированно следовать за ним.",
        "lesson_1_title": "📌 ЧАСТЬ 1: ВРЕМЯ И КОНТЕКСТ",
        "lesson_1_content": """
        ### 1. ФИЛЬТР ВРЕМЕНИ
        Мы торгуем только во время высокой волатильности.
        * **ЛОНДОН:** `10:00 – 12:00` (UTC+3)
        * **НЬЮ-ЙОРК:** `15:30 – 18:30` (UTC+3)
        
        ### 2. ДНЕВНОЙ КОНТЕКСТ (PDH/PDL)
        Единственное условие для поиска сделки - **СНЯТИЕ ЛИКВИДНОСТИ**.
        * **Снятие PDH (Max вчера):** Ищем **SHORT**.
        * **Снятие PDL (Min вчера):** Ищем **LONG**.
        """,
        "lesson_2_title": "🛠️ ЧАСТЬ 2: СТРАТЕГИЯ ВХОДА",
        "lesson_2_content": """
        ### 1. ФИБОНАЧЧИ
        Тянем сетку на импульс после снятия ликвидности.
        * **ВХОД:** `0.75` - `0.60`
        * **СТОП:** `1`
        * **TP-1:** `0.25`
        * **TP-2:** `-0.18`
        
        ### 2. FVG (Fair Value Gap)
        * Цена должна коснуться FVG в золотой зоне.
        """,
        "lesson_3_title": "⚠️ ЧАСТЬ 3: ПРАВИЛА И УПРАВЛЕНИЕ",
        "lesson_3_content": """
        <div class="rule-box">
        <h4>🚨 ПРАВИЛА</h4>
        <ul>
            <li><b>НЕТ CHOCH:</b> Не ждем смены характера движения на младших таймфреймах.</li>
            <li><b>НЕТ СДЕЛОК ВНЕ СЕССИЙ:</b> Дисциплина прежде всего.</li>
            <li><b>УПРАВЛЕНИЕ:</b> SL в безубыток только после TP-1.</li>
        </ul>
        </div>
        """
    }
}

def t(key):
    return TRANSLATIONS[st.session_state.lang][key]

# --- Üst Bar Ayarları ---
with st.expander(t('settings'), expanded=False):
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        selected_lang = st.selectbox(t('lang_sel'), ["TR", "EN", "RU"], index=["TR", "EN", "RU"].index(st.session_state.lang))
        if selected_lang != st.session_state.lang:
            st.session_state.lang = selected_lang
            st.rerun()
    with col_s2:
        theme_options = [t('theme_dark'), t('theme_light')]
        current_idx = 0 if st.session_state.theme == "Dark" else 1
        selected_theme_label = st.selectbox(t('theme_sel'), theme_options, index=current_idx)
        new_theme = "Dark" if selected_theme_label == t('theme_dark') else "Light"
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()

# ==========================================
# 1. DİNAMİK CSS VE ANİMASYON (Cyberpunk Orbital)
# ==========================================

# Tema Değişkenleri
if st.session_state.theme == "Dark":
    # KOYU MOD (NEON)
    colors = {
        "bg": "#050505",
        "text": "#e0e0e0",
        "card_bg": "rgba(20, 20, 25, 0.8)", 
        "border": "#333333",
        "accent": "#00ffcc",  # Neon Turkuaz
        "accent_hover": "#00cca3",
        "secondary_bg": "#111111",
        "grid_text": "#aaaaaa",
        "title": "#ffffff",
        "chart_grid": "#333333"
    }
    # Koyu mod animasyonu (Parlak küreler)
    anim_css = """
        .stApp::before {
            background: radial-gradient(circle, rgba(0, 255, 204, 0.2), transparent 70%);
            animation: orbMove1 20s infinite alternate linear;
        }
        .stApp::after {
            background: radial-gradient(circle, rgba(153, 0, 255, 0.2), transparent 70%);
            animation: orbMove2 25s infinite alternate-reverse linear;
        }
    """
else:
    # AÇIK MOD (TEMİZ KURUMSAL)
    colors = {
        "bg": "#f0f2f6",
        "text": "#1f2833",
        "card_bg": "rgba(255, 255, 255, 0.9)",
        "border": "#d1d5db",
        "accent": "#0077b6",  # Profesyonel Mavi
        "accent_hover": "#005f91",
        "secondary_bg": "#e5e7eb",
        "grid_text": "#4b5563",
        "title": "#000000",
        "chart_grid": "#e5e7eb"
    }
    # Açık mod animasyonu (Yumuşak mavi bulutlar)
    anim_css = """
        .stApp::before {
            background: radial-gradient(circle, rgba(0, 119, 182, 0.1), transparent 60%);
            animation: orbMove1 30s infinite alternate ease-in-out;
        }
        .stApp::after {
            background: radial-gradient(circle, rgba(100, 100, 200, 0.08), transparent 60%);
            animation: orbMove2 35s infinite alternate-reverse ease-in-out;
        }
    """

st.markdown(f"""
    <style>
        /* FONTLAR */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');

        /* TEMİZLİK */
        header, footer, #MainMenu, .stDeployButton {{display: none !important;}}
        .block-container {{padding-top: 1rem !important; padding-bottom: 2rem !important;}}

        /* ANA GÖVDE */
        .stApp {{
            background-color: {colors["bg"]};
            color: {colors["text"]};
            font-family: 'Inter', sans-serif;
        }}

        /* ARKA PLAN ANİMASYONU (ORBITAL ORBS) */
        .stApp::before, .stApp::after {{
            content: '';
            position: fixed;
            width: 60vw;
            height: 60vw;
            border-radius: 50%;
            z-index: -1;
            filter: blur(80px);
            opacity: 0.6;
        }}
        .stApp::before {{ top: -10%; left: -10%; }}
        .stApp::after {{ bottom: -10%; right: -10%; }}

        @keyframes orbMove1 {{
            0% {{ transform: translate(0, 0); }}
            100% {{ transform: translate(30%, 30%); }}
        }}
        @keyframes orbMove2 {{
            0% {{ transform: translate(0, 0); }}
            100% {{ transform: translate(-30%, -20%); }}
        }}
        
        {anim_css}

        /* NEON BAŞLIK (ORBITRON) */
        .neon-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 3.5rem;
            text-align: center;
            color: {colors["title"]};
            font-weight: 900;
            letter-spacing: 4px;
            margin-bottom: 0;
            text-shadow: 0 0 15px {colors["accent"]};
        }}

        /* KARTLAR */
        .metric-container {{
            background-color: {colors["card_bg"]};
            border: 1px solid {colors["border"]};
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }}
        .metric-container:hover {{
            transform: translateY(-5px);
            border-color: {colors["accent"]};
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: {colors["title"]};
        }}
        .metric-label {{
            font-size: 0.85rem;
            color: {colors["grid_text"]};
            text-transform: uppercase;
            font-weight: 600;
        }}

        /* TABLOLAR VE GİRDİLER */
        .stDataFrame {{ border: 1px solid {colors["border"]}; }}
        .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {{
            background-color: {colors["secondary_bg"]};
            color: {colors["text"]};
            border-color: {colors["border"]};
        }}
        
        /* TAKVİM GRID */
        .calendar-container {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
            margin-top: 15px;
        }}
        .calendar-header {{
            text-align: center;
            color: {colors["grid_text"]};
            font-weight: bold;
            border-bottom: 1px solid {colors["border"]};
            padding-bottom: 5px;
        }}
        .day-cell {{
            background-color: {colors["secondary_bg"]};
            border: 1px solid {colors["border"]};
            border-radius: 6px;
            height: 90px;
            padding: 8px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            transition: all 0.2s;
        }}
        .day-cell:hover {{
            border-color: {colors["accent"]};
            transform: scale(1.02);
            z-index: 10;
        }}
        .day-number {{
            font-size: 0.9rem;
            font-weight: bold;
            color: {colors["text"]};
            opacity: 0.7;
        }}
        .day-profit {{
            font-size: 1.1rem;
            font-weight: 800;
            margin-top: auto;
            align-self: center;
        }}
        
        /* Renklendirmeler */
        .day-win {{
            background-color: rgba(0, 255, 204, 0.15);
            border-color: {colors["accent"]};
        }}
        .day-win-light {{
            background-color: rgba(0, 119, 182, 0.15); 
            border-color: {colors["accent"]};
        }}
        .day-loss {{
            background-color: rgba(255, 75, 75, 0.15);
            border-color: #ff4b4b;
        }}
        .win-text {{ color: {colors["accent"]}; }}
        .loss-text {{ color: #ff4b4b; }}
        .empty-cell {{ background: transparent; border: none; }}
        
        /* BUTONLAR */
        .custom-btn {{
            background-color: {colors["accent"]};
            color: {colors["bg"]};
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            display: block;
            text-align: center;
        }}
        .custom-btn:hover {{
            background-color: {colors["accent_hover"]};
            color: white;
        }}
        
        /* GENEL YAZI RENGİ DÜZELTMESİ (LIGHT MODE İÇİN) */
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{
            color: {colors["text"]} !important;
        }}
        .neon-title {{ color: {colors["title"]} !important; }}
        
        /* RULE BOX */
        .rule-box {{
            background: rgba(0,0,0,0.05);
            border-left: 4px solid {colors["accent"]};
            padding: 15px;
            margin: 10px 0;
        }}
        
        /* TABS */
        .stTabs [data-baseweb="tab"] {{ color: {colors["grid_text"]}; }}
        .stTabs [data-baseweb="tab"]:hover {{ color: {colors["accent"]}; }}
        .stTabs [aria-selected="true"] {{ 
            color: {colors["accent"]} !important;
            border-bottom-color: {colors["accent"]} !important;
        }}
        
        .pricing-card {{
            background-color: {colors["card_bg"]};
            border: 1px solid {colors["border"]};
            border-radius: 12px;
            padding: 30px;
            text-align: center;
        }}
        .plan-price {{
            color: {colors["title"]};
            font-size: 2.5rem;
            font-weight: bold;
        }}
        .plan-name {{
            color: {colors["accent"]};
            font-weight: bold;
            letter-spacing: 2px;
        }}

    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VERİ YÜKLEME
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
# 3. BAŞLIK VE SEKME YAPISI
# ==========================================
wt = "light" if st.session_state.theme == "Light" else "dark"
components.html(f"""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>{{"symbols": [{{"proName": "BINANCE:BTCUSDT", "title": "Bitcoin"}}, {{"proName": "BINANCE:ETHUSDT", "title": "Ethereum"}}, {{"proName": "BINANCE:SOLUSDT", "title": "Solana"}}, {{"description": "USDT.D", "proName": "CRYPTOCAP:USDT.D"}}], "showSymbolLogo": true, "colorTheme": "{wt}", "isTransparent": true, "displayMode": "adaptive", "locale": "en"}}</script></div>""", height=50)

st.write("")
st.markdown('<div class="neon-title">CRAZYTOWN CAPITAL</div>', unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: {colors['accent']}; letter-spacing: 2px; font-size: 0.9rem; margin-top: -5px;'>{t('title_sub')}</p>", unsafe_allow_html=True)
st.write("")

tab1, tab2, tab3, tab4 = st.tabs([t('perf'), t('acad'), t('memb'), t('cont')])

# ==========================================
# TAB 1: PERFORMANS (Dashboard)
# ==========================================
with tab1:
    if df.empty:
        st.warning("Veri bulunamadı. Lütfen Google Sheet bağlantısını kontrol edin.")
    else:
        # KPI Hesaplamaları
        total_trades = len(df)
        wins = len(df[df['Sonuç'] == 'WIN'])
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        net_return = df['R_Kazanc'].sum()
        
        gross_profit = df[df['R_Kazanc'] > 0]['R_Kazanc'].sum()
        gross_loss = abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum())
        pf = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        net_color = colors['accent'] if net_return > 0 else "#ff4b4b"

        # KPI Kartları
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="metric-container"><div class="metric-value">{total_trades}</div><div class="metric-label">{t("total_trades")}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-container"><div class="metric-value">{win_rate:.1f}%</div><div class="metric-label">{t("win_rate")}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-container"><div class="metric-value" style="color:{net_color}">{net_return:.2f}R</div><div class="metric-label">{t("net_return")}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-container"><div class="metric-value">{pf:.2f}</div><div class="metric-label">{t("profit_factor")}</div></div>', unsafe_allow_html=True)

        # Hedef Barı
        st.write(""); st.write("")
        goal = 100.0
        progress = min(max(net_return / goal, 0.0), 1.0)
        st.markdown(f"""<div style="display:flex; justify-content:space-between; font-size:0.8rem; color:{colors['grid_text']}; margin-bottom:5px;"><span>{t('season_goal')} ({goal}R)</span><span style="color:{colors['accent']}">{int(progress*100)}% {t('completed')}</span></div>""", unsafe_allow_html=True)
        st.progress(progress)
        st.write("")

        # Grafikler
        plotly_theme = "plotly_white" if st.session_state.theme == "Light" else "plotly_dark"
        chart_bg = "rgba(0,0,0,0)"
        
        g1, g2 = st.columns([2, 1])
        with g1:
            df['Cum'] = df['R_Kazanc'].cumsum()
            fig = go.Figure()
            fill_c = f"rgba(0, 255, 204, 0.2)" if st.session_state.theme == "Dark" else f"rgba(0, 119, 182, 0.2)"
            fig.add_trace(go.Scatter(x=df['Tarih'], y=df['Cum'], mode='lines', fill='tozeroy', line=dict(color=colors['accent'], width=2), fillcolor=fill_c))
            fig.update_layout(template=plotly_theme, paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, margin=dict(l=0, r=0, t=10, b=0), height=300, 
                              xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=colors['border']))
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            fig_pie = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.7, color='Sonuç', color_discrete_map={'WIN':colors['accent'], 'LOSS':'#ff4b4b'})
            fig_pie.update_layout(template=plotly_theme, paper_bgcolor=chart_bg, showlegend=False, margin=dict(l=20, r=20, t=10, b=20), height=300, 
                                  annotations=[dict(text=f"{win_rate:.0f}%", x=0.5, y=0.5, font_size=24, showarrow=False, font_color=colors['title'])])
            st.plotly_chart(fig_pie, use_container_width=True)

        # Takvim (Calendar Heatmap)
        st.markdown("---")
        st.subheader(t("perf_cal"))
        
        try:
            df['Tarih_Dt'] = pd.to_datetime(df['Tarih'], dayfirst=True, errors='coerce')
            df.dropna(subset=['Tarih_Dt'], inplace=True)
            
            if not df.empty:
                df = df.sort_values('Tarih_Dt')
                months = df['Tarih_Dt'].dt.strftime('%Y-%m').unique()
                sel_mon = st.selectbox(t("select_month"), options=months, index=len(months)-1)
                
                year, month = map(int, sel_mon.split('-'))
                m_data = df[df['Tarih_Dt'].dt.strftime('%Y-%m') == sel_mon].copy()
                daily_p = m_data.groupby(m_data['Tarih_Dt'].dt.day)['R_Kazanc'].sum().to_dict()
                cal_mat = calendar.monthcalendar(year, month)
                
                # HTML String Oluşturma
                html_code = ['<div class="calendar-container">']
                
                day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                if st.session_state.lang == "TR": day_names = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
                if st.session_state.lang == "RU": day_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
                
                for d in day_names:
                    html_code.append(f'<div class="calendar-header">{d}</div>')
                
                month_total = 0
                for week in cal_mat:
                    for day in week:
                        if day == 0:
                            html_code.append('<div class="day-cell empty-cell"></div>')
                        else:
                            val = daily_p.get(day, 0)
                            month_total += val
                            
                            cell_cls = "day-cell"
                            p_cls = ""
                            p_txt = "0.00R"
                            
                            if day in daily_p:
                                if val > 0:
                                    cell_cls += " day-win" if st.session_state.theme == "Dark" else " day-win-light"
                                    p_cls = "win-text"
                                    p_txt = f"+{val:.2f}R"
                                elif val < 0:
                                    cell_cls += " day-loss"
                                    p_cls = "loss-text"
                                    p_txt = f"{val:.2f}R"
                            
                            html_code.append(f'<div class="{cell_cls}"><div class="day-number">{day}</div><div class="day-profit {p_cls}">{p_txt}</div></div>')
                
                html_code.append('</div>')
                st.markdown("".join(html_code), unsafe_allow_html=True)
                
                tot_col = colors['accent'] if month_total > 0 else '#ff4b4b'
                st.markdown(f"<div style='text-align:center; margin-top:15px; font-size:1.2rem; font-weight:bold; color:{tot_col}'>{t('total_monthly')}: {month_total:.2f}R</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Calendar Error: {e}")

        st.markdown("---")
        
        # ROI Simülatör ve Tablo
        st.subheader(t("roi_sim"))
        r1, r2, r3 = st.columns([1,1,2])
        with r1: cap = st.number_input(t("initial_cap"), min_value=100, value=1000)
        with r2: risk = st.slider(t("risk_trade"), 0.5, 5.0, 2.0)
        prof = cap * (risk / 100) * net_return
        bal = cap + prof
        perc = (prof / cap) * 100
        
        with r3:
            st.markdown(f"""
            <div style="background:{colors['card_bg']}; padding:15px; border-radius:10px; border:1px solid {colors['accent']}; text-align:center;">
                <span style="color:{colors['grid_text']}">{t('proj_bal')}</span><br>
                <span style="color:{colors['title']}; font-size:2rem; font-weight:bold;">${bal:,.2f}</span><br>
                <span style="color:{colors['accent']}">(+${prof:,.2f} / +{perc:.1f}%)</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        h_col, d_col = st.columns([4, 1])
        with h_col: st.markdown(f"##### {t('trade_log')}")
        with d_col: st.download_button(label=t("download"), data=df.to_csv(index=False).encode('utf-8'), file_name='log.csv', mime='text/csv')
        
        def highlight_win(row):
            c = colors['accent'] if row['Sonuç'] == 'WIN' else '#ff4b4b'
            return [f'color: {c}; font-weight:bold' if col == 'Sonuç' else f'color: {colors["text"]}' for col in row.index]
        
        st.dataframe(df.style.apply(highlight_win, axis=1), use_container_width=True, hide_index=True)

# ==========================================
# TAB 2: AKADEMİ (PDF İÇERİKLİ)
# ==========================================
with tab2:
    st.write("")
    st.markdown(f"<h2 style='text-align: center; color: {colors['accent']};'>{t('acad_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"""<div style="text-align: center; font-style: italic; color: {colors['grid_text']}; margin-bottom: 20px;">"{t('acad_quote')}"</div>""", unsafe_allow_html=True)

    # PDF İçerikleri
    with st.expander(t('lesson_1_title'), expanded=True):
        st.markdown(t('lesson_1_content'))
        st.info("Bu kurallar 'OATRADE SMC' PDF dokümanından derlenmiştir.")

    with st.expander(t('lesson_2_title')):
        st.markdown(t('lesson_2_content'))
        st.info("Fibonacci ve FVG kurulumları.")

    with st.expander(t('lesson_3_title')):
        st.markdown(t('lesson_3_content'), unsafe_allow_html=True)
        st.warning("Kurallar esnetilmez.")

# ==========================================
# TAB 3: MEMBERSHIP
# ==========================================
with tab3:
    st.write("")
    st.markdown(f"""<div class="metric-container" style="background: linear-gradient(90deg, {colors['card_bg']}, {colors['bg']}); border-color:{colors['accent']}">{t('limited_offer')}</div>""", unsafe_allow_html=True)
    st.write("")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="pricing-card"><div class="plan-name">{t('plan_starter')}</div><div class="plan-price">$30<span style="font-size:1rem;color:{colors['grid_text']}">/mo</span></div><a href="#" class="custom-btn custom-btn-outline">{t('sel_plan')}</a></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="pricing-card" style="border-color:{colors['accent']}"><div class="plan-name">{t('plan_pro')}</div><div class="plan-price">$75<span style="font-size:1rem;color:{colors['grid_text']}">/qtr</span></div><a href="#" class="custom-btn">{t('most_pop')}</a></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="pricing-card"><div class="plan-name">{t('plan_life')}</div><div class="plan-price">$250<span style="font-size:1rem;color:{colors['grid_text']}">/once</span></div><a href="#" class="custom-btn custom-btn-outline">{t('contact_sales')}</a></div>""", unsafe_allow_html=True)

# ==========================================
# TAB 4: CONTACT
# ==========================================
with tab4:
    st.write(""); c1, c2 = st.columns(2)
    with c1: st.markdown(f"""### 📨 Telegram\n<a href="https://t.me/Orhan1909" class="custom-btn">OPEN TELEGRAM</a>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""### 📧 Email\n**orhanaliyev02@gmail.com**""")

st.markdown("---")
st.markdown(f"<p style='text-align: center; color: {colors['accent_hover']}; font-size: 0.8rem;'>© 2025 Crazytown Capital. All rights reserved.</p>", unsafe_allow_html=True)
