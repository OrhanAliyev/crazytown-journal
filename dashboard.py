import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import calendar
import numpy as np
import time
import requests
import ccxt

# ==========================================
# 0. AYARLAR (EN BAŞTA OLMALI)
# ==========================================
st.set_page_config(
    page_title="Crazytown Capital",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SESSION STATE BAŞLATMA (Hata almamak için)
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
    "TR": {
        "title_sub": "ALGORİTMİK İŞLEM SİSTEMLERİ", "perf": "PERFORMANS", "acad": "AKADEMİ", "memb": "ÜYELİK", "cont": "İLETİŞİM", "ai_lab": "YAPAY ZEKA",
        "total_trades": "TOPLAM İŞLEM", "win_rate": "BAŞARI ORANI", "net_return": "NET GETİRİ", "profit_factor": "KÂR FAKTÖRÜ",
        "season_goal": "SEZON HEDEFİ", "completed": "TAMAMLANDI", "perf_cal": "🗓️ PERFORMANS TAKVİMİ",
        "select_month": "Ay Seçiniz", "total_monthly": "AYLIK TOPLAM PNL",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "Gerekçeli Yapay Zeka Analizi ve Canlı Piyasa Taraması.",
        "run_ai": "TARA VE ANALİZ ET", "ai_analyzing": "Piyasa Yapısı ve Emirler Taranıyor...", 
        "ai_input_label": "Coin Sembolü Girin (Örn: TAO, BTC, ETH)",
        "ai_trend": "Genel Trend", "ai_rsi": "RSI Momentum", "ai_supp": "Destek", "ai_res": "Direnç",
        "ai_score": "Güven Skoru", "ai_dec": "YZ KARARI", "ai_exp_title": "📝 ANALİZ MANTIĞI & NEDENLER",
        "bull": "BOĞA (YÜKSELİŞ) 🟢", "bear": "AYI (DÜŞÜŞ) 🔴", "neutral": "NÖTR ⚪",
        "s_buy": "GÜÇLÜ AL 🚀", "buy": "AL 🟢", "sell": "SAT 🔴", "s_sell": "GÜÇLÜ SAT 🔻", "wait": "BEKLE ✋",
        "cal_sys": "SİSTEM VERİLERİ", "cal_per": "KİŞİSEL GÜNLÜĞÜM", "add_trade": "➕ Yeni İşlem Ekle",
        "legal_head": "YASAL UYARI, SORUMLULUK BEYANI VE KVKK AYDINLATMA METNİ",
        "accept_terms": "Yukarıdaki yasal uyarı metnini, risk bildirimini ve KVKK aydınlatma metnini okudum, anladım ve kabul ediyorum.",
        "memb_title": "PLANINI SEÇ", "m_1": "BAŞLANGIÇ", "m_2": "PROFESYONEL", "m_3": "VIP (ÖMÜR BOYU)",
        "err_msg": "Coin bulunamadı. Lütfen sembolü kontrol edin."
    },
    "EN": {
        "title_sub": "ALGORITHMIC TRADING SYSTEMS", "perf": "PERFORMANCE", "acad": "ACADEMY", "memb": "MEMBERSHIP", "cont": "CONTACT", "ai_lab": "AI LAB",
        "total_trades": "TOTAL TRADES", "win_rate": "WIN RATE", "net_return": "NET RETURN", "profit_factor": "PROFIT FACTOR",
        "season_goal": "SEASON GOAL", "completed": "COMPLETED", "perf_cal": "🗓️ PERFORMANCE CALENDAR",
        "select_month": "Select Month", "total_monthly": "TOTAL MONTHLY PNL",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "Real-time analysis with explainable logic.",
        "run_ai": "SCAN MARKET", "ai_analyzing": "Analyzing Market Structure...", 
        "ai_input_label": "Enter Symbol (e.g. BTC, ETH)",
        "ai_trend": "Trend", "ai_rsi": "RSI", "ai_supp": "Support", "ai_res": "Resistance",
        "ai_score": "Confidence", "ai_dec": "AI DECISION", "ai_exp_title": "📝 LOGIC & EXPLANATION",
        "bull": "BULLISH 🟢", "bear": "BEARISH 🔴", "neutral": "NEUTRAL ⚪",
        "s_buy": "STRONG BUY 🚀", "buy": "BUY 🟢", "sell": "SELL 🔴", "s_sell": "STRONG SELL 🔻", "wait": "WAIT ✋",
        "cal_sys": "SYSTEM DATA", "cal_per": "MY JOURNAL", "add_trade": "➕ Add Trade",
        "legal_head": "LEGAL DISCLAIMER & RISK WARNING",
        "accept_terms": "I have read and accept the terms and conditions.",
        "memb_title": "CHOOSE PLAN", "m_1": "STARTER", "m_2": "PRO", "m_3": "LIFETIME",
        "err_msg": "Coin not found."
    },
    "RU": {
        "title_sub": "АЛГОРИТМИЧЕСКИЕ ТОРГОВЫЕ СИСТЕМЫ", "perf": "ЭФФЕКТИВНОСТЬ", "acad": "АКАДЕМИЯ", "memb": "ПОДПИСКА", "cont": "КОНТАКТЫ", "ai_lab": "ИИ ЛАБОРАТОРИЯ",
        "total_trades": "ВСЕГО СДЕЛОК", "win_rate": "ВИНРЕЙТ", "net_return": "ЧИСТАЯ ПРИБЫЛЬ", "profit_factor": "ПРОФИТ-ФАКТОР",
        "season_goal": "ЦЕЛЬ СЕЗОНА", "completed": "ЗАВЕРШЕНО", "perf_cal": "🗓️ КАЛЕНДАРЬ",
        "select_month": "Выберите месяц", "total_monthly": "ИТОГ МЕСЯЦА PNL",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "ИИ анализ с объяснением.",
        "run_ai": "АНАЛИЗ", "ai_analyzing": "Сканирование...", 
        "ai_input_label": "Символ (BTC, ETH...)",
        "ai_trend": "Тренд", "ai_rsi": "RSI", "ai_supp": "Поддержка", "ai_res": "Сопротивление",
        "ai_score": "Оценка", "ai_dec": "РЕШЕНИЕ", "ai_exp_title": "📝 ОБЪЯСНЕНИЕ",
        "bull": "БЫЧИЙ 🟢", "bear": "МЕДВЕЖИЙ 🔴", "neutral": "НЕЙТРАЛЬНО ⚪",
        "s_buy": "СИЛЬНАЯ ПОКУПКА 🚀", "buy": "ПОКУПАТЬ 🟢", "sell": "ПРОДАВАТЬ 🔴", "s_sell": "СИЛЬНАЯ ПРОДАЖА 🔻", "wait": "ЖДАТЬ ✋",
        "cal_sys": "СИСТЕМА", "cal_per": "МОЙ ЖУРНАЛ", "add_trade": "➕ Добавить",
        "legal_head": "ЮРИДИЧЕСКИЙ ОТКАЗ",
        "accept_terms": "Я принимаю условия.",
        "memb_title": "ВЫБЕРИТЕ ПЛАН", "m_1": "СТАРТ", "m_2": "ПРОФИ", "m_3": "LIFETIME",
        "err_msg": "Монета не найдена."
    }
}

def t(key): return TRANSLATIONS[st.session_state.lang].get(key, key)

with st.expander(t('settings'), expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        sl = st.selectbox("Language / Dil", ["TR", "EN", "RU"], index=["TR", "EN", "RU"].index(st.session_state.lang))
        if sl != st.session_state.lang: st.session_state.lang = sl; st.rerun()
    with c2:
        thm = st.selectbox("Theme / Tema", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1)
        if thm != st.session_state.theme: st.session_state.theme = thm; st.rerun()

# ==========================================
# 2. CSS TASARIM (RESOLV STYLE & MOBİL)
# ==========================================
if st.session_state.theme == "Dark":
    col = {"bg": "#050505", "txt": "#e0e0e0", "card": "rgba(20, 20, 25, 0.9)", "bd": "#333", "ac": "#00ffcc", "sec": "#111", "ttl": "#ffffff", "grd": "#aaaaaa", "ai_bg": "#0e0e0e"}
    anim = """<style>.orb-container {position:fixed;top:0;left:0;width:100%;height:100%;z-index:-1;background:#050505;} .orb {position:absolute;border-radius:50%;filter:blur(90px);opacity:0.6;animation:moveOrb 20s infinite alternate;} .orb1 {top:10%;left:10%;width:50vw;height:50vw;background:radial-gradient(circle,#00ffcc 0%,transparent 70%);} .orb2 {bottom:10%;right:10%;width:40vw;height:40vw;background:radial-gradient(circle,#9900ff 0%,transparent 70%);} @keyframes moveOrb {0%{transform:scale(1);}100%{transform:scale(1.1);}}</style><div class="orb-container"><div class="orb orb1"></div><div class="orb orb2"></div></div>"""
else:
    col = {"bg": "#f8f9fa", "txt": "#212529", "card": "rgba(255, 255, 255, 0.95)", "bd": "#dee2e6", "ac": "#0d6efd", "sec": "#ffffff", "ttl": "#000000", "grd": "#6c757d", "ai_bg": "#ffffff"}
    anim = """<style>.orb-container {position:fixed;top:0;left:0;width:100%;height:100%;z-index:-1;background:#f8f9fa;} .orb {position:absolute;border-radius:50%;filter:blur(80px);opacity:0.2;animation:moveOrb 25s infinite alternate;} .orb1 {top:-10%;left:-10%;width:60vw;height:60vw;background:radial-gradient(circle,#0d6efd 0%,transparent 60%);} @keyframes moveOrb {0%{transform:scale(1);}100%{transform:scale(1.1);}}</style><div class="orb-container"><div class="orb orb1"></div></div>"""

st.markdown(anim, unsafe_allow_html=True)

st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Inter:wght@400;600;800&display=swap');
        .stApp {{ background: transparent !important; }}
        h1, h2, h3, h4, p, div, span {{ color: {col['txt']} !important; font-family: 'Inter', sans-serif; }}
        
        .neon-title {{ font-family: 'Orbitron', sans-serif; font-size: 3rem; text-align: center; color: {col['ttl']} !important; font-weight: 900; text-shadow: 0 0 20px {col['ac']}; }}
        
        /* KART TASARIMLARI */
        .metric-container {{ background-color: {col['card']}; border: 1px solid {col['bd']}; border-radius: 10px; padding: 15px; text-align: center; }}
        .metric-value {{ font-size: 1.8rem; font-weight: 700; color: {col['ttl']} !important; }}
        .metric-label {{ font-size: 0.8rem; color: {col['grd']} !important; }}
        
        /* AI CARD */
        .ai-card {{ background-color: {col['ai_bg']}; border: 1px solid {col['bd']}; border-left-width: 5px; border-left-style: solid; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .ai-header {{ font-size: 1.5rem; font-weight: 800; color: {col['ttl']} !important; }}
        .ai-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
        .ai-label {{ font-size: 0.8rem; color: {col['grd']} !important; }}
        .ai-val {{ font-size: 1.1rem; font-weight: bold; color: {col['ttl']} !important; }}
        .explanation-box {{ background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin-top: 15px; font-size: 0.9rem; }}
        
        /* TAKVİM */
        .calendar-container {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; margin-top: 10px; }}
        .day-cell {{ background: {col['sec']}; border: 1px solid {col['bd']}; border-radius: 5px; height: 70px; padding: 5px; display: flex; flex-direction: column; justify-content: space-between; }}
        .day-num {{ font-size: 0.8rem; font-weight: bold; opacity: 0.7; }}
        .day-pnl {{ font-size: 0.9rem; font-weight: 800; align-self: center; }}
        .day-win {{ background: rgba(0, 255, 204, 0.15); border-color: {col['ac']}; }}
        .day-loss {{ background: rgba(255, 75, 75, 0.15); border-color: #ff4b4b; }}
        .win-txt {{ color: {col['ac']} !important; }} .loss-txt {{ color: #ff4b4b !important; }}
        
        /* ÜYELİK KARTLARI */
        .memb-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 20px; }}
        .memb-card {{ background: {col['card']}; border: 1px solid {col['bd']}; border-radius: 12px; padding: 25px; text-align: center; transition: 0.3s; }}
        .memb-card:hover {{ transform: translateY(-5px); border-color: {col['ac']}; }}
        .plan-price {{ font-size: 2rem; font-weight: bold; color: {col['ttl']} !important; }}
        
        /* YASAL METİN */
        .legal-box {{ margin-top: 50px; padding: 20px; border-top: 1px solid {col['bd']}; font-size: 0.75rem; color: {col['grd']} !important; text-align: justify; }}
        
        /* MOBİL UYUM */
        @media (max-width: 600px) {{
            .neon-title {{ font-size: 2rem !important; }}
            .ai-grid, .memb-grid {{ grid-template-columns: 1fr !important; }}
            .day-cell {{ height: 50px !important; padding: 2px !important; }}
            .day-num {{ font-size: 0.6rem !important; }}
            .day-pnl {{ font-size: 0.7rem !important; }}
        }}
        
        .custom-btn {{ background: {col['ac']}; color: {col['bg']} !important; padding: 8px 16px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. VERİ FONKSİYONLARI
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
    except: return pd.DataFrame() # Boş döner

def get_market_data(symbol, interval):
    symbol = symbol.upper().strip()
    # 1. CoinGecko
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
    
    # 2. Binance
    try:
        ex = ccxt.binance()
        t = f"{symbol}/USDT"
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
        with st.spinner(t('ai_analyzing')):
            df_ai, src = get_market_data(sym, tf)
            time.sleep(0.5)
        
        if not df_ai.empty and len(df_ai) > 20:
            cur = float(df_ai['close'].iloc[-1])
            sma = float(df_ai['close'].rolling(20).mean().iloc[-1])
            rsi = 100 - (100 / (1 + (df_ai['close'].diff().clip(lower=0).rolling(14).mean().iloc[-1] / abs(df_ai['close'].diff().clip(upper=0).rolling(14).mean().iloc[-1]))))
            
            # --- MANTIK MOTORU ---
            score = 50; reasons = []
            if cur > sma: score += 20; reasons.append("✅ Fiyat > SMA20 (Trend Pozitif)")
            else: score -= 20; reasons.append("⚠️ Fiyat < SMA20 (Trend Negatif)")
            
            if rsi > 55: score += 10; reasons.append(f"✅ RSI {rsi:.1f} > 55 (Momentum Güçlü)")
            elif rsi < 45: score -= 10; reasons.append(f"⚠️ RSI {rsi:.1f} < 45 (Momentum Zayıf)")
            
            score = max(0, min(100, score))
            if score >= 60: dec = t('buy'); dcol = "#00ff00"; tr = t('bull')
            elif score <= 40: dec = t('sell'); dcol = "#ff0000"; tr = t('bear')
            else: dec = t('wait'); dcol = "#aaaaaa"; tr = t('neutral')
            
            expl_html = "".join([f"<li>{r}</li>" for r in reasons])
            
            st.markdown(f"""
            <div class="ai-card" style="border-left-color: {dcol};">
                <div style="display:flex; justify-content:space-between;">
                    <div class="ai-header">{sym.upper()} / USD</div>
                    <div class="ai-header">${cur:,.2f}</div>
                </div>
                <hr style="border-color:{col['bd']}; margin:15px 0;">
                <div class="ai-grid">
                    <div><div class="ai-label">{t('ai_trend')}</div><div class="ai-val" style="color:{dcol}">{tr}</div></div>
                    <div><div class="ai-label">{t('ai_rsi')}</div><div class="ai-val">{rsi:.1f}</div></div>
                </div>
                <div class="ai-decision" style="border: 2px solid {dcol}; color:{dcol};">{t('ai_dec')}: {dec}</div>
                <div class="explanation-box">
                    <div style="font-weight:bold; color:{col['ac']}">{t('ai_exp_title')}</div>
                    <ul>{expl_html}</ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"{t('data_source')}: {src}")
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
    <p><b>1. YASAL UYARI (SPK):</b> Buradaki bilgiler yatırım tavsiyesi değildir. 6362 sayılı SPK Kanunu uyarınca sadece yetkili kurumlar tavsiye verebilir.</p>
    <p><b>2. RİSK BİLDİRİMİ:</b> Kripto paralar yüksek risk içerir. Paranızın tamamını kaybedebilirsiniz.</p>
    <p><b>3. KVKK AYDINLATMA:</b> Verileriniz (6698 sayılı Kanun) sunucuda tutulmaz, sadece tarayıcı önbelleğinde geçici işlenir.</p>
</div>
""", unsafe_allow_html=True)

ack = st.checkbox(t('accept_terms'), value=st.session_state.terms_accepted)
if ack: st.session_state.terms_accepted = True

st.markdown(f"<div style='text-align:center; font-size:0.8rem; margin-top:20px; color:{col['ac_h']}'>© 2025 Crazytown Capital.</div>", unsafe_allow_html=True)
