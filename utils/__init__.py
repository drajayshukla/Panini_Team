import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # Get the directory where this __init__.py is located (utils folder)
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to root, then into data/max.csv
    root_dir = os.path.dirname(utils_dir)
    csv_path = os.path.join(root_dir, "data", "max.csv")
    
    if os.path.exists(csv_path):
        try:
            # Using low_memory=False for mixed clinical data types
            return pd.read_csv(csv_path, low_memory=False)
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            return pd.DataFrame()
    else:
        st.error(f"CSV file not found at: {csv_path}")
        return pd.DataFrame()