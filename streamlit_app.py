# streamlit_app.py
import streamlit as st
import pandas as pd
import openai
import time
from openai import OpenAIError

# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# GPT Prompt Template (retained for future use)
def analyze_backlink(client_url, niche, competitor_url):
    pass  # Disabled for comparison-only mode

# Streamlit app UI
st.title("🔍 Backlink Opportunity Extractor")

st.sidebar.header("Input Details")
competitor_file = st.sidebar.file_uploader("Upload Competitor Backlinks (CSV with URL column)", type=['csv'], key="comp")
client_file = st.sidebar.file_uploader("Upload Client Backlinks (CSV with URL column)", type=['csv'], key="client")

if competitor_file and client_file:
    st.subheader("Unique Backlink Opportunities for Client")

    # Read and clean both CSVs
    comp_df = pd.read_csv(competitor_file)
    client_df = pd.read_csv(client_file)
    
    comp_df.columns = [col.strip().lower() for col in comp_df.columns]
    client_df.columns = [col.strip().lower() for col in client_df.columns]

    if 'url' not in comp_df.columns or 'url' not in client_df.columns:
        st.error("Both files must contain a column named 'URL'.")
    else:
        # Normalize and compare URLs
        comp_urls = set(comp_df['url'].str.strip().str.lower())
        client_urls = set(client_df['url'].str.strip().str.lower())

        unique_urls = sorted(list(comp_urls - client_urls))
        
        if unique_urls:
            result_df = pd.DataFrame(unique_urls, columns=['Potential Opportunity URL'])
            st.success(f"Found {len(unique_urls)} unique opportunities not yet used by client.")
            st.dataframe(result_df)
            st.download_button("Download Opportunities", data=result_df.to_csv(index=False), file_name="opportunities.csv")
        else:
            st.info("No unique opportunities found. The client already has all competitor links.")
else:
    st.info("Please upload both the competitor and client backlink CSV files.")
