"""
Quick Examples for Nippon India Small Cap Fund Data Analysis
============================================================

Choose your preferred approach based on your needs:
1. 🟩 Sample NAV data (for testing/demo)
2. 🟦 yfinance proxy indices (real market data)
3. 🟨 Web scraping (advanced, may need updates)
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# =============================================================================
# 🟩 OPTION 1: Sample NAV Data (Quick Start)
# =============================================================================

def create_sample_nav_csv():
    """Create a CSV file with realistic sample NAV data"""
    print("🟩 Creating Sample NAV Data...")
    
    # Generate 6 months of daily NAV data
    dates = pd.date_range(start='2024-07-01', end='2025-01-15', freq='D')
    base_nav = 165.50
    
    # Simulate realistic small-cap fund movements
    np.random.seed(42)
    daily_changes = np.random.normal(0.001, 0.028, len(dates))  # Higher volatility for small-cap
    
    nav_values = [base_nav]
    for change in daily_changes[1:]:
        new_nav = nav_values[-1] * (1 + change)
        nav_values.append(new_nav)
    
    # Create DataFrame
    sample_data = pd.DataFrame({
        'Date': dates,
        'NAV': nav_values,
        'Change': [0] + [nav_values[i] - nav_values[i-1] for i in range(1, len(nav_values))],
        'Change_Pct': [0] + [(nav_values[i] / nav_values[i-1] - 1) * 100 for i in range(1, len(nav_values))]
    })
    
    # Save to CSV
    sample_data.to_csv('nippon_sample_nav.csv', index=False)
    print(f"✅ Sample data saved to 'nippon_sample_nav.csv' ({len(sample_data)} records)")
    
    # Quick preview
    print("\n📊 Sample Data Preview:")
    print(sample_data.head())
    print(f"\nNAV Range: {sample_data['NAV'].min():.2f} - {sample_data['NAV'].max():.2f}")
    print(f"Total Return: {((sample_data['NAV'].iloc[-1] / sample_data['NAV'].iloc[0]) - 1) * 100:.2f}%")
    
    return sample_data

# =============================================================================
# 🟦 OPTION 2: yfinance Proxy Indices (Real Data)
# =============================================================================

def fetch_smallcap_indices():
    """Fetch real small-cap index data as proxy for the fund"""
    print("🟦 Fetching Real Small-Cap Index Data...")
    
    # Available Indian small-cap proxies
    indices = {
        'Nifty Smallcap 250': '^CNXSMCP',
        'BSE SmallCap': '^BSESML',
        'Nifty 50 (Benchmark)': '^NSEI'
    }
    
    results = {}
    
    for name, symbol in indices.items():
        try:
            print(f"📈 Fetching {name} ({symbol})...")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='6mo')
            
            if not hist.empty:
                # Add some useful columns
                hist['Daily_Return'] = hist['Close'].pct_change() * 100
                hist['Symbol'] = symbol
                hist['Index_Name'] = name
                
                results[name] = hist
                print(f"✅ Got {len(hist)} trading days for {name}")
                
                # Quick stats
                total_return = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
                volatility = hist['Daily_Return'].std()
                print(f"   📊 6M Return: {total_return:.2f}%, Volatility: {volatility:.2f}%")
            else:
                print(f"❌ No data found for {name}")
                
        except Exception as e:
            print(f"❌ Error fetching {name}: {str(e)}")
    
    return results

# =============================================================================
# 🟨 OPTION 3: Manual NAV Data Entry Template
# =============================================================================

def create_manual_nav_template():
    """Create a template for manual NAV data entry"""
    print("🟨 Creating Manual NAV Data Template...")
    
    # Create template with sample entries
    template_data = {
        'Date': [
            '2024-12-31', '2024-11-30', '2024-10-31', '2024-09-30',
            '2024-08-31', '2024-07-31', '2024-06-30'
        ],
        'NAV': [
            168.50, 165.20, 162.80, 159.40, 
            156.90, 153.20, 150.80
        ],
        'Notes': [
            'Latest NAV', 'Month-end', 'Month-end', 'Quarter-end',
            'Month-end', 'Month-end', 'Half-year'
        ]
    }
    
    template_df = pd.DataFrame(template_data)
    template_df.to_csv('nippon_manual_nav_template.csv', index=False)
    
    print("✅ Template saved to 'nippon_manual_nav_template.csv'")
    print("\n📝 Instructions:")
    print("1. Visit: https://www.moneycontrol.com/mutual-funds/nav/nippon-india-small-cap-fund-direct-plan-growth/MNS092")
    print("2. Copy historical NAV data")
    print("3. Replace template data with real NAV values")
    print("4. Save and use for analysis")
    
    print("\n📊 Template Preview:")
    print(template_df)
    
    return template_df

# =============================================================================
# 📊 Quick Visualization Function
# =============================================================================

def quick_plot(data, title="Fund Performance", value_col='Close'):
    """Create a quick performance plot"""
    plt.figure(figsize=(12, 6))
    
    if isinstance(data, dict):
        # Multiple series
        for name, df in data.items():
            plt.plot(df.index, df[value_col], label=name, linewidth=2)
        plt.legend()
    else:
        # Single series
        x_col = 'Date' if 'Date' in data.columns else data.index
        plt.plot(data[x_col] if 'Date' in data.columns else data.index, 
                data[value_col], linewidth=2, color='#2E86AB')
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# =============================================================================
# 🚀 Main Demo Function
# =============================================================================

def run_quick_demo():
    """Run a quick demo of all options"""
    print("🚀 Nippon India Small Cap Fund - Quick Examples")
    print("=" * 60)
    
    # Option 1: Sample Data
    print("\n" + "="*20 + " OPTION 1: Sample Data " + "="*20)
    sample_data = create_sample_nav_csv()
    
    # Option 2: Real Index Data
    print("\n" + "="*20 + " OPTION 2: Real Index Data " + "="*20)
    index_data = fetch_smallcap_indices()
    
    # Option 3: Manual Template
    print("\n" + "="*20 + " OPTION 3: Manual Template " + "="*20)
    template_data = create_manual_nav_template()
    
    # Quick visualization if we have data
    if sample_data is not None:
        print("\n📊 Creating Sample Data Visualization...")
        quick_plot(sample_data, "Nippon Small Cap Fund - Sample NAV", 'NAV')
    
    if index_data:
        print("\n📊 Creating Index Comparison...")
        # Plot just the close prices for comparison
        index_closes = {}
        for name, df in index_data.items():
            if not df.empty:
                index_closes[name] = df[['Close']]
        
        if index_closes:
            quick_plot(index_closes, "Small-Cap Indices Comparison", 'Close')
    
    print("\n✅ Quick demo completed!")
    print("\n📁 Files created:")
    print("- nippon_sample_nav.csv (sample NAV data)")
    print("- nippon_manual_nav_template.csv (template for manual entry)")

if __name__ == "__main__":
    run_quick_demo() 