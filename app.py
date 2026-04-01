import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium

# -------------------------------
# 🔐 MOT DE PASSE
# -------------------------------
st.set_page_config(page_title="Cadastre", layout="wide")

password = st.text_input("🔒 Mot de passe", type="password")

if password != "mafemmeestgeniale":
    st.warning("Accès refusé")
    st.stop()

st.title("🗺️ Cadastre Saint-Igny-de-Vers")

# -------------------------------
# 📊 CHARGEMENT DATA
# -------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("data.xlsx")

df = load_data()

# -------------------------------
# 🔍 TROUVER COLONNES
# -------------------------------
def find_col(names):
    for col in df.columns:
        for name in names:
            if name.lower() in col.lower():
                return col
    return None

col_nom = find_col(["nom"])
col_prenom = find_col(["prenom"])
col_section = find_col(["section"])
col_numero = find_col(["numero", "num"])
col_surface = find_col(["surface", "contenance"])
col_adresse = find_col(["adresse", "rue", "voie"])
col_commune = find_col(["commune", "ville"])

# -------------------------------
# 🔎 FILTRES
# -------------------------------
st.markdown("### 🔎 Recherche")

search = st.text_input("Rechercher (nom, parcelle...)")

sections = ["Toutes"]
if col_section:
    sections += sorted(df[col_section].dropna().astype(str).unique())

section_filter = st.selectbox("🧭 Filtrer par section", sections)

# -------------------------------
# 📂 FILTRAGE
# -------------------------------
res = df.copy()

if search:
    res = res[
        res.astype(str).apply(
            lambda row: row.str.contains(search, case=False).any(),
            axis=1
        )
    ]

if section_filter != "Toutes" and col_section:
    res = res[res[col_section].astype(str) == section_filter]

st.markdown(f"📊 **{len(res)} résultat(s)**")

# -------------------------------
# 📄 RESULTATS
# -------------------------------
selected_section = None
selected_numero = None

for _, row in res.iterrows():
    prenom = row.get(col_prenom, "")
    nom = row.get(col_nom, "")
    surface = row.get(col_surface, "")
    adresse = row.get(col_adresse, "")
    commune = row.get(col_commune, "")

    selected_section = str(row.get(col_section, ""))
    selected_numero = str(row.get(col_numero, ""))

    st.markdown(f"""
    ---
    👤 **Propriétaire : {prenom} {nom}**  
    📐 Surface : {surface}  
    📍 Adresse : {adresse}  
    🏙️ Commune : {commune}  
    """)

# -------------------------------
# 🗺️ CHARGEMENT GEOJSON
# -------------------------------
@st.cache_data
def load_geo():
    with open("parcelles.json", encoding="utf-8") as f:
        return json.load(f)

geo = load_geo()

# -------------------------------
# 🎯 TROUVER PARCELLE
# -------------------------------
selected_feature = None

if selected_section and selected_numero:
    for feature in geo["features"]:
        if (
            str(feature["properties"]["section"]) == selected_section
            and str(feature["properties"]["numero"]) == selected_numero
        ):
            selected_feature = feature
            break

# -------------------------------
# 🗺️ CARTE
# -------------------------------
st.markdown("## 🗺️ Carte cadastrale")

m = folium.Map(tiles="OpenStreetMap")

# style normal
def style_default(feature):
    return {
        "fillColor": "#3388ff",
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.2,
    }

# toutes les parcelles
folium.GeoJson(
    geo,
    style_function=style_default
).add_to(m)

# -------------------------------
# 🔥 ZOOM + SURBRILLANCE
# -------------------------------
if selected_feature:
    coords = selected_feature["geometry"]["coordinates"][0]

    lat_lon = [[p[1], p[0]] for p in coords]

    folium.Polygon(
        locations=lat_lon,
        color="red",
        fill=True,
        fill_opacity=0.6
    ).add_to(m)

    m.fit_bounds(lat_lon)

else:
    m.location = [46.2, 4.4]
    m.zoom_start = 13

# -------------------------------
# 📍 AFFICHAGE
# -------------------------------
st_folium(m, width=900, height=500)
