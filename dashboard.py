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
# 1. SAYFA VE STİL YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="Crazytown Capital",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- NÜKLEER GİZLİLİK CSS (FULL STEALTH) ---
st.markdown("""
    <style>
        /* GİZLİLİK PROTOKOLÜ */
        div[class^="viewerBadge_container"], .viewerBadge_container__1QSob {display: none !important;}
        #MainMenu, header, footer, .stDeployButton, [data-testid="stToolbar"] {display: none !important;}
        .stApp > header {display: none !important;}
        .block-container {padding-top: 0rem !important; padding-bottom: 2rem !important;}

        /* GENEL TASARIM */
        .stApp {background-color: #0b0c10; color: #c5c6c7; font-family: 'Inter', sans-serif;}
        
        /* TABS */
        .stTabs [data-baseweb="tab-list"] {gap: 20px; border-bottom: 1px solid #1f2833; padding-top: 10px;}
        .stTabs [data-baseweb="tab"] {height: 50px; color: #888; font-weight: 500; border: none;}
        .stTabs [data-baseweb="tab"]:hover {color: #66fcf1;}
        .stTabs [aria-selected="true"] {color: #66fcf1 !important; border-bottom: 2px solid #66fcf1 !important;}

        /* KARTLAR */
        .metric-container {background-color: #1f2833; border-radius: 8px; padding: 20px; text-align: center; border: 1px solid #2d3845; transition: transform 0.2s ease;}
        .metric-container:hover {transform: translateY(-2px); border-color: #66fcf1;}
        .metric-value {font-size: 2rem; font-weight: 700; color: #fff; margin-bottom: 5px;}
        .metric-label {font-size: 0.8rem; color: #8892b0; text-transform: uppercase; letter-spacing: 1.5px;}

        .pricing-card {background-color: #1f2833; border-radius: 12px; padding: 40px 20px; text-align: center; border: 1px solid #2d3845; height: 100%; transition: all 0.3s ease;}
        .pricing-card:hover {border-color: #66fcf1; transform: translateY(-5px);}
        .plan-name {color: #66fcf1; font-size: 1.1rem; font-weight: 700; letter-spacing: 2px; margin-bottom: 15px;}
        .plan-price {color: #fff; font-size: 2.5rem; font-weight: 700; margin-bottom: 30px;}
        
        .testimonial-card {background-color: #15161a; border-left: 3px solid #66fcf1; padding: 20px; border-radius: 0 8px 8px 0; margin-bottom: 20px;}
        .testimonial-text {font-style: italic; color: #e0e0e0; font-size: 0.95rem;}
        .testimonial-author {margin-top: 10px; color: #66fcf1; font-weight: bold; font-size: 0.85rem;}
        
        /* ACADEMY STYLE */
        .lesson-card {border: 1px solid #2d3845; padding: 20px; border-radius: 8px; margin-bottom: 15px; background: #15161a;}
        .highlight-text {color: #66fcf1; font-weight: bold;}
        .rule-box {background: rgba(102, 252, 241, 0.05); padding: 15px; border-left: 4px solid #66fcf1; margin: 10px 0;}

        .promo-banner {
            background: linear-gradient(90deg, #1f2833 0%, #0b0c10 100%);
            border: 1px solid #66fcf1; color: #fff; padding: 15px; border-radius: 8px;
            text-align: center; margin-bottom: 20px; font-weight: bold;
        }

        .custom-btn {display: inline-block; padding: 12px 30px; color: #0b0c10; background-color: #66fcf1; border-radius: 4px; text-decoration: none; font-weight: 600; width: 100%; text-align: center;}
        .custom-btn:hover {background-color: #45a29e; color: #fff;}
        .custom-btn-outline {background-color: transparent; border: 1px solid #66fcf1; color: #66fcf1;}
        .custom-btn-outline:hover {background-color: #66fcf1; color: #0b0c10;}

        .stDataFrame {border: 1px solid #2d3845;}
        [data-testid="stSidebar"] {display: none;}
        
        /* --- CALENDAR GRID CSS --- */
        .calendar-container {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 10px;
            margin-top: 20px;
        }
        .calendar-header {
            text-align: center;
            font-weight: bold;
            color: #8892b0;
            padding-bottom: 10px;
            border-bottom: 1px solid #2d3845;
        }
        .day-cell {
            background-color: #15161a;
            border: 1px solid #2d3845;
            border-radius: 8px;
            height: 100px;
            padding: 10px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            gap: 5px;
            transition: all 0.2s ease;
        }
        .day-cell:hover {
            border-color: #66fcf1;
            transform: scale(1.02);
            box-shadow: 0 4px 10px rgba(102, 252, 241, 0.1);
        }
        .day-number {
            font-size: 1rem;
            color: #8892b0;
            align-self: flex-start;
            font-weight: bold;
        }
        .day-profit {
            font-size: 1.2rem;
            font-weight: 800;
            align-self: center;
            margin-top: auto;
            margin-bottom: auto;
        }
        .day-win {
            background-color: rgba(102, 252, 241, 0.1);
            border-color: rgba(102, 252, 241, 0.3);
        }
        .day-loss {
            background-color: rgba(255, 75, 75, 0.1);
            border-color: rgba(255, 75, 75, 0.3);
        }
        .win-text {color: #66fcf1;}
        .loss-text {color: #ff4b4b;}
        .empty-cell {
            background-color: transparent;
            border: none;
        }
        
        /* Progress Bar Rengi */
        .stProgress > div > div > div > div {
            background-color: #66fcf1;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VERİ BAĞLANTISI
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
# 3. HEADER & TICKER TAPE
# ==========================================
components.html("""
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {
  "symbols": [{"proName": "BINANCE:BTCUSDT", "title": "Bitcoin"}, {"proName": "BINANCE:ETHUSDT", "title": "Ethereum"}, {"proName": "BINANCE:SOLUSDT", "title": "Solana"}, {"description": "USDT.D", "proName": "CRYPTOCAP:USDT.D"}],
  "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": false, "displayMode": "adaptive", "locale": "en"
}
  </script>
</div>
""", height=50)

st.write("")
st.markdown("<h1 style='text-align: center; font-size: 3rem; color: #FFFFFF;'>CRAZYTOWN CAPITAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #66fcf1; margin-top: -15px; letter-spacing: 2px; font-size: 0.9rem;'>ALGORITHMIC TRADING SYSTEMS</p>", unsafe_allow_html=True)
st.write("")

# TABLAR
tab1, tab2, tab3, tab4 = st.tabs(["PERFORMANCE", "ACADEMY", "MEMBERSHIP", "CONTACT"])

# ==========================================
# TAB 1: PERFORMANCE (DASHBOARD)
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
        
        # Profit Factor Hesaplama
        gross_profit = df[df['R_Kazanc'] > 0]['R_Kazanc'].sum()
        gross_loss = abs(df[df['R_Kazanc'] < 0]['R_Kazanc'].sum())
        pf = (gross_profit / gross_loss) if gross_loss > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f'<div class="metric-container"><div class="metric-value">{total}</div><div class="metric-label">TOTAL TRADES</div></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric-container"><div class="metric-value">{rate:.1f}%</div><div class="metric-label">WIN RATE</div></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="metric-container"><div class="metric-value" style="color:{"#66fcf1" if net_r_total>0 else "#ff4b4b"}">{net_r_total:.2f}R</div><div class="metric-label">NET RETURN</div></div>', unsafe_allow_html=True)
        col4.markdown(f'<div class="metric-container"><div class="metric-value">{pf:.2f}</div><div class="metric-label">PROFIT FACTOR</div></div>', unsafe_allow_html=True)

        # --- HEDEF TAKİPÇİSİ ---
        st.write(""); st.write("")
        target_r = 100.0  # HEDEF BURADAN DEĞİŞTİRİLEBİLİR
        current_progress = min(max(net_r_total / target_r, 0.0), 1.0)
        
        st.markdown(f"""
        <div style="margin-bottom: 5px; color: #8892b0; font-size: 0.8rem; display: flex; justify-content: space-between;">
            <span>SEASON GOAL ({target_r}R)</span>
            <span style="color: #66fcf1;">{int(current_progress*100)}% COMPLETED</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(current_progress)
        st.write("")

        # ANA GRAFİKLER
        g1, g2 = st.columns([2, 1])
        with g1:
            df['Cum'] = df['R_Kazanc'].cumsum()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Tarih'], y=df['Cum'], mode='lines', fill='tozeroy', line=dict(color='#66fcf1', width=2), fillcolor='rgba(102, 252, 241, 0.1)'))
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=300, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1f2833'))
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            fig_pie = px.pie(df, names='Sonuç', values=[1]*len(df), hole=0.7, color='Sonuç', color_discrete_map={'WIN':'#66fcf1', 'LOSS':'#ff4b4b'})
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(l=20, r=20, t=10, b=20), height=300, annotations=[dict(text=f"{rate:.0f}%", x=0.5, y=0.5, font_size=24, showarrow=False, font_color="white")])
            st.plotly_chart(fig_pie, use_container_width=True)

        # ==========================================
        # CUSTOM CSS TAKVİM IZGARASI (HTML Grid)
        # ==========================================
        st.markdown("---")
        st.subheader("🗓️ PERFORMANCE CALENDAR")
        
        try:
            # Tarihleri İşle
            df['Tarih_Dt'] = pd.to_datetime(df['Tarih'], dayfirst=True, errors='coerce')
            df.dropna(subset=['Tarih_Dt'], inplace=True)
            
            if not df.empty:
                df = df.sort_values('Tarih_Dt')
                
                # Ay Seçimi
                available_months = df['Tarih_Dt'].dt.strftime('%Y-%m').unique()
                selected_month_str = st.selectbox("Select Month", options=available_months, index=len(available_months)-1)
                
                # Seçilen aya göre veri filtrele
                selected_year, selected_month_int = map(int, selected_month_str.split('-'))
                monthly_data = df[df['Tarih_Dt'].dt.strftime('%Y-%m') == selected_month_str].copy()
                
                # Günlük verileri grupla: {Gün Sayısı: Toplam R}
                daily_profits = monthly_data.groupby(monthly_data['Tarih_Dt'].dt.day)['R_Kazanc'].sum().to_dict()
                
                # Takvim Matrisi Oluştur
                cal_matrix = calendar.monthcalendar(selected_year, selected_month_int)
                
                # --- HTML OLUŞTURMA ---
                html_cal = '<div class="calendar-container">'
                
                # Header (Paz, Sal, Çar...)
                days_tr = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                for day_name in days_tr:
                    html_cal += f'<div class="calendar-header">{day_name}</div>'
                
                # Günleri Döngüye Al
                total_month_profit = 0
                for week in cal_matrix:
                    for day in week:
                        if day == 0:
                            # Boş Kutu
                            html_cal += '<div class="day-cell empty-cell"></div>'
                        else:
                            # Dolu Gün
                            profit = daily_profits.get(day, 0)
                            total_month_profit += profit
                            
                            # Stil Belirle
                            cell_class = "day-cell"
                            profit_class = ""
                            profit_text = ""
                            
                            if day in daily_profits:
                                if profit > 0:
                                    cell_class += " day-win"
                                    profit_class = "win-text"
                                    profit_text = f"+{profit:.2f}R"
                                elif profit < 0:
                                    cell_class += " day-loss"
                                    profit_class = "loss-text"
                                    profit_text = f"{profit:.2f}R"
                                else:
                                    profit_text = "0.00R"
                            
                            # Kutu HTML'i
                            html_cal += f'''
                            <div class="{cell_class}">
                                <div class="day-number">{day}</div>
                                <div class="day-profit {profit_class}">{profit_text}</div>
                            </div>
                            '''
                
                html_cal += '</div>'
                
                # Ekrana Bas
                st.markdown(html_cal, unsafe_allow_html=True)
                
                # Ay Toplamı Göster
                color_total = '#66fcf1' if total_month_profit > 0 else '#ff4b4b'
                st.markdown(f"<div style='text-align:center; margin-top:15px; font-size:1.2rem; font-weight:bold; color:{color_total}'>TOTAL MONTHLY PNL: {total_month_profit:.2f}R</div>", unsafe_allow_html=True)

            else:
                st.info("Veri bekleniyor...")
                
        except Exception as e:
            st.error(f"Takvim oluşturulurken hata: {e}")


        # --- MARKET INTELLIGENCE ---
        st.markdown("---")
        st.subheader("📡 MARKET INTELLIGENCE")
        mi1, mi2 = st.columns(2)
        with mi1:
            st.markdown("##### TECHNICAL GAUGE (BTC/USDT)")
            components.html("""
            <div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{"interval": "4h", "width": "100%", "isTransparent": true, "height": "400", "symbol": "BINANCE:BTCUSDT", "showIntervalTabs": true, "displayMode": "single", "locale": "en", "colorTheme": "dark"}</script></div>
            """, height=400)
        with mi2:
            st.markdown("##### ECONOMIC CALENDAR")
            components.html("""
            <div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>{"colorTheme": "dark", "isTransparent": true, "width": "100%", "height": "400", "locale": "en", "importanceFilter": "-1,0,1", "currencyFilter": "USD"}</script></div>
            """, height=400)

        # --- ROI CALCULATOR ---
        st.markdown("---")
        st.subheader("🧮 ROI SIMULATOR")
        st.markdown("Calculate potential earnings based on historical performance.")
        roi_c1, roi_c2, roi_c3 = st.columns([1,1,2])
        with roi_c1:
            user_capital = st.number_input("Initial Capital ($)", min_value=100, value=1000, step=100)
        with roi_c2:
            user_risk = st.slider("Risk Per Trade (%)", 0.5, 5.0, 2.0, 0.1)
        
        potential_profit = user_capital * (user_risk / 100) * net_r_total
        final_balance = user_capital + potential_profit
        roi_percentage = (potential_profit / user_capital) * 100
        
        with roi_c3:
            st.markdown(f"""
            <div style="background:#1f2833; padding:15px; border-radius:8px; border:1px solid #66fcf1; text-align:center;">
                <span style="color:#888; font-size:0.9rem;">PROJECTED BALANCE</span><br>
                <span style="color:#fff; font-size:2.2rem; font-weight:bold;">${final_balance:,.2f}</span><br>
                <span style="color:#66fcf1; font-weight:bold;">(+${potential_profit:,.2f} / +%{roi_percentage:.1f})</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")
        
        # --- TABLO VE İNDİRME BUTONU ---
        col_table_head, col_download = st.columns([4, 1])
        with col_table_head:
            st.markdown("##### TRADE LOG")
        with col_download:
            # CSV İNDİRME
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 DOWNLOAD CSV",
                data=csv,
                file_name=f'crazytown_log_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                key='download-csv'
            )

        def style_df(row):
            color = '#66fcf1' if row['Sonuç'] == 'WIN' else '#ff4b4b'
            return [f'color: {color}; font-weight: 600' if col == 'Sonuç' else 'color: #c5c6c7' for col in row.index]
        st.dataframe(df.style.apply(style_df, axis=1), use_container_width=True, hide_index=True)

# ==========================================
# TAB 2: ACADEMY (OA | TRADE SMC)
# ==========================================
with tab2:
    st.write("")
    st.markdown("<h2 style='text-align: center; color: #66fcf1;'>OA | TRADE SMC MASTERY</h2>", unsafe_allow_html=True)
    st.markdown("""<div style="text-align: center; font-style: italic; color: #888; margin-bottom: 20px;">"Piyasayı yenmek değil, piyasanın yaptığı şeyi disiplinle takip etmek." [cite: 88, 89]</div>""", unsafe_allow_html=True)

    with st.expander("📌 BÖLÜM 1: ZAMAN VE BAĞLAM (TEMEL KURALLAR)", expanded=True):
        st.markdown("""
        ### 1. ZAMAN FİLTRESİ (Time Filter) [cite: 7, 16]
        Sadece bu saatlerde ekran başında olunur. Diğer saatlerde grafik analiz edilmez[cite: 16].
        * **LONDON SESSION:** `10:00 – 12:00` (TSİ) [cite: 16, 166]
        * **NEW YORK SESSION:** `15:30 – 18:30` (TSİ) [cite: 16, 167]
        
        ### 2. GÜNLÜK BAĞLAM (Daily Context) [cite: 21, 131]
        İşlem aramak için tek bir şart vardır: **LİKİDİTE ALIMI.** [cite: 132]
        * **PDH (Previous Day High):** Önceki günün en yükseği ihlal edilirse → Sadece **SHORT** aranır[cite: 138, 155].
        * **PDL (Previous Day Low):** Önceki günün en düşüğü ihlal edilirse → Sadece **LONG** aranır[cite: 138, 156].
        
        > **Not:** Kapanış (Close) şart değildir, fitil (Wick) atması yeterlidir[cite: 144, 145].
        """)

    with st.expander("🛠️ BÖLÜM 2: GİRİŞ STRATEJİSİ (SETUP)"):
        st.markdown("""
        ### 1. FIBONACCI AYARLARI [cite: 55]
        Bağlam oluştuğunda (Örn: PDH ihlali), oluşan sert harekete (Impulse) Fibonacci çekilir[cite: 55, 197].
        * **ENTRY BÖLGESİ:** `0.75` ile `0.60` arası [cite: 55, 219]
        * **STOP:** `1` (Impulse başlangıcı) [cite: 78, 220]
        * **TP-1:** `0.25` [cite: 78, 222]
        * **TP-2:** `-0.18` [cite: 78, 224]
        
        ### 2. FVG (Fair Value Gap) REJECTION [cite: 228]
        Her `0.6-0.75` bölgesine gelen fiyata girilmez.
        * O bölgede bir **FVG (Dengesizlik)** olmalı[cite: 242].
        * Fiyat FVG'ye dokunup **red yemeli** (küçük mumlar, fitiller)[cite: 55, 246, 247].
        """)

    with st.expander("⚠️ BÖLÜM 3: UYGULAMA VE YASAKLAR (ÖNEMLİ)"):
        st.markdown("""
        <div class="rule-box">
        <h4>🚨 ASLA YAPILMAYACAKLAR</h4>
        <ul>
            <li><b>CHOCH (Karakter Değişimi) ARANMAZ!</b> Bizi oyundan erken atar veya geç sokar[cite: 255, 260].</li>
            <li>Zaman filtresi dışında işlem alınmaz[cite: 16].</li>
            <li>PDH/PDL ihlali olmadan Fibonacci çekilmez[cite: 197].</li>
        </ul>
        </div>

        ### POZİSYON YÖNETİMİ
        1.  Emri `0.75 - 0.60` arasına at.
        2.  Stop `1` seviyesine koy.
        3.  Fiyat `TP-1 (0.25)` geldiğinde **Stop'u Girişe (BE) Çek**[cite: 226, 339].
        4.  `TP-2 (-0.18)` gelene kadar dokunma[cite: 344].
        """, unsafe_allow_html=True)
        
    st.info("Bu sistem bir tahmin aracı değil, bir davranış modelidir. 30 gün boyunca kuralları esnetmeden uygulayın[cite: 358, 467].")

# ==========================================
# TAB 3: MEMBERSHIP
# ==========================================
with tab3:
    st.write("")
    st.markdown("""<div class="promo-banner">🔥 LIMITED TIME OFFER: Get the LIFETIME access before prices increase on Monday!</div>""", unsafe_allow_html=True)
    
    # SOCIAL PROOF
    st.subheader("💬 TRADER FEEDBACK")
    sp1, sp2, sp3 = st.columns(3)
    with sp1: st.markdown("""<div class="testimonial-card"><div class="testimonial-text">"I've tried many signal groups, but the risk management here is top tier."</div><div class="testimonial-author">@Crypto*** (VIP Member)</div></div>""", unsafe_allow_html=True)
    with sp2: st.markdown("""<div class="testimonial-card"><div class="testimonial-text">"The dashboard transparency sold me. ROI calculator was spot on."</div><div class="testimonial-author">@Alex*** (Pro Trader)</div></div>""", unsafe_allow_html=True)
    with sp3: st.markdown("""<div class="testimonial-card"><div class="testimonial-text">"Started with Starter plan, upgraded to Lifetime. FVG setups are insane."</div><div class="testimonial-author">@Mehmet*** (VIP Member)</div></div>""", unsafe_allow_html=True)
    st.write("")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="pricing-card"><div class="plan-name">STARTER</div><div class="plan-price">$30<span style="font-size:1rem;color:#888">/mo</span></div><div class="feature-list">✓ Telegram Access<br>✓ 15m Elite Setups<br>✓ FVG & Fib Targets<br>✓ Support 24/7</div><a href="https://t.me/Orhan1909" target="_blank" class="custom-btn custom-btn-outline">SELECT PLAN</a></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="pricing-card" style="border-color: #66fcf1;"><div class="plan-name">PROFESSIONAL</div><div class="plan-price">$75<span style="font-size:1rem;color:#888">/qtr</span></div><div class="feature-list">✓ <b>All Starter Features</b><br>✓ Real-time Signals<br>✓ Market Direction (USDT.D)<br>✓ Priority Support</div><a href="https://t.me/Orhan1909" target="_blank" class="custom-btn">MOST POPULAR</a></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="pricing-card"><div class="plan-name">LIFETIME</div><div class="plan-price">$250<span style="font-size:1rem;color:#888">/once</span></div><div class="feature-list">✓ <b>Lifetime Access</b><br>✓ Future Updates Included<br>✓ Bot Setup Assistance<br>✓ Private Group</div><a href="https://t.me/Orhan1909" target="_blank" class="custom-btn custom-btn-outline">CONTACT SALES</a></div>""", unsafe_allow_html=True)

# ==========================================
# TAB 4: CONTACT & FAQ
# ==========================================
with tab4:
    st.write(""); st.write("")
    c1, c2 = st.columns(2)
    with c1: st.markdown("""### 📨 Telegram Support\nFor instant assistance:\n<a href="https://t.me/Orhan1909" class="custom-btn">OPEN TELEGRAM</a>""", unsafe_allow_html=True)
    with c2: st.markdown("""### 📧 Email\nFor business partnerships:\n**orhanaliyev02@gmail.com**""")
    
    st.write(""); st.divider()
    st.subheader("❓ FAQ")
    with st.expander("How do I get access?"): st.write("Contact us on Telegram after USDT (TRC20) payment.")
    with st.expander("Is my capital safe?"): st.write("We use strict risk management (max 2% risk per trade).")
    with st.expander("Can I cancel?"): st.write("Yes, subscriptions are non-binding.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #45a29e; font-size: 0.8rem;'>© 2025 Crazytown Capital. All rights reserved.</p>", unsafe_allow_html=True)
