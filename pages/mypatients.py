import streamlit as st
import plotly.express as px
import pandas as pd
from utils import load_data, check_password

# --- PAGE SETUP ---
st.set_page_config(page_title="Clinic Overview", page_icon="📊", layout="wide")

# --- AUTH CHECK ---
if not check_password():
    st.stop()

st.title("📊 Clinic Executive Dashboard")
st.markdown("Real-time demographic and operational insights.")

# --- LOAD DATA ---
with st.spinner("Syncing with Live Google Sheet..."):
    df = load_data()

if df.empty:
    st.warning("⚠️ Connected to Google Sheet, but no data found.")
    st.stop()

# --- LOGICAL PRE-PROCESSING ---
# 1. Normalize Column Names (Upper case & Strip spaces)
df.columns = df.columns.str.strip().str.upper()

# 2. Smart Timestamp Detection
# Look for any column containing 'TIME' or 'DATE' to identify the timestamp
time_col = next((col for col in df.columns if 'TIME' in col or 'DATE' in col), None)

if time_col:
    df['DATE_OBJ'] = pd.to_datetime(df[time_col], errors='coerce')
    df['MONTH_YEAR'] = df['DATE_OBJ'].dt.to_period('M').astype(str)
    has_time_data = True
else:
    has_time_data = False

# 3. Gender Standardization
if 'GENDER' in df.columns:
    # Standardize: "Male", "male ", "MALE" -> "Male"
    df['GENDER'] = df['GENDER'].astype(str).str.strip().str.title()
    # Handle missing/weird values
    df['GENDER'] = df['GENDER'].replace({'Nan': 'Unknown', 'None': 'Unknown', '': 'Unknown'})

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Dashboard Filters")

if 'GENDER' in df.columns:
    gender_opts = sorted(list(df['GENDER'].unique()))
    selected_gender = st.sidebar.multiselect("Filter Gender", gender_opts, default=gender_opts)
    
    if selected_gender:
        df = df[df['GENDER'].isin(selected_gender)]

# --- SECTION 1: METRICS ---
st.subheader("🏥 Operational KPIs")
k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Patients", f"{len(df):,}")

if 'GENDER' in df.columns:
    m_count = len(df[df['GENDER'] == 'Male'])
    f_count = len(df[df['GENDER'] == 'Female'])
    k2.metric("Gender Split", f"{m_count}M : {f_count}F")

if 'AGE' in df.columns:
    avg_age = pd.to_numeric(df['AGE'], errors='coerce').mean()
    k3.metric("Avg Age", f"{avg_age:.1f} Yrs")

if 'DIAGNOSIS' in df.columns:
    top_diag = df['DIAGNOSIS'].mode()[0] if not df['DIAGNOSIS'].empty else "N/A"
    k4.metric("Top Condition", str(top_diag)[:15])

st.divider()

# --- SECTION 2: TRENDS (If Time Data Exists) ---
if has_time_data:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📈 Recruitment Trend")
        growth = df.groupby('MONTH_YEAR').size().reset_index(name='Patients')
        fig = px.area(growth, x='MONTH_YEAR', y='Patients', title="Monthly Patient Volume")
        fig.update_traces(line_color='#0083B8')
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.subheader("⚧ Demographics")
        if 'GENDER' in df.columns:
            fig2 = px.pie(df, names='GENDER', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig2, use_container_width=True)

# --- SECTION 3: CLINICAL INSIGHTS ---
st.subheader("🧬 Clinical Profile")
r1, r2 = st.columns(2)

with r1:
    if 'AGE' in df.columns:
        st.write("**Age Distribution**")
        fig3 = px.histogram(df, x='AGE', color='GENDER' if 'GENDER' in df.columns else None, nbins=20)
        st.plotly_chart(fig3, use_container_width=True)

with r2:
    if 'DIAGNOSIS' in df.columns:
        st.write("**Top 10 Diagnoses**")
        diag_counts = df['DIAGNOSIS'].value_counts().head(10).sort_values(ascending=True)
        fig4 = px.bar(x=diag_counts.values, y=diag_counts.index, orientation='h')
        st.plotly_chart(fig4, use_container_width=True)