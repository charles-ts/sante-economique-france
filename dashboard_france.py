import streamlit as st
import pandas as pd
import urllib.request
import json
import ssl
import xml.etree.ElementTree as ET
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf

st.set_page_config(page_title="Charles Tsimi | Santé Économique Française", layout="wide")

st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #F4F6F9 !important; color: #0F172A !important; }
h1, h2, h3, h4, p, span, label, div[data-testid="stMarkdownContainer"] { color: #0F172A !important; }
button[data-baseweb="tab"] p { color: #334155 !important; font-weight: 600 !important; font-size: 0.95rem !important; }
button[data-baseweb="tab"][aria-selected="true"] p { color: #0F2747 !important; font-weight: 800 !important; }
div[data-testid="stMetric"] { background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-top: 3px solid #0F2747 !important; padding: 14px 16px !important; border-radius: 6px !important; box-shadow: 0 2px 5px rgba(15,23,42,0.05) !important; }
div[data-testid="stMetricLabel"] p { color: #475569 !important; font-weight: 700 !important; font-size: 0.85rem !important; }
div[data-testid="stMetricValue"] div { color: #0F172A !important; font-size: 1.4rem !important; font-weight: 800 !important; }
.bio-banner { background: #FFFFFF; border: 1px solid #CBD5E1; border-left: 5px solid #0F2747; padding: 15px 20px; border-radius: 6px; margin-bottom: 18px; }
.bio-role { font-size: 0.98rem; font-weight: 700; color: #0F2747 !important; margin-bottom: 4px; }
.bio-text { font-size: 0.92rem; color: #334155 !important; line-height: 1.5; }
.algo-box { background: #FFFFFF; border: 1px solid #CBD5E1; border-left: 5px solid #B45309; padding: 18px 22px; border-radius: 6px; margin-bottom: 18px; }
.algo-title { font-family: Georgia, serif; font-size: 1.12rem; font-weight: 700; color: #0F2747 !important; margin-bottom: 8px; }
.method-card { background: #FFFFFF; border: 1px solid #CBD5E1; border-left: 4px solid #0F2747; padding: 16px 20px; border-radius: 6px; margin-bottom: 14px; }
.method-title { font-size: 1.02rem; font-weight: 700; color: #0F2747 !important; margin-bottom: 6px; }
.method-body { font-size: 0.94rem; line-height: 1.55; color: #1E293B !important; }
.rating-card { background: #FFFFFF; border: 1px solid #CBD5E1; border-top: 4px solid #0F2747; padding: 18px; border-radius: 8px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("Charles Tsimi — Tableau de bord de la santé économique française")
st.caption("Sources croisées : INSEE · Eurostat · BCE · OCDE · Bercy (AFT) · Banque Mondiale · Yahoo Finance")



# Séries historiques consolidées 2006-2026 (INSEE / Eurostat / BCE / OCDE)
ANNEES = list(range(2006, 2027))
DATA_HIST = pd.DataFrame({
    "Année": ANNEES,
    "PIB_FR": (100.0, 102.4, 102.7, 99.7, 101.6, 103.8, 104.2, 104.8, 105.8, 107.0, 108.1, 110.6, 112.6, 114.7, 106.1, 113.3, 116.2, 117.5, 118.8, 119.6, 120.8),
    "PIB_DE": (100.0, 103.0, 104.0, 98.1, 102.2, 106.2, 106.6, 107.1, 109.5, 111.1, 113.6, 116.6, 117.9, 119.1, 114.2, 118.4, 120.0, 119.6, 119.4, 119.7, 120.9),
    "CROISS_FR": (2.4, 2.4, 0.3, -2.9, 1.9, 2.2, 0.3, 0.6, 1.0, 1.1, 1.1, 2.3, 1.8, 1.9, -7.5, 6.8, 2.6, 1.1, 1.1, 0.7, 1.0),
    "CROISS_EZ": (3.2, 3.0, 0.4, -4.5, 2.1, 1.7, -0.9, -0.2, 1.4, 2.0, 1.9, 2.6, 1.8, 1.6, -6.1, 5.9, 3.4, 0.4, 0.8, 1.1, 1.3),
    "CROISS_US": (2.8, 2.0, 0.1, -2.6, 2.7, 1.6, 2.3, 2.1, 2.5, 2.9, 1.8, 2.5, 3.0, 2.5, -2.2, 6.1, 2.5, 2.9, 2.8, 2.0, 2.1),
    "CHOM_FR": (8.8, 8.0, 7.4, 9.1, 9.3, 9.2, 9.8, 10.3, 10.3, 10.4, 10.1, 9.4, 9.0, 8.4, 8.0, 7.9, 7.3, 7.3, 7.4, 7.5, 7.4),
    "CHOM_DE": (10.3, 8.6, 7.4, 7.7, 7.0, 5.8, 5.4, 5.2, 5.0, 4.6, 4.1, 3.8, 3.4, 3.1, 3.8, 3.6, 3.1, 3.0, 3.4, 3.5, 3.4),
    "DETTE_FR": (64.6, 64.5, 68.8, 83.0, 85.3, 87.8, 90.6, 93.4, 94.9, 95.6, 98.0, 98.1, 97.8, 97.4, 114.6, 112.7, 111.2, 109.9, 113.0, 115.2, 116.5),
    "DETTE_DE": (66.5, 63.7, 65.2, 72.6, 82.4, 79.8, 81.1, 78.7, 75.7, 72.3, 69.3, 65.2, 61.9, 59.6, 68.8, 69.0, 66.1, 63.6, 62.5, 63.2, 63.5),
    "DEF_FR": (-2.4, -2.6, -3.3, -7.2, -6.9, -5.2, -5.0, -4.1, -3.9, -3.6, -3.6, -3.0, -2.3, -2.4, -8.9, -6.6, -4.7, -5.5, -5.8, -5.4, -5.0),
    "DEF_DE": (-1.7, 0.3, -0.1, -3.2, -4.4, -0.9, 0.0, 0.0, 0.6, 1.0, 1.2, 1.3, 1.9, 1.5, -4.3, -3.6, -2.5, -2.6, -2.6, -2.2, -2.0),
    "SPREAD_BPS": (3, 7, 24, 42, 38, 68, 102, 58, 46, 34, 38, 49, 36, 30, 26, 34, 52, 55, 74, 78, 76),
    "OAT_10Y": (3.80, 4.30, 4.23, 3.65, 3.12, 3.32, 2.54, 2.20, 1.67, 0.84, 0.47, 0.81, 0.78, 0.13, -0.15, 0.01, 1.70, 3.00, 2.98, 3.15, 3.10),
    "INF_FR": (1.9, 1.6, 3.2, 0.1, 1.7, 2.3, 2.2, 1.0, 0.6, 0.1, 0.3, 1.2, 2.1, 1.3, 0.5, 2.1, 5.9, 5.7, 2.3, 1.4, 1.6),
    "INF_DE": (1.8, 2.3, 2.8, 0.2, 1.1, 2.5, 2.2, 1.6, 0.8, 0.7, 0.4, 1.7, 1.9, 1.4, 0.4, 3.2, 8.7, 6.0, 2.5, 2.1, 2.0),
    "OCDE_FR": (100.8, 100.5, 98.2, 97.5, 100.4, 99.8, 98.9, 99.3, 99.6, 100.2, 100.5, 101.2, 100.6, 99.9, 96.5, 100.8, 99.5, 99.1, 99.3, 99.5, 99.8),
    "OCDE_DE": (101.2, 101.0, 98.0, 96.8, 101.1, 100.4, 99.1, 99.6, 100.1, 100.4, 100.7, 101.5, 100.8, 99.5, 97.2, 101.1, 99.2, 98.4, 98.6, 99.0, 99.6)
})

@st.cache_data(ttl=900, show_spinner=False)
def fetch_markets():
    data = {}
    for name, sym in (("CAC 40", "^FCHI"), ("DAX 40 (All.)", "^GDAXI")):
        try:
            hist = yf.Ticker(sym).history(period="1y")
            if not hist.empty:
                s = hist["Close"].copy()
                s.index = s.index.tz_localize(None)
                data[name] = s
        except Exception:
            pass
    return pd.DataFrame(data)

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_2027_news(query_str):
    url = f"https://google.com{query_str}&hl=fr&gl=FR&ceid=FR:fr"
    items = []
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
            root = ET.fromstring(resp.read().decode("utf-8"))
            for item in root.findall(".//item"):
                if len(items) < 6:
                    items.append({"title": item.find("title").text, "link": item.find("link").text, "pubDate": item.find("pubDate").text[:16]})
    except Exception:
        pass
    return items

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_rating_news():
    url = "https://google.com"
    items = []
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
            root = ET.fromstring(resp.read().decode("utf-8"))
            for item in root.findall(".//item"):
                if len(items) < 6:
                    items.append({"title": item.find("title").text, "link": item.find("link").text, "pubDate": item.find("pubDate").text[:16]})
    except Exception:
        pass
    return items

tab_macro, tab_notes, tab_methodo, tab_2027, tab_bio = st.tabs([
    "📊 Santé Économique Française (20 ans & Repères)",
    "🏛️ Note des Marchés & Agences",
    "🧭 Méthodologie & Sources",
    "🇫🇷 Présidentielles 2027",
    "👤 Bio / Parcours"
])

with tab_macro:
    df_mkt = fetch_markets()
    last = DATA_HIST.tail(1).squeeze()
    prev = DATA_HIST.tail(2).head(1).squeeze()

    with st.expander("⚡ Paramètres Flash PMI S&P Global & Simulation Conjoncturelle", expanded=False):
        p1, p2, p3, p4 = st.columns([1.2, 1.2, 1.2, 1.4])
        pmi_fr_comp = p1.number_input("France PMI Composite", value=47.8, step=0.1, format="%.1f")
        pmi_fr_manuf = p2.number_input("France PMI Manufacturier", value=46.5, step=0.1, format="%.1f")
        pmi_de_comp = p3.number_input("Allemagne PMI Composite", value=51.2, step=0.1, format="%.1f")
        ecart_pmi = pmi_fr_comp - pmi_de_comp
        p4.metric("Écart PMI FR vs DE", f"{ecart_pmi:+.1f} pts", "Contraction FR (<50)" if pmi_fr_comp < 50 else "Expansion FR (>50)", delta_color="normal" if ecart_pmi >= 0 else "inverse")

    gdp_now, inf_now, debt_now, def_now, unemp_now, sp_now, oat_now = last["CROISS_FR"], last["INF_FR"], last["DETTE_FR"], last["DEF_FR"], last["CHOM_FR"], last["SPREAD_BPS"], last["OAT_10Y"]
    score = 50 + max(-15, min(15, (gdp_now - 1.2) * 8)) + max(-15, min(10, (7.5 - unemp_now) * 4)) + max(-15, min(5, (80 - debt_now) * 0.3)) + max(-15, min(5, (def_now + 3.0) * 4)) + max(-15, min(10, (60 - sp_now) * 0.3)) + max(-10, min(10, (pmi_fr_comp - 50) * 2))
    score = int(max(0, min(100, round(score))))

    croissance_nominale = gdp_now + inf_now
    signaux = []
    if oat_now > croissance_nominale:
        signaux.append(f"🔴 <b>Effet boule de neige actif (BCE / Bercy) :</b> Le taux souverain OAT à 10 ans ({oat_now:.2f} %) dépasse la croissance nominale ({croissance_nominale:.2f} %). La dette s'auto-alimente mécaniquement.")
    else:
        signaux.append(f"🟢 <b>Soutenabilité nominale :</b> La croissance nominale ({croissance_nominale:.2f} %) absorbe encore le coût de financement à 10 ans ({oat_now:.2f} %).")
    if def_now < -3.0 and debt_now > 100.0:
        signaux.append(f"⚠️ <b>Double contrainte budgétaire (Eurostat / Bercy) :</b> Déficit hors clous européens ({def_now:.1f} % vs -3 % max) combiné à une dette élevée ({debt_now:.1f} % du PIB).")
    if "CAC 40" in df_mkt.columns and len(df_mkt["CAC 40"].dropna()) > 20:
        s_cac_tmp = df_mkt["CAC 40"].dropna()
        perf_cac_1y = ((s_cac_tmp.tail(1).squeeze() / s_cac_tmp.head(1).squeeze()) - 1) * 100
        if perf_cac_1y > 2 and pmi_fr_comp < 50:
            signaux.append(f"⚡ <b>Déconnexion Bourse / Économie réelle :</b> Le CAC 40 progresse sur 1 an ({perf_cac_1y:+.1f} %) porté par l'international, alors que l'activité domestique se contracte (PMI à {pmi_fr_comp:.1f}).")
    if ecart_pmi < -2:
        signaux.append(f"📉 <b>Décrochage franco-allemand :</b> Écart d'activité de {ecart_pmi:+.1f} pts de PMI et prime de risque souveraine de {sp_now:.0f} bps face à Berlin.")

    st.markdown(f"""
    <div class="algo-box">
        <div class="algo-title">Synthèse Conjoncturelle & Points de Vigilance — Indice de Santé Économique : {score} / 100</div>
        <div style="font-size:0.95rem;line-height:1.65;color:#1E293B;">{"<br>".join(signaux)}</div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Repères internationaux : la France face à la Zone Euro et aux États-Unis")
    m1, m2, m3 = st.columns(3)
    m1.metric("France — Croissance PIB (INSEE / Eurostat)", f"{gdp_now:+.2f} %", "Référence nationale")
    m2.metric("Zone Euro — Croissance PIB (Eurostat / BCE)", f"{last['CROISS_EZ']:+.2f} %", f"Écart France : {gdp_now - last['CROISS_EZ']:+.2f} pts")
    m3.metric("États-Unis — Croissance PIB (Baromètre mondial)", f"{last['CROISS_US']:+.2f} %", f"Écart France : {gdp_now - last['CROISS_US']:+.2f} pts")
    st.divider()

    st.subheader("Indicateurs clés de la santé économique française")
    k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
    if "CAC 40" in df_mkt.columns and len(df_mkt["CAC 40"].dropna()) >= 2:
        s_cac = df_mkt["CAC 40"].dropna()
        v1, v0 = s_cac.tail(1).squeeze(), s_cac.tail(2).head(1).squeeze()
        k1.metric("1. CAC 40", f"{v1:,.0f}", f"{((v1-v0)/v0)*100:+.2f} %")
    k2.metric("2. Spread FR-DE", f"{sp_now:.0f} bps", f"{sp_now - prev['SPREAD_BPS']:+.0f} bps", delta_color="inverse")
    k3.metric("3. Inflation IPCH", f"{inf_now:.1f} %", f"{inf_now - prev['INF_FR']:+.1f} pts", delta_color="inverse")
    k4.metric("4. PIB (1 an)", f"{gdp_now:+.2f} %", f"{gdp_now - prev['CROISS_FR']:+.2f} pts")
    k5.metric("5. Dette Pub.", f"{debt_now:.1f} %", f"{debt_now - prev['DETTE_FR']:+.1f} pts", delta_color="inverse")
    k6.metric("6. Déficit", f"{def_now:+.1f} %", f"{def_now - prev['DEF_FR']:+.1f} pts")
    k7.metric("7. Chômage", f"{unemp_now:.1f} %", f"{unemp_now - prev['CHOM_FR']:+.1f} pts", delta_color="inverse")
    st.divider()

    st.markdown("## I. Trajectoire Structurelle sur 20 ans (2006–2026)")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("### 1. Évolution du PIB Réel (Base 100 en 2006 : France vs Allemagne)")
        st.caption("Sources : INSEE (Comptes nationaux) · Eurostat · Destatis")
        fig_g = px.line(DATA_HIST, x="Année", y=["PIB_FR", "PIB_DE"], labels={"value": "Base 100 = 2006", "variable": ""})
        fig_g.for_each_trace(lambda t: t.update(name="France" if t.name == "PIB_FR" else "Allemagne", line=dict(width=3, color="#3B82F6" if t.name == "PIB_FR" else "#F59E0B")))
        fig_g.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#0F172A", size=12), xaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), yaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), height=340, legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_g, use_container_width=True)

    with g2:
        st.markdown("### 2. Taux de Chômage Harmonisé sur 20 ans (France vs Allemagne)")
        st.caption("Sources : Eurostat (Séries harmonisées BIT) · INSEE")
        fig_u = px.line(DATA_HIST, x="Année", y=["CHOM_FR", "CHOM_DE"], labels={"value": "% population active", "variable": ""})
        fig_u.for_each_trace(lambda t: t.update(name="France" if t.name == "CHOM_FR" else "Allemagne", line=dict(width=3, color="#3B82F6" if t.name == "CHOM_FR" else "#10B981")))
        fig_u.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#0F172A", size=12), xaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), yaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), height=340, legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_u, use_container_width=True)

    g3, g4 = st.columns(2)
    with g3:
        st.markdown("### 3. Dette Publique Brute sur 20 ans (% du PIB)")
        st.caption("Sources : Eurostat (Notification EDP) · INSEE · Ministère de l’Économie (Bercy)")
        fig_d = px.line(DATA_HIST, x="Année", y=["DETTE_FR", "DETTE_DE"], labels={"value": "% du PIB", "variable": ""})
        fig_d.for_each_trace(lambda t: t.update(name="France" if t.name == "DETTE_FR" else "Allemagne", line=dict(width=3, color="#EF4444" if t.name == "DETTE_FR" else "#10B981")))
        fig_d.add_hline(y=60, line_dash="dash", line_color="gray", annotation_text="Critère Maastricht (60 %)")
        fig_d.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#0F172A", size=12), xaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), yaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), height=340, legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_d, use_container_width=True)

    with g4:
        st.markdown("### 4. Déficit / Solde Public sur 20 ans (% du PIB)")
        st.caption("Sources : Eurostat · INSEE · Bercy (Loi de Finances)")
        fig_s = go.Figure(data=[
            go.Bar(name='France', x=DATA_HIST['Année'], y=DATA_HIST['DEF_FR'], marker_color='#EF4444'),
            go.Bar(name='Allemagne', x=DATA_HIST['Année'], y=DATA_HIST['DEF_DE'], marker_color='#F59E0B')
        ])
        fig_s.add_hline(y=-3.0, line_dash="dash", line_color="#475569", annotation_text="Plafond européen (-3 %)")
        fig_s.update_layout(barmode='group', template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#0F172A", size=12), xaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), yaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), height=340, yaxis_title="% du PIB", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_s, use_container_width=True)

    st.divider()
    st.markdown("## II. Conjoncture & Marchés : BCE, Bourse, OCDE & Inflation")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 5. Prime de Risque Souverain : Spread OAT-Bund 10 ans (bps)")
        st.caption("Sources : Banque Centrale Européenne (BCE) · Agence France Trésor (Bercy)")
        fig_sp = go.Figure()
        fig_sp.add_trace(go.Scatter(x=DATA_HIST["Année"], y=DATA_HIST["SPREAD_BPS"], fill='tozeroy', name="Spread FR - DE (bps)", line=dict(color="#FF4B4B", width=2.8)))
        fig_sp.add_hline(y=50, line_dash="dash", line_color="gray", annotation_text="Zone de calme (~50 bps)")
        fig_sp.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#0F172A", size=12), xaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), yaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), height=320, yaxis_title="Points de base (bps)")
        st.plotly_chart(fig_sp, use_container_width=True)

    with c2:
        st.markdown("#### 6. Bourse : CAC 40 vs DAX 40 (Base 100 sur 1 an)")
        st.caption("Sources : Euronext Paris · Deutsche Börse · Yahoo Finance")
        if "CAC 40" in df_mkt.columns and "DAX 40 (All.)" in df_mkt.columns:
            df_n = df_mkt[["CAC 40", "DAX 40 (All.)"]].dropna()
            if not df_n.empty:
                df_n = (df_n / df_n.head(1).squeeze()) * 100
                fig_m = px.line(df_n, labels={"value": "Base 100", "variable": "", "index": ""})
                fig_m.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#0F172A", size=12), xaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), yaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), height=320, legend=dict(orientation="h", y=1.12))
                st.plotly_chart(fig_m, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### 7. Indicateur Avancé d'Activité OCDE (FR vs DE)")
        st.caption("Source : OCDE (Composite Leading Indicators — CLI)")
        fig_c = px.line(DATA_HIST, x="Année", y=["OCDE_FR", "OCDE_DE"], labels={"value": "Base 100", "variable": ""})
        fig_c.for_each_trace(lambda t: t.update(name="France" if t.name == "OCDE_FR" else "Allemagne", line=dict(width=2.8, color="#3B82F6" if t.name == "OCDE_FR" else "#F59E0B")))
        fig_c.add_hline(y=100, line_dash="dash", line_color="#475569")
        fig_c.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#0F172A", size=12), xaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), yaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), height=320, legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_c, use_container_width=True)

    with c4:
        st.markdown("#### 8. Inflation Harmonisée IPCH (% annuel)")
        st.caption("Sources : Eurostat (IPCH) · INSEE · Banque Centrale Européenne (BCE)")
        fig_i = px.line(DATA_HIST, x="Année", y=["INF_FR", "INF_DE"], labels={"value": "%", "variable": ""})
        fig_i.for_each_trace(lambda t: t.update(name="France" if t.name == "INF_FR" else "Allemagne", line=dict(width=2.8, color="#3B82F6" if t.name == "INF_FR" else "#F59E0B")))
        fig_i.add_hline(y=2.0, line_dash="dash", line_color="#10B981", annotation_text="Cible BCE (2 %)")
        fig_i.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#0F172A", size=12), xaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), yaxis=dict(tickfont=dict(color="#0F172A", size=12), title_font=dict(color="#0F172A"), gridcolor="#E2E8F0"), height=320, legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_i, use_container_width=True)

with tab_notes:
    st.subheader("Évaluation Souveraine de la France par les Agences de Notation")
    st.caption("Revues semestrielles (printemps et automne) · Modifiez les notes ci-dessous après chaque publication officielle.")
    a1, a2, a3, a4 = st.columns(4)
    note_sp = a1.text_input("Standard & Poor's (S&P)", value="AA- (Persp. Négative)")
    note_moodys = a2.text_input("Moody's", value="Aa3 (Persp. Stable)")
    note_fitch = a3.text_input("Fitch Ratings", value="AA- (Persp. Négative)")
    note_scope = a4.text_input("Scope Ratings", value="AA- (Persp. Stable)")

    n1, n2, n3, n4 = st.columns(4)
    n1.markdown(f'<div class="rating-card"><h4>Standard & Poor\'s</h4><h2 style="color:#B45309 !important;">{note_sp}</h2><p style="font-size:0.85rem;color:#475569 !important;">Trajectoire du déficit et crédibilité du redressement budgétaire (Bercy).</p></div>', unsafe_allow_html=True)
    n2.markdown(f'<div class="rating-card"><h4>Moody\'s</h4><h2 style="color:#0F2747 !important;">{note_moodys}</h2><p style="font-size:0.85rem;color:#475569 !important;">Fragmentation politique et soutenabilité de la charge d\'intérêts.</p></div>', unsafe_allow_html=True)
    n3.markdown(f'<div class="rating-card"><h4>Fitch Ratings</h4><h2 style="color:#B45309 !important;">{note_fitch}</h2><p style="font-size:0.85rem;color:#475569 !important;">Ratio dette/PIB supérieur à 110 % et rigidité de la dépense publique.</p></div>', unsafe_allow_html=True)
    n4.markdown(f'<div class="rating-card"><h4>Scope Ratings</h4><h2 style="color:#15803D !important;">{note_scope}</h2><p style="font-size:0.85rem;color:#475569 !important;">Solidité institutionnelle, épargne privée élevée et profondeur du marché OAT.</p></div>', unsafe_allow_html=True)

    st.divider()
    col_synth, col_news = st.columns([1.1, 1.2])
    with col_synth:
        st.markdown("""
        <div class="method-card">
            <div class="method-title">Lecture des salles de marchés & Agence France Trésor (Bercy)</div>
            <div class="method-body">
            • <b>La prime de risque (Spread OAT-Bund / BCE) :</b> Tant que l'écart de taux à 10 ans avec l'Allemagne reste contenu sous 80-85 bps, les adjudications de Bercy demeurent fluides.<br><br>
            • <b>L'effet « boule de neige » :</b> Lorsque le taux d'intérêt moyen de la dette dépasse la croissance nominale du PIB, stabiliser la dette exige un excédent budgétaire primaire.<br><br>
            • <b>Les contre-forces françaises :</b> Diversification économique, démographie plus dynamique qu'en Allemagne et abondance de l'épargne financière des ménages.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_news:
        st.markdown("**Dernières dépêches sur la dette, Bercy et la notation de la France (Flux temps réel) :**")
        news = fetch_rating_news()
        if news:
            for item in news:
                st.markdown(f"• [{item['title']}]({item['link']}) *({item['pubDate']})*")
        else:
            st.info("Flux d'actualités en cours de synchronisation.")

with tab_methodo:
    st.subheader("Grille d'analyse & Sources Institutionnelles (INSEE, Eurostat, BCE, OCDE, Bercy)")
    st.caption("Pourquoi chacun de ces indicateurs est mobilisé pour évaluer la santé économique et budgétaire de la France.")
    items_m = [
        ("0. Principe de lecture croisée (Indice de Santé & Points de Vigilance)", "L'indicateur synthétique affiché en tête du tableau de bord croise simultanément la croissance nominale (INSEE/Eurostat), le coût de la dette à 10 ans (BCE/Bercy — test de l'effet boule de neige), l'écart entre la bourse et l'activité réelle (PMI), ainsi que la position de la France face à la Zone Euro et aux États-Unis."),
        ("1. PIB Réel — Sources : INSEE · Eurostat · Destatis", "Mesure la richesse effectivement produite hors inflation depuis 2006. Le comparer à l'Allemagne, à la Zone Euro et aux États-Unis permet d'identifier les décrochages structurels et la croissance potentielle."),
        ("2. Taux de Chômage Harmonisé — Sources : Eurostat · INSEE · BIT", "Indicateur social et politique majeur. Son évolution sur 20 ans révèle la capacité d'absorption du marché du travail français et son incidence directe sur l'équilibre des comptes sociaux."),
        ("3. Dette Publique Brute au sens de Maastricht — Sources : Eurostat · INSEE · Bercy", "Mesure l'accumulation des déficits passés rapportée au PIB. Au-delà de 110 % du PIB, la sensibilité du budget de l'État à la remontée des taux d'intérêt devient un enjeu stratégique majeur."),
        ("4. Solde / Déficit Public — Sources : Eurostat EDP · Bercy (Loi de Finances)", "Mesure l'écart annuel entre recettes et dépenses publiques. Scrutinisé par la Commission européenne (seuil de -3 %) et les agences de notation."),
        ("5. Spread OAT-Bund à 10 ans — Sources : BCE · Agence France Trésor (Bercy)", "Thermomètre quotidien de la confiance des investisseurs mesurant l'écart de rendement entre l'emprunt d'État français (OAT) et allemand (Bund) à 10 ans."),
        ("6. Indices Boursiers : CAC 40 vs DAX 40 — Sources : Euronext · Deutsche Börse", "Reflètent les anticipations de profits des grands groupes cotés, très exposés à l'international, souvent déconnectées de la conjoncture domestique."),
        ("7. Indicateur Avancé OCDE & PMI Flash — Sources : OCDE · S&P Global", "Permettent d'anticiper les retournements de cycle économique 3 à 6 mois avant la publication officielle des comptes trimestriels de l'INSEE."),
        ("8. Inflation Harmonisée IPCH — Sources : Eurostat · INSEE · BCE", "Détermine le pouvoir d'achat des ménages et dicte la politique monétaire de la Banque Centrale Européenne (cible de 2 %).")
    ]
    for t, b in items_m:
        st.markdown(f'<div class="method-card"><div class="method-title">{t}</div><div class="method-body">{b}</div></div>', unsafe_allow_html=True)




with tab_2027:
    st.subheader("Suivi Électoral & Modélisation Souveraine — Présidentielles 2027")
    st.caption("Dans cet espace, j'agrège les enquêtes d'opinion (intentions de vote brutes, croisées et pondérées) et je modélise la réaction des marchés obligataires (OAT 10 ans) face aux programmes économiques des candidats dépassant 8 %.")

    # --- SOUS-SECTION 1 : SONDAGES (BRUTS, CROISÉS, PONDÉRÉS & ÉVOLUTION) ---
    st.markdown("## 1. Baromètre des Sondages : Intentions de Vote Brutes, Croisées & Pondérées")

    default_polls = pd.DataFrame([
        {"Date": "2026-09-15", "Institut": "Ifop", "N": 1500, "Bardella / Le Pen (RN)": 33.5, "Philippe (Horizons)": 21.0, "Mélenchon (LFI)": 13.5, "Glucksmann (PP/PS)": 12.5, "Attal (Ren.)": 10.5, "Retailleau / Wauquiez (LR)": 8.5},
        {"Date": "2026-10-02", "Institut": "Elabe", "N": 1450, "Bardella / Le Pen (RN)": 32.0, "Philippe (Horizons)": 22.5, "Mélenchon (LFI)": 14.0, "Glucksmann (PP/PS)": 12.0, "Attal (Ren.)": 11.0, "Retailleau / Wauquiez (LR)": 8.5},
        {"Date": "2026-10-20", "Institut": "Ipsos", "N": 1600, "Bardella / Le Pen (RN)": 34.0, "Philippe (Horizons)": 20.5, "Mélenchon (LFI)": 13.0, "Glucksmann (PP/PS)": 13.5, "Attal (Ren.)": 10.0, "Retailleau / Wauquiez (LR)": 9.0},
        {"Date": "2026-11-05", "Institut": "Cluster 17", "N": 1800, "Bardella / Le Pen (RN)": 33.0, "Philippe (Horizons)": 21.5, "Mélenchon (LFI)": 15.0, "Glucksmann (PP/PS)": 12.0, "Attal (Ren.)": 9.5, "Retailleau / Wauquiez (LR)": 9.0},
        {"Date": "2026-11-20", "Institut": "OpinionWay", "N": 1500, "Bardella / Le Pen (RN)": 33.5, "Philippe (Horizons)": 22.0, "Mélenchon (LFI)": 13.5, "Glucksmann (PP/PS)": 12.5, "Attal (Ren.)": 10.0, "Retailleau / Wauquiez (LR)": 8.5}
    ])

    with st.expander("➕ Saisir ou actualiser un nouveau sondage publié (mise à jour immédiate)", expanded=False):
        polls_df = st.data_editor(default_polls, num_rows="dynamic", use_container_width=True)

    candidats_cols = [c for c in polls_df.columns if c not in ("Date", "Institut", "N")]
    polls_sorted = polls_df.sort_values("Date").reset_index(drop=True)

    # Calcul des moyennes brutes (non croisées) et croisées pondérées (échantillon N x fraîcheur)
    recency_weights = [1.0 + 0.25 * i for i in range(len(polls_sorted))]
    total_weights = polls_sorted["N"] * recency_weights
    croise_scores = {c: (polls_sorted[c] * total_weights).sum() / total_weights.sum() for c in candidats_cols}
    brut_scores = {c: polls_sorted[c].mean() for c in candidats_cols}

    df_synth_polls = pd.DataFrame({
        "Candidat / Bloc": candidats_cols,
        "Moyenne Brute Non Croisée (%)": [round(brut_scores[c], 2) for c in candidats_cols],
        "Moyenne Croisée Pondérée (%)": [round(croise_scores[c], 2) for c in candidats_cols],
        "Écart Pondéré vs Brut": [round(croise_scores[c] - brut_scores[c], 2) for c in candidats_cols],
        "Seuil > 8 %": ["✅ Qualifié (> 8 %)" if croise_scores[c] >= 8.0 else "❌ Sous 8 %" for c in candidats_cols]
    }).sort_values("Moyenne Croisée Pondérée (%)", ascending=False)

    col_p1, col_p2 = st.columns([1.1, 1.3])
    with col_p1:
        st.markdown("#### Comparatif : Sondages Non Croisés vs Croisés Pondérés")
        st.caption("La pondération croisée intègre la taille d'échantillon (N) et la fraîcheur de l'enquête.")
        st.dataframe(df_synth_polls, hide_index=True, use_container_width=True)

    with col_p2:
        st.markdown("#### Évolution des candidats dans les sondages jusqu'au scrutin")
        st.caption("Sources : Instituts d'opinion (Ifop, Elabe, Ipsos, Cluster 17, OpinionWay).")
        fig_polls = px.line(polls_sorted, x="Date", y=candidats_cols, markers=True, labels={"value": "Intentions de vote (%)", "variable": ""})
        fig_polls.add_hline(y=8.0, line_dash="dash", line_color="#475569", annotation_text="Seuil d'analyse (8 %)")
        fig_polls.update_traces(line=dict(width=2.8))
        fig_polls.update_layout(
            template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            font=dict(color="#0F172A", size=12), height=350,
            xaxis=dict(tickfont=dict(color="#0F172A"), gridcolor="#E2E8F0"),
            yaxis=dict(tickfont=dict(color="#0F172A"), gridcolor="#E2E8F0"),
            legend=dict(orientation="h", y=1.18)
        )
        st.plotly_chart(fig_polls, use_container_width=True)

    st.divider()

    # --- SOUS-SECTION 2 : MODÉLISATION ÉCONOMÉTRIQUE & ATTITUDE DES MARCHÉS (> 8 %) ---
    st.markdown("## 2. Programmes Économiques (> 8 %) & Conjecture de Réaction des Marchés")
    st.caption("Modélisation quantitative de la dynamique dette/PIB (équation de Domar) et de la prime de risque souverain (Spread OAT-Bund) compte tenu de l'état des finances publiques françaises.")

    with st.expander("📐 Équations du modèle de conjecture obligataire", expanded=False):
        st.markdown("""
        **1. Dynamique d'accumulation de la dette publique (Équation de Domar) :**
        $$\Delta d_t = \frac{r_t - g_t}{1 + g_t} d_{t-1} - sp_t$$
        * $d_t$ : Ratio dette publique / PIB (niveau initial : **115,2 %**).
        * $g_t = g_0 + \mu_D \cdot \Delta D - \mu_T \cdot \Delta T$ : Croissance nominale intégrant les multiplicateurs budgétaires ($\mu_D = 0,85$ sur la dépense publique, $\mu_T = 0,45$ sur les prélèvements).
        * $sp_t$ : Solde primaire corrigé de l'impulsion budgétaire nette du programme (en points de PIB).

        **2. Fonction de réaction des marchés souverains (Spread OAT-Bund en bps) :**
        $$\text{Spread}_i = \text{Spread}_0 + \alpha \cdot \max(0, -\Delta sp_i) + \beta \cdot \Phi_{\text{UE}, i} + \gamma \cdot \max(0, d_{i, 2030} - 115)$$
        """)

    s1, s2 = st.columns(2)
    aversion_marche = s1.slider("Coefficient d'aversion au risque des marchés obligataires (α)", min_value=0.6, max_value=1.8, value=1.0, step=0.1)
    taux_bce_ref = s2.number_input("Taux sans risque allemand de référence — Bund 10 ans (%)", value=2.35, step=0.05, format="%.2f")

    programmes = [
        {"Candidat": "Bardella / Le Pen (RN)", "Choc Dépenses (Mds€/an)": 38.0, "Baisses Impôts (Mds€/an)": 24.0, "Économies / Recettes (Mds€/an)": 17.0, "Friction UE (0-1)": 0.85},
        {"Candidat": "Philippe (Horizons)", "Choc Dépenses (Mds€/an)": 8.0, "Baisses Impôts (Mds€/an)": 12.0, "Économies / Recettes (Mds€/an)": 38.0, "Friction UE (0-1)": 0.15},
        {"Candidat": "Mélenchon (LFI)", "Choc Dépenses (Mds€/an)": 95.0, "Baisses Impôts (Mds€/an)": 15.0, "Économies / Recettes (Mds€/an)": 65.0, "Friction UE (0-1)": 1.00},
        {"Candidat": "Glucksmann (PP/PS)", "Choc Dépenses (Mds€/an)": 42.0, "Baisses Impôts (Mds€/an)": 6.0, "Économies / Recettes (Mds€/an)": 34.0, "Friction UE (0-1)": 0.35},
        {"Candidat": "Attal (Renaissance)", "Choc Dépenses (Mds€/an)": 10.0, "Baisses Impôts (Mds€/an)": 14.0, "Économies / Recettes (Mds€/an)": 32.0, "Friction UE (0-1)": 0.15},
        {"Candidat": "Retailleau / Wauquiez (LR)", "Choc Dépenses (Mds€/an)": 12.0, "Baisses Impôts (Mds€/an)": 22.0, "Économies / Recettes (Mds€/an)": 46.0, "Friction UE (0-1)": 0.25}
    ]

    pib_fr_mds, dette_init, sp_init, spread_init, g_base = 2920.0, 115.2, -3.4, 76.0, 0.026
    resultats_mod = []
    trajectoires_dette = {"Année":}

    for prog in programmes:
        cand = prog["Candidat"]
        impulsion_d = prog["Choc Dépenses (Mds€/an)"] / pib_fr_mds
        impulsion_t = prog["Baisses Impôts (Mds€/an)"] / pib_fr_mds
        consolidation = prog["Économies / Recettes (Mds€/an)"] / pib_fr_mds
        delta_sp = consolidation - impulsion_d - impulsion_t

        g_cand = g_base + (0.85 * impulsion_d) + (0.45 * impulsion_t) - (0.55 * consolidation)
        sp_cand = sp_init + delta_sp

        choc_deficit_pts = max(0.0, -delta_sp * 100)
        spread_proj = max(45.0, round(spread_init + aversion_marche * (22.0 * choc_deficit_pts + 48.0 * prog["Friction UE (0-1)"]) - (14.0 * max(0.0, delta_sp * 100)), 0))
        oat_proj = taux_bce_ref + (spread_proj / 100.0)
        r_eff = (oat_proj / 100.0) * 0.65 + 0.018

        d_vec = [dette_init]
        for _ in range(4):
            d_vec.append(round(d_vec[-1] * ((1 + r_eff) / (1 + g_cand)) - (sp_cand * 100), 1))
        trajectoires_dette[cand] = d_vec

        if spread_proj >= 130 or d_vec[-1] >= 123.0:
            verdict = "🔴 Tension aiguë / Risque dégradation"
        elif spread_proj >= 95 or d_vec[-1] >= 117.0:
            verdict = "🟠 Vigilance élevée / Prime de risque"
        else:
            verdict = "🟢 Détente obligataire / Crédibilité"

        resultats_mod.append({
            "Candidat (> 8 %)": cand,
            "Solde Budg. Net (Mds€/an)": round(prog["Économies / Recettes (Mds€/an)"] - prog["Choc Dépenses (Mds€/an)"] - prog["Baisses Impôts (Mds€/an)"], 1),
            "Croissance Nominale Est. (%)": round(g_cand * 100, 2),
            "Spread OAT-Bund Conjecturé (bps)": int(spread_proj),
            "Taux OAT 10 ans Est. (%)": round(oat_proj, 2),
            "Dette / PIB 2030 (%)": d_vec[-1],
            "Attitude Conjecturée des Marchés": verdict
        })

    df_res = pd.DataFrame(resultats_mod).sort_values("Spread OAT-Bund Conjecturé (bps)")
    st.dataframe(df_res, hide_index=True, use_container_width=True)

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown("#### Conjecture : Prime de Risque Souverain par Programme (bps)")
        fig_sp_cand = px.bar(df_res, x="Candidat (> 8 %)", y="Spread OAT-Bund Conjecturé (bps)", color="Spread OAT-Bund Conjecturé (bps)", color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"])
        fig_sp_cand.add_hline(y=76, line_dash="dash", line_color="#0F172A", annotation_text="Spread actuel (~76 bps)")
        fig_sp_cand.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#0F172A", size=12), height=350, coloraxis_showscale=False, xaxis=dict(tickfont=dict(color="#0F172A"), gridcolor="#E2E8F0"), yaxis=dict(tickfont=dict(color="#0F172A"), gridcolor="#E2E8F0"))
        st.plotly_chart(fig_sp_cand, use_container_width=True)

    with m_col2:
        st.markdown("#### Trajectoire Conjecturée de la Dette Publique (% du PIB, 2026–2030)")
        df_traj = pd.DataFrame(trajectoires_dette)
        fig_traj = px.line(df_traj, x="Année", y=[p["Candidat"] for p in programmes], markers=True, labels={"value": "Dette (% du PIB)", "variable": ""})
        fig_traj.update_traces(line=dict(width=2.6))
        fig_traj.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#0F172A", size=12), height=350, xaxis=dict(tickfont=dict(color="#0F172A"), gridcolor="#E2E8F0"), yaxis=dict(tickfont=dict(color="#0F172A"), gridcolor="#E2E8F0"), legend=dict(orientation="h", y=1.22))
        st.plotly_chart(fig_traj, use_container_width=True)

    # --- SOUS-SECTION 3 : VEILLE EN TEMPS RÉEL ---
    st.divider()
    st.markdown("## 3. Veille en Temps Réel : Derniers Sondages & Propositions Économiques")
    rt_c1, rt_c2 = st.columns(2)
    with rt_c1:
        st.markdown("#### 📡 Derniers sondages publiés (Ifop, Elabe, Ipsos, Cluster 17...)")
        for item in fetch_2027_news("sondage+presidentielle+2027+intentions+vote+Ifop+OR+Elabe+OR+Ipsos"):
            st.markdown(f"• [{item['title']}]({item['link']}) *({item['pubDate']})*")
    with rt_c2:
        st.markdown("#### 📑 Programmes, annonces économiques & chiffrages")
        cand_filtre = st.selectbox("Filtrer l'actualité économique par candidat :", ["Tous les candidats principaux (2027)", "Bardella / Le Pen (RN)", "Édouard Philippe (Horizons)", "Jean-Luc Mélenchon (LFI)", "Raphaël Glucksmann (Place Publique / PS)", "Gabriel Attal (Renaissance)", "Bruno Retailleau / Laurent Wauquiez (LR)"])
        q_map = {
            "Tous les candidats principaux (2027)": "programme+economique+presidentielle+2027+chiffrage+budget+impots",
            "Bardella / Le Pen (RN)": "programme+economique+Bardella+Le+Pen+2027+budget+TVA",
            "Édouard Philippe (Horizons)": "programme+economique+Edouard+Philippe+2027+dette+retraites",
            "Jean-Luc Mélenchon (LFI)": "programme+economique+Melenchon+LFI+2027+SMIC+impots",
            "Raphaël Glucksmann (Place Publique / PS)": "programme+economique+Glucksmann+2027+fiscalite+ecologie",
            "Gabriel Attal (Renaissance)": "programme+economique+Gabriel+Attal+2027+budget+travail",
            "Bruno Retailleau / Laurent Wauquiez (LR)": "programme+economique+Retailleau+Wauquiez+2027+economies+impots"
        }
        for item in fetch_2027_news(q_map[cand_filtre]):
            st.markdown(f"• [{item['title']}]({item['link']}) *({item['pubDate']})*")

with tab_bio:
    st.subheader("À propos de l'auteur — Charles Tsimi")
    st.markdown("""
    <div class="method-card">
        <div class="method-title">Consultant Senior — Politiques Publiques & Affaires Publiques | Stratégie · Direction de Projets · Analyse Géoéconomique · Écrivain</div>
        <div class="method-body">
        Fort de 10 ans d’expérience au sein du secteur public (Agence nationale de la cohésion des territoires, Agence régionale de santé Île-de-France), du conseil en organisation, d’une ONG internationale et du milieu associatif, j’accompagne les décideurs publics et privés dans le pilotage de projets complexes, leurs relations institutionnelles et leurs transformations.<br><br>
        Auteur publié aux éditions JC Lattès (<i>Clandestinement vôtre</i>, <i>Il n’y a pas de Noirs en Afrique</i>) et chroniqueur politique et géoéconomique (200+ tribunes dans <i>Mediapart</i>, <i>Jeune Afrique</i>, <i>Le Jour</i>), j’allie intelligence institutionnelle, analyse macroéconomique et outils modernes d’aide à la décision par la donnée.<br><br>
        👉 <b>Feuilleter mon CV & Dossier de Compétences Interactif :</b> <a href="https://charles-tsimi.netlify.app/" target="_blank" style="color:#B45309;font-weight:700;">https://charles-tsimi.netlify.app/</a><br>
        📩 <b>Contact direct :</b> milanga.charles@gmail.com
        </div>
    </div>
    """, unsafe_allow_html=True)
