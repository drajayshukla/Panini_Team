import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    # Find the absolute path to the 'paniniteam' folder
    # This works both locally in IDX and on Streamlit Cloud
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_path, "data", "refined_patient_registry.csv")
    
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, low_memory=False)
            
            # Convert vital signs to numeric for the sidebar filters
            # This is essential for the sliders to work
            numeric_vitals = ['WEIGHT_KG', 'BMI_VAL', 'RBS_MG_DL', 'AGE']
            for col in numeric_vitals:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
            return pd.DataFrame()
    else:
        # Debugging message to show the exact path being searched
        st.error(f"Registry not found. Searched path: {csv_path}")
        return pd.DataFrame()