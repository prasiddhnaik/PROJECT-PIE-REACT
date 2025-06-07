#!/usr/bin/env python3
"""
Real NAV Data Analysis for Mutual Fund
=====================================

Analyze the real NAV data provided (Jan 2025 - May 2025)
with comprehensive performance metrics and visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import seaborn as sns

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_and_analyze_real_data():
    """Load and perform comprehensive analysis of real NAV data"""
    
    print("📊 Loading Real NAV Data...")
    
    # Load the data
    try:
        df = pd.read_csv('real_nav_data.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        
        print(f"✅ Loaded {len(df)} NAV records from {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
        
    except FileNotFoundError:
        print("❌ real_nav_data.csv not found. Please ensure the file exists.")
        return None
    
    # Calculate additional metrics
    df['Daily_Change'] = df['NAV'].diff()
    df['Daily_Return'] = df['NAV'].pct_change() * 100
    df['Cumulative_Return'] = ((df['NAV'] / df['NAV'].iloc[0]) - 1) * 100
    
    # Rolling statistics
    df['MA_7'] = df['NAV'].rolling(window=7).mean()
    df['MA_21'] = df['NAV'].rolling(window=21).mean()
    df['Rolling_Vol_7'] = df['Daily_Return'].rolling(window=7).std()
    df['Rolling_Vol_21'] = df['Daily_Return'].rolling(window=21).std()
    
    return df

def calculate_comprehensive_metrics(df):
    """Calculate comprehensive performance metrics"""
    
    print("\n📈 Calculating Performance Metrics...")
    
    # Basic metrics
    start_nav = df['NAV'].iloc[0]
    end_nav = df['NAV'].iloc[-1]
    total_return = ((end_nav / start_nav) - 1) * 100
    
    # Time period
    start_date = df['Date'].iloc[0]
    end_date = df['Date'].iloc[-1]
    days = (end_date - start_date).days
    
    # Returns analysis
    daily_returns = df['Daily_Return'].dropna()
    avg_daily_return = daily_returns.mean()
    volatility = daily_returns.std()
    
    # Annualized metrics (assuming 252 trading days)
    annualized_return = avg_daily_return * 252
    annualized_volatility = volatility * np.sqrt(252)
    
    # Risk metrics
    max_nav = df['NAV'].max()
    min_nav = df['NAV'].min()
    
    # Drawdown analysis
    running_max = df['NAV'].expanding().max()
    drawdown = (df['NAV'] / running_max - 1) * 100
    max_drawdown = drawdown.min()
    
    # Sharpe ratio (assuming 6% risk-free rate)
    sharpe_ratio = (annualized_return - 6) / annualized_volatility if annualized_volatility > 0 else 0
    
    # Extreme values
    best_day = daily_returns.max()
    worst_day = daily_returns.min()
    
    # Positive/negative days
    positive_days = len(daily_returns[daily_returns > 0])
    negative_days = len(daily_returns[daily_returns < 0])
    win_rate = positive_days / len(daily_returns) * 100
    
    metrics = {
        'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        'days': days,
        'trading_days': len(df) - 1,
        'start_nav': start_nav,
        'end_nav': end_nav,
        'max_nav': max_nav,
        'min_nav': min_nav,
        'total_return': total_return,
        'annualized_return': annualized_return,
        'avg_daily_return': avg_daily_return,
        'volatility': volatility,
        'annualized_volatility': annualized_volatility,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'best_day': best_day,
        'worst_day': worst_day,
        'positive_days': positive_days,
        'negative_days': negative_days,
        'win_rate': win_rate
    }
    
    return metrics

def print_analysis_summary(metrics):
    """Print comprehensive analysis summary"""
    
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE NAV ANALYSIS REPORT")
    print("="*60)
    
    print(f"\n📅 PERIOD ANALYSIS")
    print(f"Analysis Period: {metrics['period']}")
    print(f"Total Days: {metrics['days']} calendar days")
    print(f"Trading Days: {metrics['trading_days']} NAV observations")
    
    print(f"\n💰 NAV SUMMARY")
    print(f"Starting NAV: ₹{metrics['start_nav']:.4f}")
    print(f"Ending NAV: ₹{metrics['end_nav']:.4f}")
    print(f"Highest NAV: ₹{metrics['max_nav']:.4f}")
    print(f"Lowest NAV: ₹{metrics['min_nav']:.4f}")
    
    print(f"\n📈 PERFORMANCE METRICS")
    print(f"Total Return: {metrics['total_return']:+.2f}%")
    print(f"Annualized Return: {metrics['annualized_return']:+.2f}%")
    print(f"Average Daily Return: {metrics['avg_daily_return']:+.3f}%")
    
    print(f"\n⚡ RISK METRICS")
    print(f"Daily Volatility: {metrics['volatility']:.2f}%")
    print(f"Annualized Volatility: {metrics['annualized_volatility']:.2f}%")
    print(f"Maximum Drawdown: {metrics['max_drawdown']:.2f}%")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    
    print(f"\n📊 EXTREME VALUES")
    print(f"Best Single Day: {metrics['best_day']:+.2f}%")
    print(f"Worst Single Day: {metrics['worst_day']:+.2f}%")
    
    print(f"\n🎯 WIN/LOSS ANALYSIS")
    print(f"Positive Days: {metrics['positive_days']} ({metrics['win_rate']:.1f}%)")
    print(f"Negative Days: {metrics['negative_days']} ({100-metrics['win_rate']:.1f}%)")
    
    # Performance interpretation
    print(f"\n🔍 ANALYSIS INSIGHTS")
    if metrics['total_return'] > 0:
        print(f"✅ Fund gained {metrics['total_return']:.2f}% over the period")
    else:
        print(f"❌ Fund lost {abs(metrics['total_return']):.2f}% over the period")
    
    if metrics['volatility'] > 3.0:
        print("⚠️  High volatility - Fund shows significant daily price swings")
    elif metrics['volatility'] > 1.5:
        print("⚡ Moderate volatility - Normal for equity funds")
    else:
        print("😌 Low volatility - Relatively stable fund")
    
    if metrics['max_drawdown'] < -20:
        print("🔴 Severe drawdown - Fund experienced significant peak-to-trough decline")
    elif metrics['max_drawdown'] < -10:
        print("🟡 Moderate drawdown - Fund had notable corrections")
    else:
        print("🟢 Mild drawdown - Fund showed resilience")

def create_comprehensive_visualizations(df, metrics):
    """Create comprehensive visualizations"""
    
    print("\n📊 Creating Comprehensive Visualizations...")
    
    # 1. Interactive Plotly Dashboard
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=('NAV Trend with Moving Averages', 'Cumulative Returns', 
                       'Daily Returns Distribution', 'Rolling Volatility',
                       'Drawdown Analysis', 'NAV vs Date with Volume'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]],
        vertical_spacing=0.08
    )
    
    # NAV trend with moving averages
    fig.add_trace(go.Scatter(x=df['Date'], y=df['NAV'], name='NAV', 
                            line=dict(color='#2E86AB', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA_7'], name='7-day MA', 
                            line=dict(color='orange', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA_21'], name='21-day MA', 
                            line=dict(color='red', width=1)), row=1, col=1)
    
    # Cumulative returns
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Cumulative_Return'], name='Cumulative Return',
                            line=dict(color='green', width=2), fill='tonexty'), row=1, col=2)
    
    # Daily returns distribution
    fig.add_trace(go.Histogram(x=df['Daily_Return'].dropna(), name='Daily Returns',
                              marker_color='purple', opacity=0.7), row=2, col=1)
    
    # Rolling volatility
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Rolling_Vol_7'], name='7-day Vol',
                            line=dict(color='orange', width=1)), row=2, col=2)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Rolling_Vol_21'], name='21-day Vol',
                            line=dict(color='red', width=1)), row=2, col=2)
    
    # Drawdown analysis
    running_max = df['NAV'].expanding().max()
    drawdown = (df['NAV'] / running_max - 1) * 100
    fig.add_trace(go.Scatter(x=df['Date'], y=drawdown, name='Drawdown',
                            fill='tonexty', fillcolor='rgba(255,0,0,0.3)',
                            line=dict(color='red', width=1)), row=3, col=1)
    
    # NAV with volume-style visualization (daily changes)
    colors = ['green' if x > 0 else 'red' for x in df['Daily_Return'].fillna(0)]
    fig.add_trace(go.Bar(x=df['Date'], y=abs(df['Daily_Return'].fillna(0)), 
                        name='Daily Change Magnitude', marker_color=colors), row=3, col=2)
    
    # Update layout
    fig.update_layout(
        height=1000,
        title_text=f"Comprehensive NAV Analysis - {metrics['period']}",
        title_x=0.5,
        showlegend=True,
        template='plotly_white'
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_xaxes(title_text="Date", row=3, col=2)
    fig.update_yaxes(title_text="NAV (₹)", row=1, col=1)
    fig.update_yaxes(title_text="Return (%)", row=1, col=2)
    fig.update_yaxes(title_text="Frequency", row=2, col=1)
    fig.update_yaxes(title_text="Volatility (%)", row=2, col=2)
    fig.update_yaxes(title_text="Drawdown (%)", row=3, col=1)
    fig.update_yaxes(title_text="Change (%)", row=3, col=2)
    
    fig.show()
    
    # 2. Static Matplotlib Analysis
    fig_static, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig_static.suptitle(f'Detailed NAV Analysis - {metrics["period"]}', fontsize=16, fontweight='bold')
    
    # NAV trend
    axes[0,0].plot(df['Date'], df['NAV'], linewidth=2, color='#2E86AB', label='NAV')
    axes[0,0].plot(df['Date'], df['MA_7'], linewidth=1, color='orange', alpha=0.8, label='7-day MA')
    axes[0,0].plot(df['Date'], df['MA_21'], linewidth=1, color='red', alpha=0.8, label='21-day MA')
    axes[0,0].set_title('NAV Trend with Moving Averages')
    axes[0,0].set_ylabel('NAV (₹)')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Monthly performance
    df_monthly = df.copy()
    df_monthly['Month'] = df_monthly['Date'].dt.to_period('M')
    monthly_returns = df_monthly.groupby('Month').agg({
        'NAV': ['first', 'last']
    }).round(4)
    monthly_returns.columns = ['Start', 'End']
    monthly_returns['Return'] = ((monthly_returns['End'] / monthly_returns['Start']) - 1) * 100
    
    monthly_returns['Return'].plot(kind='bar', ax=axes[0,1], color=['green' if x > 0 else 'red' for x in monthly_returns['Return']])
    axes[0,1].set_title('Monthly Returns')
    axes[0,1].set_ylabel('Return (%)')
    axes[0,1].tick_params(axis='x', rotation=45)
    axes[0,1].grid(True, alpha=0.3)
    
    # Daily returns distribution
    axes[0,2].hist(df['Daily_Return'].dropna(), bins=20, alpha=0.7, color='purple', edgecolor='black')
    axes[0,2].axvline(df['Daily_Return'].mean(), color='red', linestyle='--', 
                     label=f'Mean: {df["Daily_Return"].mean():.3f}%')
    axes[0,2].set_title('Daily Returns Distribution')
    axes[0,2].set_xlabel('Daily Return (%)')
    axes[0,2].set_ylabel('Frequency')
    axes[0,2].legend()
    axes[0,2].grid(True, alpha=0.3)
    
    # Cumulative returns
    axes[1,0].plot(df['Date'], df['Cumulative_Return'], linewidth=2, color='green')
    axes[1,0].fill_between(df['Date'], df['Cumulative_Return'], alpha=0.3, color='green')
    axes[1,0].set_title('Cumulative Returns')
    axes[1,0].set_ylabel('Cumulative Return (%)')
    axes[1,0].grid(True, alpha=0.3)
    axes[1,0].tick_params(axis='x', rotation=45)
    
    # Rolling volatility
    axes[1,1].plot(df['Date'], df['Rolling_Vol_7'], linewidth=1, color='orange', label='7-day')
    axes[1,1].plot(df['Date'], df['Rolling_Vol_21'], linewidth=2, color='red', label='21-day')
    axes[1,1].set_title('Rolling Volatility')
    axes[1,1].set_ylabel('Volatility (%)')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    axes[1,1].tick_params(axis='x', rotation=45)
    
    # Drawdown
    running_max = df['NAV'].expanding().max()
    drawdown = (df['NAV'] / running_max - 1) * 100
    axes[1,2].fill_between(df['Date'], drawdown, 0, alpha=0.6, color='red')
    axes[1,2].plot(df['Date'], drawdown, linewidth=1, color='darkred')
    axes[1,2].set_title('Drawdown Analysis')
    axes[1,2].set_ylabel('Drawdown (%)')
    axes[1,2].grid(True, alpha=0.3)
    axes[1,2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    # 3. Summary statistics table
    print("\n📋 MONTHLY PERFORMANCE BREAKDOWN")
    print("-" * 50)
    monthly_summary = monthly_returns.copy()
    monthly_summary.index = monthly_summary.index.astype(str)
    for month, row in monthly_summary.iterrows():
        print(f"{month}: {row['Return']:+.2f}% (₹{row['Start']:.4f} → ₹{row['End']:.4f})")

def export_analysis_report(df, metrics):
    """Export comprehensive analysis report"""
    
    print("\n💾 Exporting Analysis Report...")
    
    # Create detailed report
    report = f"""
COMPREHENSIVE NAV ANALYSIS REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

FUND PERFORMANCE SUMMARY
------------------------
Analysis Period: {metrics['period']}
Total Days: {metrics['days']} calendar days
Trading Days: {metrics['trading_days']} NAV observations

NAV STATISTICS
--------------
Starting NAV: ₹{metrics['start_nav']:.4f}
Ending NAV: ₹{metrics['end_nav']:.4f}
Highest NAV: ₹{metrics['max_nav']:.4f}
Lowest NAV: ₹{metrics['min_nav']:.4f}
NAV Range: ₹{metrics['max_nav'] - metrics['min_nav']:.4f}

RETURN ANALYSIS
---------------
Total Return: {metrics['total_return']:+.2f}%
Annualized Return: {metrics['annualized_return']:+.2f}%
Average Daily Return: {metrics['avg_daily_return']:+.3f}%

RISK METRICS
------------
Daily Volatility: {metrics['volatility']:.2f}%
Annualized Volatility: {metrics['annualized_volatility']:.2f}%
Maximum Drawdown: {metrics['max_drawdown']:.2f}%
Sharpe Ratio: {metrics['sharpe_ratio']:.2f}

EXTREME VALUES
--------------
Best Single Day: {metrics['best_day']:+.2f}%
Worst Single Day: {metrics['worst_day']:+.2f}%

TRADING STATISTICS
------------------
Positive Days: {metrics['positive_days']} ({metrics['win_rate']:.1f}%)
Negative Days: {metrics['negative_days']} ({100-metrics['win_rate']:.1f}%)

RISK ASSESSMENT
---------------
"""
    
    if metrics['total_return'] > 5:
        report += "✅ Strong positive performance over the period\n"
    elif metrics['total_return'] > 0:
        report += "✅ Positive performance, modest gains\n"
    else:
        report += "❌ Negative performance, fund declined\n"
    
    if metrics['volatility'] > 3:
        report += "⚠️  High volatility - Significant daily price movements\n"
    elif metrics['volatility'] > 1.5:
        report += "⚡ Moderate volatility - Normal for equity funds\n"
    else:
        report += "😌 Low volatility - Relatively stable fund\n"
    
    if metrics['max_drawdown'] < -15:
        report += "🔴 Severe drawdown experienced\n"
    elif metrics['max_drawdown'] < -8:
        report += "🟡 Moderate drawdown experienced\n"
    else:
        report += "🟢 Mild drawdown, good resilience\n"
    
    report += f"\nDISCLAIMER\n----------\n"
    report += f"This analysis is for educational purposes only.\n"
    report += f"Past performance does not guarantee future results.\n"
    report += f"Please consult financial professionals for investment advice.\n"
    
    # Save report
    with open('nav_analysis_report.txt', 'w') as f:
        f.write(report)
    
    # Save enhanced CSV with calculations
    df_export = df.copy()
    df_export.to_csv('nav_data_with_analysis.csv', index=False)
    
    print("✅ Files exported:")
    print("   - nav_analysis_report.txt (detailed report)")
    print("   - nav_data_with_analysis.csv (data with calculations)")

def main():
    """Main analysis function"""
    
    print("🚀 REAL NAV DATA ANALYSIS")
    print("="*40)
    
    # Load data
    df = load_and_analyze_real_data()
    if df is None:
        return
    
    # Calculate metrics
    metrics = calculate_comprehensive_metrics(df)
    
    # Print summary
    print_analysis_summary(metrics)
    
    # Create visualizations
    create_comprehensive_visualizations(df, metrics)
    
    # Export report
    export_analysis_report(df, metrics)
    
    print("\n🎉 Analysis completed successfully!")
    print("\nNext steps:")
    print("- Review the generated charts and report")
    print("- Compare with benchmark indices using streamlit_app.py")
    print("- Use the exported CSV for further analysis")

if __name__ == "__main__":
    main() 