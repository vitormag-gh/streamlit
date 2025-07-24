# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 21:09:22 2025

@author: riskf
"""
#%%
# =====================
# 📦 Imports
# =====================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# =====================

df_csv = pd.read_csv("C:\\Users\\riskf\\OneDrive\\Documents\\Courses\\Taken\\Python - Machine Learning Model Deployment with Streamlit\\12_dashboard_capstone\\data\\quarterly_canada_population.csv")


# 🔗 Load Dataset
# =====================
# Public dataset URL from GitHub
URL = "https://raw.githubusercontent.com/marcopeix/MachineLearningModelDeploymentwithStreamlit/master/12_dashboard_capstone/data/quarterly_canada_population.csv"

# Load data with correct dtypes for better memory performance
df = pd.read_csv(URL, dtype={
    'Quarter': str, 
    'Canada': np.int32,
    'Newfoundland and Labrador': np.int32,
    'Prince Edward Island': np.int32,
    'Nova Scotia': np.int32,
    'New Brunswick': np.int32,
    'Quebec': np.int32,
    'Ontario': np.int32,
    'Manitoba': np.int32,
    'Saskatchewan': np.int32,
    'Alberta': np.int32,
    'British Columbia': np.int32,
    'Yukon': np.int32,
    'Northwest Territories': np.int32,
    'Nunavut': np.int32
})

# =====================
# 🧾 Page Title & Info
# =====================
st.title("📈 Population Trends Across Canada")
st.markdown("Data Source: [Statistics Canada](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000901)")

# Show full data table in an expandable section
with st.expander("🔍 View Full Dataset"):
    st.dataframe(df)

# =====================
# 📋 Selection Form
# =====================
with st.form("population-form"):
    st.subheader("Choose your parameters")

    # Split into 3 columns for better layout
    col1, col2, col3 = st.columns(3)

    # Column 1: Start Date
    with col1:
        st.markdown("**Start Date**")
        start_quarter = st.selectbox("Quarter", ["Q1", "Q2", "Q3", "Q4"], index=2, key="start_q")
        start_year = st.slider("Year", min_value=1991, max_value=2023, value=1991, step=1, key="start_y")

    # Column 2: End Date
    with col2:
        st.markdown("**End Date**")
        end_quarter = st.selectbox("Quarter", ["Q1", "Q2", "Q3", "Q4"], index=0, key="end_q")
        end_year = st.slider("Year", min_value=1991, max_value=2023, value=2023, step=1, key="end_y")

    # Column 3: Target Location
    with col3:
        st.markdown("**Target Location**")
        target = st.selectbox("Province/Territory", options=df.columns[1:], index=0)

    # Submit button
    submit_btn = st.form_submit_button("🔎 Analyze", type="primary")

# Format date string (e.g., "Q2 2020")
start_date = f"{start_quarter} {start_year}"
end_date = f"{end_quarter} {end_year}"

# =====================
# 🧠 Helper Functions
# =====================

# Converts date string like 'Q3 2020' to a float like 2020.50 for comparison
def format_date_for_comparison(date_str):
    quarter, year = date_str.split()
    year = float(year)
    if quarter == "Q1":
        return year
    elif quarter == "Q2":
        return year + 0.25
    elif quarter == "Q3":
        return year + 0.50
    elif quarter == "Q4":
        return year + 0.75

# Checks if end date is before start date
def end_before_start(start, end):
    return format_date_for_comparison(start) > format_date_for_comparison(end)

# Displays dashboard with analysis tabs
def display_dashboard(start_date, end_date, target):
    # Tabs for population change and comparison
    tab1, tab2 = st.tabs(["📊 Population Change", "📈 Compare Provinces"])

    # ========== Tab 1: Population Change ==========
    with tab1:
        st.subheader(f"{target} — from {start_date} to {end_date}")

        # Left column: Metrics
        col1, col2 = st.columns(2)
        with col1:
            initial = df.loc[df['Quarter'] == start_date, target].item()
            final = df.loc[df['Quarter'] == end_date, target].item()

            # Calculate change percentage
            percentage_diff = round((final - initial) / initial * 100, 2)
            delta = f"{percentage_diff}%"

            # Show metrics
            st.metric(label=start_date, value=initial)
            st.metric(label=end_date, value=final, delta=delta)

        # Right column: Line chart
        with col2:
            start_idx = df[df['Quarter'] == start_date].index.item()
            end_idx = df[df['Quarter'] == end_date].index.item()
            filtered_df = df.iloc[start_idx:end_idx+1]

            fig, ax = plt.subplots()
            ax.plot(filtered_df['Quarter'], filtered_df[target], marker='o', color='tab:blue')
            ax.set_xlabel('Time')
            ax.set_ylabel('Population')
            ax.set_title(f"{target} Population Over Time")
            ax.set_xticks([filtered_df['Quarter'].iloc[0], filtered_df['Quarter'].iloc[-1]])
            fig.autofmt_xdate()
            st.pyplot(fig)

    # ========== Tab 2: Compare ==========
    with tab2:
        st.subheader(f"Compare {target} with other regions")
        all_targets = st.multiselect("Choose provinces/territories to compare", options=df.columns[1:], default=[target])

        fig, ax = plt.subplots()
        for region in all_targets:
            ax.plot(filtered_df['Quarter'], filtered_df[region], label=region)
        ax.set_xlabel("Time")
        ax.set_ylabel("Population")
        ax.set_title("Regional Population Trends")
        ax.set_xticks([filtered_df['Quarter'].iloc[0], filtered_df['Quarter'].iloc[-1]])
        ax.legend()
        fig.autofmt_xdate()
        st.pyplot(fig)

# =====================
# 🚦 Control Flow
# =====================
# After form submission
if submit_btn:
    if start_date not in df['Quarter'].tolist() or end_date not in df['Quarter'].tolist():
        st.error("❌ Invalid selection. No data found for the chosen quarter and year.")
    elif end_before_start(start_date, end_date):
        st.error("⚠️ End date must come **after** start date.")
    else:
        # Save all important state for downstream use
        st.session_state["form_submitted"] = True
        st.session_state["start_date"] = start_date
        st.session_state["end_date"] = end_date
        st.session_state["target"] = target

        # Get filtered range of rows for selected quarters
        start_idx = df[df['Quarter'] == start_date].index.item()
        end_idx = df[df['Quarter'] == end_date].index.item()
        st.session_state["filtered_df"] = df.iloc[start_idx:end_idx+1]

# Only show dashboard if form has been submitted
if st.session_state.get("form_submitted", False):
    display_dashboard(
        start_date=st.session_state["start_date"],
        end_date=st.session_state["end_date"],
        target=st.session_state["target"]
    )
with st.container():
    st.info("Click below to clear your selection and restart the dashboard.")
    if st.button("🔄 Reset and Start Over"):
        st.session_state.clear()
        st.rerun()

