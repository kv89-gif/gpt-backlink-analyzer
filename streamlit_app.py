# streamlit_app.py
import streamlit as st
import pandas as pd
from urllib.parse import urlparse
import re

# Streamlit app UI
st.title("🔍 Backlink Opportunity Checker (Smarter Spam Detection, No API)")

st.sidebar.header("Input Details")
competitor_file = st.sidebar.file_uploader("Upload Competitor Backlinks (CSV with URL column)", type=['csv'], key="comp")
client_file = st.sidebar.file_uploader("Upload Client Backlinks (CSV with URL column)", type=['csv'], key="client")

# Advanced spam detection

def is_spammy(url):
    domain = urlparse(url).netloc.lower()
    path = urlparse(url).path.lower()
    full_url = url.lower()

    spammy_patterns = [".xyz", ".info", "free", "cheap", "casino", "adult", "loan", ".buzz", ".top", ".click", ".work", ".space", ".online", ".cam"]
    spammy_cc_tlds = [".ru", ".cn", ".tk", ".ml", ".ga", ".cf", ".ua", ".art"]
    known_bad_keywords = ["download", "hack", "crack", "bet", "porno", "spyware", "txtpad"]
    known_bad_domains = ["blogspot.com", "weebly.com", "000webhostapp.com", "x10host.com"]

    reasons = []

    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain):
        reasons.append("IP address used as domain")
    if any(pattern in domain for pattern in spammy_patterns):
        reasons.append("Domain contains common spammy keyword or TLD")
    if any(domain.endswith(tld) for tld in spammy_cc_tlds):
        reasons.append("Suspicious country-code TLD")
    if any(domain.endswith(bad) or bad in domain for bad in known_bad_domains):
        reasons.append("Low-quality hosting or free subdomain")
    if any(keyword in path or keyword in full_url for keyword in known_bad_keywords):
        reasons.append("URL contains spam-related keywords")
    if len(path.split("/")) > 6:
        reasons.append("URL path is very deep")
    if re.search(r"[\u0400-\u04FF]+", path):
        reasons.append("Cyrillic characters in URL")
    if re.search(r"[0-9]{4,}", domain):
        reasons.append("Domain includes excessive numbers")
    if re.match(r"^\d+\.", domain):
        reasons.append("Domain starts with numeric subdomain")

    is_flagged = len(reasons) > 0
    return is_flagged, "; ".join(reasons)

if competitor_file and client_file:
    st.subheader("Unique Backlink Opportunities for Client")

    comp_df = pd.read_csv(competitor_file)
    client_df = pd.read_csv(client_file)

    comp_df.columns = [col.strip().lower() for col in comp_df.columns]
    client_df.columns = [col.strip().lower() for col in client_df.columns]

    if 'url' not in comp_df.columns or 'url' not in client_df.columns:
        st.error("Both files must contain a column named 'URL'.")
    else:
        comp_urls = set(comp_df['url'].dropna().str.strip().str.lower())
        client_urls = set(client_df['url'].dropna().str.strip().str.lower())

        unique_urls = sorted(list(comp_urls - client_urls))

        if unique_urls:
            st.success(f"Found {len(unique_urls)} unique opportunities not yet used by client.")

            results = []
            for url in unique_urls:
                spammy, reason = is_spammy(url)
                tag = "Spammy" if spammy else "Likely Good"
                results.append({"URL": url, "Status": tag, "Reason": reason})

            result_df = pd.DataFrame(results)
            st.dataframe(result_df)
            st.download_button("Download Opportunities", data=result_df.to_csv(index=False), file_name="backlink_opportunities.csv")
        else:
            st.info("No unique opportunities found. The client already has all competitor links.")
else:
    st.info("Please upload both the competitor and client backlink CSV files.")
