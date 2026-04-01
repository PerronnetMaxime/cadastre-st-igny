import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="Cadastre", layout="wide")

# -------------------------------
# 🔐 MOT DE PASSE
# -------------------------------
password = st.text_input("🔐 Mot de passe", type="password")

if password != "mafemmeestgeniale":
    st.stop()

# -------------------------------
# TITRE
# -------------------------------
st.title("🗺️ Cadastre Saint-Igny-de-Vers")

# -------------------------------
# CHARGEMENT DATA
# -------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("data.xlsx")

@st.cache_data
def load_geo():
    with open("parcelles.json", encoding="utf-8") as f:
        return json.load(f)

df = load_data()
geo = load_geo()

# -------------------------------
# TROUVER COLONNES
# -------------------------------
def find_col(names):
    for col in df.columns:
        for name in names:
            if name.lower() in col.lower():
                return col
    return None

col_section = find_col(["section"])
col_numero = find_col(["numero"])
col_nom = find_col(["nom"])
col_prenom = find_col(["prenom"])
col_surface = find_col(["surface"])
col_adresse = find_col(["adresse"])
col_commune = find_col(["commune"])

# -------------------------------
# 🗺️ CARTE
# -------------------------------
st.markdown("## 🗺️ Plan cadastral")

m = folium.Map(location=[46.22, 4.42], zoom_start=14, tiles="CartoDB positron")

# Parcelles (léger)
def style_all(feature):
    return {
        "fillOpacity": 0,
        "color": "#666",
        "weight": 0.5
    }

tooltip = folium.GeoJsonTooltip(
    fields=["section", "numero"],
    aliases=["Section", "N°"]
)

folium.GeoJson(
    geo,
    style_function=style_all,
    tooltip=tooltip
).add_to(m)

# -------------------------------
# 🔎 RECHERCHE
# -------------------------------
st.markdown("## 🔎 Recherche parcelle")

col1, col2 = st.columns(2)
section_input = col1.text_input("Section")
numero_input = col2.text_input("Numéro")

selected_feature = None

if section_input and numero_input:
    for feature in geo["features"]:
        sec = str(feature["properties"]["section"])
        num = str(feature["properties"]["numero"])

        if sec == section_input and num == numero_input:
            selected_feature = feature
            break

# -------------------------------
# 🎯 SURBRILLANCE
# -------------------------------
if selected_feature:

    def style_selected(feature):
        return {
            "fillColor": "red",
            "color": "red",
            "weight": 3,
            "fillOpacity": 0.5
        }

    folium.GeoJson(
        selected_feature,
        style_function=style_selected
    ).add_to(m)

    coords = selected_feature["geometry"]["coordinates"][0]
    lats = [p[1] for p in coords]
    lons = [p[0] for p in coords]

    m.location = [sum(lats)/len(lats), sum(lons)/len(lons)]
    m.zoom_start = 18

# -------------------------------
# AFFICHAGE
# -------------------------------
st_folium(m, width=1000, height=600)

# -------------------------------
# INFOS
# -------------------------------
if selected_feature:

    st.markdown("## 📍 Informations parcelle")

    section = selected_feature["properties"]["section"]
    numero = selected_feature["properties"]["numero"]

    match = df[
        (df[col_section].astype(str) == str(section)) &
        (df[col_numero].astype(str) == str(numero))
    ]

    if not match.empty:
        row = match.iloc[0]

        st.success("Parcelle trouvée")

        st.markdown(f"""
        👤 **Propriétaire : {row.get(col_prenom, "")} {row.get(col_nom, "")}**  
        📐 Surface : {row.get(col_surface, "")}  
        📍 Adresse : {row.get(col_adresse, "")}  
        🏙️ Commune : {row.get(col_commune, "")}
        """)
    else:
        st.warning("Aucune donnée trouvée")
