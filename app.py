import streamlit as st
import pandas as pd
import json
import re
import requests
from datetime import datetime
import io

# 📌 Function to clean URLs
def clean_url(url):
    return re.sub(r"https?://(www\.)?clubmed\.[a-z\.]+", "", url)

# 📌 Function to get HTTP status of a URL
def get_http_status(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code
    except requests.RequestException:
        return None

# 📌 Function to generate the migration ID
def generate_id(locale):
    return datetime.now().strftime("%Y%m%d%H%M") + f"-Replace_seoBoosters-{locale}"

# 📌 Function to generate JSON for SEO Boosters
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
    title_0 = seo_booster_0_df['title'].iloc[0] if not seo_booster_0_df.empty else "Default Title"

    seo_booster_1 = [
        {"label": row['label'], "url": row['url'], "@metadata": {"type": "#/definitions/textLinkWithRelativeUrlMandatory"}}
        for _, row in seo_booster_1_df.iterrows()
    ]
    title_1 = seo_booster_1_df['title'].iloc[0] if not seo_booster_1_df.empty else "Default Title"

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

# 📌 Function to generate CSV templates
def generate_template(columns):
    df = pd.DataFrame(columns=columns)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

# 📌 Streamlit Interface
def main():
    st.title("SEO Booster JSON Generator")
    st.write("👋 Welcome to the SEO Booster JSON Generator!")

    # 📝 Download CSV Templates
    st.subheader("📥 Download CSV Templates")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="Download URLs Template",
            data=generate_template(["url", "locale"]),
            file_name="urls_template.csv",
            mime="text/csv"
        )
    with col2:
        st.download_button(
            label="Download SEO Booster 0 Template",
            data=generate_template(["label", "url", "title"]),
            file_name="seo_booster_0_template.csv",
            mime="text/csv"
        )
    with col3:
        st.download_button(
            label="Download SEO Booster 1 Template",
            data=generate_template(["label", "url", "title"]),
            file_name="seo_booster_1_template.csv",
            mime="text/csv"
        )

    # 📝 Upload CSV Files
    st.subheader("📤 Upload your CSV files")
    uploaded_urls = st.file_uploader("Upload URLs CSV file", type="csv")
    uploaded_seo_0 = st.file_uploader("Upload SEO Booster 0 CSV file", type="csv")
    uploaded_seo_1 = st.file_uploader("Upload SEO Booster 1 CSV file", type="csv")

    locale = st.text_input("Enter locale code (e.g., fr-FR)", "fr-FR")

    if uploaded_urls and uploaded_seo_0 and uploaded_seo_1:
        urls_df = pd.read_csv(uploaded_urls)
        seo_booster_0_df = pd.read_csv(uploaded_seo_0)
        seo_booster_1_df = pd.read_csv(uploaded_seo_1)

        # Validate locale against the file
        if "locale" in urls_df.columns:
            valid_locales = urls_df["locale"].unique()
            if locale not in valid_locales:
                st.error(f"❌ Locale '{locale}' does not match the uploaded file. Available locales: {', '.join(valid_locales)}")
                return
            else:
                st.success("✅ Locale is valid.")

        if st.button("Generate JSON"):
            result = generate_json(urls_df, seo_booster_0_df, seo_booster_1_df, locale)
            st.json(result)

            json_filename = f"seo_boosters_{locale}.json"
            st.download_button(
                label="Download JSON file",
                data=json.dumps(result, indent=2),
                file_name=json_filename,
                mime="application/json"
            )

if __name__ == "__main__":
    main()
