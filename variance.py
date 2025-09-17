import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Stock Variance Dashboard", layout="wide")

# --- Load Excel File ---
file_path = "stock_data.xlsx"  # Replace with your Excel file path
df = pd.read_excel(file_path)
df.columns = df.columns.str.strip()

# --- Ensure Diff Stock column exists ---
if 'Diff Stock' not in df.columns:
    df['Diff Stock'] = df['Phys Stock'] - df['Book Stock']

# --- Sidebar Filters ---
st.sidebar.header("Filters")
categories = df['Category'].unique().tolist()
selected_category = st.sidebar.selectbox("Select Category", ["All"] + categories)

# --- Filter by Category ---
filtered_df = df.copy()
if selected_category != "All":
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]

# --- Top 30 items by absolute variance ---
filtered_df['Abs Diff'] = filtered_df['Diff Stock'].abs()
top_30 = filtered_df.sort_values('Abs Diff', ascending=False).head(30)

# --- Dashboard Title ---
st.title("📊 Stock Variance Dashboard")

# --- Top 30 Horizontal Bar Chart ---
st.subheader("Top 30 Items by Stock Difference")
fig = px.bar(
    top_30,
    y='Item Name',
    x='Diff Stock',
    orientation='h',
    color='Diff Stock',
    color_continuous_scale='RdYlGn_r',
    text='Diff Stock',
    hover_data={
        'Category': True,
        'Item No': True,
        'Barcode': True,
        'Book Stock': True,
        'Phys Stock': True,
        'Diff Stock': True,
        'Item Name': False
    }
)
fig.update_layout(
    yaxis=dict(autorange="reversed"),
    xaxis_title="Stock Difference",
    yaxis_title="",
    height=800,
)
st.plotly_chart(fig, use_container_width=True)

# --- Raw Table for Top 30 ---
st.subheader("📄 Top 30 Items Details")
key_columns = ['Category', 'Item Name', 'Item No', 'Barcode', 'Book Stock', 'Phys Stock', 'Diff Stock']
available_columns = [col for col in key_columns if col in top_30.columns]
st.dataframe(top_30[available_columns])

# --- All remaining data by category ---
st.subheader("📄 All Items by Category ")
remaining_df = filtered_df.drop(top_30.index)
st.dataframe(remaining_df[available_columns].sort_values(['Category', 'Diff Stock'], ascending=[True, False]))
