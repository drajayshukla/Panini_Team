import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    # This finds the absolute path of the 'paniniteam' folder
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # We use 'refined_patient_registry.csv' which we just created
    csv_path = os.path.join(base_path, "data", "refined_patient_registry.csv")
    
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, low_memory=False)
            # Ensure numeric columns are actually numeric for the sidebar sliders
            numeric_cols = ['WEIGHT_KG', 'BMI_VAL', 'RBS_MG_DL', 'AGE']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            return pd.DataFrame()
    else:
        st.error(f"File NOT FOUND at: {csv_path}")
        return pd.DataFrame()

def check_password():
    # Keep your existing password logic here
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True
    
    st.title("🔐 Secure Clinical Access")
    pwd = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if pwd == "EndoMaster2026": 
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("Incorrect Password")
    return False