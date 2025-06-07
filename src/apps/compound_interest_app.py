#!/usr/bin/env python3
"""
Compound Interest SIP Calculator - Streamlit App
Week 3 & 4 Implementation with Interactive UI
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os

# Add the core module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

try:
    from compound_interest_sip import CompoundInterestSIPCalculator
except ImportError:
    st.error("Could not import CompoundInterestSIPCalculator. Please ensure the core module is available.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Compound Interest SIP Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5aa0 50%, #1f4e79 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #ffd700;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #f7b733 0%, #fc4a1a 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #ffa502;
    }
    
    .error-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #ff4757;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #ffd700;
    }
</style>
""", unsafe_allow_html=True)

# Initialize calculator
@st.cache_resource
def get_calculator():
    return CompoundInterestSIPCalculator()

calc = get_calculator()

# Header
st.markdown("""
<div class="main-header">
    <h1>💰 Compound Interest SIP Calculator</h1>
    <p style="font-size: 1.2em; margin: 0;">Week 3 & 4: Annual Compounding & Monthly SIP Analysis</p>
    <p style="font-size: 0.9em; margin: 0.5em 0 0 0;">Formula: A = P(1 + r)^t | SIP: FV = PMT × [((1 + r)^n - 1) / r]</p>
    <p style="font-size: 0.8em; margin: 0.3em 0 0 0; opacity: 0.8;">🚀 Performance Optimized • AI-Powered Investment Suggestions</p>
</div>
""", unsafe_allow_html=True)

# Performance info
st.info("⚡ **Performance Optimized**: For investments longer than 3 years, calculations show key milestones (quarterly/yearly) instead of every month for faster results.")

# Sidebar for navigation
with st.sidebar:
    st.header("📊 Calculator Options")
    
    calculation_type = st.radio(
        "Choose Calculation Type:",
        ["🎯 Week 3: Annual Compound Interest", "📈 Week 4: Monthly SIP Compound", "🏦 Real Fund Analysis", "📊 Compare Scenarios"],
        help="Select the type of compound interest calculation you want to perform"
    )
    
    st.markdown("---")
    st.subheader("🎯 Quick Examples")
    
    if st.button("💻 SBI Small Cap (35% CAGR)"):
        st.session_state.quick_example = "sbi_small_cap"
    
    if st.button("📉 Quant Small Cap (-22.45% XIRR)"):
        st.session_state.quick_example = "quant_small_cap"
    
    if st.button("🛡️ Conservative (8% Returns)"):
        st.session_state.quick_example = "conservative"
    
    if st.button("🚀 Aggressive (25% Returns)"):
        st.session_state.quick_example = "aggressive"

# Main content based on calculation type
if calculation_type == "🎯 Week 3: Annual Compound Interest":
    st.header("🎯 Week 3: Annual Compound Interest Basics")
    st.info("💡 **Concept**: Use A = P(1 + r)^t for annual compounding")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Input Parameters")
        
        # Handle quick examples
        default_principal = 1000
        default_rate = 35.0
        default_years = 10
        
        if hasattr(st.session_state, 'quick_example'):
            if st.session_state.quick_example == "sbi_small_cap":
                default_principal = 1000
                default_rate = 35.0
                default_years = 10
            elif st.session_state.quick_example == "conservative":
                default_principal = 5000
                default_rate = 8.0
                default_years = 15
            elif st.session_state.quick_example == "aggressive":
                default_principal = 10000
                default_rate = 25.0
                default_years = 8
        
        principal = st.number_input(
            "💵 Principal Amount (₹)",
            min_value=100,
            max_value=10000000,
            value=default_principal,
            step=500,
            help="Initial investment amount in Indian Rupees"
        )
        
        rate = st.slider(
            "📈 Annual Interest Rate (%)",
            min_value=-30.0,
            max_value=50.0,
            value=default_rate,
            step=0.5,
            help="Expected annual return rate (can be negative for losses)"
        )
        
        time_years = st.slider(
            "⏰ Time Period (Years)",
            min_value=1,
            max_value=30,
            value=default_years,
            help="Investment duration in years"
        )
        
        if st.button("🧮 Calculate Annual Compound Interest", type="primary"):
            with st.spinner("Calculating compound interest..."):
                result = calc.calculate_annual_compound_interest(principal, rate, time_years)
                st.session_state.annual_result = result
    
    with col2:
        st.subheader("🎯 Week 3 Example")
        st.markdown("""
        **Financial Application:**
        - Model ₹1,000 SIP in SBI Small Cap
        - Long-term 35% CAGR
        - See your money grow exponentially!
        
        **AI Connection:**
        - AI Rule: "Increase SIP if growth > 10%"
        - Smart investment suggestions
        """)
    
    # Display results
    if hasattr(st.session_state, 'annual_result'):
        result = st.session_state.annual_result
        
        st.markdown("---")
        st.header("📊 Annual Compound Interest Results")
        
        # Main result card
        if result['profit'] >= 0:
            st.markdown(f"""
            <div class="success-card">
                <h2>🎉 👉 Your money grows to ₹{result['final_amount']:,.2f}! 👈</h2>
                <p><strong>Initial Investment:</strong> ₹{result['principal']:,.2f}</p>
                <p><strong>Final Amount:</strong> ₹{result['final_amount']:,.2f}</p>
                <p><strong>Total Profit:</strong> ₹{result['profit']:,.2f}</p>
                <p><strong>Return:</strong> {result['total_return_percent']:+.2f}%</p>
                <p><strong>Annual Growth:</strong> {result['annual_growth_rate']:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="error-card">
                <h2>📉 Investment Loss: ₹{abs(result['profit']):,.2f}</h2>
                <p><strong>Initial Investment:</strong> ₹{result['principal']:,.2f}</p>
                <p><strong>Final Amount:</strong> ₹{result['final_amount']:,.2f}</p>
                <p><strong>Loss:</strong> ₹{abs(result['profit']):,.2f}</p>
                <p><strong>Return:</strong> {result['total_return_percent']:+.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # AI Suggestion
        ai = result['ai_suggestion']
        if ai['should_increase']:
            st.markdown(f"""
            <div class="success-card">
                <h3>🤖 AI Investment Suggestion</h3>
                <p>{ai['reason']}</p>
                <p><strong>{ai['message']}</strong></p>
                <p>Suggested New Amount: ₹{ai['new_amount']:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info(f"🤖 **AI Analysis**: {ai['message']}")
        
        # Formula and metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Return", f"{result['total_return_percent']:+.1f}%")
        with col2:
            st.metric("📈 Annual Growth", f"{result['annual_growth_rate']:.1f}%")
        with col3:
            st.metric("💰 Profit", f"₹{result['profit']:,.0f}")
        
        st.code(result['formula_used'], language="text")
        
        # Year-wise breakdown
        if result['yearly_breakdown']:
            st.subheader("📈 Year-wise Growth Breakdown")
            df = pd.DataFrame(result['yearly_breakdown'])
            
            # Create growth chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['Year'], 
                y=df['Amount'],
                mode='lines+markers',
                name='Investment Value',
                line=dict(color='green', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title=f"₹{principal:,} Growing at {rate}% Annual Compound Interest",
                xaxis_title="Year",
                yaxis_title="Amount (₹)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            df['Amount'] = df['Amount'].apply(lambda x: f"₹{x:,.2f}")
            df['Interest_Earned'] = df['Interest_Earned'].apply(lambda x: f"₹{x:,.2f}")
            df['Total_Return_Percent'] = df['Total_Return_Percent'].apply(lambda x: f"{x:+.1f}%")
            st.dataframe(df, use_container_width=True, hide_index=True)

elif calculation_type == "📈 Week 4: Monthly SIP Compound":
    st.header("📈 Week 4: Monthly SIP Compound Interest")
    st.info("💡 **Concept**: Apply compound interest to monthly SIPs using FV = PMT × [((1 + r)^n - 1) / r]")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 SIP Parameters")
        
        # Handle quick examples
        default_sip = 1000
        default_rate = 35.0
        default_years = 5
        
        if hasattr(st.session_state, 'quick_example'):
            if st.session_state.quick_example == "quant_small_cap":
                default_sip = 1000
                default_rate = -22.45
                default_years = 1
            elif st.session_state.quick_example == "conservative":
                default_sip = 3000
                default_rate = 8.0
                default_years = 10
            elif st.session_state.quick_example == "aggressive":
                default_sip = 5000
                default_rate = 25.0
                default_years = 7
        
        monthly_sip = st.number_input(
            "💰 Monthly SIP Amount (₹)",
            min_value=100,
            max_value=100000,
            value=default_sip,
            step=500,
            help="Amount to invest every month"
        )
        
        annual_rate = st.slider(
            "📊 Annual Return Rate (%)",
            min_value=-50.0,
            max_value=50.0,
            value=default_rate,
            step=0.25,
            help="Expected annual return rate (XIRR/CAGR)"
        )
        
        time_years = st.slider(
            "📅 Investment Period (Years)",
            min_value=0.5,
            max_value=20.0,
            value=float(default_years),
            step=0.5,
            help="SIP duration in years"
        )
        
        if st.button("📈 Calculate Monthly SIP Returns", type="primary"):
            # Show optimization info for long-term investments
            if time_years > 3:
                st.info("🚀 **Performance Optimization**: For investments longer than 3 years, we'll show key milestones instead of every month for faster calculation.")
            
            with st.spinner("Calculating monthly SIP compound interest..."):
                result = calc.calculate_monthly_sip_compound(monthly_sip, annual_rate, time_years)
                st.session_state.sip_result = result
    
    with col2:
        st.subheader("🎯 Week 4 Example")
        st.markdown("""
        **Financial Application:**
        - Calculate 1-year SIP value
        - Quant Small Cap (-22.45% XIRR)
        - See the impact of negative returns
        
        **Features:**
        - Monthly compounding
        - Growth visualization
        - AI suggestions
        """)
    
    # Display SIP results
    if hasattr(st.session_state, 'sip_result'):
        result = st.session_state.sip_result
        
        st.markdown("---")
        st.header("📊 Monthly SIP Compound Interest Results")
        
        # Main result card
        if result['profit'] >= 0:
            st.markdown(f"""
            <div class="success-card">
                <h2>🎉 👉 Your SIP grows to ₹{result['final_value']:,.2f}! 👈</h2>
                <p><strong>Monthly SIP:</strong> ₹{result['monthly_sip']:,.0f} × {result['total_months']} months</p>
                <p><strong>Total Invested:</strong> ₹{result['total_invested']:,.2f}</p>
                <p><strong>Portfolio Value:</strong> ₹{result['final_value']:,.2f}</p>
                <p><strong>Total Profit:</strong> ₹{result['profit']:,.2f}</p>
                <p><strong>Return:</strong> {result['total_return_percent']:+.2f}%</p>
                <p><strong>Risk Level:</strong> {result['risk_level']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="error-card">
                <h2>📉 SIP Loss: ₹{abs(result['profit']):,.2f}</h2>
                <p><strong>Monthly SIP:</strong> ₹{result['monthly_sip']:,.0f} × {result['total_months']} months</p>
                <p><strong>Total Invested:</strong> ₹{result['total_invested']:,.2f}</p>
                <p><strong>Portfolio Value:</strong> ₹{result['final_value']:,.2f}</p>
                <p><strong>Loss:</strong> ₹{abs(result['profit']):,.2f}</p>
                <p><strong>Return:</strong> {result['total_return_percent']:+.2f}%</p>
                <p><strong>Risk Level:</strong> {result['risk_level']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # AI Suggestion
        ai = result['ai_suggestion']
        if ai['should_increase']:
            st.success(f"🤖 **AI Suggestion**: {ai['message']}")
        else:
            st.info(f"🤖 **AI Analysis**: {ai['message']}")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total Invested", f"₹{result['total_invested']:,.0f}")
        with col2:
            st.metric("📈 Portfolio Value", f"₹{result['final_value']:,.0f}")
        with col3:
            st.metric("💵 Profit/Loss", f"₹{result['profit']:,.0f}")
        with col4:
            st.metric("📊 Annual Return", f"{result['effective_annual_return']:+.1f}%")
        
        st.code(result['formula_used'], language="text")
        
        # Growth chart
        if result['monthly_breakdown']:
            st.subheader("📈 SIP Growth Visualization")
            
            df = pd.DataFrame(result['monthly_breakdown'])
            
            # Create comprehensive chart
            fig = calc.create_growth_chart(result)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show data table with optimization
            table_title = "📋 Monthly Breakdown"
            if result.get('is_optimized', False):
                table_title += " (Key Milestones)"
                st.info("📊 **Optimized View**: Showing quarterly and yearly milestones for better performance.")
            else:
                table_title += " (Sample - First 12 Months)"
            
            st.subheader(table_title)
            
            # Show appropriate number of rows
            display_rows = len(df) if result.get('is_optimized', False) else min(12, len(df))
            display_df = df.head(display_rows).copy()
            
            # Format the data
            display_df['Total_Invested'] = display_df['Total_Invested'].apply(lambda x: f"₹{x:,.0f}")
            display_df['Portfolio_Value'] = display_df['Portfolio_Value'].apply(lambda x: f"₹{x:,.0f}")
            display_df['Profit'] = display_df['Profit'].apply(lambda x: f"₹{x:,.0f}")
            display_df['Return_Percent'] = display_df['Return_Percent'].apply(lambda x: f"{x:+.1f}%")
            
            # Show milestone indicator if optimized
            columns_to_show = ['Month', 'Year', 'Total_Invested', 'Portfolio_Value', 'Profit', 'Return_Percent']
            if result.get('is_optimized', False):
                display_df['Type'] = '🎯 Milestone'
                columns_to_show = ['Month', 'Year', 'Type', 'Total_Invested', 'Portfolio_Value', 'Profit', 'Return_Percent']
            
            st.dataframe(display_df[columns_to_show], use_container_width=True, hide_index=True)

elif calculation_type == "🏦 Real Fund Analysis":
    st.header("🏦 Real Mutual Fund Performance Analysis")
    st.info("💡 **Analyze real fund performance with historical XIRR data**")
    
    # Pre-defined funds with real data
    funds_data = {
        "SBI Small Cap Fund": {"xirr": 35.0, "description": "High-growth small cap fund", "risk": "High"},
        "Quant Small Cap Fund": {"xirr": -22.45, "description": "Underperforming small cap", "risk": "Very High"},
        "HDFC Top 100 Fund": {"xirr": 12.5, "description": "Large cap stable fund", "risk": "Moderate"},
        "Axis Bluechip Fund": {"xirr": 15.8, "description": "Large cap growth fund", "risk": "Moderate"},
        "ICICI Prudential Technology": {"xirr": 28.9, "description": "Sector-focused tech fund", "risk": "High"},
        "Mirae Asset Large Cap": {"xirr": 11.2, "description": "Conservative large cap", "risk": "Low"},
        "Parag Parikh Flexi Cap": {"xirr": 18.4, "description": "Flexible allocation fund", "risk": "Moderate-High"},
        "UTI Nifty Index Fund": {"xirr": 10.8, "description": "Index tracking fund", "risk": "Low-Moderate"}
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Fund Selection & Parameters")
        
        selected_fund = st.selectbox(
            "🏦 Choose Mutual Fund",
            list(funds_data.keys()),
            help="Select a real mutual fund to analyze"
        )
        
        fund_info = funds_data[selected_fund]
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.info(f"**Description**: {fund_info['description']}")
        with col_b:
            st.warning(f"**Risk Level**: {fund_info['risk']}")
        
        monthly_sip = st.number_input(
            "💰 Monthly SIP (₹)",
            min_value=500,
            max_value=50000,
            value=5000,
            step=500
        )
        
        xirr_rate = st.number_input(
            "📊 Fund XIRR (%)",
            value=fund_info["xirr"],
            step=0.1,
            help="Historical XIRR of the selected fund"
        )
        
        time_years = st.slider(
            "📅 Investment Period (Years)",
            min_value=1.0,
            max_value=15.0,
            value=5.0,
            step=0.5
        )
        
        if st.button("🏦 Analyze Fund Performance", type="primary"):
            with st.spinner(f"Analyzing {selected_fund} performance..."):
                result = calc.model_real_fund_performance(selected_fund, monthly_sip, xirr_rate, time_years)
                st.session_state.fund_result = result
    
    with col2:
        st.subheader("🏦 Available Funds")
        for fund, info in funds_data.items():
            emoji = "🟢" if info["xirr"] > 15 else "🟡" if info["xirr"] > 0 else "🔴"
            st.write(f"{emoji} **{fund}**")
            st.write(f"   XIRR: {info['xirr']:+.1f}%")
            st.write(f"   Risk: {info['risk']}")
            st.write("---")
    
    # Display fund analysis results
    if hasattr(st.session_state, 'fund_result'):
        result = st.session_state.fund_result
        
        st.markdown("---")
        st.header(f"📊 {result['fund_name']} Analysis")
        
        # Fund result card
        if result['profit'] >= 0:
            st.markdown(f"""
            <div class="success-card">
                <h2>🏦 {result['fund_name']} Performance</h2>
                <p><strong>XIRR:</strong> {result['xirr_rate']:+.2f}%</p>
                <p><strong>Monthly SIP:</strong> ₹{result['monthly_sip']:,.0f}</p>
                <p><strong>Total Invested:</strong> ₹{result['total_invested']:,.2f}</p>
                <p><strong>Portfolio Value:</strong> ₹{result['final_value']:,.2f}</p>
                <p><strong>Profit:</strong> ₹{result['profit']:,.2f}</p>
                <p><strong>Risk Level:</strong> {result['risk_level']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="error-card">
                <h2>🏦 {result['fund_name']} Performance</h2>
                <p><strong>XIRR:</strong> {result['xirr_rate']:+.2f}%</p>
                <p><strong>Monthly SIP:</strong> ₹{result['monthly_sip']:,.0f}</p>
                <p><strong>Total Invested:</strong> ₹{result['total_invested']:,.2f}</p>
                <p><strong>Portfolio Value:</strong> ₹{result['final_value']:,.2f}</p>
                <p><strong>Loss:</strong> ₹{abs(result['profit']):,.2f}</p>
                <p><strong>Risk Level:</strong> {result['risk_level']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        if 'warning' in result:
            st.error(result['warning'])
        
        # Generate and display report
        report = calc.generate_report(result)
        with st.expander("📋 Detailed Analysis Report"):
            st.text(report)

elif calculation_type == "📊 Compare Scenarios":
    st.header("📊 Compare Investment Scenarios")
    st.info("💡 **Compare different SIP scenarios side by side**")
    
    # Create three scenarios
    col1, col2, col3 = st.columns(3)
    
    scenarios = {}
    
    with col1:
        st.subheader("🟢 Scenario 1: Conservative")
        sip1 = st.number_input("Monthly SIP 1 (₹)", value=3000, step=500, key="sip1")
        rate1 = st.slider("Annual Rate 1 (%)", -10.0, 40.0, 8.0, key="rate1")
        years1 = st.slider("Years 1", 1, 20, 10, key="years1")
        
        if st.button("Calculate Scenario 1", key="calc1"):
            scenarios['Conservative'] = calc.calculate_monthly_sip_compound(sip1, rate1, years1)
    
    with col2:
        st.subheader("🟡 Scenario 2: Moderate")
        sip2 = st.number_input("Monthly SIP 2 (₹)", value=5000, step=500, key="sip2")
        rate2 = st.slider("Annual Rate 2 (%)", -10.0, 40.0, 15.0, key="rate2")
        years2 = st.slider("Years 2", 1, 20, 10, key="years2")
        
        if st.button("Calculate Scenario 2", key="calc2"):
            scenarios['Moderate'] = calc.calculate_monthly_sip_compound(sip2, rate2, years2)
    
    with col3:
        st.subheader("🔴 Scenario 3: Aggressive")
        sip3 = st.number_input("Monthly SIP 3 (₹)", value=7000, step=500, key="sip3")
        rate3 = st.slider("Annual Rate 3 (%)", -10.0, 40.0, 25.0, key="rate3")
        years3 = st.slider("Years 3", 1, 20, 10, key="years3")
        
        if st.button("Calculate Scenario 3", key="calc3"):
            scenarios['Aggressive'] = calc.calculate_monthly_sip_compound(sip3, rate3, years3)
    
    # Store scenarios in session state
    if scenarios:
        st.session_state.scenarios = scenarios
    
    # Display comparison
    if hasattr(st.session_state, 'scenarios') and st.session_state.scenarios:
        st.markdown("---")
        st.header("📊 Scenario Comparison")
        
        scenarios = st.session_state.scenarios
        
        # Create comparison table
        comparison_data = []
        for name, result in scenarios.items():
            comparison_data.append({
                'Scenario': name,
                'Monthly_SIP': f"₹{result['monthly_sip']:,.0f}",
                'Annual_Rate': f"{result['annual_rate']:+.1f}%",
                'Years': result['time_years'],
                'Total_Invested': f"₹{result['total_invested']:,.0f}",
                'Final_Value': f"₹{result['final_value']:,.0f}",
                'Profit': f"₹{result['profit']:,.0f}",
                'Return_Percent': f"{result['total_return_percent']:+.1f}%",
                'Risk_Level': result['risk_level']
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)
        
        # Comparison chart
        fig = go.Figure()
        
        for name, result in scenarios.items():
            fig.add_trace(go.Bar(
                name=name,
                x=['Invested', 'Final Value'],
                y=[result['total_invested'], result['final_value']],
                text=[f"₹{result['total_invested']:,.0f}", f"₹{result['final_value']:,.0f}"],
                textposition='auto'
            ))
        
        fig.update_layout(
            title="💰 Investment Scenarios Comparison",
            barmode='group',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>💡 <strong>Formula References:</strong></p>
    <p>Week 3 - Annual Compound: A = P(1 + r)^t</p>
    <p>Week 4 - Monthly SIP: FV = PMT × [((1 + r)^n - 1) / r]</p>
    <p style="margin-top: 20px; font-size: 0.9em;">
        Built using Claude 4 • AI-Powered Investment Calculator • Real Fund Analysis
    </p>
</div>
""", unsafe_allow_html=True) 