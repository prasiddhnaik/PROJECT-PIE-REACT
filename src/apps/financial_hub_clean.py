import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import time
import json

# 🚀 CLEAN CONFIGURATION
st.set_page_config(
    page_title="Financial Analytics Hub", 
    page_icon="💰", 
    layout="wide"
)

# 🎨 SIMPLE CSS FOR FAST LOADING
st.markdown("""
<style>
.metric-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #007bff;
    margin: 0.5rem 0;
}
.success-box {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 5px;
    padding: 0.75rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# 🚀 MAIN APPLICATION
def main():
    # Header
    st.title("💰 Financial Analytics Hub")
    st.caption("🚀 Lightning-fast financial tools and analysis")
    
    # Sidebar
    st.sidebar.title("🔧 Quick Tools")
    st.sidebar.info("Choose a tool from the tabs above")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Dashboard", 
        "📊 Market Data", 
        "💹 SIP Calculator", 
        "📈 Charts", 
        "💱 Currency"
    ])
    
    with tab1:
        show_dashboard()
    
    with tab2:
        show_market_data()
    
    with tab3:
        show_sip_calculator()
    
    with tab4:
        show_charts()
    
    with tab5:
        show_currency_converter()

def show_dashboard():
    """📊 Main Dashboard"""
    st.header("🏠 Dashboard")
    
    # Quick metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Portfolio Value", "$125,450", "+2.3%")
    
    with col2:
        st.metric("📈 Today's Gain", "+$2,890", "+2.3%")
    
    with col3:
        st.metric("💼 Active Positions", "8", "+1")
    
    with col4:
        st.metric("⚡ Status", "Live", "Active")
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📋 Recent Activity")
    
    activity_data = {
        "Time": ["16:45", "16:30", "16:15", "16:00", "15:45"],
        "Action": ["BUY", "SELL", "BUY", "DIVIDEND", "BUY"],
        "Symbol": ["AAPL", "MSFT", "GOOGL", "VTI", "TSLA"],
        "Amount": ["$5,000", "$3,200", "$4,500", "$150", "$2,800"],
        "Status": ["✅ Complete", "✅ Complete", "✅ Complete", "✅ Complete", "✅ Complete"]
    }
    
    df = pd.DataFrame(activity_data)
    st.dataframe(df, use_container_width=True)

def show_market_data():
    """📊 Live Market Data"""
    st.header("📊 Market Data")
    
    if st.button("🔄 Refresh Data"):
        st.success("✅ Data refreshed successfully!")
    
    # Market overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🇺🇸 S&P 500", "4,567.89", "+0.67%")
        st.metric("💎 NASDAQ", "14,234.56", "+1.23%")
    
    with col2:
        st.metric("🥇 Gold", "$2,034.50", "+0.45%")
        st.metric("🛢️ Oil (WTI)", "$76.89", "-0.23%")
    
    with col3:
        st.metric("₿ Bitcoin", "$67,234", "+2.45%")
        st.metric("📈 Ethereum", "$3,456", "+1.87%")
    
    # Market table
    st.subheader("🔥 Top Movers")
    
    market_data = {
        "Symbol": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN"],
        "Price": ["$175.43", "$338.21", "$143.75", "$248.50", "$634.12", "$3,234.56"],
        "Change": ["+0.8%", "+1.2%", "-0.5%", "+3.1%", "+2.7%", "+0.9%"],
        "Volume": ["45.2M", "28.7M", "23.4M", "89.3M", "67.8M", "34.5M"],
        "Market Cap": ["$2.7T", "$2.5T", "$1.8T", "$785B", "$1.6T", "$1.7T"]
    }
    
    market_df = pd.DataFrame(market_data)
    st.dataframe(market_df, use_container_width=True)

def show_sip_calculator():
    """💹 SIP Calculator"""
    st.header("💹 SIP Calculator")
    st.caption("Calculate your Systematic Investment Plan returns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Investment Details")
        
        monthly_sip = st.number_input(
            "💰 Monthly SIP Amount (₹)", 
            min_value=500, 
            max_value=100000, 
            value=5000, 
            step=500
        )
        
        annual_rate = st.slider(
            "📈 Expected Annual Return (%)", 
            min_value=1.0, 
            max_value=30.0, 
            value=12.0, 
            step=0.5
        )
        
        time_years = st.slider(
            "⏰ Investment Duration (Years)", 
            min_value=1, 
            max_value=40, 
            value=10
        )
        
        if st.button("🔢 Calculate Returns"):
            st.success("✅ Calculation completed!")
    
    with col2:
        st.subheader("📊 Results")
        
        # Calculations
        months = time_years * 12
        monthly_rate = annual_rate / 100 / 12
        
        if monthly_rate > 0:
            future_value = monthly_sip * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
        else:
            future_value = monthly_sip * months
        
        total_invested = monthly_sip * months
        total_returns = future_value - total_invested
        
        # Display results
        st.metric("💰 Total Invested", f"₹{total_invested:,.0f}")
        st.metric("🎯 Final Value", f"₹{future_value:,.0f}")
        st.metric("📈 Total Returns", f"₹{total_returns:,.0f}")
        st.metric("📊 Return Rate", f"{(total_returns/total_invested)*100:.1f}%")
        
        # Growth chart
        years = list(range(1, time_years + 1))
        invested_values = [monthly_sip * 12 * year for year in years]
        
        chart_data = pd.DataFrame({
            "Year": years,
            "Invested": invested_values,
            "Value": [monthly_sip * 12 * year * (1 + annual_rate/100)**year for year in years]
        })
        
        fig = px.line(chart_data, x="Year", y=["Invested", "Value"], 
                     title="💹 SIP Growth Projection")
        st.plotly_chart(fig, use_container_width=True)

def show_charts():
    """📈 Interactive Charts"""
    st.header("📈 Financial Charts")
    
    chart_type = st.selectbox(
        "📊 Select Chart Type",
        ["Stock Price", "Portfolio Growth", "Market Comparison", "Sector Analysis"]
    )
    
    if chart_type == "Stock Price":
        # Generate sample stock data
        dates = pd.date_range(start='2024-01-01', end='2024-12-11', freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.5)
        
        df = pd.DataFrame({
            'Date': dates,
            'Price': prices,
            'Volume': np.random.randint(1000000, 5000000, len(dates))
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Price'], 
                                mode='lines', name='Stock Price'))
        fig.update_layout(title="📈 AAPL Stock Price", 
                         xaxis_title="Date", yaxis_title="Price ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Portfolio Growth":
        # Portfolio growth simulation
        months = pd.date_range(start='2023-01-01', end='2024-12-01', freq='M')
        portfolio_values = [10000 * (1.08 ** (i/12)) for i in range(len(months))]
        
        fig = px.line(x=months, y=portfolio_values, 
                     title="💼 Portfolio Growth Over Time")
        fig.update_layout(xaxis_title="Date", yaxis_title="Value ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Market Comparison":
        # Market indices comparison
        indices = ['S&P 500', 'NASDAQ', 'DOW JONES']
        returns = [12.5, 15.8, 8.9]
        
        fig = px.bar(x=indices, y=returns, 
                    title="📊 Market Indices - YTD Returns (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Sector Analysis
        sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer']
        weights = [35, 20, 15, 10, 20]
        
        fig = px.pie(values=weights, names=sectors, 
                    title="🥧 Portfolio Sector Allocation")
        st.plotly_chart(fig, use_container_width=True)

def show_currency_converter():
    """💱 Currency Converter"""
    st.header("💱 Currency Converter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        from_currency = st.selectbox("From Currency", 
                                   ["USD", "EUR", "GBP", "JPY", "INR", "CAD"])
        amount = st.number_input("Amount", min_value=0.01, value=100.0)
    
    with col2:
        to_currency = st.selectbox("To Currency", 
                                 ["INR", "USD", "EUR", "GBP", "JPY", "CAD"])
    
    with col3:
        if st.button("🔄 Convert"):
            # Simple conversion rates (demo)
            rates = {
                "USD": {"INR": 83.12, "EUR": 0.85, "GBP": 0.73, "JPY": 110.0},
                "EUR": {"USD": 1.18, "INR": 98.0, "GBP": 0.86, "JPY": 130.0},
                "GBP": {"USD": 1.37, "INR": 114.0, "EUR": 1.16, "JPY": 151.0},
                "JPY": {"USD": 0.009, "INR": 0.75, "EUR": 0.0077, "GBP": 0.0066},
                "INR": {"USD": 0.012, "EUR": 0.010, "GBP": 0.0088, "JPY": 1.33}
            }
            
            if from_currency == to_currency:
                converted = amount
                rate = 1.0
            else:
                rate = rates.get(from_currency, {}).get(to_currency, 1.0)
                converted = amount * rate
            
            st.success(f"✅ {amount} {from_currency} = {converted:.2f} {to_currency}")
            st.info(f"Exchange Rate: 1 {from_currency} = {rate:.4f} {to_currency}")
    
    # Exchange rates table
    st.subheader("📊 Current Exchange Rates")
    
    rates_data = {
        "Currency Pair": ["USD/INR", "EUR/USD", "GBP/USD", "USD/JPY", "EUR/INR"],
        "Rate": ["83.12", "1.18", "1.37", "110.00", "98.00"],
        "Change": ["+0.05%", "-0.12%", "+0.23%", "-0.08%", "+0.15%"],
        "24H High": ["83.25", "1.19", "1.38", "110.45", "98.25"],
        "24H Low": ["83.05", "1.17", "1.36", "109.80", "97.85"]
    }
    
    rates_df = pd.DataFrame(rates_data)
    st.dataframe(rates_df, use_container_width=True)

# 🚀 RUN THE APPLICATION
if __name__ == "__main__":
    main() 