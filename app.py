import streamlit as st
import pandas as pd
import json
import re
import requests
from datetime import datetime
#from google.colab import drive

st.title("Générateur de JSON pour SEO Boosters")

# Télécharger les fichiers CSV
uploaded_urls = st.file_uploader("Uploader le fichier des URLs", type=["csv"])
uploaded_seo_0 = st.file_uploader("Uploader le fichier SEO Boosters 0", type=["csv"])
uploaded_seo_1 = st.file_uploader("Uploader le fichier SEO Boosters 1", type=["csv"])

if uploaded_urls and uploaded_seo_0 and uploaded_seo_1:
    urls_df = pd.read_csv(uploaded_urls)
    seo_booster_0_df = pd.read_csv(uploaded_seo_0)
    seo_booster_1_df = pd.read_csv(uploaded_seo_1)

    st.success("Fichiers chargés avec succès !")
    
    # Ajoute ici ton code pour transformer les données en JSON
else:
    st.warning("Veuillez uploader tous les fichiers pour continuer.")


# 📌 Fonction améliorée pour supprimer toutes les extensions de clubmed
def clean_url(url):
    return re.sub(r"https?://(www\.)?clubmed\.[a-z\.]+", "", url)

# 📌 Fonction pour obtenir la réponse HTTP d'une URL
def get_http_status(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code
    except requests.RequestException:
        return None  # En cas d'erreur, retourner None

# 📌 Fonction pour générer l'ID avec la date du jour
def generate_id(locale):
    return datetime.now().strftime("%Y%m%d%H%M") + f"-Replace_seoBoosters-{locale}"

# 📌 Fonction pour charger et vérifier les fichiers CSV
#def load_csv_files():
#    urls_df = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/SEO Booster - Club Med/urls.csv")
#    seo_booster_0_df = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/SEO Booster - Club Med/seoBoosters.0.csv")
#    seo_booster_1_df = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/SEO Booster - Club Med/seoBoosters.1.csv")
#    
#    return urls_df, seo_booster_0_df, seo_booster_1_df

# 📌 Fonction principale pour générer le JSON
def generate_json(urls_df, seo_booster_0_df, seo_booster_1_df, locale):
    # 🔹 Vérification HTTP des URLs
    urls_df['status_code'] = urls_df['url'].apply(get_http_status)
    seo_booster_0_df['status_code'] = seo_booster_0_df['url'].apply(get_http_status)
    seo_booster_1_df['status_code'] = seo_booster_1_df['url'].apply(get_http_status)
    
    # 🔹 Filtrer les URLs valides
    urls_df = urls_df[urls_df['status_code'] == 200]
    seo_booster_0_df = seo_booster_0_df[seo_booster_0_df['status_code'] == 200]
    seo_booster_1_df = seo_booster_1_df[seo_booster_1_df['status_code'] == 200]
    
    # 🔹 Nettoyer les URLs pour enlever le domaine
    urls_df['url'] = urls_df['url'].apply(clean_url)
    seo_booster_0_df['url'] = seo_booster_0_df['url'].apply(clean_url)
    seo_booster_1_df['url'] = seo_booster_1_df['url'].apply(clean_url)

    # 🔹 Construire la liste des SEO Boosters 0 avec leurs titres
    seo_booster_0 = [
        {
            "label": row['label'],
            "url": row['url'],
            "@metadata": {
                "type": "#/definitions/textLinkWithRelativeUrlMandatory"
            }
        }
        for _, row in seo_booster_0_df.iterrows()
    ]
    title_0 = seo_booster_0_df['title'].iloc[0] if not seo_booster_0_df.empty else "Titre par défaut"

    # 🔹 Construire la liste des SEO Boosters 1 avec leurs titres
    seo_booster_1 = [
        {
            "label": row['label'],
            "url": row['url'],
            "@metadata": {
                "type": "#/definitions/textLinkWithRelativeUrlMandatory"
            }
        }
        for _, row in seo_booster_1_df.iterrows()
    ]
    title_1 = seo_booster_1_df['title'].iloc[0] if not seo_booster_1_df.empty else "Titre par défaut"

    # 🔹 Filtrer les pages qui ne doivent pas être dans leur propre SEO Booster
    excluded_urls_0 = seo_booster_0_df['url'].tolist()  # Exclure les URLs qui sont dans seoBooster 0
    excluded_urls_1 = seo_booster_1_df['url'].tolist()  # Exclure les URLs qui sont dans seoBooster 1

    # 🔹 Construire la structure JSON
    migrations = []
    for _, row in urls_df.iterrows():
        page_url = row['url']

        # Exclure la page si elle est déjà dans son propre SEO Booster
        seo_links_0 = [link for link in seo_booster_0 if link['url'] != page_url]  # Exclure de seoBooster 0
        seo_links_1 = [link for link in seo_booster_1 if link['url'] != page_url]  # Exclure de seoBooster 1

        migration = {
            "$iterate": {
                "filters": [
                    {"has": "pages"},
                    {"match": {"property": "url", "value": page_url}},
                    {"has": "components"},
                    {"has": "seoBoosters"}
                ],
                "$migrate": [
                    {
                        "op": "replace",
                        "path": "props.seoBoosters.0.title",
                        "value": title_0
                    },
                    {
                        "op": "replace",
                        "path": "props.seoBoosters.0.links",
                        "value": seo_links_0
                    },
                    {
                        "op": "replace",
                        "path": "props.seoBoosters.1.title",
                        "value": title_1
                    },
                    {
                        "op": "replace",
                        "path": "props.seoBoosters.1.links",
                        "value": seo_links_1
                    },
                    {
                        "op": "replace",
                        "path": "referenceName",
                        "value": ""
                    }
                ]
            }
        }
        
        migrations.append(migration)

    # 🔹 Générer le JSON final
    output_json = {
        "id": generate_id(locale),
        "locales": [locale],
        "migrations": migrations,
        "contentId": "dcx"
    }

    return output_json

# 📌 Interface utilisateur Streamlit
def main():
    st.title('SEO Booster JSON Generator')
    
    st.write("👋 Bienvenue dans l'outil de génération de JSON pour les SEO Boosters !")
    
    # 📝 Téléchargez vos fichiers CSV
    uploaded_file_urls = st.file_uploader("Téléchargez le fichier CSV des URLs", type="csv")
    uploaded_file_seo_0 = st.file_uploader("Téléchargez le fichier CSV de SEO Booster 0", type="csv")
    uploaded_file_seo_1 = st.file_uploader("Téléchargez le fichier CSV de SEO Booster 1", type="csv")
    
    if uploaded_file_urls and uploaded_file_seo_0 and uploaded_file_seo_1:
        # Lire les CSVs
        urls_df = pd.read_csv(uploaded_file_urls)
        seo_booster_0_df = pd.read_csv(uploaded_file_seo_0)
        seo_booster_1_df = pd.read_csv(uploaded_file_seo_1)
        
        # Choisir la locale
        locale = st.text_input("Entrez le code de locale (ex: fr-FR)", "fr-FR")
        
        # Générer le JSON
        if st.button("Générer le JSON"):
            result = generate_json(urls_df, seo_booster_0_df, seo_booster_1_df, locale)
            st.json(result)

            # Sauvegarder le fichier JSON
            json_filename = f"seo_boosters_{locale}.json"
            with open(json_filename, 'w') as f:
                json.dump(result, f, indent=2)

            st.download_button(
                label="Téléchargez le fichier JSON",
                data=json_filename,
                file_name=json_filename,
                mime="application/json"
            )

if __name__ == "__main__":
    main()
