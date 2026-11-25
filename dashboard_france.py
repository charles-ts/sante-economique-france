import streamlit as st
import pandas as pd
import urllib.request
import xml.etree.ElementTree as ET
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Charles Tsimi | Intelligence Économique & Décision", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
@import url('https://googleapis.com');
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #EEF2F6 !important; color: #0F172A !important; font-family: 'Inter', sans-serif !important; }
h1, h2, h3 { font-family: 'Playfair Display', Georgia, serif !important; color: #0B1F3A !important; }
h4, p, span, label, div[data-testid="stMarkdownContainer"] { color: #1E293B !important; }
button[data-baseweb="tab"] { background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-radius: 6px 6px 0 0 !important; padding: 8px 14px !important; margin-right: 4px !important; }
button[data-baseweb="tab"] p { color: #334155 !important; font-weight: 600 !important; font-size: 0.88rem !important; }
button[data-baseweb="tab"][aria-selected="true"] { background-color: #0B1F3A !important; border-color: #0B1F3A !important; border-bottom: 3px solid #C59B27 !important; }
button[data-baseweb="tab"][aria-selected="true"] p { color: #FFFFFF !important; font-weight: 700 !important; }
.hero-box { background: linear-gradient(125deg, #0B1F3A 0%, #173763 100%); padding: 26px 32px; border-radius: 12px; border-bottom: 5px solid #C59B27; margin-bottom: 18px; box-shadow: 0 10px 25px rgba(11,31,58,0.14); }
.hero-kicker { font-size: 0.78rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #F3D06B !important; margin-bottom: 6px; }
.hero-title { font-family: 'Playfair Display', Georgia, serif; font-size: 2.0rem; font-weight: 700; color: #FFFFFF !important; margin: 0 0 6px 0; }
.hero-sub { font-size: 0.94rem; color: #E2E8F0 !important; margin: 0; }
div[data-testid="stMetric"] { background: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-top: 4px solid #0B1F3A !important; padding: 14px !important; border-radius: 8px !important; box-shadow: 0 3px 10px rgba(15,23,42,0.04) !important; }
div[data-testid="stMetricLabel"] p { color: #475569 !important; font-weight: 700 !important; font-size: 0.8rem !important; text-transform: uppercase !important; }
div[data-testid="stMetricValue"] div { color: #0B1F3A !important; font-size: 1.42rem !important; font-weight: 800 !important; }
.synth-card { background: #FFFFFF; border: 1px solid #CBD5E1; border-left: 6px solid #C59B27; padding: 18px 22px; border-radius: 8px; margin-bottom: 18px; }
.synth-title { font-family: 'Playfair Display', Georgia, serif; font-size: 1.18rem; font-weight: 700; color: #0B1F3A !important; margin-bottom: 8px; }
.info-card { background: #FFFFFF; border: 1px solid #CBD5E1; border-left: 4px solid #0B1F3A; padding: 16px 20px; border-radius: 8px; margin-bottom: 14px; }
.rating-card { background: #FFFFFF; border: 1px solid #CBD5E1; border-top: 4px solid #0B1F3A; padding: 16px; border-radius: 8px; text-align: center; }
.credit-tag { font-size: 0.78rem; color: #64748B !important; font-style: italic; margin-top: -6px; margin-bottom: 16px; }
.footer-discrete { margin-top: 44px; padding-top: 14px; border-top: 1px solid #CBD5E1; text-align: center; font-size: 0.82rem; color: #64748B !important; }
</style>""", unsafe_allow_html=True)

DATA_FR = pd.DataFrame({
    "Année": list(range(2006, 2027)),
    "PIB_Vol": (100.0, 102.4, 102.7, 99.7, 101.6, 103.8, 104.2, 104.8, 105.8, 107.0, 108.1, 110.6, 112.6, 114.7, 106.1, 113.3, 116.2, 117.5, 118.8, 119.6, 120.8),
    "Croissance": (2.4, 2.4, 0.3, -2.9, 1.9, 2.2, 0.3, 0.6, 1.0, 1.1, 1.1, 2.3, 1.8, 1.9, -7.5, 6.8, 2.6, 1.1, 1.1, 0.7, 1.0),
    "Chomage": (8.8, 8.0, 7.4, 9.1, 9.3, 9.2, 9.8, 10.3, 10.3, 10.4, 10.1, 9.4, 9.0, 8.4, 8.0, 7.9, 7.3, 7.3, 7.4, 7.5, 7.4),
    "Dette_PIB": (64.6, 64.5, 68.8, 83.0, 85.3, 87.8, 90.6, 93.4, 94.9, 95.6, 98.0, 98.1, 97.8, 97.4, 114.6, 112.7, 111.2, 109.9, 113.0, 115.2, 116.5),
    "Solde_PIB": (-2.4, -2.6, -3.3, -7.2, -6.9, -5.2, -5.0, -4.1, -3.9, -3.6, -3.6, -3.0, -2.3, -2.4, -8.9, -6.6, -4.7, -5.5, -5.8, -5.4, -5.0),
    "Inflation": (1.9, 1.6, 3.2, 0.1, 1.7, 2.3, 2.2, 1.0, 0.6, 0.1, 0.3, 1.2, 2.1, 1.3, 0.5, 2.1, 5.9, 5.7, 2.3, 1.4, 1.6),
    "OAT_10Y": (3.80, 4.30, 4.23, 3.65, 3.12, 3.32, 2.54, 2.20, 1.67, 0.84, 0.47, 0.81, 0.78, 0.13, -0.15, 0.01, 1.70, 3.00, 2.98, 3.15, 3.10)
})

@st.cache_data(ttl=900, show_spinner=False)
def get_ticker_hist(sym, period="1y"):
    try:
        h = yf.Ticker(sym).history(period=period)
        if not h.empty:
            h.index = h.index.tz_localize(None)
            return h
    except Exception:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=1800, show_spinner=False)
def get_rss(q, limit=5):
    url = f"https://google.com{q}&hl=fr&gl=FR&ceid=FR:fr"
    out = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            root = ET.fromstring(r.read().decode("utf-8"))
            for it in root.findall(".//item"):
                if len(out) < limit:
                    out.append({"title": it.find("title").text, "link": it.find("link").text, "date": it.find("pubDate").text[:16]})
    except Exception:
        pass
    return out

def style_chart(fig, h=340):
    fig.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#0F172A", size=12), height=h, margin=dict(t=40, b=30, l=40, r=20), xaxis=dict(tickfont=dict(color="#0F172A"), gridcolor="#E2E8F0"), yaxis=dict(tickfont=dict(color="#0F172A"), gridcolor="#E2E8F0"), legend=dict(orientation="h", y=1.14))
    return fig

if "admin_unlocked" not in st.session_state:
    st.session_state["admin_unlocked"] = False

top_l, top_r = st.columns([5.5, 1.2])
with top_r:
    lang = st.radio("Langue", ["🇫🇷 Français", "🇬🇧 English"], horizontal=True, label_visibility="collapsed")
is_en = ("English" in lang)

with top_l:
    kicker = "STRATEGIC DASHBOARD · FRANCE, EUROPE & GLOBAL MARKETS" if is_en else "TABLEAU DE BORD STRATÉGIQUE · FRANCE, EUROPE & MARCHÉS"
    title_h = "Charles Tsimi — Economic Intelligence & Decision Support" if is_en else "Charles Tsimi — Intelligence Économique & Aide à la Décision"
    sub_h = "Macroeconomic trajectories, fiscal sustainability, sovereign ratings, procurement & 2027 presidential scenarios." if is_en else "Analyse conjoncturelle, soutenabilité budgétaire, marchés financiers, décision achats et scénarios 2027."
    st.markdown(f'<div class="hero-box"><div class="hero-kicker">{kicker}</div><div class="hero-title">{title_h}</div><p class="hero-sub">{sub_h}</p></div>', unsafe_allow_html=True)

labels_fr = ["🇫🇷 Économie France", "📈 Bourse CAC 40", "🌍 Europe & Monde", "🛢️ Matières Premières & Achats", "🏛️ Notations", "🗳️ Présidentielles 2027", "🎛️ Simulateur", "📚 Sources & Glossaire", "👤 Bio"]
labels_en = ["🇫🇷 France Economy", "📈 CAC 40 Market", "🌍 Europe & World", "🛢️ Commodities & Procurement", "🏛️ Ratings", "🗳️ 2027 Election", "🎛️ Simulator", "📚 Sources & Glossary", "👤 Bio"]
if st.session_state["admin_unlocked"]:
    labels_fr.append("🔒 Notes Privées")
    labels_en.append("🔒 Private Notes")



tab_fr, tab_cac, tab_eu, tab_mat, tab_not, tab_2027, tab_sim, tab_src, tab_bio = st.tabs(labels_en if is_en else labels_fr)
with tab_fr:
    st.subheader("French Macroeconomic Trajectory (2006–2026) & Cross-Analysis" if is_en else "Indicateurs Économiques de la France (2006–2026 & Croisements)")
    last, prev = DATA_FR.tail(1).squeeze(), DATA_FR.tail(2).head(1).squeeze()
    pmi_comp = 48.2
    g_nom = last["Croissance"] + last["Inflation"]
    score = int(max(0, min(100, round(50 + (last["Croissance"] - 1.2)*8 + (7.5 - last["Chomage"])*4 + (80 - last["Dette_PIB"])*0.3 + (last["Solde_PIB"] + 3.0)*4 + (pmi_comp - 50)*1.5))))

    st.markdown(f"""<div class="synth-card"><div class="synth-title">{'Economic Health Index' if is_en else 'Synthèse Conjoncturelle — Indice de Santé Économique'} : {score} / 100 | Flash PMI France : {pmi_comp} pts</div>
    <div>• <b>{'Debt Sustainability (ECB / Treasury)' if is_en else 'Équation de soutenabilité (BCE / Bercy)'} :</b> OAT 10Y ({last['OAT_10Y']:.2f} %) vs {'Nominal Growth' if is_en else 'Croissance nominale'} ({g_nom:.2f} %) — {'🔴 Snowball effect active' if (is_en and last['OAT_10Y'] > g_nom) else ('🔴 Effet boule de neige actif' if last['OAT_10Y'] > g_nom else '🟢 Nominal sustainability')}.<br>
    • <b>Flash PMI S&P Global :</b> {pmi_comp} pts ({'50 = expansion threshold' if is_en else 'seuil expansion = 50'}).</div></div>""", unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("GDP Growth" if is_en else "1. Croissance PIB", f"{last['Croissance']:+.1f} %", f"{last['Croissance']-prev['Croissance']:+.1f} pts")
    c2.metric("Unemployment" if is_en else "2. Chômage BIT", f"{last['Chomage']:.1f} %", f"{last['Chomage']-prev['Chomage']:+.1f} pts", delta_color="inverse")
    c3.metric("Public Debt" if is_en else "3. Dette / PIB", f"{last['Dette_PIB']:.1f} %", f"{last['Dette_PIB']-prev['Dette_PIB']:+.1f} pts", delta_color="inverse")
    c4.metric("Fiscal Balance" if is_en else "4. Solde Public", f"{last['Solde_PIB']:+.1f} %", f"{last['Solde_PIB']-prev['Solde_PIB']:+.1f} pts")
    c5.metric("Inflation HICP" if is_en else "5. Inflation IPCH", f"{last['Inflation']:.1f} %", f"{last['Inflation']-prev['Inflation']:+.1f} pts", delta_color="inverse")
    c6.metric("10Y OAT Yield" if is_en else "6. Taux OAT 10 ans", f"{last['OAT_10Y']:.2f} %", f"{last['OAT_10Y']-prev['OAT_10Y']:+.2f} pts", delta_color="inverse")

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("#### Phillips Curve: Unemployment vs Inflation (2006–2026)" if is_en else "#### Croisement I : Courbe de Phillips Française (Chômage vs Inflation)")
        fig_ph = px.scatter(DATA_FR, x="Chomage", y="Inflation", text="Année", color="Année", color_continuous_scale="Blues")
        fig_ph.update_traces(textposition="top center", marker=dict(size=10))
        st.plotly_chart(style_chart(fig_ph), use_container_width=True)
        st.markdown('<div class="credit-tag">Graphique : Charles Tsimi | Sources : INSEE · Eurostat (2006–2026)</div>', unsafe_allow_html=True)
    with g2:
        st.markdown("#### Debt Sustainability: 10Y OAT Rate vs Nominal Growth" if is_en else "#### Croisement II : Soutenabilité de la Dette (Taux OAT vs Croissance Nominale)")
        df_s = DATA_FR.copy()
        df_s["Croissance_Nominale"] = df_s["Croissance"] + df_s["Inflation"]
        fig_sn = px.line(df_s, x="Année", y=["OAT_10Y", "Croissance_Nominale"], labels={"value": "%", "variable": ""})
        fig_sn.for_each_trace(lambda t: t.update(name="OAT 10Y (%)" if t.name == "OAT_10Y" else ("Nominal Growth (%)" if is_en else "Croissance Nominale (%)"), line=dict(width=3, color="#DC2626" if t.name == "OAT_10Y" else "#0B1F3A")))
        st.plotly_chart(style_chart(fig_sn), use_container_width=True)
        st.markdown('<div class="credit-tag">Graphique : Charles Tsimi | Sources : BCE · Agence France Trésor (Bercy) · INSEE</div>', unsafe_allow_html=True)

    g3, g4 = st.columns(2)
    with g3:
        st.markdown("#### Trajectoire Budgétaire sur 20 ans : Dette (% PIB) & Solde Public (% PIB)")
        fig_b = go.Figure()
        fig_b.add_trace(go.Bar(x=DATA_FR["Année"], y=DATA_FR["Solde_PIB"], name="Solde Public (% PIB)", marker_color="#B45309"))
        fig_b.add_trace(go.Scatter(x=DATA_FR["Année"], y=DATA_FR["Dette_PIB"]/10, name="Dette / 10 (échelle)", line=dict(color="#0B1F3A", width=3)))
        st.plotly_chart(style_chart(fig_b), use_container_width=True)
        st.markdown('<div class="credit-tag">Graphique : Charles Tsimi | Sources : Eurostat (Notification EDP) · Bercy (Loi de Finances)</div>', unsafe_allow_html=True)
    with g4:
        st.markdown("#### Dynamique de Richesse Réelle (PIB Base 100 en 2006) & Taux de Chômage")
        fig_p = px.line(DATA_FR, x="Année", y=["PIB_Vol", "Chomage"], labels={"value": "Indice / %", "variable": ""})
        st.plotly_chart(style_chart(fig_p), use_container_width=True)
        st.markdown('<div class="credit-tag">Graphique : Charles Tsimi | Sources : INSEE (Comptes Nationaux) · Eurostat</div>', unsafe_allow_html=True)

with tab_cac:
    st.subheader("Paris Stock Exchange (CAC 40) & Live Market Flash" if is_en else "Bourse de Paris — CAC 40 & Flash Infos Financiers")
    cac = get_ticker_hist("^FCHI", "1y")
    col_b1, col_b2 = st.columns([1.4, 1.0])
    with col_b1:
        if not cac.empty:
            v_now, v_prev = cac["Close"].tail(1).squeeze(), cac["Close"].tail(2).head(1).squeeze()
            st.metric("CAC 40 Index (Euronext Paris)", f"{v_now:,.2f} pts", f"{((v_now-v_prev)/v_prev)*100:+.2f} %")
            fig_c = px.area(cac.reset_index(), x="Date", y="Close", labels={"Close": "Points", "Date": ""})
            fig_c.update_traces(line_color="#0B1F3A", fillcolor="rgba(11,31,58,0.12)")
            st.plotly_chart(style_chart(fig_c, 360), use_container_width=True)
            st.markdown('<div class="credit-tag">Graphique : Charles Tsimi | Sources : Euronext Paris · Yahoo Finance</div>', unsafe_allow_html=True)
    with col_b2:
        st.markdown("#### 📰 Flash Infos Bourse (Boursorama, Les Échos, Zonebourse)")
        for it in get_rss("CAC+40+Bourse+Paris+Euronext+Boursorama+OR+Les+Echos", 4):
            st.markdown(f'<div class="info-card"><b><a href="{it["link"]}" target="_blank" style="text-decoration:none;color:#0B1F3A;">{it["title"]}</a></b><br><span style="font-size:0.8rem;color:#64748B;">{it["date"]}</span></div>', unsafe_allow_html=True)

with tab_eu:
    st.subheader("Eurozone & Global Economy (GDP & Growth)" if is_en else "Zone Euro & Économie Mondiale (Croissance & PIB)")
    df_w = pd.DataFrame({"Année": list(range(2019, 2027)), "France": (1.9, -7.5, 6.8, 2.6, 1.1, 1.1, 0.7, 1.0), "Zone Euro": (1.6, -6.1, 5.9, 3.4, 0.4, 0.8, 1.1, 1.3), "USA": (2.5, -2.2, 6.1, 2.5, 2.9, 2.8, 2.0, 2.1), "China": (6.0, 2.2, 8.4, 3.0, 5.2, 5.0, 4.5, 4.2), "World": (2.8, -2.7, 6.5, 3.5, 3.3, 3.2, 3.2, 3.3)})
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("World GDP (IMF)" if is_en else "PIB Mondial (FMI)", "$115 Tn", "+3.3 %")
    e2.metric("Eurozone Growth" if is_en else "Croissance Zone Euro", "+1.3 %", "+0.2 pt")
    e3.metric("ECB Deposit Rate" if is_en else "Taux Directeur BCE", "2.50 %", "ECB")
    e4.metric("US GDP Growth" if is_en else "Croissance États-Unis", "+2.1 %", "+1.1 pt vs FR")
    st.plotly_chart(style_chart(px.line(df_w, x="Année", y=["France", "Zone Euro", "USA", "China", "World"], markers=True), 380), use_container_width=True)
    st.markdown('<div class="credit-tag">Graphique : Charles Tsimi | Sources : FMI (WEO) · Eurostat · Banque Mondiale · BCE</div>', unsafe_allow_html=True)

with tab_mat:
    st.subheader("Commodities & Procurement Decision Support (Real EUR € Costs)" if is_en else "Matières Premières & Décision Achats (Coûts Réels en Euros €)")
    fx = get_ticker_hist("EURUSD=X", "6mo")
    eurusd = fx["Close"].tail(1).squeeze() if not fx.empty else 1.08
    commods = [("Brent Oil", "BZ=F"), ("Copper", "HG=F"), ("Natural Gas", "NG=F"), ("Wheat", "ZW=F"), ("Gold", "GC=F")]
    cols_c = st.columns(6)
    cols_c.pop(0).metric("EUR / USD", f"{eurusd:.4f} $", "Forex")
    series_eur, var_list = {}, []
    for label, sym in commods:
        hc = get_ticker_hist(sym, "6mo")
        if not hc.empty:
            v1_u, v0_u = hc["Close"].tail(1).squeeze(), hc["Close"].tail(2).head(1).squeeze()
            cols_c.pop(0).metric(f"{label} (€)", f"{v1_u/eurusd:,.2f} €", f"{((v1_u-v0_u)/v0_u)*100:+.2f} %")
            if not fx.empty:
                al = pd.DataFrame({"c": hc["Close"], "fx": fx["Close"]}).dropna()
                if not al.empty:
                    es = al["c"] / al["fx"]
                    series_eur[label] = (es / es.head(1).squeeze()) * 100
                    var_list.append(((es.tail(1).squeeze() / es.head(1).squeeze()) - 1) * 100)
    pression = int(max(0, min(100, round(50 + (sum(var_list)/len(var_list))*2.5)))) if var_list else 48
    st.markdown(f'<div class="synth-card"><div class="synth-title">{"Procurement Pressure Index" if is_en else "Indice Composite de Pression Achats (Intrants en €)"} : {pression} / 100</div><div>{"Favorable window for long-term supplier price renegotiation." if (is_en and pression < 55) else ("Fenêtre favorable pour verrouiller des contrats longs ou renégocier les tarifs fournisseurs." if pression < 55 else "Tension sur les intrants : activer les couvertures.")}</div></div>', unsafe_allow_html=True)
    if series_eur:
        st.plotly_chart(style_chart(px.line(pd.DataFrame(series_eur)), 350), use_container_width=True)
        st.markdown('<div class="credit-tag">Graphique : Charles Tsimi | Sources : ICE Futures · COMEX · CBOT · BCE (EUR/USD)</div>', unsafe_allow_html=True)

with tab_not:
    st.subheader("Sovereign Credit Ratings & Rating Agency Scale" if is_en else "Notations Financières de la France & Décryptage des Agences")
    n1, n2, n3, n4 = st.columns(4)
    n1.markdown('<div class="rating-card"><h4>Standard & Poor\'s</h4><h2>AA- (Negative)</h2><p>3 notches below AAA</p></div>', unsafe_allow_html=True)
    n2.markdown('<div class="rating-card"><h4>Moody\'s</h4><h2>Aa3 (Stable)</h2><p>Equivalent to AA-</p></div>', unsafe_allow_html=True)
    n3.markdown('<div class="rating-card"><h4>Fitch Ratings</h4><h2>AA- (Negative)</h2><p>3 notches below AAA</p></div>', unsafe_allow_html=True)
    n4.markdown('<div class="rating-card"><h4>Scope Ratings</h4><h2>AA- (Stable)</h2><p>ECB-recognized EU agency</p></div>', unsafe_allow_html=True)
    st.divider()
    st.dataframe(pd.DataFrame([
        {"Grade": "Prime (AAA / Aaa)", "Meaning": "Minimal default risk (Germany, Netherlands). Lowest borrowing yields."},
        {"Grade": "High Grade (AA+ to AA- / Aa1 to Aa3)", "Meaning": "Current French sovereign tier. High institutional strength, sensitive to fiscal deficits."},
        {"Grade": "Upper Medium (A+ to A-)", "Meaning": "Higher sensitivity to economic shocks; triggers higher sovereign risk spreads."},
        {"Grade": "Lower Medium (BBB+ to BBB-)", "Meaning": "Threshold of Investment Grade (Italy). Below BB+ is Speculative ('Junk')."}
    ]), hide_index=True, use_container_width=True)

with tab_2027:
    st.subheader("2027 French Presidential Election — Polls, Market Model & Charles's Third Eye" if is_en else "Présidentielles 2027 — Sondages, Modélisation Souveraine & Le Troisième Œil de Charles")
    sub_s, sub_oeil, sub_p = st.tabs([
        "📊 Polls & Trajectories (> 10%)" if is_en else "📊 Sondages & Évolution (> 10 %)",
        "👁️ Charles's Third Eye" if is_en else "👁️ Le Troisième Œil de Charles",
        "📐 Programs & Markets" if is_en else "📐 Programmes & Marchés"
    ])

    polls_data = pd.DataFrame.from_records((
        {"Date": "2026-06-15", "Source": "Ifop-Fiducial", "N": 1500, "Marine Le Pen": 34.0, "Édouard Philippe": 21.5, "Jean-Luc Mélenchon": 13.5, "Raphaël Glucksmann": 12.0, "Bruno Retailleau": 7.5, "Gabriel Attal": 5.5, "Éric Zemmour": 4.0, "David Lisnard": 1.5, "Nathalie Arthaud": 0.5},
        {"Date": "2026-07-20", "Source": "Elabe / Les Échos", "N": 1480, "Marine Le Pen": 33.5, "Édouard Philippe": 22.0, "Jean-Luc Mélenchon": 14.0, "Raphaël Glucksmann": 12.5, "Bruno Retailleau": 7.0, "Gabriel Attal": 5.0, "Éric Zemmour": 4.0, "David Lisnard": 1.5, "Nathalie Arthaud": 0.5},
        {"Date": "2026-09-10", "Source": "Ipsos / La Tribune", "N": 1600, "Marine Le Pen": 34.5, "Édouard Philippe": 20.5, "Jean-Luc Mélenchon": 13.0, "Raphaël Glucksmann": 13.0, "Bruno Retailleau": 8.0, "Gabriel Attal": 5.0, "Éric Zemmour": 3.8, "David Lisnard": 1.7, "Nathalie Arthaud": 0.5},
        {"Date": "2026-10-18", "Source": "Cluster 17", "N": 1850, "Marine Le Pen": 33.0, "Édouard Philippe": 21.0, "Jean-Luc Mélenchon": 15.0, "Raphaël Glucksmann": 12.0, "Bruno Retailleau": 8.0, "Gabriel Attal": 5.0, "Éric Zemmour": 4.0, "David Lisnard": 1.5, "Nathalie Arthaud": 0.5},
        {"Date": "2026-11-18", "Source": "OpinionWay / CNews", "N": 1520, "Marine Le Pen": 34.0, "Édouard Philippe": 21.5, "Jean-Luc Mélenchon": 14.0, "Raphaël Glucksmann": 12.5, "Bruno Retailleau": 7.5, "Gabriel Attal": 4.5, "Éric Zemmour": 4.0, "David Lisnard": 1.5, "Nathalie Arthaud": 0.5}
    ))

    with sub_s:
        with st.expander("➕ Saisir ou actualiser une enquête publiée (recalcul immédiat)", expanded=False):
            polls_df = st.data_editor(polls_data, num_rows="dynamic", use_container_width=True)
        cands_all = tuple(c for c in polls_df.columns if c not in ("Date", "Source", "N"))
        polls_s = polls_df.sort_values("Date").reset_index(drop=True)
        w_tot = polls_s["N"] * pd.Series(tuple(1.0 + 0.25 * i for i in range(len(polls_s))))
        brut_map = {c: round(float(polls_s[c].mean()), 2) for c in cands_all}
        croise_map = {c: round(float((polls_s[c] * w_tot).sum() / w_tot.sum()), 2) for c in cands_all}
        cands_sup10 = tuple(c for c in cands_all if croise_map[c] >= 10.0)

        col_s1, col_s2 = st.columns((1.05, 1.35))
        with col_s1:
            st.dataframe(pd.DataFrame({"Candidat": cands_all, "Moy. Brute (%)": tuple(brut_map[c] for c in cands_all), "Moy. Croisée Pondérée (%)": tuple(croise_map[c] for c in cands_all), "Seuil > 10 %": tuple("✅ > 10 %" if croise_map[c] >= 10.0 else "< 10 %" for c in cands_all)}).sort_values("Moy. Croisée Pondérée (%)", ascending=False), hide_index=True, use_container_width=True)
            st.caption("Sources : Ifop-Fiducial, Elabe, Ipsos, Cluster 17, OpinionWay.")
        with col_s2:
            st.markdown("#### Trajectoire dynamique croisée des candidats > 10 %")
            fig_s10 = px.line(polls_s, x="Date", y=list(cands_sup10), markers=True, labels={"value": "Intentions (%)", "variable": ""})
            fig_s10.add_hline(y=10.0, line_dash="dash", line_color="#475569", annotation_text="Seuil 10 %")
            st.plotly_chart(style_chart(fig_s10, 340), use_container_width=True)
            st.markdown('<div class="credit-tag">Graphique & Agrégation : Charles Tsimi | Sources : Instituts de sondages français (2026)</div>', unsafe_allow_html=True)

        st.markdown("**📡 Dernières dépêches sondagières en temps réel :**")
        for it in get_rss("sondage+presidentielle+2027+Le+Pen+OR+Philippe+OR+Melenchon+OR+Glucksmann+Ifop+OR+Elabe+OR+Ipsos", 4):
            st.markdown(f"• [{it['title']}]({it['link']}) *({it['date']})*")
