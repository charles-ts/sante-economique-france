import streamlit as st
import pandas as pd
import urllib.request
import xml.etree.ElementTree as ET
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Charles Tsimi | Intelligence Économique & Décision", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #F8FAFC !important; color: #0F172A !important; }
[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #CBD5E1 !important; }
h1, h2, h3, h4, p, span, label, div[data-testid="stMarkdownContainer"] { color: #0F172A !important; }
div[data-testid="stMetric"] { background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-top: 3px solid #0F2747 !important; padding: 14px !important; border-radius: 6px !important; box-shadow: 0 2px 4px rgba(15,23,42,0.03) !important; }
div[data-testid="stMetricLabel"] p { color: #475569 !important; font-weight: 700 !important; font-size: 0.84rem !important; }
div[data-testid="stMetricValue"] div { color: #0F2747 !important; font-size: 1.38rem !important; font-weight: 800 !important; }
.synth-card { background: #FFFFFF; border: 1px solid #CBD5E1; border-left: 5px solid #B45309; padding: 18px 22px; border-radius: 6px; margin-bottom: 18px; }
.synth-title { font-family: Georgia, serif; font-size: 1.15rem; font-weight: 700; color: #0F2747 !important; margin-bottom: 8px; }
.info-card { background: #FFFFFF; border: 1px solid #CBD5E1; border-left: 4px solid #0F2747; padding: 16px 20px; border-radius: 6px; margin-bottom: 14px; }
.credit-tag { font-size: 0.8rem; color: #64748B !important; font-style: italic; margin-top: -8px; margin-bottom: 14px; }
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

with st.sidebar:
    st.markdown("### 🧭 Navigation")
    section = st.selectbox("Choisir un module d'analyse :", [
        "1. Indicateurs Économiques France",
        "2. Bourse de Paris (CAC 40)",
        "3. Europe & Économie Mondiale",
        "4. Matières Premières & Décision Achats",
        "5. Notations Financières & Agences",
        "6. Présidentielles 2027",
        "7. Simulateur Macro & Budgétaire",
        "8. Générateur de Notes & Fiches",
        "9. Sources, Glossaire & Monétisation",
        "10. À propos — Charles Tsimi"
    ])
    st.divider()
    st.caption("Conçu et édité par **Charles Tsimi** · Sources : INSEE, Eurostat, BCE, OCDE, Bercy, FMI.")

st.title("Charles Tsimi — Intelligence Économique & Aide à la Décision")
if section == "1. Indicateurs Économiques France":
    st.subheader("1. Indicateurs Économiques de la France (Trajectoire 2006–2026 & Croisements)")
    last, prev = DATA_FR.tail(1).squeeze(), DATA_FR.tail(2).head(1).squeeze()
    pmi_comp = 48.2
    g_nom = last["Croissance"] + last["Inflation"]
    score = int(max(0, min(100, round(50 + (last["Croissance"] - 1.2)*8 + (7.5 - last["Chomage"])*4 + (80 - last["Dette_PIB"])*0.3 + (last["Solde_PIB"] + 3.0)*4 + (pmi_comp - 50)*1.5))))

    st.markdown(f"""<div class="synth-card"><div class="synth-title">Synthèse Conjoncturelle — Indice de Santé Économique : {score} / 100 | Flash PMI Composite France : {pmi_comp} pts</div>
    <div>• <b>Équation de soutenabilité (BCE / Bercy) :</b> Taux souverain OAT 10 ans ({last['OAT_10Y']:.2f} %) vs Croissance nominale ({g_nom:.2f} %) — {'🔴 Effet boule de neige actif' if last['OAT_10Y'] > g_nom else '🟢 Soutenabilité nominale'}.<br>
    • <b>Climat des affaires (Flash PMI S&P Global) :</b> À {pmi_comp} pts (seuil d'expansion à 50), l'activité privée signale une stabilisation progressive portée par les services.</div></div>""", unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("1. Croissance PIB", f"{last['Croissance']:+.1f} %", f"{last['Croissance']-prev['Croissance']:+.1f} pts")
    c2.metric("2. Chômage BIT", f"{last['Chomage']:.1f} %", f"{last['Chomage']-prev['Chomage']:+.1f} pts", delta_color="inverse")
    c3.metric("3. Dette / PIB", f"{last['Dette_PIB']:.1f} %", f"{last['Dette_PIB']-prev['Dette_PIB']:+.1f} pts", delta_color="inverse")
    c4.metric("4. Solde Public", f"{last['Solde_PIB']:+.1f} %", f"{last['Solde_PIB']-prev['Solde_PIB']:+.1f} pts")
    c5.metric("5. Inflation IPCH", f"{last['Inflation']:.1f} %", f"{last['Inflation']-prev['Inflation']:+.1f} pts", delta_color="inverse")
    c6.metric("6. Taux OAT 10 ans", f"{last['OAT_10Y']:.2f} %", f"{last['OAT_10Y']-prev['OAT_10Y']:+.2f} pts", delta_color="inverse")

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("#### Croisement I : Courbe de Phillips Française (Chômage vs Inflation, 2006–2026)")
        fig_ph = px.scatter(DATA_FR, x="Chomage", y="Inflation", text="Année", color="Année", color_continuous_scale="Blues")
        fig_ph.update_traces(textposition="top center", marker=dict(size=10))
        st.plotly_chart(style_chart(fig_ph), use_container_width=True)
        st.markdown('<div class="credit-tag">Graphique : Charles Tsimi | Sources : INSEE · Eurostat (Séries harmonisées 2006–2026)</div>', unsafe_allow_html=True)
    with g2:
        st.markdown("#### Croisement II : Soutenabilité de la Dette (Taux OAT 10 ans vs Croissance Nominale)")
        df_s = DATA_FR.copy()
        df_s["Croissance_Nominale"] = df_s["Croissance"] + df_s["Inflation"]
        fig_sn = px.line(df_s, x="Année", y=["OAT_10Y", "Croissance_Nominale"], labels={"value": "%", "variable": ""})
        fig_sn.for_each_trace(lambda t: t.update(name="Taux OAT 10 ans (%)" if t.name == "OAT_10Y" else "Croissance Nominale (%)", line=dict(width=3, color="#DC2626" if t.name == "OAT_10Y" else "#0F2747")))
        st.plotly_chart(style_chart(fig_sn), use_container_width=True)
        st.markdown('<div class="credit-tag">Graphique : Charles Tsimi | Sources : BCE · Agence France Trésor (Bercy) · INSEE</div>', unsafe_allow_html=True)

    g3, g4 = st.columns(2)
    with g3:
        st.markdown("#### Trajectoire Budgétaire sur 20 ans : Dette (% PIB) & Solde Public (% PIB)")
        fig_b = go.Figure()
        fig_b.add_trace(go.Bar(x=DATA_FR["Année"], y=DATA_FR["Solde_PIB"], name="Solde Public (% PIB)", marker_color="#B45309"))
        fig_b.add_trace(go.Scatter(x=DATA_FR["Année"], y=DATA_FR["Dette_PIB"]/10, name="Dette / 10 (échelle)", line=dict(color="#0F2747", width=3)))
        st.plotly_chart(style_chart(fig_b), use_container_width=True)
        st.markdown('<div class="credit-tag">Graphique : Charles Tsimi | Sources : Eurostat (Notification EDP) · Bercy (Loi de Finances)</div>', unsafe_allow_html=True)
    with g4:
        st.markdown("#### Dynamique de Richesse Réelle (PIB Base 100 en 2006) & Taux de Chômage")
        fig_p = px.line(DATA_FR, x="Année", y=["PIB_Vol", "Chomage"], labels={"value": "Indice / %", "variable": ""})
        st.plotly_chart(style_chart(fig_p), use_container_width=True)
        st.markdown('<div class="credit-tag">Graphique : Charles Tsimi | Sources : INSEE (Comptes Nationaux) · Eurostat</div>', unsafe_allow_html=True)

elif section == "2. Bourse de Paris (CAC 40)":
    st.subheader("2. Bourse de Paris — CAC 40 & Actualité Financière en Direct")
    cac = get_ticker_hist("^FCHI", "1y")
    col_b1, col_b2 = st.columns([1.4, 1.0])
    with col_b1:
        if not cac.empty:
            v_now, v_prev = cac["Close"].tail(1).squeeze(), cac["Close"].tail(2).head(1).squeeze()
            st.metric("Indice CAC 40 (Euronext Paris — Temps réel)", f"{v_now:,.2f} pts", f"{((v_now-v_prev)/v_prev)*100:+.2f} %")
            fig_c = px.area(cac.reset_index(), x="Date", y="Close", labels={"Close": "Points", "Date": ""})
            fig_c.update_traces(line_color="#0F2747", fillcolor="rgba(15,39,71,0.12)")
            st.plotly_chart(style_chart(fig_c, 360), use_container_width=True)
            st.markdown('<div class="credit-tag">Graphique : Charles Tsimi | Sources : Euronext Paris · Yahoo Finance (Flux temps réel)</div>', unsafe_allow_html=True)
    with col_b2:
        st.markdown("#### 📰 Flash Infos Bourse de Paris (Boursorama, Les Échos, Zonebourse)")
        for it in get_rss("CAC+40+Bourse+Paris+Euronext+Boursorama+OR+Les+Echos", 4):
            st.markdown(f'<div class="info-card"><b><a href="{it["link"]}" target="_blank" style="text-decoration:none;color:#0F2747;">{it["title"]}</a></b><br><span style="font-size:0.8rem;color:#64748B;">Publié : {it["date"]}</span></div>', unsafe_allow_html=True)

elif section == "3. Europe & Économie Mondiale":
    st.subheader("3. Zone Euro & Économie Mondiale (Croissance & PIB)")
    df_w = pd.DataFrame({
        "Année": list(range(2019, 2027)),
        "France": (1.9, -7.5, 6.8, 2.6, 1.1, 1.1, 0.7, 1.0),
        "Zone Euro": (1.6, -6.1, 5.9, 3.4, 0.4, 0.8, 1.1, 1.3),
        "États-Unis": (2.5, -2.2, 6.1, 2.5, 2.9, 2.8, 2.0, 2.1),
        "Chine": (6.0, 2.2, 8.4, 3.0, 5.2, 5.0, 4.5, 4.2),
        "Monde": (2.8, -2.7, 6.5, 3.5, 3.3, 3.2, 3.2, 3.3)
    })
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("PIB Mondial (FMI)", "115 000 Mds $", "+3,3 % croissance")
    e2.metric("Croissance Zone Euro", "+1,3 %", "+0,2 pt vs 2025")
    e3.metric("Taux Directeur BCE", "2,50 %", "Facilité de dépôt")
    e4.metric("Croissance États-Unis", "+2,1 %", "+1,1 pt vs France")
    fig_w = px.line(df_w, x="Année", y=["France", "Zone Euro", "États-Unis", "Chine", "Monde"], markers=True, labels={"value": "Croissance PIB (%)", "variable": ""})
    st.plotly_chart(style_chart(fig_w, 380), use_container_width=True)
    st.markdown('<div class="credit-tag">Graphique : Charles Tsimi | Sources : FMI (World Economic Outlook) · Eurostat · Banque Mondiale · BCE</div>', unsafe_allow_html=True)

elif section == "4. Matières Premières & Décision Achats":
    st.subheader("4. Matières Premières & Aide à la Décision Achats (Coûts Réels en Euros €)")
    fx = get_ticker_hist("EURUSD=X", "6mo")
    eurusd = fx["Close"].tail(1).squeeze() if not fx.empty else 1.08

    commods = [("Pétrole Brent", "BZ=F", "baril"), ("Cuivre Industriel", "HG=F", "livre"), ("Gaz Naturel", "NG=F", "MMBtu"), ("Blé Meunier", "ZW=F", "boisseau"), ("Or (Valeur refuge)", "GC=F", "once")]
    cols_c = st.columns(6)
    cols_c[0].metric("Parité EUR / USD", f"{eurusd:.4f} $", "Taux BCE / Forex")
    series_usd, series_eur, var_3m_list = {}, {}, []

    for idx, (label, sym, unite) in enumerate(commods):
        hc = get_ticker_hist(sym, "6mo")
        if not hc.empty:
            v1_usd = hc["Close"].tail(1).squeeze()
            v0_usd = hc["Close"].tail(2).head(1).squeeze()
            v1_eur = v1_usd / eurusd
            cols_c[idx+1].metric(f"{label} (€)", f"{v1_eur:,.2f} €", f"{((v1_usd-v0_usd)/v0_usd)*100:+.2f} % (USD)")
            series_usd[label] = (hc["Close"] / hc["Close"].head(1).squeeze()) * 100
            if not fx.empty:
                aligned = pd.DataFrame({"c": hc["Close"], "fx": fx["Close"]}).dropna()
                if not aligned.empty:
                    eur_s = aligned["c"] / aligned["fx"]
                    series_eur[label] = (eur_s / eur_s.head(1).squeeze()) * 100
                    var_3m_list.append(((eur_s.tail(1).squeeze() / eur_s.head(1).squeeze()) - 1) * 100)

    pression = int(max(0, min(100, round(50 + (sum(var_3m_list)/len(var_3m_list))*2.5)))) if var_3m_list else 48
    recommandation = "🟢 Fenêtre favorable pour verrouiller des contrats longs ou négocier des baisses tarifaires fournisseurs." if pression < 45 else ("🟠 Vigilance modérée : privilégier les clauses d'indexation symétriques." if pression < 65 else "🔴 Forte tension sur les intrants : activer les couvertures et sécuriser les stocks critiques.")
    st.markdown(f'<div class="synth-card"><div class="synth-title">Indice Composite de Pression Achats (Intrants convertis en €) : {pression} / 100</div><div><b>Recommandation Direction des Achats :</b> {recommandation}</div></div>', unsafe_allow_html=True)

    if series_eur:
        fig_cm = px.line(pd.DataFrame(series_eur), labels={"value": "Coût réel en Euros (Base 100 sur 6 mois)", "variable": "", "index": ""})
        st.plotly_chart(style_chart(fig_cm, 360), use_container_width=True)
        st.markdown('<div class="credit-tag">Graphique & Indice Pression Achats : Charles Tsimi | Sources : ICE Futures · COMEX · CBOT · BCE (Parité EUR/USD)</div>', unsafe_allow_html=True)
elif section == "5. Notations Financières & Agences":
    st.subheader("5. Notations Financières de la France & Décryptage du Système des Agences")
    n1, n2, n3, n4 = st.columns(4)
    n1.markdown('<div class="rating-card"><h4>Standard & Poor\'s</h4><h2>AA- (Persp. Négative)</h2><p>3e cran sous le triple A</p></div>', unsafe_allow_html=True)
    n2.markdown('<div class="rating-card"><h4>Moody\'s</h4><h2>Aa3 (Persp. Stable)</h2><p>Équivalent AA- (4e cran)</p></div>', unsafe_allow_html=True)
    n3.markdown('<div class="rating-card"><h4>Fitch Ratings</h4><h2>AA- (Persp. Négative)</h2><p>3e cran sous le triple A</p></div>', unsafe_allow_html=True)
    n4.markdown('<div class="rating-card"><h4>Scope Ratings</h4><h2>AA- (Persp. Stable)</h2><p>Agence européenne agréée BCE</p></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("#### Comprendre l'échelle de notation souveraine (Impact sur les taux d'emprunt)")
    df_scale = pd.DataFrame([
        {"Catégorie": "Qualité maximale (Prime)", "S&P / Fitch / Scope": "AAA", "Moody's": "Aaa", "Signification financière": "Risque de défaut quasi nul (ex : Allemagne, Pays-Bas). Taux d'emprunt plancher."},
        {"Catégorie": "Haute qualité (High Grade)", "S&P / Fitch / Scope": "AA+ / AA / AA-", "Moody's": "Aa1 / Aa2 / Aa3", "Signification financière": "Zone actuelle de la France. Signature très solide, mais sensibilité accrue aux dérapages budgétaires."},
        {"Catégorie": "Qualité moyenne supérieure", "S&P / Fitch / Scope": "A+ / A / A-", "Moody's": "A1 / A2 / A3", "Signification financière": "Sensibilité aux chocs conjoncturels. Hausse mécanique de la prime de risque exigée par les fonds."},
        {"Catégorie": "Qualité moyenne inférieure", "S&P / Fitch / Scope": "BBB+ / BBB / BBB-", "Moody's": "Baa1 / Baa2 / Baa3", "Signification financière": "Seuil limite de la catégorie « Investment Grade » (ex : Italie). En dessous (BB+ / Ba1), catégorie spéculative (« Junk »)."}
    ])
    st.dataframe(df_scale, hide_index=True, use_container_width=True)

elif section == "6. Présidentielles 2027":
    st.subheader("6. Analyse Économique & Budgétaire — Présidentielles 2027")
    sub_sond, sub_prog, sub_veille = st.tabs(["📊 Sondages (8 Candidats & Dynamiques)", "📐 Programmes & Modélisation des Marchés", "📡 Veille Temps Réel"])

    polls_8 = pd.DataFrame([
        {"Date": "2026-08-15", "N": 1500, "RN (Bardella/Le Pen)": 33.0, "Horizons (Philippe)": 21.5, "LFI (Mélenchon)": 13.5, "PP/PS (Glucksmann)": 12.0, "Renaissance (Attal)": 10.0, "LR (Retailleau/Wauquiez)": 8.5, "EELV (Tondelier)": 4.5, "Reconquête (Zemmour)": 4.0},
        {"Date": "2026-09-20", "N": 1600, "RN (Bardella/Le Pen)": 33.5, "Horizons (Philippe)": 21.0, "LFI (Mélenchon)": 14.0, "PP/PS (Glucksmann)": 12.5, "Renaissance (Attal)": 9.5, "LR (Retailleau/Wauquiez)": 8.5, "EELV (Tondelier)": 4.0, "Reconquête (Zemmour)": 4.5},
        {"Date": "2026-10-25", "N": 1550, "RN (Bardella/Le Pen)": 34.0, "Horizons (Philippe)": 20.5, "LFI (Mélenchon)": 13.0, "PP/PS (Glucksmann)": 13.0, "Renaissance (Attal)": 10.0, "LR (Retailleau/Wauquiez)": 9.0, "EELV (Tondelier)": 4.2, "Reconquête (Zemmour)": 3.8},
        {"Date": "2026-11-22", "N": 1700, "RN (Bardella/Le Pen)": 33.5, "Horizons (Philippe)": 22.0, "LFI (Mélenchon)": 13.5, "PP/PS (Glucksmann)": 12.5, "Renaissance (Attal)": 10.0, "LR (Retailleau/Wauquiez)": 8.5, "EELV (Tondelier)": 4.0, "Reconquête (Zemmour)": 4.0}
    ])
    cands_8 = [c for c in polls_8.columns if c not in ("Date", "N")]

    with sub_sond:
        st.markdown("#### Vue croisée dynamique des 8 principaux candidats & Indice original de Stabilité (IVDE)")
        w_rec = [1.0 + 0.3 * i for i in range(len(polls_8))]
        w_tot = polls_8["N"] * w_rec
        df_ivde = pd.DataFrame({
            "Candidat (Top 8)": cands_8,
            "Moyenne Brute (%)": [round(polls_8[c].mean(), 2) for c in cands_8],
            "Moyenne Croisée Pondérée (%)": [round((polls_8[c]*w_tot).sum()/w_tot.sum(), 2) for c in cands_8],
            "Momentum (Dernier vs Début)": [round(polls_8[c].tail(1).squeeze() - polls_8[c].head(1).squeeze(), 2) for c in cands_8],
            "Indice Original IVDE (Stabilité/100)": [round(100 - polls_8[c].std()*12, 1) for c in cands_8]
        }).sort_values("Moyenne Croisée Pondérée (%)", ascending=False)
        st.dataframe(df_ivde, hide_index=True, use_container_width=True)

        fig_all8 = px.line(polls_8, x="Date", y=cands_8, markers=True, labels={"value": "Intentions de vote (%)", "variable": ""})
        st.plotly_chart(style_chart(fig_all8, 360), use_container_width=True)
        st.markdown('<div class="credit-tag">Graphique & Indice IVDE : Charles Tsimi | Sources : Agrégation pondérée Ifop, Elabe, Ipsos, Cluster 17</div>', unsafe_allow_html=True)

        cand_solo = st.selectbox("Isoler la courbe d'évolution séparée d'un candidat :", cands_8)
        fig_solo = px.area(polls_8, x="Date", y=cand_solo, markers=True, labels={cand_solo: "Intentions (%)", "Date": ""})
        fig_solo.update_traces(line_color="#B45309", fillcolor="rgba(180,83,9,0.15)")
        st.plotly_chart(style_chart(fig_solo, 260), use_container_width=True)

    with sub_prog:
        st.markdown("#### Chiffrage des programmes & Modélisation mathématique de la réaction des marchés")
        aversion = st.slider("Aversion au risque des marchés obligataires (α)", 0.6, 1.8, 1.0, 0.1)
        progs = [
            ("RN (Bardella/Le Pen)", 38.0, 24.0, 17.0, 0.85, "Baisse TVA énergie, priorité nationale, hausse dépenses régaliennes"),
            ("Horizons (Philippe)", 8.0, 12.0, 38.0, 0.15, "Maîtrise dépense sociale, réforme retraite/travail, désendettement"),
            ("LFI (Mélenchon)", 95.0, 15.0, 65.0, 1.00, "SMIC 1600€, retraite 60 ans, planification écologique, forte hausse fiscalité capital"),
            ("PP/PS (Glucksmann)", 42.0, 6.0, 34.0, 0.35, "Investissement vert européen, taxation superprofits & hauts patrimoines"),
            ("Renaissance (Attal)", 10.0, 14.0, 32.0, 0.15, "Politique de l'offre, baisse charges travail, trajectoire désendettement"),
            ("LR (Retailleau/Wauquiez)", 12.0, 22.0, 46.0, 0.25, "Choc d'économies publiques, baisse impôts de production & succession")
        ]
        res_p, traj_p = [], {"Année": list(range(2026, 2031))}
        for nom, dep, imp, eco, fric, mesures in progs:
            dsp = (eco - dep - imp) / 2920.0
            g_est = 0.026 + 0.85*(dep/2920.0) + 0.45*(imp/2920.0) - 0.55*(eco/2920.0)
            prime = max(45.0, round(76.0 + aversion*(22.0*max(0.0, -dsp*100) + 48.0*fric) - 14.0*max(0.0, dsp*100), 0))
            oat = 2.35 + prime/100.0
            dv = [115.2]
            for _ in range(4):
                dv.append(round(dv[-1]*((1 + (oat/100.0)*0.65 + 0.018)/(1 + g_est)) - ((-0.034 + dsp)*100), 1))
            traj_p[nom] = dv
            ismf = int(max(0, min(100, round(100 - (prime - 45)*0.6 - max(0, dv[-1] - 112)*2.5))))
            res_p.append({"Candidat": nom, "Mesures phares": mesures, "Solde Net (Mds€/an)": round(eco-dep-imp, 1), "Prime Risque (bps)": int(prime), "Taux OAT Est. (%)": round(oat, 2), "Dette 2030 (% PIB)": dv[-1], "Indice Soutenabilité ISMF (/100)": ismf})
        df_rp = pd.DataFrame(res_p).sort_values("Indice Soutenabilité ISMF (/100)", ascending=False)
        st.dataframe(df_rp, hide_index=True, use_container_width=True)
        fig_tp = px.line(pd.DataFrame(traj_p), x="Année", y=[x.pop(0) if isinstance(x, list) else x[0] for x in progs], markers=True, labels={"value": "Dette Conjecturée (% PIB)", "variable": ""})
        st.plotly_chart(style_chart(fig_tp, 340), use_container_width=True)
        st.markdown('<div class="credit-tag">Modélisation & Indice ISMF : Charles Tsimi | Équation dynamique de Domar sur base INSEE / Bercy</div>', unsafe_allow_html=True)

    with sub_veille:
        st.markdown("#### Flux en temps réel : Sondages & Propositions économiques des candidats")
        for it in get_rss("presidentielle+2027+programme+economique+OR+sondage+budget", 6):
            st.markdown(f"• [{it['title']}]({it['link']}) *({it['date']})*")
