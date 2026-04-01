import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="Cadastre PRO", layout="wide")

# -------------------------------
# 🔐 MOT DE PASSE
# -------------------------------
password = st.text_input("🔐 Mot de passe", type="password")

if password != "mafemmeestgeniale":
    st.stop()

st.title("🗺️ Cadastre PRO - Saint-Igny-de-Vers")

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    df.columns = df.columns.str.lower()
    return df

@st.cache_data
def load_geo():
    with open("parcelles.json", encoding="utf-8") as f:
        return json.load(f)

df = load_data()
geo = load_geo()

# -------------------------------
# COLONNES
# -------------------------------
def col(name):
    return [c for c in df.columns if name in c][0]

col_section = col("section")
col_numero = col("numero")
col_nom = col("nom")
col_prenom = col("prenom")
col_surface = col("surface")
col_adresse = col("adresse")
col_commune = col("commune")

# -------------------------------
# 🔎 RECHERCHE INTELLIGENTE
# -------------------------------
st.markdown("## 🔎 Recherche rapide")

search = st.text_input("Tape numéro ou nom (ex: 283 ou Dupont)")

section_input = ""
numero_input = ""

if search:
    res = df[df.astype(str).apply(lambda row: row.str.contains(search, case=False).any(), axis=1)]

    if not res.empty:
        row = res.iloc[0]
        section_input = str(row[col_section]).strip().upper()
        numero_input = str(row[col_numero]).strip()

# -------------------------------
# CARTE
# -------------------------------
st.markdown("## 🗺️ Carte")

center = [46.22, 4.42]
zoom = 14
selected_feature = None

# chercher dans geojson
if section_input and numero_input:
    for f in geo["features"]:
        sec = str(f["properties"]["section"]).strip().upper()
        num = str(f["properties"]["numero"]).strip()

        if sec == section_input and num == numero_input:
            selected_feature = f
            break

# recalcul centre
if selected_feature:
    coords = selected_feature["geometry"]["coordinates"][0]
    lats = [p[1] for p in coords]
    lons = [p[0] for p in coords]

    center = [sum(lats)/len(lats), sum(lons)/len(lons)]
    zoom = 18

# carte IGN
m = folium.Map(location=center, zoom_start=zoom, tiles=None)

folium.TileLayer(
    tiles="https://wxs.ign.fr/essentiels/geoportail/wmts?"
          "SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0"
          "&LAYER=ORTHOIMAGERY.ORTHOPHOTOS"
          "&STYLE=normal&TILEMATRIXSET=PM"
          "&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}"
          "&FORMAT=image/jpeg",
    attr="IGN"
).add_to(m)

# parcelles
def style(feature):
    return {
        "fillOpacity": 0,
        "color": "#444",
        "weight": 1
    }

folium.GeoJson(geo, style_function=style).add_to(m)

# surlignage
if selected_feature:
    folium.GeoJson(
        selected_feature,
        style_function=lambda x: {
            "fillColor": "red",
            "color": "red",
            "weight": 3,
            "fillOpacity": 0.5
        }
    ).add_to(m)

# affichage carte + clic
map_data = st_folium(m, width=1000, height=600)

# -------------------------------
# 👆 CLIC SUR CARTE
# -------------------------------
if map_data and map_data.get("last_clicked"):

    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    for f in geo["features"]:
        coords = f["geometry"]["coordinates"][0]
        lats = [p[1] for p in coords]
        lons = [p[0] for p in coords]

        if min(lats) <= lat <= max(lats) and min(lons) <= lon <= max(lons):
            section_input = str(f["properties"]["section"]).strip().upper()
            numero_input = str(f["properties"]["numero"]).strip()
            break

# -------------------------------
# INFOS
# -------------------------------
if section_input and numero_input:

    st.markdown("## 📍 Informations parcelle")

    match = df[
        (df[col_section].astype(str).str.strip().str.upper() == section_input) &
        (df[col_numero].astype(str).str.strip() == numero_input)
    ]

    if not match.empty:
        row = match.iloc[0]

        st.success(f"Parcelle {section_input} {numero_input}")

        st.markdown(f"""
        👤 **{row[col_prenom]} {row[col_nom]}**  
        📐 Surface : {row[col_surface]}  
        📍 Adresse : {row[col_adresse]}  
        🏙️ Commune : {row[col_commune]}
        """)
    else:
        st.warning("Parcelle non trouvée dans Excel")
