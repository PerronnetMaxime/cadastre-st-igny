import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cadastre St Igny de Vers", layout="centered")

st.title("🔎 Cadastre St Igny de Vers")

df = pd.read_excel("data.xlsx")
df = df.fillna("")

# 🔍 Détection automatique des colonnes
def find_col(possibles):
    for col in df.columns:
        for p in possibles:
            if p.lower() in col.lower():
                return col
    return None

col_nom = find_col(["nom", "proprietaire"])
col_prenom = find_col(["prenom"])
col_surface = find_col(["contenance", "surface"])
col_ville = find_col(["ville"])
col_adresse = find_col(["adresse", "voie", "rue"])

# Recherche
recherche = st.text_input("🔍 Rechercher")

# Filtre section
col_section = find_col(["section"])
sections = sorted(df[col_section].unique()) if col_section else []
section_filtre = st.selectbox("🧭 Filtrer par section", ["Toutes"] + list(sections))

# Filtrage
res = df.copy()

if recherche:
    res = res[
        res.astype(str).apply(lambda row: row.str.contains(recherche, case=False).any(), axis=1)
    ]

if section_filtre != "Toutes" and col_section:
    res = res[res[col_section] == section_filtre]

st.write(f"📊 {len(res)} résultat(s)")

# Affichage propre
for _, row in res.iterrows():
    st.markdown(f"""
    ---
    👤 **Nom : {row.get(col_nom, 'N/A')}**  
    📐 Surface : {row.get(col_surface, '')}  
    📍 Adresse : {row.get(col_adresse, 'Non renseignée')}  
    🏙️ Commune : {row.get(col_commune, '')}
    """)
