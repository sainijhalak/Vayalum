import streamlit as st, os, datetime
from PIL import Image
from google.generativeai import GenerativeModel

UPLOAD_DIR=os.path.join(os.path.dirname(__file__),"..","uploads")
os.makedirs(UPLOAD_DIR,exist_ok=True)

st.markdown("## 📷 Crop Disease Detection")
st.info("Upload an image of your crop or leaf for AI-based analysis.")

file=st.file_uploader("Choose an image",type=["jpg","jpeg","png"])
if file:
    img=Image.open(file).convert("RGB")
    st.image(img,caption="Uploaded image",use_container_width=True)
    path=os.path.join(UPLOAD_DIR,f"{datetime.datetime.utcnow():%Y%m%d%H%M%S}_{file.name}")
    img.save(path)

    try:
        model=GenerativeModel("gemini-2.5-flash")
        resp=model.generate_content([
            "You are a crop expert. Identify the crop/disease and suggest treatment.",
            {"mime_type":file.type,"data":file.getvalue()}])
        st.success("✅ Analysis complete!")
        st.markdown(resp.text)
    except Exception as e:
        st.error(f"Error analyzing: {e}")
