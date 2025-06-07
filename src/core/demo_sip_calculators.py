#!/usr/bin/env python3
"""
💰 Demo Script for SIP Calculators
Demonstrates the functionality of both simple and advanced SIP calculators
"""

import os
import sys

def demo_simple_sip():
    """Demo the simple SIP calculator with predefined values"""
    print("=" * 60)
    print("🔢 SIMPLE SIP CALCULATOR DEMO")
    print("=" * 60)
    
    # Import the calculation function
    from sip_calculator import calculate_compound_interest, ai_recommendation
    
    # Sample data
    test_cases = [
        {"principal": 100000, "rate": 12, "time": 10, "description": "Conservative Investment"},
        {"principal": 50000, "rate": 15, "time": 5, "description": "Aggressive Growth"},
        {"principal": 200000, "rate": 8, "time": 15, "description": "Long-term Safe Investment"}
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {case['description']} ---")
        print(f"💵 Principal: ₹{case['principal']:,}")
        print(f"📈 Rate: {case['rate']}%")
        print(f"⏰ Time: {case['time']} years")
        
        final_amount, growth_percentage = calculate_compound_interest(
            case['principal'], case['rate'], case['time']
        )
        
        print(f"🎉 👉 Your money grows to ₹{final_amount:,.2f}! 👈")
        print(f"💹 Total Growth: {growth_percentage:.2f}%")
        print(f"💰 Profit: ₹{final_amount - case['principal']:,.2f}")
        
        # AI recommendation
        ai_rec = ai_recommendation(growth_percentage, case['principal'])
        print(f"🤖 AI Recommendation: {ai_rec.strip()}")
        print("-" * 50)

def demo_portfolio_analysis():
    """Demo the portfolio analysis with sample data"""
    print("\n" + "=" * 60)
    print("💼 PORTFOLIO ANALYSIS DEMO")
    print("=" * 60)
    
    # Import functions
    from advanced_sip_calculator import (
        calculate_compound_interest, 
        calculate_portfolio_returns,
        portfolio_ai_recommendation
    )
    
    # Sample portfolio
    sample_portfolio = {
        "Equity Mutual Fund": {
            'principal': 150000,
            'rate': 15,
            'time': 10,
            'allocation': 60
        },
        "Debt Fund": {
            'principal': 75000,
            'rate': 8,
            'time': 10,
            'allocation': 30
        },
        "Gold ETF": {
            'principal': 25000,
            'rate': 10,
            'time': 10,
            'allocation': 10
        }
    }
    
    print("📊 Sample Portfolio Configuration:")
    total_principal = 0
    for name, data in sample_portfolio.items():
        print(f"  • {name}: ₹{data['principal']:,} ({data['allocation']}%) at {data['rate']}% for {data['time']} years")
        total_principal += data['principal']
    
    print(f"\n💰 Total Investment: ₹{total_principal:,}")
    
    # Calculate results
    portfolio_results, total_weighted_return, total_weighted_amount, total_principal = calculate_portfolio_returns(sample_portfolio)
    
    print(f"\n📈 PORTFOLIO RESULTS:")
    print("-" * 50)
    
    for name, data in portfolio_results.items():
        print(f"\n💰 {name}:")
        print(f"   Final Amount: ₹{data['final_amount']:,.2f}")
        print(f"   Growth: {data['growth_percentage']:.2f}%")
        print(f"   Weighted Return: {data['weighted_return']:.2f}%")
        print(f"   Profit: ₹{data['profit']:,.2f}")
    
    print(f"\n🎉 👉 Your portfolio grows to ₹{total_weighted_amount:,.2f}! 👈")
    print(f"📊 Portfolio Weighted Return: {total_weighted_return:.2f}%")
    print(f"💰 Total Profit: ₹{total_weighted_amount - total_principal:,.2f}")
    
    # AI recommendation for portfolio
    print(f"\n🤖 AI PORTFOLIO ANALYSIS:")
    portfolio_ai_recommendation(total_weighted_return, portfolio_results)

def demo_streamlit_info():
    """Show information about the Streamlit app"""
    print("\n" + "=" * 60)
    print("🌐 STREAMLIT WEB APP DEMO")
    print("=" * 60)
    
    print("📱 To run the interactive web application:")
    print("   python3 -m streamlit run streamlit_sip_calculator.py")
    print()
    print("🚀 Features of the web app:")
    print("   • Interactive input forms")
    print("   • Real-time calculations")
    print("   • Beautiful pie charts and bar charts")
    print("   • Portfolio allocation analysis")
    print("   • AI recommendations")
    print("   • Professional UI with metrics")
    print()
    print("🌍 The app will open in your browser at http://localhost:8501")

def create_sample_portfolio_chart():
    """Create a sample portfolio visualization"""
    try:
        import matplotlib.pyplot as plt
        
        # Sample data for pie chart
        investments = ['Equity Mutual Fund', 'Debt Fund', 'Gold ETF']
        allocations = [60, 30, 10]
        returns = [15, 8, 10]
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Pie chart for allocation
        ax1.pie(allocations, labels=investments, autopct='%1.1f%%', colors=colors, startangle=90)
        ax1.set_title('💼 Portfolio Allocation', fontsize=14, fontweight='bold')
        
        # Bar chart for returns
        bars = ax2.bar(investments, returns, color=colors)
        ax2.set_title('📈 Expected Returns', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Return (%)')
        ax2.set_ylim(0, max(returns) + 2)
        
        # Add value labels on bars
        for bar, return_val in zip(bars, returns):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{return_val}%', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('sample_portfolio_demo.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("📊 Sample portfolio chart saved as 'sample_portfolio_demo.png'")
        
    except ImportError:
        print("📊 Install matplotlib to see portfolio charts: pip install matplotlib")
    except Exception as e:
        print(f"📊 Chart generation skipped: {e}")

def main():
    """Main demo function"""
    print("💰 SIP CALCULATOR SUITE - COMPLETE DEMO")
    print("🎯 Demonstrating all features with sample data")
    print("=" * 60)
    
    try:
        # Demo 1: Simple SIP Calculator
        demo_simple_sip()
        
        # Demo 2: Portfolio Analysis
        demo_portfolio_analysis()
        
        # Demo 3: Streamlit App Info
        demo_streamlit_info()
        
        # Demo 4: Sample Chart
        print("\n" + "=" * 60)
        print("📊 SAMPLE PORTFOLIO VISUALIZATION")
        print("=" * 60)
        create_sample_portfolio_chart()
        
        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("🎯 You now have three powerful SIP calculators:")
        print("   1️⃣ sip_calculator.py - Simple command-line version")
        print("   2️⃣ advanced_sip_calculator.py - Portfolio analysis with charts")
        print("   3️⃣ streamlit_sip_calculator.py - Interactive web application")
        print()
        print("🚀 Try them out and start your investment journey!")
        print("💫 Happy Investing!")
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Please install required packages:")
        print("   pip install matplotlib pandas streamlit plotly")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("💡 Please check if all calculator files are present")

if __name__ == "__main__":
    main() 