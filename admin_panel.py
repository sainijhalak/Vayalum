import streamlit as st
import sqlite3
import os
import pandas as pd

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

# Verify database exists
if not os.path.exists(DB_PATH):
    st.error(f"Database not found at {DB_PATH}. Please make sure the app has been initialized.")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(page_title="👨‍💻 Admin Panel", page_icon="🧑‍🌾", layout="wide")
st.title("👨‍💻 Admin Dashboard – AI Farm Assistant")
st.markdown("Manage users and view statistics for your app.")

# --- DATABASE UTILS ---
def get_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

def get_all_users():
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()
        query = "SELECT id, username, created_at FROM users ORDER BY created_at DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return pd.DataFrame()

def get_upload_count(user_id):
    try:
        conn = get_connection()
        if conn is None:
            return 0
        query = "SELECT COUNT(*) as total_uploads FROM uploads WHERE user_id = ?"
        cur = conn.cursor()
        cur.execute(query, (user_id,))
        count = cur.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        st.error(f"Error counting uploads for user {user_id}: {e}")
        return 0

def delete_user(user_id):
    try:
        conn = get_connection()
        if conn is None:
            return False
        cur = conn.cursor()
        # First delete user's uploads
        cur.execute("DELETE FROM uploads WHERE user_id = ?", (user_id,))
        # Then delete user
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error deleting user {user_id}: {e}")
        return False

# --- ADMIN AUTH (Simple Password) ---
st.sidebar.header("🔐 Admin Login")
admin_password = st.sidebar.text_input("Enter Admin Password", type="password")

if admin_password != "1946":  # Change this to your own password
    st.warning("Please enter the correct admin password to continue.")
    st.stop()

# --- MAIN DASHBOARD ---
st.success("✅ Logged in as Admin")

users = get_all_users()

if users.empty:
    st.info("No users found in the database yet.")
else:
    # Add search box
    search = st.text_input("🔍 Search user by name:")
    if search:
        users = users[users["username"].str.contains(search, case=False, na=False)]

    # Add upload count column dynamically
    users["Total Uploads"] = users["id"].apply(get_upload_count)

    # Display users in table
    st.dataframe(users, use_container_width=True)

    # Optional delete user
    st.subheader("🗑️ Manage Users")
    user_to_delete = st.selectbox("Select user to delete", options=["None"] + users["username"].tolist())
    if user_to_delete != "None":
        if st.button("Delete User"):
            user_id = users.loc[users["username"] == user_to_delete, "id"].values[0]
            delete_user(user_id)
            st.success(f"✅ Deleted user '{user_to_delete}' successfully!")
            st.rerun()


st.markdown("---")
st.caption("Admin panel for AI Farm Assistant — built with Streamlit 🧩")