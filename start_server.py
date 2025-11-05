from flask import Flask, request, Response
from pyngrok import ngrok, conf
import google.generativeai as genai
from langdetect import detect
import os
import streamlit as st
from twilio.rest import Client

# Configure ngrok path - update this path to where your ngrok.exe is located
conf.get_default().ngrok_path = r"C:\Users\saini\OneDrive\Desktop\ngrok\ngrok.exe"

# --- Load Twilio and Gemini Credentials from Streamlit Secrets ---
TWILIO_ACCOUNT_SID = st.secrets["TWILIO"]["ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO"]["AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = st.secrets["TWILIO"]["PHONE_NUMBER"]
VERIFY_SERVICE_SID = st.secrets["TWILIO"]["VERIFY_SERVICE_SID"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Initialize Flask app
app = Flask(__name__)

# Language voice mapping for Twilio
VOICE_MAPPING = {
    "hi": "hi-IN",  # Hindi
    "bn": "bn-IN",  # Bengali
    "te": "te-IN",  # Telugu
    "ta": "ta-IN",  # Tamil
    "gu": "gu-IN",  # Gujarati
    "kn": "kn-IN",  # Kannada
    "ml": "ml-IN",  # Malayalam
    "mr": "mr-IN",  # Marathi
    "pa": "pa-IN",  # Punjabi
    "en": "en-IN",  # English (India)
}

def detect_indian_language(text):
    """Detect Indian language from text using script detection"""
    for ch in text:
        o = ord(ch)
        if 0x0900 <= o <= 0x097F:
            return "hi"  # Hindi/Devanagari
        if 0x0980 <= o <= 0x09FF:
            return "bn"  # Bengali
        if 0x0C00 <= o <= 0x0C7F:
            return "te"  # Telugu
        if 0x0B80 <= o <= 0x0BFF:
            return "ta"  # Tamil
        if 0x0A80 <= o <= 0x0AFF:
            return "gu"  # Gujarati
        if 0x0C80 <= o <= 0x0CFF:
            return "kn"  # Kannada
        if 0x0D00 <= o <= 0x0D7F:
            return "ml"  # Malayalam
    return "hi"  # Default to Hindi if no specific script detected

@app.route("/voice", methods=["POST"])
def voice_reply():
    """Handle incoming voice calls from Twilio"""
    try:
        speech_text = request.form.get("SpeechResult", "").strip()
        print("🧑‍🌾 Farmer said:", speech_text)

        if not speech_text:
            response = """
                <Response>
                    <Say voice="Polly.Aditi" language="hi-IN">
                        नमस्ते किसान भाई! मैं आपकी कृषि सहायक हूँ। 
                        कृपया बताइए, आपकी फसल से जुड़ा क्या प्रश्न है?
                    </Say>
                    <Gather input="speech" action="/voice" method="POST" timeout="8" />
                </Response>
            """
            return Response(response, mimetype="text/xml")

        try:
            lang_code = detect(speech_text)
        except Exception:
            lang_code = "en"

        print("🌐 Detected language:", lang_code)

        model = genai.GenerativeModel("gemini-1.5-flash")
        system_prompt = (
            f"The farmer said: '{speech_text}'. "
            f"Reply concisely in the same language ({lang_code}). "
            "Give helpful farming advice or politely refuse irrelevant questions."
        )
        ai_reply = model.generate_content(system_prompt).text
        print("🤖 Gemini reply:", ai_reply)

        # TwiML response
        twiml = f"""
            <Response>
                <Say voice="Polly.Aditi" language="{ 'hi-IN' if lang_code=='hi' else 'en-IN' }">
                    {ai_reply}
                </Say>
                <Pause length="1"/>
                <Say voice="Polly.Aditi" language="{ 'hi-IN' if lang_code=='hi' else 'en-IN' }">
                    क्या आप एक और प्रश्न पूछना चाहेंगे? कृपया बोलें।
                </Say>
                <Gather input="speech" action="/voice" method="POST" timeout="8" />
            </Response>
        """
        return Response(twiml, mimetype="text/xml")

    except Exception as e:
        print("❌ Error:", e)
        return Response("<Response><Say>System error occurred.</Say></Response>", mimetype="text/xml")

if __name__ == "__main__":
    try:
        print("🚀 Starting KrishiMitra Voice AI Server...")
        
        # Start ngrok tunnel
        public_url = ngrok.connect(5005).public_url
        print(f"🌍 Public URL: {public_url}")
        print(f"📞 Configure this URL in Twilio: {public_url}/voice")
        
        # Start Flask server
        app.run(port=5005)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
