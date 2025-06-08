#!/usr/bin/env python3
"""
Fund Comparison Analyzer with Scroll Wheel
=========================================

Compare multiple mutual funds with interactive visualizations
and scroll wheel functionality for better user experience.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from datetime import datetime
import seaborn as sns
import streamlit as st

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class FundComparator:
    """Enhanced fund comparison class with scroll wheel and interactive features"""
    
    def __init__(self):
        self.funds_data = {}
        self.fund_metrics = {}
        
    def load_fund_data(self, csv_file, fund_name):
        """Load fund data from CSV file"""
        try:
            df = pd.read_csv(csv_file)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            
            # Calculate additional metrics
            df['Daily_Return'] = df['NAV'].pct_change() * 100
            df['Cumulative_Return'] = ((df['NAV'] / df['NAV'].iloc[0]) - 1) * 100
            df['MA_7'] = df['NAV'].rolling(window=7).mean()
            df['MA_21'] = df['NAV'].rolling(window=21).mean()
            df['Rolling_Vol_7'] = df['Daily_Return'].rolling(window=7).std()
            
            self.funds_data[fund_name] = df
            print(f"✅ Loaded {fund_name}: {len(df)} records from {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
            
            return df
            
        except FileNotFoundError:
            print(f"❌ File {csv_file} not found")
            return None
            
    def calculate_fund_metrics(self, fund_name):
        """Calculate comprehensive metrics for a fund"""
        if fund_name not in self.funds_data:
            return None
            
        df = self.funds_data[fund_name]
        daily_returns = df['Daily_Return'].dropna()
        
        # Basic metrics
        start_nav = df['NAV'].iloc[0]
        end_nav = df['NAV'].iloc[-1]
        total_return = ((end_nav / start_nav) - 1) * 100
        
        # Time period
        start_date = df['Date'].iloc[0]
        end_date = df['Date'].iloc[-1]
        days = (end_date - start_date).days
        
        # Risk metrics
        avg_daily_return = daily_returns.mean()
        volatility = daily_returns.std()
        annualized_return = avg_daily_return * 252
        annualized_volatility = volatility * np.sqrt(252)
        
        # Drawdown analysis
        running_max = df['NAV'].expanding().max()
        drawdown = (df['NAV'] / running_max - 1) * 100
        max_drawdown = drawdown.min()
        
        # Additional metrics
        sharpe_ratio = (annualized_return - 6) / annualized_volatility if annualized_volatility > 0 else 0
        best_day = daily_returns.max()
        worst_day = daily_returns.min()
        positive_days = len(daily_returns[daily_returns > 0])
        total_trading_days = len(daily_returns)
        win_rate = positive_days / total_trading_days * 100 if total_trading_days > 0 else 0
        
        metrics = {
            'fund_name': fund_name,
            'start_nav': start_nav,
            'end_nav': end_nav,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'annualized_volatility': annualized_volatility,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'best_day': best_day,
            'worst_day': worst_day,
            'win_rate': win_rate,
            'days': days,
            'trading_days': total_trading_days
        }
        
        self.fund_metrics[fund_name] = metrics
        return metrics
        
    def create_comparison_table(self):
        """Create a comparison table of all loaded funds"""
        if not self.fund_metrics:
            print("❌ No fund metrics available. Load funds first.")
            return None
            
        comparison_data = []
        for fund_name, metrics in self.fund_metrics.items():
            comparison_data.append([
                fund_name,
                f"₹{metrics['start_nav']:.2f}",
                f"₹{metrics['end_nav']:.2f}",
                f"{metrics['total_return']:+.2f}%",
                f"{metrics['annualized_return']:+.2f}%",
                f"{metrics['annualized_volatility']:.2f}%",
                f"{metrics['max_drawdown']:.2f}%",
                f"{metrics['sharpe_ratio']:.2f}",
                f"{metrics['win_rate']:.1f}%"
            ])
            
        columns = ['Fund', 'Start NAV', 'End NAV', 'Total Return', 
                  'Annualized Return', 'Volatility', 'Max Drawdown', 
                  'Sharpe Ratio', 'Win Rate']
                  
        comparison_df = pd.DataFrame(comparison_data, columns=columns)
        return comparison_df
        
    def create_interactive_comparison_charts(self):
        """Create interactive comparison charts with scroll wheel functionality"""
        if len(self.funds_data) < 2:
            print("❌ Need at least 2 funds for comparison")
            return
            
        print("📊 Creating Interactive Comparison Charts with Scroll Wheel...")
        
        # Create main comparison dashboard
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('NAV Comparison', 'Cumulative Returns Comparison',
                           'Daily Returns Distribution', 'Rolling Volatility Comparison',
                           'Drawdown Comparison', 'Monthly Returns Comparison'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]],
            vertical_spacing=0.08
        )
        
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#593E2A', '#0B5345']
        
        fund_names = list(self.funds_data.keys())
        
        # 1. NAV Comparison (normalized to 100 for better comparison)
        for i, fund_name in enumerate(fund_names):
            df = self.funds_data[fund_name]
            normalized_nav = (df['NAV'] / df['NAV'].iloc[0]) * 100
            
            fig.add_trace(go.Scatter(
                x=df['Date'], 
                y=normalized_nav,
                name=f'{fund_name} (Normalized)',
                line=dict(color=colors[i % len(colors)], width=2),
                hovertemplate=f'<b>{fund_name}</b><br>' +
                             'Date: %{x}<br>' +
                             'Normalized NAV: %{y:.2f}<br>' +
                             '<extra></extra>'
            ), row=1, col=1)
            
        # 2. Cumulative Returns
        for i, fund_name in enumerate(fund_names):
            df = self.funds_data[fund_name]
            fig.add_trace(go.Scatter(
                x=df['Date'], 
                y=df['Cumulative_Return'],
                name=f'{fund_name} Returns',
                line=dict(color=colors[i % len(colors)], width=2),
                hovertemplate=f'<b>{fund_name}</b><br>' +
                             'Date: %{x}<br>' +
                             'Cumulative Return: %{y:.2f}%<br>' +
                             '<extra></extra>'
            ), row=1, col=2)
            
        # 3. Daily Returns Distribution
        for i, fund_name in enumerate(fund_names):
            df = self.funds_data[fund_name]
            fig.add_trace(go.Histogram(
                x=df['Daily_Return'].dropna(),
                name=f'{fund_name} Daily Returns',
                opacity=0.7,
                marker_color=colors[i % len(colors)],
                nbinsx=30
            ), row=2, col=1)
            
        # 4. Rolling Volatility
        for i, fund_name in enumerate(fund_names):
            df = self.funds_data[fund_name]
            fig.add_trace(go.Scatter(
                x=df['Date'], 
                y=df['Rolling_Vol_7'],
                name=f'{fund_name} Vol',
                line=dict(color=colors[i % len(colors)], width=1),
                hovertemplate=f'<b>{fund_name}</b><br>' +
                             'Date: %{x}<br>' +
                             '7-day Volatility: %{y:.2f}%<br>' +
                             '<extra></extra>'
            ), row=2, col=2)
            
        # 5. Drawdown Comparison
        for i, fund_name in enumerate(fund_names):
            df = self.funds_data[fund_name]
            running_max = df['NAV'].expanding().max()
            drawdown = (df['NAV'] / running_max - 1) * 100
            
            fig.add_trace(go.Scatter(
                x=df['Date'], 
                y=drawdown,
                name=f'{fund_name} Drawdown',
                fill='tonexty' if i == 0 else None,
                fillcolor=f'rgba({int(colors[i % len(colors)][1:3], 16)}, {int(colors[i % len(colors)][3:5], 16)}, {int(colors[i % len(colors)][5:7], 16)}, 0.3)',
                line=dict(color=colors[i % len(colors)], width=1),
                hovertemplate=f'<b>{fund_name}</b><br>' +
                             'Date: %{x}<br>' +
                             'Drawdown: %{y:.2f}%<br>' +
                             '<extra></extra>'
            ), row=3, col=1)
            
        # 6. Monthly Returns Comparison
        for i, fund_name in enumerate(fund_names):
            df = self.funds_data[fund_name]
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
                name=f'{fund_name} Monthly',
                marker_color=colors[i % len(colors)],
                opacity=0.8,
                hovertemplate=f'<b>{fund_name}</b><br>' +
                             'Month: %{x}<br>' +
                             'Monthly Return: %{y:.2f}%<br>' +
                             '<extra></extra>'
            ), row=3, col=2)
        
        # Update layout with scroll wheel functionality
        fig.update_layout(
            height=1200,
            title_text="📊 Comprehensive Fund Comparison Dashboard",
            title_x=0.5,
            title_font_size=20,
            showlegend=True,
            template='plotly_white',
            # Enable scroll wheel zooming
            dragmode='zoom',
            # Add scroll wheel configuration
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=list([
                        dict(
                            args=[{"visible": [True] * len(fig.data)}],
                            label="Show All",
                            method="restyle"
                        ),
                        dict(
                            args=[{"yaxis.type": "linear"}],
                            label="Linear Scale",
                            method="relayout"
                        ),
                        dict(
                            args=[{"yaxis.type": "log"}],
                            label="Log Scale",
                            method="relayout"
                        )
                    ]),
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.01,
                    xanchor="left",
                    y=1.02,
                    yanchor="top"
                ),
            ]
        )
        
        # Update axes labels and enable scroll wheel for all subplots
        fig.update_xaxes(title_text="Date", row=3, col=1)
        fig.update_xaxes(title_text="Date", row=3, col=2)
        fig.update_yaxes(title_text="Normalized NAV", row=1, col=1)
        fig.update_yaxes(title_text="Cumulative Return (%)", row=1, col=2)
        fig.update_yaxes(title_text="Frequency", row=2, col=1)
        fig.update_yaxes(title_text="Volatility (%)", row=2, col=2)
        fig.update_yaxes(title_text="Drawdown (%)", row=3, col=1)
        fig.update_yaxes(title_text="Monthly Return (%)", row=3, col=2)
        
        # Enable scroll wheel for all subplots
        for i in range(1, 4):  # rows
            for j in range(1, 3):  # cols
                fig.update_xaxes(
                    showspikes=True,
                    spikecolor="gray",
                    spikesnap="cursor",
                    spikemode="across",
                    row=i, col=j
                )
                fig.update_yaxes(
                    showspikes=True,
                    spikecolor="gray",
                    spikesnap="cursor",
                    spikemode="across",
                    row=i, col=j
                )
        
        # Configure for better interactivity
        config = {
            'scrollZoom': True,  # Enable scroll wheel zooming
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'fund_comparison',
                'height': 1200,
                'width': 1600,
                'scale': 1
            }
        }
        
        # Display chart inline in Streamlit instead of saving to file
        if 'st' in globals():
            st.plotly_chart(fig, use_container_width=True, key="fund_comparison")
        else:
            fig.show()
        
        return fig
        
    def create_detailed_comparison_chart(self):
        """Create a detailed side-by-side comparison chart"""
        if len(self.funds_data) != 2:
            print("❌ This function works best with exactly 2 funds")
            return
            
        fund_names = list(self.funds_data.keys())
        fund1_name, fund2_name = fund_names[0], fund_names[1]
        fund1_data = self.funds_data[fund1_name]
        fund2_data = self.funds_data[fund2_name]
        
        # Create detailed comparison
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(f'{fund1_name} vs {fund2_name} - NAV Trends',
                           'Correlation Analysis',
                           'Risk-Return Scatter',
                           'Performance Metrics Comparison'),
            specs=[[{"secondary_y": True}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "table"}]]
        )
        
        # NAV trends with dual y-axis
        fig.add_trace(go.Scatter(
            x=fund1_data['Date'], 
            y=fund1_data['NAV'],
            name=fund1_name,
            line=dict(color='#2E86AB', width=2)
        ), row=1, col=1, secondary_y=False)
        
        fig.add_trace(go.Scatter(
            x=fund2_data['Date'], 
            y=fund2_data['NAV'],
            name=fund2_name,
            line=dict(color='#A23B72', width=2)
        ), row=1, col=1, secondary_y=True)
        
        # Correlation analysis
        # Align dates for correlation
        merged_data = pd.merge(
            fund1_data[['Date', 'Daily_Return']].rename(columns={'Daily_Return': f'{fund1_name}_Return'}),
            fund2_data[['Date', 'Daily_Return']].rename(columns={'Daily_Return': f'{fund2_name}_Return'}),
            on='Date',
            how='inner'
        )
        
        if len(merged_data) > 0:
            correlation = merged_data[f'{fund1_name}_Return'].corr(merged_data[f'{fund2_name}_Return'])
            
            fig.add_trace(go.Scatter(
                x=merged_data[f'{fund1_name}_Return'],
                y=merged_data[f'{fund2_name}_Return'],
                mode='markers',
                name=f'Correlation: {correlation:.3f}',
                marker=dict(
                    color=merged_data.index,
                    colorscale='Viridis',
                    size=6,
                    opacity=0.7
                ),
                hovertemplate=f'<b>Daily Returns Correlation</b><br>' +
                             f'{fund1_name}: %{{x:.2f}}%<br>' +
                             f'{fund2_name}: %{{y:.2f}}%<br>' +
                             '<extra></extra>'
            ), row=1, col=2)
            
        # Risk-Return scatter
        metrics1 = self.fund_metrics[fund1_name]
        metrics2 = self.fund_metrics[fund2_name]
        
        fig.add_trace(go.Scatter(
            x=[metrics1['annualized_volatility'], metrics2['annualized_volatility']],
            y=[metrics1['annualized_return'], metrics2['annualized_return']],
            mode='markers+text',
            text=[fund1_name, fund2_name],
            textposition=['top center', 'bottom center'],
            marker=dict(size=15, color=['#2E86AB', '#A23B72']),
            name='Risk-Return',
            hovertemplate='<b>%{text}</b><br>' +
                         'Volatility: %{x:.2f}%<br>' +
                         'Return: %{y:.2f}%<br>' +
                         '<extra></extra>'
        ), row=2, col=1)
        
        # Performance metrics table
        table_data = [
            ['Metric', fund1_name, fund2_name],
            ['Total Return', f"{metrics1['total_return']:+.2f}%", f"{metrics2['total_return']:+.2f}%"],
            ['Annualized Return', f"{metrics1['annualized_return']:+.2f}%", f"{metrics2['annualized_return']:+.2f}%"],
            ['Volatility', f"{metrics1['annualized_volatility']:.2f}%", f"{metrics2['annualized_volatility']:.2f}%"],
            ['Max Drawdown', f"{metrics1['max_drawdown']:.2f}%", f"{metrics2['max_drawdown']:.2f}%"],
            ['Sharpe Ratio', f"{metrics1['sharpe_ratio']:.2f}", f"{metrics2['sharpe_ratio']:.2f}"],
            ['Win Rate', f"{metrics1['win_rate']:.1f}%", f"{metrics2['win_rate']:.1f}%"]
        ]
        
        fig.add_trace(go.Table(
            header=dict(values=table_data[0],
                       fill_color='lightblue',
                       align='center',
                       font=dict(size=12, color='black')),
            cells=dict(values=list(zip(*table_data[1:])),
                      fill_color='white',
                      align='center',
                      font=dict(size=11))
        ), row=2, col=2)
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text=f"🔍 Detailed Comparison: {fund1_name} vs {fund2_name}",
            title_x=0.5,
            showlegend=True,
            template='plotly_white'
        )
        
        # Update axes
        fig.update_yaxes(title_text=f"{fund1_name} NAV (₹)", secondary_y=False, row=1, col=1)
        fig.update_yaxes(title_text=f"{fund2_name} NAV (₹)", secondary_y=True, row=1, col=1)
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_xaxes(title_text=f"{fund1_name} Daily Return (%)", row=1, col=2)
        fig.update_yaxes(title_text=f"{fund2_name} Daily Return (%)", row=1, col=2)
        fig.update_xaxes(title_text="Volatility (%)", row=2, col=1)
        fig.update_yaxes(title_text="Annualized Return (%)", row=2, col=1)
        
        # Enable scroll wheel
        config = {
            'scrollZoom': True,
            'displayModeBar': True,
            'displaylogo': False
        }
        
        # Display detailed comparison inline in Streamlit instead of saving to file
        if 'st' in globals():
            st.plotly_chart(fig, use_container_width=True, key="detailed_comparison")
        else:
            fig.show()
        
        return fig
        
    def export_comparison_report(self):
        """Export comprehensive comparison report"""
        if not self.fund_metrics:
            print("❌ No fund data to export")
            return
            
        print("💾 Exporting Comparison Report...")
        
        report = f"""
COMPREHENSIVE FUND COMPARISON REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}

FUNDS ANALYZED
--------------
"""
        
        for fund_name in self.fund_metrics.keys():
            report += f"- {fund_name}\n"
            
        report += f"""
PERFORMANCE COMPARISON
----------------------
"""
        
        # Create comparison table
        comparison_df = self.create_comparison_table()
        if comparison_df is not None:
            report += comparison_df.to_string(index=False)
            
        report += f"""

DETAILED ANALYSIS
-----------------
"""
        
        for fund_name, metrics in self.fund_metrics.items():
            report += f"""
{fund_name}:
  - Total Return: {metrics['total_return']:+.2f}%
  - Annualized Return: {metrics['annualized_return']:+.2f}%
  - Volatility: {metrics['annualized_volatility']:.2f}%
  - Max Drawdown: {metrics['max_drawdown']:.2f}%
  - Sharpe Ratio: {metrics['sharpe_ratio']:.2f}
  - Win Rate: {metrics['win_rate']:.1f}%
  - Best Day: {metrics['best_day']:+.2f}%
  - Worst Day: {metrics['worst_day']:+.2f}%
"""
        
        # Performance ranking
        report += f"""
PERFORMANCE RANKING
-------------------
"""
        
        # Rank by total return
        sorted_funds = sorted(self.fund_metrics.items(), key=lambda x: x[1]['total_return'], reverse=True)
        report += "By Total Return:\n"
        for i, (fund_name, metrics) in enumerate(sorted_funds, 1):
            report += f"  {i}. {fund_name}: {metrics['total_return']:+.2f}%\n"
            
        # Rank by Sharpe ratio
        sorted_funds_sharpe = sorted(self.fund_metrics.items(), key=lambda x: x[1]['sharpe_ratio'], reverse=True)
        report += "\nBy Sharpe Ratio (Risk-Adjusted Returns):\n"
        for i, (fund_name, metrics) in enumerate(sorted_funds_sharpe, 1):
            report += f"  {i}. {fund_name}: {metrics['sharpe_ratio']:.2f}\n"
            
        report += f"""
RISK ANALYSIS
-------------
"""
        
        # Risk assessment
        for fund_name, metrics in self.fund_metrics.items():
            risk_level = "Low" if metrics['annualized_volatility'] < 15 else "Moderate" if metrics['annualized_volatility'] < 25 else "High"
            report += f"{fund_name}: {risk_level} Risk (Volatility: {metrics['annualized_volatility']:.2f}%)\n"
            
        report += f"""
CORRELATION ANALYSIS
--------------------
"""
        
        if len(self.fund_metrics) == 2:
            fund_names = list(self.funds_data.keys())
            fund1_data = self.funds_data[fund_names[0]]
            fund2_data = self.funds_data[fund_names[1]]
            
            merged_data = pd.merge(
                fund1_data[['Date', 'Daily_Return']].rename(columns={'Daily_Return': f'{fund_names[0]}_Return'}),
                fund2_data[['Date', 'Daily_Return']].rename(columns={'Daily_Return': f'{fund_names[1]}_Return'}),
                on='Date',
                how='inner'
            )
            
            if len(merged_data) > 0:
                correlation = merged_data[f'{fund_names[0]}_Return'].corr(merged_data[f'{fund_names[1]}_Return'])
                report += f"Correlation between {fund_names[0]} and {fund_names[1]}: {correlation:.3f}\n"
                
                if correlation > 0.8:
                    report += "High positive correlation - funds move together\n"
                elif correlation > 0.5:
                    report += "Moderate positive correlation\n"
                elif correlation > -0.5:
                    report += "Low correlation - some diversification benefit\n"
                else:
                    report += "Negative correlation - good diversification\n"
                    
        report += f"""
INVESTMENT RECOMMENDATIONS
--------------------------
"""
        
        best_performer = max(self.fund_metrics.items(), key=lambda x: x[1]['total_return'])
        best_risk_adjusted = max(self.fund_metrics.items(), key=lambda x: x[1]['sharpe_ratio'])
        
        report += f"Best Overall Performer: {best_performer[0]} ({best_performer[1]['total_return']:+.2f}%)\n"
        report += f"Best Risk-Adjusted: {best_risk_adjusted[0]} (Sharpe: {best_risk_adjusted[1]['sharpe_ratio']:.2f})\n"
        
        report += f"""
DISCLAIMER
----------
This analysis is for educational purposes only.
Past performance does not guarantee future results.
Please consult financial professionals for investment advice.
"""
        
        # Save report
        with open('fund_comparison_report.txt', 'w') as f:
            f.write(report)
            
        # Save comparison CSV
        if comparison_df is not None:
            comparison_df.to_csv('fund_comparison_metrics.csv', index=False)
            
        print("✅ Files exported:")
        print("   - fund_comparison_report.txt")
        print("   - fund_comparison_metrics.csv")
        print("   - fund_comparison_interactive.html")
        if len(self.fund_metrics) == 2:
            print("   - detailed_fund_comparison.html")

def main():
    """Main comparison function"""
    
    print("🚀 FUND COMPARISON ANALYZER WITH SCROLL WHEEL")
    print("=" * 50)
    
    # Initialize comparator
    comparator = FundComparator()
    
    # Load fund data
    print("\n📊 Loading Fund Data...")
    
    # Load the original fund (let's call it Nippon India Small Cap)
    nippon_data = comparator.load_fund_data('real_nav_data.csv', 'Nippon India Small Cap')
    
    # Load HDFC Small Cap Fund
    hdfc_data = comparator.load_fund_data('hdfc_nav_data.csv', 'HDFC Small Cap Fund')
    
    if nippon_data is None or hdfc_data is None:
        print("❌ Failed to load fund data")
        return
        
    # Calculate metrics for both funds
    print("\n📈 Calculating Fund Metrics...")
    nippon_metrics = comparator.calculate_fund_metrics('Nippon India Small Cap')
    hdfc_metrics = comparator.calculate_fund_metrics('HDFC Small Cap Fund')
    
    # Print comparison summary
    print("\n" + "="*70)
    print("📊 FUND COMPARISON SUMMARY")
    print("="*70)
    
    comparison_table = comparator.create_comparison_table()
    if comparison_table is not None:
        print(comparison_table.to_string(index=False))
    
    # Create interactive visualizations with scroll wheel
    print("\n📊 Creating Interactive Comparison Charts...")
    comparator.create_interactive_comparison_charts()
    
    # Create detailed comparison for 2 funds
    print("\n🔍 Creating Detailed Comparison...")
    comparator.create_detailed_comparison_chart()
    
    # Export comprehensive report
    comparator.export_comparison_report()
    
    print("\n🎉 Comparison analysis completed!")
    print("\nGenerated files:")
    print("- fund_comparison_interactive.html (main dashboard with scroll wheel)")
    print("- detailed_fund_comparison.html (detailed 2-fund comparison)")
    print("- fund_comparison_report.txt (comprehensive analysis report)")
    print("- fund_comparison_metrics.csv (comparison metrics)")
    
    print("\n💡 Features:")
    print("- Interactive charts with scroll wheel zooming")
    print("- Hover tooltips for detailed information")
    print("- Correlation analysis between funds")
    print("- Risk-return scatter plot")
    print("- Performance ranking and recommendations")

if __name__ == "__main__":
    main() 