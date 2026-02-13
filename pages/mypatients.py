import streamlit as st
import pandas as pd
import sys
import os

# --- 1. SYSTEM PATH & AUTH ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from utils import load_data, check_password

st.set_page_config(page_title="Endo Registry", layout="wide")

if not check_password():
    st.stop()

# --- 2. DATA LOADING ---
df = load_data()

if df.empty:
    st.warning("⚠️ No data found. Please ensure 'data/refined_patient_registry.csv' exists.")
    st.stop()

# Ensure headers are clean (First Principle: Data Integrity)
df.columns = [col.strip() for col in df.columns]

st.title("🏥 Patient Registry & Clinical Search")

# --- 3. SIDEBAR: CLINICAL SEARCH & FILTERS ---
st.sidebar.header("🔍 Search & Filters")
global_search = st.sidebar.text_input("Search Name, ID, or Diagnosis", "")

# Keyword Filter (Research Tags)
if 'KEY WORD' in df.columns:
    raw_keywords = df['KEY WORD'].dropna().unique()
    all_tags = sorted(list(set([t.strip() for item in raw_keywords for t in str(item).split(',')])))
    selected_tags = st.sidebar.multiselect("Research Categories", all_tags)

# NEW: Metabolic Sliders (Possible thanks to Refined CSV)
st.sidebar.divider()
st.sidebar.subheader("📈 Metabolic Range")
if 'BMI_VAL' in df.columns:
    bmi_range = st.sidebar.slider("BMI Filter", 10.0, 50.0, (10.0, 50.0))

# --- 4. FILTERING ENGINE ---
filtered_df = df.copy()

if global_search:
    mask = (
        filtered_df['FILE UPLOAD'].astype(str).str.contains(global_search, case=False, na=False) |
        filtered_df['MAX ID'].astype(str).str.contains(global_search, case=False, na=False) |
        filtered_df['DIAGNOSIS'].astype(str).str.contains(global_search, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

if 'KEY WORD' in df.columns and selected_tags:
    tag_pattern = '|'.join(selected_tags)
    filtered_df = filtered_df[filtered_df['KEY WORD'].str.contains(tag_pattern, case=False, na=False)]

if 'BMI_VAL' in filtered_df.columns:
    filtered_df = filtered_df[(filtered_df['BMI_VAL'].between(bmi_range[0], bmi_range[1])) | (filtered_df['BMI_VAL'].isna())]

# --- 5. DASHBOARD UI ---
m1, m2, m3 = st.columns(3)
m1.metric("Patients Found", len(filtered_df))
if 'BMI_VAL' in filtered_df.columns:
    m2.metric("Avg BMI", f"{filtered_df['BMI_VAL'].mean():.1f}")
if 'AGE' in filtered_df.columns:
    # Convert age string "61 Years" to numeric for mean calculation
    age_numeric = pd.to_numeric(filtered_df['AGE'].astype(str).str.extract('(\d+)')[0], errors='coerce')
    m3.metric("Avg Age", f"{age_numeric.mean():.1f}")

# Main Data Table (EHR Style)
view_cols = ['MAX ID', 'FILE UPLOAD', 'AGE', 'GENDER', 'BMI_VAL', 'BP_MMHG', 'DIAGNOSIS', 'KEY WORD']
# Only display columns that actually exist
available_cols = [c for c in view_cols if c in filtered_df.columns]
st.dataframe(filtered_df[available_cols], use_container_width=True)

st.divider()

# --- 6. DETAILED CLINICAL CARDS ---
st.subheader("📋 Comprehensive Clinical View")

if filtered_df.empty:
    st.info("No matching records.")
else:
    for _, row in filtered_df.iterrows():
        label = f"👤 {row.get('FILE UPLOAD', 'N/A')} | ID: {row.get('MAX ID', 'N/A')} | {row.get('DIAGNOSIS', 'No Diagnosis')[:40]}..."
        with st.expander(label):
            c1, c2, c3 = st.columns([1, 1.2, 1.2])
            
            with c1:
                st.markdown("**Demographics**")
                st.write(f"**Age/Sex:** {row.get('AGE', 'N/A')} / {row.get('GENDER', 'N/A')}")
                st.write(f"**Contact:** {row.get('XXXXXXXXCONTACT NUMBER', 'N/A')}")
                st.info(f"**Research Tags:** {row.get('KEY WORD', 'None')}")
                
            with c2:
                st.markdown("**Metabolic Profile**")
                st.write(f"**BMI:** {row.get('BMI_VAL', 'N/A')}")
                st.write(f"**BP:** {row.get('BP_MMHG', 'N/A')}")
                st.write(f"**RBS:** {row.get('RBS_MG_DL', 'N/A')} mg/dL")
                st.warning("**Case Notes**")
                st.write(row.get('CASE_NOTES', 'No notes'))

            with c3:
                st.success("**Prescription Summary**")
                st.write(row.get('PRESCRIPTION', 'N/A'))
                st.markdown("**Clinical Observations**")
                st.write(row.get('CLINICAL NOTES', 'N/A'))