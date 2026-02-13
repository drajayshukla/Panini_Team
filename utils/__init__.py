import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION ---
DATA_PATH = "data/max.csv"
APP_PASSWORD = "EndoMaster2026" 

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True

    st.title("🔐 Clinic Access")
    pwd = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if pwd == APP_PASSWORD:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("Invalid Password")
    return False

@st.cache_data(ttl=3600)
def load_data():
    if not os.path.exists(DATA_PATH):
        st.error(f"Data file not found at {DATA_PATH}")
        return pd.DataFrame()
    
    # Read CSV
    df = pd.read_csv(DATA_PATH)
    
    # Standardize Column Names
    df.columns = df.columns.str.strip().str.upper()
    
    # Basic Cleaning
    if 'TIMESTAMP' in df.columns:
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], errors='coerce')
    
    if 'GENDER' in df.columns:
        df['GENDER'] = df['GENDER'].str.strip().str.title()
        
    return df