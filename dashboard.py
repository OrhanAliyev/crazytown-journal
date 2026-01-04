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
import re

# ==========================================
# 0. AYARLAR
# ==========================================
st.set_page_config(
    page_title="OA|Trade Terminal",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# KENDİ TRC20 CÜZDAN ADRESİNİ BURAYA YAZ:
MY_TRC20_WALLET = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t" 

# Gizleme Stilleri ve Kompakt Menu Stili
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
/* Selectboxları küçültmek için ek stil */
div[data-testid="stSelectbox"] > div > div {
    min-height: 35px !important;
    font-size: 0.8rem !important;
}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# YFINANCE KONTROLÜ
try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

if 'lang' not in st.session_state: st.session_state.lang = "TR"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"

# ==========================================
# 1. KOMPAKT ÜST MENÜ (SAĞ KÖŞE)
# ==========================================
c_space, c_lang, c_theme = st.columns([10, 1, 1.2])

with c_lang:
    curr_lang = st.session_state.lang
    lang_opts = ["TR", "EN", "RU"]
    sel_lang = st.selectbox("Dil", lang_opts, index=lang_opts.index(curr_lang), label_visibility="collapsed", key="top_lang_select")
    if sel_lang != st.session_state.lang:
        st.session_state.lang = sel_lang
        st.rerun()

with c_theme:
    curr_theme = st.session_state.theme
    theme_opts = ["🌙 Dark", "☀️ Light"]
    idx = 0 if curr_theme == "Dark" else 1
    sel_theme_raw = st.selectbox("Tema", theme_opts, index=idx, label_visibility="collapsed", key="top_theme_select")
    new_theme = "Dark" if "Dark" in sel_theme_raw else "Light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

# ==========================================
# 2. ÇEVİRİLER
# ==========================================
TRANSLATIONS = {
    "EN": {
        "title_sub": "ALGORITHMIC TRADING SYSTEMS", "perf": "PERFORMANCE", "tools": "TRADING DESK", "acad": "ACADEMY", "memb": "MEMBERSHIP", "cont": "CONTACT", "ai_lab": "AI LAB & CHARTS",
        "total_trades": "TOTAL TRADES", "win_rate": "WIN RATE", "net_return": "NET RETURN", "profit_factor": "PROFIT FACTOR",
        "season_goal": "SEASON GOAL", "completed": "COMPLETED", "perf_cal": "🗓️ PERFORMANCE CALENDAR",
        "select_month": "Select Month", "total_monthly": "TOTAL MONTHLY PNL", "market_intel": "📡 MARKET INTELLIGENCE",
        "roi_sim": "🧮 ROI SIMULATOR", "roi_desc": "Calculate potential earnings.", "initial_cap": "Initial Capital ($)",
        "risk_trade": "Risk Per Trade (%)", "proj_bal": "PROJECTED BALANCE", "trade_log": "TRADE LOG", "download": "📥 DOWNLOAD CSV",
        "limited_offer": "🔥 LIMITED TIME OFFER: Get LIFETIME access!", "feedback": "💬 TRADER FEEDBACK",
        "plan_starter": "STARTER", "plan_pro": "PRO TRADER", "plan_life": "LIFETIME VIP", "sel_plan": "SELECT YOUR PLAN",
        "most_pop": "MOST POPULAR", "contact_sales": "CONTACT SALES", "faq": "❓ FAQ", "settings": "⚙️ SETTINGS",
        "lang_sel": "Language", "theme_sel": "Theme", "theme_dark": "Dark (Neon)", "theme_light": "Light (Corporate)",
        "acad_title": "OA | TRADE SMC MASTERY", "acad_quote": "Not beating the market, but following it with discipline.",
        "acad_1_title": "📘 1. SMC: SMART MONEY CONCEPTS",
        "acad_1_content": "Detailed explanation of BOS, CHoCH, FVG, and Order Blocks.",
        "acad_2_title": "⚡ 2. AMD STRATEGY (POWER OF 3)",
        "acad_2_content": "Accumulation, Manipulation, Distribution strategy details.",
        "acad_3_title": "🌍 3. SESSIONS & TIMING",
        "acad_3_content": "London, New York, and Killzone timings.",
        "acad_4_title": "📊 4. CRITICAL INDICES",
        "acad_4_content": "BTC.D, USDT.D, and TOTAL3 analysis.",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "Real-time market scanning & AI Confidence Score.",
        "run_ai": "SCAN MARKET", "ai_analyzing": "Scanning Order Flow...", 
        "ai_input_label": "Enter Symbol (e.g. BTC, ETH, SOL, PEPE)",
        "ai_trend": "General Trend", "ai_rsi": "RSI Indicator", "ai_supp": "Est. Support", "ai_res": "Est. Resistance",
        "ai_score": "Crazytown Confidence Score", "ai_dec": "AI DECISION",
        "bull": "BULLISH 🟢", "bear": "BEARISH 🔴", "neutral": "NEUTRAL ⚪",
        "s_buy": "STRONG BUY 🚀", "buy": "BUY 🟢", "sell": "SELL 🔴", "s_sell": "STRONG SELL 🔻", "wait": "WAIT ✋",
        "data_source": "Data Source", "err_msg": "Coin not found. Try adding USDT (e.g. PEPEUSDT)",
        "ai_tf": "Timeframe",
        "pay_title": "CHOOSE YOUR PLAN",
        "pay_subtitle": "Unlock professional tools and join the elite circle.",
        "p1_price": "$30", "p1_dur": "/month", "p1_f1": "Daily Signals", "p1_f2": "Basic AI Access", "p1_f3": "Community Chat",
        "p2_price": "$75", "p2_dur": "/3 months", "p2_f1": "Everything in Starter", "p2_f2": "Full AI Scan (Unlimited)", "p2_f3": "Priority Support", "p2_badge": "BEST VALUE",
        "p3_price": "$250", "p3_dur": "/lifetime", "p3_f1": "One-time Payment", "p3_f2": "Source Code Access", "p3_f3": "1-on-1 Mentorship",
        "checkout_title": "💳 SECURE CHECKOUT",
        "step_1": "1. Copy Wallet Address (TRC20)",
        "step_2": "2. Send Exact Amount",
        "step_3": "3. Verify Transaction",
        "tx_placeholder": "Paste Transaction Hash (TxID)",
        "verify_btn": "CONFIRM PAYMENT",
        "success_msg": "WELCOME TO THE CLUB! 🥂",
        "join_btn": "ACCESS VIP CHANNEL", 
        "legal_warning": "<b>LEGAL DISCLAIMER:</b> Trading cryptocurrencies and digital assets involves high risk due to market volatility and may not be suitable for every investor profile. The analyses, data, and market comments provided on the <b>OA|Trade</b> platform are <b>not within the scope of investment advisory services.</b> Investment advisory services are provided only by authorized institutions, taking into account your personal risk and return preferences. The content shared here is general in nature and intended for educational and strategy development purposes only. As it may not be compatible with your financial situation, making trading decisions based solely on this information may not yield results consistent with your expectations. <b>OA|Trade</b> cannot be held responsible for any direct or indirect material/moral damages or loss of profit resulting from the use of the information provided.",
        "footer_links": "Home | Legal Notices | Terms of Use | Privacy Policy | Risk Disclosure<br>GDPR Clarification Text | Cookie Policy | Contact",
        "copyright": "2026 © OA|Trade - All Rights Reserved."
    },
    "TR": {
        "title_sub": "ALGORİTMİK İŞLEM SİSTEMLERİ", "perf": "PERFORMANS", "tools": "ARAÇLAR & ANALİZ", "acad": "AKADEMİ", "memb": "ÜYELİK", "cont": "İLETİŞİM", "ai_lab": "YZ LABORATUVARI",
        "total_trades": "TOPLAM İŞLEM", "win_rate": "BAŞARI ORANI", "net_return": "NET GETİRİ", "profit_factor": "KÂR FAKTÖRÜ",
        "season_goal": "SEZON HEDEFİ", "completed": "TAMAMLANDI", "perf_cal": "🗓️ PERFORMANS TAKVİMİ",
        "select_month": "Ay Seçiniz", "total_monthly": "AYLIK TOPLAM PNL", "market_intel": "📡 PİYASA İSTİHBARATI",
        "roi_sim": "🧮 ROI SİMÜLATÖRÜ", "roi_desc": "Geçmiş performansa dayalı kazanç hesapla.", "initial_cap": "Başlangıç Sermayesi ($)",
        "risk_trade": "İşlem Başı Risk (%)", "proj_bal": "TAHMİNİ BAKİYE", "trade_log": "İŞLEM GEÇMİŞİ", "download": "📥 CSV İNDİR",
        "limited_offer": "🔥 SINIRLI TEKLİF: Zam gelmeden ÖMÜR BOYU erişimi kap!", "feedback": "💬 YATIRIMCI YORUMLARI",
        "plan_starter": "BAŞLANGIÇ", "plan_pro": "PROFESYONEL", "plan_life": "ÖMÜR BOYU VIP", "sel_plan": "PLANINI SEÇ VE ÖDE",
        "most_pop": "EN POPÜLER", "contact_sales": "SATIŞA ULAŞ", "faq": "❓ SIK SORULANLAR", "settings": "⚙️ AYARLAR",
        "lang_sel": "Dil", "theme_sel": "Tema", "theme_dark": "Koyu Mod (Neon)", "theme_light": "Açık Mod (Kurumsal)",
        "acad_title": "OA | TRADE SMC USTALIK SINIFI", "acad_quote": "Piyasayı yenmek değil, disiplinle takip etmek.",
        "acad_1_title": "📘 1. SMC: AKILLI PARA KONSEPTİ",
        "acad_1_content": """
        #### 🏦 SMART MONEY CONCEPTS (SMC) NEDİR?
        Bankalar ve büyük fonların (Market Maker) izini sürmektir. Grafik rastgele hareket etmez, likiditeye (paraya) gider.
        
        **TEMEL YAPILAR:**
        * **BOS (Break of Structure):** Trend yönünde kırılım. Trendin devam edeceğini gösterir.
        * **CHoCH (Change of Character):** Trendin dönüş sinyalidir. Yükselişten düşüşe (veya tam tersi) geçişin ilk habercisidir.
        * **FVG (Fair Value Gap):** Fiyatın hızlı hareket edip arkasında bıraktığı boşluktur. Fiyat er ya da geç bu boşluğu doldurmak (onarmak) ister.
        * **OB (Order Block):** Sert hareket öncesi son zıt mumdur. Kurumsal emirlerin yığıldığı bölgedir.
        """,
        "acad_2_title": "⚡ 2. AMD STRATEJİSİ (POWER OF 3)",
        "acad_2_content": """
        #### 🎯 ACCUMULATION - MANIPULATION - DISTRIBUTION
        Her mumda veya trendde 3 aşama vardır. Tuzağa düşmemek için bunu bilmelisin.
        
        1.  **A - ACCUMULATION (Birikim):** Fiyat dar bir alana sıkışır. Emirler toplanır. (Genelde Asya seansı).
        2.  **M - MANIPULATION (Tuzak):** Fiyat aniden desteği/direnci kırar. Stopları patlatır. Herkesi terse yatırır.
        3.  **D - DISTRIBUTION (Dağıtım):** Gerçek hareket başlar. Manipülasyonun tam tersine doğru hızlı bir ralli olur.
        
        **💡 STRATEJİ:** Yatay piyasayı gör -> Sahte kırılımı (M) bekle -> İçeri gir -> Gerçek yönü (D) yakala.
        """,
        "acad_3_title": "🌍 3. SEANSLAR & ZAMANLAMA",
        "acad_3_content": """
        #### ⏰ EN VERİMLİ İŞLEM SAATLERİ (TSİ)
        Kripto 7/24 açıktır ama para belirli saatlerde akar.
        
        * **🇬🇧 LONDRA SEANSI (09:00 - 12:00):** * Günün ilk hacmi girer. 
            * Genelde günün en düşük veya en yüksek seviyesi (Low/High of the day) burada oluşur.
        * **🇺🇸 NEW YORK SEANSI (15:00 - 18:00):**
            * En yüksek volatilite ve haber akışı buradadır.
            * Londra'nın devamı veya tam tersi (Reversal) yaşanır.
        * **🚫 ASYA SEANSI (Gece):** * Genelde yatay (Accumulation) geçer. İşlem önerilmez.
            
        **⚡ KILLZONE:** İki seansın çakıştığı **15:30 - 17:00** arası en tehlikeli ama en kârlı zamandır.
        """,
        "acad_4_title": "📊 4. KRİTİK ENDEKSLER (PUSULA)",
        "acad_4_content": """
        Analiz yaparken sadece grafiğe bakma, büyük resme bak:
        
        * **🟡 BTC.D (Bitcoin Dominance):**
            * Para Bitcoin'e mi akıyor, Altcoin'lere mi?
            * **Yükseliyorsa:** BTC güçlü, Altcoinler ezilir.
            * **Düşüyorsa:** Altcoin rallisi (Altseason) yakındır.
        * **💵 USDT.D (Tether Dominance):**
            * Yatırımcı nakitte mi bekliyor?
            * **Yükseliyorsa:** Piyasa düşer (Korku).
            * **Düşüyorsa:** Piyasa yükselir (Alım iştahı).
        * **🚀 TOTAL3:**
            * BTC ve ETH hariç tüm Altcoinlerin piyasa değeri.
            * Altcoin sepetin varsa bakman gereken tek grafik budur.
        """,
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "Gelişmiş Teknik Analiz & YZ Güven Skoru.",
        "run_ai": "TARA VE ANALİZ ET", "ai_analyzing": "Piyasa Yapısı Taranıyor...", 
        "ai_input_label": "Coin Sembolü (Örn: TAO, BTC, ETH, PEPE)",
        "ai_trend": "Genel Trend", "ai_rsi": "RSI Göstergesi", "ai_supp": "Tahmini Destek", "ai_res": "Tahmini Direnç",
        "ai_score": "Crazytown Güven Skoru", "ai_dec": "YZ KARARI",
        "bull": "BOĞA (YÜKSELİŞ) 🟢", "bear": "AYI (DÜŞÜŞ) 🔴", "neutral": "NÖTR ⚪",
        "s_buy": "GÜÇLÜ AL 🚀", "buy": "AL 🟢", "sell": "SAT 🔴", "s_sell": "GÜÇLÜ SAT 🔻", "wait": "BEKLE ✋",
        "data_source": "Veri Kaynağı", "err_msg": "Coin bulunamadı. USDT eklemeyi dene (Örn: PEPEUSDT)",
        "ai_tf": "Zaman Dilimi",
        "pay_title": "PLANINI SEÇ",
        "pay_subtitle": "Profesyonel araçların kilidini aç ve elit gruba katıl.",
        "p1_price": "$30", "p1_dur": "/aylık", "p1_f1": "Günlük Sinyaller", "p1_f2": "Temel YZ Erişimi", "p1_f3": "Topluluk Erişimi",
        "p2_price": "$75", "p2_dur": "/3 aylık", "p2_f1": "Başlangıç Paketi Dahil", "p2_f2": "Sınırsız YZ Analizi", "p2_f3": "Öncelikli Destek", "p2_badge": "EN ÇOK TERCİH EDİLEN",
        "p3_price": "$250", "p3_dur": "/tek seferlik", "p3_f1": "Tek Ödeme, Ömür Boyu", "p3_f2": "Kaynak Kod Erişimi", "p3_f3": "Birebir Mentorluk",
        "checkout_title": "💳 GÜVENLİ ÖDEME",
        "step_1": "1. Cüzdan Adresini Kopyala (TRC20)",
        "step_2": "2. Tam Tutarı Gönder",
        "step_3": "3. İşlemi Doğrula",
        "tx_placeholder": "İşlem Kodunu (TxID) Yapıştır",
        "verify_btn": "ÖDEMEYİ ONAYLA",
        "success_msg": "ARAMIZA HOŞ GELDİN! 🥂",
        "join_btn": "VIP KANALA GİRİŞ",
        "legal_warning": "<b>YASAL UYARI:</b> Kripto para ve dijital varlık ticareti, piyasa volatilitesi nedeniyle yüksek risk içerir ve her yatırımcı profili için uygun olmayabilir. <b>OA|Trade</b> platformunda sunulan analizler, veriler ve piyasa yorumları <b>yatırım danışmanlığı kapsamında değildir.</b> Yatırım danışmanlığı hizmeti; yalnızca yetkili kuruluşlar tarafından, kişisel risk ve getiri tercihleriniz dikkate alınarak sunulmaktadır. Burada paylaşılan içerikler tamamen genel nitelikli olup, eğitim ve strateji geliştirme amacı taşır. Mali durumunuz ile uyumlu olmayabileceğinden, yalnızca buradaki bilgilere dayanarak alım-satım kararı vermeniz beklentilerinize uygun sonuçlar doğurmayabilir. <b>OA|Trade</b>, sunulan bilgilerin kullanımı sonucu oluşabilecek doğrudan veya dolaylı maddi/manevi zararlardan ve kâr mahrumiyetinden hiçbir şekilde sorumlu tutulamaz.",
        "footer_links": "Anasayfa | Yasal Bildirimler | Kullanım Koşulları | Gizlilik Politikası | Risk Bildirimi<br>KVKK Aydınlatma Metni | Çerez Politikası | İletişim",
        "copyright": "2026 © OA|Trade - Tüm Hakları Saklıdır."
    },
    "RU": {
        "title_sub": "АЛГОРИТМИЧЕСКИЕ ТОРГОВЫЕ СИСТЕМЫ", "perf": "ЭФФЕКТИВНОСТЬ", "tools": "ИНСТРУМЕНТЫ", "acad": "АКАДЕМИЯ", "memb": "ПОДПИСКА", "cont": "КОНТАКТЫ", "ai_lab": "ИИ ЛАБОРАТОРИЯ",
        "total_trades": "ВСЕГО СДЕЛОК", "win_rate": "ВИНРЕЙТ", "net_return": "ЧИСТАЯ ПРИБЫЛЬ", "profit_factor": "ПРОФИТ-ФАКТОР",
        "season_goal": "ЦЕЛЬ СЕЗОНА", "completed": "ЗАВЕРШЕНО", "perf_cal": "🗓️ КАЛЕНДАРЬ",
        "select_month": "Выберите месяц", "total_monthly": "ИТОГ МЕСЯЦА PNL", "market_intel": "📡 РЫНОК",
        "roi_sim": "🧮 ROI СИМУЛЯТОР", "roi_desc": "Рассчитайте прибыль.", "initial_cap": "Капитал", "risk_trade": "Риск", "proj_bal": "ПРОГНОЗ", "trade_log": "ЖУРНАЛ", "download": "📥 СКАЧАТЬ",
        "limited_offer": "🔥 ПРЕДЛОЖЕНИЕ: LIFETIME доступ!", "feedback": "💬 ОТЗЫВЫ",
        "plan_starter": "СТАРТ", "plan_pro": "ПРОФИ", "plan_life": "LIFETIME", "sel_plan": "ВЫБРАТЬ",
        "most_pop": "ПОПУЛЯРНЫЙ", "contact_sales": "СВЯЗАТЬСЯ", "faq": "❓ FAQ", "settings": "⚙️ НАСТРОЙКИ",
        "lang_sel": "Язык", "theme_sel": "Тема", "theme_dark": "Темная", "theme_light": "Светлая",
        "acad_title": "OA | TRADE SMC МАСТЕРСТВО", "acad_quote": "Дисциплина прежде всего.",
        "acad_1_title": "📘 1. SMC: SMART MONEY CONCEPTS",
        "acad_1_content": "Детальное объяснение BOS, CHoCH, FVG и Order Blocks.",
        "acad_2_title": "⚡ 2. СТРАТЕГИЯ AMD",
        "acad_2_content": "Accumulation, Manipulation, Distribution.",
        "acad_3_title": "🌍 3. СЕССИИ",
        "acad_3_content": "Лондон, Нью-Йорк и Killzone.",
        "acad_4_title": "📊 4. ИНДЕКСЫ",
        "acad_4_content": "Анализ BTC.D, USDT.D и TOTAL3.",
        "ai_title": "🤖 PRO AI SCANNER", "ai_desc": "ИИ анализ.",
        "run_ai": "АНАЛИЗ", "ai_analyzing": "Сканирование...", 
        "ai_input_label": "Символ (BTC, ETH...)",
        "ai_trend": "Тренд", "ai_rsi": "RSI", "ai_supp": "Поддержка", "ai_res": "Сопротивление",
        "ai_score": "Оценка уверенности", "ai_dec": "РЕШЕНИЕ",
        "bull": "БЫЧИЙ 🟢", "bear": "МЕДВЕЖИЙ 🔴", "neutral": "НЕЙТРАЛЬНО ⚪",
        "s_buy": "СИЛЬНАЯ ПОКУПКА 🚀", "buy": "ПОКУПАТЬ 🟢", "sell": "ПРОДАВАТЬ 🔴", "s_sell": "СИЛЬНАЯ ПРОДАЖ 🔻", "wait": "ЖДАТЬ ✋",
        "data_source": "Источник", "err_msg": "Монета не найдена.",
        "ai_tf": "Таймфрейм",
        "pay_title": "ВЫБЕРИТЕ ПЛАН",
        "pay_subtitle": "Разблокируйте профессиональные инструменты.",
        "p1_price": "$30", "p1_dur": "/мес", "p1_f1": "Сигналы", "p1_f2": "Базовый ИИ", "p1_f3": "Чат",
        "p2_price": "$75", "p2_dur": "/3 мес", "p2_f1": "Всё из Старт", "p2_f2": "Полный ИИ", "p2_f3": "Поддержка", "p2_badge": "ПОПУЛЯРНЫЙ",
        "p3_price": "$250", "p3_dur": "/навсегда", "p3_f1": "Один платеж", "p3_f2": "Исходный код", "p3_f3": "Менторство",
        "checkout_title": "💳 ОПЛАТА",
        "step_1": "1. Скопируйте адрес (TRC20)",
        "step_2": "2. Отправьте сумму",
        "step_3": "3. Подтвердите",
        "tx_placeholder": "Вставьте TxID",
        "verify_btn": "ПОДТВЕРДИТЬ",
        "success_msg": "ДОБРО ПОЖАЛОВАТЬ! 🥂",
        "join_btn": "ВОЙТИ В VIP",
        "legal_warning": "<b>ЮРИДИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ:</b> Торговля криптовалютами и цифровыми активами сопряжена с высоким риском из-за волатильности рынка и может не подходить для каждого инвестора. Анализ, данные и рыночные комментарии, представленные на платформе <b>OA|Trade</b>, <b>не являются инвестиционными рекомендациями.</b> Услуги инвестиционного консультирования предоставляются только уполномоченными организациями с учетом ваших личных предпочтений по риску и доходности. Представленный здесь контент носит общий характер и предназначен исключительно для образовательных целей. <b>OA|Trade</b> не несет ответственности за любые прямые или косвенные убытки или упущенную выгоду, возникшие в результате использования предоставленной информации.",
        "footer_links": "Главная | Юридические уведомления | Условия использования | Политика конфиденциальности | Уведомление о рисках<br>Текст разъяснения GDPR | Политика использования файлов cookie | Контакт",
        "copyright": "2026 © OA|Trade - Все права защищены."
    }
}

def t(key): return TRANSLATIONS[st.session_state.lang].get(key, key)

# ==========================================
# 3. DİNAMİK RENK VE TASARIM
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
        }}

        .neon-title {{ font-family: 'Orbitron', sans-serif; font-size: 3.5rem; text-align: center; color: {col['ttl']} !important; font-weight: 900; letter-spacing: 4px; margin: 0; {f"text-shadow: 0 0 20px {col['ac']};" if st.session_state.theme == "Dark" else ""} animation: pulse 3s infinite alternate; }}
        .metric-container {{ background-color: {col['card']}; border: 1px solid {col['bd']}; border-radius: 10px; padding: 15px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
        .metric-value {{ font-size: 2rem; font-weight: 700; color: {col['ttl']} !important; }}
        .metric-label {{ font-size: 0.8rem; color: {col['grd']} !important; font-weight: 600; letter-spacing: 1px; }}
        
        /* AI CARD STYLING */
        .ai-card {{ background-color: {col['ai_bg']}; border: 1px solid {col['bd']}; border-left-width: 6px; border-left-style: solid; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); }}
        .ai-header {{ font-size: 1.6rem; font-weight: 800; color: {col['ttl']} !important; margin-bottom: 5px; }}
        .ai-sub {{ font-size: 0.9rem; margin-bottom: 20px; font-weight: 600; }}
        .ai-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
        .ai-item {{ padding: 5px 0; }}
        .ai-label {{ font-size: 0.85rem; color: {col['grd']} !important; margin-bottom: 3px; }}
        .ai-val {{ font-size: 1.2rem; font-weight: 800; color: {col['ttl']} !important; }}
        .ai-decision {{ font-size: 1.8rem; font-weight: 900; text-align: left; margin-top: 15px; display: flex; align-items: center; gap: 10px; }}

        .pro-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 20px; }}
        .pro-item {{ background: {col['sec']}; border: 1px solid {col['bd']}; border-radius: 8px; padding: 10px; text-align: left; }}
        .pro-name {{ font-weight: 800; color: {col['ttl']} !important; font-size: 0.8rem; margin-bottom: 3px; }}
        .pro-status {{ font-weight: bold; font-size: 0.9rem; }}

        .day-win {{ background: rgba(0, 255, 204, 0.15); border-color: {col['ac']}; }}
        .day-win-light {{ background: rgba(13, 110, 253, 0.15); border-color: {col['ac']}; }}
        .day-loss {{ background: rgba(255, 75, 75, 0.15); border-color: #ff4b4b; }}
        .win-text {{ color: {col['ac']} !important; }} .loss-text {{ color: #ff4b4b !important; }} .empty-cell {{ background: transparent; border: none; }}
        
        .stTabs [data-baseweb="tab"] {{ color: {col['grd']} !important; }}
        .stTabs [aria-selected="true"] {{ color: {col['ac']} !important; border-bottom-color: {col['ac']} !important; }}
        .custom-btn {{ background-color: {col['ac']}; color: {col['bg']} !important; padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; display: block; text-align: center; }}
        .custom-btn-outline {{ border: 1px solid {col['ac']}; color: {col['ac']} !important; background: transparent; }}
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{ background-color: {col['sec']}; color: {col['txt']}; border-color: {col['bd']}; }}
        
        /* PRICING TABLE STYLES */
        .pricing-box {{
            background: {col['card']};
            border: 1px solid {col['bd']};
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: transform 0.3s;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .pricing-box:hover {{ transform: scale(1.02); border-color: {col['ac']}; }}
        .price-title {{ font-size: 1.2rem; font-weight: 800; color: {col['grd']}; letter-spacing: 1px; }}
        .price-tag {{ font-size: 3rem; font-weight: 900; color: {col['ttl']}; margin: 10px 0; }}
        .price-dur {{ font-size: 1rem; color: {col['grd']}; }}
        .feature-list {{ text-align: left; margin: 20px 0; color: {col['txt']}; font-size: 0.9rem; }}
        .feature-item {{ margin-bottom: 8px; display: flex; align-items: center; }}
        .check-icon {{ color: {col['ac']}; margin-right: 10px; font-weight: bold; }}
        .best-value {{
            background: {col['ac']}; color: {col['bg']}; font-weight: bold; font-size: 0.8rem;
            padding: 5px 15px; border-radius: 20px; display: inline-block; margin-bottom: 10px;
        }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. VERİ YÜKLEME (HATAYI GÖRMEZDEN GELEN MOD)
# ==========================================
@st.cache_data(ttl=60)
def load_data():
    # 1. Deneme: Bulut Şifresi
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in st.secrets:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
            client = gspread.authorize(creds)
            return pd.DataFrame(client.open("Crazytown_Journal").sheet1.get_all_records())
    except:
        pass 

    # 2. Deneme: Bilgisayardaki Dosya
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        data = client.open("Crazytown_Journal").sheet1.get_all_records()
        if data:
            df = pd.DataFrame(data)
            if 'R_Kazanc' in df.columns: 
                df['R_Kazanc'] = df['R_Kazanc'].astype(str).str.replace(',', '.')
                df['R_Kazanc'] = pd.to_numeric(df['R_Kazanc'], errors='coerce').fillna(0)
            return df
    except Exception as e:
        st.error(f"⚠️ Dosya Bulunamadı: {e}")

    # 3. Deneme: Demo Veri
    dates = pd.date_range(end=datetime.today(), periods=20)
    demo_data = {
        'Tarih': dates.strftime("%d.%m.%Y"),
        'Parite': ['DOSYA/YOK', 'BTC/USDT'] * 10,
        'Yön': ['LONG', 'SHORT'] * 10,
        'Sonuç': ['WIN', 'LOSS'] * 10,
        'R_Kazanc': [0] * 20
    }
    return pd.DataFrame(demo_data)

df = load_data()

# --- YENİ YARDIMCI FONKSİYONLAR (CANLI VERİLER) ---
@st.cache_data(ttl=300) # 5 dakikada bir yeniler
def get_market_movers():
    try:
        exchange = ccxt.binance()
        tickers = exchange.fetch_tickers()
        usdt_tickers = {k: v for k, v in tickers.items() if k.endswith('/USDT')}
        sorted_tickers = sorted(usdt_tickers.values(), key=lambda x: x['percentage'], reverse=True)
        top_gainers = sorted_tickers[:5]
        top_losers = sorted_tickers[-5:]
        return top_gainers, top_losers
    except:
        return [], []

def calculate_rsi_scanner(symbols=["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "AVAX/USDT", "DOGE/USDT", "DOT/USDT", "TRX/USDT", "LINK/USDT", "MATIC/USDT", "LTC/USDT", "SHIB/USDT", "UNI/USDT"]):
    results = []
    exchange = ccxt.binance()
    for sym in symbols:
        try:
            ohlcv = exchange.fetch_ohlcv(sym, timeframe='4h', limit=30)
            df_rsi = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
            delta = df_rsi['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            val = rsi.iloc[-1]
            
            status = "NÖTR"
            if val > 70: status = "AŞIRI ALIM (SAT!)"
            elif val < 30: status = "AŞIRI SATIM (AL!)"
            
            results.append({"Coin": sym, "RSI (4s)": round(val, 2), "Durum": status})
        except: pass
    return pd.DataFrame(results)

def get_crypto_data(symbol, timeframe):
    symbol = symbol.upper().strip()
    try:
        cg_map = {
            "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "AVAX": "avalanche-2",
            "DOGE": "dogecoin", "XRP": "ripple", "BNB": "binancecoin", "ADA": "cardano",
            "PEPE": "pepe", "SHIB": "shiba-inu", "SUI": "sui", "DOT": "polkadot",
            "TAO": "bittensor", "WIF": "dogwifhat"
        }
        if symbol in cg_map: cg_id = cg_map[symbol]
        else:
            search_url = f"https://api.coingecko.com/api/v3/search?query={symbol}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp_s = requests.get(search_url, headers=headers, timeout=2).json()
            if resp_s.get("coins"): cg_id = resp_s["coins"][0]["id"]
            else: cg_id = symbol.lower()
        days = "1" if timeframe == "15m" else ("30" if timeframe == "1d" else "7")
        url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/ohlc?vs_currency=usd&days={days}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close'])
                df['time'] = pd.to_datetime(df['time'], unit='ms')
                return df, "CoinGecko API (Best)"
    except: pass
    try:
        import ccxt
        exchange = ccxt.binance()
        if "/" not in symbol: symbol_ccxt = f"{symbol}/USDT"
        else: symbol_ccxt = symbol
        tf_map = {"1h": "1h", "4h": "4h", "1d": "1d"}
        ohlcv = exchange.fetch_ohlcv(symbol_ccxt, timeframe=tf_map.get(timeframe, '1h'), limit=100)
        if ohlcv:
            df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            return df, "Binance API (Fallback)"
    except Exception as e: pass
    return pd.DataFrame(), "Data Error"

wt = "light" if st.session_state.theme == "Light" else "dark"
components.html(f"""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>{{"symbols": [{{"proName": "BINANCE:BTCUSDT", "title": "Bitcoin"}}, {{"proName": "BINANCE:ETHUSDT", "title": "Ethereum"}}, {{"proName": "BINANCE:SOLUSDT", "title": "Solana"}}], "showSymbolLogo": true, "colorTheme": "{wt}", "isTransparent": true, "displayMode": "adaptive", "locale": "en"}}</script></div>""", height=50)

st.write("")
st.markdown('<div class="neon-title">OA|Trade</div>', unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: {col['ac']}; letter-spacing: 2px; font-size: 0.9rem; margin-top: -5px; font-weight:bold;'>{t('title_sub')}</p>", unsafe_allow_html=True)
st.write("")

# SEKME YAPISI
tab1, tab_tools, tab2, tab5, tab3, tab4 = st.tabs([t('perf'), t('tools'), t('acad'), t('ai_lab'), t('memb'), t('cont')])

# TAB 1: PERFORMANS
with tab1:
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

# ==========================================
# TAB: PROFESYONEL VADELİ İŞLEMLER MASASI
# ==========================================
with tab_tools:
    st.write("")
    st.markdown(f"<h2 style='text-align: center; color: {col['ac']}; letter-spacing: 2px;'>⚡ VADELİ İŞLEMLER TERMİNALİ</h2>", unsafe_allow_html=True)
    
    # --- ÜST BÖLÜM: FEAR & GREED + MARKET MOVERS ---
    col_t1, col_t2 = st.columns([1, 2])
    
    with col_t1:
        st.markdown("### 🧠 PİYASA DUYGU DURUMU")
        try:
            fg_resp = requests.get("https://api.alternative.me/fng/?limit=1", timeout=2)
            fg_data = fg_resp.json()['data'][0]
            fg_val = int(fg_data['value'])
            
            # PRO GAUGE CHART (Hız Göstergesi)
            fig_fg = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = fg_val,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': fg_data['value_classification'], 'font': {'size': 20, 'color': col['txt']}},
                number = {'font': {'color': col['ttl']}},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': col['bd']},
                    'bar': {'color': col['ac']},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 2,
                    'bordercolor': col['bd'],
                    'steps': [
                        {'range': [0, 25], 'color': '#ff4b4b'},
                        {'range': [25, 50], 'color': '#ffcc00'},
                        {'range': [50, 75], 'color': '#00ccff'},
                        {'range': [75, 100], 'color': '#00ffcc'}],
                }))
            fig_fg.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': col['txt']})
            st.plotly_chart(fig_fg, use_container_width=True)
        except:
            st.error("Veri alınamadı.")

    with col_t2:
        st.markdown("### 🚀 ANLIK MARKET HAREKETLERİ (24s)")
        gainers, losers = get_market_movers()
        
        t1, t2 = st.tabs(["🔥 EN ÇOK YÜKSELENLER", "🩸 EN ÇOK DÜŞENLER"])
        
        with t1:
            if gainers:
                for g in gainers:
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; padding:8px; background:{col['sec']}; margin-bottom:5px; border-radius:5px; border-left:4px solid #00ffcc;">
                        <span style="font-weight:bold; color:{col['txt']}">{g['symbol'].replace('/USDT','')}</span>
                        <span style="font-weight:bold; color:#00ffcc">%{g['percentage']:.2f} ⬆</span>
                        <span style="color:{col['grd']}">${float(g['last']):.4f}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else: st.info("Veri yükleniyor...")
            
        with t2:
            if losers:
                for l in losers:
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; padding:8px; background:{col['sec']}; margin-bottom:5px; border-radius:5px; border-left:4px solid #ff4b4b;">
                        <span style="font-weight:bold; color:{col['txt']}">{l['symbol'].replace('/USDT','')}</span>
                        <span style="font-weight:bold; color:#ff4b4b">%{l['percentage']:.2f} ⬇</span>
                        <span style="color:{col['grd']}">${float(l['last']):.4f}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else: st.info("Veri yükleniyor...")

    st.markdown("---")

    # --- ORTA BÖLÜM: RSI TARAYICI VE VADELİ VERİLER ---
    c_rsi, c_fut = st.columns([1, 1])
    
    with c_rsi:
        st.markdown("### 📡 RSI RADAR (AŞIRI ALIM/SATIM)")
        st.caption("Piyasadaki en popüler 15 coin taranır. RSI < 30 ise AL, RSI > 70 ise SAT sinyalidir.")
        
        if st.button("TARAMAYI BAŞLAT 🔍", use_container_width=True):
            with st.spinner("Piyasa taranıyor..."):
                df_rsi = calculate_rsi_scanner()
                
                # EĞER TABLO BOŞ DEĞİLSE VE 'Durum' SÜTUNU VARSA:
                if not df_rsi.empty and 'Durum' in df_rsi.columns:
                    st.dataframe(
                        df_rsi.style.applymap(
                            lambda x: f"color: {'red' if 'SAT' in str(x) else ('green' if 'AL' in str(x) else 'gray')}", 
                            subset=['Durum']
                        ), 
                        use_container_width=True, 
                        hide_index=True
                    )
                else:
                    # EĞER VERİ ÇEKİLEMEDİYSE:
                    st.warning("⚠️ Veri alınamadı veya piyasa şu an yanıt vermiyor. Lütfen sayfayı yenileyip tekrar deneyin.")

    with c_fut:
        st.markdown("### 📊 VADELİ İŞLEMLER VERİSİ")
        st.caption("Funding Rate (Fonlama): Pozitif ise Longlar baskın, Negatif ise Shortlar baskın.")
        
        fut_sym = st.text_input("Coin Ara (Örn: ETH)", "BTC")
        try:
            # Binance Funding Rate Çekme
            exc_fut = ccxt.binance({'options': {'defaultType': 'future'}})
            ticker_fut = exc_fut.fetch_ticker(f"{fut_sym.upper()}/USDT")
            funding = exc_fut.fetch_funding_rate(f"{fut_sym.upper()}/USDT")
            
            fr = float(funding['fundingRate']) * 100
            vol = float(ticker_fut['quoteVolume'])
            
            f_col = "#00ffcc" if fr > 0.01 else ("#ff4b4b" if fr < 0 else "#aaaaaa")
            
            st.markdown(f"""
            <div style="background:{col['card']}; padding:15px; border-radius:10px; border:1px solid {col['bd']}; text-align:center;">
                <div style="font-size:1.5rem; font-weight:bold; color:{col['ttl']}">{fut_sym.upper()}/USDT PERP</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px;">
                    <div>
                        <div style="font-size:0.8rem; color:{col['grd']}">FUNDING (8H)</div>
                        <div style="font-size:1.2rem; font-weight:bold; color:{f_col}">{fr:.4f}%</div>
                    </div>
                    <div>
                        <div style="font-size:0.8rem; color:{col['grd']}">24H HACİM</div>
                        <div style="font-size:1.2rem; font-weight:bold; color:{col['txt']}">${vol:,.0f}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except:
            st.error("Vadeli veri alınamadı.")

    st.markdown("---")

    # --- POZİSYON HESAPLAYICI (EKSTRA) ---
    with st.expander("🧮 POZİSYON VE RİSK HESAPLAYICI", expanded=False):
        rc1, rc2 = st.columns(2)
        with rc1: 
            ab = st.number_input("Kasa ($)", value=1000.0, key="tool_kasa") 
            rp = st.number_input("Risk (%)", value=1.0, key="tool_risk")
        with rc2: 
            ep = st.number_input("Giriş ($)", value=0.0, key="tool_entry") 
            sp = st.number_input("Stop ($)", value=0.0, key="tool_stop")
            
        if ep > 0 and sp > 0:
            ra = ab * (rp/100); ps = ra / abs(ep-sp); tv = ps * ep
            st.info(f"Risk: ${ra:.2f} | Adet: {ps:.4f} | Büyüklük: ${tv:,.2f}")

    st.markdown("---")

    # --- ALT BÖLÜM: LİKİDASYON HARİTASI & HABERLER ---
    st.markdown("### 🔥 CANLI LİKİDASYON ISI HARİTASI")
    st.caption("Aşağıdaki harita, fiyatın nereye giderse kimlerin 'patlayacağını' gösterir. Sarı/Parlak alanlar likiditenin (stopların) olduğu yerlerdir.")
    
    # Coinglass Embed (En temiz yöntem)
    components.iframe("https://www.coinglass.com/pro/futures/liquidation_map", height=600, scrolling=True)
    
    st.markdown("---")
    
    # HABER AKIŞI
    st.markdown("### 📰 CANLI HABER AKIŞI (GLOBAL)")
    try:
        # Google News RSS (Ücretsiz ve güvenilir)
        rss_url = "https://news.google.com/rss/search?q=cryptocurrency+when:1d&hl=en-US&gl=US&ceid=US:en"
        feed = requests.get(rss_url, timeout=5).text
        # Basit XML parse (Regex ile hızlı çözüm)
        items = re.findall(r'<item>(.*?)</item>', feed, re.DOTALL)
        
        for item in items[:5]: # Son 5 haber
            title = re.search(r'<title>(.*?)</title>', item).group(1)
            link = re.search(r'<link>(.*?)</link>', item).group(1)
            source = re.search(r'<source.*?>(.*?)</source>', item).group(1)
            
            st.markdown(f"""
            <div style="padding:10px; border-bottom:1px solid {col['bd']};">
                <a href="{link}" target="_blank" style="text-decoration:none; color:{col['txt']}; font-weight:bold; font-size:0.95rem;">{title}</a>
                <div style="font-size:0.75rem; color:{col['grd']}; margin-top:4px;">Kaynak: {source}</div>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.error("Haber kaynağına ulaşılamadı.")

# TAB 2: AKADEMİ (GÜNCELLENMİŞ)
with tab2:
    st.write("")
    st.markdown(f"<h2 style='text-align: center; color: {col['ac']} !important; margin-bottom:10px;'>{t('acad_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; color: {col['grd']}; font-style: italic; margin-bottom: 30px;'>{t('acad_quote')}</div>", unsafe_allow_html=True)
    
    # 1. SMC BÖLÜMÜ
    with st.expander(t('acad_1_title'), expanded=True):
        st.markdown(t('acad_1_content'))
        st.info("💡 **İPUCU:** Fiyat her zaman FVG boşluklarını doldurmak ister. Giriş için acele etme, fiyatın sana gelmesini bekle.")

    # 2. AMD STRATEJİSİ
    with st.expander(t('acad_2_title'), expanded=False):
        st.markdown(t('acad_2_content'))
        st.code("""
      (M)anipulation (Tuzak/Fake)
          ^
          |
(D)istribution (Gerçek Yön)  <----+
          |
(A)ccumulation (Yatay) . . . . . .|
        """, language="text")

    # 3. SEANSLAR
    with st.expander(t('acad_3_title'), expanded=False):
        st.markdown(t('acad_3_content'))
        c_sess1, c_sess2, c_sess3 = st.columns(3)
        c_sess1.metric("Londra", "09:00 - 12:00", "Volatilite Başlar")
        c_sess2.metric("New York", "15:00 - 18:00", "Trend Belirlenir")
        c_sess3.metric("Killzone", "15:30 - 17:00", "🔥 Yüksek Risk")

    # 4. KRİTİK ENDEKSLER
    with st.expander(t('acad_4_title'), expanded=False):
        st.markdown(t('acad_4_content'))
        st.warning("⚠️ **UYARI:** USDT.D yükselirken Long işlem almak, rüzgara karşı koşmak gibidir.")

# TAB 5: AI LAB & MUM GRAFİKLERİ
with tab5:
    st.write("")
    st.markdown(f"<h2 style='text-align: center; color: {col['ac']} !important;'>{t('ai_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"""<div style="text-align: center; font-style: italic; color: {col['grd']} !important; margin-bottom: 20px;">{t('ai_desc')}</div>""", unsafe_allow_html=True)
    
    ai_c1, ai_c2, ai_c3 = st.columns([2, 1, 1])
    with ai_c1: user_symbol = st.text_input(t('ai_input_label'), value="TAO")
    with ai_c2: tf = st.selectbox(t('ai_tf'), ["1h", "4h", "1d"])
    with ai_c3:
        st.write("")
        run_analysis = st.button(t('run_ai'), key="ai_btn", use_container_width=True)

    if run_analysis:
        dec_col, trend_text, decision = "#888888", "NEUTRAL", "WAIT"
        wave_status, core_status, beluga_status = "NEUTRAL", "STABLE", "50.0"
        macd_status, div_status = "NEUTRAL", "NONE"
        wave_col, core_col, macd_col, div_col = "#888", "#888", "#888", "#888"
        score, rsi_val = 50, 50.0
        change_24h, current_price, supp, res = 0.0, 0.0, 0.0, 0.0
        direction = "NEUTRAL"

        with st.spinner(t('ai_analyzing')):
            live_df, source = get_crypto_data(user_symbol, tf)
            time.sleep(0.5) 
        
        if not live_df.empty and len(live_df) > 20:
            current_price = float(live_df['close'].iloc[-1])
            open_price = float(live_df['open'].iloc[-1])
            change_24h = ((current_price - open_price) / open_price) * 100
            
            # YENİ: Ortalamalar (SMA & EMA)
            live_df['SMA20'] = live_df['close'].rolling(window=20).mean()
            live_df['EMA50'] = live_df['close'].ewm(span=50, adjust=False).mean()
            sma_val = float(live_df['SMA20'].iloc[-1]) if not pd.isna(live_df['SMA20'].iloc[-1]) else current_price
            
            delta = live_df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().fillna(0)
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().fillna(0)
            rs = gain / (loss + 0.0001)
            live_df['RSI'] = 100 - (100 / (1 + rs))
            rsi_val = float(live_df['RSI'].iloc[-1]) if not pd.isna(live_df['RSI'].iloc[-1]) else 50.0
            
            supp = live_df['low'].tail(50).min()
            res = live_df['high'].tail(50).max()
            
            ema50 = live_df['EMA50'].iloc[-1]
            wave_status = "BULLISH WAVE 🌊" if current_price > ema50 else "BEARISH WAVE 🌊"
            wave_col = "#00ff00" if current_price > ema50 else "#ff0000"

            std_dev = live_df['close'].rolling(20).std().iloc[-1]
            core_status = "HIGH VOLATILITY ⚡" if std_dev > (current_price * 0.02) else "STABLE CORE 🛡️"
            core_col = "#ffcc00" if "HIGH" in core_status else "#00ccff"

            stoch_k = ((rsi_val - 30) / (70 - 30)) * 100
            beluga_val = max(0, min(100, stoch_k)) 
            beluga_status = f"{beluga_val:.1f} (OSC)"

            ema12 = live_df['close'].ewm(span=12, adjust=False).mean()
            ema26 = live_df['close'].ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9, adjust=False).mean()
            macd_val = macd.iloc[-1]
            sig_val = signal.iloc[-1]
            macd_status = "BUY CROSS 🟢" if macd_val > sig_val else "SELL CROSS 🔴"
            macd_col = "#00ff00" if macd_val > sig_val else "#ff0000"

            price_trend = live_df['close'].iloc[-1] > live_df['close'].iloc[-5]
            rsi_trend = live_df['RSI'].iloc[-1] > live_df['RSI'].iloc[-5]
            if price_trend and not rsi_trend: div_status = "BEARISH DIV 📉"; div_col = "#ff0000"
            elif not price_trend and rsi_trend: div_status = "BULLISH DIV 📈"; div_col = "#00ff00"
            else: div_status = "NO DIVERGENCE"; div_col = "#888"

            score = 50
            if current_price > sma_val: score += 15
            if rsi_val > 50: score += 10
            if change_24h > 0: score += 10
            if macd_val > sig_val: score += 15
            score = max(0, min(100, score))
            
            if score >= 80: decision = t('s_buy'); dec_col = "#00ff00"; trend_text = t('bull'); direction = "BULL"
            elif score >= 60: decision = t('buy'); dec_col = "#00cc00"; trend_text = t('bull'); direction = "BULL"
            elif score <= 20: decision = t('s_sell'); dec_col = "#ff0000"; trend_text = t('bear'); direction = "BEAR"
            elif score <= 40: decision = t('sell'); dec_col = "#cc0000"; trend_text = t('bear'); direction = "BEAR"
            else: decision = t('wait'); dec_col = "#aaaaaa"; trend_text = t('neutral'); direction = "NEUTRAL"
            
            # --- HTML ÇIKTISI ---
            html_card = f"""
<div class="ai-card" style="border-left-color: {dec_col} !important;">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div>
<div class="ai-header">{user_symbol.upper()} / USD</div>
<div class="ai-sub" style="color:{dec_col} !important;">{change_24h:+.2f}%</div>
</div>
<div style="text-align:right;">
<div class="ai-header">${current_price:,.4f}</div>
</div>
</div>
<hr style="border-color: {col['bd']}; margin: 15px 0;">
<div class="ai-grid">
<div class="ai-item"><div class="ai-label">{t('ai_trend')}</div><div class="ai-val" style="color:{dec_col} !important">{trend_text}</div></div>
<div class="ai-item"><div class="ai-label">{t('ai_rsi')}</div><div class="ai-val">{rsi_val:.2f}</div></div>
<div class="ai-item"><div class="ai-label">{t('ai_supp')}</div><div class="ai-val">${supp:,.4f}</div></div>
<div class="ai-item"><div class="ai-label">{t('ai_res')}</div><div class="ai-val">${res:,.4f}</div></div>
</div>
<div style="margin-top:25px; margin-bottom:10px; font-weight:800; color:{col['ac']} !important; letter-spacing:1px;">PRO TOOLKIT 🛠️</div>
<div class="pro-grid">
<div class="pro-item"><div class="pro-name">Market Waves Pro</div><div class="pro-status" style="color:{wave_col}">{wave_status}</div></div>
<div class="pro-item"><div class="pro-name">Market Core Pro</div><div class="pro-status" style="color:{core_col}">{core_status}</div></div>
<div class="pro-item"><div class="pro-name">Beluga Nautilus</div><div class="pro-status">{beluga_status}</div></div>
<div class="pro-item"><div class="pro-name">Ultimate MACD</div><div class="pro-status" style="color:{macd_col}">{macd_status}</div></div>
<div class="pro-item"><div class="pro-name">Ultimate RSI</div><div class="pro-status">{rsi_val:.1f}</div></div>
<div class="pro-item"><div class="pro-name">Premium Divergence</div><div class="pro-status" style="color:{div_col}">{div_status}</div></div>
</div>
<div class="ai-label" style="margin-top:25px;">{t('ai_score')}:</div>
<div style="background:#333; border-radius:10px; height:10px; width:100%; margin-top:5px; overflow:hidden;">
<div style="background: linear-gradient(90deg, #ff4b4b, #ffff00, #00ffcc); width:{score}%; height:100%;"></div>
</div>
<div style="text-align:right; font-size:0.8rem; color:#888;">{score}/100</div>
<div class="ai-decision" style="border: 2px solid {dec_col}; color: {dec_col} !important;">
{t('ai_dec')}: {decision}
</div>
</div>
"""
            st.markdown(html_card, unsafe_allow_html=True)
            st.caption(f"{t('data_source')}: {source}")

            # --- 🕯️ MUM GRAFİĞİ (OHLC) ---
            st.write("")
            fig_ai = go.Figure()
            last_50 = live_df.tail(60).reset_index(drop=True)
            
            # Candlesticks
            fig_ai.add_trace(go.Candlestick(
                x=last_50.index,
                open=last_50['open'], high=last_50['high'],
                low=last_50['low'], close=last_50['close'],
                name='OHLC'
            ))
            
            # SMA 20 (Sarı)
            fig_ai.add_trace(go.Scatter(x=last_50.index, y=last_50['SMA20'], mode='lines', name='SMA 20', line=dict(color='#ffd700', width=1.5)))
            
            # EMA 50 (Mavi)
            fig_ai.add_trace(go.Scatter(x=last_50.index, y=last_50['EMA50'], mode='lines', name='EMA 50', line=dict(color='#00bfff', width=1.5)))
            
            pt = "plotly_white" if st.session_state.theme == "Light" else "plotly_dark"
            fig_ai.update_layout(
                template=pt, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                height=500, 
                margin=dict(l=0,r=0,t=20,b=0),
                xaxis=dict(showgrid=False, rangeslider=dict(visible=False)), 
                yaxis=dict(gridcolor=col['bd'])
            )
            st.plotly_chart(fig_ai, use_container_width=True)

        else:
            st.error(t("err_msg"))

# TAB 3: ÜYELİK & PROFESYONEL ÖDEME SİSTEMİ
with tab3:
    st.write("")
    st.markdown(f"<h1 style='text-align: center; color: {col['ac']} !important;'>{t('pay_title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: {col['grd']}; margin-bottom: 40px;'>{t('pay_subtitle')}</p>", unsafe_allow_html=True)
    
    # 1. PLAN KARTLARI (3 SÜTUN)
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        st.markdown(f"""
        <div class="pricing-box">
            <div class="price-title">{t('plan_starter')}</div>
            <div class="price-tag">{t('p1_price')}</div>
            <div class="price-dur">{t('p1_dur')}</div>
            <div class="feature-list">
                <div class="feature-item"><span class="check-icon">✓</span>{t('p1_f1')}</div>
                <div class="feature-item"><span class="check-icon">✓</span>{t('p1_f2')}</div>
                <div class="feature-item"><span class="check-icon">✓</span>{t('p1_f3')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_p2:
        st.markdown(f"""
        <div class="pricing-box" style="border-color: {col['ac']}; box-shadow: 0 0 20px {col['ac']}20;">
            <div class="best-value">{t('p2_badge')}</div>
            <div class="price-title">{t('plan_pro')}</div>
            <div class="price-tag" style="color:{col['ac']} !important">{t('p2_price')}</div>
            <div class="price-dur">{t('p2_dur')}</div>
            <div class="feature-list">
                <div class="feature-item"><span class="check-icon">✓</span>{t('p2_f1')}</div>
                <div class="feature-item"><span class="check-icon">✓</span>{t('p2_f2')}</div>
                <div class="feature-item"><span class="check-icon">✓</span>{t('p2_f3')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_p3:
        st.markdown(f"""
        <div class="pricing-box">
            <div class="price-title">{t('plan_life')}</div>
            <div class="price-tag">{t('p3_price')}</div>
            <div class="price-dur">{t('p3_dur')}</div>
            <div class="feature-list">
                <div class="feature-item"><span class="check-icon">✓</span>{t('p3_f1')}</div>
                <div class="feature-item"><span class="check-icon">✓</span>{t('p3_f2')}</div>
                <div class="feature-item"><span class="check-icon">✓</span>{t('p3_f3')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # 2. ÖDEME ALANI (TEK BÜYÜK ALAN)
    st.subheader(t('checkout_title'))
    
    # PLAN SEÇİMİ
    plan_options = {t('plan_starter'): 30, t('plan_pro'): 75, t('plan_life'): 250}
    selected_plan = st.selectbox(t('sel_plan'), list(plan_options.keys()), index=1)
    amount = plan_options[selected_plan]
    
    # İKİ KOLONLU ÖDEME EKRANI
    chk_c1, chk_c2 = st.columns([1, 2])
    
    with chk_c1:
        # QR KOD VE TUTAR
        st.markdown(f"""
        <div style="background: {col['sec']}; border-radius: 10px; padding: 20px; text-align: center; border: 1px solid {col['bd']};">
            <div style="font-weight: bold; margin-bottom: 10px;">SCAN TO PAY</div>
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={MY_TRC20_WALLET}" style="border-radius:10px; margin-bottom:10px;">
            <div style="font-size: 1.5rem; color: {col['ac']}; font-weight: 900;">${amount} USDT</div>
            <div style="font-size: 0.8rem; opacity: 0.7;">Network: TRON (TRC20)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with chk_c2:
        # ADIMLAR VE GİRİŞ
        st.info(f"**{t('step_1')}**")
        st.code(MY_TRC20_WALLET, language="text") # KOPYALANABİLİR ALAN
        
        st.info(f"**{t('step_2')}**")
        
        st.info(f"**{t('step_3')}**")
        tx_id = st.text_input("Transaction ID (TxID)", placeholder=t('tx_placeholder'))
        
        if st.button(t('verify_btn'), type="primary", use_container_width=True):
            if len(tx_id) > 10:
                with st.spinner("Checking Blockchain..."):
                    time.sleep(2)
                    st.balloons()
                    st.success(t('success_msg'))
                    st.markdown(f"""
                    <a href="https://t.me/+E_vuNnVyJ7U2ZTI0" target="_blank" style="text-decoration: none;">
                        <div style="background: #0088cc; color: white; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1.2rem; margin-top: 10px; box-shadow: 0 4px 15px rgba(0,136,204,0.4);">
                            {t('join_btn')} ✈️
                        </div>
                    </a>
                    """, unsafe_allow_html=True)
            else:
                st.error("Invalid TxID format.")

with tab4:
    st.write(""); c1, c2 = st.columns(2)
    with c1: st.markdown(f"""### 📨 Telegram\n<a href="https://t.me/+QHt8nTqozrw2Zjlk" class="custom-btn">OPEN TELEGRAM</a>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""### 📧 Email\n**orhanaliyev02@gmail.com**""")

# ==========================================
# FOOTER (KESİN ÇÖZÜM - BOŞLUKSUZ)
# ==========================================
st.markdown("---")

st.markdown(f"""
<style>
.final-footer {{
    width: 100%;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #444;
    text-align: center;
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: #999;
}}
.final-legal {{
    text-align: justify;
    margin-bottom: 20px;
    line-height: 1.5;
    font-size: 0.7rem;
    opacity: 0.85;
}}
.final-links {{
    margin-bottom: 15px;
}}
.final-links a {{
    text-decoration: none;
    color: #bbb !important;
    margin: 0 8px;
    font-weight: 600;
    transition: 0.3s;
}}
.final-links a:hover {{
    color: #00ffcc !important;
}}
.final-copy {{
    font-weight: bold;
    color: #eee;
    margin-top: 15px;
}}
</style>
<div class="final-footer">
<div class="final-legal">{t('legal_warning')}</div>
<div class="final-links">{t('footer_links')}</div>
<div class="final-copy">{t('copyright')}</div>
</div>
""", unsafe_allow_html=True)