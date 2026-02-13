import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # Find the root directory relative to this file (utils/__init__.py)
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(utils_dir)
    csv_path = os.path.join(root_dir, "data", "max.csv")
    
    if os.path.exists(csv_path):
        try:
            # low_memory=False handles mixed types in clinical data
            return pd.read_csv(csv_path, low_memory=False)
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            return pd.DataFrame()
    else:
        st.error(f"Data file not found at: {csv_path}")
        return pd.DataFrame()

def check_password():
    # Your existing password logic here...
    pass