import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Stock Variance Dashboard", layout="wide")

# --- Load Data Function ---
@st.cache_data
def load_data():
    df = pd.read_excel("stock_data.xlsx")  # Replace with your Excel file path
    df.columns = df.columns.str.strip()

    if 'Diff Stock' not in df.columns:
        df['Diff Stock'] = df['Phys Stock'] - df['Book Stock']

    cost_col = "Cost Price"  # Adjust if your Excel has a different name
    df['Book Value'] = df['Book Stock'] * df[cost_col]
    df['Phys Value'] = df['Phys Stock'] * df[cost_col]
    df['Diff Value'] = df['Diff Stock'] * df[cost_col]

    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filters")
categories = df['Category'].unique().tolist()
selected_category = st.sidebar.selectbox("Select Category", ["All"] + categories)

# --- Filtered Data ---
filtered_df = df.copy()
if selected_category != "All":
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]

# --- Summary Metrics ---
total_book_stock = filtered_df['Book Stock'].sum()
total_phys_stock = filtered_df['Phys Stock'].sum()
total_diff_stock = filtered_df['Diff Stock'].sum()

total_book_value = filtered_df['Book Value'].sum()
total_phys_value = filtered_df['Phys Value'].sum()
total_diff_value = filtered_df['Diff Value'].sum()

stock_variance_pct = (
    (total_diff_stock / total_book_stock) * 100 if total_book_stock != 0 else 0
)

# --- Dashboard Title ---
st.title("📊 Stock Variance Dashboard")

# --- Summary Section (No Arrows) ---
st.markdown("### 📊 Stock Summary")
col1, col2, col3, col4 = st.columns(4, gap="large")

with col1:
    st.markdown(
        f"<h5>System Stock</h5>"
        f"<p style='font-size:28px; font-weight:bold;'>{total_book_stock:,.0f}</p>"
        f"<p style='font-size:14px; color:gray;'>AED {total_book_value:,.0f}</p>",
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"<h5>Physical Stock</h5>"
        f"<p style='font-size:28px; font-weight:bold;'>{total_phys_stock:,.0f}</p>"
        f"<p style='font-size:14px; color:gray;'>AED {total_phys_value:,.0f}</p>",
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"<h5>Stock Difference</h5>"
        f"<p style='font-size:28px; font-weight:bold;'>{total_diff_stock:,.0f}</p>"
        f"<p style='font-size:14px; color:gray;'>AED {total_diff_value:,.0f}</p>",
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"<h5>Stock Variance %</h5>"
        f"<p style='font-size:28px; font-weight:bold;'>{stock_variance_pct:.2f} %</p>",
        unsafe_allow_html=True
    )

# --- Top 30 items by absolute variance ---
filtered_df['Abs Diff'] = filtered_df['Diff Stock'].abs()
top_30 = filtered_df.sort_values('Abs Diff', ascending=False).head(30)

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
        'Book Value': True,
        'Phys Value': True,
        'Diff Value': True,
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
key_columns = [
    'Category', 'Item Name', 'Item No', 'Barcode',
    'Book Stock', 'Phys Stock', 'Diff Stock',
    'Book Value', 'Phys Value', 'Diff Value'
]
available_columns = [col for col in key_columns if col in top_30.columns]
st.dataframe(top_30[available_columns])

# --- All remaining data by category ---
st.subheader("📄 All Items by Category")
remaining_df = filtered_df.drop(top_30.index)
st.dataframe(
    remaining_df[available_columns].sort_values(['Category', 'Diff Stock'], ascending=[True, False])
)
