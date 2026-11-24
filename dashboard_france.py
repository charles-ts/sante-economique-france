import streamlit as st
import pandas as pd
import urllib.request
import xml.etree.ElementTree as ET
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf

st.set_page_config(page_title="Charles Tsimi | Santé Économique Française", layout="wide")
st.markdown("""<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #F4F6F9 !important; color: #0F172A !important; }
h1, h2, h3, h4, p, span, label, div[data-testid="stMarkdownContainer"] { color: #0F172A !important; }
button[data-baseweb="tab"] p { color: #334155 !important; font-weight: 600 !important; }
button[data-baseweb="tab"][aria-selected="true"] p { color: #0F2747 !important; font-weight: 800 !important; }
div[data-testid="stMetric"] { background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-top: 3px solid #0F2747 !important; padding: 12px !important; border-radius: 6px !important; }
.algo-box { background: #FFFFFF; border: 1px solid #CBD5E1; border-left: 5px solid #B45309; padding: 16px 20px; border-radius: 6px; margin-bottom: 16px; }
.algo-title { font-family: Georgia, serif; font-size: 1.1rem; font-weight: 700; color: #0F2747 !important; margin-bottom: 6px; }
.method-card { background: #FFFFFF; border: 1px solid #CBD5E1; border-left: 4px solid #0F2747; padding: 14px 18px; border-radius: 6px; margin-bottom: 12px; }
.method-title { font-size: 1rem; font-weight: 700; color: #0F2747 !important; margin-bottom: 4px; }
.method-body { font-size: 0.92rem; line-height: 1.5; color: #1E293B !important; }
.rating-card { background: #FFFFFF; border: 1px solid #CBD5E1; border-top: 4px solid #0F2747; padding: 16px; border-radius: 8px; text-align: center; }
</style>""", unsafe_allow_html=True)

st.title("Charles Tsimi — Tableau de bord de la santé économique française")
st.caption("Sources croisées : INSEE · Eurostat · BCE · OCDE · Bercy (AFT) · Banque Mondiale · Yahoo Finance")
DATA_HIST = pd.DataFrame({
    "Année": list(range(2006, 2027)),
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

def style_fig(fig, h=320):
    fig.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#0F172A", size=12), height=h, xaxis=dict(tickfont=dict(color="#0F172A"), gridcolor="#E2E8F0"), yaxis=dict(tickfont=dict(color="#0F172A"), gridcolor="#E2E8F0"), legend=dict(orientation="h", y=1.15))
    return fig
tab_macro, tab_notes, tab_methodo, tab_2027, tab_bio = st.tabs(["📊 Santé Économique Française (20 ans & Repères)", "🏛️ Note des Marchés & Agences", "🧭 Méthodologie & Sources", "🇫🇷 Présidentielles 2027", "👤 Bio / Parcours"])

with tab_macro:
    df_mkt = fetch_markets()
    last, prev = DATA_HIST.tail(1).squeeze(), DATA_HIST.tail(2).head(1).squeeze()
    gdp_now, inf_now, debt_now, def_now, unemp_now, sp_now, oat_now = last["CROISS_FR"], last["INF_FR"], last["DETTE_FR"], last["DEF_FR"], last["CHOM_FR"], last["SPREAD_BPS"], last["OAT_10Y"]
    score = int(max(0, min(100, round(50 + (gdp_now - 1.2)*8 + (7.5 - unemp_now)*4 + (80 - debt_now)*0.3 + (def_now + 3.0)*4 + (60 - sp_now)*0.3))))
    signaux = [
        f"🔴 <b>Effet boule de neige actif (BCE / Bercy) :</b> Le taux souverain OAT à 10 ans ({oat_now:.2f} %) dépasse la croissance nominale ({gdp_now + inf_now:.2f} %).",
        f"⚠️ <b>Double contrainte budgétaire (Eurostat / Bercy) :</b> Déficit à {def_now:.1f} % (plafond -3 %) et dette à {debt_now:.1f} % du PIB."
    ]
    st.markdown(f'<div class="algo-box"><div class="algo-title">Synthèse Conjoncturelle & Points de Vigilance — Indice de Santé Économique : {score} / 100</div><div>{"<br>".join(signaux)}</div></div>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("France — PIB (INSEE / Eurostat)", f"{gdp_now:+.2f} %", "Référence nationale")
    m2.metric("Zone Euro — PIB (Eurostat / BCE)", f"{last['CROISS_EZ']:+.2f} %", f"Écart France : {gdp_now - last['CROISS_EZ']:+.2f} pts")
    m3.metric("États-Unis — PIB (Baromètre mondial)", f"{last['CROISS_US']:+.2f} %", f"Écart France : {gdp_now - last['CROISS_US']:+.2f} pts")
    st.divider()

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("### 1. PIB Réel (Base 100 en 2006) — INSEE · Eurostat")
        st.plotly_chart(style_fig(px.line(DATA_HIST, x="Année", y=["PIB_FR", "PIB_DE"])), use_container_width=True)
    with g2:
        st.markdown("### 2. Chômage Harmonisé (20 ans) — Eurostat · INSEE")
        st.plotly_chart(style_fig(px.line(DATA_HIST, x="Année", y=["CHOM_FR", "CHOM_DE"])), use_container_width=True)
    g3, g4 = st.columns(2)
    with g3:
        st.markdown("### 3. Dette Publique (% PIB) — Eurostat · Bercy")
        st.plotly_chart(style_fig(px.line(DATA_HIST, x="Année", y=["DETTE_FR", "DETTE_DE"])), use_container_width=True)
    with g4:
        st.markdown("### 4. Déficit Public (% PIB) — Eurostat · Bercy")
        st.plotly_chart(style_fig(px.bar(DATA_HIST, x="Année", y=["DEF_FR", "DEF_DE"], barmode="group")), use_container_width=True)
with tab_notes:
    st.subheader("Évaluation Souveraine de la France par les Agences de Notation")
    n1, n2, n3, n4 = st.columns(4)
    n1.markdown('<div class="rating-card"><h4>Standard & Poor\'s</h4><h2>AA- (Négative)</h2></div>', unsafe_allow_html=True)
    n2.markdown('<div class="rating-card"><h4>Moody\'s</h4><h2>Aa3 (Stable)</h2></div>', unsafe_allow_html=True)
    n3.markdown('<div class="rating-card"><h4>Fitch Ratings</h4><h2>AA- (Négative)</h2></div>', unsafe_allow_html=True)
    n4.markdown('<div class="rating-card"><h4>Scope Ratings</h4><h2>AA- (Stable)</h2></div>', unsafe_allow_html=True)

with tab_methodo:
    st.subheader("Grille d'analyse & Sources (INSEE, Eurostat, BCE, OCDE, Bercy)")
    for t, b in [("1. PIB Réel (INSEE · Eurostat)", "Mesure la croissance en volume hors inflation depuis 2006."), ("2. Chômage (Eurostat · INSEE)", "Capacité d'absorption du marché du travail sur 20 ans."), ("3. Dette & Déficit (Eurostat · Bercy)", "Soutenabilité budgétaire face aux critères européens (-3 % et 60 %)."), ("4. Spread OAT 10 ans (BCE · AFT)", "Thermomètre quotidien de la confiance des investisseurs.")]:
        st.markdown(f'<div class="method-card"><div class="method-title">{t}</div><div class="method-body">{b}</div></div>', unsafe_allow_html=True)
