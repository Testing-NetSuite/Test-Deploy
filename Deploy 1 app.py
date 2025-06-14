import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

st.set_page_config(layout="wide")
st.title("📊 Dashboard Sales PT AMI")

# Upload
uploaded_file = st.file_uploader("📂 Upload file Excel (.xlsx)", type=['xlsx'])
if uploaded_file:
    df_outlet = pd.read_excel(uploaded_file, sheet_name='Sales by Outlet')
    df_menu = pd.read_excel(uploaded_file, sheet_name='Sales per Menu per Outlet')

    df_outlet['Month'] = pd.to_datetime(df_outlet['Month'])
    df_menu['Month'] = pd.to_datetime(df_menu['Month'])

    area = st.sidebar.selectbox("📌 Pilih Area", sorted(df_outlet['Area'].unique()))
    kota = st.sidebar.selectbox(
        "🏙️ Pilih Kota",
        sorted(df_outlet[df_outlet['Area'] == area]['Kota'].unique())
    )

    df_outlet_f = df_outlet[(df_outlet['Area'] == area) & (df_outlet['Kota'] == kota)]
    df_menu_f = df_menu[(df_menu['Area'] == area) & (df_menu['Kota'] == kota)]

    st.sidebar.write(f"✅ Jumlah Outlet: {df_outlet_f['Outlet'].nunique()}")

    st.header(f"📈 Trend Penjualan: {area} - {kota}")

    # Trend Total Sales
    m = df_outlet_f.groupby('Month').agg({'Total Sales': 'sum'}).reset_index()
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=m, x='Month', y='Total Sales', marker='o', ax=ax1)
    ax1.set_title('Total Sales Trend')
    ax1.tick_params(axis='x', rotation=45)
    st.pyplot(fig1)

    # Channel Sales
    c = df_outlet_f.groupby('Month').agg({
        'Sales Dine In + Take Away': 'sum',
        'Sales Ojol': 'sum'
    }).reset_index()
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=c, x='Month', y='Sales Dine In + Take Away', marker='o', label='Dine In + Take Away', ax=ax2)
    sns.lineplot(data=c, x='Month', y='Sales Ojol', marker='o', label='Ojol', ax=ax2)
    ax2.set_title('Channel Sales Trend')
    ax2.tick_params(axis='x', rotation=45)
    ax2.legend()
    st.pyplot(fig2)

    # Pie Channel
    total = df_outlet_f[['Sales Dine In + Take Away', 'Sales Ojol']].sum()
    fig3, ax3 = plt.subplots()
    ax3.pie(total, labels=total.index, autopct='%1.1f%%', startangle=140, colors=['#4CAF50', '#2196F3'])
    ax3.set_title('Channel Composition')
    st.pyplot(fig3)

    # Top 10 Menu
    top = df_menu_f.groupby('Menu').agg({'Total Qty': 'sum'}).reset_index().sort_values(by='Total Qty', ascending=False)
    fig4, ax4 = plt.subplots(figsize=(8, 6))
    sns.barplot(data=top.head(10), x='Total Qty', y='Menu', palette='viridis', ax=ax4)
    ax4.set_title('Top 10 Menu')
    st.pyplot(fig4)

    # Download filtered data
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_outlet_f.to_excel(writer, sheet_name='Outlet', index=False)
        df_menu_f.to_excel(writer, sheet_name='Menu', index=False)
    st.download_button(
        label="⬇️ Download Filtered Excel",
        data=buffer,
        file_name=f"{area}_{kota}_Filtered.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
