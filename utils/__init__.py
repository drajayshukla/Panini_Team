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

# --- 2. GOOGLE AUTHENTICATION ---
@st.cache_resource
# --- 2. GOOGLE AUTHENTICATION ---
@st.cache_resource
def get_gspread_client():
    """Authenticates using the secrets file."""
    if "gcp_service_account" not in st.secrets:
        st.error("Secrets not found! Check .streamlit/secrets.toml")
        st.stop()
    
    # 1. Load the secrets into a dictionary
    credentials_dict = dict(st.secrets["gcp_service_account"])

    # 🟢 THE FIX: Force-replace literal \n with actual newlines
    credentials_dict["private_key"] = credentials_dict["private_key"].replace("\\n", "\n")
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # 2. Authenticate using the fixed dictionary
    creds = Credentials.from_service_account_info(
        credentials_dict, scopes=scopes
    )
    return gspread.authorize(creds)
# --- 3. DATA LOADER ---
@st.cache_data(ttl=600)
def load_data():
    """Fetches data from Google Sheets and cleans it."""
    try:
        client = get_gspread_client()
        # Open the sheet by Name (easier than ID)
        sheet = client.open(SHEET_NAME).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # --- CLEANING ---
        df.columns = df.columns.str.strip().str.upper()
        
        # Fix Mobile Number Column
        contact_col = next((col for col in df.columns if 'CONTACT' in col), None)
        if contact_col:
            df.rename(columns={contact_col: 'MOBILE_NUMBER'}, inplace=True)
            
        # Fix Age
        if 'AGE' in df.columns:
            df['AGE'] = pd.to_numeric(df['AGE'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()