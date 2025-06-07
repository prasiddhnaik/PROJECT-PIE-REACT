import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime
import warnings
import math
warnings.filterwarnings('ignore')

# Import our portfolio calculator
from portfolio_return_calculator import PortfolioReturnCalculator

# Page configuration
st.set_page_config(
    page_title="AI Portfolio Advisor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling and scroll wheel
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 10px 0;
    }
    
    .warning-card {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .critical-card {
        background: #f8d7da;
        border: 1px solid #dc3545;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .success-card {
        background: #d1e7dd;
        border: 1px solid #198754;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Custom scroll wheel input styling */
    .scroll-input {
        width: 100%;
        padding: 10px;
        border: 2px solid #667eea;
        border-radius: 5px;
        font-size: 16px;
        text-align: center;
    }
    
    .allocation-container {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>

<script>
function updateAllocation(fundName, delta) {
    const inputElement = document.getElementById('allocation_' + fundName);
    if (inputElement) {
        let currentValue = parseFloat(inputElement.value) || 0;
        let newValue = Math.max(0, Math.min(100, currentValue + delta));
        inputElement.value = newValue.toFixed(1);
        inputElement.dispatchEvent(new Event('change'));
    }
}

// Add scroll wheel functionality
document.addEventListener('wheel', function(e) {
    if (e.target.classList.contains('scroll-input')) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -1 : 1;
        const fundName = e.target.id.replace('allocation_', '');
        updateAllocation(fundName, delta);
    }
});
</script>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'calculator' not in st.session_state:
        st.session_state.calculator = PortfolioReturnCalculator()
    
    if 'funds_loaded' not in st.session_state:
        st.session_state.funds_loaded = []
    
    if 'allocations' not in st.session_state:
        st.session_state.allocations = {}
    
    if 'auto_normalize' not in st.session_state:
        st.session_state.auto_normalize = True

def load_fund_data():
    """Load fund data section"""
    st.subheader("📂 Load Fund Data")
    
    # Predefined funds
    predefined_funds = {
        "Nippon Small Cap": "real_nav_data.csv",
        "HDFC Small Cap": "hdfc_nav_data.csv",
        "Axis Multi Asset": "axis_nav_data.csv"
    }
    
    st.write("**Quick Load Predefined Funds:**")
    
    col1, col2 = st.columns(2)
    
    for i, (fund_name, file_path) in enumerate(predefined_funds.items()):
        with col1 if i % 2 == 0 else col2:
            if st.button(f"Load {fund_name}", key=f"load_{fund_name}"):
                try:
                    if st.session_state.calculator.load_fund_data(fund_name, file_path):
                        if fund_name not in st.session_state.funds_loaded:
                            st.session_state.funds_loaded.append(fund_name)
                        st.success(f"✅ Loaded {fund_name}")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error loading {fund_name}: {str(e)}")
    
    if st.session_state.funds_loaded:
        col_header, col_clear_all = st.columns([3, 1])
        with col_header:
            st.write("**Loaded Funds:**")
        with col_clear_all:
            if st.button("🗑️ Remove All", key="remove_all_funds", help="Remove all loaded funds", type="secondary"):
                st.session_state["confirm_remove_all"] = True
                st.rerun()
        for fund in st.session_state.funds_loaded:
            col_fund, col_remove = st.columns([4, 1])
            with col_fund:
                # Get fund info if available
                fund_data = st.session_state.calculator.funds_data.get(fund)
                if fund_data is not None:
                    data_points = len(fund_data)
                    st.write(f"• **{fund}** ({data_points} data points)")
                else:
                    st.write(f"• **{fund}**")
            with col_remove:
                if st.button("❌", key=f"remove_{fund}", help=f"Remove {fund} from portfolio", type="secondary"):
                    # Show confirmation in a more subtle way
                    st.session_state[f"confirm_remove_{fund}"] = True
                    st.rerun()
        
        # Handle confirmation dialogs
        for fund in st.session_state.funds_loaded[:]:  # Create a copy to avoid modification during iteration
            if st.session_state.get(f"confirm_remove_{fund}", False):
                st.warning(f"⚠️ Are you sure you want to remove **{fund}**? This will clear all its data and allocations.")
                col_yes, col_no = st.columns(2)
                
                with col_yes:
                    if st.button(f"✅ Yes, Remove {fund}", key=f"confirm_yes_{fund}"):
                        # Remove fund from calculator
                        if fund in st.session_state.calculator.funds_data:
                            del st.session_state.calculator.funds_data[fund]
                        
                        # Remove from loaded funds list
                        if fund in st.session_state.funds_loaded:
                            st.session_state.funds_loaded.remove(fund)
                        
                        # Remove from allocations if present
                        if fund in st.session_state.allocations:
                            del st.session_state.allocations[fund]
                        
                        # Clear confirmation state
                        if f"confirm_remove_{fund}" in st.session_state:
                            del st.session_state[f"confirm_remove_{fund}"]
                        
                        st.success(f"🗑️ Removed {fund} successfully!")
                        st.rerun()
                
                with col_no:
                    if st.button(f"❌ Cancel", key=f"confirm_no_{fund}"):
                        # Clear confirmation state
                        if f"confirm_remove_{fund}" in st.session_state:
                            del st.session_state[f"confirm_remove_{fund}"]
                        st.rerun()
        
        # Handle "Remove All" confirmation
        if st.session_state.get("confirm_remove_all", False):
            st.error("⚠️ **Are you sure you want to remove ALL funds?** This will clear all data and allocations.")
            col_yes_all, col_no_all = st.columns(2)
            
            with col_yes_all:
                if st.button("✅ Yes, Remove All Funds", key="confirm_yes_all"):
                    # Clear all fund data
                    st.session_state.calculator.funds_data.clear()
                    st.session_state.funds_loaded.clear()
                    st.session_state.allocations.clear()
                    
                    # Clear confirmation state
                    if "confirm_remove_all" in st.session_state:
                        del st.session_state["confirm_remove_all"]
                    
                    st.success("🗑️ All funds removed successfully!")
                    st.rerun()
            
            with col_no_all:
                if st.button("❌ Cancel", key="confirm_no_all"):
                    if "confirm_remove_all" in st.session_state:
                        del st.session_state["confirm_remove_all"]
                    st.rerun()

def display_individual_returns():
    """Display individual fund returns with AI warnings"""
    if not st.session_state.funds_loaded:
        st.warning("Please load fund data first!")
        return None
    
    st.subheader("📊 Individual Fund Performance")
    
    returns_data = []
    
    for fund_name in st.session_state.funds_loaded:
        ret_data = st.session_state.calculator.calculate_percentage_return(fund_name)
        if ret_data:
            returns_data.append(ret_data)
            
            # Create metric card
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                # Consistent card format for all funds
                # Determine color based on performance but keep same structure
                if ret_data['return_percent'] < -15:
                    return_color = "#dc3545"  # Red
                    card_class = "critical-card"
                elif ret_data['return_percent'] < -5:
                    return_color = "#856404"  # Orange
                    card_class = "warning-card"
                elif ret_data['return_percent'] < 0:
                    return_color = "#856404"  # Orange for any negative
                    card_class = "warning-card"
                else:
                    return_color = "#198754"  # Green
                    card_class = "success-card"
                
                st.markdown(f"""
                <div class="{card_class}">
                    <h4>{fund_name}</h4>
                    <h2 style="color: {return_color};">Return: {ret_data['return_percent']:.2f}%</h2>
                    <p>Period: {ret_data['start_date']} to {ret_data['end_date']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.metric("Start NAV", f"₹{ret_data['nav_start']:.2f}")
            
            with col3:
                st.metric("End NAV", f"₹{ret_data['nav_end']:.2f}")
            
            # AI Advisor analysis (always show for consistency)
            ai_advice = st.session_state.calculator.ai_advisor_warning(ret_data['return_percent'], fund_name)
            
            # Always show AI advisor, but expand based on performance
            with st.expander(f"🤖 AI Advisor for {fund_name}", expanded=ret_data['return_percent'] < -5):
                # Always show risk level
                st.info(f"🎯 Risk Level: **{ai_advice['risk_level']}**")
                
                # Show warnings if any
                if ai_advice['warnings']:
                    for warning in ai_advice['warnings']:
                        st.warning(warning)
                else:
                    # Show positive message for good performance
                    if ret_data['return_percent'] >= -5:
                        st.success(f"✅ {fund_name} performance is within acceptable range")
                
                # Show recommendations if any
                if ai_advice['recommendations']:
                    for rec in ai_advice['recommendations']:
                        st.info(f"💡 {rec}")
                else:
                    # Show standard advice for acceptable performance
                    if ret_data['return_percent'] >= -5:
                        st.info("💡 Continue monitoring performance and maintain current strategy")
    
    return returns_data

def create_performance_pie_chart(returns_data):
    """Create interactive pie chart for fund performance comparison"""
    if not returns_data:
        return None
    
    fund_names = [item['fund_name'] for item in returns_data]
    returns = [item['return_percent'] for item in returns_data]
    
    # Convert negative returns to positive for pie chart visualization
    # We'll show absolute values but keep the sign information in hover
    abs_returns = [abs(ret) for ret in returns]
    
    # Create custom colors based on performance
    colors = []
    for ret in returns:
        if ret >= 0:
            colors.append('#28a745')  # Green for positive
        elif ret >= -5:
            colors.append('#ffc107')  # Yellow for small negative
        elif ret >= -15:
            colors.append('#fd7e14')  # Orange for medium negative
        else:
            colors.append('#dc3545')  # Red for large negative
    
    # Create custom hover text
    hover_text = [
        f"<b>{name}</b><br>" +
        f"Return: {ret:.2f}%<br>" +
        f"Performance: {'Positive' if ret >= 0 else 'Negative'}<br>" +
        f"Risk Level: {'Low' if ret >= -5 else 'Medium' if ret >= -15 else 'High'}"
        for name, ret in zip(fund_names, returns)
    ]
    
    fig = go.Figure(data=[go.Pie(
        labels=fund_names,
        values=abs_returns,
        hole=0.4,
        hovertemplate="%{text}<extra></extra>",
        text=hover_text,
        textinfo='label+percent',
        textposition='auto',
        marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2))
    )])
    
    fig.update_layout(
        title={
            'text': "🎯 Fund Performance Distribution (by Absolute Return)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        font=dict(size=12),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        ),
        annotations=[
            dict(
                text="Performance<br>Breakdown",
                x=0.5, y=0.5,
                font_size=14,
                showarrow=False
            )
        ]
    )
    
    return fig

def create_fund_nav_pie_chart(returns_data):
    """Create pie chart showing fund allocation by NAV values"""
    if not returns_data:
        return None
    
    fund_names = [item['fund_name'] for item in returns_data]
    nav_end_values = [item['nav_end'] for item in returns_data]
    
    # Create hover text with detailed info
    hover_text = [
        f"<b>{name}</b><br>" +
        f"Current NAV: ₹{nav_end:.2f}<br>" +
        f"Start NAV: ₹{item['nav_start']:.2f}<br>" +
        f"Return: {item['return_percent']:.2f}%<br>" +
        f"Period: {item['duration_days']} days"
        for name, nav_end, item in zip(fund_names, nav_end_values, returns_data)
    ]
    
    # Use a different color scheme for NAV visualization
    colors = px.colors.qualitative.Pastel
    
    fig = go.Figure(data=[go.Pie(
        labels=fund_names,
        values=nav_end_values,
        hole=0.3,
        hovertemplate="%{text}<extra></extra>",
        text=hover_text,
        textinfo='label+value',
        textposition='auto',
        marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2))
    )])
    
    fig.update_layout(
        title={
            'text': "💰 Fund Distribution by Current NAV Value",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        font=dict(size=12),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        ),
        annotations=[
            dict(
                text="NAV<br>Distribution",
                x=0.5, y=0.5,
                font_size=14,
                showarrow=False
            )
        ]
    )
    
    return fig

def create_bar_chart(returns_data):
    """Create and display bar chart"""
    if not returns_data:
        st.warning("No data available for chart. Please load fund data first.")
        return
    
    st.subheader("📈 Performance Visualization")
    
    try:
        # Create tabs for different chart types
        chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs(["📊 Bar Chart", "🎯 Performance Pie", "💰 NAV Pie", "📈 Combined View"])
        
        with chart_tab1:
            fig = st.session_state.calculator.create_return_bar_chart(returns_data)
            st.plotly_chart(fig, use_container_width=True, key="performance_bar_chart")
        
        with chart_tab2:
            st.markdown("**Performance Distribution by Absolute Return Values**")
            st.info("🔍 This pie chart shows the relative magnitude of returns (positive/negative) with color coding")
            perf_pie_fig = create_performance_pie_chart(returns_data)
            if perf_pie_fig:
                st.plotly_chart(perf_pie_fig, use_container_width=True, key="performance_pie_chart")
        
        with chart_tab3:
            st.markdown("**Fund Distribution by Current NAV Values**")
            st.info("💡 This pie chart shows the relative NAV values of your funds")
            nav_pie_fig = create_fund_nav_pie_chart(returns_data)
            if nav_pie_fig:
                st.plotly_chart(nav_pie_fig, use_container_width=True, key="nav_pie_chart")
        
        with chart_tab4:
            st.markdown("**Side-by-Side Comparison**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 🎯 Performance Distribution")
                perf_pie_fig = create_performance_pie_chart(returns_data)
                if perf_pie_fig:
                    # Adjust size for side-by-side display
                    perf_pie_fig.update_layout(height=400)
                    st.plotly_chart(perf_pie_fig, use_container_width=True, key="combined_perf_pie")
            
            with col2:
                st.markdown("##### 💰 NAV Distribution")
                nav_pie_fig = create_fund_nav_pie_chart(returns_data)
                if nav_pie_fig:
                    # Adjust size for side-by-side display
                    nav_pie_fig.update_layout(height=400)
                    st.plotly_chart(nav_pie_fig, use_container_width=True, key="combined_nav_pie")
                    
    except Exception as e:
        st.error(f"Error creating charts: {str(e)}")
        st.info("Please ensure fund data is properly loaded.")

def portfolio_allocation_interface():
    """Interactive portfolio allocation with scroll wheel"""
    if not st.session_state.funds_loaded:
        st.warning("Please load fund data first!")
        return None
    
    st.subheader("💼 Portfolio Allocation (Scroll Wheel Enabled)")
    st.info("💡 Tip: Use your mouse scroll wheel on the input fields to adjust allocations!")
    
    # Auto-normalize option
    st.session_state.auto_normalize = st.checkbox("Auto-normalize to 100%", value=True)
    
    # Allocation inputs with scroll wheel functionality
    allocations = {}
    
    st.markdown('<div class="allocation-container">', unsafe_allow_html=True)
    
    cols = st.columns(len(st.session_state.funds_loaded))
    
    for i, fund_name in enumerate(st.session_state.funds_loaded):
        with cols[i]:
            # Current allocation
            current_value = st.session_state.allocations.get(fund_name, 100/len(st.session_state.funds_loaded))
            
            # Create input with custom HTML for scroll wheel
            st.markdown(f"""
            <label for="allocation_{fund_name}" style="font-weight: bold;">{fund_name}</label>
            <input 
                type="number" 
                id="allocation_{fund_name}" 
                class="scroll-input"
                value="{current_value:.1f}"
                min="0" 
                max="100" 
                step="0.1"
                placeholder="0.0"
            />
            <small style="color: #666;">Use scroll wheel to adjust</small>
            """, unsafe_allow_html=True)
            
            # Regular Streamlit input as backup (hidden)
            allocation = st.number_input(
                f"Allocation %",
                min_value=0.0,
                max_value=100.0,
                value=current_value,
                step=0.1,
                key=f"alloc_{fund_name}",
                label_visibility="collapsed"
            )
            
            allocations[fund_name] = allocation
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Update session state
    st.session_state.allocations = allocations
    
    # Show current total
    total_allocation = sum(allocations.values())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if abs(total_allocation - 100) < 0.01:
            st.success(f"Total Allocation: {total_allocation:.1f}%")
        else:
            st.warning(f"Total Allocation: {total_allocation:.1f}%")
    
    with col2:
        if st.button("🎯 Auto Balance to 100%"):
            if total_allocation > 0:
                normalized = {fund: (alloc/total_allocation)*100 for fund, alloc in allocations.items()}
                st.session_state.allocations = normalized
                st.rerun()
    
    with col3:
        if st.button("⚖️ Equal Distribution"):
            equal_weight = 100 / len(st.session_state.funds_loaded)
            st.session_state.allocations = {fund: equal_weight for fund in st.session_state.funds_loaded}
            st.rerun()
    
    return allocations

def display_portfolio_analysis(allocations):
    """Display portfolio analysis and AI recommendations"""
    if not allocations or sum(allocations.values()) == 0:
        st.warning("Please set portfolio allocations!")
        return
    
    st.subheader("💰 Portfolio Analysis")
    
    # Calculate portfolio return
    portfolio_result = st.session_state.calculator.calculate_weighted_portfolio_return(allocations)
    
    if portfolio_result:
        # Display portfolio return prominently
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Portfolio Return",
                f"{portfolio_result['total_return']:.2f}%",
                delta=f"vs individual avg"
            )
        
        with col2:
            # Calculate risk level
            if portfolio_result['total_return'] < -15:
                risk_color = "🔴"
                risk_level = "HIGH RISK"
            elif portfolio_result['total_return'] < -5:
                risk_color = "🟡"
                risk_level = "MEDIUM RISK"
            else:
                risk_color = "🟢"
                risk_level = "LOW RISK"
            
            st.metric("Risk Level", f"{risk_color} {risk_level}")
        
        with col3:
            total_days = max([st.session_state.calculator.calculate_percentage_return(fund)['duration_days'] 
                            for fund in allocations.keys()])
            annualized_return = ((1 + portfolio_result['total_return']/100) ** (365/total_days) - 1) * 100
            st.metric("Annualized Return", f"{annualized_return:.2f}%")
        
        # Fund contributions breakdown
        st.write("**Fund Contributions:**")
        contrib_data = []
        for fund, contrib in portfolio_result['fund_contributions'].items():
            contrib_data.append({
                'Fund': fund,
                'Allocation': f"{contrib['weight']:.1f}%",
                'Individual Return': f"{contrib['individual_return']:.2f}%",
                'Contribution': f"{contrib['contribution']:.2f}%"
            })
        
        contrib_df = pd.DataFrame(contrib_data)
        st.dataframe(contrib_df, use_container_width=True)
        
        return portfolio_result

def display_ai_recommendations(allocations, returns_data):
    """Display AI weight adjustment recommendations"""
    if not allocations or not returns_data:
        return
    
    st.subheader("🤖 AI Portfolio Recommendations")
    
    ai_adjustments = st.session_state.calculator.ai_weight_adjustment(allocations, returns_data)
    
    if ai_adjustments['adjustments_made']:
        st.warning("🤖 AI has identified potential improvements to your portfolio:")
        
        for adjustment in ai_adjustments['adjustments_made']:
            st.write(f"• {adjustment}")
        
        # Show comparison table
        comparison_data = []
        for fund in allocations.keys():
            orig = ai_adjustments['original_weights'].get(fund, 0)
            adj = ai_adjustments['adjusted_weights'].get(fund, 0)
            change = adj - orig
            
            comparison_data.append({
                'Fund': fund,
                'Current %': f"{orig:.1f}%",
                'AI Recommended %': f"{adj:.1f}%",
                'Change': f"{change:+.1f}%"
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Calculate potential improvement
        new_portfolio = st.session_state.calculator.calculate_weighted_portfolio_return(ai_adjustments['adjusted_weights'])
        current_portfolio = st.session_state.calculator.calculate_weighted_portfolio_return(allocations)
        
        if new_portfolio and current_portfolio:
            improvement = new_portfolio['total_return'] - current_portfolio['total_return']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current Portfolio Return", f"{current_portfolio['total_return']:.2f}%")
            with col2:
                st.metric("AI-Optimized Return", f"{new_portfolio['total_return']:.2f}%", 
                         delta=f"{improvement:+.2f}%")
            
            if st.button("🚀 Apply AI Recommendations"):
                st.session_state.allocations = ai_adjustments['adjusted_weights']
                st.success("AI recommendations applied!")
                st.rerun()
    else:
        st.success("✅ Your current allocation is already optimized according to AI analysis!")

def display_charts(allocations, returns_data):
    """Display pie charts and other visualizations"""
    if not allocations:
        return
    
    st.subheader("📊 Portfolio Visualizations")
    
    try:
        col1, col2 = st.columns(2)
        
        with col1:
            # Current allocation pie chart
            pie_fig = st.session_state.calculator.create_allocation_pie_chart(
                allocations, "Current Portfolio Allocation"
            )
            st.plotly_chart(pie_fig, use_container_width=True, key="current_allocation_pie")
        
        with col2:
            # AI recommended allocation
            if returns_data:
                ai_adjustments = st.session_state.calculator.ai_weight_adjustment(allocations, returns_data)
                ai_pie_fig = st.session_state.calculator.create_allocation_pie_chart(
                    ai_adjustments['adjusted_weights'], "AI-Recommended Allocation"
                )
                st.plotly_chart(ai_pie_fig, use_container_width=True, key="ai_allocation_pie")
            else:
                st.info("Load fund data to see AI recommendations")
                
    except Exception as e:
        st.error(f"Error creating charts: {str(e)}")
        st.info("Please try loading fund data first.")

def calculate_sip_compound_interest(principal, rate, time):
    """
    Calculate compound interest using the formula: A = P(1 + r/100)^t
    
    Args:
        principal (float): Initial investment amount in ₹
        rate (float): Annual interest rate in %
        time (float): Time period in years
    
    Returns:
        tuple: (final_amount, growth_percentage)
    """
    final_amount = principal * (1 + rate/100) ** time
    growth_percentage = ((final_amount - principal) / principal) * 100
    return final_amount, growth_percentage

def sip_ai_recommendation(growth_percentage, current_amount):
    """AI-powered recommendation system for SIP"""
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

def create_sip_portfolio_pie_chart(portfolio_data):
    """Create interactive pie chart for SIP portfolio allocation"""
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
        textposition='auto',
        marker=dict(colors=px.colors.qualitative.Set3)
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

def main():
    """Main Streamlit application"""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Portfolio Advisor</h1>
        <p>Advanced Portfolio Analysis with Intelligent Recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # Fund management
        if st.button("🔄 Reset All Data"):
            st.session_state.calculator = PortfolioReturnCalculator()
            st.session_state.funds_loaded = []
            st.session_state.allocations = {}
            st.rerun()
        
        st.write("**Quick Actions:**")
        if st.button("📊 Sample Portfolio"):
            # Quick load with sample data
            sample_allocations = {"Nippon Small Cap": 40, "HDFC Small Cap": 30, "Axis Multi Asset": 30}
            st.session_state.allocations = sample_allocations
        
        if st.session_state.funds_loaded:
            st.write("**Export Options:**")
            if st.button("📄 Generate Report"):
                st.info("Report generation feature coming soon!")
            
            if st.button("💾 Save Portfolio"):
                st.info("Save/Load feature coming soon!")
    
    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📂 Data Loading", "📊 Performance Analysis", "💼 Portfolio Allocation", "🤖 AI Insights", "📈 SIP Calculator"])
    
    with tab1:
        load_fund_data()
    
    with tab2:
        returns_data = display_individual_returns()
        if returns_data:
            create_bar_chart(returns_data)
        else:
            st.info("📊 Load fund data from the 'Data Loading' tab to see performance analysis.")
    
    with tab3:
        allocations = portfolio_allocation_interface()
        if allocations and st.session_state.funds_loaded:
            portfolio_result = display_portfolio_analysis(allocations)
            # Get returns data for charts
            returns_data = []
            for fund_name in st.session_state.funds_loaded:
                ret_data = st.session_state.calculator.calculate_percentage_return(fund_name)
                if ret_data:
                    returns_data.append(ret_data)
            if returns_data:
                display_charts(allocations, returns_data)
        else:
            st.info("💼 Load fund data and set allocations to see portfolio analysis.")
    
    with tab4:
        if st.session_state.funds_loaded:
            # Get current data
            allocations = st.session_state.allocations
            returns_data = []
            for fund_name in st.session_state.funds_loaded:
                ret_data = st.session_state.calculator.calculate_percentage_return(fund_name)
                if ret_data:
                    returns_data.append(ret_data)
            
            if allocations and returns_data:
                display_ai_recommendations(allocations, returns_data)
            else:
                st.info("🤖 Complete portfolio allocation to see AI insights.")
        else:
            st.info("🤖 Load fund data first to get AI recommendations.")
    
    with tab5:
        st.header("📈 SIP Calculator with Portfolio Analysis")
        st.markdown("**Calculate investment growth with AI recommendations and portfolio allocation**")
        
        # Sidebar for SIP mode selection
        sip_mode = st.selectbox(
            "🔢 Choose Calculator Mode:",
            ["💰 Simple SIP Calculator", "💼 Portfolio SIP Analysis"]
        )
        
        if sip_mode == "💰 Simple SIP Calculator":
            st.subheader("💰 Simple SIP Calculator")
            
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
                    final_amount, growth_percentage = calculate_sip_compound_interest(principal, rate, time)
                    
                    # Display results with the requested positive message
                    st.success(f"🎉 👉 **Your money grows to ₹{final_amount:,.2f}!** 👈")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("💰 Final Amount", f"₹{final_amount:,.2f}", f"₹{final_amount - principal:,.2f}")
                    with col_b:
                        st.metric("📈 Total Growth", f"{growth_percentage:.2f}%")
                    with col_c:
                        st.metric("💵 Profit", f"₹{final_amount - principal:,.2f}")
                    
                    # AI Recommendation (with the requested feature: if growth > 10%, suggest increasing SIP)
                    ai_rec = sip_ai_recommendation(growth_percentage, principal)
                    if ai_rec['color'] == 'success':
                        st.success(f"🤖 **AI Recommendation:**\n{ai_rec['message']}")
                    elif ai_rec['color'] == 'info':
                        st.info(f"🤖 **AI Recommendation:**\n{ai_rec['message']}")
                    else:
                        st.warning(f"🤖 **AI Recommendation:**\n{ai_rec['message']}")
        
        elif sip_mode == "💼 Portfolio SIP Analysis":
            st.subheader("💼 Portfolio SIP Analysis with Allocation")
            st.markdown("**Input allocation percentages, calculate weighted returns, and view pie charts**")
            
            # Portfolio setup
            st.subheader("📊 Portfolio Setup")
            
            num_investments = st.number_input(
                "How many SIP investments in your portfolio?",
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
                st.subheader(f"💰 SIP Investment {i+1}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    name = st.text_input(
                        f"Investment Name",
                        value=f"SIP Fund {i+1}",
                        key=f"sip_name_{i}"
                    )
                
                with col2:
                    principal = st.number_input(
                        f"Principal (₹)",
                        min_value=1.0,
                        value=50000.0,
                        step=1000.0,
                        key=f"sip_principal_{i}"
                    )
                
                with col3:
                    rate = st.number_input(
                        f"Return (%)",
                        min_value=0.1,
                        max_value=50.0,
                        value=12.0,
                        step=0.1,
                        key=f"sip_rate_{i}"
                    )
                
                with col4:
                    allocation = st.number_input(
                        f"Allocation (%)",
                        min_value=0.1,
                        max_value=100.0,
                        value=100.0/num_investments,
                        step=0.1,
                        key=f"sip_allocation_{i}",
                        help="Portfolio allocation percentage"
                    )
                
                time = st.number_input(
                    f"Time Period (years)",
                    min_value=0.1,
                    max_value=50.0,
                    value=10.0,
                    step=0.1,
                    key=f"sip_time_{i}"
                )
                
                # Calculate individual investment
                final_amount, growth_percentage = calculate_sip_compound_interest(principal, rate, time)
                
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
                if st.button("🔄 Normalize Allocations to 100%", key="normalize_sip"):
                    for item in portfolio_data:
                        item['allocation'] = (item['allocation'] / total_allocation) * 100
                    st.success("✅ Allocations normalized!")
            
            # Calculate portfolio results
            if st.button("📊 Analyze SIP Portfolio", type="primary"):
                # Calculate weighted returns
                total_weighted_return = sum(item['growth_percentage'] * item['allocation'] / 100 for item in portfolio_data)
                total_weighted_amount = sum(item['final_amount'] * item['allocation'] / 100 for item in portfolio_data)
                total_principal = sum(item['principal'] for item in portfolio_data)
                total_profit = total_weighted_amount - total_principal
                
                # Display portfolio summary with the requested positive message
                st.success(f"🎉 👉 **Your SIP portfolio grows to ₹{total_weighted_amount:,.2f}!** 👈")
                
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
                    # Pie chart for allocation percentages
                    pie_fig = create_sip_portfolio_pie_chart(portfolio_data)
                    st.plotly_chart(pie_fig, use_container_width=True)
                
                with col_chart2:
                    # Bar chart for returns comparison
                    df = pd.DataFrame(portfolio_data)
                    
                    # Color code based on performance
                    colors = []
                    for growth in df['growth_percentage']:
                        if growth > 15:
                            colors.append('#28a745')  # Green for excellent
                        elif growth > 10:
                            colors.append('#17a2b8')  # Blue for good
                        else:
                            colors.append('#ffc107')  # Yellow for needs improvement
                    
                    bar_fig = go.Figure(data=[
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
                    
                    bar_fig.update_layout(
                        title={
                            'text': "📈 SIP Returns Comparison",
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {'size': 20}
                        },
                        xaxis_title="SIP Investments",
                        yaxis_title="Return (%)",
                        font=dict(size=12),
                        yaxis=dict(tickformat='.1f')
                    )
                    
                    st.plotly_chart(bar_fig, use_container_width=True)
                
                # Detailed results table
                st.subheader("🔍 Detailed SIP Analysis")
                
                df_results = pd.DataFrame(portfolio_data)
                df_results['Final Amount (₹)'] = df_results['final_amount'].apply(lambda x: f"₹{x:,.2f}")
                df_results['Principal (₹)'] = df_results['principal'].apply(lambda x: f"₹{x:,.2f}")
                df_results['Profit (₹)'] = df_results['profit'].apply(lambda x: f"₹{x:,.2f}")
                df_results['Return (%)'] = df_results['growth_percentage'].apply(lambda x: f"{x:.2f}%")
                df_results['Allocation (%)'] = df_results['allocation'].apply(lambda x: f"{x:.1f}%")
                
                display_df = df_results[['name', 'Principal (₹)', 'Final Amount (₹)', 'Return (%)', 'Allocation (%)', 'Profit (₹)']]
                display_df.columns = ['SIP Investment', 'Principal', 'Final Amount', 'Return', 'Allocation', 'Profit']
                
                st.dataframe(display_df, use_container_width=True)
                
                # AI Portfolio Recommendations
                st.subheader("🤖 AI SIP Portfolio Analysis")
                
                best_performer = max(portfolio_data, key=lambda x: x['growth_percentage'])
                worst_performer = min(portfolio_data, key=lambda x: x['growth_percentage'])
                
                if total_weighted_return > 15:
                    st.success(f"""
🚀 **EXCELLENT** SIP portfolio performance with {total_weighted_return:.2f}% weighted return!
💡 Your diversification strategy is working exceptionally well.
🎯 Consider increasing allocation to **{best_performer['name']}** (top performer with {best_performer['growth_percentage']:.1f}% return)
                    """)
                elif total_weighted_return > 10:
                    st.info(f"""
✅ **GOOD** SIP portfolio performance with {total_weighted_return:.2f}% weighted return!
📈 Your portfolio is beating inflation and growing steadily.
💡 Consider rebalancing towards better performers.
💰 **AI Suggestion**: Since your growth is above 10%, consider increasing your SIP amounts!
                    """)
                elif total_weighted_return > 5:
                    st.warning(f"""
⚖️ **MODERATE** SIP portfolio performance with {total_weighted_return:.2f}% weighted return.
🔍 Review underperforming investments.
⚠️ Consider reducing allocation to **{worst_performer['name']}** (lowest performer with {worst_performer['growth_percentage']:.1f}% return)
                    """)
                else:
                    st.error(f"""
⚠️ SIP Portfolio needs **IMPROVEMENT** with {total_weighted_return:.2f}% weighted return!
🔄 Consider diversifying into higher-return SIP funds.
💭 Review your investment strategy with a financial advisor.
                    """)
                
                # Diversification analysis
                allocations = [item['allocation'] for item in portfolio_data]
                if max(allocations) > 60:
                    st.warning("⚠️ **CONCENTRATION RISK**: One SIP dominates your portfolio. Consider better diversification.")
                elif len(portfolio_data) >= 4 and max(allocations) < 40:
                    st.success("✅ **GOOD DIVERSIFICATION**: Well-balanced SIP portfolio allocation.")

if __name__ == "__main__":
    main() 