import streamlit as st
import pandas as pd
import os

DATA_PATH = "data/max.csv"

@st.cache_data(ttl=600)
def load_data():
    if not os.path.exists(DATA_PATH):
        # This will show the error but not crash the app
        return pd.DataFrame()
    
    try:
        # We use low_memory=False because medical data often has mixed types
        df = pd.read_csv(DATA_PATH, low_memory=False)
        
        # Clean column names (strip spaces, but keep case for matching your CSV)
        df.columns = [col.strip() for col in df.columns]
        
        # Standardize Gender for filtering
        if 'GENDER' in df.columns:
            df['GENDER'] = df['GENDER'].astype(str).str.strip().str.upper()
            
        return df
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return pd.DataFrame()