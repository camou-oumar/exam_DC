
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import os
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt

# =====================================================
# STYLE : background , selectbox et bouttons
# =====================================================
st.markdown(
    """
    <style>
    /* =======================
       BACKGROUND PRINCIPAL
       ======================= */
    .stApp {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6, #93c5fd);
        color: #020617;  /* texte foncé pour contraste */
    }

    /* =========================
       LABELS DES SELECTBOX
       ========================= */
    label[for] {
        color: #020617 !important;   /* labels visibles sur fond clair */
        font-weight: 600;
        font-size: 16px;
    }

    /* =========================
       CONTENEUR DES SELECTBOX
       ========================= */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;  /* fond blanc pour selectbox */
        color: #020617 !important;             /* texte sélectionné */
        border-radius: 8px;
        border: 2px solid #1e40af;
        min-height: 45px;
    }

    div[data-baseweb="select"] span {
        color: #020617 !important;
        font-weight: 600;
    }

    ul[role="listbox"] {
        background-color: #ffffff !important;
        color: #020617 !important;
        border-radius: 8px;
    }

    ul[role="listbox"] li {
        color: #020617 !important;
        font-weight: 500;
    }

    ul[role="listbox"] li:hover {
        background-color: #bfdbfe !important;
    }

    /* =======================
       BOUTONS
       ======================= */
    .stButton > button {
        background-color: #3b82f6;
        color: #ffffff;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        padding: 0.5em 1.5em;
    }

    .stButton > button:hover {
        background-color: #2563eb;
        color: #ffffff;
    }

    /* =======================
       SIDEBAR
       ======================= */
    section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #3b82f6, #60a5fa); /* bleu clair dégradé */
    color: #020617; /* texte noir pour contraste */
}
    </style>
    """,
    unsafe_allow_html=True
)


# =====================================================
# TITRE
# =====================================================
st.title("     << DC APP WEB SCRAPER >>")
st.markdown(
    "<h3 style='text-align:center;'>Application de scraping de données avec BeautifulSoup, "
    "téléchargement CSV, dashboard et formulaire d’évaluation</h3>", unsafe_allow_html=True)

# =====================================================
# SCRAPING
# =====================================================


site = st.selectbox(
    "Sélectionnez un site à scraper",
    (
        "vetements-homme",
        "chaussures-homme",
        "vetements-enfants",
        "chaussures-enfants"
    ),
    key="site_select"
)

urls = {
    "vetements-homme": "https://sn.coinafrique.com/categorie/vetements-homme",
    "chaussures-homme": "https://sn.coinafrique.com/categorie/chaussures-homme",
    "vetements-enfants": "https://sn.coinafrique.com/categorie/vetements-enfants",
    "chaussures-enfants": "https://sn.coinafrique.com/categorie/chaussures-enfants"
}

nbr_page = st.number_input(
    "Nombre de pages à scraper",
    min_value=1,
    max_value=50,
    value=2
)

clic = st.button("Lancer le scraping")

def scrape_data(base_url, nbr_page):
    data = []

    for page in range(1, nbr_page + 1):
        url = f"{base_url}?page={page}"
        res = get(url)
        soup = bs(res.content, "html.parser")

        containers = soup.find_all("div", class_="col s6 m4 l3")

        for container in containers:
            try:
                lien = container.find("a")["href"]
                url_annonce = "https://sn.coinafrique.com" + lien

                res_annonce = get(url_annonce)
                soup_annonce = bs(res_annonce.content, "html.parser")

                types = soup_annonce.find(
                    "h1", class_="title title-ad hide-on-large-and-down"
                ).text.strip()

                prix = soup_annonce.find(
                    "p", class_="price"
                ).text.replace("CFA", "").strip()

                adresse = soup_annonce.find(
                    "span", {"data-address": True}
                )["data-address"]

                image_lien = soup_annonce.find(
                    "div", style=True
                )["style"][20:].strip("()")

                data.append({
                    "types": types,
                    "prix": int(prix.replace(" ", "")),
                    "adresse": adresse,
                    "image_lien": image_lien
                })

            except:
                continue

    return pd.DataFrame(data)

if clic:
    with st.spinner("Scraping en cours..."):
        df = scrape_data(urls[site], nbr_page)

    if not df.empty:
        st.success(f"{len(df)} annonces récupérées")
        st.dataframe(df)

        st.download_button(
            "Télécharger en CSV",
            df.to_csv(index=False),
            file_name=f"{site}.csv",
            mime="text/csv"
        )
    else:
        st.warning("Aucune donnée récupérée")

# =====================================================
# TELECHARGER LES DONNÉES DÉJÀ SCRAPÉES
# =====================================================
st.sidebar.markdown("<h3 style='text-align:center;'>Téléchargement des données déjà scrapées à l'aide de Web Scraper</h3>", unsafe_allow_html=True)


fichiers = {
    "Vêtement-homme": "datas/vetement_homme.csv",
    "Vêtement-enfant": "datas/vetement_enfant.csv",
    "Chausure-homme": "datas/chaussure_enfant.csv",
    "Chaussure-enfant" :"datas/chaussure_homme.csv"
}

fichier_selectionne = st.sidebar.selectbox(
    "Choisir une catégorie",
    list(fichiers.keys())
)

chemin_fichier = fichiers[fichier_selectionne]

if os.path.exists(chemin_fichier):
    df_brut = pd.read_csv(chemin_fichier)

    st.sidebar.download_button(
        "Télécharger le CSV",
        df_brut.to_csv(index=False),
        file_name=os.path.basename(chemin_fichier),
        mime="text/csv"
    )
else:
    st.sidebar.error("Fichier introuvable")

# =====================================================
# DASHBOARD 
# =====================================================
st.subheader("Dashboard des données")

uploaded_file = st.file_uploader(
    "Importez un fichier CSV pour afficher le dashboard",
    type=["csv"],
    key="dashboard_upload"
)

if uploaded_file is not None:
    
    df_dash = pd.read_csv(uploaded_file)

    if not df_dash.empty and "prix" in df_dash.columns and "adresse" in df_dash.columns:

    
        
        # initialisation des colonnes
        col1, col2, col3 = st.columns(3)
        col1.metric(" Nombre d'annonces", len(df_dash))
        col2.metric(" Prix moyen (CFA)", int(df_dash["prix"].mean()))
        col3.metric(" Prix max (CFA)", int(df_dash["prix"].max()))

        #st.markdown("---")

        
        # LES GRAPHIQUES
        
        if "types_habits" in df_dash.columns and "adresse" in df_dash.columns:
    
            st.markdown(" Répartition des types d'habits et des annonces par adresse")

            # Création de deux colonnes
            col1, col2 = st.columns(2)

            # Graphique 1 : Types d'habits
            with col1:
                st.markdown("Types d'habits")
                types_counts = df_dash["types_habits"].value_counts()
                st.bar_chart(types_counts)

            # Graphique 2 : Annonces par adresse
            with col2:
                st.markdown("Nombre d'annonces par adresse ")
                adresse_counts = df_dash["adresse"].value_counts()#.head(10)
                st.bar_chart(adresse_counts)

        else:
            st.info("Les colonnes 'types_habits' et/ou 'adresse' sont manquantes dans le CSV")

            

# =====================================================
# FORMULAIRES 
# =====================================================
st.subheader(" Évaluation de l’application")

formulaire = st.selectbox(
    "Choisissez un formulaire d’évaluation",
    (
        "Sélectionner un formulaire pour soumettre votre feadback",
        "Google Forms",
        "KoboToolbox"
    ),
    key="form_select"
)

if formulaire == "Google Forms":
    components.html(
        """<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSc4t4OQDWswUAWd4N2giY6FYuFgSDFcaD62drgnU1WvCwIYjQ/viewform?usp=publish-editor"
        width="100%" height="800"></iframe>""",
        height=820
    )

elif formulaire == "KoboToolbox":
    components.html(
        """<iframe src="https://ee.kobotoolbox.org/x/cpsZ1jDd"
        width="100%" height="800"></iframe>""",
        height=820
    )


