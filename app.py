import streamlit as st
import pandas as pd
import json
import re
import requests
from datetime import datetime

# 📌 Fonction pour nettoyer les URLs
def clean_url(url):
    return re.sub(r"https?://(www\.)?clubmed\.[a-z\.]+", "", url)

# 📌 Fonction pour obtenir la réponse HTTP d'une URL
def get_http_status(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code
    except requests.RequestException:
        return None

# 📌 Fonction pour générer l'ID
def generate_id(locale):
    return datetime.now().strftime("%Y%m%d%H%M") + f"-Replace_seoBoosters-{locale}"

# 📌 Fonction principale pour générer le JSON
def generate_json(urls_df, seo_booster_0_df, seo_booster_1_df, locale):
    urls_df['status_code'] = urls_df['url'].apply(get_http_status)
    seo_booster_0_df['status_code'] = seo_booster_0_df['url'].apply(get_http_status)
    seo_booster_1_df['status_code'] = seo_booster_1_df['url'].apply(get_http_status)

    urls_df = urls_df[urls_df['status_code'] == 200]
    seo_booster_0_df = seo_booster_0_df[seo_booster_0_df['status_code'] == 200]
    seo_booster_1_df = seo_booster_1_df[seo_booster_1_df['status_code'] == 200]

    urls_df['url'] = urls_df['url'].apply(clean_url)
    seo_booster_0_df['url'] = seo_booster_0_df['url'].apply(clean_url)
    seo_booster_1_df['url'] = seo_booster_1_df['url'].apply(clean_url)

    seo_booster_0 = [
        {"label": row['label'], "url": row['url'], "@metadata": {"type": "#/definitions/textLinkWithRelativeUrlMandatory"}}
        for _, row in seo_booster_0_df.iterrows()
    ]
    title_0 = seo_booster_0_df['title'].iloc[0] if not seo_booster_0_df.empty else "Titre par défaut"

    seo_booster_1 = [
        {"label": row['label'], "url": row['url'], "@metadata": {"type": "#/definitions/textLinkWithRelativeUrlMandatory"}}
        for _, row in seo_booster_1_df.iterrows()
    ]
    title_1 = seo_booster_1_df['title'].iloc[0] if not seo_booster_1_df.empty else "Titre par défaut"

    migrations = []
    for _, row in urls_df.iterrows():
        page_url = row['url']

        seo_links_0 = [link for link in seo_booster_0 if link['url'] != page_url]
        seo_links_1 = [link for link in seo_booster_1 if link['url'] != page_url]

        migration = {
            "$iterate": {
                "filters": [
                    {"has": "pages"},
                    {"match": {"property": "url", "value": page_url}},
                    {"has": "components"},
                    {"has": "seoBoosters"}
                ],
                "$migrate": [
                    {"op": "replace", "path": "props.seoBoosters.0.title", "value": title_0},
                    {"op": "replace", "path": "props.seoBoosters.0.links", "value": seo_links_0},
                    {"op": "replace", "path": "props.seoBoosters.1.title", "value": title_1},
                    {"op": "replace", "path": "props.seoBoosters.1.links", "value": seo_links_1},
                    {"op": "replace", "path": "referenceName", "value": ""}
                ]
            }
        }

        migrations.append(migration)

    output_json = {
        "id": generate_id(locale),
        "locales": [locale],
        "migrations": migrations,
        "contentId": "dcx"
    }

    return output_json

# 📌 Interface utilisateur Streamlit
def main():
    st.title("Générateur de JSON pour SEO Boosters")
    st.write("👋 Bienvenue dans l'outil de génération de JSON pour les SEO Boosters !")

    # 📝 Téléchargez vos fichiers CSV
    uploaded_urls = st.file_uploader("Téléchargez le fichier CSV des URLs", type="csv")
    uploaded_seo_0 = st.file_uploader("Téléchargez le fichier CSV de SEO Booster 0", type="csv")
    uploaded_seo_1 = st.file_uploader("Téléchargez le fichier CSV de SEO Booster 1", type="csv")

    if uploaded_urls and uploaded_seo_0 and uploaded_seo_1:
        urls_df = pd.read_csv(uploaded_urls)
        seo_booster_0_df = pd.read_csv(uploaded_seo_0)
        seo_booster_1_df = pd.read_csv(uploaded_seo_1)

        locale = st.text_input("Entrez le code de locale (ex: fr-FR)", "fr-FR")

        if st.button("Générer le JSON"):
            result = generate_json(urls_df, seo_booster_0_df, seo_booster_1_df, locale)
            st.json(result)

            json_filename = f"seo_boosters_{locale}.json"
            with open(json_filename, 'w') as f:
                json.dump(result, f, indent=2)

            st.download_button(
                label="Téléchargez le fichier JSON",
                data=json.dumps(result, indent=2),
                file_name=json_filename,
                mime="application/json"
            )

if __name__ == "__main__":
    main()
