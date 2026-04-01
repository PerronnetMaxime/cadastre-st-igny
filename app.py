import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium

# -------------------------------
# CONFIG + MOT DE PASSE
# -------------------------------
st.set_page_config(page_title="Cadastre", layout="wide")

password = st.text_input("🔐 Mot de passe", type="password")

if password != "mafemmeestgeniale":
    st.warning("Accès sécurisé")
    st.stop()

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
# DETECTION COLONNES
# -------------------------------
def find_col(names):
    for col in df.columns:
        for name in names:
            if name.lower() in col.lower():
                return col
    return None

col_section = find_col(["section"])
col_numero = find_col(["numero", "num"])
col_nom = find_col(["nom"])
col_prenom = find_col(["prenom"])
col_surface = find_col(["surface"])
col_adresse = find_col(["adresse"])
col_commune = find_col(["commune"])

# -------------------------------
# 🗺️ CARTE GLOBALE (TOUTES PARCELLES)
# -------------------------------
st.markdown("## 🗺️ Plan cadastral")

m = folium.Map(location=[46.2, 4.4], zoom_start=13)

# Affichage avec numéros comme Géoportail
for feature in geo["features"]:
    try:
        coords = feature["geometry"]["coordinates"][0]
        section = feature["properties"]["section"]
        numero = feature["properties"]["numero"]

        # centre parcelle
        lat = sum([p[1] for p in coords]) / len(coords)
        lon = sum([p[0] for p in coords]) / len(coords)

        # contour
        folium.Polygon(
            locations=[(p[1], p[0]) for p in coords],
            color="black",
            weight=1,
            fill=False
        ).add_to(m)

        # numéro au centre
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f"""
                <div style="font-size:8px;color:black;">
                    {numero}
                </div>
            """)
        ).add_to(m)

    except:
        pass

st_folium(m, width=900, height=500)

# -------------------------------
# 🔎 RECHERCHE
# -------------------------------
st.markdown("## 🔎 Recherche parcelle")

section_input = st.text_input("Section (ex: AB)")
numero_input = st.text_input("Numéro (ex: 283)")

# -------------------------------
# RESULTAT + CARTE ZOOM
# -------------------------------
if section_input and numero_input:

    section_input = section_input.upper()

    st.markdown("## 📍 Résultat")

    match = df[
        (df[col_section].astype(str) == section_input) &
        (df[col_numero].astype(str) == numero_input)
    ]

    if not match.empty:
        row = match.iloc[0]

        st.success("Parcelle trouvée")

        st.markdown(f"""
        👤 **Propriétaire : {row.get(col_prenom, '')} {row.get(col_nom, '')}**  
        📐 Surface : {row.get(col_surface, '')}  
        📍 Adresse : {row.get(col_adresse, '')}  
        🏙️ Commune : {row.get(col_commune, '')}
        """)

    else:
        st.warning("Aucune donnée trouvée")

    # -------------------------------
    # CARTE ZOOM + SURBRILLANCE
    # -------------------------------
    m2 = folium.Map(location=[46.2, 4.4], zoom_start=17)

    def style_function(feature):
        section = str(feature["properties"]["section"])
        numero = str(feature["properties"]["numero"])

        if section == section_input and numero == numero_input:
            return {
                "fillColor": "red",
                "color": "red",
                "weight": 3,
                "fillOpacity": 0.6,
            }
        else:
            return {
                "fillColor": "#3388ff",
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.05,
            }

    # centrage sur parcelle
    center = [46.2, 4.4]

    for feature in geo["features"]:
        if (str(feature["properties"]["section"]) == section_input and
            str(feature["properties"]["numero"]) == numero_input):

            coords = feature["geometry"]["coordinates"][0]
            lats = [p[1] for p in coords]
            lons = [p[0] for p in coords]

            center = [sum(lats)/len(lats), sum(lons)/len(lons)]
            break

    m2 = folium.Map(location=center, zoom_start=18)

    folium.GeoJson(
        geo,
        style_function=style_function
    ).add_to(m2)

    st_folium(m2, width=900, height=500)
