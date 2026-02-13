import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import load_data, check_password

# --- PAGE SETUP ---
st.set_page_config(page_title="Clinic Overview", page_icon="📊", layout="wide")

# --- AUTH CHECK ---
if not check_password():
    st.stop()

# --- HEADER ---
st.title("📊 Clinic Executive Dashboard")
st.markdown("Real-time demographic and operational insights.")

# --- LOAD DATA ---
with st.spinner("Analyzing clinical data..."):
    df = load_data()

if df.empty:
    st.warning("No data available to analyze.")
    st.stop()

# --- PRE-PROCESSING FOR ANALYTICS ---
# 1. Convert Timestamp for Time Series
if 'TIMESTAMP' in df.columns:
    df['DATE'] = pd.to_datetime(df['TIMESTAMP'], errors='coerce')
    df['MONTH_YEAR'] = df['DATE'].dt.to_period('M').astype(str)

# 2. Gender Standardization
if 'GENDER' in df.columns:
    df['GENDER'] = df['GENDER'].str.strip().str.title()  # Fixes "MALE", "Male ", "male"

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Dashboard Filters")
selected_gender = st.sidebar.multiselect(
    "Filter Gender",
    options=df['GENDER'].unique(),
    default=df['GENDER'].unique()
)

# Apply Filter
df_filtered = df[df['GENDER'].isin(selected_gender)]

# --- SECTION 1: HIGH-LEVEL KPI METRICS ---
st.subheader("🏥 Operational KPIs")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        "Total Patient Registry", 
        f"{len(df_filtered):,}", 
        delta="Live Count",
        delta_color="off"
    )

with kpi2:
    # Calculate Male/Female Ratio
    m_count = len(df_filtered[df_filtered['GENDER'] == 'Male'])
    f_count = len(df_filtered[df_filtered['GENDER'] == 'Female'])
    ratio = f"{m_count}:{f_count}"
    st.metric("Gender Ratio (M:F)", ratio)

with kpi3:
    if 'AGE' in df_filtered.columns:
        avg_age = df_filtered['AGE'].mean()
        st.metric("Average Patient Age", f"{avg_age:.1f} Years")

with kpi4:
    # Most Common Condition
    if 'DIAGNOSIS' in df_filtered.columns:
        top_diag = df_filtered['DIAGNOSIS'].mode()[0] if not df_filtered['DIAGNOSIS'].empty else "N/A"
        st.metric("Top Diagnosis", str(top_diag)[:15] + "...")

st.divider()

# --- SECTION 2: RECRUITMENT & GROWTH (TIME SERIES) ---
# Only show this if Timestamp exists
if 'TIMESTAMP' in df.columns:
    col_growth, col_demo = st.columns([2, 1])
    
    with col_growth:
        st.subheader("📈 Patient Recruitment Trend")
        # Group by Month
        growth_data = df_filtered.groupby('MONTH_YEAR').size().reset_index(name='Patients')
        
        fig_growth = px.area(
            growth_data, 
            x='MONTH_YEAR', 
            y='Patients',
            title="Monthly Patient Volume",
            markers=True,
            color_discrete_sequence=['#0083B8'] # Medical Blue
        )
        fig_growth.update_layout(xaxis_title="Month", yaxis_title="New Patients", template="plotly_white")
        st.plotly_chart(fig_growth, use_container_width=True)

    with col_demo:
        st.subheader("⚧ Gender Split")
        fig_pie = px.pie(
            df_filtered, 
            names='GENDER', 
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

# --- SECTION 3: CLINICAL DEMOGRAPHICS ---
st.subheader("🧬 Population Demographics")

c1, c2 = st.columns(2)

with c1:
    st.write("**Age Distribution by Gender**")
    if 'AGE' in df_filtered.columns:
        # Histogram with Gender Overlay
        fig_age = px.histogram(
            df_filtered, 
            x="AGE", 
            color="GENDER", 
            nbins=20, 
            marginal="box", # Adds boxplot on top
            hover_data=df_filtered.columns,
            color_discrete_map={"Male": "#636EFA", "Female": "#EF553B"}
        )
        fig_age.update_layout(barmode='overlay', template="plotly_white")
        fig_age.update_traces(opacity=0.75)
        st.plotly_chart(fig_age, use_container_width=True)

with c2:
    st.write("**Top 10 Diagnoses (Prevalence)**")
    if 'DIAGNOSIS' in df_filtered.columns:
        # Horizontal Bar Chart for readability
        diag_counts = df_filtered['DIAGNOSIS'].value_counts().head(10).sort_values(ascending=True)
        
        fig_diag = px.bar(
            x=diag_counts.values,
            y=diag_counts.index,
            orientation='h',
            text=diag_counts.values,
            color=diag_counts.values,
            color_continuous_scale="Blues"
        )
        fig_diag.update_layout(xaxis_title="Count", yaxis_title=None, showlegend=False, template="plotly_white")
        st.plotly_chart(fig_diag, use_container_width=True)

# --- SECTION 4: DATA QUALITY HEALTH CHECK ---
with st.expander("🛠 Data Quality Health Check"):
    st.write("Monitoring missing fields to ensure registry integrity.")
    
    missing_age = df_filtered['AGE'].isna().sum()
    missing_diag = df_filtered['DIAGNOSIS'].replace('', pd.NA).isna().sum()
    missing_contact = df_filtered['MOBILE_NUMBER'].isna().sum() if 'MOBILE_NUMBER' in df_filtered.columns else 0
    
    cq1, cq2, cq3 = st.columns(3)
    cq1.caption(f"Missing Age: {missing_age}")
    cq2.caption(f"Missing Diagnosis: {missing_diag}")
    cq3.caption(f"Missing Contacts: {missing_contact}")