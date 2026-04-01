import streamlit as st
import pandas as pd

# ⚙️ CONFIG
st.set_page_config(
    page_title="Cadastre St Igny",
    page_icon="🏡",
    layout="centered"
)

# 🔐 MOT DE PASSE
PASSWORD = "1234"  # 👉 change ici

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Accès sécurisé")

    pwd = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")

    st.stop()

# 🎨 STYLE
st.markdown("""
<style>
.card {
    padding: 15px;
    border-radius: 15px;
    background-color: #f9f9f9;
    margin-bottom: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.title {
    font-size: 20px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🏡 Cadastre St Igny de Vers")

# 📂 CHARGEMENT DATA
@st.cache_data
def load_data():
    return pd.read_excel("data.xlsx")

df = load_data()

# 🔎 DETECTION COLONNES
def trouver_col(noms):
    for col in df.columns:
        for n in noms:
            if n.lower() in col.lower():
                return col
    return None

col_prenom = trouver_col(["prenom", "prénom"])
col_nom = trouver_col(["nom", "proprietaire"])
col_commune = trouver_col(["commune", "ville"])
col_surface = trouver_col(["surface", "contenance"])
col_adresse = trouver_col(["adresse", "rue", "voie"])
col_section = trouver_col(["section"])
col_numero = trouver_col(["numero", "parcelle"])

# 🔍 RECHERCHE
recherche = st.text_input("🔎 Rechercher (nom, parcelle...)")

# 🎯 FILTRE SECTION
if col_section:
    sections = sorted(df[col_section].dropna().unique())
    section = st.selectbox("📌 Filtrer par section", ["Toutes"] + list(sections))
else:
    section = "Toutes"

# 🧠 FILTRAGE
res = df.copy()

if recherche:
    res = res[
        res.astype(str).apply(
            lambda r: r.str.contains(recherche, case=False, na=False)
        ).any(axis=1)
    ]

if section != "Toutes" and col_section:
    res = res[res[col_section] == section]

# 📊 RESULTATS
st.write(f"📊 {len(res)} résultat(s)")

# 🧾 AFFICHAGE
for _, row in res.iterrows():
    prenom = row.get(col_prenom, "") if col_prenom else ""
    nom = row.get(col_nom, "N/A") if col_nom else ""
    commune = row.get(col_commune, "") if col_commune else ""
    surface = row.get(col_surface, "")
    adresse = row.get(col_adresse, "Non renseignée")
    numero = row.get(col_numero, "")

    st.markdown(f"""
<div class="card">
    <div class="title">🏠 Parcelle {numero}</div>
    👤 <b>{prenom} {nom}</b><br>
    📐 Surface : {surface}<br>
    📍 {adresse}<br>
    🏙️ {commune}
</div>
""", unsafe_allow_html=True)
