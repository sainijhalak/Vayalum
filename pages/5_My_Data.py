import streamlit as st, sqlite3, os

DB_PATH=os.path.join(os.path.dirname(__file__),"..","data.db")

st.markdown("## 🗂️ My Saved Uploads")

if not st.session_state.get("user"):
    st.info("Please log in from the home page to view your uploads.")
    st.stop()

uid=st.session_state.user["id"]
with sqlite3.connect(DB_PATH) as conn:
    rows=conn.execute("SELECT filename,filepath,result,created_at FROM uploads WHERE user_id=? ORDER BY created_at DESC",(uid,)).fetchall()

if not rows:
    st.info("No uploads found.")
else:
    for fn,fp,res,dt in rows:
        with st.expander(f"🖼 {fn} — {dt}"):
            if os.path.exists(fp): st.image(fp,width=300)
            st.write(res)
