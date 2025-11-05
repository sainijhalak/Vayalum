import streamlit as st
from twilio.rest import Client

st.markdown("## 📞 KrishiMitra Voice Agent")
st.info("Call the AI farming assistant through Twilio.")

try:
    creds=st.secrets["TWILIO"]
    client=Client(creds["ACCOUNT_SID"],creds["AUTH_TOKEN"])
    phone=st.text_input("Enter phone number (+91...):")
    if st.button("📲 Make Demo Call"):
        call=client.calls.create(
            to=phone, from_=creds["PHONE_NUMBER"],
            url="http://demo.twilio.com/docs/voice.xml")
        st.success(f"Call initiated! SID: {call.sid}")
except Exception as e:
    st.error(f"Twilio not configured or error: {e}")
