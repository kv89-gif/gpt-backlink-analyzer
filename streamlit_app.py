# streamlit_app.py
import streamlit as st
import pandas as pd
import openai

# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# GPT Prompt Template
def analyze_backlink(client_url, niche, competitor_url):
    prompt = f"""
    You are an SEO analyst.

    Client website: {client_url}
    Niche: {niche}

    Analyze competitor backlink: {competitor_url}

    Provide:
    1. Relevance (High/Medium/Low)
    2. Quality (High/Medium/Low)
    3. Ease (Easy/Moderate/Difficult)
    4. Recommendation

    Format response as:
    Relevance: <value>\nQuality: <value>\nEase: <value>\nRecommendation: <text>
    """

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.3
    )
    return response.choices[0].message.content

# Streamlit app UI
st.title("🔍 GPT-Powered Backlink Analyzer")

st.sidebar.header("Input Details")
client_url = st.sidebar.text_input("Your Client's URL")
niche = st.sidebar.text_input("Your Client's Niche")
uploaded_file = st.sidebar.file_uploader("Upload Competitor Backlinks (CSV)", type=['csv'])

if uploaded_file and client_url and niche:
    df = pd.read_csv(uploaded_file)
    st.subheader("Competitor Backlink Analysis")

    # Normalize column names to lowercase for flexibility
    df.columns = [col.strip().lower() for col in df.columns]

    if 'url' not in df.columns:
        st.error("Your CSV must have a column named 'URL'.")
    else:
        results = []
        for url in df['url']:
            with st.spinner(f"Analyzing {url}..."):
                analysis = analyze_backlink(client_url, niche, url)
                parsed = dict(line.split(": ", 1) for line in analysis.strip().split("\n"))
                parsed['Competitor URL'] = url
                results.append(parsed)

        result_df = pd.DataFrame(results)
        st.dataframe(result_df[['Competitor URL', 'Relevance', 'Quality', 'Ease', 'Recommendation']])

        # Export results
        st.download_button("Download Results", data=result_df.to_csv(index=False), file_name="analysis_results.csv")
else:
    st.info("Please fill all details and upload your competitor backlinks CSV.")
