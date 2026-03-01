"""
Streamlit Homework: Sales Dashboard
Run with: streamlit run dashboard.py

Build a complete sales dashboard with:
- Sidebar filters (date range, category, region, status)
- KPI metrics row
- Multiple chart tabs (Overview, By Category, By Region, Data)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- Page Config ---
st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")

# --- Load Data ---
DATA_PATH = Path(__file__).parent / "data" / "sales_dashboard.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["revenue"] = df["quantity"] * df["unit_price"]
    return df


df = load_data()

st.title("📊 Sales Dashboard")

# =====================================================================
# TODO 1: Sidebar Filters
# =====================================================================
# Create a sidebar with the following filters:
#
# 1. Date range:
#    - Use st.sidebar.date_input for a start date and an end date
#    - Default to the min and max dates in the dataset
#
# 2. Categories:
#    - Use st.sidebar.multiselect
#    - Options: all unique categories from the dataset
#    - Default: all selected
#
# 3. Regions:
#    - Use st.sidebar.multiselect
#    - Options: all unique regions from the dataset
#    - Default: all selected
#
# 4. Status:
#    - Use st.sidebar.multiselect
#    - Options: all unique statuses from the dataset
#    - Default: all selected

st.sidebar.header("Filters")

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()

#Date range
start_date = st.sidebar.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)

#categories
selected_categories = st.sidebar.multiselect(
    "Category:",
    options=df["category"].unique().tolist(),
    default=df["category"].unique().tolist(),
)
#regions
selected_regions = st.sidebar.multiselect(
    "Region:",
    options=df["region"].unique().tolist(),
    default=df["region"].unique().tolist(),
)
#status
selected_statuses = st.sidebar.multiselect(
    "Status:",
    options=df["status"].unique().tolist(),
    default=df["status"].unique().tolist(),
)


# =====================================================================
# TODO 2: Apply Filters
# =====================================================================
# Filter the DataFrame using all the sidebar values from TODO 1.
# Combine conditions with & (and).
# Store the result in a variable called `filtered`.
#
# Hint: df["order_date"].dt.date converts datetime to date for comparison

filtered = df[
    (df["order_date"].dt.date >= start_date)
    & (df["order_date"].dt.date <= end_date)
    & (df["category"].isin(selected_categories))
    & (df["region"].isin(selected_regions))
    & (df["status"].isin(selected_statuses))
]

st.caption(f"Showing {len(filtered)} of {len(df)} orders")



# =====================================================================
# TODO 3: KPI Metrics Row
# =====================================================================
# Create 4 columns using st.columns(4) and display these metrics:
#
# Column 1: Total Revenue — sum of filtered["revenue"], formatted as $X,XXX.XX
# Column 2: Total Orders — number of rows in filtered
# Column 3: Average Order Value — mean of filtered["revenue"], formatted as $X,XXX.XX
# Column 4: Top Category — category with the highest total revenue
#st.columns(4)` to create the layout

# Use `col.metric("Label", "Value")` to display each metric
# Format numbers with f-strings: `f"${value:,.2f}"`
# Find the top category: `filtered.groupby("category")["revenue"].sum().idxmax()`
# Handle the empty DataFrame case: check `if len(filtered) > 0` before computing averages or max values
# Hint: Use col.metric("Label", "Value")
# Hint: Handle the case where filtered is empty (total_orders == 0)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${filtered["revenue"].sum():,.2f}")
col2.metric("Total Orders", len(filtered["order_id"]))
col3.metric("Average Order Value", 'N/A' if len(filtered) == 0 else f"${filtered['revenue'].mean():,.2f}")
col4.metric("Top Category", 'N/A' if len(filtered) == 0 else filtered.groupby('category')['revenue'].sum().idxmax())

# =====================================================================
# TODO 4: Visualization Tabs
# =====================================================================
# Create 4 tabs: "Overview", "By Category", "By Region", "Data"

# Overview tab:
#   - Monthly revenue line chart
#   - Group by month: filtered.groupby(filtered["order_date"].dt.to_period("M"))
#   - Use px.line with markers=True
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "By Category", "By Region", "Data"])
with tab1:
    if len(filtered) == 0:
             st.info('No Data to display') 
    else:
        monthly = (
            filtered.groupby(filtered["order_date"].dt.to_period("M"))["revenue"]
            .sum()
            .reset_index()
        )   
        monthly["order_date"] = monthly["order_date"].astype(str)

        fig = px.line(monthly, x="order_date", y="revenue", markers=True)
        st.plotly_chart(fig, use_container_width=True)

# By Category tab:
#   - Horizontal bar chart of revenue by category
#   - Use px.bar with orientation="h"
#   - Sort by revenue ascending (so highest is at top)

with tab2:
    if len(filtered) == 0:
             st.info('No Data to display') 
    else:
        category_df = (
            filtered.groupby("category")["revenue"].sum().reset_index().sort_values(by="revenue", ascending=True))
    
        fig = px.bar(category_df, x="revenue", y="category", orientation="h", color="category")
        st.plotly_chart(fig, use_container_width=True)

    

# By Region tab:
#   - Pie chart of revenue by region
#   - Use px.pie

with tab3:
    if len(filtered) == 0:
             st.info('No Data to display') 
    else:
        region_df = (
            filtered.groupby("region")["revenue"].sum().reset_index()
        )

        fig = px.pie(region_df, values="revenue", names="region")
        st.plotly_chart(fig, use_container_width=True)

# Data tab:
#   - Display the filtered DataFrame with st.dataframe
#   - Add a download button using st.download_button to export as CSV

with tab4:
    if len(filtered) == 0:
             st.info('No Data to display') 
    else:
        data_df = (
            st.dataframe(filtered, use_container_width=True)
        )
        csv_data = filtered.to_csv(index=False)
        st.download_button(
        label="Download as CSV",
        data=csv_data,
        file_name="filtered_sales_data.csv",
        mime="text/csv",
        )

# For all charts, use st.plotly_chart(fig, use_container_width=True)
# Add st.info("No data to display.") when filtered is empty
