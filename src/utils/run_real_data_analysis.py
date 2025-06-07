#!/usr/bin/env python3
"""
Quick Script to Analyze Real NAV Data
====================================

This script demonstrates how to use the real NAV data with our
existing Nippon Fund Analyzer tools and Streamlit app.
"""

import pandas as pd
from nippon_fund_analyzer import NipponFundAnalyzer
import matplotlib.pyplot as plt

def quick_real_data_analysis():
    """Quick analysis using the NipponFundAnalyzer class"""
    
    print("🚀 Quick Real NAV Data Analysis")
    print("=" * 40)
    
    # Initialize analyzer
    analyzer = NipponFundAnalyzer()
    
    # Load real data
    print("📊 Loading real NAV data...")
    try:
        real_data = pd.read_csv('real_nav_data.csv')
        real_data['Date'] = pd.to_datetime(real_data['Date'])
        
        # Convert to the format expected by the analyzer
        real_data = real_data.rename(columns={'NAV': 'Close'})
        real_data = real_data.set_index('Date')
        
        print(f"✅ Loaded {len(real_data)} records")
        
        # Calculate metrics using the existing analyzer
        metrics = analyzer.calculate_performance_metrics(real_data)
        
        # Print summary
        print("\n📈 PERFORMANCE SUMMARY")
        print("-" * 30)
        for key, value in metrics.items():
            if isinstance(value, float):
                if 'return' in key.lower() or 'volatility' in key.lower():
                    print(f"{key.replace('_', ' ').title()}: {value:.2f}%")
                else:
                    print(f"{key.replace('_', ' ').title()}: {value:.4f}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Create visualizations
        print("\n📊 Creating charts...")
        analyzer.create_interactive_charts(real_data, "Real NAV Data Analysis")
        
        return real_data, metrics
        
    except FileNotFoundError:
        print("❌ real_nav_data.csv not found. Please run the main analysis first.")
        return None, None

def compare_with_benchmark():
    """Compare real data with benchmark indices"""
    
    print("\n🔍 Comparing with Benchmark Indices...")
    
    analyzer = NipponFundAnalyzer()
    
    # Fetch benchmark data
    indices = {
        '^CNXSMCP': 'Nifty SmallCap 250',
        '^BSESML': 'BSE SmallCap',
        '^NSEI': 'Nifty 50'
    }
    
    print("📥 Fetching benchmark data...")
    for symbol, name in indices.items():
        try:
            data = analyzer.fetch_proxy_data(symbol, period='6mo')
            if data is not None:
                metrics = analyzer.calculate_performance_metrics(data)
                print(f"\n{name} ({symbol}):")
                print(f"  Total Return: {metrics.get('total_return', 0):.2f}%")
                print(f"  Volatility: {metrics.get('volatility', 0):.2f}%")
                print(f"  Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
        except Exception as e:
            print(f"❌ Could not fetch {name}: {str(e)}")

def streamlit_instructions():
    """Provide instructions for using Streamlit app with real data"""
    
    print("\n🖥️  STREAMLIT APP INSTRUCTIONS")
    print("=" * 40)
    print("To analyze your real NAV data in the web interface:")
    print()
    print("1. Run the Streamlit app:")
    print("   streamlit run streamlit_app.py")
    print()
    print("2. In the sidebar, select 'Manual NAV Data Entry'")
    print()
    print("3. Upload the 'real_nav_data.csv' file using the file uploader")
    print()
    print("4. The app will automatically process and display:")
    print("   - Interactive charts")
    print("   - Performance metrics")
    print("   - Risk analysis")
    print("   - Benchmark comparisons")
    print()
    print("5. You can export results and generate reports")

def main():
    """Main function"""
    
    # Run quick analysis
    data, metrics = quick_real_data_analysis()
    
    if data is not None:
        # Compare with benchmarks
        compare_with_benchmark()
        
        # Provide Streamlit instructions
        streamlit_instructions()
        
        print("\n✅ Analysis complete!")
        print("\nGenerated files:")
        print("- real_nav_data.csv (your data)")
        print("- nav_analysis_report.txt (detailed report)")
        print("- nav_data_with_analysis.csv (data with calculations)")
        
        print("\nNext steps:")
        print("1. Review the generated report and charts")
        print("2. Use the Streamlit app for interactive analysis")
        print("3. Compare with benchmark indices over time")
        print("4. Consider the insights for investment decisions")

if __name__ == "__main__":
    main() 