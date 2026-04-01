import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cadastre St Igny de Vers", layout="centered")

st.title("🔎 Cadastre St Igny de Vers")

df = pd.read_excel("data.xlsx")
df = df.fillna("")

# Recherche
recherche = st.text_input("🔍 Rechercher")

# Filtre section
sections = sorted(df["section"].unique())
section_filtre = st.selectbox("🧭 Filtrer par section", ["Toutes"] + list(sections))

# Filtrage
res = df.copy()

if recherche:
    res = res[
        res.astype(str).apply(lambda row: row.str.contains(recherche, case=False).any(), axis=1)
    ]

if section_filtre != "Toutes":
    res = res[res["section"] == section_filtre]

st.write(f"📊 {len(res)} résultat(s)")

# Détection adresse automatique
def get_adresse(row):
    if "adresse" in row:
        return row["adresse"]
    elif "voie" in row:
        return row["voie"]
    elif "num_voie" in row:
        return str(row.get("num_voie", "")) + " " + str(row.get("voie", ""))
    else:
        return "Non renseignée"

# Affichage
for _, row in res.iterrows():
    st.markdown(f"""
    ---
    👤 **Nom : {row.get('nom', 'N/A')}**  
    📐 Surface : {row.get('contenance', '')}  
    📍 Adresse : {get_adresse(row)}  
    🏙️ Commune : {row.get('commune_tx', '')}
    """)
