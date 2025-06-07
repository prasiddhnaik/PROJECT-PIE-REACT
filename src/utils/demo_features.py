#!/usr/bin/env python3
"""
Demo Script: Portfolio Return Calculator Features
Demonstrates the key features requested:
1. Percentage return calculations with bar chart
2. AI advisor warnings for returns < -5%
3. Weighted portfolio returns with pie chart
4. AI-simulated weight adjustments
"""

import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from portfolio_return_calculator import PortfolioReturnCalculator

def main():
    print("🎯 FEATURE DEMONSTRATION: Portfolio Return Calculator")
    print("=" * 70)
    
    # Initialize calculator
    calc = PortfolioReturnCalculator()
    
    # Load fund data
    print("\n📂 Loading Fund Data...")
    success1 = calc.load_fund_data("Nippon Small Cap", "real_nav_data.csv")
    success2 = calc.load_fund_data("HDFC Small Cap", "hdfc_nav_data.csv")
    
    if not (success1 and success2):
        print("❌ Error loading fund data!")
        return
    
    print("\n" + "="*70)
    print("🎯 FEATURE 1: PERCENTAGE RETURN CALCULATION")
    print("Formula: (NAV_end - NAV_start) / NAV_start × 100")
    print("="*70)
    
    returns_data = []
    for fund_name in ["Nippon Small Cap", "HDFC Small Cap"]:
        ret_data = calc.calculate_percentage_return(fund_name)
        if ret_data:
            returns_data.append(ret_data)
            
            print(f"\n📊 {fund_name}:")
            print(f"   NAV Start: ₹{ret_data['nav_start']:.2f}")
            print(f"   NAV End:   ₹{ret_data['nav_end']:.2f}")
            print(f"   Return:    {ret_data['return_percent']:.2f}%")
            print(f"   Period:    {ret_data['start_date']} to {ret_data['end_date']}")
            
            # AI Advisor Warning System (key feature!)
            print(f"\n🤖 AI ADVISOR ANALYSIS:")
            ai_advice = calc.ai_advisor_warning(ret_data['return_percent'], fund_name)
            
            if ret_data['return_percent'] < -5:
                print(f"   🚨 WARNING TRIGGERED: Return < -5%")
            else:
                print(f"   ✅ No warnings - performance acceptable")
                
            for warning in ai_advice['warnings']:
                print(f"   ⚠️  {warning}")
            for rec in ai_advice['recommendations']:
                print(f"   💡 {rec}")
            print(f"   🎯 Risk Level: {ai_advice['risk_level']}")
    
    print("\n" + "="*70)
    print("🎯 FEATURE 2: BAR CHART VISUALIZATION")
    print("="*70)
    
    # Create bar chart
    fig = calc.create_return_bar_chart(returns_data)
    fig.write_html("demo_bar_chart.html")
    print("✅ Bar chart created: demo_bar_chart.html")
    print("   📊 Color coding:")
    print("      🔴 Red: Severe losses (< -15%)")
    print("      🟠 Orange: Moderate losses (-15% to -5%)")
    print("      🟡 Yellow: Small gains/losses (-5% to 5%)")
    print("      🟢 Green: Good gains (> 5%)")
    print("   📏 Warning line at -5% threshold")
    
    print("\n" + "="*70)
    print("🎯 FEATURE 3: WEIGHTED PORTFOLIO RETURN")
    print("="*70)
    
    # Sample allocation
    allocations = {
        "Nippon Small Cap": 60,
        "HDFC Small Cap": 40
    }
    
    print(f"\n💼 Portfolio Allocation:")
    for fund, weight in allocations.items():
        print(f"   {fund}: {weight}%")
    
    # Calculate weighted return
    portfolio_result = calc.calculate_weighted_portfolio_return(allocations)
    
    if portfolio_result:
        print(f"\n📈 Weighted Portfolio Return: {portfolio_result['total_return']:.2f}%")
        print(f"\n💰 Fund Contributions:")
        for fund, contrib in portfolio_result['fund_contributions'].items():
            print(f"   {fund}:")
            print(f"      Weight: {contrib['weight']}%")
            print(f"      Individual Return: {contrib['individual_return']:.2f}%")
            print(f"      Contribution: {contrib['contribution']:.2f}%")
            print(f"      Formula: {contrib['weight']}% × {contrib['individual_return']:.2f}% = {contrib['contribution']:.2f}%")
    
    print("\n" + "="*70)
    print("🎯 FEATURE 4: PIE CHART VISUALIZATION")
    print("="*70)
    
    # Create pie chart
    pie_fig = calc.create_allocation_pie_chart(allocations, "Portfolio Allocation Demo")
    pie_fig.write_html("demo_pie_chart.html")
    print("✅ Pie chart created: demo_pie_chart.html")
    print("   🥧 Interactive donut chart with percentages")
    print("   🎨 Professional color scheme")
    print("   📱 Responsive design")
    
    print("\n" + "="*70)
    print("🎯 FEATURE 5: AI WEIGHT ADJUSTMENT SIMULATION")
    print("="*70)
    
    # AI weight adjustments
    ai_adjustments = calc.ai_weight_adjustment(allocations, returns_data)
    
    print(f"\n🤖 AI Analysis of Current Allocation:")
    if ai_adjustments['adjustments_made']:
        print("   📉 AI detected suboptimal allocation!")
        for adjustment in ai_adjustments['adjustments_made']:
            print(f"   • {adjustment}")
        
        print(f"\n📊 Allocation Comparison:")
        print(f"{'Fund':<20} {'Original':<10} {'AI-Adjusted':<12} {'Change'}")
        print("-" * 55)
        for fund in allocations.keys():
            orig = ai_adjustments['original_weights'].get(fund, 0)
            adj = ai_adjustments['adjusted_weights'].get(fund, 0)
            change = adj - orig
            print(f"{fund:<20} {orig:>7.1f}%    {adj:>9.1f}%      {change:>+5.1f}%")
        
        # Calculate improvement
        new_portfolio = calc.calculate_weighted_portfolio_return(ai_adjustments['adjusted_weights'])
        if new_portfolio and portfolio_result:
            improvement = new_portfolio['total_return'] - portfolio_result['total_return']
            print(f"\n💡 Expected Improvement: {improvement:+.2f}%")
            print(f"   Current Return: {portfolio_result['total_return']:.2f}%")
            print(f"   AI-Optimized:   {new_portfolio['total_return']:.2f}%")
    else:
        print("   ✅ Current allocation is already optimal!")
    
    # Create AI-adjusted pie chart
    ai_pie_fig = calc.create_allocation_pie_chart(
        ai_adjustments['adjusted_weights'], 
        "AI-Recommended Portfolio Allocation"
    )
    ai_pie_fig.write_html("demo_ai_pie_chart.html")
    print("\n✅ AI-recommended pie chart: demo_ai_pie_chart.html")
    
    print("\n" + "="*70)
    print("🎯 SUMMARY OF FEATURES DEMONSTRATED")
    print("="*70)
    print("✅ 1. Percentage Return Calculation with exact formula")
    print("✅ 2. AI Advisor Warnings (triggers at -5% threshold)")
    print("✅ 3. Color-coded Bar Chart with warning line")
    print("✅ 4. Weighted Portfolio Return calculation")
    print("✅ 5. Interactive Pie Charts for allocation")
    print("✅ 6. AI-simulated weight adjustments")
    print("✅ 7. Professional visualizations saved as HTML")
    
    print(f"\n📁 Generated Files:")
    print(f"   • demo_bar_chart.html")
    print(f"   • demo_pie_chart.html") 
    print(f"   • demo_ai_pie_chart.html")
    
    print(f"\n🚀 Next Steps:")
    print(f"   • Run 'streamlit run streamlit_portfolio_app.py' for interactive web app")
    print(f"   • Open HTML files in browser for standalone charts")
    print(f"   • Modify allocations in the script to test different scenarios")

if __name__ == "__main__":
    main() 