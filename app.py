import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cadastre St Igny de Vers", layout="wide")

st.title("🔎 Cadastre St Igny de Vers")

df = pd.read_excel("data.xlsx")

recherche = st.text_input("Recherche (nom, parcelle, commune...)")

if recherche:
    res = df[
        df.astype(str).apply(lambda row: row.str.contains(recherche, case=False).any(), axis=1)
    ]
    st.write(f"Résultats : {len(res)}")
    st.dataframe(res)
