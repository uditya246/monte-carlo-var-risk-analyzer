import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import fetch_data
from risk_model import (
    calculate_log_returns,
    calculate_statistics,
    calculate_historical_var,
    run_monte_carlo_simulation,
    calculate_monte_carlo_var
)

# Configuration
st.set_page_config(page_title="Risk Analyzer", layout="wide")

# CSS to make the dashboard look cleaner
st.markdown("""
<style>
    .kpi-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    .kpi-title {
        font-size: 14px;
        color: #6c757d;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: bold;
        color: #212529;
    }
</style>
""", unsafe_allow_html=True)

# Top section: Title and Description
st.title("📈 Monte Carlo Value-at-Risk (VaR) & Portfolio Risk Analyzer")
st.markdown("""
This dashboard estimates the financial downside risk of a stock using **Monte Carlo simulation** and **Value-at-Risk (VaR)**.
""")

# Sidebar inputs
st.sidebar.header("Configuration")
ticker = st.sidebar.text_input("Stock Ticker (e.g., AAPL, RELIANCE.NS)", value="AAPL").upper()
period = st.sidebar.selectbox("Historical Period", ["1Y", "3Y", "5Y"])
investment_amount = st.sidebar.number_input("Investment Amount (₹ or $)", min_value=1000.0, value=100000.0, step=1000.0)
num_simulations = st.sidebar.number_input("Number of Simulations", min_value=1000, max_value=100000, value=10000, step=1000)
confidence_level_str = st.sidebar.selectbox("Confidence Level", ["95%", "99%"])
confidence_level = 0.95 if confidence_level_str == "95%" else 0.99

# Fetch Data
if ticker:
    with st.spinner('Fetching historical data...'):
        prices, error = fetch_data(ticker, period)
    
    if error:
        st.error(error)
    else:
        # Perform calculations
        returns = calculate_log_returns(prices)
        stats = calculate_statistics(returns)
        
        # Monte Carlo Simulation
        simulated_returns = run_monte_carlo_simulation(
            stats['mean'], 
            stats['volatility'], 
            num_simulations=int(num_simulations),
            seed=42 # Fixed seed for reproducibility
        )
        simulated_pnl = simulated_returns * investment_amount
        
        # VaR Calculations
        mc_var_95 = calculate_monte_carlo_var(simulated_returns, investment_amount, 0.95)
        mc_var_99 = calculate_monte_carlo_var(simulated_returns, investment_amount, 0.99)
        
        hist_var_95 = calculate_historical_var(returns, investment_amount, 0.95)
        hist_var_99 = calculate_historical_var(returns, investment_amount, 0.99)
        
        # KPI Cards
        st.subheader("Key Performance Indicators")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Current Price", f"{prices.iloc[-1]:.2f}")
        with col2:
            st.metric("Daily Volatility", f"{stats['volatility']*100:.2f}%")
        with col3:
            st.metric("Annualized Vol.", f"{stats['annualized_volatility']*100:.2f}%")
        with col4:
            st.metric(f"MC VaR ({confidence_level_str})", f"{abs(mc_var_95 if confidence_level == 0.95 else mc_var_99):,.2f}")
        with col5:
            st.metric(f"Hist VaR ({confidence_level_str})", f"{abs(hist_var_95 if confidence_level == 0.95 else hist_var_99):,.2f}")

        st.markdown("---")
        
        # Layout for Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("1. Historical Price Chart")
            fig_price = px.line(x=prices.index, y=prices.values, title=f"{ticker} Historical Close Price")
            fig_price.update_xaxes(title="Date")
            fig_price.update_yaxes(title="Price")
            st.plotly_chart(fig_price, use_container_width=True)
            
        with chart_col2:
            st.subheader("2. Return Distribution")
            fig_ret = px.histogram(returns, nbins=50, title=f"Historical Daily Log Returns")
            # Mark VaR
            selected_hist_var_return = np.percentile(returns, (1 - confidence_level) * 100)
            fig_ret.add_vline(x=selected_hist_var_return, line_dash="dash", line_color="red", 
                              annotation_text=f"VaR {confidence_level_str}")
            fig_ret.update_layout(showlegend=False)
            st.plotly_chart(fig_ret, use_container_width=True)

        st.markdown("---")
        
        st.subheader("3. Monte Carlo Simulation (P&L Distribution)")
        fig_mc = px.histogram(simulated_pnl, nbins=100, title="Simulated 1-Day P&L Distribution")
        fig_mc.add_vline(x=mc_var_95, line_dash="dash", line_color="orange", annotation_text="95% VaR")
        fig_mc.add_vline(x=mc_var_99, line_dash="dash", line_color="red", annotation_text="99% VaR")
        st.plotly_chart(fig_mc, use_container_width=True)

        st.markdown("---")
        
        st.subheader("4. Risk Summary")
        st.info(f"""
        **Investment:** {investment_amount:,.2f}  
        
        **95% Monte Carlo VaR:** {abs(mc_var_95):,.2f}  
        **99% Monte Carlo VaR:** {abs(mc_var_99):,.2f}  
        
        **Interpretation:** Based on the simulation, there is an estimated {(1-0.95)*100:.0f}% probability that the one-day loss could exceed {abs(mc_var_95):,.2f}, and an estimated {(1-0.99)*100:.0f}% probability that the one-day loss could exceed {abs(mc_var_99):,.2f}.
        
        *(Note: VaR is an estimate under model assumptions and not a guarantee of maximum loss.)*
        """)
        
        st.markdown("---")
        
        st.subheader("5. Historical vs Monte Carlo VaR Comparison")
        comparison_data = {
            "Method": ["Historical VaR", "Monte Carlo VaR", "Historical VaR", "Monte Carlo VaR"],
            "Confidence": ["95%", "95%", "99%", "99%"],
            "Estimated VaR Loss": [abs(hist_var_95), abs(mc_var_95), abs(hist_var_99), abs(mc_var_99)]
        }
        df_comp = pd.DataFrame(comparison_data)
        st.dataframe(df_comp.style.format({"Estimated VaR Loss": "{:,.2f}"}), use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("🎓 How it works")
        st.markdown("""
        1. **Historical prices → returns:** We download the daily closing prices and calculate the daily logarithmic returns: `ln(P_t / P_(t-1))`
        2. **Returns → mean and volatility:** We calculate the average daily return and the standard deviation (volatility) of those returns.
        3. **Mean + volatility → simulated returns:** We use a random number generator to create thousands of possible future daily returns assuming they follow a normal distribution.
        4. **Simulated returns → simulated P&L:** We multiply the simulated returns by your investment amount to see potential monetary gains or losses.
        5. **P&L distribution → VaR:** We find the lowest 5% (for 95% confidence) or 1% (for 99% confidence) of simulated outcomes.
        
        **What is VaR?**  
        Value-at-Risk (VaR) estimates the potential loss that will not be exceeded with a given confidence level under the model assumptions. 
        
        **What is Monte Carlo simulation?**  
        It is a mathematical technique that generates many possible future outcomes using randomly sampled numbers based on estimated statistical parameters.
        """)
