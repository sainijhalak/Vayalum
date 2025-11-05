from flask import Flask, request, jsonify, Response
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import os

app = Flask(__name__)

# ---- Twilio credentials (from your .streamlit/secrets.toml or hardcoded for testing) ----
TWILIO_ACCOUNT_SID = "AC0686a6da540788ebb308e2f2fa875961"
TWILIO_AUTH_TOKEN = "c8d40a0538fb43663c55a335a78577b2"
TWILIO_PHONE_NUMBER = "+13368282514"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ---- This is the endpoint Twilio will call when the call is answered ----
@app.route("/voice", methods=["POST"])
def voice():
    """Respond to an incoming call with a greeting message"""
    resp = VoiceResponse()
    resp.say("Namaste! This is KrishiMitra, your AI farming assistant. "
             "Currently I can greet you, but interactive AI conversation will be added soon.",
             voice='alice', language='en-IN')
    return Response(str(resp), mimetype="application/xml")


# ---- Streamlit or Frontend will POST here to start an outbound call ----
@app.route("/v1/outbound-call", methods=["POST"])
def outbound_call():
    try:
        data = request.get_json()
        to_number = data.get("to")
        topic = data.get("topic", "General Crop Advice")

        if not to_number:
            return jsonify({"error": "Missing 'to' parameter"}), 400

        # Create the call
        call = client.calls.create(
            to=to_number,
            from_=TWILIO_PHONE_NUMBER,
            url="https://george-factualistic-elfreda.ngrok-free.dev/voice",  # <-- Update with your live ngrok URL
            method="POST"
        )

        return jsonify({
            "message": f"✅ Call initiated to {to_number} for topic: {topic}",
            "call_sid": call.sid
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---- Simple test route ----
@app.route("/", methods=["GET"])
def home():
    return "🚀 KrishiMitra Twilio Voice Server is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
