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

class AdvancedChartCreator:
    """Advanced financial chart creator with professional-grade visualizations"""
    
    def __init__(self):
        self.color_palette = {
            'bullish': '#00ff88',
            'bearish': '#ff4444', 
            'neutral': '#4285f4',
            'background': '#ffffff',
            'text': '#2c3e50'
        }
    
    def create_candlestick_chart(self, symbol="AAPL", period="3mo"):
        """Create professional candlestick chart with volume"""
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                st.warning(f"No data available for {symbol}")
                return None
            
            # Create subplot with secondary y-axis
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=(f'{symbol} Price Chart', 'Volume'),
                row_width=[0.7, 0.3]
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
                    increasing_line_color=self.color_palette['bullish'],
                    decreasing_line_color=self.color_palette['bearish']
                ),
                row=1, col=1
            )
            
            # Volume bars
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['Volume'],
                    name='Volume',
                    marker_color=self.color_palette['neutral'],
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                title=f"{symbol} - Candlestick Chart with Volume",
                template='plotly_white',
                height=600,
                xaxis_rangeslider_visible=False,
                showlegend=False
            )
            
            return fig
        except Exception as e:
            st.error(f"Error creating candlestick chart: {str(e)}")
            return None
    
    def create_technical_indicators_chart(self, symbol="AAPL", period="6mo"):
        """Create chart with moving averages and RSI"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                st.warning(f"No data available for {symbol}")
                return None
            
            # Calculate technical indicators
            data['MA20'] = data['Close'].rolling(window=20).mean()
            data['MA50'] = data['Close'].rolling(window=50).mean()
            
            # RSI calculation
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # Create subplot
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=(f'{symbol} Price with Moving Averages', 'RSI (14)'),
                row_heights=[0.7, 0.3]
            )
            
            # Price and moving averages
            fig.add_trace(
                go.Scatter(x=data.index, y=data['Close'], name='Close Price',
                          line=dict(color=self.color_palette['neutral'], width=2)),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=data.index, y=data['MA20'], name='MA 20',
                          line=dict(color=self.color_palette['bullish'], width=1.5)),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=data.index, y=data['MA50'], name='MA 50',
                          line=dict(color=self.color_palette['bearish'], width=1.5)),
                row=1, col=1
            )
            
            # RSI
            fig.add_trace(
                go.Scatter(x=data.index, y=data['RSI'], name='RSI',
                          line=dict(color='purple', width=2)),
                row=2, col=1
            )
            
            # Add RSI reference lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            
            fig.update_layout(
                title=f"{symbol} - Technical Analysis",
                template='plotly_white',
                height=700,
                showlegend=True
            )
            
            return fig
        except Exception as e:
            st.error(f"Error creating technical indicators chart: {str(e)}")
            return None
    
    def create_correlation_heatmap(self, symbols=["AAPL", "GOOGL", "MSFT", "TSLA"], period="1y"):
        """Create correlation heatmap for multiple stocks"""
        try:
            # Fetch data for all symbols
            data = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                if not hist.empty:
                    data[symbol] = hist['Close']
            
            if not data:
                st.warning("No data available for correlation analysis")
                return None
            
            # Create DataFrame and calculate correlation
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
                textfont={"size": 12},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title="Stock Correlation Heatmap",
                template='plotly_white',
                height=500,
                width=500
            )
            
            return fig
        except Exception as e:
            st.error(f"Error creating correlation heatmap: {str(e)}")
            return None
    
    def create_portfolio_performance_chart(self, portfolio_data):
        """Create comprehensive portfolio performance chart"""
        try:
            if not portfolio_data:
                return None
            
            # Sample portfolio performance data
            dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
            np.random.seed(42)
            
            # Generate realistic portfolio performance
            returns = np.random.normal(0.0008, 0.02, len(dates))  # Daily returns
            portfolio_value = [100000]  # Starting value
            
            for return_rate in returns[1:]:
                new_value = portfolio_value[-1] * (1 + return_rate)
                portfolio_value.append(new_value)
            
            # Benchmark (S&P 500 proxy)
            benchmark_returns = np.random.normal(0.0005, 0.015, len(dates))
            benchmark_value = [100000]
            
            for return_rate in benchmark_returns[1:]:
                new_value = benchmark_value[-1] * (1 + return_rate)
                benchmark_value.append(new_value)
            
            # Create figure
            fig = go.Figure()
            
            # Portfolio line
            fig.add_trace(go.Scatter(
                x=dates,
                y=portfolio_value,
                mode='lines',
                name='Your Portfolio',
                line=dict(color=self.color_palette['bullish'], width=3),
                hovertemplate='Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>'
            ))
            
            # Benchmark line
            fig.add_trace(go.Scatter(
                x=dates,
                y=benchmark_value,
                mode='lines',
                name='S&P 500 Benchmark',
                line=dict(color=self.color_palette['neutral'], width=2, dash='dash'),
                hovertemplate='Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>'
            ))
            
            # Calculate and add performance metrics
            final_portfolio = portfolio_value[-1]
            final_benchmark = benchmark_value[-1]
            portfolio_return = ((final_portfolio / 100000) - 1) * 100
            benchmark_return = ((final_benchmark / 100000) - 1) * 100
            
            fig.update_layout(
                title=f"Portfolio Performance vs Benchmark<br>" +
                      f"<span style='font-size:14px'>Portfolio: {portfolio_return:.1f}% | " +
                      f"Benchmark: {benchmark_return:.1f}% | " +
                      f"Alpha: {portfolio_return - benchmark_return:.1f}%</span>",
                xaxis_title='Date',
                yaxis_title='Portfolio Value ($)',
                template='plotly_white',
                height=500,
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            st.error(f"Error creating portfolio performance chart: {str(e)}")
            return None
    
    def create_risk_return_scatter(self, symbols=["AAPL", "GOOGL", "MSFT", "TSLA", "SPY"], period="1y"):
        """Create risk-return scatter plot"""
        try:
            risk_return_data = []
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                
                if not hist.empty:
                    # Calculate returns and risk
                    returns = hist['Close'].pct_change().dropna()
                    annual_return = returns.mean() * 252 * 100  # Annualized
                    annual_volatility = returns.std() * np.sqrt(252) * 100  # Annualized
                    
                    risk_return_data.append({
                        'Symbol': symbol,
                        'Return': annual_return,
                        'Risk': annual_volatility,
                        'Sharpe': annual_return / annual_volatility if annual_volatility > 0 else 0
                    })
            
            if not risk_return_data:
                st.warning("No data available for risk-return analysis")
                return None
            
            df = pd.DataFrame(risk_return_data)
            
            # Create scatter plot
            fig = px.scatter(
                df, x='Risk', y='Return',
                text='Symbol',
                color='Sharpe',
                size='Sharpe',
                title='Risk-Return Analysis',
                labels={'Risk': 'Annual Volatility (%)', 'Return': 'Annual Return (%)'},
                color_continuous_scale='RdYlGn'
            )
            
            fig.update_traces(textposition="top center")
            fig.update_layout(
                template='plotly_white',
                height=500,
                showlegend=False
            )
            
            # Add efficient frontier line (simplified)
            x_range = np.linspace(df['Risk'].min(), df['Risk'].max(), 100)
            efficient_frontier = 0.5 * x_range + 2  # Simplified curve
            
            fig.add_trace(go.Scatter(
                x=x_range,
                y=efficient_frontier,
                mode='lines',
                name='Efficient Frontier',
                line=dict(color='red', dash='dash', width=2)
            ))
            
            return fig
        except Exception as e:
            st.error(f"Error creating risk-return scatter: {str(e)}")
            return None
    
    def create_sector_allocation_sunburst(self):
        """Create sector allocation sunburst chart"""
        try:
            # Sample sector allocation data
            data = {
                'Technology': {'AAPL': 25, 'GOOGL': 15, 'MSFT': 20},
                'Healthcare': {'JNJ': 10, 'PFE': 8, 'UNH': 7},
                'Financial': {'JPM': 8, 'BAC': 5, 'WFC': 2}
            }
            
            # Prepare data for sunburst
            ids = []
            labels = []
            parents = []
            values = []
            
            # Add sectors
            for sector, stocks in data.items():
                ids.append(sector)
                labels.append(sector)
                parents.append("")
                values.append(sum(stocks.values()))
                
                # Add stocks
                for stock, allocation in stocks.items():
                    ids.append(f"{sector}-{stock}")
                    labels.append(stock)
                    parents.append(sector)
                    values.append(allocation)
            
            # Create sunburst chart
            fig = go.Figure(go.Sunburst(
                ids=ids,
                labels=labels,
                parents=parents,
                values=values,
                branchvalues="total",
                hovertemplate='<b>%{label}</b><br>Allocation: %{value}%<extra></extra>',
                maxdepth=2
            ))
            
            fig.update_layout(
                title="Portfolio Sector Allocation",
                template='plotly_white',
                height=500
            )
            
            return fig
        except Exception as e:
            st.error(f"Error creating sunburst chart: {str(e)}")
            return None

def render_advanced_charts_section():
    """Render the advanced charts section in Streamlit"""
    st.header("📊 Advanced Financial Charts")
    
    chart_creator = AdvancedChartCreator()
    
    # Chart selection
    chart_type = st.selectbox(
        "Select Chart Type:",
        [
            "📈 Candlestick Chart",
            "🔧 Technical Indicators", 
            "🔥 Correlation Heatmap",
            "💼 Portfolio Performance",
            "⚡ Risk-Return Analysis",
            "🌟 Sector Allocation"
        ]
    )
    
    if chart_type == "📈 Candlestick Chart":
        col1, col2 = st.columns([2, 1])
        with col1:
            symbol = st.text_input("Stock Symbol:", value="AAPL")
        with col2:
            period = st.selectbox("Period:", ["1mo", "3mo", "6mo", "1y", "2y"])
        
        if st.button("Generate Candlestick Chart", type="primary"):
            with st.spinner("Creating candlestick chart..."):
                fig = chart_creator.create_candlestick_chart(symbol, period)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "🔧 Technical Indicators":
        col1, col2 = st.columns([2, 1])
        with col1:
            symbol = st.text_input("Stock Symbol:", value="AAPL", key="tech_symbol")
        with col2:
            period = st.selectbox("Period:", ["3mo", "6mo", "1y", "2y"], key="tech_period")
        
        if st.button("Generate Technical Chart", type="primary"):
            with st.spinner("Creating technical indicators chart..."):
                fig = chart_creator.create_technical_indicators_chart(symbol, period)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "🔥 Correlation Heatmap":
        symbols = st.text_area(
            "Stock Symbols (comma-separated):",
            value="AAPL,GOOGL,MSFT,TSLA,AMZN"
        ).split(',')
        symbols = [s.strip().upper() for s in symbols if s.strip()]
        
        period = st.selectbox("Period:", ["6mo", "1y", "2y"], key="corr_period")
        
        if st.button("Generate Correlation Heatmap", type="primary"):
            with st.spinner("Creating correlation heatmap..."):
                fig = chart_creator.create_correlation_heatmap(symbols, period)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "💼 Portfolio Performance":
        if st.button("Generate Portfolio Performance Chart", type="primary"):
            with st.spinner("Creating portfolio performance chart..."):
                fig = chart_creator.create_portfolio_performance_chart({})
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "⚡ Risk-Return Analysis":
        symbols = st.text_area(
            "Stock Symbols for Analysis:",
            value="AAPL,GOOGL,MSFT,TSLA,SPY",
            key="risk_symbols"
        ).split(',')
        symbols = [s.strip().upper() for s in symbols if s.strip()]
        
        if st.button("Generate Risk-Return Analysis", type="primary"):
            with st.spinner("Creating risk-return scatter plot..."):
                fig = chart_creator.create_risk_return_scatter(symbols)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "🌟 Sector Allocation":
        if st.button("Generate Sector Allocation Chart", type="primary"):
            with st.spinner("Creating sector allocation sunburst..."):
                fig = chart_creator.create_sector_allocation_sunburst()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

# Quick chart functions for easy integration
def quick_candlestick_chart(symbol="AAPL", period="3mo"):
    """Quick function to create candlestick chart"""
    creator = AdvancedChartCreator()
    return creator.create_candlestick_chart(symbol, period)

def quick_technical_chart(symbol="AAPL", period="6mo"):
    """Quick function to create technical indicators chart"""
    creator = AdvancedChartCreator()
    return creator.create_technical_indicators_chart(symbol, period)

def quick_correlation_heatmap(symbols=["AAPL", "GOOGL", "MSFT", "TSLA"]):
    """Quick function to create correlation heatmap"""
    creator = AdvancedChartCreator()
    return creator.create_correlation_heatmap(symbols) 