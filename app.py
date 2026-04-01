import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cadastre St Igny de Vers", layout="centered")

st.title("🔎 Cadastre St Igny de Vers")

df = pd.read_excel("data.xlsx")

# Nettoyage
df = df.fillna("")

# 🔍 Recherche texte
recherche = st.text_input("🔍 Rechercher (nom, parcelle...)")

# 🎯 Filtre section
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

# Résultats
st.write(f"📊 {len(res)} résultat(s)")

# Affichage mobile
for _, row in res.iterrows():
    st.markdown(f"""
    ---
    🏠 **Parcelle : {row.get('numero', '')}**  
    📍 Commune : {row.get('commune_tx', '')}  
    🧭 Section : {row.get('section', '')}  
    👤 Propriétaire : {row.get('nom', 'N/A')}  
    📐 Surface : {row.get('contenance', '')}
    """)
