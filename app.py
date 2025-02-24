import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime
import requests
import pyperclip  # Pour permettre la copie du texte

# 📌 Fonction pour nettoyer les URLs Club Med
def clean_url(url):
    return re.sub(r"https?://(www\.)?clubmed\.[a-z\.]+", "", url)

# 📌 Générer un ID unique pour le fichier JSON
def generate_id(locale):
    return datetime.now().strftime("%Y%m%d%H%M") + f"-Replace_seoBoosters-{locale}"

# 📌 Générer un fichier CSV template
def generate_template(columns):
    df = pd.DataFrame(columns=columns)
    return df.to_csv(index=False).encode("utf-8")

# 📌 Génération dynamique du JSON
def generate_json(urls_df, seo_booster_0_df, seo_booster_1_df, locale):
    urls_df['url'] = urls_df['url'].apply(clean_url)
    seo_booster_0_df['url'] = seo_booster_0_df['url'].apply(clean_url)
    seo_booster_1_df['url'] = seo_booster_1_df['url'].apply(clean_url)

    seo_booster_0 = [{"label": row['label'], "url": row['url'], "@metadata": {"type": "#/definitions/textLinkWithRelativeUrlMandatory"}}
                      for _, row in seo_booster_0_df.iterrows()]
    seo_booster_1 = [{"label": row['label'], "url": row['url'], "@metadata": {"type": "#/definitions/textLinkWithRelativeUrlMandatory"}}
                      for _, row in seo_booster_1_df.iterrows()]

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
                    {"op": "replace", "path": "props.seoBoosters.0.links", "value": seo_links_0},
                    {"op": "replace", "path": "props.seoBoosters.1.links", "value": seo_links_1}
                ]
            }
        }
        migrations.append(migration)

    return {
        "id": generate_id(locale),
        "locales": [locale],
        "migrations": migrations,
        "contentId": "dcx"
    }

# 📌 Interface Streamlit
def main():
    st.title("🔍 Private Club Med SEOBooster Generator")
    st.write("🚀 **This app is made by Orpheus!**")
    st.write("🔹 Updates: **No duplicate hosted pages, locale validation, automatic templates, next steps email template.**")

    # 📥 Télécharger les modèles CSV
    st.subheader("📥 Download CSV Templates")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("URLs Template", generate_template(["url", "locale"]), "urls_template.csv", "text/csv")
    with col2:
        st.download_button("SEO Booster 0 Template", generate_template(["label", "url", "title"]), "seo_booster_0_template.csv", "text/csv")
    with col3:
        st.download_button("SEO Booster 1 Template", generate_template(["label", "url", "title"]), "seo_booster_1_template.csv", "text/csv")

    st.write("ℹ️ **URLs file:** Ensure URLs contain your locale and all pages you want to update.")
    st.write("ℹ️ **SEO Boosters 0 & 1 files:** Must contain at least **23 pages**, a title, and labels (anchor text).")

    # 📤 Upload des fichiers CSV
    st.subheader("📤 Upload CSV Files")
    uploaded_urls = st.file_uploader("Upload URLs CSV file", type="csv")
    uploaded_seo_0 = st.file_uploader("Upload SEO Booster 0 CSV file", type="csv")
    uploaded_seo_1 = st.file_uploader("Upload SEO Booster 1 CSV file", type="csv")

    # 🏷️ Sélection de la locale
    locale = st.text_input("Enter locale code (e.g., fr-FR)", "fr-FR")

    # 🗓️ Ajout de champs dynamiques pour le mois et le sujet
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox("📆 Select Month", [datetime.now().strftime("%B"), "January", "February", "March", "April",
                                                 "May", "June", "July", "August", "September", "October", "November", "December"])
    with col2:
        topic = st.text_input("📝 Enter Topic", "")

    if uploaded_urls and uploaded_seo_0 and uploaded_seo_1:
        urls_df = pd.read_csv(uploaded_urls, encoding="ISO-8859-1")
        seo_booster_0_df = pd.read_csv(uploaded_seo_0)
        seo_booster_1_df = pd.read_csv(uploaded_seo_1)

        # ✅ Validation du locale
        if "locale" in urls_df.columns:
            valid_locales = urls_df["locale"].unique()
            if locale not in valid_locales:
                st.error(f"❌ Locale '{locale}' does not match the uploaded file. Available locales: {', '.join(valid_locales)}")
                return
            else:
                st.success("✅ Locale is valid.")

        # 🚀 Génération du JSON
        if st.button("Generate JSON"):
            result = generate_json(urls_df, seo_booster_0_df, seo_booster_1_df, locale)
            st.json(result)

            json_filename = f"seo_boosters_{locale}.json"
            st.download_button("Download JSON file", json.dumps(result, indent=2), json_filename, "application/json")

            # 📩 Génération dynamique de l'email
            if topic:
                email_subject = f"SEO Booster Request - {locale} - {month} - {topic}"
                email_body = f"""
                Subject: {email_subject}

                Hello Team,

                Please find attached the JSON file for the SEO Booster update.

                - **Locale**: {locale}
                - **Month**: {month}
                - **Topic**: {topic}
                - **Generated on**: {datetime.now().strftime('%Y-%m-%d')}
                
                Let me know if you need any adjustments.

                Best regards,
                [Your Name]
                """
                st.subheader("📧 Email Template")
                st.text_area("📩 Copy & Paste this email:", email_body, height=150)

                if st.button("📋 Copy Email to Clipboard"):
                    pyperclip.copy(email_body)
                    st.success("📎 Email copied to clipboard!")

if __name__ == "__main__":
    main()
