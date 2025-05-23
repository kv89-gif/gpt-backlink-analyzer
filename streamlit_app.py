# streamlit_app.py
import streamlit as st
import pandas as pd
from urllib.parse import urlparse
import re

# Streamlit app UI
st.title("🔍 Backlink Opportunity Checker")

st.sidebar.header("Input Details")
competitor_file = st.sidebar.file_uploader("Upload Competitor Backlinks (CSV with URL column)", type=['csv'], key="comp")
client_file = st.sidebar.file_uploader("Upload Client Backlinks (CSV with URL column)", type=['csv'], key="client")

# Check if a domain is an IP address
def is_ip_address(domain):
    try:
        return re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", domain) is not None
    except:
        return False

# Extract root domain, including handling IPs
def extract_root_domain(domain):
    if is_ip_address(domain):
        return domain
    parts = domain.split('.')
    if len(parts) >= 2:
        return '.'.join(parts[-2:])
    return domain

# Spam detection logic
def is_spammy(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower().split(':')[0].strip()  # Remove port if exists
    root_domain = extract_root_domain(domain)
    path = parsed.path.lower()
    full_url = url.lower()

    # Optional debug
    # print(f"Parsed domain: {domain}")

    spammy_patterns = [".xyz", ".info", ".icu", ".buzz", ".top", ".click", ".work", ".space", ".online", ".cam", "free", "cheap", "casino", "adult", "loan", "offer", "deal", "bonus"]
    spammy_cc_tlds = [".ru", ".cn", ".tk", ".ml", ".ga", ".cf", ".ua", ".art", ".pw"]
    known_bad_keywords = ["download", "hack", "crack", "bet", "porno", "spyware", "txtpad", "seo", "backlink", "referral"]
    known_bad_domains = ["blogspot.com", "weebly.com", "000webhostapp.com", "x10host.com", "wordpress.com", "wixsite.com"]

    reasons = []

    if is_ip_address(domain):
        reasons.append("IP address used as domain")
    if any(pattern in root_domain for pattern in spammy_patterns):
        reasons.append("Domain contains spammy keyword or TLD")
    if any(root_domain.endswith(tld) for tld in spammy_cc_tlds):
        reasons.append("Suspicious country-code TLD")
    if root_domain.endswith(".cn") or ".cn/" in full_url:
        reasons.append("Chinese domain or path pattern")
    if any(root_domain.endswith(bad) or bad in root_domain for bad in known_bad_domains):
        reasons.append("Low-quality or free hosting provider")
    if re.match(r"^\d+", domain.split(".")[0]):
        reasons.append("Subdomain starts with a number")
    if re.search(r"[0-9]{4,}", root_domain):
        reasons.append("Excessive numbers in domain name")
    if any(keyword in path or keyword in full_url for keyword in known_bad_keywords):
        reasons.append("Suspicious keyword in path or URL")
    if re.search(r"[\u0400-\u04FF]+", path):
        reasons.append("Cyrillic characters in URL")
    if len(root_domain.split(".")) > 3:
        reasons.append("Nested subdomain or excessive domain depth")

    is_flagged = len(reasons) > 0
    return is_flagged, "; ".join(reasons)

# Main logic
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
