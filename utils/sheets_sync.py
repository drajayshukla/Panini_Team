import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Define the scope
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_sheet_connection():
    """Authenticates with Google Sheets and returns the client."""
    # Check if secrets exist
    if "gcp_service_account" not in st.secrets:
        st.error("Secrets not found! Please check your Streamlit Cloud settings.")
        st.stop()
    
    try:
        credentials_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(
            credentials_dict, scopes=SCOPES
        )
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Authentication Error: {e}")
        st.stop()