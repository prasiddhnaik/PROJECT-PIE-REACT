#!/usr/bin/env python3
"""
💰 Advanced SIP Calculator with Portfolio Allocation & AI Recommendations
A comprehensive tool for calculating investment growth with portfolio analysis and visualizations
"""

import math
import matplotlib.pyplot as plt
import pandas as pd

def calculate_compound_interest(principal, rate, time):
    """
    Calculate compound interest using the formula: A = P(1 + r/100)^t
    
    Args:
        principal (float): Initial investment amount in ₹
        rate (float): Annual interest rate in %
        time (float): Time period in years
    
    Returns:
        tuple: (final_amount, growth_percentage)
    """
    final_amount = principal * (1 + rate/100) ** time
    growth_percentage = ((final_amount - principal) / principal) * 100
    return final_amount, growth_percentage

def ai_recommendation(growth_percentage, current_amount):
    """
    AI-powered recommendation system
    
    Args:
        growth_percentage (float): Total growth percentage
        current_amount (float): Current investment amount
    
    Returns:
        str: AI recommendation message
    """
    if growth_percentage > 10:
        suggested_increase = min(current_amount * 0.2, 10000)  # Suggest 20% increase, max ₹10,000
        return f"""
🤖 AI RECOMMENDATION:
🚀 Excellent growth of {growth_percentage:.1f}%! 
💡 Consider increasing your SIP by ₹{suggested_increase:,.0f} to maximize your wealth!
🎯 Higher investments in good-performing assets can compound your returns exponentially.
"""
    elif growth_percentage > 5:
        return f"""
🤖 AI RECOMMENDATION:
✅ Good growth of {growth_percentage:.1f}%! 
📈 Your investment is performing well. Consider maintaining this strategy.
"""
    else:
        return f"""
🤖 AI RECOMMENDATION:
⚠️ Growth of {growth_percentage:.1f}% could be improved.
💭 Consider reviewing your investment strategy or exploring higher-yield options.
"""

def get_portfolio_input():
    """Get portfolio allocation input from user"""
    print("\n💼 PORTFOLIO ALLOCATION SETUP")
    print("=" * 50)
    
    try:
        num_investments = int(input("📊 How many different investments do you want to include? "))
        if num_investments <= 0:
            print("❌ Please enter a positive number of investments.")
            return None
        
        portfolio = {}
        total_allocation = 0
        
        for i in range(num_investments):
            print(f"\n--- Investment {i+1} ---")
            name = input(f"📝 Enter name for Investment {i+1}: ").strip()
            if not name:
                name = f"Investment {i+1}"
            
            principal = float(input(f"💵 Enter Principal Amount for {name} (₹): "))
            rate = float(input(f"📈 Enter Expected Annual Return for {name} (%): "))
            time = float(input(f"⏰ Enter Time Period for {name} (years): "))
            allocation = float(input(f"🥧 Enter Allocation Percentage for {name} (%): "))
            
            if principal <= 0 or rate < 0 or time <= 0 or allocation <= 0:
                print("❌ Please enter positive values.")
                return None
            
            portfolio[name] = {
                'principal': principal,
                'rate': rate,
                'time': time,
                'allocation': allocation
            }
            total_allocation += allocation
        
        if abs(total_allocation - 100) > 0.01:
            print(f"⚠️ Warning: Total allocation is {total_allocation}%, not 100%")
            normalize = input("🔄 Would you like to normalize allocations to 100%? (y/n): ").lower().strip()
            if normalize in ['y', 'yes']:
                for name in portfolio:
                    portfolio[name]['allocation'] = (portfolio[name]['allocation'] / total_allocation) * 100
                print("✅ Allocations normalized to 100%")
        
        return portfolio
    
    except ValueError:
        print("❌ Please enter valid numerical values.")
        return None

def calculate_portfolio_returns(portfolio):
    """Calculate weighted portfolio returns"""
    portfolio_results = {}
    total_weighted_return = 0
    total_weighted_amount = 0
    total_principal = 0
    
    for name, data in portfolio.items():
        final_amount, growth_percentage = calculate_compound_interest(
            data['principal'], data['rate'], data['time']
        )
        
        weight = data['allocation'] / 100
        weighted_return = growth_percentage * weight
        weighted_amount = final_amount * weight
        
        portfolio_results[name] = {
            'principal': data['principal'],
            'final_amount': final_amount,
            'growth_percentage': growth_percentage,
            'allocation': data['allocation'],
            'weighted_return': weighted_return,
            'weighted_amount': weighted_amount,
            'profit': final_amount - data['principal']
        }
        
        total_weighted_return += weighted_return
        total_weighted_amount += weighted_amount
        total_principal += data['principal']
    
    return portfolio_results, total_weighted_return, total_weighted_amount, total_principal

def create_allocation_pie_chart(portfolio_results):
    """Create and display pie chart for portfolio allocation"""
    try:
        # Data for pie chart
        names = list(portfolio_results.keys())
        allocations = [data['allocation'] for data in portfolio_results.values()]
        colors = plt.cm.Set3(range(len(names)))
        
        # Create the pie chart
        plt.figure(figsize=(10, 8))
        wedges, texts, autotexts = plt.pie(
            allocations, 
            labels=names, 
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            explode=[0.05] * len(names)  # Slight separation for better visibility
        )
        
        # Enhance the appearance
        plt.title('💼 Portfolio Allocation Distribution', fontsize=16, fontweight='bold', pad=20)
        
        # Make percentage text more readable
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        # Add a legend with returns information
        legend_labels = []
        for name, data in portfolio_results.items():
            legend_labels.append(f"{name}: {data['growth_percentage']:.1f}% return")
        
        plt.legend(wedges, legend_labels, title="Investment Returns", 
                  loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig('portfolio_allocation.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("📊 Pie chart saved as 'portfolio_allocation.png'")
        
    except Exception as e:
        print(f"❌ Error creating pie chart: {e}")
        print("💡 Make sure matplotlib is installed: pip install matplotlib")

def display_portfolio_results(portfolio_results, total_weighted_return, total_weighted_amount, total_principal):
    """Display comprehensive portfolio results"""
    print("\n" + "=" * 70)
    print("📊 PORTFOLIO ANALYSIS RESULTS")
    print("=" * 70)
    
    # Individual investment results
    print("\n🔍 INDIVIDUAL INVESTMENT PERFORMANCE:")
    print("-" * 70)
    for name, data in portfolio_results.items():
        print(f"\n💰 {name}:")
        print(f"   Principal: ₹{data['principal']:,.2f}")
        print(f"   Final Amount: ₹{data['final_amount']:,.2f}")
        print(f"   Growth: {data['growth_percentage']:.2f}%")
        print(f"   Allocation: {data['allocation']:.1f}%")
        print(f"   Profit: ₹{data['profit']:,.2f}")
    
    # Portfolio summary
    print("\n" + "=" * 70)
    print("📈 PORTFOLIO SUMMARY:")
    print("=" * 70)
    print(f"💰 Total Principal Invested: ₹{total_principal:,.2f}")
    print(f"🎯 Portfolio Weighted Return: {total_weighted_return:.2f}%")
    print(f"💹 Total Portfolio Value: ₹{total_weighted_amount:,.2f}")
    
    total_profit = total_weighted_amount - total_principal
    print(f"💰 Total Profit: ₹{total_profit:,.2f}")
    
    # Positive message as requested
    print(f"\n🎉 👉 Your portfolio grows to ₹{total_weighted_amount:,.2f}! 👈 🎉")
    
    # Best and worst performers
    best_performer = max(portfolio_results.items(), key=lambda x: x[1]['growth_percentage'])
    worst_performer = min(portfolio_results.items(), key=lambda x: x[1]['growth_percentage'])
    
    print(f"\n🏆 Best Performer: {best_performer[0]} ({best_performer[1]['growth_percentage']:.2f}%)")
    print(f"⚠️ Lowest Performer: {worst_performer[0]} ({worst_performer[1]['growth_percentage']:.2f}%)")

def portfolio_ai_recommendation(total_weighted_return, portfolio_results):
    """AI recommendations for portfolio"""
    print(f"\n🤖 AI PORTFOLIO ANALYSIS:")
    print("=" * 50)
    
    if total_weighted_return > 15:
        print("🚀 EXCELLENT portfolio performance!")
        print("💡 Your diversification strategy is working well.")
        best_performer = max(portfolio_results.items(), key=lambda x: x[1]['growth_percentage'])
        print(f"🎯 Consider increasing allocation to {best_performer[0]} (top performer)")
    elif total_weighted_return > 10:
        print("✅ GOOD portfolio performance!")
        print("📈 Your portfolio is beating inflation comfortably.")
        print("💡 Consider rebalancing towards better performers.")
    elif total_weighted_return > 5:
        print("⚖️ MODERATE portfolio performance.")
        print("🔍 Review underperforming investments.")
        worst_performer = min(portfolio_results.items(), key=lambda x: x[1]['growth_percentage'])
        print(f"⚠️ Consider reducing allocation to {worst_performer[0]} (lowest performer)")
    else:
        print("⚠️ Portfolio needs IMPROVEMENT!")
        print("🔄 Consider diversifying into higher-return assets.")
        print("💭 Review your investment strategy with a financial advisor.")
    
    # Diversification analysis
    allocations = [data['allocation'] for data in portfolio_results.values()]
    if max(allocations) > 60:
        print("\n⚠️ CONCENTRATION RISK: One investment dominates your portfolio.")
        print("💡 Consider better diversification across asset classes.")
    elif len(portfolio_results) >= 4 and max(allocations) < 40:
        print("\n✅ GOOD DIVERSIFICATION: Well-balanced portfolio allocation.")

def simple_sip_calculator():
    """Original simple SIP calculator"""
    print("💰 Welcome to the Simple SIP Calculator!")
    print("=" * 45)
    
    try:
        principal = float(input("💵 Enter Principal Amount (₹): "))
        rate = float(input("📈 Enter Annual Interest Rate (%): "))
        time = float(input("⏰ Enter Time Period (years): "))
        
        if principal <= 0 or rate < 0 or time <= 0:
            print("❌ Please enter positive values.")
            return
        
        final_amount, growth_percentage = calculate_compound_interest(principal, rate, time)
        
        print(f"\n🎉 👉 Your money grows to ₹{final_amount:,.2f}! 👈 🎉")
        print(f"💹 Total Growth: {growth_percentage:.2f}%")
        print(f"💰 Profit Earned: ₹{final_amount - principal:,.2f}")
        
        # AI recommendation
        ai_message = ai_recommendation(growth_percentage, principal)
        print(ai_message)
        
    except ValueError:
        print("❌ Please enter valid numerical values.")

def main():
    """Main program execution"""
    while True:
        print("\n💰 SIP CALCULATOR WITH PORTFOLIO ANALYSIS")
        print("=" * 50)
        print("1️⃣ Simple SIP Calculator")
        print("2️⃣ Portfolio Analysis with Pie Chart")
        print("3️⃣ Exit")
        
        choice = input("\n🔢 Choose an option (1/2/3): ").strip()
        
        if choice == '1':
            simple_sip_calculator()
        
        elif choice == '2':
            portfolio = get_portfolio_input()
            if portfolio:
                portfolio_results, total_weighted_return, total_weighted_amount, total_principal = calculate_portfolio_returns(portfolio)
                display_portfolio_results(portfolio_results, total_weighted_return, total_weighted_amount, total_principal)
                portfolio_ai_recommendation(total_weighted_return, portfolio_results)
                
                # Create pie chart
                show_chart = input("\n📊 Would you like to see the portfolio pie chart? (y/n): ").lower().strip()
                if show_chart in ['y', 'yes']:
                    create_allocation_pie_chart(portfolio_results)
        
        elif choice == '3':
            print("\n💫 Thank you for using SIP Calculator! Happy Investing! 💫")
            break
        
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 