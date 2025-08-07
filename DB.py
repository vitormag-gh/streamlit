import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ---------------------------
# Session State Setup
# ---------------------------
if "connected" not in st.session_state:
    st.session_state.connected = False
if "supabase" not in st.session_state:
    st.session_state.supabase = None
if "show_data" not in st.session_state:
    st.session_state.show_data = False
if "data" not in st.session_state:
    st.session_state.data = None

# ---------------------------
# Connect Function
# ---------------------------
def connect_to_db():
    url: str = st.secrets['supbase']['supabase_url']
    key: str = st.secrets['supbase']['supabase_key']
    client: Client = create_client(url, key)
    st.session_state.supabase = client
    st.session_state.connected = True
    st.success("✅ Connected to Supabase")

# ---------------------------
# Disconnect Function
# ---------------------------
def disconnect_db():
    st.session_state.supabase = None
    st.session_state.connected = False
    st.session_state.show_data = False
    st.session_state.data = None
    st.success("🔌 Disconnected from Supabase")

# ---------------------------
# Query Function
# ---------------------------
def run_query():
    response = st.session_state.supabase.table('car_parts_monthly_sales').select("*").execute()
    return pd.json_normalize(response.data)

# ---------------------------
# UI Layout
# ---------------------------
st.title("📦 Car Parts Dashboard")

# Connect/Disconnect buttons
col1, col2 = st.columns(2)
with col1:
    if not st.session_state.connected:
        if st.button("🔗 Connect to Database"):
            connect_to_db()
with col2:
    if st.session_state.connected:
        if st.button("🔌 Disconnect"):
            disconnect_db()

# Reload / Clear buttons
if st.session_state.connected:
    col3, col4 = st.columns(2)
    with col3:
        if st.button("🔄 Reload Data"):
            st.session_state.data = run_query()
            st.session_state.show_data = True
    with col4:
        if st.button("🧹 Clear Output"):
            st.session_state.show_data = False

# ---------------------------
# Show and Filter Data
# ---------------------------
if st.session_state.connected and st.session_state.show_data and st.session_state.data is not None:
    df = st.session_state.data

    # Display raw data preview
    st.subheader("📄 Raw Data")
    st.dataframe(df)

    # Column selector for filtering
    st.subheader("🔍 Filter Data")
    filter_col = st.selectbox("Choose a column to filter by:", df.columns)

    # Dynamic filter based on data type
    if pd.api.types.is_numeric_dtype(df[filter_col]):
        min_val = float(df[filter_col].min())
        max_val = float(df[filter_col].max())
        selected_range = st.slider(f"Select range for {filter_col}", min_val, max_val, (min_val, max_val))
        filtered_df = df[(df[filter_col] >= selected_range[0]) & (df[filter_col] <= selected_range[1])]

    elif pd.api.types.is_datetime64_any_dtype(df[filter_col]):
        min_date = df[filter_col].min()
        max_date = df[filter_col].max()
        selected_dates = st.date_input(f"Select date range for {filter_col}", [min_date, max_date])
        if len(selected_dates) == 2:
            filtered_df = df[(df[filter_col] >= pd.to_datetime(selected_dates[0])) &
                             (df[filter_col] <= pd.to_datetime(selected_dates[1]))]
        else:
            filtered_df = df

    else:  # Assume categorical
        unique_vals = df[filter_col].dropna().unique()
        selected_vals = st.multiselect(f"Select values for {filter_col}", unique_vals, default=list(unique_vals))
        filtered_df = df[df[filter_col].isin(selected_vals)]

    # Display filtered data
    st.subheader("📊 Filtered Data")
    st.dataframe(filtered_df)
