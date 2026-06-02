import streamlit as st
import pandas as pd
from scrapers.wikipedia import scrape
from pipeline.cleaner import clean
from pipeline.validator import validate
from pipeline.versioning import save_and_version

# ============================================================
# CONFIGURATION DE LA PAGE
# Doit être la première commande Streamlit dans le fichier
# ============================================================
st.set_page_config(
    page_title="Data Pipeline",
    page_icon="🔬",
    layout="wide",                    # utilise toute la largeur
    initial_sidebar_state="expanded"  # sidebar ouverte par défaut
)

# ============================================================
# THEME SOMBRE — CSS personnalisé
# st.markdown avec unsafe_allow_html permet d'injecter du CSS
# ============================================================
st.markdown("""
    <style>
        /* Fond principal */
        .stApp { background-color: #0e1117; color: #fafafa; }
        
        /* Boîte de succès personnalisée */
        .success-box {
            background-color: #1a3a2a;
            border-left: 4px solid #00c853;
            padding: 1rem;
            border-radius: 4px;
            margin: 0.5rem 0;
        }
        
        /* Boîte d'erreur personnalisée */
        .error-box {
            background-color: #3a1a1a;
            border-left: 4px solid #ff5252;
            padding: 1rem;
            border-radius: 4px;
            margin: 0.5rem 0;
        }
        
        /* Boîte d'info personnalisée */
        .info-box {
            background-color: #1a2a3a;
            border-left: 4px solid #2196f3;
            padding: 1rem;
            border-radius: 4px;
            margin: 0.5rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR — Panneau latéral
# Contient les paramètres de la pipeline
# ============================================================
with st.sidebar:
    st.title("⚙️ Paramètres")
    st.divider()
    
    # Sélection de la source de données
    # selectbox = menu déroulant
    source = st.selectbox(
        "Source de données",
        ["Wikipedia", "Showlabs.tv"],
        help="Choisir la source à scraper"
    )
    
    st.divider()
    
    # Nom du sujet — saisi manuellement par l'utilisateur
    # C'est le nom qu'on passera à save_and_version()
    subject = st.text_input(
        "Nom du sujet",
        placeholder="ex: population, cinema...",
        help="Ce nom sera utilisé pour nommer le fichier CSV"
    )
    
    st.divider()
    
    # Colonnes à supprimer — optionnel
    # text_area = zone de texte multiligne
    colonnes_input = st.text_area(
        "Colonnes à supprimer (optionnel)",
        placeholder="Une colonne par ligne...",
        help="Les colonnes inutiles à supprimer du dataset"
    )
    
    # Convertir le texte en liste de colonnes
    # "Source\nNotes" → ["Source", "Notes"]
    colonnes_inutiles = [
        col.strip() 
        for col in colonnes_input.split("\n") 
        if col.strip()
    ]

# ============================================================
# CONTENU PRINCIPAL
# ============================================================
st.title("🔬 Data Cleaning Pipeline")
st.caption("Scrape, nettoie et exporte des données en CSV propre")
st.divider()

# ============================================================
# SAISIE DE L'URL
# ============================================================
url = st.text_input(
    "🌐 URL à scraper",
    placeholder="https://en.wikipedia.org/wiki/...",
    help="Colle ici l'URL de la page à scraper"
)

# Exemples d'URLs cliquables
st.caption("Exemples :")
col1, col2, col3 = st.columns(3)

# st.columns() divise la page en colonnes
# Chaque bouton remplit l'URL automatiquement
with col1:
    if st.button("🌍 Population mondiale"):
        url = "https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population"

with col2:
    if st.button("💹 PIB par pays"):
        url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"

with col3:
    if st.button("❤️ Espérance de vie"):
        url = "https://en.wikipedia.org/wiki/List_of_countries_by_life_expectancy"

st.divider()

# ============================================================
# BOUTON DE LANCEMENT
# ============================================================
# st.button retourne True quand on clique dessus
lancer = st.button("🚀 Lancer la pipeline", type="primary", use_container_width=True)

# ============================================================
# EXECUTION DE LA PIPELINE
# On entre dans ce bloc uniquement si l'utilisateur a cliqué
# ============================================================
if lancer:
    
    # Vérifications avant de lancer
    if not url:
        st.error("❌ Veuillez entrer une URL")
        st.stop()  # arrête l'exécution
    
    if not subject:
        st.error("❌ Veuillez entrer un nom de sujet")
        st.stop()
    
    # --------------------------------------------------------
    # ÉTAPE 1 — SCRAPING
    # st.status() crée un bloc expansible avec un statut
    # --------------------------------------------------------
    with st.status("📡 Étape 1 — Scraping en cours...", expanded=True) as status:
        try:
            st.write("🔄 Connexion à la page...")
            df_brut = scrape(url)
            st.write(f"✅ {len(df_brut)} lignes extraites")
            st.write(f"✅ {len(df_brut.columns)} colonnes trouvées : {list(df_brut.columns)}")
            status.update(label="✅ Étape 1 — Scraping terminé", state="complete")
        except Exception as e:
            status.update(label="❌ Étape 1 — Scraping échoué", state="error")
            st.error(f"Erreur : {e}")
            st.stop()
    
    # --------------------------------------------------------
    # ÉTAPE 2 — NETTOYAGE
    # --------------------------------------------------------
    with st.status("🧹 Étape 2 — Nettoyage en cours...", expanded=True) as status:
        try:
            st.write("🔄 Suppression des colonnes inutiles...")
            st.write("🔄 Suppression des références [1], [b]...")
            st.write("🔄 Nettoyage des types de données...")
            df_propre = clean(df_brut, colonnes_inutiles)
            st.write(f"✅ Dataset nettoyé : {len(df_propre)} lignes × {len(df_propre.columns)} colonnes")
            status.update(label="✅ Étape 2 — Nettoyage terminé", state="complete")
        except Exception as e:
            status.update(label="❌ Étape 2 — Nettoyage échoué", state="error")
            st.error(f"Erreur : {e}")
            st.stop()
    
    # --------------------------------------------------------
    # ÉTAPE 3 — VALIDATION (DQV)
    # --------------------------------------------------------
    with st.status("✅ Étape 3 — Validation en cours...", expanded=True) as status:
        
        # On réimplémente les checks ici pour afficher
        # les résultats visuellement dans Streamlit
        from pipeline.validator import (
            check_no_empty_country,
            check_positive_population,
            check_percentage_range,
            check_missing_values,
            check_no_duplicates
        )
        
        checks = [
            check_no_empty_country(df_propre),
            check_positive_population(df_propre),
            check_percentage_range(df_propre),
            check_missing_values(df_propre),
            check_no_duplicates(df_propre)
        ]
        
        # Afficher chaque résultat
        for check in checks:
            st.write(check["message"])
        
        # Verdict final
        accepted = all(check["success"] for check in checks)
        
        if accepted:
            status.update(label="✅ Étape 3 — Dataset accepté", state="complete")
        else:
            status.update(label="❌ Étape 3 — Dataset rejeté", state="error")
            st.stop()
    
    # --------------------------------------------------------
    # ÉTAPE 4 — VERSIONING (DVC)
    # --------------------------------------------------------
    with st.status("📦 Étape 4 — Versioning en cours...", expanded=True) as status:
        try:
            filepath, version = save_and_version(df_propre, subject=subject)
            st.write(f"✅ Fichier sauvegardé : {filepath}")
            st.write(f"✅ Version créée : {version}")
            status.update(label=f"✅ Étape 4 — Version {version} créée", state="complete")
        except Exception as e:
            status.update(label="❌ Étape 4 — Versioning échoué", state="error")
            st.error(f"Erreur : {e}")
            st.stop()
    
    # --------------------------------------------------------
    # RÉSULTATS FINAUX
    # --------------------------------------------------------
    st.divider()
    st.success(f"🎉 Pipeline terminée avec succès — Version {version}")
    
    # Métriques principales
    # st.metric() affiche une valeur avec un label
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Lignes", len(df_propre))
    with col2:
        st.metric("📋 Colonnes", len(df_propre.columns))
    with col3:
        st.metric("🏷️ Version", version)
    with col4:
        st.metric("✅ Checks qualité", f"{sum(c['success'] for c in checks)}/{len(checks)}")
    
    # Aperçu du dataset
    st.subheader("👁️ Aperçu des données nettoyées")
    st.dataframe(df_propre, use_container_width=True)
    
    # Bouton de téléchargement CSV
    # df.to_csv() convertit le DataFrame en texte CSV
    st.download_button(
        label="⬇️ Télécharger le CSV",
        data=df_propre.to_csv(index=False).encode("utf-8"),
        file_name=f"{subject}_{version}.csv",
        mime="text/csv",
        use_container_width=True
    )