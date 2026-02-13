import streamlit as st
import pandas as pd
import sys
import os

# --- PATH CONFIGURATION ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from utils import load_data, check_password

st.set_page_config(page_title="My Patients", layout="wide")

if not check_password():
    st.stop()

st.title("🏥 Clinical Registry & Keyword Search")

# --- LOAD AND SANITIZE DATA ---
df = load_data()

if df.empty:
    st.warning("⚠️ No data found in data/max.csv. Please check the file path.")
    st.stop()

# 🟢 DATA SANITIZER: Remove trailing spaces from CSV headers
# Your CSV has "AGE ", "DIAGNOSIS ", etc. This fix is mandatory.
df.columns = [col.strip() for col in df.columns]

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Search Filters")
global_search = st.sidebar.text_input("Search Name, ID, or Diagnosis", "")

# Handle "KEY WORD" column (which contains commas like "DM, THYROID")
if 'KEY WORD' in df.columns:
    # Extract unique, clean tags
    raw_keywords = df['KEY WORD'].dropna().unique()
    all_tags = set()
    for item in raw_keywords:
        for tag in str(item).split(','):
            all_tags.add(tag.strip())
    
    selected_tags = st.sidebar.multiselect("Filter by Research Category", sorted(list(all_tags)))

# --- FILTERING ENGINE ---
filtered_df = df.copy()

# Filter by Global Search
if global_search:
    mask = (
        filtered_df['FILE UPLOAD'].astype(str).str.contains(global_search, case=False, na=False) |
        filtered_df['MAX ID'].astype(str).str.contains(global_search, case=False, na=False) |
        filtered_df['DIAGNOSIS'].astype(str).str.contains(global_search, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

# Filter by Research Tags
if 'KEY WORD' in df.columns and selected_tags:
    tag_pattern = '|'.join(selected_tags)
    filtered_df = filtered_df[filtered_df['KEY WORD'].str.contains(tag_pattern, case=False, na=False)]

# --- DASHBOARD UI ---
st.metric("Total Records Found", len(filtered_df))

# Main Data Table
# We use only specific columns for the overview table
overview_cols = ['TIMESTAMP', 'FILE UPLOAD', 'AGE', 'GENDER', 'MAX ID', 'DIAGNOSIS', 'KEY WORD']
st.dataframe(filtered_df[overview_cols], use_container_width=True)

st.divider()

# --- DETAILED CLINICAL VIEW ---
st.subheader("📋 Comprehensive Patient Details")

if filtered_df.empty:
    st.info("No patients found matching the search criteria.")
else:
    for _, row in filtered_df.iterrows():
        # Clean up empty values for the title
        p_name = row.get('FILE UPLOAD', 'N/A')
        p_id = row.get('MAX ID', 'N/A')
        p_diag = row.get('DIAGNOSIS', 'No Diagnosis Listed')
        
        # Expander for each patient
        with st.expander(f"👤 {p_name} | ID: {p_id} | {p_diag}"):
            c1, c2, c3 = st.columns([1, 1, 1])
            
            with c1:
                st.markdown("**Demographics**")
                st.write(f"**Age:** {row.get('AGE', 'N/A')}")
                st.write(f"**Gender:** {row.get('GENDER', 'N/A')}")
                st.write(f"**Mobile:** {row.get('XXXXXXXXCONTACT NUMBER', 'N/A')}")
                st.markdown("**Research Info**")
                st.info(f"Tags: {row.get('KEY WORD', 'None')}")

            with c2:
                st.markdown("**Patient Profile & Vitals**")
                # This handles the multi-line "PATIENT DETAILS" column
                details = row.get('PATIENT DETAILS', 'No entry')
                if str(details).strip() == "X" or str(details).strip() == "":
                    st.write("Detailed profile not available.")
                else:
                    st.text(details)

            with c3:
                st.markdown("**Clinical Notes & RX**")
                st.success("**Prescription Summary**")
                st.write(row.get('PRESCRIPTION', 'N/A'))
                st.warning("**Clinical Notes**")
                st.write(row.get('CLINICAL NOTES', 'N/A'))