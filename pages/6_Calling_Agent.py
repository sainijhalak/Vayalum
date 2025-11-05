import streamlit as st
from twilio.rest import Client
import requests
import re

st.title("📞 KrishiMitra — Interactive AI Voice Agent")

# Load credentials safely
try:
    TWILIO_ACCOUNT_SID = st.secrets["TWILIO"]["ACCOUNT_SID"]
    TWILIO_AUTH_TOKEN = st.secrets["TWILIO"]["AUTH_TOKEN"]
    TWILIO_PHONE_NUMBER = st.secrets["TWILIO"]["PHONE_NUMBER"]
    VAPI_KEY = st.secrets["VAPI"]["VAPI_KEY"]
    ASSISTANT_ID = st.secrets["VAPI"]["ASSISTANT_ID"]
except Exception as e:
    st.error("⚠️ Missing or incorrect credentials in .streamlit/secrets.toml")
    st.stop()

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Validate phone format
def valid_phone(p):
    return re.match(r"^\+\d{10,15}$", p)

# Input UI
phone = st.text_input("Enter phone number (E.164 format, e.g., +919876543210):")
topic = st.selectbox(
    "Select topic to discuss with KrishiMitra:",
    [
        "🌾 General Crop Advice",
        "🐛 Pest & Disease Control",
        "💧 Irrigation Planning",
        "🧪 Fertilizer Guidance",
        "🌤️ Weather Updates",
        "💰 Market Price Insights"
    ]
)

if st.button("🎤 Start AI Call"):
    if not valid_phone(phone):
        st.error("Please enter a valid phone number with +91 etc.")
    else:
        with st.spinner("📞 Connecting KrishiMitra AI Voice Assistant..."):
            try:
                # ✅ Correct Gemini Voice API endpoint
                url = "https://api.vapi.ai/v1/outbound-call"
                headers = {
                    "Authorization": f"Bearer {VAPI_KEY}",
                    "Content-Type": "application/json"
                }

                data = {
                    "assistant_id": ASSISTANT_ID,
                    "type": "phone",
                    "phone_number": phone,
                    "metadata": {
                        "topic": topic,
                        "intro_message": f"Hello! I’m KrishiMitra, your AI farming assistant. Let's talk about {topic}."
                    }
                }

                response = requests.post(url, headers=headers, json=data)

                if response.status_code in [200, 201]:
                    st.success("✅ KrishiMitra is calling you now! Please answer 📱")
                    st.json(response.json())
                else:
                    st.error(f"❌ API call failed: {response.text}")

            except Exception as e:
                st.error(f"⚠️ Error while starting AI call: {e}")
