import yfinance as yf
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class NipponFundAnalyzer:
    """
    Comprehensive analyzer for Nippon India Small Cap Fund with multiple data sources
    """
    
    def __init__(self):
        self.fund_name = "Nippon India Small Cap Fund"
        self.proxy_symbols = {
            'nifty_smallcap_250': '^CNXSMCP',
            'nifty_50': '^NSEI',
            'bse_smallcap': '^BSESML'
        }
        self.sample_nav_data = None
        self.proxy_data = {}
        
    def create_sample_nav_data(self, start_date='2023-01-01', periods=180):
        """
        Generate realistic sample NAV data for demonstration
        """
        print("📊 Generating sample NAV data...")
        
        # Base NAV starting point
        base_nav = 160.0
        dates = pd.date_range(start=start_date, periods=periods, freq='D')
        
        # Simulate realistic NAV movements
        np.random.seed(42)  # For reproducible results
        daily_returns = np.random.normal(0.0008, 0.025, periods)  # ~20% annual vol
        
        # Add some trend and seasonality
        trend = np.linspace(0, 0.15, periods)  # 15% growth over period
        seasonality = 0.05 * np.sin(2 * np.pi * np.arange(periods) / 365)
        
        cumulative_returns = np.cumsum(daily_returns + trend/periods + seasonality/periods)
        nav_values = base_nav * np.exp(cumulative_returns)
        
        self.sample_nav_data = pd.DataFrame({
            'Date': dates,
            'NAV': nav_values,
            'Change': np.concatenate([[0], np.diff(nav_values)]),
            'Return_Pct': np.concatenate([[0], np.diff(nav_values) / nav_values[:-1] * 100])
        })
        
        print(f"✅ Generated {len(self.sample_nav_data)} days of sample NAV data")
        return self.sample_nav_data
    
    def fetch_proxy_data(self, symbol_key='nifty_smallcap_250', period='6mo'):
        """
        Fetch proxy index data using yfinance
        """
        try:
            symbol = self.proxy_symbols[symbol_key]
            print(f"📈 Fetching {symbol_key.upper()} data via yfinance...")
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                raise ValueError(f"No data found for {symbol}")
            
            # Process the data
            proxy_df = hist.reset_index()
            proxy_df['Symbol'] = symbol_key
            proxy_df['Daily_Return'] = proxy_df['Close'].pct_change() * 100
            
            self.proxy_data[symbol_key] = proxy_df
            
            print(f"✅ Fetched {len(proxy_df)} trading days for {symbol_key}")
            return proxy_df
            
        except Exception as e:
            print(f"❌ Error fetching {symbol_key}: {str(e)}")
            return None
    
    def scrape_moneycontrol_nav(self, scheme_code="MNS092"):
        """
        Attempt to scrape NAV data from Moneycontrol
        Note: This is a basic implementation - real scraping may need headers, sessions, etc.
        """
        try:
            print("🌐 Attempting to scrape NAV data from Moneycontrol...")
            
            url = f"https://www.moneycontrol.com/mutual-funds/nav/nippon-india-small-cap-fund-direct-plan-growth/{scheme_code}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=1800)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # This is a basic attempt - real implementation would need to parse the actual HTML structure
                print("⚠️  Web scraping requires specific HTML parsing based on Moneycontrol's current structure")
                print("💡 For production use, consider using official APIs or manual CSV data")
                
                return None
            else:
                print(f"❌ Failed to fetch data: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Scraping error: {str(e)}")
            return None
    
    def save_sample_data_to_csv(self, filename="nippon_sample_nav.csv"):
        """
        Save sample NAV data to CSV for external use
        """
        if self.sample_nav_data is not None:
            self.sample_nav_data.to_csv(filename, index=False)
            print(f"💾 Sample NAV data saved to {filename}")
        else:
            print("❌ No sample data to save. Generate sample data first.")
    
    def analyze_performance(self, data_source='sample'):
        """
        Perform comprehensive performance analysis
        """
        if data_source == 'sample' and self.sample_nav_data is not None:
            df = self.sample_nav_data.copy()
            value_col = 'NAV'
        elif data_source in self.proxy_data:
            df = self.proxy_data[data_source].copy()
            value_col = 'Close'
        else:
            print("❌ No data available for analysis")
            return None
        
        print(f"\n📊 Performance Analysis ({data_source.upper()})")
        print("=" * 50)
        
        # Basic statistics
        current_value = df[value_col].iloc[-1]
        start_value = df[value_col].iloc[0]
        total_return = ((current_value / start_value) - 1) * 100
        
        # Volatility
        if 'Return_Pct' in df.columns:
            volatility = df['Return_Pct'].std()
        else:
            returns = df[value_col].pct_change().dropna() * 100
            volatility = returns.std()
        
        # Max drawdown
        rolling_max = df[value_col].expanding().max()
        drawdown = (df[value_col] / rolling_max - 1) * 100
        max_drawdown = drawdown.min()
        
        print(f"Current Value: {current_value:.2f}")
        print(f"Total Return: {total_return:.2f}%")
        print(f"Volatility: {volatility:.2f}%")
        print(f"Max Drawdown: {max_drawdown:.2f}%")
        
        return {
            'total_return': total_return,
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'current_value': current_value
        }
    
    def create_visualizations(self, data_source='sample'):
        """
        Create comprehensive visualizations
        """
        if data_source == 'sample' and self.sample_nav_data is not None:
            df = self.sample_nav_data.copy()
            value_col = 'NAV'
            title_suffix = "Sample NAV Data"
        elif data_source in self.proxy_data:
            df = self.proxy_data[data_source].copy()
            value_col = 'Close'
            title_suffix = f"{data_source.upper()} Index"
        else:
            print("❌ No data available for visualization")
            return
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'{self.fund_name} Analysis - {title_suffix}', fontsize=16, fontweight='bold')
        
        # 1. Price/NAV Chart
        axes[0, 0].plot(df['Date'] if 'Date' in df.columns else df.index, df[value_col], linewidth=2, color='#2E86AB')
        axes[0, 0].set_title('NAV/Price Trend')
        axes[0, 0].set_ylabel('Value')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Returns Distribution
        if 'Return_Pct' in df.columns:
            returns = df['Return_Pct'].dropna()
        else:
            returns = df[value_col].pct_change().dropna() * 100
        
        axes[0, 1].hist(returns, bins=30, alpha=0.7, color='#A23B72', edgecolor='black')
        axes[0, 1].set_title('Daily Returns Distribution')
        axes[0, 1].set_xlabel('Daily Return (%)')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Rolling Volatility
        rolling_vol = returns.rolling(window=30).std()
        axes[1, 0].plot(df['Date'][-len(rolling_vol):] if 'Date' in df.columns else df.index[-len(rolling_vol):], 
                       rolling_vol, color='#F18F01', linewidth=2)
        axes[1, 0].set_title('30-Day Rolling Volatility')
        axes[1, 0].set_ylabel('Volatility (%)')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Drawdown Chart
        rolling_max = df[value_col].expanding().max()
        drawdown = (df[value_col] / rolling_max - 1) * 100
        axes[1, 1].fill_between(df['Date'] if 'Date' in df.columns else df.index, 
                               drawdown, 0, alpha=0.6, color='#C73E1D')
        axes[1, 1].set_title('Drawdown')
        axes[1, 1].set_ylabel('Drawdown (%)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Interactive Plotly chart
        fig_plotly = go.Figure()
        fig_plotly.add_trace(go.Scatter(
            x=df['Date'] if 'Date' in df.columns else df.index,
            y=df[value_col],
            mode='lines',
            name=value_col,
            line=dict(color='#2E86AB', width=2)
        ))
        
        fig_plotly.update_layout(
            title=f'{self.fund_name} - {title_suffix}',
            xaxis_title='Date',
            yaxis_title='Value',
            template='plotly_white',
            height=500
        )
        
        fig_plotly.show()

# Demo usage functions
def demo_all_options():
    """
    Demonstrate all three data fetching options
    """
    analyzer = NipponFundAnalyzer()
    
    print("🚀 Nippon India Small Cap Fund Analyzer Demo")
    print("=" * 60)
    
    # Option 1: Sample NAV Data
    print("\n🟩 OPTION 1: Sample NAV Data")
    sample_data = analyzer.create_sample_nav_data()
    analyzer.save_sample_data_to_csv()
    analyzer.analyze_performance('sample')
    
    # Option 2: Proxy Index Data
    print("\n🟦 OPTION 2: Proxy Index Data (Nifty Smallcap 250)")
    proxy_data = analyzer.fetch_proxy_data('nifty_smallcap_250', period='6mo')
    if proxy_data is not None:
        analyzer.analyze_performance('nifty_smallcap_250')
    
    # Option 3: Web Scraping Attempt
    print("\n🟨 OPTION 3: Web Scraping (Moneycontrol)")
    scraped_data = analyzer.scrape_moneycontrol_nav()
    
    # Visualizations
    print("\n📊 Creating Visualizations...")
    analyzer.create_visualizations('sample')
    
    return analyzer

if __name__ == "__main__":
    # Run the demo
    analyzer = demo_all_options()
    
    print("\n✅ Demo completed!")
    print("\nNext steps:")
    print("1. Install requirements: pip install -r requirements.txt")
    print("2. Run this script: python nippon_fund_analyzer.py")
    print("3. Check generated CSV file for sample data")
    print("4. Modify the code for your specific needs") 