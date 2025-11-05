import streamlit as st
import google.generativeai as genai

st.markdown("## 🏛️ Government Schemes")
st.info("Get the latest verified schemes and subsidies for farmers.")

query = st.text_input("Enter scheme name or topic (e.g., PM-Kisan):")
if query:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("Add GEMINI_API_KEY in .streamlit/secrets.toml.")
        st.stop()
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model=genai.GenerativeModel("gemini-2.0-flash-exp")

    prompt=f"""
    Search real-time official Indian government schemes related to "{query}".
    Show:
    • Scheme Name
    • Benefits
    • Eligibility
    • How to Apply
    • Official Website
    Summarize only from verified .gov.in or nabard.org sources.
    """
    with st.spinner("Fetching live updates..."):
        try:
            res=model.generate_content(prompt)
            st.markdown(res.text)
        except Exception as e:
            st.error(f"Error: {e}")
