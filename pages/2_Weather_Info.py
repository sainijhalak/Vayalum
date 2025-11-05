import streamlit as st, requests

st.markdown("## 🌦️ Weather Information")
st.info("Enter any city or village name to get weather & farming advice.")

city = st.text_input("City / Village Name:")
if st.button("🔍 Check Weather") and city:
    if "OPENWEATHER_API_KEY" not in st.secrets:
        st.error("Add OPENWEATHER_API_KEY to .streamlit/secrets.toml.")
        st.stop()

    key = st.secrets["OPENWEATHER_API_KEY"]
    url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"
    r=requests.get(url)
    if r.status_code==200:
        data=r.json()
        st.success(f"✅ {city.title()} Weather")
        st.metric("Temperature °C",data["main"]["temp"])
        st.metric("Humidity %",data["main"]["humidity"])
        st.metric("Wind Speed m/s",data["wind"]["speed"])
    else:
        st.error("Could not fetch weather data.")
