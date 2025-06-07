#!/usr/bin/env python3

from financial_api_integration import FinancialAPIIntegrator

def test_crypto_apis():
    print("🧪 Testing Crypto APIs with Fixed Rate Limiting")
    print("=" * 55)
    
    api = FinancialAPIIntegrator()
    cryptos = ['bitcoin', 'ethereum', 'cardano', 'polkadot']
    
    results = []
    for crypto in cryptos:
        print(f"\n🪙 Testing {crypto.title()}...")
        result = api.get_crypto_price(crypto)
        
        if result:
            print(f"✅ {crypto.title()}: ${result['price_usd']:,.0f} USD")
            print(f"   INR: ₹{result['price_inr']:,.0f}")
            print(f"   24h Change: {result['change_24h']:+.1f}%")
            print(f"   Source: {result['source']}")
            results.append("✅ PASSED")
        else:
            print(f"❌ {crypto.title()}: Failed")
            results.append("❌ FAILED")
    
    print("\n" + "=" * 55)
    print("📊 SUMMARY:")
    for i, crypto in enumerate(cryptos):
        print(f"   {crypto.title()}: {results[i]}")
    
    passed = results.count("✅ PASSED")
    total = len(results)
    print(f"\n🎯 Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All crypto APIs working! Your dashboard should now display crypto data.")
    else:
        print("⚠️  Some APIs still failing. Check the error messages above.")

if __name__ == "__main__":
    test_crypto_apis() 