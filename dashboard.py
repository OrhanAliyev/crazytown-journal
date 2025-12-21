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
# 0. DİL VE TEMA VERİTABANI
# ==========================================
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
        "settings": "⚙️ SETTINGS / AYARLAR",
        "lang_sel": "Language / Dil",
        "theme_sel": "Theme / Tema",
        "theme_dark": "Dark Mode (Neon)",
        "theme_light": "Light Mode (Clean)",
        "acad_title": "OA | TRADE SMC MASTERY",
        "acad_quote": "Not beating the market, but following it with discipline.",
        # AKADEMİ İÇERİKLERİ (PDF'TEN)
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
        * *Note: A wick sweep is enough, candle close is not required.*
        """,
        "lesson_2_title": "🛠️ PART 2: ENTRY SETUP (FIB & FVG)",
        "lesson_2_content": """
        ### 1. FIBONACCI RETRACEMENT
        Draw Fib on the impulse leg created after the liquidity sweep.
        * **ENTRY ZONE:** `0.75` - `0.60` (Golden Pocket)
        * **STOP LOSS:** `1` (Start of the impulse)
        * **TP-1:** `0.25`
        * **TP-2:** `-0.18`
        
        ### 2. FVG REJECTION
        * Price must tap into a **Fair Value Gap (FVG)** inside the Golden Zone.
        * Wait for a rejection wick or reaction.
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
        "settings": "⚙️ AYARLAR / SETTINGS",
        "lang_sel": "Dil / Language",
        "theme_sel": "Tema / Theme",
        "theme_dark": "Koyu Mod (Neon)",
        "theme_light": "Açık Mod (Temiz)",
        "acad_title": "OA | TRADE SMC USTALIK SINIFI",
        "acad_quote": "Piyasayı yenmek değil, disiplinle takip etmek.",
        # AKADEMİ İÇERİKLERİ (PDF'TEN)
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
        * *Not: Fitil atması (Wick) yeterlidir, mum kapanışı şart değildir.*
        """,
        "lesson_2_title": "🛠️ BÖLÜM 2: GİRİŞ STRATEJİSİ (FIB & FVG)",
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
            <li><b>CHOCH YOK:</b> Düşük zaman diliminde kırılım (Choch) beklenmez. Sizi geç sokar veya yanıltır.</li>
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
        "lang_sel": "Язык / Language",
        "theme_sel": "Тема / Theme",
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
        """,
        "lesson_3_title": "⚠️ ЧАСТЬ 3: ПРАВИЛА И УПРАВЛЕНИЕ",
        "lesson_3_content": """
        <div class="rule-box">
        <h4>🚨 ПРАВИЛА</h4>
        <ul>
            <li><b>НЕТ CHOCH:</b> Не ждем смены характера движения на младших таймфреймах.</li>
            <li><b>НЕТ СДЕЛОК ВНЕ СЕССИЙ:</b> Дисциплина прежде всего.</li>
        </ul>
        </div>
        """
    }
}

# ==========================================
# 1. SAYFA VE SESSION STATE
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

def t(key):
    return TRANSLATIONS[st.session_state.lang][key]

# --- AYARLAR MENÜSÜ ---
with st.expander(t('settings'), expanded=False):
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sel_lang = st.selectbox(t('lang_sel'), ["TR", "EN", "RU"], index=["TR", "EN", "RU"].index(st.session_state.lang))
        if sel_lang != st.session_state.lang:
            st.session_state.lang = sel_lang
            st.rerun()
    with col_s2:
        theme_options = ["Dark", "Light"]
        theme_labels = [t('theme_dark'), t('theme_light')]
        current_index = 0 if st.session_state.theme == "Dark" else 1
        sel_theme_label = st.selectbox(t('theme_sel'), theme_labels, index=current_index)
        
        new_theme = "Dark" if sel_theme_label == t('theme_dark') else "Light"
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()

# ==========================================
# 2. DİNAMİK CSS VE RENK PALETLERİ
# ==========================================
if st.session_state.theme == "Dark":
    # --- KOYU MOD ---
    bg_color = "#050505" # Daha derin siyah
    text_color = "#e0e0e0"
    card_bg = "rgba(20, 20, 25, 0.9)" # Hafif transparan
    border_color = "#333"
    accent_color = "#00ffcc" # Daha parlak neon
    accent_hover = "#00ccaa"
    secondary_bg = "#111"
    grid_header_color = "#888"
    title_color = "#ffffff"
    cal_text_color = "#ffffff"
    
    # Animasyon: Koyu arka planda parlak neon çizgiler
    anim_bg_image = f"""
        linear-gradient(45deg, rgba(0, 255, 204, 0.03) 25%, transparent 25%, transparent 75%, rgba(0, 255, 204, 0.03) 75%, rgba(0, 255, 204, 0.03)),
        linear-gradient(45deg, rgba(0, 255, 204, 0.03) 25%, transparent 25%, transparent 75%, rgba(0, 255, 204, 0.03) 75%, rgba(0, 255, 204, 0.03))
    """
else:
    # --- AÇIK MOD ---
    bg_color = "#f4f7f6"
    text_color = "#1f2833"
    card_bg = "#ffffff"
    border_color = "#d1d5db"
    accent_color = "#0077b6" # Profesyonel Mavi
    accent_hover = "#005f91"
    secondary_bg = "#e5e7eb"
    grid_header_color = "#4b5563"
    title_color = "#000000"
    cal_text_color = "#1f2833" # Takvim yazısı koyu
    
    # Animasyon: Açık arka planda hafif mavi çizgiler
    anim_bg_image = f"""
        linear-gradient(45deg, rgba(0, 119, 182, 0.05) 25%, transparent 25%, transparent 75%, rgba(0, 119, 182, 0.05) 75%, rgba(0, 119, 182, 0.05)),
        linear-gradient(45deg, rgba(0, 119, 182, 0.05) 25%, transparent 25%, transparent 75%, rgba(0, 119, 182, 0.05) 75%, rgba(0, 119, 182, 0.05))
    """

# --- CSS ENJEKSİYONU ---
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');

        /* RESET */
        div[class^="viewerBadge_container"], .viewerBadge_container__1QSob {{display: none !important;}}
        #MainMenu, header, footer, .stDeployButton, [data-testid="stToolbar"] {{display: none !important;}}
        .stApp > header {{display: none !important;}}
        .block-container {{padding-top: 2rem !important; padding-bottom: 2rem !important;}}

        /* ANA GÖVDE VE ARKA PLAN ANIMASYONU */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
            font-family: 'Inter', sans-serif;
            background-image: {anim_bg_image};
            background-position: 0 0, 30px 30px;
            background-size: 60px 60px;
            animation: slide 10s linear infinite;
        }}
        
        @keyframes slide {{
            0% {{background-position: 0 0, 30px 30px;}}
            100% {{background-position: 60px 60px, 90px 90px;}}
        }}

        /* NEON BAŞLIK */
        .neon-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 3.5rem;
            text-align: center;
            color: {title_color};
            text-transform: uppercase;
            font-weight: 900;
            margin-bottom: 0px;
            letter-spacing: 4px;
            /* Sadece Dark Modda Parlama Efekti */
            {f"text-shadow: 0 0 10px {accent_color}, 0 0 20px {accent_color}, 0 0 40px {accent_color};" if st.session_state.theme == "Dark" else ""}
            animation: pulse 3s infinite alternate;
        }}
        
        @keyframes pulse {{
            0% {{opacity: 1; transform: scale(1);}}
            100% {{opacity: 0.95; transform: scale(0.99);}}
        }}

        /* TABS */
        .stTabs [data-baseweb="tab-list"] {{gap: 20px; border-bottom: 1px solid {border_color}; padding-top: 10px;}}
        .stTabs [data-baseweb="tab"] {{height: 50px; color: {grid_header_color}; font-weight: 600; border: none; background-color: transparent;}}
        .stTabs [data-baseweb="tab"]:hover {{color: {accent_color};}}
        .stTabs [aria-selected="true"] {{color: {accent_color} !important; border-bottom: 2px solid {accent_color} !important;}}

        /* METRİK KARTLARI */
        .metric-container {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
            backdrop-filter: blur(5px);
        }}
        .metric-container:hover {{transform: translateY(-5px); border-color: {accent_color};}}
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: {title_color};
            margin-bottom: 5px;
        }}
        .metric-label {{
            font-size: 0.8rem;
            color: {grid_header_color};
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
        }}

        /* PRICING CARDS */
        .pricing-card {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 40px 20px;
            text-align: center;
            height: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}
        .pricing-card:hover {{border-color: {accent_color}; transform: translateY(-5px);}}
        .plan-name {{color: {accent_color}; font-size: 1.1rem; font-weight: 700; letter-spacing: 2px; margin-bottom: 15px;}}
        .plan-price {{color: {title_color}; font-size: 2.5rem; font-weight: 700; margin-bottom: 30px;}}
        .feature-list {{color: {text_color}; margin-bottom: 20px; line-height: 1.6;}}

        /* BUTTONS */
        .custom-btn {{display: inline-block; padding: 12px 30px; color: {bg_color}; background-color: {accent_color}; border-radius: 4px; text-decoration: none; font-weight: 600; width: 100%; text-align: center; transition: 0.3s;}}
        .custom-btn:hover {{background-color: {accent_hover}; color: #fff;}}
        .custom-btn-outline {{background-color: transparent; border: 1px solid {accent_color}; color: {accent_color};}}
        .custom-btn-outline:hover {{background-color: {accent_color}; color: {bg_color};}}

        /* TAKVİM GRID CSS */
        .calendar-container {{display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; margin-top: 20px;}}
        .calendar-header {{text-align: center; font-weight: bold; color: {grid_header_color}; padding-bottom: 10px; border-bottom: 1px solid {border_color};}}
        .day-cell {{
            background-color: {secondary_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            height: 100px;
            padding: 10px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            gap: 5px;
            transition: all 0.2s ease;
        }}
        .day-cell:hover {{border-color: {accent_color}; transform: scale(1.02); z-index: 2;}}
        .day-number {{
            font-size: 1rem;
            color: {cal_text_color};
            font-weight: bold;
            opacity: 0.8;
        }}
        .day-profit {{font-size: 1.1rem; font-weight: 800; align-self: center; margin-top: auto; margin-bottom: auto;}}
        
        .day-win {{background-color: rgba(0, 255, 204, 0.1); border-color: {accent_color};}}
        .day-win-light {{background-color: rgba(0, 119, 182, 0.1); border-color: {accent_color};}}
        
        .day-loss {{background-color: rgba(255, 75, 75, 0.1); border-color: #ff4b4b;}}
        
        .win-text {{color: {accent_color};}}
        .loss-text {{color: #ff4b4b;}}
        .empty-cell {{background-color: transparent; border: none;}}

        /* DIĞERLERI */
        .stDataFrame {{border: 1px solid {border_color};}}
        .stProgress > div > div > div > div {{background-color: {accent_color};}}
        .streamlit-expanderContent, .stMarkdown p, h1, h2, h3, h4, h5, h6 {{color: {text_color} !important;}}
        .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {{background-color: {secondary_bg}; color: {text_color}; border-color: {border_color};}}
        
        /* TESTIMONIAL */
        .testimonial-card {{background-color: {secondary_bg}; border-left: 3px solid {accent_color}; padding: 20px; margin-bottom: 20px;}}
        .testimonial-text {{font-style: italic; color: {text_color};}}
        .testimonial-author {{margin-top: 10px; color: {accent_color}; font-weight: bold;}}
        
        /* RULE BOX ACADEMY */
        .rule-box {{background: rgba(0,0,0,0.2); padding: 15px; border-left: 4px solid {accent_color}; margin: 10px 0; color: {text_color};}}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. VERİ BAĞLANTISI
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
# 4. BAŞLIK VE WIDGET
# ==========================================
widget_theme = "light" if st.session_state.theme == "Light" else "dark"
components.html(f"""
<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>{{"symbols": [{{"proName": "BINANCE:BTCUSDT", "title": "Bitcoin"}}, {{"proName": "BINANCE:ETHUSDT", "title": "Ethereum"}}, {{"proName": "BINANCE:SOLUSDT", "title": "Solana"}}, {{"description": "USDT.D", "proName": "CRYPTOCAP:USDT.D"}}], "showSymbolLogo": true, "colorTheme": "{widget_theme}", "isTransparent": true, "displayMode": "adaptive", "locale": "en"}}</script></div>
""", height=50)

st.write("")
# YENİ NEON BAŞLIK
st.markdown(f'<div class="neon-title">CRAZYTOWN CAPITAL</div>', unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: {accent_color}; letter-spacing: 2px; font-size: 0.9rem; margin-top: -5px;'>{t('title_sub')}</p>", unsafe_allow_html=True)
st.write("")

# TABLAR
tab1, tab2, tab3, tab4 = st.tabs([t('perf'), t('acad'), t('memb'), t('cont')])

# ==========================================
# TAB 1: PERFORMANS
# ==========================================
with tab1:
    if df.empty:
        st.warning("Data not found.")
    else:
        # KPI
        total = len(df)
        win = len(df[df['Sonuç'] == 'WIN'])
        rate = (win / total * 100) if total > 0 else 0
        net_r_total = df['R_Kazanc'].sum()
        gross_profit = df[df['R_Kazanc'] > 0]['R_Kazanc'].sum()
        gross_loss = abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum())
        pf = (gross_profit / gross_loss) if gross_loss > 0 else 0
        net_color = accent_color if net_r_total > 0 else "#ff4b4b"

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="metric-container"><div class="metric-value">{total}</div><div class="metric-label">{t("total_trades")}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-container"><div class="metric-value">{rate:.1f}%</div><div class="metric-label">{t("win_rate")}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-container"><div class="metric-value" style="color:{net_color}">{net_r_total:.2f}R</div><div class="metric-label">{t("net_return")}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-container"><div class="metric-value">{pf:.2f}</div><div class="metric-label">{t("profit_factor")}</div></div>', unsafe_allow_html=True)

        st.write(""); st.write("")
        target_r = 100.0
        current_progress = min(max(net_r_total / target_r, 0.0), 1.0)
        st.markdown(f"""<div style="margin-bottom: 5px; color: {grid_header_color}; font-size: 0.8rem; display: flex; justify-content: space-between;"><span>{t("season_goal")} ({target_r}R)</span><span style="color: {accent_color};">{int(current_progress*100)}% {t("completed")}</span></div>""", unsafe_allow_html=True)
        st.progress(current_progress)
        st.write("")

        # Plotly
        ptemp = "plotly_white" if st.session_state.theme == "Light" else "plotly_dark"
        bg_c = "rgba(0,0,0,0)"
        
        g1, g2 = st.columns([2, 1])
        with g1:
            df['Cum'] = df['R_Kazanc'].cumsum()
            fig = go.Figure()
            fill_c = f"rgba(0, 255, 204, 0.2)" if st.session_state.theme == "Dark" else f"rgba(0, 119, 182, 0.2)"
            fig.add_trace(go.Scatter(x=df['Tarih'], y=df['Cum'], mode='lines', fill='tozeroy', line=dict(color=accent_color, width=2), fillcolor=fill_c))
            fig.update_layout(template=ptemp, paper_bgcolor=bg_c, plot_bgcolor=bg_c, margin=dict(l=0, r=0, t=10, b=0), height=300, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=border_color))
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            fig_pie = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.7, color='Sonuç', color_discrete_map={'WIN':accent_color, 'LOSS':'#ff4b4b'})
            fig_pie.update_layout(template=ptemp, paper_bgcolor=bg_c, showlegend=False, margin=dict(l=20, r=20, t=10, b=20), height=300, annotations=[dict(text=f"{rate:.0f}%", x=0.5, y=0.5, font_size=24, showarrow=False, font_color=title_color)])
            st.plotly_chart(fig_pie, use_container_width=True)

        # TAKVİM
        st.markdown("---")
        st.subheader(t("perf_cal"))
        try:
            df['Tarih_Dt'] = pd.to_datetime(df['Tarih'], dayfirst=True, errors='coerce')
            df.dropna(subset=['Tarih_Dt'], inplace=True)
            if not df.empty:
                df = df.sort_values('Tarih_Dt')
                av_months = df['Tarih_Dt'].dt.strftime('%Y-%m').unique()
                sel_mon = st.selectbox(t("select_month"), options=av_months, index=len(av_months)-1)
                
                sel_y, sel_m = map(int, sel_mon.split('-'))
                m_data = df[df['Tarih_Dt'].dt.strftime('%Y-%m') == sel_mon].copy()
                d_prof = m_data.groupby(m_data['Tarih_Dt'].dt.day)['R_Kazanc'].sum().to_dict()
                cal_mat = calendar.monthcalendar(sel_y, sel_m)
                
                html_p = ['<div class="calendar-container">']
                d_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                if st.session_state.lang == "TR": d_names = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
                if st.session_state.lang == "RU": d_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
                
                for dn in d_names: html_p.append(f'<div class="calendar-header">{dn}</div>')
                
                m_tot = 0
                for week in cal_mat:
                    for day in week:
                        if day == 0:
                            html_p.append('<div class="day-cell empty-cell"></div>')
                        else:
                            p = d_prof.get(day, 0)
                            m_tot += p
                            cc = "day-cell"
                            pt, pc = "0.00R", ""
                            
                            if day in d_prof:
                                if p > 0:
                                    cc += " day-win" if st.session_state.theme == "Dark" else " day-win-light"
                                    pc = "win-text"
                                    pt = f"+{p:.2f}R"
                                elif p < 0:
                                    cc += " day-loss"
                                    pc = "loss-text"
                                    pt = f"{p:.2f}R"
                            
                            html_p.append(f'<div class="{cc}"><div class="day-number">{day}</div><div class="day-profit {pc}">{pt}</div></div>')
                
                html_p.append('</div>')
                st.markdown("".join(html_p), unsafe_allow_html=True)
                tc = accent_color if m_tot > 0 else '#ff4b4b'
                st.markdown(f"<div style='text-align:center; margin-top:15px; font-size:1.2rem; font-weight:bold; color:{tc}'>{t('total_monthly')}: {m_tot:.2f}R</div>", unsafe_allow_html=True)
        except Exception as e: st.error(e)

        st.markdown("---")
        st.subheader(t("market_intel"))
        m1, m2 = st.columns(2)
        with m1: components.html(f"""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{{"interval": "4h", "width": "100%", "isTransparent": true, "height": "400", "symbol": "BINANCE:BTCUSDT", "showIntervalTabs": true, "displayMode": "single", "locale": "en", "colorTheme": "{widget_theme}"}}</script></div>""", height=400)
        with m2: components.html(f"""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>{{"colorTheme": "{widget_theme}", "isTransparent": true, "width": "100%", "height": "400", "locale": "en", "importanceFilter": "-1,0,1", "currencyFilter": "USD"}}</script></div>""", height=400)

        st.markdown("---")
        st.subheader(t("roi_sim"))
        r1, r2, r3 = st.columns([1,1,2])
        with r1: u_cap = st.number_input(t("initial_cap"), min_value=100, value=1000)
        with r2: u_risk = st.slider(t("risk_trade"), 0.5, 5.0, 2.0)
        p_prof = u_cap * (u_risk / 100) * net_r_total
        f_bal = u_cap + p_prof
        roi_p = (p_prof / u_cap) * 100
        with r3: st.markdown(f"""<div style="background:{card_bg}; padding:15px; border-radius:8px; border:1px solid {accent_color}; text-align:center;"><span style="color:{grid_header_color};">{t("proj_bal")}</span><br><span style="color:{title_color}; font-size:2.2rem; font-weight:bold;">${f_bal:,.2f}</span><br><span style="color:{accent_color};">(+${p_prof:,.2f} / +%{roi_p:.1f})</span></div>""", unsafe_allow_html=True)

        st.markdown("---")
        ch, cd = st.columns([4, 1])
        with ch: st.markdown(f"##### {t('trade_log')}")
        with cd: st.download_button(label=t("download"), data=df.to_csv(index=False).encode('utf-8'), file_name='log.csv', mime='text/csv')
        
        def sdf(row):
            c = accent_color if row['Sonuç'] == 'WIN' else '#ff4b4b'
            tc = text_color
            return [f'color: {c}; font-weight: 600' if col == 'Sonuç' else f'color: {tc}' for col in row.index]
        st.dataframe(df.style.apply(sdf, axis=1), use_container_width=True, hide_index=True)

# ==========================================
# TAB 2: AKADEMİ (DÜZELTİLDİ)
# ==========================================
with tab2:
    st.write("")
    st.markdown(f"<h2 style='text-align: center; color: {accent_color};'>{t('acad_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"""<div style="text-align: center; font-style: italic; color: {grid_header_color}; margin-bottom: 20px;">"{t('acad_quote')}"</div>""", unsafe_allow_html=True)
    
    with st.expander(t('lesson_1_title'), expanded=True):
        st.markdown(t('lesson_1_content'))
    
    with st.expander(t('lesson_2_title')):
        st.markdown(t('lesson_2_content'))
        
    with st.expander(t('lesson_3_title')):
        st.markdown(t('lesson_3_content'), unsafe_allow_html=True)

# ==========================================
# TAB 3: MEMBERSHIP
# ==========================================
with tab3:
    st.write(""); st.markdown(f"""<div class="promo-banner">{t('limited_offer')}</div>""", unsafe_allow_html=True)
    st.subheader(t('feedback'))
    s1, s2, s3 = st.columns(3)
    with s1: st.markdown(f"""<div class="testimonial-card"><div class="testimonial-text">"Risk management is top tier."</div><div class="testimonial-author">@Crypto***</div></div>""", unsafe_allow_html=True)
    with s2: st.markdown(f"""<div class="testimonial-card"><div class="testimonial-text">"Transparency sold me."</div><div class="testimonial-author">@Alex***</div></div>""", unsafe_allow_html=True)
    with s3: st.markdown(f"""<div class="testimonial-card"><div class="testimonial-text">"FVG setups are insane."</div><div class="testimonial-author">@Mehmet***</div></div>""", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"""<div class="pricing-card"><div class="plan-name">{t('plan_starter')}</div><div class="plan-price">$30<span style="font-size:1rem;color:{grid_header_color}">/mo</span></div><a href="https://t.me/Orhan1909" class="custom-btn custom-btn-outline">{t('sel_plan')}</a></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div class="pricing-card" style="border-color:{accent_color}"><div class="plan-name">{t('plan_pro')}</div><div class="plan-price">$75<span style="font-size:1rem;color:{grid_header_color}">/qtr</span></div><a href="https://t.me/Orhan1909" class="custom-btn">{t('most_pop')}</a></div>""", unsafe_allow_html=True)
    with c3: st.markdown(f"""<div class="pricing-card"><div class="plan-name">{t('plan_life')}</div><div class="plan-price">$250<span style="font-size:1rem;color:{grid_header_color}">/once</span></div><a href="https://t.me/Orhan1909" class="custom-btn custom-btn-outline">{t('contact_sales')}</a></div>""", unsafe_allow_html=True)

# ==========================================
# TAB 4: CONTACT
# ==========================================
with tab4:
    st.write(""); c1, c2 = st.columns(2)
    with c1: st.markdown("""### 📨 Telegram\n<a href="https://t.me/Orhan1909" class="custom-btn">OPEN TELEGRAM</a>""", unsafe_allow_html=True)
    with c2: st.markdown("""### 📧 Email\n**orhanaliyev02@gmail.com**""")
    st.divider(); st.subheader(t('faq'))
    with st.expander("Access?"): st.write("Contact via Telegram.")

st.markdown("---")
st.markdown(f"<p style='text-align: center; color: {accent_hover}; font-size: 0.8rem;'>© 2025 Crazytown Capital. All rights reserved.</p>", unsafe_allow_html=True)
