import streamlit as st
import pandas as pd
import sys
import os

# Add the parent directory (paniniteam) to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from utils import load_data, check_password

st.set_page_config(page_title="My Patients", layout="wide")
# ... rest of your code



if not check_password():
    st.stop()

st.title("🔎 Patient Registry & Keyword Search")

df = load_data()

if df.empty:
    st.warning("⚠️ data/max.csv is empty or missing. Please upload data.")
    st.stop()

# --- SEARCH & FILTER SECTION ---
st.sidebar.header("Filter & Search")
global_search = st.sidebar.text_input("Search Name, ID, or Diagnosis", "")

# Logic for Keyword extraction from 'KEY WORD' column
if 'KEY WORD' in df.columns:
    # Get unique keywords, handling comma-separated values
    keywords = df['KEY WORD'].dropna().unique()
    flat_keywords = sorted(list(set([k.strip() for sub in keywords for k in str(sub).split(',')])))
    selected_tag = st.sidebar.multiselect("Research Tags (Key Words)", flat_keywords)

# --- FILTERING LOGIC ---
filtered_df = df.copy()

if global_search:
    # Search across File Upload, Max ID, and Diagnosis
    mask = (
        filtered_df['FILE UPLOAD'].astype(str).str.contains(global_search, case=False, na=False) |
        filtered_df['MAX ID'].astype(str).str.contains(global_search, case=False, na=False) |
        filtered_df['DIAGNOSIS'].astype(str).str.contains(global_search, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

if 'KEY WORD' in df.columns and selected_tag:
    # Match any of the selected tags
    tag_mask = filtered_df['KEY WORD'].astype(str).apply(lambda x: any(tag in x for tag in selected_tag))
    filtered_df = filtered_df[tag_mask]

# --- DISPLAY ---
st.metric("Records Found", len(filtered_df))

# Table View
display_cols = ['TIMESTAMP', 'FILE UPLOAD', 'AGE', 'GENDER', 'MAX ID', 'DIAGNOSIS', 'KEY WORD']
st.dataframe(filtered_df[display_cols], use_container_width=True)

st.divider()

# --- DETAILED CARD VIEW ---
st.subheader("📋 Clinical Detail View")
for _, row in filtered_df.iterrows():
    with st.expander(f"📌 {row['FILE UPLOAD']} | ID: {row['MAX ID']} | {row['DIAGNOSIS']}"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Patient Demographics**")
            st.write(f"Age/Sex: {row['AGE']} / {row['GENDER']}")
            st.write(f"Contact: {row.get('XXXXXXXXCONTACT NUMBER', 'N/A')}")
            st.info("**Patient Profile**")
            st.text(row.get('PATIENT DETAILS', 'No details available'))
            
        with col2:
            st.markdown("**Clinical Assessment**")
            st.write(f"**Keywords:** {row['KEY WORD']}")
            st.success("**Prescription**")
            st.text(row.get('PRESCRIPTION', 'N/A'))
            st.warning("**Case Notes**")
            st.write(row.get('CASE NOTES', 'N/A'))