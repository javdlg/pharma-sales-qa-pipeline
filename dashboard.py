# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import json
# pyrefly: ignore [missing-import]
import plotly.express as px
import os

st.set_page_config(page_title="Pharma QA Dashboard", layout="wide", page_icon="💊")

st.title("💊 Pharma Sales Data Quality Assurance Dashboard")
st.markdown("This dashboard visualizes the results of the automated QA pipeline, highlighting the 'firewall' effectiveness in preventing corrupted data from entering the analytical data warehouse.")

# Load Data
@st.cache_data
def load_summary():
    with open("logs/qa_summary.json", "r") as f:
        return json.load(f)

@st.cache_data
def load_rejections():
    if os.path.exists("logs/qa_rejections.csv"):
        return pd.read_csv("logs/qa_rejections.csv")
    return pd.DataFrame()

try:
    summary = load_summary()
    df_rejections = load_rejections()
except FileNotFoundError:
    st.error("Pipeline logs not found. Please run `python main.py` first to generate the QA reports.")
    st.stop()

# --- Top-Level KPIs ---
st.header("Executive QA Summary")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Raw Records Received", f"{summary['initial_rows']:,}")
col2.metric("Clean Records Accepted", f"{summary['final_rows']:,}")
col3.metric("Records Rejected", f"{summary['total_rejected']:,}", delta="- Anomalies Detected", delta_color="inverse")
col4.metric("Retention Rate", f"{summary['retention_percentage']}%")

st.divider()

# --- Detailed Analytics ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Rejection Breakdown")
    if not df_rejections.empty:
        st.markdown("##### Frequent Anomalies")
        rejection_counts = df_rejections['rejection_reason'].value_counts()
        
        # Display each rejection reason as a classic KPI Card
        for reason, count in rejection_counts.items():
            st.metric(label=f"⚠️ {reason}", value=f"{count:,} records")
    else:
        st.info("No rejections found. The dataset was perfectly clean.")

with col_right:
    st.subheader("Rejections by ATC Code")
    if not df_rejections.empty:
        atc_counts = df_rejections.groupby('codigo_atc').size().reset_index(name='Count')
        atc_counts = atc_counts.sort_values('Count', ascending=True)
        
        fig_bar = px.bar(
            atc_counts,
            x='Count',
            y='codigo_atc',
            orientation='h',
            text='Count',
            color_discrete_sequence=['#ff6b6b']
        )
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(xaxis_title="Number of Rejected Rows", yaxis_title="ATC Code", margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No rejections found.")

st.divider()

# --- Audit Log View ---
st.subheader("Automated Audit Log")
with st.expander("View detailed pipeline execution log"):
    if 'audit_log' in summary and summary['audit_log']:
        for entry in summary['audit_log']:
            st.write(f"- {entry}")
    else:
        st.write("No warnings or errors reported during extraction.")

# --- Raw Rejections Explorer ---
st.subheader("Raw Rejections Explorer (For Operations Investigation)")
st.markdown("Use this table to investigate specific corrupted records flagged by the pipeline. This data can be exported and sent to the point-of-sale franchises for root-cause analysis.")
if not df_rejections.empty:
    st.dataframe(df_rejections, use_container_width=True)
else:
    st.success("The pipeline did not flag any rows for investigation.")
