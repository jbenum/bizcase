# Immix Integration Business Case Web App (Streamlit UI)

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Immix Integration Business Case", layout="wide")
st.title("Immix Integration Business Case Dashboard")

# Sidebar Inputs
st.sidebar.header("Input Variables")
months = 48

unit_sales_per_month = st.sidebar.number_input("Unit Sales per Month", value=10)
price_per_unit = st.sidebar.number_input("Price per Unit ($)", value=1000)

new_logo_arr_per_month = st.sidebar.number_input("New Logo ARR per Month ($)", value=20000)
upsell_arr_per_month = st.sidebar.number_input("Upsell ARR per Month ($)", value=5000)

retention_improvement_rate = st.sidebar.slider("Retention Improvement Rate (Monthly %)", 0.0, 0.05, 0.01)

cogs_per_month = st.sidebar.number_input("COGS per Month ($)", value=8000)
opex_per_month = st.sidebar.number_input("OpEX per Month ($)", value=12000)

tax_rate = st.sidebar.slider("Tax Rate (%)", 0.0, 1.0, 0.25)
wacc = st.sidebar.slider("Annual WACC (%)", 0.0, 0.25, 0.10) / 12

# DataFrame to store projections
data = pd.DataFrame(index=range(1, months + 1))

# Revenue Calculations
data['Unit Sales'] = unit_sales_per_month
data['Unit Price'] = price_per_unit
data['Unit Revenue'] = data['Unit Sales'] * data['Unit Price']

data['New Logo ARR'] = new_logo_arr_per_month
data['Upsell ARR'] = upsell_arr_per_month
data['Cumulative ARR'] = data['New Logo ARR'].cumsum() + data['Upsell ARR'].cumsum()
data['Total Revenue'] = data['Unit Revenue'] + data['Cumulative ARR']

data['GRR Factor'] = (1 + retention_improvement_rate) ** data.index
data['GRR Adjusted Revenue'] = data['Total Revenue'] * data['GRR Factor']

# Cost and Profit Calculations
data['COGS'] = cogs_per_month
data['OpEX'] = opex_per_month
data['EBIT'] = data['GRR Adjusted Revenue'] - data['COGS'] - data['OpEX']
data['Tax'] = data['EBIT'] * tax_rate
data['Net Income'] = data['EBIT'] - data['Tax']

# NPV Calculation
data['Discount Factor'] = 1 / ((1 + wacc) ** data.index)
data['NPV of Net Income'] = data['Net Income'] * data['Discount Factor']

# Summary Metrics
total_revenue = data['GRR Adjusted Revenue'].sum()
total_costs = data['COGS'].sum() + data['OpEX'].sum()
total_npv = data['NPV of Net Income'].sum()

st.subheader("Key Metrics")
st.metric("Total GRR Adjusted Revenue", f"${total_revenue:,.0f}")
st.metric("Total Costs", f"${total_costs:,.0f}")
st.metric("Total Net Present Value (NPV)", f"${total_npv:,.0f}")

# Visual Dashboard
sns.set(style="whitegrid")
fig, axs = plt.subplots(2, 2, figsize=(16, 10))

axs[0, 0].plot(data.index, data['GRR Adjusted Revenue'], label='GRR Adjusted Revenue', color='blue')
axs[0, 0].set_title('Monthly GRR Adjusted Revenue')
axs[0, 0].set_xlabel('Month')
axs[0, 0].set_ylabel('Revenue ($)')
axs[0, 0].legend()

axs[0, 1].plot(data.index, data['Net Income'], label='Net Income', color='green')
axs[0, 1].set_title('Monthly Net Income')
axs[0, 1].set_xlabel('Month')
axs[0, 1].set_ylabel('Net Income ($)')
axs[0, 1].legend()

axs[1, 0].plot(data.index, data['NPV of Net Income'].cumsum(), label='Cumulative NPV', color='purple')
axs[1, 0].set_title('Cumulative NPV of Net Income')
axs[1, 0].set_xlabel('Month')
axs[1, 0].set_ylabel('NPV ($)')
axs[1, 0].legend()

axs[1, 1].plot(data.index, data['EBIT'], label='EBIT', color='orange')
axs[1, 1].plot(data.index, data['COGS'] + data['OpEX'], label='Total Costs', color='red')
axs[1, 1].set_title('EBIT vs Total Costs')
axs[1, 1].set_xlabel('Month')
axs[1, 1].set_ylabel('Amount ($)')
axs[1, 1].legend()

plt.tight_layout()
st.pyplot(fig)

# Display table if user wants to explore data
if st.checkbox("Show Detailed Data Table"):
    st.dataframe(data.round(2))
