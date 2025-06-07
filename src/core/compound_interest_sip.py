#!/usr/bin/env python3
"""
Compound Interest SIP Calculator
Week 3 & 4 Implementation: Annual and Monthly SIP Calculations
"""

import math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class CompoundInterestSIPCalculator:
    """Enhanced SIP Calculator with Compound Interest"""
    
    def __init__(self):
        self.ai_rules = {
            "increase_threshold": 10.0,  # If growth > 10%, suggest increase
            "max_increase_percent": 20.0,  # Max 20% increase suggested
            "conservative_rate": 8.0,    # Conservative rate for safety
            "aggressive_rate": 35.0     # Aggressive rate for high-risk funds
        }
    
    def calculate_annual_compound_interest(self, principal, rate, time_years):
        """
        Week 3: Basic Compound Interest Calculation
        Formula: A = P(1 + r)^t
        
        Args:
            principal (float): Initial investment in ₹
            rate (float): Annual interest rate (as percentage)
            time_years (int): Investment duration in years
            
        Returns:
            dict: Calculation results with breakdown
        """
        r = rate / 100  # Convert percentage to decimal
        final_amount = principal * ((1 + r) ** time_years)
        profit = final_amount - principal
        
        # Year-wise breakdown
        yearly_data = []
        for year in range(1, time_years + 1):
            amount_at_year = principal * ((1 + r) ** year)
            yearly_data.append({
                'Year': year,
                'Amount': amount_at_year,
                'Interest_Earned': amount_at_year - principal,
                'Total_Return_Percent': ((amount_at_year - principal) / principal) * 100
            })
        
        # AI Rule: Check if growth > 10%
        annual_growth = ((final_amount / principal) ** (1/time_years) - 1) * 100
        ai_suggestion = self._get_ai_suggestion(annual_growth, principal)
        
        return {
            'principal': principal,
            'rate': rate,
            'time_years': time_years,
            'final_amount': final_amount,
            'profit': profit,
            'total_return_percent': (profit / principal) * 100,
            'annual_growth_rate': annual_growth,
            'yearly_breakdown': yearly_data,
            'ai_suggestion': ai_suggestion,
            'formula_used': f"A = ₹{principal:,.0f} × (1 + {rate}%)^{time_years} = ₹{final_amount:,.2f}"
        }
    
    def calculate_monthly_sip_compound(self, monthly_sip, annual_rate, time_years):
        """
        Week 4: Monthly SIP with Compound Interest (OPTIMIZED)
        Formula: FV = PMT × [((1 + r)^n - 1) / r]
        Where r = annual_rate/12, n = months, PMT = monthly_sip
        
        Args:
            monthly_sip (float): Monthly SIP amount in ₹
            annual_rate (float): Annual return rate (as percentage)
            time_years (float): Investment duration in years
            
        Returns:
            dict: Detailed SIP calculation results
        """
        monthly_rate = annual_rate / (12 * 100)  # Monthly rate as decimal
        total_months = int(time_years * 12)
        
        if monthly_rate == 0:
            # If rate is 0, simple multiplication
            final_value = monthly_sip * total_months
            total_invested = final_value
            profit = 0
        else:
            # Compound SIP formula
            final_value = monthly_sip * (((1 + monthly_rate) ** total_months - 1) / monthly_rate)
            total_invested = monthly_sip * total_months
            profit = final_value - total_invested
        
        # OPTIMIZATION: Only calculate detailed breakdown for investments <= 3 years
        # For longer periods, calculate key milestones only
        monthly_data = []
        
        if total_months <= 36:  # 3 years or less - full monthly breakdown
            self._calculate_full_monthly_breakdown(
                monthly_data, monthly_sip, monthly_rate, total_months
            )
        else:  # Longer periods - calculate quarterly milestones + key points
            self._calculate_optimized_breakdown(
                monthly_data, monthly_sip, monthly_rate, total_months, time_years
            )
        
        # AI Analysis
        effective_annual_return = ((final_value / total_invested) ** (1/time_years) - 1) * 100
        ai_suggestion = self._get_ai_suggestion(effective_annual_return, monthly_sip)
        
        # Risk assessment
        risk_level = self._assess_risk_level(annual_rate)
        
        return {
            'monthly_sip': monthly_sip,
            'annual_rate': annual_rate,
            'time_years': time_years,
            'total_months': total_months,
            'total_invested': total_invested,
            'final_value': final_value,
            'profit': profit,
            'total_return_percent': (profit / total_invested) * 100 if total_invested > 0 else 0,
            'effective_annual_return': effective_annual_return,
            'monthly_breakdown': monthly_data,
            'ai_suggestion': ai_suggestion,
            'risk_level': risk_level,
            'formula_used': f"FV = ₹{monthly_sip:,.0f} × [((1 + {monthly_rate:.4f})^{total_months} - 1) / {monthly_rate:.4f}]",
            'is_optimized': total_months > 36
        }
    
    def _calculate_full_monthly_breakdown(self, monthly_data, monthly_sip, monthly_rate, total_months):
        """Calculate month-by-month breakdown for short-term investments"""
        running_investment = 0
        running_value = 0
        
        for month in range(1, total_months + 1):
            running_investment += monthly_sip
            if monthly_rate == 0:
                running_value = running_investment
            else:
                running_value = monthly_sip * (((1 + monthly_rate) ** month - 1) / monthly_rate)
            
            monthly_data.append({
                'Month': month,
                'Year': (month - 1) // 12 + 1,
                'Date': datetime.now() + timedelta(days=30 * month),
                'Monthly_SIP': monthly_sip,
                'Total_Invested': running_investment,
                'Portfolio_Value': running_value,
                'Profit': running_value - running_investment,
                'Return_Percent': ((running_value - running_investment) / running_investment) * 100 if running_investment > 0 else 0
            })
    
    def _calculate_optimized_breakdown(self, monthly_data, monthly_sip, monthly_rate, total_months, time_years):
        """Calculate optimized breakdown for long-term investments (quarterly + key milestones)"""
        # Calculate quarterly points + final value
        calculation_points = []
        
        # Add quarterly points (every 3 months)
        for quarter in range(1, int(total_months/3) + 1):
            calculation_points.append(quarter * 3)
        
        # Add yearly milestones
        for year in range(1, int(time_years) + 1):
            month = year * 12
            if month not in calculation_points and month <= total_months:
                calculation_points.append(month)
        
        # Add final month
        if total_months not in calculation_points:
            calculation_points.append(total_months)
        
        # Sort and remove duplicates
        calculation_points = sorted(list(set(calculation_points)))
        
        for month in calculation_points:
            running_investment = monthly_sip * month
            if monthly_rate == 0:
                running_value = running_investment
            else:
                running_value = monthly_sip * (((1 + monthly_rate) ** month - 1) / monthly_rate)
            
            monthly_data.append({
                'Month': month,
                'Year': (month - 1) // 12 + 1,
                'Date': datetime.now() + timedelta(days=30 * month),
                'Monthly_SIP': monthly_sip,
                'Total_Invested': running_investment,
                'Portfolio_Value': running_value,
                'Profit': running_value - running_investment,
                'Return_Percent': ((running_value - running_investment) / running_investment) * 100 if running_investment > 0 else 0,
                'Is_Milestone': True  # Mark as milestone calculation
            })
    
    def model_real_fund_performance(self, fund_name, monthly_sip, xirr_rate, time_years):
        """
        Model real mutual fund performance with given XIRR
        
        Args:
            fund_name (str): Name of the fund
            monthly_sip (float): Monthly SIP amount
            xirr_rate (float): Fund's XIRR rate (can be negative)
            time_years (float): Investment duration
            
        Returns:
            dict: Real fund modeling results
        """
        result = self.calculate_monthly_sip_compound(monthly_sip, xirr_rate, time_years)
        
        # Add fund-specific information
        result['fund_name'] = fund_name
        result['xirr_rate'] = xirr_rate
        
        # Special handling for negative returns
        if xirr_rate < 0:
            result['warning'] = f"⚠️ {fund_name} has negative XIRR of {xirr_rate}%. Your investment may lose value."
            result['risk_level'] = "🚨 Very High Risk"
        
        return result
    
    def _get_ai_suggestion(self, growth_rate, current_amount):
        """AI Rule: Suggest SIP increase if growth > 10%"""
        if growth_rate > self.ai_rules["increase_threshold"]:
            suggested_increase_percent = min(
                (growth_rate - self.ai_rules["increase_threshold"]) / 2,
                self.ai_rules["max_increase_percent"]
            )
            suggested_increase = current_amount * (suggested_increase_percent / 100)
            
            return {
                'should_increase': True,
                'current_growth': growth_rate,
                'suggested_increase_percent': suggested_increase_percent,
                'suggested_increase_amount': suggested_increase,
                'new_amount': current_amount + suggested_increase,
                'reason': f"🤖 AI Rule Activated: Growth of {growth_rate:.1f}% > 10% threshold. Consider increasing SIP!",
                'message': f"💡 Consider increasing your SIP by ₹{suggested_increase:,.0f} ({suggested_increase_percent:.1f}%) to maximize wealth creation!"
            }
        else:
            return {
                'should_increase': False,
                'current_growth': growth_rate,
                'reason': f"📊 Current growth of {growth_rate:.1f}% is below 10% threshold. Maintain current SIP.",
                'message': "🔄 Continue with current SIP amount. Monitor performance quarterly."
            }
    
    def _assess_risk_level(self, annual_rate):
        """Assess risk level based on expected returns"""
        if annual_rate < 0:
            return "🚨 Very High Risk (Negative Returns)"
        elif annual_rate < 5:
            return "🛡️ Very Low Risk"
        elif annual_rate < 10:
            return "💚 Low Risk"
        elif annual_rate < 15:
            return "📊 Moderate Risk"
        elif annual_rate < 25:
            return "⚠️ High Risk"
        else:
            return "🚨 Very High Risk"
    
    def create_growth_chart(self, sip_data):
        """Create optimized interactive growth chart using Plotly"""
        df = pd.DataFrame(sip_data['monthly_breakdown'])
        
        # OPTIMIZATION: Use simpler chart layout for better performance
        # Create single primary chart with essential information
        fig = go.Figure()
        
        # Main chart: Portfolio Value vs Investment
        fig.add_trace(
            go.Scatter(
                x=df['Month'], 
                y=df['Total_Invested'], 
                name='💰 Total Invested',
                line=dict(color='#3B82F6', width=3),
                hovertemplate='<b>Month %{x}</b><br>Invested: ₹%{y:,.0f}<extra></extra>'
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['Month'], 
                y=df['Portfolio_Value'], 
                name='📈 Portfolio Value',
                line=dict(color='#10B981', width=3),
                fill='tonexty' if sip_data['profit'] >= 0 else None,
                fillcolor='rgba(16, 185, 129, 0.1)',
                hovertemplate='<b>Month %{x}</b><br>Value: ₹%{y:,.0f}<extra></extra>'
            )
        )
        
        # Add profit area if negative returns
        if sip_data['profit'] < 0:
            fig.add_trace(
                go.Scatter(
                    x=df['Month'], 
                    y=df['Portfolio_Value'], 
                    name='📉 Loss Area',
                    line=dict(color='#EF4444', width=2),
                    fill='tonexty',
                    fillcolor='rgba(239, 68, 68, 0.1)',
                    hovertemplate='<b>Month %{x}</b><br>Loss: ₹%{customdata:,.0f}<extra></extra>',
                    customdata=df['Profit'].abs()
                )
            )
        
        # Optimize layout for performance
        fig.update_layout(
            title={
                'text': f"📊 SIP Growth: ₹{sip_data['monthly_sip']:,.0f}/month × {sip_data['time_years']} years",
                'x': 0.5,
                'font': {'size': 18}
            },
            xaxis_title="📅 Month",
            yaxis_title="💵 Amount (₹)",
            height=500,  # Reduced height for better performance
            showlegend=True,
            hovermode='x unified',
            template='plotly_white',
            # Performance optimizations
            dragmode=False,  # Disable dragging
            scrollZoom=False,  # Disable scroll zoom
        )
        
        # Format y-axis for Indian currency
        fig.update_yaxis(tickformat='₹,.0f')
        
        # Add performance indicator text
        optimization_note = ""
        if sip_data.get('is_optimized', False):
            optimization_note = " (Optimized view - showing key milestones)"
        
        fig.add_annotation(
            text=f"Final Value: ₹{sip_data['final_value']:,.0f} | Profit: ₹{sip_data['profit']:,.0f}{optimization_note}",
            xref="paper", yref="paper",
            x=0.5, y=-0.1,
            showarrow=False,
            font=dict(size=12, color='gray')
        )
        
        return fig
    
    def generate_report(self, calculation_data):
        """Generate comprehensive text report"""
        data = calculation_data
        
        report = f"""
🎯 COMPOUND INTEREST SIP ANALYSIS REPORT
{'='*60}

📊 INVESTMENT DETAILS:
   • Monthly SIP: ₹{data['monthly_sip']:,.0f}
   • Annual Return Rate: {data['annual_rate']:.2f}%
   • Investment Period: {data['time_years']} years ({data['total_months']} months)
   • Risk Level: {data['risk_level']}

💰 FINANCIAL RESULTS:
   • Total Investment: ₹{data['total_invested']:,.2f}
   • Final Portfolio Value: ₹{data['final_value']:,.2f}
   • Total Profit: ₹{data['profit']:,.2f}
   • Total Return: {data['total_return_percent']:+.2f}%
   • Effective Annual Return: {data['effective_annual_return']:+.2f}%

🤖 AI ANALYSIS:
   • {data['ai_suggestion']['reason']}
   • {data['ai_suggestion']['message']}

📈 WEALTH CREATION MESSAGE:
   🎉 👉 Your money grows to ₹{data['final_value']:,.2f}! 👈 🎉

📐 FORMULA USED:
   {data['formula_used']}
"""
        
        if 'fund_name' in data:
            report += f"""
🏦 FUND PERFORMANCE:
   • Fund: {data['fund_name']}
   • XIRR: {data['xirr_rate']:+.2f}%
"""
        
        return report

def demo_week3_annual_compound():
    """Week 3 Demo: Annual Compound Interest"""
    print("🎯 WEEK 3: COMPOUND INTEREST BASICS")
    print("="*50)
    
    calc = CompoundInterestSIPCalculator()
    
    # Model ₹1,000 SIP in SBI Small Cap (35% CAGR)
    principal = 1000
    rate = 35.0  # SBI Small Cap long-term CAGR
    time_years = 10
    
    result = calc.calculate_annual_compound_interest(principal, rate, time_years)
    
    print(f"📈 Investment: ₹{principal:,} at {rate}% for {time_years} years")
    print(f"🎉 👉 Your money grows to ₹{result['final_amount']:,.2f}! 👈")
    print(f"💰 Profit: ₹{result['profit']:,.2f}")
    print(f"📊 Total Return: {result['total_return_percent']:+.2f}%")
    print(f"📐 Formula: {result['formula_used']}")
    print(f"🤖 AI Suggestion: {result['ai_suggestion']['message']}")
    
    return result

def demo_week4_monthly_sip():
    """Week 4 Demo: Monthly SIP Compound Interest"""
    print("\n🎯 WEEK 4: MONTHLY SIP COMPOUND INTEREST")
    print("="*50)
    
    calc = CompoundInterestSIPCalculator()
    
    # Quant Small Cap (-22.45% XIRR) - 1 year
    monthly_sip = 1000
    annual_rate = -22.45  # Quant Small Cap XIRR
    time_years = 1
    
    result = calc.model_real_fund_performance(
        "Quant Small Cap Fund", monthly_sip, annual_rate, time_years
    )
    
    print(f"📈 Monthly SIP: ₹{monthly_sip:,} in {result['fund_name']}")
    print(f"📊 XIRR: {annual_rate:+.2f}% | Duration: {time_years} year")
    print(f"💰 Total Invested: ₹{result['total_invested']:,.2f}")
    print(f"📉 Portfolio Value: ₹{result['final_value']:,.2f}")
    print(f"💸 Loss: ₹{abs(result['profit']):,.2f}")
    print(f"🚨 Total Return: {result['total_return_percent']:+.2f}%")
    
    if 'warning' in result:
        print(f"⚠️  {result['warning']}")
    
    print(f"🤖 AI Analysis: {result['ai_suggestion']['message']}")
    
    return result

if __name__ == "__main__":
    # Run demos
    print("💡 COMPOUND INTEREST SIP CALCULATOR DEMO")
    print("🚀 Week 3 & 4 Implementation\n")
    
    # Week 3 Demo
    week3_result = demo_week3_annual_compound()
    
    # Week 4 Demo  
    week4_result = demo_week4_monthly_sip()
    
    # Additional examples
    print("\n🎯 ADDITIONAL EXAMPLES:")
    print("="*30)
    
    calc = CompoundInterestSIPCalculator()
    
    # SBI Small Cap positive scenario
    print("\n📈 SBI Small Cap (Positive Scenario - 35% CAGR):")
    sbi_result = calc.calculate_monthly_sip_compound(5000, 35, 5)
    print(f"   ₹5,000/month × 5 years = ₹{sbi_result['final_value']:,.2f}")
    print(f"   Profit: ₹{sbi_result['profit']:,.2f} ({sbi_result['total_return_percent']:+.1f}%)")
    print(f"   🤖 {sbi_result['ai_suggestion']['message']}") 