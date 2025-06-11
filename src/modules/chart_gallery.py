import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 🎨 Chart Gallery - Professional Financial Visualizations

def create_market_overview_dashboard():
    """Create comprehensive market overview with multiple charts"""
    st.header("📊 Live Market Dashboard")
    
    # Major indices data
    indices = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC", 
        "Dow Jones": "^DJI",
        "Nifty 50": "^NSEI"
    }
    
    # Create 2x2 grid for mini charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Major Indices")
        for name, symbol in list(indices.items())[:2]:
            create_mini_price_chart(symbol, name)
    
    with col2:
        st.subheader("🌍 Global Markets")
        for name, symbol in list(indices.items())[2:]:
            create_mini_price_chart(symbol, name)

def create_mini_price_chart(symbol, name):
    """Create mini price chart for dashboard"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="5d")
        
        if data.empty:
            st.warning(f"No data for {name}")
            return
        
        # Calculate change
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
        change_pct = ((current_price - prev_price) / prev_price) * 100
        
        # Color based on change
        color = '#00ff88' if change_pct >= 0 else '#ff4444'
        
        # Create mini chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            line=dict(color=color, width=3),
            showlegend=False
        ))
        
        fig.update_layout(
            title=f"{name}: ${current_price:.2f} ({change_pct:+.2f}%)",
            height=200,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False),
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading {name}: {str(e)}")

def create_advanced_candlestick_chart():
    """Advanced candlestick chart with technical indicators"""
    st.header("📈 Advanced Stock Analysis")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        symbol = st.text_input("Enter Stock Symbol:", value="AAPL", key="candlestick_symbol")
    with col2:
        period = st.selectbox("Time Period:", ["1mo", "3mo", "6mo", "1y"], key="candlestick_period")
    with col3:
        indicators = st.multiselect("Technical Indicators:", 
                                  ["Moving Averages", "Bollinger Bands", "Volume"], 
                                  default=["Moving Averages"])
    
    if st.button("📊 Generate Advanced Chart", type="primary"):
        with st.spinner(f"Loading {symbol} data..."):
            fig = create_candlestick_with_indicators(symbol, period, indicators)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

def create_candlestick_with_indicators(symbol, period, indicators):
    """Create candlestick chart with selected technical indicators"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            st.error(f"No data available for {symbol}")
            return None
        
        # Calculate technical indicators
        if "Moving Averages" in indicators:
            data['MA20'] = data['Close'].rolling(window=20).mean()
            data['MA50'] = data['Close'].rolling(window=50).mean()
        
        if "Bollinger Bands" in indicators:
            data['BB_Middle'] = data['Close'].rolling(window=20).mean()
            data['BB_Std'] = data['Close'].rolling(window=20).std()
            data['BB_Upper'] = data['BB_Middle'] + (data['BB_Std'] * 2)
            data['BB_Lower'] = data['BB_Middle'] - (data['BB_Std'] * 2)
        
        # Create subplots
        rows = 2 if "Volume" in indicators else 1
        fig = make_subplots(
            rows=rows, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=[f'{symbol} Price Chart'] + (['Volume'] if "Volume" in indicators else []),
            row_heights=[0.7, 0.3] if rows == 2 else [1]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=symbol,
                increasing_line_color='#00ff88',
                decreasing_line_color='#ff4444'
            ),
            row=1, col=1
        )
        
        # Add technical indicators
        if "Moving Averages" in indicators:
            fig.add_trace(
                go.Scatter(x=data.index, y=data['MA20'], name='MA 20',
                          line=dict(color='orange', width=2)),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=data.index, y=data['MA50'], name='MA 50',
                          line=dict(color='blue', width=2)),
                row=1, col=1
            )
        
        if "Bollinger Bands" in indicators:
            fig.add_trace(
                go.Scatter(x=data.index, y=data['BB_Upper'], name='BB Upper',
                          line=dict(color='gray', width=1), opacity=0.7),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=data.index, y=data['BB_Lower'], name='BB Lower',
                          line=dict(color='gray', width=1), opacity=0.7,
                          fill='tonexty', fillcolor='rgba(128,128,128,0.1)'),
                row=1, col=1
            )
        
        # Volume
        if "Volume" in indicators:
            fig.add_trace(
                go.Bar(x=data.index, y=data['Volume'], name='Volume',
                       marker_color='rgba(0,100,200,0.7)'),
                row=2, col=1
            )
        
        fig.update_layout(
            title=f"{symbol} - Advanced Technical Analysis",
            template='plotly_white',
            height=700 if "Volume" in indicators else 500,
            xaxis_rangeslider_visible=False,
            showlegend=True
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        return None

def create_crypto_dashboard():
    """Create cryptocurrency dashboard"""
    st.header("₿ Cryptocurrency Dashboard")
    
    cryptos = {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD", 
        "Binance Coin": "BNB-USD",
        "Cardano": "ADA-USD"
    }
    
    # Create grid layout
    cols = st.columns(2)
    
    for i, (name, symbol) in enumerate(cryptos.items()):
        with cols[i % 2]:
            create_crypto_mini_chart(symbol, name)

def create_crypto_mini_chart(symbol, name):
    """Create mini crypto chart"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="7d")
        
        if data.empty:
            st.warning(f"No data for {name}")
            return
        
        current_price = data['Close'].iloc[-1]
        change_pct = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
        
        color = '#00ff88' if change_pct >= 0 else '#ff4444'
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            line=dict(color=color, width=3),
            fill='tonexty',
            fillcolor=f'rgba({255 if change_pct < 0 else 0}, {255 if change_pct >= 0 else 0}, 0, 0.1)'
        ))
        
        fig.update_layout(
            title=f"{name}: ${current_price:.2f} ({change_pct:+.1f}%)",
            height=250,
            margin=dict(l=0, r=0, t=30, b=0),
            template='plotly_white',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading {name}")

def create_correlation_matrix():
    """Create stock correlation heatmap"""
    st.header("🔥 Stock Correlation Analysis")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        symbols = st.text_area(
            "Enter stock symbols (comma-separated):",
            value="AAPL,GOOGL,MSFT,TSLA,AMZN,META,NVDA",
            height=100
        )
    with col2:
        period = st.selectbox("Analysis Period:", ["3mo", "6mo", "1y", "2y"])
    
    if st.button("🔍 Generate Correlation Matrix", type="primary"):
        symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
        
        with st.spinner("Calculating correlations..."):
            fig = create_correlation_heatmap(symbol_list, period)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                # Add insights
                st.subheader("📈 Correlation Insights")
                st.info("""
                **Reading the Heatmap:**
                - 🟢 **Green (close to 1)**: Stocks move together
                - 🔴 **Red (close to -1)**: Stocks move opposite  
                - ⚪ **White (close to 0)**: No correlation
                
                **Diversification Tip:** Choose stocks with low correlation (closer to 0) for better portfolio diversification!
                """)

def create_correlation_heatmap(symbols, period):
    """Create correlation heatmap"""
    try:
        data = {}
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if not hist.empty:
                data[symbol] = hist['Close']
        
        if len(data) < 2:
            st.error("Need at least 2 valid symbols for correlation analysis")
            return None
        
        df = pd.DataFrame(data)
        correlation_matrix = df.corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.round(3).values,
            texttemplate="%{text}",
            textfont={"size": 10, "color": "white"},
            hoverongaps=False,
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title="Stock Correlation Matrix",
            template='plotly_white',
            height=600,
            width=600
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating correlation matrix: {str(e)}")
        return None

def create_portfolio_treemap():
    """Create portfolio allocation treemap"""
    st.header("🌳 Portfolio Allocation Treemap")
    
    # Sample portfolio data
    portfolio_data = {
        'Technology': {'AAPL': 25, 'GOOGL': 15, 'MSFT': 20, 'NVDA': 10},
        'Healthcare': {'JNJ': 8, 'PFE': 5, 'UNH': 7},
        'Finance': {'JPM': 6, 'BAC': 4}
    }
    
    # Prepare data for treemap
    sectors = []
    stocks = []
    allocations = []
    colors = []
    
    sector_colors = {'Technology': '#4285f4', 'Healthcare': '#34a853', 'Finance': '#fbbc04'}
    
    for sector, stocks_dict in portfolio_data.items():
        for stock, allocation in stocks_dict.items():
            sectors.append(sector)
            stocks.append(stock)
            allocations.append(allocation)
            colors.append(sector_colors.get(sector, '#9aa0a6'))
    
    # Create treemap
    fig = go.Figure(go.Treemap(
        labels=stocks,
        parents=sectors,
        values=allocations,
        textinfo="label+value+percent parent",
        hovertemplate='<b>%{label}</b><br>Allocation: %{value}%<br>Sector: %{parent}<extra></extra>',
        marker_colors=colors
    ))
    
    fig.update_layout(
        title="Portfolio Allocation by Sector",
        template='plotly_white',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add portfolio summary
    total_allocation = sum(allocations)
    st.metric("Total Portfolio", f"{total_allocation}%", 
              delta=f"{100-total_allocation}% remaining" if total_allocation < 100 else "Fully allocated")

def create_risk_return_scatter():
    """Create risk-return scatter plot"""
    st.header("⚡ Risk vs Return Analysis")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        symbols = st.text_area(
            "Enter stocks to analyze:",
            value="AAPL,GOOGL,MSFT,TSLA,AMZN,SPY",
            height=80
        )
    with col2:
        period = st.selectbox("Analysis Period:", ["6mo", "1y", "2y"], key="risk_period")
    
    if st.button("📊 Generate Risk-Return Plot", type="primary"):
        symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
        
        with st.spinner("Analyzing risk and returns..."):
            fig = create_risk_return_plot(symbol_list, period)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

def create_risk_return_plot(symbols, period):
    """Create risk-return scatter plot"""
    try:
        risk_return_data = []
        
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if not hist.empty:
                returns = hist['Close'].pct_change().dropna()
                annual_return = returns.mean() * 252 * 100
                annual_volatility = returns.std() * np.sqrt(252) * 100
                sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
                
                risk_return_data.append({
                    'Symbol': symbol,
                    'Return': annual_return,
                    'Risk': annual_volatility,
                    'Sharpe': sharpe_ratio
                })
        
        if not risk_return_data:
            st.error("No valid data for analysis")
            return None
        
        df = pd.DataFrame(risk_return_data)
        
        # Create scatter plot
        fig = px.scatter(
            df, x='Risk', y='Return',
            text='Symbol',
            color='Sharpe',
            size='Sharpe',
            title='Risk vs Return Analysis (Annualized)',
            labels={'Risk': 'Annual Volatility (%)', 'Return': 'Annual Return (%)'},
            color_continuous_scale='RdYlGn',
            hover_data={'Sharpe': ':.3f'}
        )
        
        fig.update_traces(textposition="top center", textfont_size=12)
        fig.update_layout(
            template='plotly_white',
            height=500,
            showlegend=False
        )
        
        # Add quadrant lines
        avg_risk = df['Risk'].mean()
        avg_return = df['Return'].mean()
        
        fig.add_hline(y=avg_return, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=avg_risk, line_dash="dash", line_color="gray", opacity=0.5)
        
        return fig
    except Exception as e:
        st.error(f"Error creating risk-return plot: {str(e)}")
        return None

def render_chart_gallery():
    """Main function to render the complete chart gallery"""
    st.title("📊 Professional Chart Gallery")
    
    # Sidebar for chart selection
    st.sidebar.header("📈 Chart Selection")
    chart_category = st.sidebar.selectbox(
        "Choose Chart Category:",
        [
            "🌟 Market Overview",
            "📈 Advanced Stock Charts", 
            "₿ Cryptocurrency Dashboard",
            "🔥 Correlation Analysis",
            "🌳 Portfolio Visualization",
            "⚡ Risk Analysis"
        ]
    )
    
    # Render selected chart category
    if chart_category == "🌟 Market Overview":
        create_market_overview_dashboard()
        
    elif chart_category == "📈 Advanced Stock Charts":
        create_advanced_candlestick_chart()
        
    elif chart_category == "₿ Cryptocurrency Dashboard":
        create_crypto_dashboard()
        
    elif chart_category == "🔥 Correlation Analysis":
        create_correlation_matrix()
        
    elif chart_category == "🌳 Portfolio Visualization":
        create_portfolio_treemap()
        
    elif chart_category == "⚡ Risk Analysis":
        create_risk_return_scatter()
    
    # Add chart tips
    with st.expander("💡 Chart Tips & Insights"):
        st.markdown("""
        ### 📊 How to Read These Charts:
        
        **📈 Candlestick Charts:**
        - Green candles = Price went up
        - Red candles = Price went down
        - Wicks show high/low prices
        
        **🔥 Correlation Matrix:**
        - Values close to 1 = Stocks move together
        - Values close to -1 = Stocks move opposite
        - Values close to 0 = No relationship
        
        **⚡ Risk-Return Plot:**
        - Top-left quadrant = High return, low risk (ideal!)
        - Bottom-right = Low return, high risk (avoid!)
        
        **💡 Pro Tip:** Use these charts to make better investment decisions!
        """)

if __name__ == "__main__":
    render_chart_gallery() 