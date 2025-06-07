import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
from io import StringIO

# Import our API integrator
try:
    from financial_api_integration import FinancialAPIIntegrator
    HAS_API_INTEGRATION = True
except ImportError:
    HAS_API_INTEGRATION = False

# Page configuration
st.set_page_config(
    page_title="🚀 Financial Analytics Hub",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ff6b6b;
    }
    .success-metric {
        border-left-color: #51cf66;
    }
    .warning-metric {
        border-left-color: #ffd43b;
    }
    .error-metric {
        border-left-color: #ff6b6b;
    }
    .api-section {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #2196f3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🚀 Financial Analytics Hub")
st.markdown("""
**Real-time market data • Advanced analytics • Professional insights**

**Powered by CoinGecko, Frankfurter & Yahoo Finance APIs**

Choose your data source from the sidebar and explore comprehensive financial analysis through interactive charts and metrics.
""")

# Sidebar for data source selection
st.sidebar.header("🔧 Configuration")

# Update data source options to include APIs
data_source_options = ["Sample NAV Data", "Proxy Indices (yfinance)", "Upload CSV", "Manual Entry"]
if HAS_API_INTEGRATION:
    data_source_options.insert(-1, "Live Market APIs")

data_source = st.sidebar.selectbox(
    "Select Data Source:",
    data_source_options
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'api_integrator' not in st.session_state and HAS_API_INTEGRATION:
    st.session_state.api_integrator = FinancialAPIIntegrator()

# Helper functions
@st.cache_data
def generate_sample_nav_data(start_date, periods):
    """Generate realistic sample NAV data"""
    base_nav = 165.50
    dates = pd.date_range(start=start_date, periods=periods, freq='D')
    
    np.random.seed(42)
    daily_changes = np.random.normal(0.001, 0.028, len(dates))
    
    nav_values = [base_nav]
    for change in daily_changes[1:]:
        new_nav = nav_values[-1] * (1 + change)
        nav_values.append(new_nav)
    
    return pd.DataFrame({
        'Date': dates,
        'NAV': nav_values,
        'Change': [0] + [nav_values[i] - nav_values[i-1] for i in range(1, len(nav_values))],
        'Change_Pct': [0] + [(nav_values[i] / nav_values[i-1] - 1) * 100 for i in range(1, len(nav_values))]
    })

@st.cache_data
def fetch_proxy_index_data(symbol, period):
    """Fetch proxy index data using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return None
        
        hist = hist.reset_index()
        hist['Daily_Return'] = hist['Close'].pct_change() * 100
        hist['Symbol'] = symbol
        
        return hist
    except Exception as e:
        st.error(f"Error fetching {symbol}: {str(e)}")
        return None

def calculate_metrics(data, value_col='NAV'):
    """Calculate performance metrics"""
    if data is None or data.empty:
        return None
    
    current_value = data[value_col].iloc[-1]
    start_value = data[value_col].iloc[0]
    total_return = ((current_value / start_value) - 1) * 100
    
    # Calculate daily returns
    if 'Change_Pct' in data.columns:
        returns = data['Change_Pct'].dropna()
    else:
        returns = data[value_col].pct_change().dropna() * 100
    
    volatility = returns.std()
    
    # Max drawdown
    rolling_max = data[value_col].expanding().max()
    drawdown = (data[value_col] / rolling_max - 1) * 100
    max_drawdown = drawdown.min()
    
    # Sharpe ratio (assuming 6% risk-free rate)
    excess_returns = returns.mean() * 252 - 6  # Annualized
    sharpe_ratio = excess_returns / (volatility * np.sqrt(252)) if volatility > 0 else 0
    
    return {
        'current_value': current_value,
        'total_return': total_return,
        'volatility': volatility,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe_ratio,
        'avg_daily_return': returns.mean(),
        'best_day': returns.max(),
        'worst_day': returns.min()
    }

def create_performance_chart(data, value_col='NAV', title="Performance Chart"):
    """Create interactive performance chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['Date'] if 'Date' in data.columns else data.index,
        y=data[value_col],
        mode='lines',
        name=value_col,
        line=dict(color='#2E86AB', width=2),
        hovertemplate='Date: %{x}<br>Value: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Value',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig

def create_returns_distribution(data, value_col='NAV'):
    """Create returns distribution chart"""
    if 'Change_Pct' in data.columns:
        returns = data['Change_Pct'].dropna()
    else:
        returns = data[value_col].pct_change().dropna() * 100
    
    fig = px.histogram(
        x=returns,
        nbins=30,
        title="Daily Returns Distribution",
        labels={'x': 'Daily Return (%)', 'y': 'Frequency'},
        template='plotly_white'
    )
    
    fig.add_vline(x=returns.mean(), line_dash="dash", line_color="red", 
                  annotation_text=f"Mean: {returns.mean():.2f}%")
    
    return fig

def create_drawdown_chart(data, value_col='NAV'):
    """Create drawdown chart"""
    rolling_max = data[value_col].expanding().max()
    drawdown = (data[value_col] / rolling_max - 1) * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['Date'] if 'Date' in data.columns else data.index,
        y=drawdown,
        fill='tonexty',
        mode='lines',
        name='Drawdown',
        line=dict(color='#C73E1D'),
        fillcolor='rgba(199, 62, 29, 0.3)'
    ))
    
    fig.update_layout(
        title="Drawdown Analysis",
        xaxis_title='Date',
        yaxis_title='Drawdown (%)',
        template='plotly_white',
        height=300
    )
    
    return fig

# Main content based on data source selection
if data_source == "Sample NAV Data":
    st.header("🟩 Sample NAV Data")
    st.info("This option generates realistic sample NAV data for demonstration purposes.")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime(2024, 7, 1))
    with col2:
        periods = st.slider("Number of Days", min_value=30, max_value=365, value=180)
    
    if st.button("Generate Sample Data", type="primary"):
        with st.spinner("Generating sample data..."):
            st.session_state.data = generate_sample_nav_data(start_date, periods)
            st.session_state.analysis_results = calculate_metrics(st.session_state.data)
        st.success(f"Generated {len(st.session_state.data)} days of sample NAV data!")

elif data_source == "Proxy Indices (yfinance)":
    st.header("🟦 Proxy Indices Data")
    st.info("Fetch real market data from Indian small-cap indices as proxy for fund performance.")
    
    col1, col2 = st.columns(2)
    with col1:
        index_choice = st.selectbox(
            "Select Index:",
            ["Nifty Smallcap 250 (^CNXSMCP)", "BSE SmallCap (^BSESML)", "Nifty 50 (^NSEI)"]
        )
    with col2:
        period = st.selectbox("Period:", ["1mo", "3mo", "6mo", "1y", "2y"])
    
    symbol_map = {
        "Nifty Smallcap 250 (^CNXSMCP)": "^CNXSMCP",
        "BSE SmallCap (^BSESML)": "^BSESML",
        "Nifty 50 (^NSEI)": "^NSEI"
    }
    
    if st.button("Fetch Index Data", type="primary"):
        symbol = symbol_map[index_choice]
        with st.spinner(f"Fetching {index_choice} data..."):
            proxy_data = fetch_proxy_index_data(symbol, period)
            if proxy_data is not None:
                st.session_state.data = proxy_data
                st.session_state.analysis_results = calculate_metrics(proxy_data, 'Close')
                st.success(f"Fetched {len(proxy_data)} trading days for {index_choice}!")
            else:
                st.error("Failed to fetch data. Please try again.")

elif data_source == "Live Market APIs" and HAS_API_INTEGRATION:
    st.header("🟣 Live Market APIs")
    st.markdown("""
    <div class="api-section">
        <h4>🚀 Real-time Market Data Integration</h4>
        <p>Access live cryptocurrency prices, exchange rates, and stock data from multiple sources!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🪙 Cryptocurrency Data")
        crypto_choice = st.selectbox(
            "Select Cryptocurrency:",
            ["bitcoin", "ethereum", "cardano", "solana", "polkadot"]
        )
        
        if st.button("Get Crypto Price", type="primary"):
            with st.spinner(f"Fetching {crypto_choice} data..."):
                crypto_data = st.session_state.api_integrator.get_crypto_price(crypto_choice)
                if crypto_data:
                    st.success("✅ Live crypto data retrieved!")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("USD Price", f"${crypto_data['price_usd']:,.2f}")
                        st.metric("24h Change", f"{crypto_data['change_24h']:+.2f}%")
                    with col_b:
                        st.metric("INR Price", f"₹{crypto_data['price_inr']:,.2f}")
                        st.metric("Market Cap", f"${crypto_data['market_cap_usd']:,.0f}")
                else:
                    st.error("Failed to fetch crypto data")
    
    with col2:
        st.subheader("💱 Exchange Rates")
        col_from, col_to = st.columns(2)
        with col_from:
            from_currency = st.selectbox("From:", ["USD", "EUR", "GBP", "JPY"])
        with col_to:
            to_currency = st.selectbox("To:", ["INR", "USD", "EUR", "GBP"])
        
        if st.button("Get Exchange Rate", type="primary"):
            with st.spinner(f"Fetching {from_currency} to {to_currency} rate..."):
                fx_data = st.session_state.api_integrator.get_exchange_rate(from_currency, to_currency)
                if fx_data:
                    st.success("✅ Live exchange rate retrieved!")
                    st.metric(f"{from_currency} to {to_currency}", f"{fx_data['rate']:.4f}")
                    st.caption(f"Date: {fx_data['date']} | Source: {fx_data['source']}")
                else:
                    st.error("Failed to fetch exchange rate")
    
    # Stock Data Section
    st.subheader("📈 Stock Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        stock_symbol = st.selectbox(
            "Select Stock:",
            ["AAPL", "MSFT", "GOOGL", "TSLA", "INDA", "NVDA", "META"]
        )
    with col2:
        period = st.selectbox("Period:", ["1mo", "3mo", "6mo", "1y"], key="stock_period")
    with col3:
        if st.button("Get Stock Data", type="primary"):
            with st.spinner(f"Fetching {stock_symbol} data..."):
                stock_data = st.session_state.api_integrator.get_yfinance_data(stock_symbol, period)
                if stock_data:
                    # Convert to the format expected by our analyzer
                    df = stock_data['data'].copy()
                    df['Date'] = pd.to_datetime(df['Date'])
                    df['Change'] = df['NAV'].diff()
                    df['Change_Pct'] = df['NAV'].pct_change() * 100
                    
                    st.session_state.data = df
                    st.session_state.analysis_results = calculate_metrics(df)
                    
                    st.success(f"✅ Loaded {stock_data['data_points']} days of {stock_symbol} data!")
                    
                    # Quick metrics
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Current Price", f"${stock_data['current_price']:.2f}")
                    with col_b:
                        st.metric("Return", f"{stock_data['return_percent']:+.2f}%")
                    with col_c:
                        st.metric("Data Source", stock_data['source'])
                else:
                    st.error("Failed to fetch stock data")
    
    # Live API Status
    st.subheader("📊 API Status Dashboard")
    status_col1, status_col2, status_col3 = st.columns(3)
    
    if st.button("🔄 Test All APIs"):
        with st.spinner("Testing API connections..."):
            # Test crypto API
            btc_test = st.session_state.api_integrator.get_crypto_price("bitcoin")
            # Test forex API  
            fx_test = st.session_state.api_integrator.get_exchange_rate("USD", "INR")
            # Test stock API
            stock_test = st.session_state.api_integrator.get_yfinance_data("AAPL", "1mo")
            
            with status_col1:
                if btc_test:
                    st.success("🟢 CoinGecko API")
                    st.caption(f"BTC: ${btc_test['price_usd']:,.0f}")
                else:
                    st.error("🔴 CoinGecko API")
            
            with status_col2:
                if fx_test:
                    st.success("🟢 Frankfurter API")
                    st.caption(f"USD/INR: {fx_test['rate']:.2f}")
                else:
                    st.error("🔴 Frankfurter API")
            
            with status_col3:
                if stock_test:
                    st.success(f"🟢 {stock_test['source']}")
                    st.caption(f"AAPL: ${stock_test['current_price']:.2f}")
                else:
                    st.error("🔴 Stock API")

elif data_source == "Upload CSV":
    st.header("📁 Upload CSV Data")
    st.info("Upload your own CSV file with NAV data. Required columns: Date, NAV")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type="csv",
        help="CSV should have 'Date' and 'NAV' columns"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df['Date'] = pd.to_datetime(df['Date'])
            
            if 'NAV' in df.columns:
                # Calculate additional metrics
                df['Change'] = df['NAV'].diff()
                df['Change_Pct'] = df['NAV'].pct_change() * 100
                
                st.session_state.data = df
                st.session_state.analysis_results = calculate_metrics(df)
                st.success(f"Uploaded {len(df)} records successfully!")
                
                # Show preview
                st.subheader("Data Preview")
                st.dataframe(df.head(10))
            else:
                st.error("CSV must contain 'NAV' column")
        except Exception as e:
            st.error(f"Error reading CSV: {str(e)}")

elif data_source == "Manual Entry":
    st.header("✏️ Manual Data Entry")
    st.info("Enter NAV data manually for quick analysis.")
    
    # Create a simple form for manual entry
    with st.form("manual_entry_form"):
        st.subheader("Enter NAV Data Points")
        
        num_points = st.slider("Number of data points", min_value=3, max_value=20, value=7)
        
        dates = []
        navs = []
        
        cols = st.columns(2)
        for i in range(num_points):
            with cols[0]:
                date = st.date_input(f"Date {i+1}", 
                                   value=datetime.now() - timedelta(days=(num_points-i-1)*30),
                                   key=f"date_{i}")
                dates.append(date)
            with cols[1]:
                nav = st.number_input(f"NAV {i+1}", 
                                    value=150.0 + i*2.5, 
                                    min_value=0.0, 
                                    step=0.01,
                                    key=f"nav_{i}")
                navs.append(nav)
        
        if st.form_submit_button("Create Dataset", type="primary"):
            manual_data = pd.DataFrame({
                'Date': dates,
                'NAV': navs
            })
            manual_data = manual_data.sort_values('Date')
            manual_data['Change'] = manual_data['NAV'].diff()
            manual_data['Change_Pct'] = manual_data['NAV'].pct_change() * 100
            
            st.session_state.data = manual_data
            st.session_state.analysis_results = calculate_metrics(manual_data)
            st.success("Manual dataset created successfully!")

# Display analysis if data is available
if st.session_state.data is not None and st.session_state.analysis_results is not None:
    st.header("📊 Performance Analysis")
    
    # Key metrics
    metrics = st.session_state.analysis_results
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card success-metric">', unsafe_allow_html=True)
        st.metric(
            "Total Return",
            f"{metrics['total_return']:.2f}%",
            delta=f"{metrics['avg_daily_return']:.3f}% daily avg"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card warning-metric">', unsafe_allow_html=True)
        st.metric(
            "Volatility",
            f"{metrics['volatility']:.2f}%",
            delta=f"Sharpe: {metrics['sharpe_ratio']:.2f}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card error-metric">', unsafe_allow_html=True)
        st.metric(
            "Max Drawdown",
            f"{metrics['max_drawdown']:.2f}%",
            delta=f"Worst day: {metrics['worst_day']:.2f}%"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Current Value",
            f"{metrics['current_value']:.2f}",
            delta=f"Best day: {metrics['best_day']:.2f}%"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts
    st.subheader("📈 Performance Charts")
    
    # Main performance chart
    value_col = 'NAV' if 'NAV' in st.session_state.data.columns else 'Close'
    perf_chart = create_performance_chart(
        st.session_state.data, 
        value_col, 
        "Nippon India Small Cap Fund - Price Movement"
    )
    st.plotly_chart(perf_chart, use_container_width=True)
    
    # Additional charts in columns
    col1, col2 = st.columns(2)
    
    with col1:
        returns_chart = create_returns_distribution(st.session_state.data, value_col)
        st.plotly_chart(returns_chart, use_container_width=True)
    
    with col2:
        drawdown_chart = create_drawdown_chart(st.session_state.data, value_col)
        st.plotly_chart(drawdown_chart, use_container_width=True)
    
    # Data table
    with st.expander("📋 View Raw Data"):
        st.dataframe(st.session_state.data, use_container_width=True)
    
    # Download options
    st.subheader("💾 Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        csv = st.session_state.data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"nippon_fund_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Create summary report
        summary_text = f"""
Nippon India Small Cap Fund Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Performance Metrics:
- Total Return: {metrics['total_return']:.2f}%
- Volatility: {metrics['volatility']:.2f}%
- Max Drawdown: {metrics['max_drawdown']:.2f}%
- Sharpe Ratio: {metrics['sharpe_ratio']:.2f}
- Current Value: {metrics['current_value']:.2f}
- Average Daily Return: {metrics['avg_daily_return']:.3f}%
- Best Single Day: {metrics['best_day']:.2f}%
- Worst Single Day: {metrics['worst_day']:.2f}%

Data Period: {len(st.session_state.data)} observations
Data Source: {data_source}
"""
        
        st.download_button(
            label="Download Report",
            data=summary_text,
            file_name=f"nippon_fund_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

# API Integration Status
if HAS_API_INTEGRATION:
    st.sidebar.markdown("---")
    st.sidebar.markdown("🔗 **API Integration: Active**")
    st.sidebar.success("✅ CoinGecko, Frankfurter & Yahoo Finance")
else:
    st.sidebar.markdown("---")
    st.sidebar.warning("⚠️ API Integration: Inactive")
    st.sidebar.caption("Install financial_api_integration.py")

# Footer
st.markdown("---")
st.markdown("""
**📝 Notes:**
- Sample data is for demonstration purposes only
- Proxy indices provide market trend approximation
- Live APIs provide real-time market data
- Past performance does not guarantee future results
- This tool is for educational purposes only

**🔗 Useful Links:**
- [Moneycontrol - Nippon Small Cap Fund](https://www.moneycontrol.com/mutual-funds/nav/nippon-india-small-cap-fund-direct-plan-growth/MNS092)
- [Yahoo Finance - Nifty Smallcap 250](https://finance.yahoo.com/quote/%5ECNXSMCP/)
""") 