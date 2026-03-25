import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Configuration
st.set_page_config(
    page_title="Institutional Trade Execution Model",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI enhancements
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: #FAFAFA;
}
</style>
""", unsafe_allow_html=True)

st.title("📈 Institutional Trade Execution & Market Impact")
st.markdown("Analyze market impact, slippage, and execution risk using the square-root, temporary, and permanent impact models.")

# --- Sidebar Controls ---
st.sidebar.header("Execution Parameters")

order_size = st.sidebar.number_input("Order Size (Shares)", min_value=1000, max_value=10000000, value=500000, step=1000)
adv = st.sidebar.number_input("Average Daily Volume (ADV)", min_value=10000, max_value=50000000, value=5000000, step=10000)
participation_rate = st.sidebar.slider("Participation Rate (%)", min_value=1.0, max_value=50.0, value=10.0, step=1.0) / 100.0
volatility = st.sidebar.slider("Annualized Volatility (%)", min_value=5.0, max_value=100.0, value=20.0, step=0.5) / 100.0
risk_aversion = st.sidebar.slider("Risk Aversion (λ)", min_value=1e-6, max_value=1e-3, value=1e-4, step=1e-6, format="%.6f")

current_price = 100.0  # Base price for simulation

# Derived Parameters
trading_horizon_days = (order_size / adv) / participation_rate
daily_volatility = volatility / np.sqrt(252)

# --- Market Impact Models ---
# Using standard square-root model formulation:
# Impact = gamma * sigma * sqrt(Q / V)
gamma_temp = 0.5  # Temporary impact coefficient
gamma_perm = 0.1  # Permanent impact coefficient

# 1. Temporary Impact (Square-Root Model)
# Representing the immediate cost of liquidity
temp_impact_pct = gamma_temp * daily_volatility * np.sqrt(order_size / adv) * np.sqrt(participation_rate)
temp_impact_cost = temp_impact_pct * current_price * order_size

# 2. Permanent Impact
# Representing the information leakage
perm_impact_pct = gamma_perm * daily_volatility * (order_size / adv)
perm_impact_cost = perm_impact_pct * current_price * order_size / 2  # Average over the execution

# 3. Execution Risk (Variance)
# Variance of price over the horizon
execution_variance = (daily_volatility * current_price)**2 * trading_horizon_days
execution_risk_cost = risk_aversion * execution_variance * order_size

total_expected_cost = temp_impact_cost + perm_impact_cost + execution_risk_cost
slippage_bps = (total_expected_cost / (current_price * order_size)) * 10000

# --- Metrics Display ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Trading Horizon", f"{trading_horizon_days:.2f} Days")
col2.metric("Total Slippage (bps)", f"{slippage_bps:.1f} bps")
col3.metric("Total Cost ($)", f"${total_expected_cost:,.2f}")
col4.metric("Temp Impact (%)", f"{temp_impact_pct*100:.2f} %")

st.markdown("---")

# --- Visualizations ---

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Cost Breakdown")
    breakdown_data = pd.DataFrame({
        "Cost Component": ["Temporary Impact", "Permanent Impact", "Risk Penalty"],
        "Amount ($)": [temp_impact_cost, perm_impact_cost, execution_risk_cost]
    })
    fig_bar = px.bar(breakdown_data, x="Cost Component", y="Amount ($)", color="Cost Component",
                     color_discrete_sequence=["#1f77b4", "#ff7f0e", "#d62728"],
                     title="Execution Cost Breakdown")
    fig_bar.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_bar, use_container_width=True)

with row1_col2:
    st.subheader("Animated Price Path Simulation")
    # Simulate a price path (e.g., VWAP execution)
    np.random.seed(42)
    n_steps = 50
    dt = trading_horizon_days / n_steps
    
    # Brownian motion
    dW = np.random.normal(0, np.sqrt(dt), n_steps)
    price_path = np.zeros(n_steps + 1)
    price_path[0] = current_price
    
    # Impact terms per step
    step_perm_impact = (perm_impact_pct * current_price) / n_steps
    step_temp_impact = (temp_impact_pct * current_price)
    
    impacted_path = np.zeros(n_steps + 1)
    impacted_path[0] = current_price - step_temp_impact  # Assuming selling

    for i in range(1, n_steps + 1):
        drift = 0
        shock = current_price * daily_volatility * dW[i-1]
        price_path[i] = price_path[i-1] + shock
        impacted_path[i] = price_path[i-1] + shock - step_perm_impact * i - step_temp_impact

    time_steps = np.linspace(0, trading_horizon_days, n_steps + 1)
    
    path_df_list = []
    for step in range(1, n_steps + 2):
        temp_df = pd.DataFrame({
            "Time (Days)": time_steps[:step].tolist() * 2,
            "Price": price_path[:step].tolist() + impacted_path[:step].tolist(),
            "Type": ["Unimpacted"]*step + ["Impacted"]*step,
            "Frame": [step]* (2*step)
        })
        path_df_list.append(temp_df)
        
    anim_df = pd.concat(path_df_list, ignore_index=True)
    
    fig_anim = px.line(anim_df, x="Time (Days)", y="Price", color="Type",
                       animation_frame="Frame", range_x=[0, trading_horizon_days],
                       range_y=[min(impacted_path)*0.99, max(price_path)*1.01],
                       title="Price Deviation (Executing Sell Order)",
                       color_discrete_map={"Unimpacted": "#FAFAFA", "Impacted": "#00E676"})
    fig_anim.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_anim, use_container_width=True)


row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("3D Surface: Slippage vs Size & Participation")
    
    # Create grid
    q_range = np.linspace(adv * 0.01, adv * 0.5, 30)
    rho_range = np.linspace(0.01, 0.5, 30)
    Q_grid, Rho_grid = np.meshgrid(q_range, rho_range)
    
    # Calculate total slippage (bps) for grid
    Z_temp = gamma_temp * daily_volatility * np.sqrt(Q_grid / adv) * np.sqrt(Rho_grid)
    Z_cost_temp = Z_temp * current_price * Q_grid
    
    Z_perm = gamma_perm * daily_volatility * (Q_grid / adv)
    Z_cost_perm = Z_perm * current_price * Q_grid / 2
    
    Z_horizon = (Q_grid / adv) / Rho_grid
    Z_variance = (daily_volatility * current_price)**2 * Z_horizon
    Z_cost_risk = risk_aversion * Z_variance * Q_grid
    
    Z_total_cost = Z_cost_temp + Z_cost_perm + Z_cost_risk
    Z_slippage = (Z_total_cost / (current_price * Q_grid)) * 10000
    
    fig_3d = go.Figure(data=[go.Surface(z=Z_slippage, x=q_range/1000, y=rho_range*100, colorscale='Viridis')])
    fig_3d.update_layout(
        title='Total Slippage (bps)',
        scene=dict(
            xaxis_title='Order Size (k Shares)',
            yaxis_title='Participation Rate (%)',
            zaxis_title='Slippage (bps)'
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_3d, use_container_width=True)

with row2_col2:
    st.subheader("Impact Heatmap (Cost)")
    
    # Heatmap of Risk-Adjusted Cost
    # Red implies hot (high cost), green implies low cost
    fig_heat = px.imshow(Z_slippage,
                         labels=dict(x="Order Size", y="Participation Rate", color="Slippage (bps)"),
                         x=np.round(q_range/1000, 0),
                         y=np.round(rho_range*100, 1),
                         color_continuous_scale=["#00E676", "#FFC107", "#D32F2F"])
    
    # The requirement says "red as hot then yellow and all the way to green".
    # High slippage = Red, Mid = Yellow, Low = Green.
    # Therefore we need the scale to go from Green (lowest values) to Red (highest values), which px.imshow maps.
    fig_heat.update_layout(
        title="Slippage Heatmap",
        xaxis_title="Order Size (k Shares)",
        yaxis_title="Participation Rate (%)",
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_heat, use_container_width=True)
