import streamlit as st
# Now this import will work perfectly because we fixed __init__.py
from utils import check_password, load_data 

st.set_page_config(page_title="Panini-DM Dashboard", page_icon="🏥", layout="wide")

st.title("🏥 Panini-DM: Educator Dashboard")

if not check_password():
    st.stop()

# Load data to ensure connection works
df = load_data()

if not df.empty:
    st.success(f"✅ System Online. {len(df)} Patient Records Loaded.")
    st.markdown("### Select a tool from the sidebar to begin.")
else:
    st.warning("Connected to Google Sheets, but no data found.")