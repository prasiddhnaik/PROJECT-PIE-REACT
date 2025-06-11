import streamlit as st
import time
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import hashlib
from typing import Dict, List, Optional, Any
import warnings
import pandas as pd
import plotly.graph_objects as go
warnings.filterwarnings('ignore')

# Import chart gallery
try:
    from modules.chart_gallery import render_chart_gallery
    CHART_GALLERY_AVAILABLE = True
except ImportError:
    CHART_GALLERY_AVAILABLE = False

# Import API configuration
try:
    from config import API_CONFIG
    ALPHA_VANTAGE_KEY = API_CONFIG.get('alpha_vantage_key', 'demo')
except ImportError:
    ALPHA_VANTAGE_KEY = 'demo'

# 🚀 LAZY LOADING - Initialize on demand
_api_integrator = None
_supabase_client = None

def get_api_integrator_lazy():
    """Lazy load API integrator only when needed"""
    global _api_integrator
    if _api_integrator is None:
        _api_integrator = get_api_integrator()
    return _api_integrator

def get_supabase_lazy():
    """Lazy load Supabase client only when needed"""
    global _supabase_client
    if _supabase_client is None:
        try:
            from utils.supabase_client import get_supabase_client
            _supabase_client = get_supabase_client()
        except ImportError:
            _supabase_client = None
    return _supabase_client

# 🎨 BEAUTIFUL ANIMATIONS & VISUAL EFFECTS
ENHANCED_CSS = """
<style>
/* 🚀 Global Animation Styles */
* {
    transition: all 0.3s ease-in-out !important;
}

/* 🎯 Animated Loading Spinner */
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* 🌟 Enhanced Header with Animation */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    animation: fadeIn 1s ease-out;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.main-header h1 {
    color: white;
    text-align: center;
    font-size: 3rem;
    font-weight: 700;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

.live-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    background: #00ff7f;
    border-radius: 50%;
    animation: pulse 2s infinite;
    margin-left: 10px;
}

/* 🎪 Animated Metrics Cards */
.metric-card {
    background: linear-gradient(145deg, #ffffff, #f0f2f6);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    animation: fadeIn 0.8s ease-out;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.2);
}

/* 🚀 Fast Loading Placeholder */
.lazy-placeholder {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
    background: linear-gradient(45deg, #f8f9fa, #e9ecef);
    border-radius: 15px;
    margin: 2rem 0;
    animation: pulse 2s infinite;
}

.lazy-placeholder h3 {
    color: #6c757d;
    font-weight: 300;
}

/* 🎯 Loading Animation */
.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
</style>
"""

def render_animated_header():
    """🌟 Render beautiful animated header with live indicators"""
    st.markdown(ENHANCED_CSS, unsafe_allow_html=True)
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Financial Analytics Hub <span class="live-indicator"></span></h1>
        <p style="text-align: center; color: rgba(255,255,255,0.9); font-size: 1.2rem; margin: 0;">
            ⚡ Lightning-Fast • 🔄 Real-Time Data • 📊 Professional Analytics
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_animated_metric(title, value, delta=None, card_class="metric-card"):
    """🎪 Render animated metric cards"""
    delta_html = f"<span style='color: #28a745;'>+{delta}</span>" if delta else ""
    st.markdown(f"""
    <div class="{card_class}">
        <h4 style="margin: 0; color: #333;">{title}</h4>
        <h2 style="margin: 10px 0 0 0; color: #667eea;">{value} {delta_html}</h2>
    </div>
    """, unsafe_allow_html=True)

def render_success_notification(message):
    """✅ Success notification with animation"""
    st.markdown(f"""
    <div style="background: linear-gradient(45deg, #28a745, #20c997); color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)

def render_loading_animation(text="Loading..."):
    """🎯 Beautiful loading animation"""
    st.markdown(f"""
    <div class="lazy-placeholder">
        <h3><span class="loading-spinner"></span> &nbsp; {text}</h3>
    </div>
    """, unsafe_allow_html=True)

def render_live_price_indicator(symbol, price, change_pct):
    """💰 Live price indicator with animation"""
    color = "#28a745" if change_pct >= 0 else "#dc3545"
    arrow = "↗" if change_pct >= 0 else "↘"
    
    st.markdown(f"""
    <div style="display: inline-block; background: {color}; color: white; padding: 0.5rem 1rem; border-radius: 20px; margin: 0.2rem; animation: pulse 2s infinite;">
        <strong>{symbol}</strong> ${price} <span style="font-size: 1.2rem;">{arrow}</span> {change_pct:.2f}%
    </div>
    """, unsafe_allow_html=True)

# 📊 MINIMAL API INTEGRATOR - Only what's needed
@st.cache_resource(ttl=900)
def get_api_integrator():
    """Lightweight API integrator with minimal initialization"""
    return FinancialAPIIntegrator()

class FinancialAPIIntegrator:
    """Lightweight API integrator focused on speed"""
    
    def __init__(self):
        self.cache = {}
        self.last_update = {}
    
    @st.cache_data(ttl=180, show_spinner=False)
    def get_crypto_price(self, crypto_id="bitcoin"):
        """Get crypto price with fast caching"""
        try:
            response = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd&include_24hr_change=true",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if crypto_id in data:
                    crypto_data = data[crypto_id]
                    return {
                        'success': True,
                        'data': {
                            'current_price': crypto_data['usd'],
                            'change_24h': crypto_data.get('usd_24h_change', 0)
                        }
                    }
            
            return {'success': False, 'error': 'API error'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_exchange_rate(self, from_currency="USD", to_currency="INR"):
        """Get exchange rate with fast caching"""
        try:
            response = requests.get(
                f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'rates' in data and to_currency in data['rates']:
                    return {
                        'success': True,
                        'data': {
                            'rate': data['rates'][to_currency],
                            'from': from_currency,
                            'to': to_currency
                        }
                    }
            
            return {'success': False, 'error': 'Rate not found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @st.cache_data(ttl=120, show_spinner=False)
    def get_alpha_vantage_stock(self, symbol):
        """Get stock data using Alpha Vantage API"""
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    
                    current_price = float(quote.get('05. price', 0))
                    change_percent = float(quote.get('10. change percent', '0').replace('%', ''))
                    
                    return {
                        'success': True,
                        'data': {
                            'symbol': symbol,
                            'current_price': current_price,
                            'change_percent': change_percent,
                            'source': 'Alpha Vantage'
                        }
                    }
                else:
                    return {'success': False, 'error': 'Invalid API response'}
            
            return {'success': False, 'error': f'API error: {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

@st.cache_data(ttl=300, show_spinner=False)
def get_live_market_data():
    """Generate sample market data for demonstration"""
    try:
        # Create sample data
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
        data = []
        
        for symbol in symbols:
            # Sample data for demonstration
            data.append({
                'Symbol': symbol,
                'Price': f"${200 + hash(symbol) % 300:.2f}",
                'Change': f"{(hash(symbol) % 10 - 5):.2f}%",
                'Volume': f"{(hash(symbol) % 1000000):,}"
            })
        
        return pd.DataFrame(data)
    
    except Exception as e:
        return None

def render_live_status():
    """Render live status indicator"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔴 Live Status")
    st.sidebar.success("🟢 All systems operational")
    st.sidebar.info(f"🕒 Last update: {datetime.now().strftime('%H:%M:%S')}")

def render_auto_update_controls():
    """Render auto-update controls"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔄 Auto Updates")
    
    auto_update = st.sidebar.checkbox("🔄 Enable auto-refresh", value=True)
    
    if auto_update:
        interval = st.sidebar.selectbox("⏰ Refresh interval", 
                                      options=[30, 60, 120, 300], 
                                      index=1, 
                                      format_func=lambda x: f"{x} seconds")
        st.sidebar.success(f"✅ Auto-refresh every {interval}s")
    else:
        st.sidebar.info("ℹ️ Manual refresh only")

# 🚀 MAIN APP - LIGHTNING FAST WITH LAZY LOADING
def main():
    """🚀 Main app with instant loading and lazy initialization"""
    
    # Apply CSS immediately for fast UI
    st.markdown(ENHANCED_CSS, unsafe_allow_html=True)
    
    # Fast header load
    render_animated_header()
    
    # Authentication sidebar (loads instantly)
    try:
        from utils.auth_component import render_auth_sidebar
        user = render_auth_sidebar()
    except ImportError:
        st.sidebar.warning("⚠️ Authentication not configured")
        user = None
    
    # Main tab structure (loads instantly)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "🏠 Home", 
        "📊 Real-Time Analytics", 
        "💹 Investment Hub", 
        "🌍 Global Markets", 
        "📈 Professional Chart Gallery",
        "💰 Cryptocurrency", 
        "💱 Currency Exchange", 
        "📰 Market News", 
        "🎲 Monte Carlo Simulation",
        "👤 My Dashboard"
    ])
    
    # ✨ LAZY LOADING - Only load tab content when accessed
    
    with tab1:
        st.header("🏠 Welcome to Financial Analytics Hub")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_animated_metric("🚀 Status", "Live & Ready")
        with col2:
            render_animated_metric("⚡ Loading", "Instant")
        with col3:
            render_animated_metric("📊 Data Sources", "10+ APIs")
        with col4:
            render_animated_metric("🔄 Updates", "Real-Time")
        
        st.info("🎯 **Lazy Loading Active**: Each tab loads instantly when you click it. No more waiting!")
        
        st.subheader("🚀 Quick Start Guide")
        st.markdown("""
        ### Choose Your Adventure:
        
        - **📊 Real-Time Analytics**: Live market data, stock prices, and financial metrics
        - **💹 Investment Hub**: SIP calculations, portfolio analysis, and savings tools  
        - **🌍 Global Markets**: International indices, bonds, and economic indicators
        - **📈 Professional Chart Gallery**: Advanced charts with technical analysis
        - **💰 Cryptocurrency**: Real-time crypto prices and market analysis
        - **💱 Currency Exchange**: Live exchange rates and currency conversion
        - **📰 Market News**: Latest financial news and market insights
        - **🎲 Monte Carlo Simulation**: Advanced risk analysis and probability modeling
        - **👤 My Dashboard**: Personal portfolio and saved calculations
        
        🎯 **Pro Tip**: Each tab loads only when you need it, ensuring lightning-fast performance!
        """)
    
    with tab2:
        if st.session_state.get('tab2_loaded', False) or st.button("📊 Load Real-Time Analytics", key="load_tab2"):
            st.session_state.tab2_loaded = True
            
            with st.spinner("📊 Loading real-time market data..."):
                api = get_api_integrator_lazy()
                
                # Live status and controls
                render_live_status()
                render_auto_update_controls()
                
                st.subheader("📈 Live Market Overview")
                
                # Quick market stats
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    btc_data = api.get_crypto_price("bitcoin")
                    if btc_data and btc_data.get('success'):
                        btc_price = btc_data['data']['current_price']
                        btc_change = btc_data['data'].get('change_24h', 0)
                        render_live_price_indicator("BTC", f"{btc_price:,.0f}", btc_change)
                    else:
                        st.metric("₿ Bitcoin", "Loading...")
                
                with col2:
                    # Get stock data (using Alpha Vantage)
                    stock_data = api.get_alpha_vantage_stock("AAPL")
                    if stock_data and stock_data.get('success'):
                        price = stock_data['data']['current_price']
                        change = stock_data['data'].get('change_percent', 0)
                        render_live_price_indicator("AAPL", f"{price:.2f}", change)
                    else:
                        st.metric("🍎 Apple", "Loading...")
                
                with col3:
                    usd_inr = api.get_exchange_rate("USD", "INR")
                    if usd_inr and usd_inr.get('success'):
                        rate = usd_inr['data']['rate']
                        st.metric("💱 USD/INR", f"₹{rate:.2f}")
                    else:
                        st.metric("💱 USD/INR", "Loading...")
                
                with col4:
                    render_animated_metric("🔄 Last Update", datetime.now().strftime("%H:%M:%S"))
                
                # Market data table
                st.subheader("📊 Market Data")
                
                market_data = get_live_market_data()
                if market_data is not None:
                    st.dataframe(market_data, use_container_width=True)
                else:
                    st.info("📊 Market data loading...")
        else:
            render_loading_animation("Click to load Real-Time Analytics")
    
    with tab3:
        if st.session_state.get('tab3_loaded', False) or st.button("💹 Load Investment Hub", key="load_tab3"):
            st.session_state.tab3_loaded = True
            
            with st.spinner("💹 Loading investment tools..."):
                api = get_api_integrator_lazy()
                
                # SIP Calculator and other investment tools would go here
                st.header("💹 Investment Hub")
                st.subheader("🔧 SIP Calculator")
                
                # SIP Calculator UI
                col1, col2 = st.columns(2)
                
                with col1:
                    monthly_sip = st.number_input("💰 Monthly SIP Amount (₹)", min_value=500, max_value=100000, value=5000, step=500)
                    annual_rate = st.slider("📈 Expected Annual Return (%)", min_value=1.0, max_value=30.0, value=12.0, step=0.5)
                    time_years = st.slider("⏰ Investment Duration (Years)", min_value=1, max_value=40, value=10)
                
                with col2:
                    # Quick calculation
                    months = time_years * 12
                    monthly_rate = annual_rate / 100 / 12
                    
                    if monthly_rate > 0:
                        future_value = monthly_sip * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
                    else:
                        future_value = monthly_sip * months
                    
                    total_invested = monthly_sip * months
                    total_returns = future_value - total_invested
                    
                    st.metric("💰 Total Invested", f"₹{total_invested:,.0f}")
                    st.metric("🎯 Future Value", f"₹{future_value:,.0f}")
                    st.metric("📈 Total Returns", f"₹{total_returns:,.0f}")
                    st.metric("📊 Return %", f"{(total_returns/total_invested)*100:.1f}%")
                
                # Save calculation
                if user and st.button("💾 Save Calculation"):
                    calculation_data = {
                        'monthly_sip': monthly_sip,
                        'annual_rate': annual_rate,
                        'time_years': time_years,
                        'total_invested': total_invested,
                        'final_value': future_value,
                        'total_returns': total_returns,
                        'calculation_type': 'sip_calculator'
                    }
                    
                    supabase = get_supabase_lazy()
                    if supabase:
                        result = supabase.save_calculation(calculation_data, user['id'])
                        if result['success']:
                            render_success_notification("Calculation saved successfully!")
                        else:
                            st.error(f"Error saving: {result['error']}")
        else:
            render_loading_animation("Click to load Investment Hub")
    
    with tab4:
        if st.session_state.get('tab4_loaded', False) or st.button("🌍 Load Global Markets", key="load_tab4"):
            st.session_state.tab4_loaded = True
            
            with st.spinner("🌍 Loading global market data..."):
                api = get_api_integrator_lazy()
                
                st.header("🌍 Global Markets")
                st.info("🌍 Global market data loading...")
        else:
            render_loading_animation("Click to load Global Markets")
    
    with tab5:
        if st.session_state.get('tab5_loaded', False) or st.button("📈 Load Professional Charts", key="load_tab5"):
            st.session_state.tab5_loaded = True
            
            with st.spinner("📈 Loading professional charts..."):
                if CHART_GALLERY_AVAILABLE:
                    render_chart_gallery()
                else:
                    st.error("📈 Chart gallery not available")
        else:
            render_loading_animation("Click to load Professional Chart Gallery")
    
    with tab6:
        if st.session_state.get('tab6_loaded', False) or st.button("💰 Load Cryptocurrency", key="load_tab6"):
            st.session_state.tab6_loaded = True
            
            with st.spinner("💰 Loading cryptocurrency data..."):
                api = get_api_integrator_lazy()
                
                st.header("💰 Cryptocurrency Dashboard")
                
                # Top cryptos
                crypto_symbols = ["bitcoin", "ethereum", "binancecoin", "cardano", "solana"]
                
                for crypto in crypto_symbols:
                    data = api.get_crypto_price(crypto)
                    if data and data.get('success'):
                        price = data['data']['current_price']
                        change = data['data'].get('change_24h', 0)
                        st.metric(f"🪙 {crypto.title()}", f"${price:,.2f}", f"{change:+.2f}%")
        else:
            render_loading_animation("Click to load Cryptocurrency")
    
    with tab7:
        if st.session_state.get('tab7_loaded', False) or st.button("💱 Load Currency Exchange", key="load_tab7"):
            st.session_state.tab7_loaded = True
            
            with st.spinner("💱 Loading currency exchange..."):
                api = get_api_integrator_lazy()
                
                st.header("💱 Currency Exchange")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    from_currency = st.selectbox("From Currency", ["USD", "EUR", "GBP", "JPY", "INR"])
                
                with col2:
                    to_currency = st.selectbox("To Currency", ["INR", "USD", "EUR", "GBP", "JPY"])
                
                with col3:
                    amount = st.number_input("Amount", min_value=1.0, value=100.0)
                
                if st.button("💱 Convert"):
                    rate_data = api.get_exchange_rate(from_currency, to_currency)
                    if rate_data and rate_data.get('success'):
                        rate = rate_data['data']['rate']
                        converted = amount * rate
                        st.success(f"💰 {amount} {from_currency} = {converted:.2f} {to_currency}")
                        st.info(f"📊 Exchange Rate: 1 {from_currency} = {rate:.4f} {to_currency}")
        else:
            render_loading_animation("Click to load Currency Exchange")
    
    with tab8:
        if st.session_state.get('tab8_loaded', False) or st.button("📰 Load Market News", key="load_tab8"):
            st.session_state.tab8_loaded = True
            
            with st.spinner("📰 Loading market news..."):
                api = get_api_integrator_lazy()
                
                st.header("📰 Market News & Insights")
                st.info("📰 Financial news loading...")
        else:
            render_loading_animation("Click to load Market News")
    
    with tab9:
        if st.session_state.get('tab9_loaded', False) or st.button("🎲 Load Monte Carlo", key="load_tab9"):
            st.session_state.tab9_loaded = True
            
            with st.spinner("🎲 Loading Monte Carlo simulation..."):
                st.header("🎲 Monte Carlo Simulation")
                st.info("🎲 Advanced simulation tools loading...")
        else:
            render_loading_animation("Click to load Monte Carlo Simulation")
    
    with tab10:
        if user:
            if st.session_state.get('tab10_loaded', False) or st.button("👤 Load My Dashboard", key="load_tab10"):
                st.session_state.tab10_loaded = True
                
                with st.spinner("👤 Loading your dashboard..."):
                    supabase = get_supabase_lazy()
                    
                    st.header(f"👤 Welcome back, {user.get('email', 'User')}")
                    
                    if supabase:
                        # Get user's calculations
                        calculations_result = supabase.get_user_calculations(user['id'])
                        
                        if calculations_result['success'] and calculations_result['data']:
                            st.subheader("📊 Your Recent Calculations")
                            
                            for calc in calculations_result['data'][:5]:
                                with st.expander(f"📊 {calc['calculation_type'].title()} - {calc['created_at'][:10]}"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.write(f"💰 Monthly SIP: ₹{calc.get('monthly_sip', 0):,.0f}")
                                        st.write(f"📈 Annual Rate: {calc.get('annual_rate', 0):.1f}%")
                                        st.write(f"⏰ Duration: {calc.get('time_years', 0)} years")
                                    
                                    with col2:
                                        st.write(f"📊 Total Invested: ₹{calc.get('total_invested', 0):,.0f}")
                                        st.write(f"🎯 Final Value: ₹{calc.get('final_value', 0):,.0f}")
                                        profit = calc.get('final_value', 0) - calc.get('total_invested', 0)
                                        st.write(f"💰 Profit: ₹{profit:,.0f}")
                        else:
                            st.info("📝 No saved calculations found. Start using the Investment Hub!")
                    else:
                        st.warning("⚠️ Database not configured")
            else:
                render_loading_animation("Click to load Your Dashboard")
        else:
            st.info("🔐 Please login to access your personal dashboard")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🚀 <strong>Lightning Fast Loading</strong> • ⚡ Lazy Loading Active • Built with ❤️ using Streamlit</p>
        <p><small>Last updated: {}</small></p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main() 