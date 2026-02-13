import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURATION ---
SHEET_NAME = "MAX ENDOCRINOLOGY DATA (Responses)"
APP_PASSWORD = "EndoMaster2026"

# --- 1. PASSWORD FUNCTION ---
def check_password():
    """Simple password protection for the app."""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.markdown("## 🔐 Login Required")
    pwd = st.text_input("Enter Access Password", type="password")
    if st.button("Login"):
        if pwd == APP_PASSWORD:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("Incorrect Password")
    return False

# --- 2. GOOGLE AUTHENTICATION (WITH FIX) ---
@st.cache_resource
def get_gspread_client():
    """Authenticates using secrets and repairs PEM formatting."""
    if "gcp_service_account" not in st.secrets:
        st.error("Secrets missing from Streamlit Cloud Settings!")
        st.stop()
    
    # 1. Convert secrets to a dictionary
    creds_dict = dict(st.secrets["gcp_service_account"])

    # 🟢 FIX FOR: InvalidData(InvalidPadding)
    # This converts literal "\n" text into real line breaks for the PEM reader
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google Auth Error: {e}")
        st.stop()

@st.cache_data(ttl=600)
def load_data():
    """Fetches data from your specific Google Sheet ID."""
    try:
        client = get_gspread_client()
        # 🟢 YOUR SPECIFIC SHEET ID
        SHEET_ID = "1tvbgS5n-_CzgELdgM_jWNe-qot14ynGXmX67D_f-b8U"
        sheet = client.open_by_key(SHEET_ID).sheet1
        
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Normalize column names to avoid errors
        df.columns = df.columns.str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()