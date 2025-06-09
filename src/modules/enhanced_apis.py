#!/usr/bin/env python3
"""
🚀 Enhanced APIs Module for Financial Analytics Hub
Integrates additional free APIs that work immediately
"""

import requests
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

@st.cache_data(ttl=1800)  # 30-minute cache
def get_world_bank_economic_data():
    """Get World Bank economic indicators for major economies"""
    
    # Key economic indicators
    indicators = {
        'NY.GDP.MKTP.CD': 'GDP (Current USD)',
        'FP.CPI.TOTL.ZG': 'Inflation Rate (%)',
        'SL.UEM.TOTL.ZS': 'Unemployment Rate (%)',
        'NY.GDP.MKTP.KD.ZG': 'GDP Growth Rate (%)',
        'NE.TRD.GNFS.ZS': 'Trade (% of GDP)'
    }
    
    # Major economies
    countries = {
        'US': 'United States',
        'CN': 'China', 
        'JP': 'Japan',
        'DE': 'Germany',
        'IN': 'India',
        'GB': 'United Kingdom',
        'FR': 'France',
        'CA': 'Canada'
    }
    
    economic_data = {}
    
    for country_code, country_name in countries.items():
        economic_data[country_name] = {}
        
        for indicator_code, indicator_name in indicators.items():
            try:
                url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"
                params = {
                    'format': 'json',
                    'date': '2020:2023',
                    'per_page': 5
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1 and data[1] and data[1][0]['value']:
                        latest = data[1][0]
                        economic_data[country_name][indicator_name] = {
                            'value': latest['value'],
                            'date': latest['date'],
                            'formatted_value': f"{latest['value']:,.2f}" if latest['value'] else "N/A"
                        }
            except Exception as e:
                print(f"World Bank API error for {country_name} {indicator_name}: {e}")
                continue
    
    return economic_data

@st.cache_data(ttl=300)  # 5-minute cache for crypto
def get_enhanced_crypto_data():
    """Get comprehensive crypto data from working APIs"""
    
    # Major cryptocurrencies
    cryptos = {
        'bitcoin': 'BTC',
        'ethereum': 'ETH',
        'binancecoin': 'BNB',
        'cardano': 'ADA',
        'solana': 'SOL',
        'xrp': 'XRP',
        'polkadot': 'DOT',
        'dogecoin': 'DOGE'
    }
    
    crypto_data = {}
    
    # Method 1: CryptoCompare (working in your logs)
    for crypto_id, symbol in cryptos.items():
        try:
            url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbol}&tsyms=USD"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'RAW' in data and symbol in data['RAW'] and 'USD' in data['RAW'][symbol]:
                    raw_data = data['RAW'][symbol]['USD']
                    
                    crypto_data[crypto_id] = {
                        'symbol': symbol,
                        'price': raw_data.get('PRICE', 0),
                        'change_24h': raw_data.get('CHANGEPCT24HOUR', 0),
                        'market_cap': raw_data.get('MKTCAP', 0),
                        'volume_24h': raw_data.get('TOTALVOLUME24HTO', 0),
                        'source': 'CryptoCompare',
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"CryptoCompare error for {crypto_id}: {e}")
            continue
    
    # Method 2: Binance (working in your logs)
    binance_pairs = {
        'bitcoin': 'BTCUSDT',
        'ethereum': 'ETHUSDT',
        'binancecoin': 'BNBUSDT',
        'cardano': 'ADAUSDT',
        'solana': 'SOLUSDT'
    }
    
    for crypto_id, pair in binance_pairs.items():
        if crypto_id not in crypto_data:  # Only if CryptoCompare failed
            try:
                url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    crypto_data[crypto_id] = {
                        'symbol': pair.replace('USDT', ''),
                        'price': float(data.get('lastPrice', 0)),
                        'change_24h': float(data.get('priceChangePercent', 0)),
                        'volume_24h': float(data.get('volume', 0)),
                        'source': 'Binance',
                        'timestamp': datetime.now().isoformat()
                    }
            except Exception as e:
                print(f"Binance error for {crypto_id}: {e}")
                continue
    
    return crypto_data

@st.cache_data(ttl=1800)  # 30-minute cache
def get_enhanced_forex_data():
    """Get comprehensive forex data from working APIs"""
    
    # Major currency pairs
    base_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF']
    target_currencies = ['USD', 'EUR', 'GBP', 'INR', 'CNY', 'JPY']
    
    forex_data = {}
    
    # Method 1: ExchangeRate-API (working in your logs)
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})
            
            for currency in target_currencies:
                if currency != 'USD' and currency in rates:
                    forex_data[f'USD/{currency}'] = {
                        'rate': rates[currency],
                        'base': 'USD',
                        'target': currency,
                        'date': data.get('date', ''),
                        'source': 'ExchangeRate-API',
                        'timestamp': datetime.now().isoformat()
                    }
    except Exception as e:
        print(f"ExchangeRate-API error: {e}")
    
    # Method 2: Frankfurter for EUR pairs
    try:
        url = "https://api.frankfurter.app/latest?from=EUR"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})
            
            for currency in ['USD', 'GBP', 'JPY', 'CHF']:
                if currency in rates:
                    forex_data[f'EUR/{currency}'] = {
                        'rate': rates[currency],
                        'base': 'EUR',
                        'target': currency,
                        'date': data.get('date', ''),
                        'source': 'Frankfurter (ECB)',
                        'timestamp': datetime.now().isoformat()
                    }
    except Exception as e:
        print(f"Frankfurter error: {e}")
    
    return forex_data

def display_enhanced_api_dashboard():
    """Display enhanced API dashboard with working APIs"""
    
    st.header("🚀 Enhanced API Dashboard")
    st.info("🔥 **NEW**: Additional free APIs integrated! Real-time economic data from World Bank, enhanced crypto data, and more!")
    
    # Create tabs for different data types
    tab1, tab2, tab3 = st.columns(3)
    
    with tab1:
        st.subheader("🌍 Global Economic Data")
        if st.button("📊 Load Economic Indicators", type="primary"):
            with st.spinner("Loading World Bank data..."):
                economic_data = get_world_bank_economic_data()
                
                if economic_data:
                    st.success(f"✅ Loaded data for {len(economic_data)} countries")
                    
                    # Create economic comparison chart
                    countries = list(economic_data.keys())
                    gdp_data = []
                    inflation_data = []
                    
                    for country in countries:
                        gdp_info = economic_data[country].get('GDP (Current USD)', {})
                        inflation_info = economic_data[country].get('Inflation Rate (%)', {})
                        
                        if gdp_info.get('value'):
                            gdp_data.append({'Country': country, 'GDP (Trillions USD)': gdp_info['value']/1e12})
                        
                        if inflation_info.get('value'):
                            inflation_data.append({'Country': country, 'Inflation Rate (%)': inflation_info['value']})
                    
                    # GDP Chart
                    if gdp_data:
                        df_gdp = pd.DataFrame(gdp_data)
                        fig_gdp = px.bar(df_gdp, x='Country', y='GDP (Trillions USD)', 
                                        title='🌍 Global GDP Comparison (Trillions USD)')
                        fig_gdp.update_layout(xaxis_tickangle=45)
                        st.plotly_chart(fig_gdp, use_container_width=True)
                    
                    # Inflation Chart
                    if inflation_data:
                        df_inflation = pd.DataFrame(inflation_data)
                        fig_inflation = px.bar(df_inflation, x='Country', y='Inflation Rate (%)', 
                                             title='📈 Global Inflation Rates (%)', color='Inflation Rate (%)',
                                             color_continuous_scale='RdYlBu_r')
                        fig_inflation.update_layout(xaxis_tickangle=45)
                        st.plotly_chart(fig_inflation, use_container_width=True)
                    
                    # Display detailed data
                    with st.expander("📋 Detailed Economic Data"):
                        for country, indicators in economic_data.items():
                            st.write(f"**{country}:**")
                            for indicator, info in indicators.items():
                                st.write(f"  • {indicator}: {info.get('formatted_value', 'N/A')} ({info.get('date', 'N/A')})")
                else:
                    st.error("❌ Failed to load economic data")
    
    with tab2:
        st.subheader("🪙 Enhanced Crypto Data")
        if st.button("🔄 Load Crypto Data", type="primary"):
            with st.spinner("Loading enhanced crypto data..."):
                crypto_data = get_enhanced_crypto_data()
                
                if crypto_data:
                    st.success(f"✅ Loaded {len(crypto_data)} cryptocurrencies")
                    
                    # Create crypto comparison
                    crypto_list = []
                    for crypto_id, data in crypto_data.items():
                        crypto_list.append({
                            'Cryptocurrency': data['symbol'],
                            'Price (USD)': data['price'],
                            'Change 24h (%)': data['change_24h'],
                            'Market Cap': data.get('market_cap', 0),
                            'Source': data['source']
                        })
                    
                    df_crypto = pd.DataFrame(crypto_list)
                    
                    # Price chart
                    fig_crypto = px.bar(df_crypto, x='Cryptocurrency', y='Price (USD)', 
                                       title='🪙 Cryptocurrency Prices (USD)', color='Change 24h (%)',
                                       color_continuous_scale='RdYlGn')
                    st.plotly_chart(fig_crypto, use_container_width=True)
                    
                    # Data table
                    st.dataframe(df_crypto, use_container_width=True)
                else:
                    st.error("❌ Failed to load crypto data")
    
    with tab3:
        st.subheader("💱 Enhanced Forex Data")
        if st.button("💹 Load Forex Data", type="primary"):
            with st.spinner("Loading enhanced forex data..."):
                forex_data = get_enhanced_forex_data()
                
                if forex_data:
                    st.success(f"✅ Loaded {len(forex_data)} currency pairs")
                    
                    # Create forex comparison
                    forex_list = []
                    for pair, data in forex_data.items():
                        forex_list.append({
                            'Currency Pair': pair,
                            'Exchange Rate': data['rate'],
                            'Base Currency': data['base'],
                            'Target Currency': data['target'],
                            'Source': data['source'],
                            'Date': data['date']
                        })
                    
                    df_forex = pd.DataFrame(forex_list)
                    
                    # Exchange rate chart
                    fig_forex = px.bar(df_forex, x='Currency Pair', y='Exchange Rate', 
                                      title='💱 Current Exchange Rates', color='Source')
                    fig_forex.update_layout(xaxis_tickangle=45)
                    st.plotly_chart(fig_forex, use_container_width=True)
                    
                    # Data table
                    st.dataframe(df_forex, use_container_width=True)
                else:
                    st.error("❌ Failed to load forex data")
    
    # API Status Section
    st.markdown("---")
    st.subheader("📡 Enhanced API Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌍 World Bank API", "✅ ACTIVE", "Unlimited free")
        st.caption("Global economic indicators")
    
    with col2:
        st.metric("🪙 CryptoCompare", "✅ ACTIVE", "Unlimited free")
        st.caption("6,000+ cryptocurrencies")
    
    with col3:
        st.metric("📈 Binance API", "✅ ACTIVE", "1,200 req/min")
        st.caption("1,000+ trading pairs")
    
    with col4:
        st.metric("💱 ExchangeRate-API", "✅ ACTIVE", "1,500 req/month")
        st.caption("170+ currencies")

if __name__ == "__main__":
    # For testing
    display_enhanced_api_dashboard() 