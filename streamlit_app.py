# streamlit_app.py
import streamlit as st
import pandas as pd
from urllib.parse import urlparse

# Streamlit app UI
st.title("🔍 Backlink Opportunity Checker (No GPT, No API Quota)")

st.sidebar.header("Input Details")
competitor_file = st.sidebar.file_uploader("Upload Competitor Backlinks (CSV with URL column)", type=['csv'], key="comp")
client_file = st.sidebar.file_uploader("Upload Client Backlinks (CSV with URL column)", type=['csv'], key="client")

# Simple heuristic to detect spammy domains
def is_spammy(url):
    domain = urlparse(url).netloc.lower()
    spammy_patterns = [".xyz", ".info", "free", "cheap", "casino", "adult", "loan"]
    return any(pattern in domain for pattern in spammy_patterns)

if competitor_file and client_file:
    st.subheader("Unique Backlink Opportunities for Client")

    comp_df = pd.read_csv(competitor_file)
    client_df = pd.read_csv(client_file)

    comp_df.columns = [col.strip().lower() for col in comp_df.columns]
    client_df.columns = [col.strip().lower() for col in client_df.columns]

    if 'url' not in comp_df.columns or 'url' not in client_df.columns:
        st.error("Both files must contain a column named 'URL'.")
    else:
        comp_urls = set(comp_df['url'].str.strip().str.lower())
        client_urls = set(client_df['url'].str.strip().str.lower())

        unique_urls = sorted(list(comp_urls - client_urls))

        if unique_urls:
            st.success(f"Found {len(unique_urls)} unique opportunities not yet used by client.")

            results = []
            for url in unique_urls:
                tag = "Spammy" if is_spammy(url) else "Likely Good"
                results.append({"URL": url, "Status": tag})

            result_df = pd.DataFrame(results)
            st.dataframe(result_df)
            st.download_button("Download Opportunities", data=result_df.to_csv(index=False), file_name="backlink_opportunities.csv")
        else:
            st.info("No unique opportunities found. The client already has all competitor links.")
else:
    st.info("Please upload both the competitor and client backlink CSV files.")
