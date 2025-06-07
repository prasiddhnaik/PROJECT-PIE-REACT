#!/usr/bin/env python3
"""
💰 Simple SIP Calculator with AI Recommendations
A user-friendly tool for calculating investment growth with intelligent suggestions
"""

import math

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

def get_user_input():
    """Get and validate user input"""
    print("💰 Welcome to the SIP Calculator with AI Recommendations!")
    print("=" * 55)
    
    try:
        principal = float(input("💵 Enter Principal Amount (₹): "))
        rate = float(input("📈 Enter Annual Interest Rate (%): "))
        time = float(input("⏰ Enter Time Period (years): "))
        
        if principal <= 0 or rate < 0 or time <= 0:
            print("❌ Please enter positive values for principal and time, and non-negative rate.")
            return None
        
        return principal, rate, time
    
    except ValueError:
        print("❌ Please enter valid numerical values.")
        return None

def display_results(principal, rate, time, final_amount, growth_percentage):
    """Display formatted results"""
    print("\n" + "=" * 55)
    print("📊 INVESTMENT CALCULATION RESULTS")
    print("=" * 55)
    
    print(f"💰 Initial Investment: ₹{principal:,.2f}")
    print(f"📈 Interest Rate: {rate}% per annum")
    print(f"⏰ Time Period: {time} years")
    print(f"💹 Total Growth: {growth_percentage:.2f}%")
    print("-" * 55)
    
    # Positive message as requested
    print(f"🎉 👉 Your money grows to ₹{final_amount:,.2f}! 👈 🎉")
    
    # Additional insights
    profit = final_amount - principal
    print(f"💰 Total Profit Earned: ₹{profit:,.2f}")
    
    if time > 0:
        annual_profit = profit / time
        print(f"📅 Average Annual Profit: ₹{annual_profit:,.2f}")

def main():
    """Main program execution"""
    while True:
        # Get user input
        user_data = get_user_input()
        if user_data is None:
            continue
        
        principal, rate, time = user_data
        
        # Calculate results
        final_amount, growth_percentage = calculate_compound_interest(principal, rate, time)
        
        # Display results
        display_results(principal, rate, time, final_amount, growth_percentage)
        
        # AI Recommendation
        ai_message = ai_recommendation(growth_percentage, principal)
        print(ai_message)
        
        # Ask if user wants to calculate again
        print("=" * 55)
        again = input("🔄 Would you like to calculate again? (y/n): ").lower().strip()
        if again not in ['y', 'yes']:
            print("\n💫 Thank you for using SIP Calculator! Happy Investing! 💫")
            break
        print()

if __name__ == "__main__":
    main() 