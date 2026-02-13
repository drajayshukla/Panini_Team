import streamlit as st
import pandas as pd
from utils import load_data, check_password

st.set_page_config(page_title="Patient Search", layout="wide")

if not check_password():
    st.stop()

st.title("🔎 Clinical Registry Search")
df = load_data()

if df.empty:
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")
search_query = st.sidebar.text_input("Global Search (Name, ID, Diagnosis)", "")

# Keyword Filter (Multi-select)
if 'KEY WORD' in df.columns:
    # Extract unique keywords from the comma-separated strings
    all_keywords = set()
    df['KEY WORD'].dropna().str.split(',').apply(lambda x: [all_keywords.add(i.strip()) for i in x])
    selected_keywords = st.sidebar.multiselect("Filter by Research Category", options=sorted(list(all_keywords)))

# --- SEARCH LOGIC ---
filtered_df = df.copy()

if search_query:
    # Search across all columns
    mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
    filtered_df = filtered_df[mask]

if 'KEY WORD' in df.columns and selected_keywords:
    # Filter for rows that contain any of the selected keywords
    pattern = '|'.join(selected_keywords)
    filtered_df = filtered_df[filtered_df['KEY WORD'].str.contains(pattern, na=False, case=False)]

# --- DISPLAY RESULTS ---
st.metric("Patients Found", len(filtered_df))

# Data Table with specific column selection for readability
cols_to_show = ['TIMESTAMP', 'MAX ID', 'GENDER', 'AGE', 'DIAGNOSIS', 'KEY WORD']
st.dataframe(filtered_df[cols_to_show], use_container_width=True)

st.divider()

# --- DETAILED PATIENT VIEW ---
st.subheader("📋 Detailed Patient Records")
if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        with st.expander(f"Patient: {row.get('FILE UPLOAD', 'N/A')} | ID: {row.get('MAX ID', 'N/A')} | {row.get('DIAGNOSIS', 'No Diagnosis')}"):
            c1, c2 = st.columns(2)
            with c1:
                st.info("**Clinical Notes**")
                st.write(row.get('CLINICAL NOTES', 'N/A'))
                st.info("**Case Notes**")
                st.write(row.get('CASE NOTES', 'N/A'))
            with c2:
                st.warning("**Prescription Summary**")
                st.write(row.get('PRESCRIPTION', 'N/A'))
                st.success("**Research Tags**")
                st.write(row.get('KEY WORD', 'N/A'))
else:
    st.info("Adjust filters to view patient details.")