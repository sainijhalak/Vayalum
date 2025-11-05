import streamlit as st
import sqlite3, hashlib, datetime, os

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

st.set_page_config(page_title="Vayalum – AI Farm Assistant", page_icon="🌱", layout="centered")

# --- Theme Styling (keep this global look) ---
st.markdown("""
<style>
body, .stApp {background: linear-gradient(135deg,#f0fdf4,#e6fffa);}
.vayalum-header h1 {
    text-align:center; 
    background: linear-gradient(90deg,#16a34a,#059669,#065f46);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.vayalum-card {
    background:rgba(255,255,255,0.8); backdrop-filter:blur(10px);
    border-radius:16px; padding:1.5rem; box-shadow:0 4px 10px rgba(0,0,0,0.08);
}
.stButton>button {
    background:linear-gradient(90deg,#16a34a,#22c55e);
    border:none; border-radius:10px; color:white; padding:0.6rem 1rem; font-weight:600;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class='vayalum-header'>
    <h1>🌾 Vayalum — AI Farm Assistant</h1>
</div>
<div class='vayalum-card' style='text-align:center'>
🤖 Smart multilingual AI | 🌤 Weather | 📷 Crop Detection | 🏛 Schemes | ☎ Voice Call
</div>
""", unsafe_allow_html=True)


# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL)""")
    conn.commit(); conn.close()
init_db()

def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

# ---------- Register ----------
st.markdown("### 🆕 Register or 👤 Login to continue")

tab1, tab2 = st.tabs(["Register", "Login"])

with tab1:
    reg_user = st.text_input("Username", key="ruser")
    reg_pw = st.text_input("Password", type="password", key="rpw")
    if st.button("Register"):
        if reg_user and reg_pw:
            conn = sqlite3.connect(DB_PATH)
            try:
                conn.execute("INSERT INTO users (username,password_hash,created_at) VALUES (?,?,?)",
                             (reg_user.lower(), hash_pw(reg_pw), datetime.datetime.utcnow().isoformat()))
                conn.commit()
                st.success("✅ Registration successful! You can now log in.")
            except sqlite3.IntegrityError:
                st.error("Username already exists.")
            conn.close()
        else:
            st.warning("Please fill all fields.")

with tab2:
    user = st.text_input("Username", key="luser")
    pw = st.text_input("Password", type="password", key="lpw")
    if st.button("Login"):
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("SELECT id,password_hash FROM users WHERE username=?",(user.lower(),)).fetchone()
        conn.close()
        if row and row[1]==hash_pw(pw):
            st.session_state.user = {"id":row[0],"username":user.lower()}
            st.success(f"Welcome back, {user}! 🌱")
            st.info("Use the left sidebar to navigate between pages.")
        else:
            st.error("Invalid username or password.")
