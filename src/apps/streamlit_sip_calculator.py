#!/usr/bin/env python3
"""
💰 Interactive SIP Calculator with Portfolio Analysis - Streamlit App
A beautiful web interface for calculating investment growth with portfolio analysis and AI recommendations
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Configure Streamlit page
st.set_page_config(
    page_title="💰 SIP Calculator with Portfolio Analysis",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def calculate_compound_interest(principal, rate, time):
    """Calculate compound interest"""
    final_amount = principal * (1 + rate/100) ** time
    growth_percentage = ((final_amount - principal) / principal) * 100
    return final_amount, growth_percentage

def ai_recommendation(growth_percentage, current_amount):
    """AI-powered recommendation system"""
    if growth_percentage > 10:
        suggested_increase = min(current_amount * 0.2, 10000)
        return {
            'status': 'excellent',
            'message': f"""
🚀 **Excellent growth of {growth_percentage:.1f}%!**
💡 Consider increasing your SIP by ₹{suggested_increase:,.0f} to maximize your wealth!
🎯 Higher investments in good-performing assets can compound your returns exponentially.
""",
            'color': 'success'
        }
    elif growth_percentage > 5:
        return {
            'status': 'good',
            'message': f"""
✅ **Good growth of {growth_percentage:.1f}%!**
📈 Your investment is performing well. Consider maintaining this strategy.
""",
            'color': 'info'
        }
    else:
        return {
            'status': 'needs_improvement',
            'message': f"""
⚠️ **Growth of {growth_percentage:.1f}% could be improved.**
💭 Consider reviewing your investment strategy or exploring higher-yield options.
""",
            'color': 'warning'
        }

def create_allocation_pie_chart(portfolio_data):
    """Create interactive pie chart for portfolio allocation"""
    names = [item['name'] for item in portfolio_data]
    allocations = [item['allocation'] for item in portfolio_data]
    returns = [item['growth_percentage'] for item in portfolio_data]
    
    # Create custom hover text
    hover_text = [
        f"<b>{name}</b><br>" +
        f"Allocation: {allocation:.1f}%<br>" +
        f"Return: {return_rate:.1f}%<br>" +
        f"Principal: ₹{item['principal']:,.0f}<br>" +
        f"Final: ₹{item['final_amount']:,.0f}"
        for name, allocation, return_rate, item in zip(names, allocations, returns, portfolio_data)
    ]
    
    fig = go.Figure(data=[go.Pie(
        labels=names,
        values=allocations,
        hole=0.4,
        hovertemplate="%{text}<extra></extra>",
        text=hover_text,
        textinfo='label+percent',
        textposition='auto'
    )])
    
    fig.update_layout(
        title={
            'text': "💼 Portfolio Allocation Distribution",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        font=dict(size=12),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    return fig

def create_returns_bar_chart(portfolio_data):
    """Create interactive bar chart for returns comparison"""
    df = pd.DataFrame(portfolio_data)
    
    # Color code based on performance
    colors = []
    for growth in df['growth_percentage']:
        if growth > 10:
            colors.append('#28a745')  # Green for excellent
        elif growth > 5:
            colors.append('#17a2b8')  # Blue for good
        else:
            colors.append('#ffc107')  # Yellow for needs improvement
    
    fig = go.Figure(data=[
        go.Bar(
            x=df['name'],
            y=df['growth_percentage'],
            marker_color=colors,
            text=[f"{x:.1f}%" for x in df['growth_percentage']],
            textposition='auto',
            hovertemplate="<b>%{x}</b><br>" +
                         "Return: %{y:.1f}%<br>" +
                         "Principal: ₹%{customdata[0]:,.0f}<br>" +
                         "Final: ₹%{customdata[1]:,.0f}<extra></extra>",
            customdata=list(zip(df['principal'], df['final_amount']))
        )
    ])
    
    fig.update_layout(
        title={
            'text': "📈 Investment Returns Comparison",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="Investments",
        yaxis_title="Return (%)",
        font=dict(size=12),
        yaxis=dict(tickformat='.1f')
    )
    
    return fig

def main():
    # Header
    st.title("💰 SIP Calculator with Portfolio Analysis")
    st.markdown("**A comprehensive tool for calculating investment growth with AI recommendations**")
    
    # Sidebar for navigation
    st.sidebar.title("🧭 Navigation")
    app_mode = st.sidebar.selectbox(
        "Choose Application Mode:",
        ["🔢 Simple SIP Calculator", "💼 Portfolio Analysis"]
    )
    
    if app_mode == "🔢 Simple SIP Calculator":
        st.header("🔢 Simple SIP Calculator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            principal = st.number_input(
                "💵 Principal Amount (₹)",
                min_value=1.0,
                value=100000.0,
                step=1000.0,
                help="Enter the initial investment amount"
            )
            
            rate = st.number_input(
                "📈 Annual Interest Rate (%)",
                min_value=0.1,
                max_value=50.0,
                value=12.0,
                step=0.1,
                help="Expected annual return percentage"
            )
            
            time = st.number_input(
                "⏰ Time Period (years)",
                min_value=0.1,
                max_value=50.0,
                value=10.0,
                step=0.1,
                help="Investment duration in years"
            )
        
        with col2:
            if st.button("💰 Calculate Returns", type="primary"):
                final_amount, growth_percentage = calculate_compound_interest(principal, rate, time)
                
                # Display results
                st.success(f"🎉 **Your money grows to ₹{final_amount:,.2f}!**")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("💰 Final Amount", f"₹{final_amount:,.2f}", f"₹{final_amount - principal:,.2f}")
                with col_b:
                    st.metric("📈 Total Growth", f"{growth_percentage:.2f}%")
                with col_c:
                    st.metric("💵 Profit", f"₹{final_amount - principal:,.2f}")
                
                # AI Recommendation
                ai_rec = ai_recommendation(growth_percentage, principal)
                if ai_rec['color'] == 'success':
                    st.success(f"🤖 **AI Recommendation:**\n{ai_rec['message']}")
                elif ai_rec['color'] == 'info':
                    st.info(f"🤖 **AI Recommendation:**\n{ai_rec['message']}")
                else:
                    st.warning(f"🤖 **AI Recommendation:**\n{ai_rec['message']}")
    
    elif app_mode == "💼 Portfolio Analysis":
        st.header("💼 Portfolio Analysis with Allocation")
        
        # Portfolio setup
        st.subheader("📊 Portfolio Setup")
        
        num_investments = st.number_input(
            "How many investments in your portfolio?",
            min_value=2,
            max_value=10,
            value=3,
            step=1
        )
        
        # Dynamic input fields for portfolio
        portfolio_data = []
        total_allocation = 0
        
        st.markdown("---")
        
        for i in range(num_investments):
            st.subheader(f"💰 Investment {i+1}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                name = st.text_input(
                    f"Name",
                    value=f"Investment {i+1}",
                    key=f"name_{i}"
                )
            
            with col2:
                principal = st.number_input(
                    f"Principal (₹)",
                    min_value=1.0,
                    value=50000.0,
                    step=1000.0,
                    key=f"principal_{i}"
                )
            
            with col3:
                rate = st.number_input(
                    f"Return (%)",
                    min_value=0.1,
                    max_value=50.0,
                    value=12.0,
                    step=0.1,
                    key=f"rate_{i}"
                )
            
            with col4:
                allocation = st.number_input(
                    f"Allocation (%)",
                    min_value=0.1,
                    max_value=100.0,
                    value=100.0/num_investments,
                    step=0.1,
                    key=f"allocation_{i}"
                )
            
            time = st.number_input(
                f"Time Period (years)",
                min_value=0.1,
                max_value=50.0,
                value=10.0,
                step=0.1,
                key=f"time_{i}"
            )
            
            # Calculate individual investment
            final_amount, growth_percentage = calculate_compound_interest(principal, rate, time)
            
            portfolio_data.append({
                'name': name,
                'principal': principal,
                'rate': rate,
                'time': time,
                'allocation': allocation,
                'final_amount': final_amount,
                'growth_percentage': growth_percentage,
                'profit': final_amount - principal
            })
            
            total_allocation += allocation
            
            st.markdown("---")
        
        # Allocation validation
        if abs(total_allocation - 100) > 0.01:
            st.warning(f"⚠️ Total allocation is {total_allocation:.1f}%, not 100%")
            if st.button("🔄 Normalize Allocations to 100%"):
                for item in portfolio_data:
                    item['allocation'] = (item['allocation'] / total_allocation) * 100
                st.success("✅ Allocations normalized!")
        
        # Calculate portfolio results
        if st.button("📊 Analyze Portfolio", type="primary"):
            # Calculate weighted returns
            total_weighted_return = sum(item['growth_percentage'] * item['allocation'] / 100 for item in portfolio_data)
            total_weighted_amount = sum(item['final_amount'] * item['allocation'] / 100 for item in portfolio_data)
            total_principal = sum(item['principal'] for item in portfolio_data)
            total_profit = total_weighted_amount - total_principal
            
            # Display portfolio summary
            st.success(f"🎉 **Your portfolio grows to ₹{total_weighted_amount:,.2f}!**")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 Total Investment", f"₹{total_principal:,.2f}")
            with col2:
                st.metric("📈 Portfolio Return", f"{total_weighted_return:.2f}%")
            with col3:
                st.metric("💹 Portfolio Value", f"₹{total_weighted_amount:,.2f}")
            with col4:
                st.metric("💵 Total Profit", f"₹{total_profit:,.2f}")
            
            # Charts
            st.subheader("📊 Portfolio Visualizations")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Pie chart
                pie_fig = create_allocation_pie_chart(portfolio_data)
                st.plotly_chart(pie_fig, use_container_width=True)
            
            with col_chart2:
                # Bar chart
                bar_fig = create_returns_bar_chart(portfolio_data)
                st.plotly_chart(bar_fig, use_container_width=True)
            
            # Detailed results table
            st.subheader("🔍 Detailed Investment Analysis")
            
            df_results = pd.DataFrame(portfolio_data)
            df_results['Final Amount (₹)'] = df_results['final_amount'].apply(lambda x: f"₹{x:,.2f}")
            df_results['Principal (₹)'] = df_results['principal'].apply(lambda x: f"₹{x:,.2f}")
            df_results['Profit (₹)'] = df_results['profit'].apply(lambda x: f"₹{x:,.2f}")
            df_results['Return (%)'] = df_results['growth_percentage'].apply(lambda x: f"{x:.2f}%")
            df_results['Allocation (%)'] = df_results['allocation'].apply(lambda x: f"{x:.1f}%")
            
            display_df = df_results[['name', 'Principal (₹)', 'Final Amount (₹)', 'Return (%)', 'Allocation (%)', 'Profit (₹)']]
            display_df.columns = ['Investment', 'Principal', 'Final Amount', 'Return', 'Allocation', 'Profit']
            
            st.dataframe(display_df, use_container_width=True)
            
            # AI Portfolio Recommendations
            st.subheader("🤖 AI Portfolio Analysis")
            
            best_performer = max(portfolio_data, key=lambda x: x['growth_percentage'])
            worst_performer = min(portfolio_data, key=lambda x: x['growth_percentage'])
            
            if total_weighted_return > 15:
                st.success(f"""
🚀 **EXCELLENT** portfolio performance with {total_weighted_return:.2f}% weighted return!
💡 Your diversification strategy is working well.
🎯 Consider increasing allocation to **{best_performer['name']}** (top performer with {best_performer['growth_percentage']:.1f}% return)
""")
            elif total_weighted_return > 10:
                st.info(f"""
✅ **GOOD** portfolio performance with {total_weighted_return:.2f}% weighted return!
📈 Your portfolio is beating inflation comfortably.
💡 Consider rebalancing towards better performers.
""")
            elif total_weighted_return > 5:
                st.warning(f"""
⚖️ **MODERATE** portfolio performance with {total_weighted_return:.2f}% weighted return.
🔍 Review underperforming investments.
⚠️ Consider reducing allocation to **{worst_performer['name']}** (lowest performer with {worst_performer['growth_percentage']:.1f}% return)
""")
            else:
                st.error(f"""
⚠️ Portfolio needs **IMPROVEMENT** with {total_weighted_return:.2f}% weighted return!
🔄 Consider diversifying into higher-return assets.
💭 Review your investment strategy with a financial advisor.
""")
            
            # Diversification analysis
            allocations = [item['allocation'] for item in portfolio_data]
            if max(allocations) > 60:
                st.warning("⚠️ **CONCENTRATION RISK**: One investment dominates your portfolio. Consider better diversification.")
            elif len(portfolio_data) >= 4 and max(allocations) < 40:
                st.success("✅ **GOOD DIVERSIFICATION**: Well-balanced portfolio allocation.")
    
    # Footer
    st.markdown("---")
    st.markdown("💫 **Happy Investing!** • Built with Streamlit & ❤️")

if __name__ == "__main__":
    main() 