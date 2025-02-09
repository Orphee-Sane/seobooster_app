import streamlit as st
import pandas as pd
import json
import re
import requests
from datetime import datetime

# 📌 Function to generate CSV templates
def generate_template(columns):
    return ",".join(columns)

# 📌 Function to clean URLs
def clean_url(url):
    return re.sub(r"https?://(www\.)?clubmed\.[a-z\.]+", "", url)

# 📌 Function to generate JSON ID
def generate_id(locale):
    return datetime.now().strftime("%Y%m%d%H%M") + f"-Replace_seoBoosters-{locale}"

# 📌 Streamlit Interface
def main():
    st.title("Private Club Med SEOBooster JSON Generator")
    st.write("👋 This new app is made by Orpheus to ease the generation of seobooster.")
    st.write("🚀 **Main Updates:** No repetition of the hosted page in the seobooster, locale validation from the input file, etc.")

    # 📝 Download CSV Templates
    st.subheader("📥 Download CSV Templates")
    st.write("ℹ️ **Pro tips:** Ensure URLs contain your locale and all pages you want to update.")
    st.write("ℹ️ **SEO Boosters 0 & 1:** Must contain at least **23 pages**, a title, and labels (anchor text).")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="📄 URLs Template",
            data=generate_template(["url", "locale"]),
            file_name="urls_template.csv",
            mime="text/csv"
        )
    with col2:
        st.download_button(
            label="📄 SEO Booster 0 Template",
            data=generate_template(["label", "url", "title"]),
            file_name="seo_booster_0_template.csv",
            mime="text/csv"
        )
    with col3:
        st.download_button(
            label="📄 SEO Booster 1 Template",
            data=generate_template(["label", "url", "title"]),
            file_name="seo_booster_1_template.csv",
            mime="text/csv"
        )

    # 📝 Upload CSV Files
    st.subheader("📤 Upload your CSV files")
    uploaded_urls = st.file_uploader("📌 Upload URLs CSV file", type="csv")
    uploaded_seo_0 = st.file_uploader("📌 Upload SEO Booster 0 CSV file", type="csv")
    uploaded_seo_1 = st.file_uploader("📌 Upload SEO Booster 1 CSV file", type="csv")

    # 📌 Locale validation
    locale = st.text_input("🌍 Enter locale code (e.g., fr-FR)", "fr-FR")

    if uploaded_urls and uploaded_seo_0 and uploaded_seo_1:
        urls_df = pd.read_csv(uploaded_urls)
        seo_booster_0_df = pd.read_csv(uploaded_seo_0)
        seo_booster_1_df = pd.read_csv(uploaded_seo_1)

        # ✅ Validate locale against the file
        if "locale" in urls_df.columns:
            valid_locales = urls_df["locale"].unique()
            if locale not in valid_locales:
                st.error(f"❌ Locale '{locale}' does not match the uploaded file. Available locales: {', '.join(valid_locales)}")
                return
            else:
                st.success("✅ Locale is valid.")

        # 📌 Generate JSON
        if st.button("🚀 Generate JSON"):
            result = generate_json(urls_df, seo_booster_0_df, seo_booster_1_df, locale)
            st.json(result)

            json_filename = f"seo_boosters_{locale}.json"
            st.download_button(
                label="📥 Download JSON file",
                data=json.dumps(result, indent=2),
                file_name=json_filename,
                mime="application/json"
            )

            # 📌 Instructions after JSON generation
            st.subheader("✅ Next Steps: Send Your SEO Booster Request")
            st.write("📧 **Now, send your input files to the SEO Booster team!**")
            st.write("🚀 Use the following format for your email subject:")

            # 📌 Generate email template dynamically
            country = locale.split("-")[1] if "-" in locale else locale.upper()
            month = datetime.now().strftime("%B")
            topic = "SEO Update"

            email_subject = f"Seobooster request - {country} - {month} - {topic}"
            email_body = f"""
Hello,

Please process the SEO Booster update for the country **{country}**.

📎 **Attached files:**  
- JSON generated via the SEO Booster tool  
- CSV files used for generation  

📌 **Request details:**  
- **Country:** {country}  
- **Month:** {month}  
- **Topic:** {topic}  

Thank you for your support.

Best regards,  
[Your Name]
"""

            st.text_area("📩 Email Template", email_body, height=200)
            st.button("📋 Copy Email", on_click=lambda: st.session_state.update({"email_text": email_body}))

            # 📌 Mailto link
            email_link = f"mailto:seobooster@clubmed.com?subject={email_subject.replace(' ', '%20')}&body={email_body.replace(' ', '%20').replace('\n', '%0A')}"
            st.markdown(f"[📧 Open Email Client]( {email_link} )", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
