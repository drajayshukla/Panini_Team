import streamlit as st
import pandas as pd
import os

DATA_PATH = "data/max.csv"

@st.cache_data
def load_data():
    # Use absolute path relative to this file's location
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_path, "data", "max.csv")
    
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    else:
        st.error(f"CSV not found at {csv_path}")
        return pd.DataFrame()