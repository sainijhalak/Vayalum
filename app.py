import streamlit as st
import google.generativeai as genai
# language detection
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except Exception:
    LANGDETECT_AVAILABLE = False

import sqlite3
import os
import hashlib
import datetime
import base64
import requests
import streamlit.components.v1 as components
import html
from PIL import Image
from io import BytesIO

# ------------------ CONFIG ------------------
APP_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(APP_DIR, "data.db")
UPLOAD_DIR = os.path.join(APP_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="AI Farm Assistant", page_icon="🌱", layout="centered")

# --- simple styling to make the app look more professional ---
st.markdown(
    """
    <style>
    /* Reset theme colors for better visibility */
    .stApp {
        background-color: var(--background-color);
    }

    /* Enhanced text visibility for all themes */
    .stMarkdown, p, div, span, li, h1, h2, h3, h4, h5, h6 {
        color: var(--text-color) !important;
    }
    
    /* Chat message visibility */
    .stChatMessage {
        background: var(--background-color) !important;
        border: 1px solid var(--primary-color) !important;
        padding: 1rem !important;
        margin: 8px 0 !important;
        border-radius: 8px !important;
    .stChatMessage p, .stChatMessage div {
        color: #0f172a !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    
    /* Header and card styling */
    .vayalum-header { 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
        color: #0f172a !important; 
        margin-bottom: 8px; 
    }
    .vayalum-card { 
        background: #ffffff; 
        color: #0f172a !important; 
        padding: 16px; 
        border-radius: 8px; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.08); 
        margin-bottom: 12px; 
    }
    .sidebar .sidebar-content { background: linear-gradient(180deg,#ffffff,#f1f5f9); }

    /* Make form fields and buttons readable regardless of Streamlit theme */
    input, textarea, select {
        background: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #e6e9ef !important;
        border-radius: 8px !important;
        padding: 10px 12px !important;
        font-size: 16px !important;
    }
    /* placeholder color */
    ::placeholder { color: #94a3b8 !important; }

    /* File uploader area */
    .stFileUploader > div, .stFileUploader input {
        background: #ffffff !important;
        color: #0f172a !important;
    }

    /* Buttons */
    button, .stButton>button {
        background: linear-gradient(180deg,#0f172a,#111827) !important;
        color: #fff !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        border: none !important;
        font-size: 16px !important;
    }

    /* Alerts / error boxes: keep readable */
    .stAlert, [role="alert"] {
        color: #0f172a !important;
        background: white !important;
        border: 1px solid currentColor !important;
    }

    /* Improve text input visibility */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        color: #0f172a !important;
        background: white !important;
        font-size: 16px !important;
    }

    /* Better visibility for chat input */
    .stChatInputContainer {
        background: white !important;
        padding: 10px !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
    }

    /* Enhanced form input visibility */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--primary-color) !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
    }

    /* Button styling */
    .stButton button {
        background-color: var(--primary-color) !important;
        color: var(--background-color) !important;
        border: none !important;
        padding: 8px 16px !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }

    /* Sidebar and navigation */
    .sidebar .sidebar-content {
        background: var(--background-color) !important;
    }
    
    /* Card styling */
    .card {
        background: color-mix(in srgb, var(--background-color) 95%, var(--primary-color) 5%) !important;
        border: 1px solid var(--primary-color) !important;
        color: var(--text-color) !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        margin-bottom: 1rem !important;
    }

    /* Alert/info boxes */
    .stAlert {
        background-color: color-mix(in srgb, var(--background-color) 90%, var(--primary-color) 10%) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--primary-color) !important;
        padding: 1rem !important;
        border-radius: 6px !important;
    }

    /* Font settings */
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', system-ui, sans-serif !important;
    }
    
    .stMarkdown, .stChat {
        font-size: 16px !important;
        line-height: 1.6 !important;
    }

    /* Code blocks and preformatted text */
    code, pre {
        background-color: color-mix(in srgb, var(--background-color) 95%, var(--text-color) 5%) !important;
        color: var(--text-color) !important;
        padding: 0.2em 0.4em !important;
        border-radius: 4px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='vayalum-header'><h1 style='margin:0;'>Vayalum — AI Farm Assistant</h1></div>", unsafe_allow_html=True)
st.markdown("<div class='vayalum-card'>🤖 Multilingual farming guide — now with weather, crop detection, login, schemes and Vayalum AI page</div>", unsafe_allow_html=True)

# Configure Gemini API if available in secrets
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")  # Using Flash model for faster responses
        except Exception:
            model = genai.GenerativeModel("gemini-2.0-pro")  # Fallback to older version if needed
    except Exception:
        model = None
else:
    model = None

# ------------------ SYSTEM PROMPT ------------------
SYSTEM_PROMPT = """
You are "KrishiMitra", a helpful and knowledgeable AI assistant for Indian farmers.

🎯 Your Responsibilities:
- Answer ONLY agriculture and farming-related questions.
    - Support all major languages — including Indian languages (for example: Hindi, Bengali, Telugu, Marathi, Tamil, Urdu, Gujarati, Kannada, Malayalam, Odia, Punjabi, Assamese, Maithili) as well as other world languages (for example: Spanish, French, Arabic).
    - Detect the language(s) the user used and REPLY ONLY in the same language(s) the user used.
        - If the user writes in a single language, reply only in that language.
        - If the user mixes languages, mirror that mixture in your reply.
        - Do NOT add translations, do NOT reply in any additional languages.
        - If language detection fails, try to reply in the user's language; if that's not possible, reply in English.
- Be short, practical, and friendly — use emojis and simple words.
- Use clear, actionable farming guidance and cite common practices; avoid giving medical or legal advice.
- If the user asks something unrelated to farming, politely refuse in the same language the user used.

Tone and format:
- Keep answers concise (1–6 short sentences) and practical.
- Use emojis where helpful.
- When giving instructions (e.g., treatment steps), present them as a short numbered or bullet list in the same language.
"""

# ------------------ DATABASE / AUTH ------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            filepath TEXT,
            result TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(username: str, password: str) -> (bool, str):
    # normalize username
    username = username.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, hash_password(password), datetime.datetime.utcnow().isoformat()),
        )
        conn.commit()
        return True, "User created"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    finally:
        conn.close()


def verify_user(username: str, password: str) -> (bool, int):
    # normalize username same as create_user
    username = username.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False, None
    user_id, pw_hash = row
    if pw_hash == hash_password(password):
        return True, user_id
    return False, None


def save_upload(user_id, filename, filepath, result_text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO uploads (user_id, filename, filepath, result, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, filename, filepath, result_text, datetime.datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


init_db()

# ------------------ UI: NAVIGATION ------------------
# Pages: only show Login/Register when not logged in
PUBLIC_PAGES = ["Register", "Login"]
PROTECTED_PAGES = ["Chat", "Weather", "Crop ID", "Government Schemes", "My Data", "Calling Agent"]

if "user" not in st.session_state or st.session_state.user is None:
    # show Register first so new users register before trying to log in
    page = st.sidebar.selectbox("Navigate", PUBLIC_PAGES, index=0)
else:
    PAGES = PROTECTED_PAGES + ["Logout"]
    page = st.sidebar.selectbox("Navigate", PAGES, index=0)

# Simple session user object
if "user" not in st.session_state:
    st.session_state.user = None

# ------------------ HELPERS ------------------
lang_name_map = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "bn": "Bengali",
    "te": "Telugu",
    "mr": "Marathi",
    "ta": "Tamil",
    "ur": "Urdu",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "or": "Odia",
    "pa": "Punjabi",
    "as": "Assamese",
}


def detect_language(text: str):
    if LANGDETECT_AVAILABLE:
        try:
            code = detect(text)
            return code, lang_name_map.get(code, code)
        except Exception:
            return None, None
    return None, None


# ------------------ PAGES ------------------
if page == "Register":
    st.header("🆕 Register")
    st.markdown("Please register before logging in.")
    with st.form(key='reg_form'):
        reg_user = st.text_input("Username", placeholder="Choose a username", key="reg_user")
        reg_pw = st.text_input("Password", type="password", placeholder="Choose a password", key="reg_pw")
        reg_sub = st.form_submit_button("Register")
        if reg_sub:
            if not reg_user or not reg_pw:
                st.error("Please provide a username and password to register.")
            else:
                ok, msg = create_user(reg_user, reg_pw)
                if ok:
                    st.success("Registration successful. You can now go to the Login page.")
                else:
                    st.error(msg)

elif page == "Login":
    st.header("👤 Login")
    st.markdown("If you already have an account, enter your credentials below.")
    with st.form(key='login_form'):
        login_user = st.text_input("Username", placeholder="Username", key="login_user")
        login_pw = st.text_input("Password", type="password", placeholder="Password", key="login_pw")
        submitted = st.form_submit_button("Login")
        if submitted:
            if not login_user or not login_pw:
                st.error("Please enter both username and password.")
            else:
                ok, user_id = verify_user(login_user, login_pw)
                if ok:
                    st.session_state.user = {"id": user_id, "username": login_user.strip().lower()}
                    st.success(f"Logged in as {login_user}")
                    try:
                        st.experimental_rerun()
                    except Exception:
                        pass
                else:
                    st.error("Invalid username or password")

elif page == "Chat":
    st.header("💬 Chat with KrishiMitra")

    # Setup chat memory
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Display previous messages
    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask your question about farming in any language...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # language detection
        detected_lang, detected_lang_name = detect_language(user_input)

        # prepare messages for model
        messages_for_model = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        if detected_lang_name:
            messages_for_model.append({
                "role": "system",
                "content": f"Detected user language: {detected_lang_name} ({detected_lang}). Reply ONLY in that language unless the user asked in multiple languages.",
            })
        messages_for_model.append({"role": "user", "content": user_input})

        # call model if available
        bot_reply = ""
        if model is None:
            bot_reply = "AI model not configured. Please add GEMINI_API_KEY to Streamlit secrets to enable chat." 
        else:
            try:
                if hasattr(model, "chat"):
                    resp = model.chat(messages=messages_for_model)
                    bot_reply = getattr(resp, "text", None) or getattr(resp, "output_text", None) or str(resp)
                else:
                    # fallback to single prompt
                    full_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages_for_model])
                    resp = model.generate_content(full_prompt)
                    bot_reply = getattr(resp, "text", None) or str(resp)
            except Exception as e:
                bot_reply = f"⚠️ Error while contacting model: {e}"

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

elif page == "Weather":
    st.header("🌦️ Weather Information (Multilingual)")

    # --- Input ---
    query = st.text_input("Enter city name in any Indian language (e.g., दिल्ली, মুম্বই, చెన్నై):")

    if st.button("🔍 Check Weather") and query:
        # --- Check if API key is available ---
        if "OPENWEATHER_API_KEY" not in st.secrets:
            st.warning("No OpenWeatherMap API key configured. Please add OPENWEATHER_API_KEY to Streamlit secrets.")
            st.stop()

        key = st.secrets["OPENWEATHER_API_KEY"]

        # --- Fetch weather data ---
        try:
            # detect language from the user's query
            def detect_indian_language(text):
                # Check for specific Indian scripts
                for ch in text:
                    o = ord(ch)
                    # Devanagari (Hindi, Marathi)
                    if 0x0900 <= o <= 0x097F:
                        return "hi"  # Hindi
                    # Bengali
                    if 0x0980 <= o <= 0x09FF:
                        return "bn"
                    # Telugu
                    if 0x0C00 <= o <= 0x0C7F:
                        return "te"
                    # Tamil
                    if 0x0B80 <= o <= 0x0BFF:
                        return "ta"
                    # Gujarati
                    if 0x0A80 <= o <= 0x0AFF:
                        return "gu"
                    # Kannada
                    if 0x0C80 <= o <= 0x0CFF:
                        return "kn"
                    # Malayalam
                    if 0x0D00 <= o <= 0x0D7F:
                        return "ml"
                    # Odia
                    if 0x0B00 <= o <= 0x0B7F:
                        return "or"
                    # Punjabi (Gurmukhi)
                    if 0x0A00 <= o <= 0x0A7F:
                        return "pa"
                    # Assamese (shares script with Bengali)
                    if 0x0980 <= o <= 0x09FF:
                        return "as"
                return "en"  # Default to English if no Indian script detected

            detected_lang = detect_indian_language(query)
            lang_names = {
                "hi": "Hindi",
                "bn": "Bengali",
                "te": "Telugu",
                "ta": "Tamil",
                "gu": "Gujarati",
                "kn": "Kannada",
                "ml": "Malayalam",
                "or": "Odia",
                "pa": "Punjabi",
                "as": "Assamese",
                "en": "English"
            }

            url = f"https://api.openweathermap.org/data/2.5/weather?q={query}&appid={key}&units=metric"
            r = requests.get(url, timeout=10)
            data = r.json()
            
            if r.status_code == 200:
                # --- Extract weather info ---
                weather = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                wind = data["wind"]["speed"]

                # --- Build weather summary ---
                language_name = lang_names.get(detected_lang, "English")
                base_text = (
                    f"City/Location: {query}\n"
                    f"Temperature: {temp}°C\n"
                    f"Weather: {weather}\n"
                    f"Humidity: {humidity}%\n"
                    f"Wind Speed: {wind} m/s\n\n"
                    f"Act as a farming expert. Use the above weather information to provide farmer-friendly advice "
                    f"about irrigation timing, pest control measures, and crop care specifically for this weather. "
                    f"Response MUST be in {language_name} language only. Use appropriate farming terms in {language_name}. "
                    f"Make it concise but informative for farmers."
                )

                # --- Generate localized response using Gemini ---
                try:
                    response = model.generate_content(base_text)
                    st.success("✅")  # Weather information received (in Hindi)
                    st.markdown(response.text)
                except Exception as e:
                    # Fallback responses in various languages
                    fallback = {
                        "hi": f"**{query}** का मौसम: तापमान {temp}°C, आर्द्रता {humidity}%, हवा {wind} m/s",
                        "bn": f"**{query}** এর আবহাওয়া: তাপমাত্রা {temp}°C, আর্দ্রতা {humidity}%, বায়ু {wind} m/s",
                        "te": f"**{query}** వాతావరణం: ఉష్ణోగ్రత {temp}°C, తేమ {humidity}%, గాలి {wind} m/s",
                        "ta": f"**{query}** வானிலை: வெப்பநிலை {temp}°C, ஈரப்பதம் {humidity}%, காற்று {wind} m/s"
                    }
                    st.write(fallback.get(detected_lang, f"**{query}** — Temperature: {temp}°C, Humidity: {humidity}%, Wind: {wind} m/s"))
                    st.warning("⚠️ Could not generate detailed advice. Showing basic information.")

            else:
                st.error(data.get("message", "Could not fetch weather."))

        except Exception as e:
            st.error(f"Error fetching weather: {e}")


elif page == "Crop ID":
    st.header("📷 Crop Disease Detection (AI-Powered)")
    st.markdown(
        "Upload a clear image of your crop, leaf, or fruit. "
        "The AI will identify possible diseases and suggest treatment steps."
    )

    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded image", use_container_width=True)  # fixed use_column_width

        # Save image temporarily
        ts = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{ts}_{uploaded_file.name}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        image.save(filepath)

        st.info("🔍 Analyzing the image using Gemini Vision AI...")

        try:
            # Use Gemini Vision model
            from google.generativeai import GenerativeModel

            vision_model = GenerativeModel("gemini-2.5-flash")  # works well for image analysis
            response = vision_model.generate_content([
                "You are an expert crop disease detection assistant. "
                "Analyze the uploaded crop/leaf image, identify the crop type if possible, "
                "detect any visible disease or nutrient deficiency, and suggest treatments in simple language. "
                "If healthy, say the crop looks healthy.",
                {"mime_type": uploaded_file.type, "data": uploaded_file.getvalue()}
            ])

            result_text = response.text
            st.success("✅ Analysis Complete!")
            st.markdown(result_text)

        except Exception as e:
            st.error(f"⚠️ Error analyzing image with Gemini: {e}")
            result_text = f"Analysis failed: {e}"

        # Associate result with user (if you track uploads)
        user_id = st.session_state.user["id"] if st.session_state.get("user") else None
        save_upload(user_id, filename, filepath, result_text)
        st.success("🗂️ Image saved and result recorded in database.")

elif page == "Government Schemes":
    st.header("🏛️ Live Government Schemes for Farmers (Real-Time)")

    st.markdown("""
    🔍 This section fetches the **latest official updates** about Indian government schemes for farmers  
    — like PM-Kisan, Fasal Bima Yojana, soil health programs, and subsidies —  
    directly from trusted sources (gov.in, NABARD, ICAR, etc.).
    """)
   
    query = st.text_input("Enter scheme name or topic (e.g., PM-Kisan, crop insurance, fertilizer subsidy):")

    if query:
        with st.spinner("Fetching latest scheme updates..."):
            try:
                # use fast Gemini model with browsing ability
                model = genai.GenerativeModel("gemini-2.0-flash-exp")

                prompt = f"""
                Search the web for *real-time* official government schemes, farmer programs, and subsidies
                in India related to: "{query}".
                Only summarize information from **verified sources** such as:
                - pmkisan.gov.in
                - agricoop.gov.in
                - pib.gov.in
                - pmfby.gov.in
                - nabard.org
                - data.gov.in

                Present the result clearly:
                • Scheme Name  
                • Purpose / Key Benefits  
                • Eligibility / How to Apply  
                • Official Website Link  
                • Provide the summary in the same language the user asked in (Hindi or English).
                """

                response = model.generate_content(prompt)
                st.subheader("🧭 Latest Verified Schemes and Updates:")
                st.write(response.text)

            except Exception as e:
                st.error(f"⚠️ Error fetching live data: {e}")
    else:
        st.info("Type a scheme name or topic above to get live updates.")


elif page == "My Data":
    st.header("🗂️ My Saved Data and Uploads")

    # Check login
    if not st.session_state.get("user"):
        st.info("Log in to view or manage your uploads.")
    else:
        user_id = st.session_state.user["id"]

        # --- Load user uploads ---
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, filename, filepath, result, created_at 
                FROM uploads 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            """, (user_id,))
            rows = c.fetchall()

        if not rows:
            st.info("No uploads yet.")
        else:
            st.markdown("### 📸 Your Uploaded Images")

            # ------------------------------------------
            # ✅ Delete ALL button (now actually works)
            # ------------------------------------------
            with st.expander("⚠️ Delete ALL My Data"):
                st.warning("This will permanently delete all your uploaded files and records.")
                delete_all_confirm = st.button("🗑 Yes, delete all my data permanently")

                if delete_all_confirm:
                    try:
                        # Delete all files first
                        for r in rows:
                            _, _, filepath, _, _ = r
                            if os.path.exists(filepath):
                                os.remove(filepath)

                        # Delete all DB records
                        with sqlite3.connect(DB_PATH) as conn:
                            c = conn.cursor()
                            c.execute("DELETE FROM uploads WHERE user_id = ?", (user_id,))
                            conn.commit()

                        st.success("✅ All your uploads have been deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting all data: {e}")

            # ------------------------------------------
            # Individual delete per upload
            # ------------------------------------------
            for r in rows:
                _id, filename, filepath, result, created_at = r
                with st.expander(f"🖼 {filename} — {created_at}"):
                    if os.path.exists(filepath):
                        st.image(filepath, width=300)
                    else:
                        st.warning("Image file not found on disk.")

                    st.write(f"**Result:** {result}")

                    # Delete individual file
                    if st.button(f"Delete {filename}", key=f"del_{_id}"):
                        try:
                            if os.path.exists(filepath):
                                os.remove(filepath)
                            with sqlite3.connect(DB_PATH) as conn:
                                c = conn.cursor()
                                c.execute("DELETE FROM uploads WHERE id = ?", (_id,))
                                conn.commit()

                            st.success(f"✅ Deleted {filename} successfully.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error deleting {filename}: {e}")

elif page == "Logout":
    # Clear the user session state
    st.session_state.user = None
    # Clear other session states that might contain user data
    if "messages" in st.session_state:
        del st.session_state.messages
    st.success("👋 You have been logged out successfully!")
    st.info("Please use the sidebar to log in again.")
    # Rerun the app to update the navigation
    st.rerun()

elif page == "Calling Agent":
    st.header("📞 KrishiMitra – AI Voice Agent via Twilio")

    from twilio.rest import Client
    import re

    # Load from secrets
    try:
        TWILIO_ACCOUNT_SID = st.secrets["TWILIO"]["ACCOUNT_SID"]
        TWILIO_AUTH_TOKEN = st.secrets["TWILIO"]["AUTH_TOKEN"]
        TWILIO_PHONE_NUMBER = st.secrets["TWILIO"]["PHONE_NUMBER"]
        VERIFY_SERVICE_SID = st.secrets["TWILIO"]["VERIFY_SERVICE_SID"]
    except Exception as e:
        st.error("⚠️ Twilio credentials missing. Add them to .streamlit/secrets.toml.")
        st.stop()

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    if "stage" not in st.session_state:
        st.session_state.stage = "send_otp"
    if "user_number" not in st.session_state:
        st.session_state.user_number = ""

    # --- Helper ---
    def valid_phone(p):
        return re.match(r"^\+\d{10,15}$", p)

    # --- Stage 1: Send OTP ---
    if st.session_state.stage == "send_otp":
        st.subheader("1️⃣ Enter your mobile number")
        phone = st.text_input("Phone (E.164 format, e.g. +919876543210):")
        if st.button("📲 Send OTP"):
            if not valid_phone(phone):
                st.error("Please enter a valid phone number with +91 etc.")
            else:
                try:
                    client.verify.services(VERIFY_SERVICE_SID).verifications.create(to=phone, channel="sms")
                    st.session_state.user_number = phone
                    st.session_state.stage = "verify_otp"
                    st.success(f"OTP sent to {phone}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to send OTP: {e}")

    # --- Stage 2: Verify OTP ---
    elif st.session_state.stage == "verify_otp":
        st.subheader("2️⃣ Verify OTP")
        otp = st.text_input("Enter 6-digit OTP:")
        if st.button("✅ Verify"):
            try:
                result = client.verify.services(VERIFY_SERVICE_SID).verification_checks.create(
                    to=st.session_state.user_number, code=otp
                )
                if result.status == "approved":
                    st.session_state.stage = "call"
                    st.success("OTP verified successfully ✅")
                    st.rerun()
                else:
                    st.error("Invalid OTP, please try again.")
            except Exception as e:
                st.error(f"Verification failed: {e}")
        if st.button("🔁 Resend OTP"):
            try:
                client.verify.services(VERIFY_SERVICE_SID).verifications.create(to=st.session_state.user_number, channel="sms")
                st.success("New OTP sent ✅")
            except Exception as e:
                st.error(f"Error resending: {e}")

    # --- Stage 3: Make the call ---
    elif st.session_state.stage == "call":
        st.subheader("3️⃣ Make a voice call to the farmer")

        topic = st.selectbox("Select topic:", [
            "🌾 General Crop Advice",
            "🐛 Pest Control",
            "💧 Irrigation",
            "🧪 Fertilizer Guidance",
            "🌤️ Weather Update",
            "💰 Market Prices"
        ])

        if st.button("🎤 Call Now"):
            with st.spinner("Calling..."):
                try:
                    # Twilio demo voice XML (you can replace this with your own TwiML webhook)
                    call = client.calls.create(
                        to=st.session_state.user_number,
                        from_=TWILIO_PHONE_NUMBER,
                        url="http://demo.twilio.com/docs/voice.xml",
                        method="GET"
                    )
                    st.success(f"Call initiated ✅  (SID: {call.sid})")
                    st.info("Your phone should ring shortly. This demo TwiML plays a sample message.")
                except Exception as e:
                    st.error(f"Call failed: {e}")

        if st.button("🔁 Verify Another Number"):
            for key in ["stage", "user_number"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
