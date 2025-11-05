# pages/6_Calling_Agent.py
import streamlit as st
import requests
import re

st.set_page_config(page_title="KrishiMitra — Voice Agent", page_icon="📞")

st.title("📞 KrishiMitra — Interactive AI Voice Agent")
st.markdown("Enter your phone number (E.164 format) and press **Call Now** to receive a call from KrishiMitra.")

# ---------------------------
# Ensure session_state keys
# ---------------------------
if "user_number" not in st.session_state:
    st.session_state.user_number = ""  # will store verified phone (or last entered)

if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False

# ---------------------------
# Helper functions
# ---------------------------
def valid_phone(p):
    return bool(re.match(r"^\+\d{10,15}$", p))

# Default backend URL (change to your active ngrok URL if needed)
DEFAULT_BACKEND = "http://127.0.0.1:5000/v1/outbound-call"
BACKEND_URL = st.secrets.get("BACKEND_URL", DEFAULT_BACKEND)

# ---------------------------
# Phone input area
# ---------------------------
col1, col2 = st.columns([3,1])
with col1:
    phone_input = st.text_input("Phone (E.164, e.g. +919876543210):", value=st.session_state.user_number, key="phone_input")
with col2:
    if st.button("Save number"):
        if not phone_input:
            st.warning("Enter a phone number first.")
        elif not valid_phone(phone_input):
            st.error("Please use E.164 format: +countrycodexxxxxxxxx")
        else:
            st.session_state.user_number = phone_input
            st.session_state.otp_verified = True  # assume verified for now (or connect Twilio Verify flow)
            st.success(f"Saved number: {st.session_state.user_number}")

st.caption("Tip: include country code, e.g. +91 for India")

# ---------------------------
# Topic selection
# ---------------------------
topic = st.selectbox(
    "Select topic to discuss with KrishiMitra:",
    [
        "🌾 General Crop Advice",
        "🐛 Pest & Disease Control",
        "💧 Irrigation Planning",
        "🧪 Fertilizer Guidance",
        "🌤️ Weather Updates",
        "💰 Market Price Insights"
    ],
)

# ---------------------------
# Call button (uses session_state.user_number)
# ---------------------------
if st.button("🎤 Call Now"):
    # use session stored number if present, else use direct input
    dest = st.session_state.user_number or phone_input
    if not dest:
        st.error("No phone number provided. Please enter and save a phone number above.")
    elif not valid_phone(dest):
        st.error("Invalid phone number format. Enter in E.164 (+countrycode) format.")
    else:
        with st.spinner("Connecting to KrishiMitra voice server..."):
            try:
                payload = {"to": dest, "topic": topic}
                # Use HTTPS if your backend is exposed by ngrok — override BACKEND_URL in .streamlit/secrets.toml if needed
                resp = requests.post(BACKEND_URL, json=payload, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(data.get("message", "Call initiated."))
                    if "call_sid" in data:
                        st.info(f"Call SID: {data['call_sid']}")
                else:
                    # show server response text for debugging
                    try:
                        text = resp.json()
                    except Exception:
                        text = resp.text
                    st.error(f"API call failed ({resp.status_code}): {text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to Flask backend: {e}")

# ---------------------------
# Show current saved number & backend info
# ---------------------------
st.markdown("---")
st.write("**Saved number:**", st.session_state.user_number or "*None*")
st.write("**Backend URL used:**", BACKEND_URL)
st.info("Make sure your Flask voice server (twilio_voice_server.py) is running and ngrok (if used) is up. "
        "If you used a custom ngrok URL, set it in `.streamlit/secrets.toml` as `BACKEND_URL`.")
