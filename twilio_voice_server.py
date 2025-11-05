from flask import Flask, request, jsonify
from twilio.rest import Client
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ KrishiMitra Voice Server is running!"

@app.route("/v1/outbound-call", methods=["POST"])
def outbound_call():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    phone_number = data.get("to")
    topic = data.get("topic", "General Crop Advice")

    if not phone_number:
        return jsonify({"error": "Missing phone number"}), 400

    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "AC0686a6da540788ebb308e2f2fa875961")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "c8d40a0538fb43663c55a335a78577b2")
    twilio_number = "+13368282514"  # your Twilio number

    try:
        client = Client(account_sid, auth_token)
        call = client.calls.create(
            twiml=f'<Response><Say>Hello! This is KrishiMitra. You selected {topic}. I am here to help you with your crops.</Say></Response>',
            to=phone_number,
            from_=twilio_number,
        )
        return jsonify({
            "message": f"Call initiated to {phone_number} for topic '{topic}'",
            "call_sid": call.sid
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Starting KrishiMitra Voice Server on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)
