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
        "title": "ALGORITHMIC TRADING SYSTEMS",
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
        "monthly_breakdown": "🗓️ MONTHLY BREAKDOWN",
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
        "theme_dark": "Dark Mode (Gece)",
        "theme_light": "Light Mode (Gündüz)",
        "acad_title": "OA | TRADE SMC MASTERY",
        "acad_quote": "Not beating the market, but following it with discipline.",
        "lesson_1": "📌 PART 1: TIME & CONTEXT",
        "lesson_2": "🛠️ PART 2: ENTRY SETUP",
        "lesson_3": "⚠️ PART 3: RULES & EXECUTION"
    },
    "TR": {
        "title": "ALGORİTMİK İŞLEM SİSTEMLERİ",
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
        "monthly_breakdown": "🗓️ AYLIK DETAY",
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
        "theme_dark": "Koyu Mod",
        "theme_light": "Açık Mod",
        "acad_title": "OA | TRADE SMC USTALIK SINIFI",
        "acad_quote": "Piyasayı yenmek değil, disiplinle takip etmek.",
        "lesson_1": "📌 BÖLÜM 1: ZAMAN VE BAĞLAM",
        "lesson_2": "🛠️ BÖLÜM 2: GİRİŞ STRATEJİSİ",
        "lesson_3": "⚠️ BÖLÜM 3: KURALLAR VE YÖNETİM"
    },
    "RU": {
        "title": "АЛГОРИТМИЧЕСКИЕ ТОРГОВЫЕ СИСТЕМЫ",
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
        "monthly_breakdown": "🗓️ ЕЖЕМЕСЯЧНЫЙ ОТЧЕТ",
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
        "lesson_1": "📌 ЧАСТЬ 1: ВРЕМЯ И КОНТЕКСТ",
        "lesson_2": "🛠️ ЧАСТЬ 2: СТРАТЕГИЯ ВХОДА",
        "lesson_3": "⚠️ ЧАСТЬ 3: ПРАВИЛА И УПРАВЛЕНИЕ"
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

# Session State Başlatma
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
    bg_color = "#0b0c10"
    text_color = "#c5c6c7"
    card_bg = "#1f2833"
    border_color = "#2d3845"
    accent_color = "#66fcf1"
    accent_hover = "#45a29e"
    secondary_bg = "#15161a"
    grid_header_color = "#8892b0"
    title_color = "#FFFFFF"
    
    # Animasyon: Koyu arka planda parlak çizgiler
    anim_gradient_1 = "rgba(102, 252, 241, 0.03)"
    anim_gradient_2 = "rgba(102, 252, 241, 0)"
    
else:
    # --- AÇIK MOD (Light Mode Fixes) ---
    bg_color = "#f0f2f6"       # Hafif gri arka plan (Göz yormaz)
    text_color = "#31333F"     # Koyu gri yazı (Okunurluk için)
    card_bg = "#ffffff"        # Beyaz kartlar
    border_color = "#d1d5db"
    accent_color = "#0083B8"   # Koyu Mavi/Turkuaz (Beyaz üstünde net görünür)
    accent_hover = "#006791"
    secondary_bg = "#e5e7eb"   # İkincil alanlar (Calendar grid gibi)
    grid_header_color = "#4b5563"
    title_color = "#111111"    # Simsiyah başlık
    
    # Animasyon: Açık arka planda hafif mavi çizgiler
    anim_gradient_1 = "rgba(0, 131, 184, 0.05)"
    anim_gradient_2 = "rgba(0, 131, 184, 0)"

# --- CSS ENJEKSİYONU ---
st.markdown(f"""
    <style>
        /* TEMEL SIFIRLAMA */
        div[class^="viewerBadge_container"], .viewerBadge_container__1QSob {{display: none !important;}}
        #MainMenu, header, footer, .stDeployButton, [data-testid="stToolbar"] {{display: none !important;}}
        .stApp > header {{display: none !important;}}
        .block-container {{padding-top: 1rem !important; padding-bottom: 2rem !important;}}

        /* ANA GÖVDE VE ANİMASYON */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
            font-family: 'Inter', sans-serif;
        }}
        
        /* HAREKETLİ ELMAS DESENİ */
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0; left: 0;
            width: 200%; height: 200%;
            background-image: 
                linear-gradient(45deg, {anim_gradient_1} 25%, transparent 25%, transparent 75%, {anim_gradient_1} 75%, {anim_gradient_1}),
                linear-gradient(45deg, {anim_gradient_1} 25%, transparent 25%, transparent 75%, {anim_gradient_1} 75%, {anim_gradient_1});
            background-position: 0 0, 20px 20px;
            background-size: 40px 40px;
            opacity: 1;
            z-index: -1;
            animation: diamondMove 60s linear infinite;
        }}
        
        @keyframes diamondMove {{
            0% {{ transform: translate(0, 0); }}
            100% {{ transform: translate(-50px, -50px); }}
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
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
        }}
        .metric-container:hover {{transform: translateY(-2px); border-color: {accent_color};}}
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: {title_color}; /* Light modda siyah, dark modda beyaz */
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

        /* TESTIMONIALS */
        .testimonial-card {{
            background-color: {secondary_bg};
            border-left: 3px solid {accent_color};
            padding: 20px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 20px;
        }}
        .testimonial-text {{font-style: italic; color: {text_color}; font-size: 0.95rem;}}
        .testimonial-author {{margin-top: 10px; color: {accent_color}; font-weight: bold; font-size: 0.85rem;}}

        /* BUTTONS */
        .custom-btn {{display: inline-block; padding: 12px 30px; color: {bg_color}; background-color: {accent_color}; border-radius: 4px; text-decoration: none; font-weight: 600; width: 100%; text-align: center; transition: 0.3s;}}
        .custom-btn:hover {{background-color: {accent_hover}; color: #fff;}}
        .custom-btn-outline {{background-color: transparent; border: 1px solid {accent_color}; color: {accent_color};}}
        .custom-btn-outline:hover {{background-color: {accent_color}; color: {bg_color};}}

        /* TAKVİM GRID */
        .calendar-container {{display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; margin-top: 20px;}}
        .calendar-header {{text-align: center; font-weight: bold; color: {grid_header_color}; padding-bottom: 10px; border-bottom: 1px solid {border_color};}}
        .day-cell {{
            background-color: {secondary_bg}; /* Koyu/Açık modda ikincil renk */
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
        .day-cell:hover {{border-color: {accent_color}; transform: scale(1.02);}}
        .day-number {{
            font-size: 1rem;
            color: {text_color}; /* Light modda koyu renk olacak */
            font-weight: bold;
            opacity: 0.8;
        }}
        .day-profit {{font-size: 1.1rem; font-weight: 800; align-self: center; margin-top: auto; margin-bottom: auto;}}
        .day-win {{background-color: rgba(102, 252, 241, 0.15); border-color: {accent_color};}} 
        /* Light mode win background fix */
        .day-win-light {{background-color: rgba(0, 131, 184, 0.1); border-color: {accent_color};}}

        .win-text {{color: {accent_color};}}
        .loss-text {{color: #ff4b4b;}}
        .empty-cell {{background-color: transparent; border: none;}}

        /* DIĞERLERI */
        .stDataFrame {{border: 1px solid {border_color};}}
        .stProgress > div > div > div > div {{background-color: {accent_color};}}
        
        /* EXPANDER TEXT FIX */
        .streamlit-expanderContent {{color: {text_color};}}
        .stMarkdown p {{color: {text_color};}}
        h1, h2, h3, h4, h5, h6 {{color: {title_color} !important;}}
        
        /* Input Fields Background Fix */
        .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {{
            background-color: {secondary_bg}; 
            color: {text_color};
            border-color: {border_color};
        }}
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
# 4. HEADER
# ==========================================
# Widget Theme Selection
widget_theme = "light" if st.session_state.theme == "Light" else "dark"

components.html(f"""
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {{
  "symbols": [{{"proName": "BINANCE:BTCUSDT", "title": "Bitcoin"}}, {{"proName": "BINANCE:ETHUSDT", "title": "Ethereum"}}, {{"proName": "BINANCE:SOLUSDT", "title": "Solana"}}, {{"description": "USDT.D", "proName": "CRYPTOCAP:USDT.D"}}],
  "showSymbolLogo": true, "colorTheme": "{widget_theme}", "isTransparent": true, "displayMode": "adaptive", "locale": "en"
}}
  </script>
</div>
""", height=50)

st.write("")
st.markdown(f"<h1 style='text-align: center; font-size: 3rem; color: {title_color};'>CRAZYTOWN CAPITAL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: {accent_color}; margin-top: -15px; letter-spacing: 2px; font-size: 0.9rem;'>{t('title')}</p>", unsafe_allow_html=True)
st.write("")

# TABLAR
tab1, tab2, tab3, tab4 = st.tabs([t('perf'), t('acad'), t('memb'), t('cont')])

# ==========================================
# TAB 1: PERFORMANCE
# ==========================================
with tab1:
    if df.empty:
        st.warning("System initializing... Data not found or sheet is empty.")
    else:
        # KPI & GRAFİKLER
        total = len(df)
        win = len(df[df['Sonuç'] == 'WIN'])
        rate = (win / total * 100) if total > 0 else 0
        net_r_total = df['R_Kazanc'].sum()
        
        gross_profit = df[df['R_Kazanc'] > 0]['R_Kazanc'].sum()
        gross_loss = abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum())
        pf = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        net_color = accent_color if net_r_total > 0 else "#ff4b4b"

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f'<div class="metric-container"><div class="metric-value">{total}</div><div class="metric-label">{t("total_trades")}</div></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric-container"><div class="metric-value">{rate:.1f}%</div><div class="metric-label">{t("win_rate")}</div></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="metric-container"><div class="metric-value" style="color:{net_color}">{net_r_total:.2f}R</div><div class="metric-label">{t("net_return")}</div></div>', unsafe_allow_html=True)
        col4.markdown(f'<div class="metric-container"><div class="metric-value">{pf:.2f}</div><div class="metric-label">{t("profit_factor")}</div></div>', unsafe_allow_html=True)

        st.write(""); st.write("")
        target_r = 100.0
        current_progress = min(max(net_r_total / target_r, 0.0), 1.0)
        
        st.markdown(f"""
        <div style="margin-bottom: 5px; color: {grid_header_color}; font-size: 0.8rem; display: flex; justify-content: space-between;">
            <span>{t("season_goal")} ({target_r}R)</span>
            <span style="color: {accent_color};">{int(current_progress*100)}% {t("completed")}</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(current_progress)
        st.write("")

        # Plotly Teması Ayarlama
        plotly_template = "plotly_white" if st.session_state.theme == "Light" else "plotly_dark"
        chart_bg_color = "rgba(0,0,0,0)"

        g1, g2 = st.columns([2, 1])
        with g1:
            df['Cum'] = df['R_Kazanc'].cumsum()
            fig = go.Figure()
            # Gradient fill (Tema bazlı opaklık)
            fill_color = f"rgba(102, 252, 241, 0.2)" if st.session_state.theme == "Dark" else f"rgba(0, 131, 184, 0.2)"
            
            fig.add_trace(go.Scatter(x=df['Tarih'], y=df['Cum'], mode='lines', fill='tozeroy', line=dict(color=accent_color, width=2), fillcolor=fill_color))
            
            fig.update_layout(template=plotly_template, paper_bgcolor=chart_bg_color, plot_bgcolor=chart_bg_color, margin=dict(l=0, r=0, t=10, b=0), height=300, 
                              xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=border_color))
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            fig_pie = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.7, color='Sonuç', color_discrete_map={'WIN':accent_color, 'LOSS':'#ff4b4b'})
            fig_pie.update_layout(template=plotly_template, paper_bgcolor=chart_bg_color, showlegend=False, margin=dict(l=20, r=20, t=10, b=20), height=300, 
                                  annotations=[dict(text=f"{rate:.0f}%", x=0.5, y=0.5, font_size=24, showarrow=False, font_color=title_color)])
            st.plotly_chart(fig_pie, use_container_width=True)

        # TAKVİM (LIGHT MODE DÜZELTMELİ)
        st.markdown("---")
        st.subheader(t("perf_cal"))
        
        try:
            df['Tarih_Dt'] = pd.to_datetime(df['Tarih'], dayfirst=True, errors='coerce')
            df.dropna(subset=['Tarih_Dt'], inplace=True)
            
            if not df.empty:
                df = df.sort_values('Tarih_Dt')
                available_months = df['Tarih_Dt'].dt.strftime('%Y-%m').unique()
                selected_month_str = st.selectbox(t("select_month"), options=available_months, index=len(available_months)-1)
                
                selected_year, selected_month_int = map(int, selected_month_str.split('-'))
                monthly_data = df[df['Tarih_Dt'].dt.strftime('%Y-%m') == selected_month_str].copy()
                daily_profits = monthly_data.groupby(monthly_data['Tarih_Dt'].dt.day)['R_Kazanc'].sum().to_dict()
                cal_matrix = calendar.monthcalendar(selected_year, selected_month_int)
                
                html_parts = ['<div class="calendar-container">']
                
                if st.session_state.lang == "TR": days_tr = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
                elif st.session_state.lang == "RU": days_tr = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
                else: days_tr = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

                for day_name in days_tr:
                    html_parts.append(f'<div class="calendar-header">{day_name}</div>')
                
                total_month_profit = 0
                for week in cal_matrix:
                    for day in week:
                        if day == 0:
                            html_parts.append('<div class="day-cell empty-cell"></div>')
                        else:
                            profit = daily_profits.get(day, 0)
                            total_month_profit += profit
                            cell_class = "day-cell"
                            profit_text = ""
                            profit_class = ""
                            
                            if day in daily_profits:
                                if profit > 0:
                                    # Light mode'da farklı sınıf kullan ki arka plan düzgün görünsün
                                    cell_class += " day-win" if st.session_state.theme == "Dark" else " day-win-light day-win"
                                    profit_class = "win-text"
                                    profit_text = f"+{profit:.2f}R"
                                elif profit < 0:
                                    cell_class += " day-loss"
                                    profit_class = "loss-text"
                                    profit_text = f"{profit:.2f}R"
                                else:
                                    profit_text = "0.00R"
                            
                            html_parts.append(f'<div class="{cell_class}"><div class="day-number">{day}</div><div class="day-profit {profit_class}">{profit_text}</div></div>')
                
                html_parts.append('</div>')
                st.markdown("".join(html_parts), unsafe_allow_html=True)
                
                color_total = accent_color if total_month_profit > 0 else '#ff4b4b'
                st.markdown(f"<div style='text-align:center; margin-top:15px; font-size:1.2rem; font-weight:bold; color:{color_total}'>{t('total_monthly')}: {total_month_profit:.2f}R</div>", unsafe_allow_html=True)
            else:
                st.info("No Data")
        except Exception as e:
            st.error(f"Error: {e}")

        st.markdown("---")
        st.subheader(t("market_intel"))
        mi1, mi2 = st.columns(2)
        with mi1:
            st.markdown("##### TECHNICAL GAUGE (BTC/USDT)")
            components.html(f"""
            <div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{{"interval": "4h", "width": "100%", "isTransparent": true, "height": "400", "symbol": "BINANCE:BTCUSDT", "showIntervalTabs": true, "displayMode": "single", "locale": "en", "colorTheme": "{widget_theme}"}}</script></div>
            """, height=400)
        with mi2:
            st.markdown("##### ECONOMIC CALENDAR")
            components.html(f"""
            <div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>{{"colorTheme": "{widget_theme}", "isTransparent": true, "width": "100%", "height": "400", "locale": "en", "importanceFilter": "-1,0,1", "currencyFilter": "USD"}}</script></div>
            """, height=400)

        # ROI ve Tablo
        st.markdown("---")
        st.subheader(t("roi_sim"))
        st.markdown(t("roi_desc"))
        roi_c1, roi_c2, roi_c3 = st.columns([1,1,2])
        with roi_c1:
            user_capital = st.number_input(t("initial_cap"), min_value=100, value=1000, step=100)
        with roi_c2:
            user_risk = st.slider(t("risk_trade"), 0.5, 5.0, 2.0, 0.1)
        
        potential_profit = user_capital * (user_risk / 100) * net_r_total
        final_balance = user_capital + potential_profit
        roi_percentage = (potential_profit / user_capital) * 100
        
        with roi_c3:
            st.markdown(f"""
            <div style="background:{card_bg}; padding:15px; border-radius:8px; border:1px solid {accent_color}; text-align:center;">
                <span style="color:{grid_header_color}; font-size:0.9rem;">{t("proj_bal")}</span><br>
                <span style="color:{title_color}; font-size:2.2rem; font-weight:bold;">${final_balance:,.2f}</span><br>
                <span style="color:{accent_color}; font-weight:bold;">(+${potential_profit:,.2f} / +%{roi_percentage:.1f})</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")
        
        col_table_head, col_download = st.columns([4, 1])
        with col_table_head:
            st.markdown(f"##### {t('trade_log')}")
        with col_download:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(label=t("download"), data=csv, file_name=f'crazytown_log_{datetime.now().strftime("%Y%m%d")}.csv', mime='text/csv', key='download-csv')

        # TABLO STİLİ (Açık modda yazıların görünmesini sağlar)
        def style_df(row):
            color = accent_color if row['Sonuç'] == 'WIN' else '#ff4b4b'
            # Yazı rengini tema değişkenine bağladık
            text_c = text_color 
            return [f'color: {color}; font-weight: 600' if col == 'Sonuç' else f'color: {text_c}' for col in row.index]
        
        st.dataframe(df.style.apply(style_df, axis=1), use_container_width=True, hide_index=True)

# ==========================================
# TAB 2: ACADEMY
# ==========================================
with tab2:
    st.write("")
    st.markdown(f"<h2 style='text-align: center; color: {accent_color};'>{t('acad_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"""<div style="text-align: center; font-style: italic; color: {grid_header_color}; margin-bottom: 20px;">"{t('acad_quote')}"</div>""", unsafe_allow_html=True)

    with st.expander(t('lesson_1'), expanded=True):
        st.markdown("""
        ### 1. TIME FILTER
        * **LONDON:** `10:00 – 12:00` (UTC+3)
        * **NEW YORK:** `15:30 – 18:30` (UTC+3)
        
        ### 2. DAILY CONTEXT
        * **PDH:** Break → Search **SHORT**.
        * **PDL:** Break → Search **LONG**.
        """)

    with st.expander(t('lesson_2')):
        st.markdown("""
        ### 1. FIBONACCI
        * **ENTRY:** `0.75` - `0.60`
        * **STOP:** `1`
        """)

    with st.expander(t('lesson_3')):
        st.markdown(f"""
        <div class="rule-box">
        <h4>🚨 RULES</h4>
        <ul>
            <li>NO CHOCH.</li>
            <li>No trade outside time windows.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 3 & 4 (SHORTENED FOR BREVITY, LOGIC SAME)
# ==========================================
with tab3:
    st.write("")
    st.markdown(f"""<div class="promo-banner">{t('limited_offer')}</div>""", unsafe_allow_html=True)
    st.subheader(t('feedback'))
    sp1, sp2, sp3 = st.columns(3)
    with sp1: st.markdown(f"""<div class="testimonial-card"><div class="testimonial-text">"Risk management is top tier."</div><div class="testimonial-author">@Crypto***</div></div>""", unsafe_allow_html=True)
    with sp2: st.markdown(f"""<div class="testimonial-card"><div class="testimonial-text">"Transparency sold me."</div><div class="testimonial-author">@Alex***</div></div>""", unsafe_allow_html=True)
    with sp3: st.markdown(f"""<div class="testimonial-card"><div class="testimonial-text">"FVG setups are insane."</div><div class="testimonial-author">@Mehmet***</div></div>""", unsafe_allow_html=True)
    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="pricing-card"><div class="plan-name">{t('plan_starter')}</div><div class="plan-price">$30<span style="font-size:1rem;color:{grid_header_color}">/mo</span></div><div class="feature-list">✓ Telegram Access<br>✓ 15m Elite Setups</div><a href="https://t.me/Orhan1909" target="_blank" class="custom-btn custom-btn-outline">{t('sel_plan')}</a></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="pricing-card" style="border-color: {accent_color};"><div class="plan-name">{t('plan_pro')}</div><div class="plan-price">$75<span style="font-size:1rem;color:{grid_header_color}">/qtr</span></div><div class="feature-list">✓ <b>All Starter Features</b><br>✓ Real-time Signals</div><a href="https://t.me/Orhan1909" target="_blank" class="custom-btn">{t('most_pop')}</a></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="pricing-card"><div class="plan-name">{t('plan_life')}</div><div class="plan-price">$250<span style="font-size:1rem;color:{grid_header_color}">/once</span></div><div class="feature-list">✓ <b>Lifetime Access</b><br>✓ Private Group</div><a href="https://t.me/Orhan1909" target="_blank" class="custom-btn custom-btn-outline">{t('contact_sales')}</a></div>""", unsafe_allow_html=True)

with tab4:
    st.write(""); st.write("")
    c1, c2 = st.columns(2)
    with c1: st.markdown("""### 📨 Telegram\n<a href="https://t.me/Orhan1909" class="custom-btn">OPEN TELEGRAM</a>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""### 📧 Email\n**orhanaliyev02@gmail.com**""")
    st.write(""); st.divider()
    st.subheader(t('faq'))
    with st.expander("Access?"): st.write("Contact via Telegram.")
    with st.expander("Capital Safe?"): st.write("Max 2% risk per trade.")

st.markdown("---")
st.markdown(f"<p style='text-align: center; color: {accent_hover}; font-size: 0.8rem;'>© 2025 Crazytown Capital. All rights reserved.</p>", unsafe_allow_html=True)
