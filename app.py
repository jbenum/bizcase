# Immix Integration Business Case Web App (Streamlit UI with Monte Carlo)

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Immix Integration Business Case", layout="wide")
st.title("Immix Integration Business Case Dashboard")

# Sidebar Inputs
st.sidebar.header("Revenue Forecast")
months = 48

# Simulation settings
st.sidebar.header("Monte Carlo Settings")
run_simulation = st.sidebar.checkbox("Run Monte Carlo Simulation", value=False)
simulations = st.sidebar.number_input("# of Simulations", min_value=100, max_value=10000, value=1000, step=100)

# Forecast inputs
total_bookings_forecast = st.sidebar.number_input("Total Bookings Forecast ($)", value=2000000)
soc_needs_pct = st.sidebar.slider("% of Forecast with SOC Needs", 0.0, 1.0, 0.5)
conversion_rate = st.sidebar.slider("Conversion Rate from Bookings", 0.0, 1.0, 0.3)

new_logo_revenue = (total_bookings_forecast * soc_needs_pct * conversion_rate) / months

st.sidebar.header("Revenue Retention")
avg_mrr_per_client = st.sidebar.number_input("Average MRR per Client ($)", value=2000)
total_accounts = st.sidebar.number_input("Total # of Accounts", value=50)
churn_retention_rate = st.sidebar.slider("Churn Retention Rate (%)", 0.0, 1.0, 0.9)
churn_impact_month = st.sidebar.slider("Churn Impact After # of Months", 1, 48, 12)

initial_retained_revenue = avg_mrr_per_client * total_accounts
monthly_retention = np.ones(months) * initial_retained_revenue
monthly_retention[churn_impact_month:] *= churn_retention_rate

upsell_arr_per_month = st.sidebar.number_input("Upsell ARR per Month ($)", value=5000)

st.sidebar.header("COGS Breakdown (% of MRR)")
hosting_pct = st.sidebar.slider("Hosting Cost %", 0.0, 1.0, 0.05)
ps_pct = st.sidebar.slider("Professional Services %", 0.0, 1.0, 0.10)
support_pct = st.sidebar.slider("Customer Support %", 0.0, 1.0, 0.08)
cs_pct = st.sidebar.slider("Customer Success %", 0.0, 1.0, 0.07)

st.sidebar.header("OpEx Inputs")
marketing_cac_pct = st.sidebar.slider("Marketing CAC % of MRR", 0.0, 1.0, 0.15)
sales_commission_pct = st.sidebar.slider("Sales Commission %", 0.0, 1.0, 0.12)
support_maint_pct = st.sidebar.slider("Support & Maint. % of MRR", 0.0, 1.0, 0.1)
monthly_squad_cost = st.sidebar.number_input("Monthly Squad Cost ($)", value=15000)
development_months = st.sidebar.slider("# of Dev Months", 1, 48, 12)

# Tax and WACC
tax_rate = st.sidebar.slider("Tax Rate (%)", 0.0, 1.0, 0.25)
wacc = st.sidebar.slider("Annual WACC (%)", 0.0, 0.25, 0.10) / 12

# Base model calculation
def run_model():
    data = pd.DataFrame(index=range(1, months + 1))
    data['New Logo Revenue'] = new_logo_revenue
    data['Upsell ARR'] = upsell_arr_per_month
    data['Retained MRR'] = monthly_retention
    data['Cumulative ARR'] = data['Retained MRR'].cumsum() + data['Upsell ARR'].cumsum()
    data['Total Revenue'] = data['New Logo Revenue'] + data['Cumulative ARR']
    data['COGS'] = data['Total Revenue'] * (hosting_pct + ps_pct + support_pct + cs_pct)
    data['OpEX'] = (
        data['Total Revenue'] * (marketing_cac_pct + sales_commission_pct + support_maint_pct)
        + monthly_squad_cost * (data.index <= development_months)
    )
    data['EBIT'] = data['Total Revenue'] - data['COGS'] - data['OpEX']
    data['Tax'] = data['EBIT'] * tax_rate
    data['Net Income'] = data['EBIT'] - data['Tax']
    data['Discount Factor'] = 1 / ((1 + wacc) ** data.index)
    data['NPV of Net Income'] = data['Net Income'] * data['Discount Factor']
    return data

# Run Monte Carlo Simulation
if run_simulation:
    rev_results = []
    cost_results = []
    npv_results = []
    for _ in range(simulations):
        rev_variation = np.random.normal(loc=new_logo_revenue, scale=new_logo_revenue * 0.1, size=months)
        data_sim = run_model()
        data_sim['Total Revenue'] = rev_variation + data_sim['Cumulative ARR']
        data_sim['COGS'] = data_sim['Total Revenue'] * (hosting_pct + ps_pct + support_pct + cs_pct)
        data_sim['OpEX'] = (
            data_sim['Total Revenue'] * (marketing_cac_pct + sales_commission_pct + support_maint_pct)
            + monthly_squad_cost * (data_sim.index <= development_months)
        )
        data_sim['EBIT'] = data_sim['Total Revenue'] - data_sim['COGS'] - data_sim['OpEX']
        data_sim['Tax'] = data_sim['EBIT'] * tax_rate
        data_sim['Net Income'] = data_sim['EBIT'] - data_sim['Tax']
        data_sim['Discount Factor'] = 1 / ((1 + wacc) ** data_sim.index)
        data_sim['NPV of Net Income'] = data_sim['Net Income'] * data_sim['Discount Factor']

        rev_results.append(data_sim['Total Revenue'].sum())
        cost_results.append((data_sim['COGS'] + data_sim['OpEX']).sum())
        npv_results.append(data_sim['NPV of Net Income'].sum())

    st.subheader("Monte Carlo Simulation Results")
    st.write(f"**Expected Total Revenue:** ${np.mean(rev_results):,.0f}")
    st.write(f"**Expected Total Costs:** ${np.mean(cost_results):,.0f}")
    st.write(f"**Expected NPV:** ${np.mean(npv_results):,.0f}")
    st.write(f"**NPV Range (95% CI):** ${np.percentile(npv_results, 2.5):,.0f} - ${np.percentile(npv_results, 97.5):,.0f}")

# Main model run
model_data = run_model()
total_revenue = model_data['Total Revenue'].sum()
total_costs = model_data['COGS'].sum() + model_data['OpEX'].sum()
total_npv = model_data['NPV of Net Income'].sum()

st.subheader("Key Metrics")
st.metric("Total Revenue", f"${total_revenue:,.0f}")
st.metric("Total Costs", f"${total_costs:,.0f}")
st.metric("Total Net Present Value (NPV)", f"${total_npv:,.0f}")

# Visual Dashboard
sns.set(style="whitegrid")
fig, axs = plt.subplots(2, 2, figsize=(16, 10))

axs[0, 0].plot(model_data.index, model_data['Total Revenue'], label='Total Revenue', color='blue')
axs[0, 0].set_title('Monthly Total Revenue')
axs[0, 0].set_xlabel('Month')
axs[0, 0].set_ylabel('Revenue ($)')
axs[0, 0].legend()

axs[0, 1].plot(model_data.index, model_data['Net Income'], label='Net Income', color='green')
axs[0, 1].set_title('Monthly Net Income')
axs[0, 1].set_xlabel('Month')
axs[0, 1].set_ylabel('Net Income ($)')
axs[0, 1].legend()

axs[1, 0].plot(model_data.index, model_data['NPV of Net Income'].cumsum(), label='Cumulative NPV', color='purple')
axs[1, 0].set_title('Cumulative NPV of Net Income')
axs[1, 0].set_xlabel('Month')
axs[1, 0].set_ylabel('NPV ($)')
axs[1, 0].legend()

axs[1, 1].plot(model_data.index, model_data['EBIT'], label='EBIT', color='orange')
axs[1, 1].plot(model_data.index, model_data['COGS'] + model_data['OpEX'], label='Total Costs', color='red')
axs[1, 1].set_title('EBIT vs Total Costs')
axs[1, 1].set_xlabel('Month')
axs[1, 1].set_ylabel('Amount ($)')
axs[1, 1].legend()

plt.tight_layout()
st.pyplot(fig)

if st.checkbox("Show Detailed Data Table"):
    st.dataframe(model_data.round(2))
