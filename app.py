import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="Cadastre", layout="wide")

st.title("🗺️ Cadastre Saint-Igny-de-Vers")

# -------------------------------
# CHARGEMENT DATA
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    return df

df = load_data()

# -------------------------------
# FONCTION POUR TROUVER COLONNES
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
# FILTRES
# -------------------------------
st.markdown("### 🔎 Recherche")

search = st.text_input("Rechercher (nom, parcelle...)")

sections = ["Toutes"]
if col_section:
    sections += sorted(df[col_section].dropna().astype(str).unique())

section_filter = st.selectbox("🧭 Filtrer par section", sections)

# -------------------------------
# FILTRAGE DATA
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
# AFFICHAGE RESULTATS
# -------------------------------
for _, row in res.iterrows():
    prenom = row.get(col_prenom, "")
    nom = row.get(col_nom, "")
    surface = row.get(col_surface, "")
    adresse = row.get(col_adresse, "")
    commune = row.get(col_commune, "")

    st.markdown(f"""
    ---
    👤 **Propriétaire : {prenom} {nom}**  
    📐 Surface : {surface}  
    📍 Adresse : {adresse}  
    🏙️ Commune : {commune}  
    """)

# -------------------------------
# CARTE CADASTRALE
# -------------------------------
st.markdown("## 🗺️ Carte cadastrale")

@st.cache_data
def load_geo():
    with open("parcelles.json", encoding="utf-8") as f:
        return json.load(f)

geo = load_geo()

m = folium.Map(location=[46.2, 4.4], zoom_start=13)

def style(feature):
    return {
        "fillColor": "#3388ff",
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.2,
    }

tooltip = folium.GeoJsonTooltip(
    fields=["section", "numero"],
    aliases=["Section :", "Parcelle :"]
)

folium.GeoJson(
    geo,
    style_function=style,
    tooltip=tooltip
).add_to(m)

map_data = st_folium(m, width=900, height=500)

# -------------------------------
# CLIC SUR PARCELLE
# -------------------------------
if map_data and map_data.get("last_clicked"):

    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    for feature in geo["features"]:
        try:
            coords = feature["geometry"]["coordinates"][0]

            lats = [p[1] for p in coords]
            lons = [p[0] for p in coords]

            if min(lats) <= lat <= max(lats) and min(lons) <= lon <= max(lons):

                section = str(feature["properties"]["section"])
                numero = str(feature["properties"]["numero"])

                st.markdown("### 📍 Parcelle sélectionnée")
                st.write(f"Section : {section}")
                st.write(f"Numéro : {numero}")

                match = df[
                    (df[col_section].astype(str) == section) &
                    (df[col_numero].astype(str) == numero)
                ]

                if not match.empty:
                    row = match.iloc[0]

                    prenom = row.get(col_prenom, "")
                    nom = row.get(col_nom, "")
                    surface = row.get(col_surface, "")
                    adresse = row.get(col_adresse, "")
                    commune = row.get(col_commune, "")

                    st.success("Informations trouvées")

                    st.markdown(f"""
                    👤 **Propriétaire : {prenom} {nom}**  
                    📐 Surface : {surface}  
                    📍 Adresse : {adresse}  
                    🏙️ Commune : {commune}
                    """)

                else:
                    st.warning("Aucune donnée trouvée dans Excel")

                break

        except:
            pass
