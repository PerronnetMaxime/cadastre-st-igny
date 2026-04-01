import streamlit as st
import pandas as pd

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="Cadastre", layout="centered")

# -------------------------------
# 🔐 MOT DE PASSE
# -------------------------------
password = st.text_input("🔐 Mot de passe", type="password")

if password != "mafemmeestgeniale":
    st.stop()

# -------------------------------
# TITRE
# -------------------------------
st.title("📄 Cadastre Saint-Igny-de-Vers")

# -------------------------------
# CHARGEMENT DATA
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    df.columns = df.columns.str.lower()
    return df

df = load_data()

# -------------------------------
# TROUVER COLONNES
# -------------------------------
def col(name):
    for c in df.columns:
        if name in c:
            return c
    return None

col_section = col("section")
col_numero = col("numero")
col_nom = col("nom")
col_prenom = col("prenom")
col_surface = col("surface")
col_adresse = col("adresse")
col_commune = col("commune")

# -------------------------------
# 🔎 RECHERCHE
# -------------------------------
st.markdown("## 🔎 Recherche parcelle")

col1, col2 = st.columns(2)

section_input = col1.text_input("Section (ex: AB)")
numero_input = col2.text_input("Numéro (ex: 283)")

section_input = section_input.strip().upper()
numero_input = numero_input.strip()

# -------------------------------
# RESULTAT
# -------------------------------
if section_input and numero_input:

    result = df[
        (df[col_section].astype(str).str.strip().str.upper() == section_input) &
        (df[col_numero].astype(str).str.strip() == numero_input)
    ]

    st.markdown("## 📍 Résultat")

    if not result.empty:
        row = result.iloc[0]

        st.success("Parcelle trouvée")

        st.markdown(f"""
        👤 **Propriétaire : {row.get(col_prenom, "")} {row.get(col_nom, "")}**  
        📐 Surface : {row.get(col_surface, "")}  
        📍 Adresse : {row.get(col_adresse, "")}  
        🏙️ Commune : {row.get(col_commune, "")}
        """)

    else:
        st.error("❌ Parcelle introuvable")
