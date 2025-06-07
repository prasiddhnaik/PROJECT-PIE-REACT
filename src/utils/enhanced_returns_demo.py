#!/usr/bin/env python3

from financial_api_integration import FinancialAPIIntegrator
import pandas as pd

def demo_enhanced_returns():
    """Demonstration of Enhanced Stock Return Features"""
    print("🚀 ENHANCED STOCK RETURNS DEMONSTRATION")
    print("📈 Advanced Financial Analytics & Risk Metrics")
    print("=" * 60)
    
    api = FinancialAPIIntegrator()
    
    # Showcase different stock types with enhanced analytics
    demo_stocks = [
        {"symbol": "AAPL", "name": "Apple Inc.", "type": "Large Cap Tech"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "type": "High Volatility Growth"},
        {"symbol": "MSFT", "name": "Microsoft Corp.", "type": "Stable Large Cap"}
    ]
    
    enhanced_results = []
    
    for stock in demo_stocks:
        print(f"\n🏢 ANALYZING: {stock['name']} ({stock['symbol']})")
        print(f"   Category: {stock['type']}")
        print("-" * 50)
        
        # Get enhanced data
        data = api.get_yfinance_data(stock['symbol'], period="3mo")
        
        if data and 'return_metrics' in data:
            metrics = data['return_metrics']
            profile = data.get('stock_profile', {})
            
            # Display comprehensive metrics
            print(f"💰 Current Price: ${metrics['current_price']:.2f}")
            print(f"📊 Total Return (3M): {metrics['total_return']:+.2f}%")
            print(f"📈 Annualized Return: {metrics['annualized_return']:+.2f}%")
            print(f"📉 Annualized Volatility: {metrics['volatility']:.1f}%")
            print(f"⚡ Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"📉 Maximum Drawdown: {metrics['max_drawdown']:.1f}%")
            print(f"🎯 Market Beta: {metrics['beta']}")
            print(f"🎲 Win Rate: {metrics['win_rate']:.1f}%")
            print(f"⚠️  Value at Risk (95%): {metrics['value_at_risk_95']:.2f}%")
            print(f"📅 Trading Days Analyzed: {metrics['trading_days']}")
            
            # Risk Assessment
            risk_level = "Low" if metrics['volatility'] < 20 else "Medium" if metrics['volatility'] < 35 else "High"
            print(f"🚨 Risk Assessment: {risk_level}")
            
            # Performance vs Risk
            if metrics['sharpe_ratio'] > 1.0:
                perf_rating = "Excellent (High return for risk taken)"
            elif metrics['sharpe_ratio'] > 0.5:
                perf_rating = "Good (Decent risk-adjusted returns)"
            elif metrics['sharpe_ratio'] > 0:
                perf_rating = "Fair (Positive but low risk-adjusted returns)"
            else:
                perf_rating = "Poor (Negative risk-adjusted returns)"
            
            print(f"📊 Risk-Adjusted Performance: {perf_rating}")
            
            # Market conditions context
            print(f"🏦 Market Regime: {data.get('market_regime', 'Unknown')}")
            print(f"🏭 Sector: {profile.get('sector', 'Unknown')}")
            
            # Store for comparison
            enhanced_results.append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'type': stock['type'],
                'current_price': metrics['current_price'],
                'total_return': metrics['total_return'],
                'annualized_return': metrics['annualized_return'],
                'volatility': metrics['volatility'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'max_drawdown': metrics['max_drawdown'],
                'beta': metrics['beta'],
                'win_rate': metrics['win_rate'],
                'var_95': metrics['value_at_risk_95'],
                'risk_level': risk_level
            })
        else:
            print("❌ Failed to get enhanced data")
    
    # Portfolio Comparison Analysis
    if enhanced_results:
        print("\n" + "=" * 60)
        print("📊 PORTFOLIO COMPARISON MATRIX")
        print("=" * 60)
        
        # Create comparison DataFrame
        df = pd.DataFrame(enhanced_results)
        
        print("\n🏆 PERFORMANCE RANKINGS:")
        print("-" * 30)
        
        # Best performers by different metrics
        best_return = df.loc[df['total_return'].idxmax()]
        best_sharpe = df.loc[df['sharpe_ratio'].idxmax()]
        lowest_risk = df.loc[df['volatility'].idxmin()]
        best_win_rate = df.loc[df['win_rate'].idxmax()]
        
        print(f"🥇 Best Total Return: {best_return['symbol']} ({best_return['total_return']:+.1f}%)")
        print(f"⚡ Best Sharpe Ratio: {best_sharpe['symbol']} ({best_sharpe['sharpe_ratio']:.2f})")
        print(f"🛡️  Lowest Volatility: {lowest_risk['symbol']} ({lowest_risk['volatility']:.1f}%)")
        print(f"🎯 Best Win Rate: {best_win_rate['symbol']} ({best_win_rate['win_rate']:.1f}%)")
        
        print("\n📈 RISK-RETURN SUMMARY:")
        print("-" * 30)
        for _, row in df.iterrows():
            print(f"{row['symbol']}: {row['total_return']:+6.1f}% return, {row['volatility']:5.1f}% vol, {row['sharpe_ratio']:5.2f} Sharpe")
        
        print("\n💡 INVESTMENT INSIGHTS:")
        print("-" * 30)
        
        # Portfolio insights
        avg_return = df['total_return'].mean()
        avg_vol = df['volatility'].mean()
        
        print(f"📊 Portfolio Average Return: {avg_return:+.1f}%")
        print(f"📊 Portfolio Average Volatility: {avg_vol:.1f}%")
        
        # Risk-adjusted recommendation
        high_sharpe_stocks = df[df['sharpe_ratio'] > 1.0]['symbol'].tolist()
        if high_sharpe_stocks:
            print(f"✅ High Risk-Adjusted Returns: {', '.join(high_sharpe_stocks)}")
        
        conservative_picks = df[df['volatility'] < 25]['symbol'].tolist()
        if conservative_picks:
            print(f"🛡️  Conservative Picks: {', '.join(conservative_picks)}")
        
        growth_picks = df[df['total_return'] > avg_return]['symbol'].tolist()
        if growth_picks:
            print(f"🚀 Growth Leaders: {', '.join(growth_picks)}")
    
    print("\n🎉 Enhanced Returns Demonstration Complete!")
    print("\n🔥 NEW FEATURES SHOWCASED:")
    print("   ✅ Comprehensive Risk Metrics (VaR, Max Drawdown, Beta)")
    print("   ✅ Risk-Adjusted Performance (Sharpe Ratio, Win Rate)")
    print("   ✅ Market Context (Regime, Sector Analysis)")
    print("   ✅ Advanced Return Calculations (Annualized, Volatility)")
    print("   ✅ Portfolio Comparison Matrix")
    print("   ✅ Investment Grade Risk Assessment")
    print("   ✅ Intelligent Performance Rankings")

if __name__ == "__main__":
    demo_enhanced_returns() 