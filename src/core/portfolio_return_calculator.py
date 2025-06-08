import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class PortfolioReturnCalculator:
    """
    Portfolio Return Calculator with AI Advisor Features
    
    Features:
    - Calculate percentage returns for individual funds
    - AI-like warnings for poor performance
    - Portfolio allocation analysis with weighted returns
    - Interactive visualizations
    - AI-simulated weight adjustments
    """
    
    def __init__(self):
        self.funds_data = {}
        self.portfolio_weights = {}
        self.ai_recommendations = {}
        
    def load_fund_data(self, fund_name, csv_file_path):
        """Load NAV data for a fund from CSV file"""
        try:
            df = pd.read_csv(csv_file_path)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            self.funds_data[fund_name] = df
            print(f"✅ Loaded {len(df)} data points for {fund_name}")
            return True
        except Exception as e:
            print(f"❌ Error loading {fund_name}: {str(e)}")
            return False
    
    def calculate_percentage_return(self, fund_name):
        """Calculate percentage return for a fund"""
        if fund_name not in self.funds_data:
            print(f"❌ Fund '{fund_name}' not found!")
            return None
            
        df = self.funds_data[fund_name]
        nav_start = df.iloc[0]['NAV']
        nav_end = df.iloc[-1]['NAV']
        
        percentage_return = ((nav_end - nav_start) / nav_start) * 100
        
        return {
            'fund_name': fund_name,
            'nav_start': nav_start,
            'nav_end': nav_end,
            'return_percent': percentage_return,
            'start_date': df.iloc[0]['Date'].strftime('%Y-%m-%d'),
            'end_date': df.iloc[-1]['Date'].strftime('%Y-%m-%d'),
            'duration_days': (df.iloc[-1]['Date'] - df.iloc[0]['Date']).days
        }
    
    def ai_advisor_warning(self, return_percent, fund_name):
        """AI Advisor feature - generate warnings for poor performance"""
        warnings = []
        recommendations = []
        
        if return_percent < -5:
            warnings.append(f"⚠️ POOR PERFORMANCE ALERT: {fund_name} has declined {abs(return_percent):.2f}%")
            recommendations.append("Consider reviewing investment strategy")
            
        if return_percent < -15:
            warnings.append(f"🚨 SEVERE DECLINE WARNING: {fund_name} shows significant losses")
            recommendations.append("Consider reducing allocation or exiting position")
            
        if return_percent < -25:
            warnings.append(f"💥 CRITICAL LOSS ALERT: {fund_name} in deep red territory")
            recommendations.append("IMMEDIATE ACTION REQUIRED - Review fund fundamentals")
            
        if return_percent > 20:
            warnings.append(f"🎉 EXCELLENT PERFORMANCE: {fund_name} showing strong gains")
            recommendations.append("Consider booking partial profits")
            
        if return_percent > 50:
            warnings.append(f"🚀 OUTSTANDING RETURNS: {fund_name} exceptional performance")
            recommendations.append("Review if gains are sustainable, consider rebalancing")
            
        return {
            'warnings': warnings,
            'recommendations': recommendations,
            'risk_level': self._get_risk_level(return_percent)
        }
    
    def _get_risk_level(self, return_percent):
        """Determine risk level based on returns"""
        if return_percent < -25:
            return "CRITICAL"
        elif return_percent < -15:
            return "HIGH"
        elif return_percent < -5:
            return "MEDIUM"
        elif return_percent < 5:
            return "LOW"
        else:
            return "GROWTH"
    
    def create_return_bar_chart(self, returns_data):
        """Create bar chart for fund returns"""
        fig = go.Figure()
        
        colors = []
        for ret in returns_data:
            if ret['return_percent'] < -15:
                colors.append('#FF4444')  # Red for severe losses
            elif ret['return_percent'] < -5:
                colors.append('#FF8844')  # Orange for moderate losses
            elif ret['return_percent'] < 5:
                colors.append('#FFAA44')  # Yellow for small gains/losses
            else:
                colors.append('#44AA44')  # Green for good gains
        
        fig.add_trace(go.Bar(
            x=[ret['fund_name'] for ret in returns_data],
            y=[ret['return_percent'] for ret in returns_data],
            marker_color=colors,
            text=[f"{ret['return_percent']:.2f}%" for ret in returns_data],
            textposition='auto',
            name='Fund Returns'
        ))
        
        fig.update_layout(
            title='Fund Performance - Percentage Returns',
            xaxis_title='Funds',
            yaxis_title='Return (%)',
            template='plotly_white',
            showlegend=False,
            height=500
        )
        
        # Add horizontal line at -5% (warning threshold)
        fig.add_hline(y=-5, line_dash="dash", line_color="red", 
                      annotation_text="AI Warning Threshold (-5%)")
        
        return fig
    
    def calculate_weighted_portfolio_return(self, allocations):
        """Calculate weighted portfolio return based on allocations"""
        if not allocations:
            print("❌ No allocations provided!")
            return None
            
        # Validate allocations sum to 100%
        total_allocation = sum(allocations.values())
        if abs(total_allocation - 100) > 0.01:
            print(f"⚠️ Warning: Allocations sum to {total_allocation}%, not 100%")
            
        portfolio_return = 0
        fund_contributions = {}
        
        for fund_name, weight in allocations.items():
            if fund_name in self.funds_data:
                fund_return = self.calculate_percentage_return(fund_name)
                if fund_return:
                    contribution = (weight / 100) * fund_return['return_percent']
                    portfolio_return += contribution
                    fund_contributions[fund_name] = {
                        'weight': weight,
                        'individual_return': fund_return['return_percent'],
                        'contribution': contribution
                    }
        
        return {
            'total_return': portfolio_return,
            'fund_contributions': fund_contributions,
            'allocations': allocations
        }
    
    def ai_weight_adjustment(self, current_allocations, returns_data):
        """AI-simulated weight adjustments based on performance"""
        adjusted_weights = current_allocations.copy()
        adjustments_made = []
        
        if len(returns_data) < 2:
            return {
                'original_weights': current_allocations,
                'adjusted_weights': adjusted_weights,
                'adjustments_made': []
            }
        
        # Calculate relative performance for smarter adjustments
        returns_list = [ret['return_percent'] for ret in returns_data]
        avg_return = np.mean(returns_list)
        best_return = max(returns_list)
        worst_return = min(returns_list)
        
        for ret in returns_data:
            fund_name = ret['fund_name']
            return_percent = ret['return_percent']
            
            if fund_name in adjusted_weights:
                current_weight = adjusted_weights[fund_name]
                new_weight = current_weight
                
                # Enhanced AI Logic for weight adjustments
                if return_percent < -20:  # Severe underperformance
                    new_weight = max(5, current_weight * 0.4)  # Reduce by 60%, min 5%
                    adjustments_made.append(f"🔻 MAJOR REDUCTION: {fund_name} from {current_weight:.1f}% to {new_weight:.1f}% (Severe losses: {return_percent:.2f}%)")
                    
                elif return_percent < -15:  # High underperformance
                    new_weight = max(10, current_weight * 0.6)  # Reduce by 40%, min 10%
                    adjustments_made.append(f"📉 SIGNIFICANT REDUCTION: {fund_name} from {current_weight:.1f}% to {new_weight:.1f}% (High losses: {return_percent:.2f}%)")
                    
                elif return_percent < -10:  # Moderate underperformance
                    new_weight = max(15, current_weight * 0.75)  # Reduce by 25%, min 15%
                    adjustments_made.append(f"⬇️ REDUCTION: {fund_name} from {current_weight:.1f}% to {new_weight:.1f}% (Moderate losses: {return_percent:.2f}%)")
                
                # NEW: Enhanced logic for smaller performance differences
                elif return_percent < avg_return - 2:  # Below average by more than 2%
                    new_weight = max(20, current_weight * 0.85)  # Reduce by 15%, min 20%
                    adjustments_made.append(f"📊 MINOR REDUCTION: {fund_name} from {current_weight:.1f}% to {new_weight:.1f}% (Below average: {return_percent:.2f}% vs {avg_return:.2f}%)")
                
                elif return_percent > 25:  # Excellent performance
                    new_weight = min(60, current_weight * 1.3)  # Increase by 30%, cap at 60%
                    adjustments_made.append(f"🚀 MAJOR INCREASE: {fund_name} from {current_weight:.1f}% to {new_weight:.1f}% (Excellent: {return_percent:.2f}%)")
                    
                elif return_percent > 15:  # Good performance
                    new_weight = min(50, current_weight * 1.2)  # Increase by 20%, cap at 50%
                    adjustments_made.append(f"📈 INCREASE: {fund_name} from {current_weight:.1f}% to {new_weight:.1f}% (Good performance: {return_percent:.2f}%)")
                
                elif return_percent > 5:  # Moderate positive performance
                    new_weight = min(45, current_weight * 1.1)  # Increase by 10%, cap at 45%
                    adjustments_made.append(f"⬆️ MODEST INCREASE: {fund_name} from {current_weight:.1f}% to {new_weight:.1f}% (Positive: {return_percent:.2f}%)")
                
                # NEW: Relative performance adjustments
                elif return_percent > avg_return + 1:  # Above average by more than 1%
                    new_weight = min(40, current_weight * 1.05)  # Increase by 5%, cap at 40%
                    adjustments_made.append(f"📊 MINOR INCREASE: {fund_name} from {current_weight:.1f}% to {new_weight:.1f}% (Above average: {return_percent:.2f}% vs {avg_return:.2f}%)")
                
                # Special case: If performance gap is significant between funds
                elif len(returns_data) == 2:
                    other_return = [r['return_percent'] for r in returns_data if r['fund_name'] != fund_name][0]
                    performance_gap = abs(return_percent - other_return)
                    
                    if performance_gap > 3:  # Significant gap between two funds
                        if return_percent > other_return:  # This fund is better
                            new_weight = min(65, current_weight * 1.15)  # Favor better performer
                            adjustments_made.append(f"⚖️ REBALANCE FAVOR: {fund_name} from {current_weight:.1f}% to {new_weight:.1f}% (Outperforming by {performance_gap:.2f}%)")
                        else:  # This fund is worse
                            new_weight = max(25, current_weight * 0.85)  # Reduce worse performer
                            adjustments_made.append(f"⚖️ REBALANCE REDUCE: {fund_name} from {current_weight:.1f}% to {new_weight:.1f}% (Underperforming by {performance_gap:.2f}%)")
                
                adjusted_weights[fund_name] = round(new_weight, 1)
        
        # Normalize weights to sum to 100%
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            for fund in adjusted_weights:
                adjusted_weights[fund] = round((adjusted_weights[fund] / total_weight) * 100, 1)
        
        # Add summary if adjustments were made
        if adjustments_made:
            adjustments_made.append(f"📊 AI ANALYSIS: Avg return {avg_return:.2f}%, Best {best_return:.2f}%, Worst {worst_return:.2f}%")
        
        return {
            'original_weights': current_allocations,
            'adjusted_weights': adjusted_weights,
            'adjustments_made': adjustments_made
        }
    
    def create_allocation_pie_chart(self, allocations, title="Portfolio Allocation"):
        """Create pie chart for portfolio allocations"""
        labels = list(allocations.keys())
        values = list(allocations.values())
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            textinfo='label+percent',
            textposition='auto',
            marker=dict(
                colors=px.colors.qualitative.Set3[:len(labels)],
                line=dict(color='#FFFFFF', width=2)
            )
        )])
        
        fig.update_layout(
            title=title,
            showlegend=True,
            height=500,
            template='plotly_white'
        )
        
        return fig
    
    def generate_comprehensive_report(self, allocations):
        """Generate comprehensive portfolio analysis report"""
        print("=" * 80)
        print("🤖 AI PORTFOLIO ADVISOR - COMPREHENSIVE ANALYSIS")
        print("=" * 80)
        
        # Calculate individual fund returns
        returns_data = []
        for fund_name in self.funds_data.keys():
            ret_data = self.calculate_percentage_return(fund_name)
            if ret_data:
                returns_data.append(ret_data)
        
        # Display individual fund performance
        print("\n📊 INDIVIDUAL FUND PERFORMANCE:")
        print("-" * 50)
        for ret in returns_data:
            print(f"Fund: {ret['fund_name']}")
            print(f"  Return: {ret['return_percent']:.2f}%")
            print(f"  Period: {ret['start_date']} to {ret['end_date']}")
            print(f"  Duration: {ret['duration_days']} days")
            
            # AI Advisor warnings
            ai_advice = self.ai_advisor_warning(ret['return_percent'], ret['fund_name'])
            if ai_advice['warnings']:
                for warning in ai_advice['warnings']:
                    print(f"  {warning}")
            if ai_advice['recommendations']:
                for rec in ai_advice['recommendations']:
                    print(f"  💡 {rec}")
            print(f"  🎯 Risk Level: {ai_advice['risk_level']}")
            print()
        
        # Calculate weighted portfolio return
        if allocations:
            print("\n💼 PORTFOLIO ANALYSIS:")
            print("-" * 50)
            portfolio_result = self.calculate_weighted_portfolio_return(allocations)
            
            if portfolio_result:
                print(f"Portfolio Return: {portfolio_result['total_return']:.2f}%")
                print("\nFund Contributions:")
                for fund, contrib in portfolio_result['fund_contributions'].items():
                    print(f"  {fund}: {contrib['weight']}% allocation × {contrib['individual_return']:.2f}% return = {contrib['contribution']:.2f}% contribution")
                
                # AI Weight Adjustments
                print("\n🤖 AI RECOMMENDED WEIGHT ADJUSTMENTS:")
                print("-" * 50)
                ai_adjustments = self.ai_weight_adjustment(allocations, returns_data)
                
                if ai_adjustments['adjustments_made']:
                    for adjustment in ai_adjustments['adjustments_made']:
                        print(f"  {adjustment}")
                    
                    print(f"\nOriginal vs AI-Adjusted Allocations:")
                    print("Fund" + " " * 16 + "Original" + " " * 4 + "AI-Adjusted")
                    print("-" * 45)
                    for fund in allocations.keys():
                        orig = ai_adjustments['original_weights'].get(fund, 0)
                        adj = ai_adjustments['adjusted_weights'].get(fund, 0)
                        print(f"{fund:<20} {orig:>6.1f}%    {adj:>8.1f}%")
                    
                    # Calculate new portfolio return with adjusted weights
                    new_portfolio = self.calculate_weighted_portfolio_return(ai_adjustments['adjusted_weights'])
                    if new_portfolio:
                        print(f"\nAI-Adjusted Portfolio Return: {new_portfolio['total_return']:.2f}%")
                        improvement = new_portfolio['total_return'] - portfolio_result['total_return']
                        print(f"Expected Improvement: {improvement:+.2f}%")
                else:
                    print("  ✅ No adjustments needed - current allocation is optimal")
        
        return returns_data, portfolio_result if allocations else None

def main():
    """Main function demonstrating the portfolio calculator"""
    print("🚀 Portfolio Return Calculator with AI Advisor")
    print("=" * 60)
    
    # Initialize calculator
    calc = PortfolioReturnCalculator()
    
    # Load sample funds (you can modify these paths)
    funds_to_load = {
        "Nippon Small Cap": "real_nav_data.csv",
        "HDFC Small Cap": "hdfc_nav_data.csv"
    }
    
    print("\n📂 Loading fund data...")
    loaded_funds = []
    for fund_name, file_path in funds_to_load.items():
        try:
            if calc.load_fund_data(fund_name, file_path):
                loaded_funds.append(fund_name)
        except FileNotFoundError:
            print(f"⚠️ File not found: {file_path}")
            continue
    
    if not loaded_funds:
        print("❌ No fund data loaded. Please ensure CSV files exist.")
        return
    
    # Example allocations (you can modify these)
    sample_allocations = {
        "Nippon Small Cap": 60,
        "HDFC Small Cap": 40
    }
    
    # Filter allocations to only include loaded funds
    allocations = {fund: weight for fund, weight in sample_allocations.items() if fund in loaded_funds}
    
    print(f"\n📊 Analysis for {len(loaded_funds)} funds:")
    for fund in loaded_funds:
        print(f"  • {fund}")
    
    # Generate comprehensive report
    returns_data, portfolio_result = calc.generate_comprehensive_report(allocations)
    
    # Create visualizations
    print("\n📈 Generating visualizations...")
    
    if returns_data:
        # Bar chart for returns
        bar_fig = calc.create_return_bar_chart(returns_data)
        
        # Display charts inline instead of saving files
        st.plotly_chart(bar_fig, use_container_width=True, key="bar_chart")
    
    if allocations:
        # Pie chart for current allocation
        pie_fig = calc.create_allocation_pie_chart(allocations, "Current Portfolio Allocation")
        
        # Display pie chart inline
        st.plotly_chart(pie_fig, use_container_width=True, key="pie_chart")
        
        # AI-adjusted allocation pie chart
        ai_adjustments = calc.ai_weight_adjustment(allocations, returns_data)
        ai_pie_fig = calc.create_allocation_pie_chart(
            ai_adjustments['adjusted_weights'], 
            "AI-Recommended Portfolio Allocation"
        )
        
        # AI-adjusted allocation pie chart
        st.plotly_chart(ai_pie_fig, use_container_width=True, key="ai_pie_chart")
    
    print("\n✨ Analysis complete! Check the generated HTML files for interactive charts.")

if __name__ == "__main__":
    main() 