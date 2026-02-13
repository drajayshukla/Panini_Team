# app.py
import streamlit as st
import pandas as pd
from utils.sheets_sync import get_sheet_connection

st.title("Panini-DM: Educator Dashboard")

# 1. Fetch Cleaned Data from Google Sheets
conn = get_sheet_connection("YOUR_SHEET_ID")
data = conn.get_all_records()
df = pd.DataFrame(data)

# 2. Filter for "Unverified" entries for cleaning
pending = df[df['Verified'] == 'False']

st.subheader("Pending Data Verification")
st.table(pending[['Timestamp', 'Label', 'Value', 'SuggestedDose']])

# 3. Action: Verification Button
if st.button("Verify & Send Next Dose"):
    # Logic to update Google Sheet 'Verified' status to 'True'
    st.success("Dose confirmed and sent to WhatsApp!")