#!/usr/bin/env python3
"""
Enhanced Streamlit Fund Comparison App
====================================

Interactive web application for comparing multiple mutual funds
with scroll wheel functionality and comprehensive analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, date
import base64
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Fund Comparison Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .positive {
        color: #00C851;
        font-weight: bold;
    }
    .negative {
        color: #FF4444;
        font-weight: bold;
    }
    .neutral {
        color: #33b5e5;
        font-weight: bold;
    }
    .fund-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .comparison-table {
        font-size: 0.9rem;
    }
    .stSelectbox > div > div > div {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitFundComparator:
    """Enhanced Streamlit fund comparison class"""
    
    def __init__(self):
        if 'funds_data' not in st.session_state:
            st.session_state.funds_data = {}
        if 'fund_metrics' not in st.session_state:
            st.session_state.fund_metrics = {}
    
    def load_csv_data(self, uploaded_file, fund_name):
        """Load fund data from uploaded CSV"""
        try:
            df = pd.read_csv(uploaded_file)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            
            # Calculate metrics
            df['Daily_Return'] = df['NAV'].pct_change() * 100
            df['Cumulative_Return'] = ((df['NAV'] / df['NAV'].iloc[0]) - 1) * 100
            df['MA_7'] = df['NAV'].rolling(window=7).mean()
            df['MA_21'] = df['NAV'].rolling(window=21).mean()
            df['Rolling_Vol_7'] = df['Daily_Return'].rolling(window=7).std()
            
            return df
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None
    
    def calculate_metrics(self, df, fund_name):
        """Calculate comprehensive fund metrics"""
        daily_returns = df['Daily_Return'].dropna()
        
        # Basic metrics
        start_nav = df['NAV'].iloc[0]
        end_nav = df['NAV'].iloc[-1]
        total_return = ((end_nav / start_nav) - 1) * 100
        
        # Risk metrics
        avg_daily_return = daily_returns.mean()
        volatility = daily_returns.std()
        annualized_return = avg_daily_return * 252
        annualized_volatility = volatility * np.sqrt(252)
        
        # Drawdown
        running_max = df['NAV'].expanding().max()
        drawdown = (df['NAV'] / running_max - 1) * 100
        max_drawdown = drawdown.min()
        
        # Additional metrics
        sharpe_ratio = (annualized_return - 6) / annualized_volatility if annualized_volatility > 0 else 0
        positive_days = len(daily_returns[daily_returns > 0])
        win_rate = positive_days / len(daily_returns) * 100 if len(daily_returns) > 0 else 0
        
        return {
            'fund_name': fund_name,
            'start_nav': start_nav,
            'end_nav': end_nav,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'annualized_volatility': annualized_volatility,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'best_day': daily_returns.max(),
            'worst_day': daily_returns.min(),
            'trading_days': len(daily_returns)
        }
    
    def create_comparison_charts(self, selected_funds):
        """Create interactive comparison charts with scroll wheel"""
        if len(selected_funds) < 2:
            st.warning("Please select at least 2 funds for comparison")
            return
        
        # Create main comparison dashboard
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('📈 Normalized NAV Comparison', '📊 Cumulative Returns',
                           '📉 Daily Returns Distribution', '⚡ Rolling Volatility',
                           '🔴 Drawdown Analysis', '📅 Monthly Performance'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]],
            vertical_spacing=0.08
        )
        
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#593E2A', '#0B5345']
        
        for i, fund_name in enumerate(selected_funds):
            df = st.session_state.funds_data[fund_name]
            color = colors[i % len(colors)]
            
            # 1. Normalized NAV
            normalized_nav = (df['NAV'] / df['NAV'].iloc[0]) * 100
            fig.add_trace(go.Scatter(
                x=df['Date'], y=normalized_nav,
                name=f'{fund_name}',
                line=dict(color=color, width=2),
                hovertemplate=f'<b>{fund_name}</b><br>Date: %{{x}}<br>Normalized: %{{y:.2f}}<extra></extra>'
            ), row=1, col=1)
            
            # 2. Cumulative Returns
            fig.add_trace(go.Scatter(
                x=df['Date'], y=df['Cumulative_Return'],
                name=f'{fund_name} Return',
                line=dict(color=color, width=2),
                showlegend=False,
                hovertemplate=f'<b>{fund_name}</b><br>Date: %{{x}}<br>Return: %{{y:.2f}}%<extra></extra>'
            ), row=1, col=2)
            
            # 3. Daily Returns Distribution
            fig.add_trace(go.Histogram(
                x=df['Daily_Return'].dropna(),
                name=f'{fund_name}',
                opacity=0.7,
                marker_color=color,
                showlegend=False,
                nbinsx=25
            ), row=2, col=1)
            
            # 4. Rolling Volatility
            fig.add_trace(go.Scatter(
                x=df['Date'], y=df['Rolling_Vol_7'],
                name=f'{fund_name} Vol',
                line=dict(color=color, width=1),
                showlegend=False,
                hovertemplate=f'<b>{fund_name}</b><br>Date: %{{x}}<br>Volatility: %{{y:.2f}}%<extra></extra>'
            ), row=2, col=2)
            
            # 5. Drawdown
            running_max = df['NAV'].expanding().max()
            drawdown = (df['NAV'] / running_max - 1) * 100
            fig.add_trace(go.Scatter(
                x=df['Date'], y=drawdown,
                name=f'{fund_name} DD',
                fill='tonexty' if i == 0 else None,
                line=dict(color=color, width=1),
                showlegend=False,
                hovertemplate=f'<b>{fund_name}</b><br>Date: %{{x}}<br>Drawdown: %{{y:.2f}}%<extra></extra>'
            ), row=3, col=1)
            
            # 6. Monthly Returns
            df_monthly = df.copy()
            df_monthly['Month'] = df_monthly['Date'].dt.to_period('M')
            monthly_returns = df_monthly.groupby('Month').agg({
                'NAV': ['first', 'last']
            }).round(4)
            monthly_returns.columns = ['Start', 'End']
            monthly_returns['Return'] = ((monthly_returns['End'] / monthly_returns['Start']) - 1) * 100
            
            fig.add_trace(go.Bar(
                x=[str(month) for month in monthly_returns.index],
                y=monthly_returns['Return'],
                name=f'{fund_name}',
                marker_color=color,
                opacity=0.8,
                showlegend=False,
                hovertemplate=f'<b>{fund_name}</b><br>Month: %{{x}}<br>Return: %{{y:.2f}}%<extra></extra>'
            ), row=3, col=2)
        
        # Update layout with scroll wheel functionality
        fig.update_layout(
            height=1000,
            title_text="📊 Comprehensive Fund Comparison Dashboard",
            title_x=0.5,
            title_font_size=18,
            showlegend=True,
            template='plotly_white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Update axes
        fig.update_yaxes(title_text="Normalized NAV", row=1, col=1)
        fig.update_yaxes(title_text="Cumulative Return (%)", row=1, col=2)
        fig.update_yaxes(title_text="Frequency", row=2, col=1)
        fig.update_yaxes(title_text="Volatility (%)", row=2, col=2)
        fig.update_yaxes(title_text="Drawdown (%)", row=3, col=1)
        fig.update_yaxes(title_text="Monthly Return (%)", row=3, col=2)
        
        # Configure for scroll wheel and interactivity
        config = {
            'scrollZoom': True,  # Enable scroll wheel zooming
            'displayModeBar': True,
            'displaylogo': False,
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'fund_comparison_dashboard',
                'height': 1000,
                'width': 1400,
                'scale': 2
            }
        }
        
        st.plotly_chart(fig, use_container_width=True, config=config)
        
        return fig
    
    def create_risk_return_chart(self, selected_funds):
        """Create risk-return scatter plot"""
        if len(selected_funds) < 2:
            return
        
        metrics_list = []
        for fund_name in selected_funds:
            if fund_name in st.session_state.fund_metrics:
                metrics_list.append(st.session_state.fund_metrics[fund_name])
        
        if not metrics_list:
            return
        
        fig = go.Figure()
        
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#593E2A', '#0B5345']
        
        for i, metrics in enumerate(metrics_list):
            fig.add_trace(go.Scatter(
                x=[metrics['annualized_volatility']],
                y=[metrics['annualized_return']],
                mode='markers+text',
                text=[metrics['fund_name']],
                textposition='top center',
                marker=dict(
                    size=15,
                    color=colors[i % len(colors)],
                    line=dict(width=2, color='white')
                ),
                name=metrics['fund_name'],
                hovertemplate=f'<b>{metrics["fund_name"]}</b><br>' +
                             f'Volatility: {metrics["annualized_volatility"]:.2f}%<br>' +
                             f'Return: {metrics["annualized_return"]:.2f}%<br>' +
                             f'Sharpe Ratio: {metrics["sharpe_ratio"]:.2f}<extra></extra>'
            ))
        
        # Add quadrant lines
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=20, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title="🎯 Risk-Return Analysis",
            xaxis_title="Annualized Volatility (%)",
            yaxis_title="Annualized Return (%)",
            template='plotly_white',
            height=500,
            showlegend=False
        )
        
        config = {'scrollZoom': True, 'displayModeBar': True, 'displaylogo': False}
        st.plotly_chart(fig, use_container_width=True, config=config)

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown("""
    <div class="fund-header">
        <h1>📊 Fund Comparison Analyzer</h1>
        <p>Compare multiple mutual funds with interactive charts and scroll wheel functionality</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize comparator
    comparator = StreamlitFundComparator()
    
    # Sidebar
    st.sidebar.title("🔧 Configuration")
    
    # File upload section
    st.sidebar.subheader("📁 Upload Fund Data")
    
    uploaded_files = st.sidebar.file_uploader(
        "Upload CSV files (Date, NAV columns)",
        type=['csv'],
        accept_multiple_files=True,
        help="Upload CSV files with Date and NAV columns for each fund"
    )
    
    # Process uploaded files
    if uploaded_files:
        for uploaded_file in uploaded_files:
            fund_name = uploaded_file.name.replace('.csv', '').replace('_', ' ').title()
            
            if fund_name not in st.session_state.funds_data:
                with st.spinner(f"Loading {fund_name}..."):
                    df = comparator.load_csv_data(uploaded_file, fund_name)
                    if df is not None:
                        st.session_state.funds_data[fund_name] = df
                        metrics = comparator.calculate_metrics(df, fund_name)
                        st.session_state.fund_metrics[fund_name] = metrics
                        st.sidebar.success(f"✅ Loaded {fund_name}")
    
    # Default data loading
    if not st.session_state.funds_data:
        st.sidebar.info("💡 No data loaded. Upload CSV files or use sample data below:")
        
        if st.sidebar.button("📊 Load Sample Data (Nippon & HDFC)"):
            with st.spinner("Loading sample data..."):
                try:
                    # Load Nippon data
                    nippon_df = pd.read_csv('real_nav_data.csv')
                    nippon_df['Date'] = pd.to_datetime(nippon_df['Date'])
                    nippon_df = nippon_df.sort_values('Date')
                    nippon_df['Daily_Return'] = nippon_df['NAV'].pct_change() * 100
                    nippon_df['Cumulative_Return'] = ((nippon_df['NAV'] / nippon_df['NAV'].iloc[0]) - 1) * 100
                    nippon_df['MA_7'] = nippon_df['NAV'].rolling(window=7).mean()
                    nippon_df['MA_21'] = nippon_df['NAV'].rolling(window=21).mean()
                    nippon_df['Rolling_Vol_7'] = nippon_df['Daily_Return'].rolling(window=7).std()
                    
                    st.session_state.funds_data['Nippon India Small Cap'] = nippon_df
                    st.session_state.fund_metrics['Nippon India Small Cap'] = comparator.calculate_metrics(nippon_df, 'Nippon India Small Cap')
                    
                    # Load HDFC data
                    hdfc_df = pd.read_csv('hdfc_nav_data.csv')
                    hdfc_df['Date'] = pd.to_datetime(hdfc_df['Date'])
                    hdfc_df = hdfc_df.sort_values('Date')
                    hdfc_df['Daily_Return'] = hdfc_df['NAV'].pct_change() * 100
                    hdfc_df['Cumulative_Return'] = ((hdfc_df['NAV'] / hdfc_df['NAV'].iloc[0]) - 1) * 100
                    hdfc_df['MA_7'] = hdfc_df['NAV'].rolling(window=7).mean()
                    hdfc_df['MA_21'] = hdfc_df['NAV'].rolling(window=21).mean()
                    hdfc_df['Rolling_Vol_7'] = hdfc_df['Daily_Return'].rolling(window=7).std()
                    
                    st.session_state.funds_data['HDFC Small Cap Fund'] = hdfc_df
                    st.session_state.fund_metrics['HDFC Small Cap Fund'] = comparator.calculate_metrics(hdfc_df, 'HDFC Small Cap Fund')
                    
                    st.sidebar.success("✅ Sample data loaded!")
                    st.rerun()
                    
                except FileNotFoundError:
                    st.sidebar.error("❌ Sample data files not found")
    
    # Fund selection
    if st.session_state.funds_data:
        st.sidebar.subheader("🎯 Select Funds to Compare")
        available_funds = list(st.session_state.funds_data.keys())
        selected_funds = st.sidebar.multiselect(
            "Choose funds for comparison:",
            available_funds,
            default=available_funds if len(available_funds) <= 3 else available_funds[:2]
        )
        
        # Analysis options
        st.sidebar.subheader("📊 Analysis Options")
        show_correlation = st.sidebar.checkbox("Show Correlation Analysis", value=True)
        show_risk_return = st.sidebar.checkbox("Show Risk-Return Plot", value=True)
        show_monthly = st.sidebar.checkbox("Show Monthly Breakdown", value=True)
        
        # Main content
        if selected_funds:
            # Overview metrics
            st.subheader("📈 Fund Overview")
            
            cols = st.columns(len(selected_funds))
            for i, fund_name in enumerate(selected_funds):
                metrics = st.session_state.fund_metrics[fund_name]
                with cols[i]:
                    return_class = "positive" if metrics['total_return'] > 0 else "negative"
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{fund_name}</h4>
                        <p>Total Return: <span class="{return_class}">{metrics['total_return']:+.2f}%</span></p>
                        <p>Volatility: <span class="neutral">{metrics['annualized_volatility']:.2f}%</span></p>
                        <p>Max Drawdown: <span class="negative">{metrics['max_drawdown']:.2f}%</span></p>
                        <p>Sharpe Ratio: <span class="neutral">{metrics['sharpe_ratio']:.2f}</span></p>
                        <p>Win Rate: <span class="neutral">{metrics['win_rate']:.1f}%</span></p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Comparison table
            st.subheader("📊 Detailed Comparison")
            comparison_data = []
            for fund_name in selected_funds:
                metrics = st.session_state.fund_metrics[fund_name]
                comparison_data.append({
                    'Fund': fund_name,
                    'Total Return (%)': f"{metrics['total_return']:+.2f}",
                    'Annualized Return (%)': f"{metrics['annualized_return']:+.2f}",
                    'Volatility (%)': f"{metrics['annualized_volatility']:.2f}",
                    'Max Drawdown (%)': f"{metrics['max_drawdown']:.2f}",
                    'Sharpe Ratio': f"{metrics['sharpe_ratio']:.2f}",
                    'Best Day (%)': f"{metrics['best_day']:+.2f}",
                    'Worst Day (%)': f"{metrics['worst_day']:+.2f}",
                    'Win Rate (%)': f"{metrics['win_rate']:.1f}"
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)
            
            # Interactive charts with scroll wheel
            st.subheader("📊 Interactive Analysis (Scroll Wheel Enabled)")
            st.info("💡 Use your mouse scroll wheel to zoom in/out on any chart. Click and drag to pan.")
            
            # Main comparison dashboard
            comparator.create_comparison_charts(selected_funds)
            
            # Risk-return analysis
            if show_risk_return and len(selected_funds) >= 2:
                st.subheader("🎯 Risk-Return Analysis")
                comparator.create_risk_return_chart(selected_funds)
            
            # Correlation analysis
            if show_correlation and len(selected_funds) == 2:
                st.subheader("🔗 Correlation Analysis")
                fund1, fund2 = selected_funds[0], selected_funds[1]
                df1 = st.session_state.funds_data[fund1]
                df2 = st.session_state.funds_data[fund2]
                
                # Merge on date for correlation
                merged = pd.merge(
                    df1[['Date', 'Daily_Return']].rename(columns={'Daily_Return': f'{fund1}_Return'}),
                    df2[['Date', 'Daily_Return']].rename(columns={'Daily_Return': f'{fund2}_Return'}),
                    on='Date'
                )
                
                if len(merged) > 0:
                    correlation = merged[f'{fund1}_Return'].corr(merged[f'{fund2}_Return'])
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.metric("Correlation Coefficient", f"{correlation:.3f}")
                        
                        if correlation > 0.8:
                            st.info("🔗 High positive correlation - funds move together")
                        elif correlation > 0.5:
                            st.info("🔗 Moderate positive correlation")
                        elif correlation > -0.5:
                            st.warning("🔗 Low correlation - some diversification benefit")
                        else:
                            st.success("🔗 Negative correlation - good diversification")
                    
                    with col2:
                        # Correlation scatter plot
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=merged[f'{fund1}_Return'],
                            y=merged[f'{fund2}_Return'],
                            mode='markers',
                            marker=dict(color='blue', size=6, opacity=0.6),
                            name='Daily Returns',
                            hovertemplate=f'{fund1}: %{{x:.2f}}%<br>{fund2}: %{{y:.2f}}%<extra></extra>'
                        ))
                        
                        fig.update_layout(
                            title=f"Daily Returns Correlation",
                            xaxis_title=f"{fund1} Daily Return (%)",
                            yaxis_title=f"{fund2} Daily Return (%)",
                            template='plotly_white',
                            height=400
                        )
                        
                        config = {'scrollZoom': True, 'displayModeBar': True, 'displaylogo': False}
                        st.plotly_chart(fig, use_container_width=True, config=config)
            
            # Monthly breakdown
            if show_monthly:
                st.subheader("📅 Monthly Performance Breakdown")
                
                for fund_name in selected_funds:
                    df = st.session_state.funds_data[fund_name]
                    df_monthly = df.copy()
                    df_monthly['Month'] = df_monthly['Date'].dt.to_period('M')
                    monthly_returns = df_monthly.groupby('Month').agg({
                        'NAV': ['first', 'last']
                    }).round(4)
                    monthly_returns.columns = ['Start_NAV', 'End_NAV']
                    monthly_returns['Monthly_Return'] = ((monthly_returns['End_NAV'] / monthly_returns['Start_NAV']) - 1) * 100
                    
                    st.write(f"**{fund_name}**")
                    monthly_display = monthly_returns.copy()
                    monthly_display.index = monthly_display.index.astype(str)
                    monthly_display['Monthly_Return'] = monthly_display['Monthly_Return'].apply(lambda x: f"{x:+.2f}%")
                    monthly_display['Start_NAV'] = monthly_display['Start_NAV'].apply(lambda x: f"₹{x:.2f}")
                    monthly_display['End_NAV'] = monthly_display['End_NAV'].apply(lambda x: f"₹{x:.2f}")
                    st.dataframe(monthly_display, use_container_width=True)
            
            # Export functionality
            st.subheader("💾 Export Data")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Download Comparison CSV"):
                    csv = comparison_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"fund_comparison_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("📈 Generate Report"):
                    report = f"""
FUND COMPARISON REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}

FUNDS ANALYZED:
{', '.join(selected_funds)}

PERFORMANCE SUMMARY:
"""
                    for fund_name in selected_funds:
                        metrics = st.session_state.fund_metrics[fund_name]
                        report += f"""
{fund_name}:
- Total Return: {metrics['total_return']:+.2f}%
- Volatility: {metrics['annualized_volatility']:.2f}%
- Max Drawdown: {metrics['max_drawdown']:.2f}%
- Sharpe Ratio: {metrics['sharpe_ratio']:.2f}
"""
                    
                    st.download_button(
                        label="Download Report",
                        data=report,
                        file_name=f"fund_report_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
            
            with col3:
                st.info("📊 Charts are interactive with scroll wheel zoom enabled!")
        
        else:
            st.info("👆 Please select funds from the sidebar to start comparison")
    
    else:
        st.info("📁 Please upload fund data files using the sidebar or load sample data")
        
        # Sample data format
        st.subheader("📋 CSV Format Required")
        st.code("""
Date,NAV
2025-01-01,35.6219
2025-01-02,35.8182
2025-01-03,35.7485
...
        """)
        
        st.markdown("**Required columns:** `Date` and `NAV`")

if __name__ == "__main__":
    main() 