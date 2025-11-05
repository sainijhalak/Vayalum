import streamlit as st
import google.generativeai as genai

st.markdown("## 💬 Chat with KrishiMitra")
st.info("Ask your farming questions in any language!")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    st.error("Missing Gemini API key. Add it in .streamlit/secrets.toml.")
    st.stop()

if "chat" not in st.session_state:
    st.session_state.chat = []

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("🌱 Type your question...")
if prompt:
    st.session_state.chat.append({"role":"user","content":prompt})
    with st.chat_message("user"): st.markdown(prompt)
    reply = model.generate_content(f"You are an Indian farming assistant. {prompt}").text
    st.session_state.chat.append({"role":"assistant","content":reply})
    with st.chat_message("assistant"): st.markdown(reply)
