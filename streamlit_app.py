# streamlit_app.py
import streamlit as st
import pandas as pd
import openai
import time
from openai import OpenAIError  # Correct way to import base error class

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

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.3
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        raise RuntimeError("You have exceeded your OpenAI quota or encountered an API error. Please check your OpenAI account.") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

# Streamlit app UI
st.title("🔍 GPT-Powered Backlink Analyzer")

st.sidebar.header("Input Details")
client_url = st.sidebar.text_input("Your Client's URL")
niche = st.sidebar.text_input("Your Client's Niche")
uploaded_file = st.sidebar.file_uploader("Upload Competitor Backlinks (CSV)", type=['csv'])

manual_mode = False

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
                try:
                    analysis = analyze_backlink(client_url, niche, url)
                    parsed = dict(line.split(": ", 1) for line in analysis.strip().split("\n") if ": " in line)
                    parsed['Competitor URL'] = url
                    results.append(parsed)
                    time.sleep(1.5)  # Delay to avoid rate limit
                except RuntimeError as e:
                    st.error(str(e))
                    manual_mode = True
                    break
                except Exception as e:
                    st.warning(f"Failed to analyze {url}: {e}")

        if manual_mode:
            st.warning("Switched to manual mode due to quota limits. You can now analyze one URL at a time below.")
            manual_url = st.text_input("Enter a competitor backlink URL manually")
            if manual_url:
                if client_url and niche:
                    try:
                        manual_result = analyze_backlink(client_url, niche, manual_url)
                        st.text_area("GPT Analysis Result", manual_result, height=150)
                    except Exception as e:
                        st.error(f"Manual analysis failed: {e}")
                else:
                    st.info("Please fill in the client URL and niche in the sidebar.")
        else:
            result_df = pd.DataFrame(results)
            required_cols = ['Competitor URL', 'Relevance', 'Quality', 'Ease', 'Recommendation']

            if all(col in result_df.columns for col in required_cols):
                st.dataframe(result_df[required_cols])
                st.download_button("Download Results", data=result_df.to_csv(index=False), file_name="analysis_results.csv")
            else:
                st.warning("The response from GPT did not contain all expected fields. Showing raw results instead.")
                st.dataframe(result_df)
else:
    st.info("Please fill all details and upload your competitor backlinks CSV.")
