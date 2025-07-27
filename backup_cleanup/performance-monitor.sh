#!/bin/bash

echo "🏎️  CRYPTO ANALYTICS ENGINE PERFORMANCE MONITOR 🏎️"
echo "=================================================="
echo ""

# Backend Health Check
echo "🔧 Backend Engine Status:"
echo "-------------------------"
backend_status=$(curl -s "http://localhost:8001/health" | jq -r '.status // "unreachable"')
if [ "$backend_status" = "healthy" ]; then
    echo "✅ Backend: HEALTHY"
else
    echo "❌ Backend: $backend_status"
fi

# Performance Test - API Response Times
echo ""
echo "⚡ API Performance Tests:"
echo "------------------------"

# Test Top 100 Endpoint
echo -n "📊 Top 100 Crypto: "
top100_time=$(curl -w "%{time_total}" -s "http://localhost:8001/api/top100/crypto" -o /dev/null)
echo "${top100_time}s"

# Test Individual Crypto
echo -n "💰 BTC Data: "
btc_time=$(curl -w "%{time_total}" -s "http://localhost:8001/api/crypto/btc" -o /dev/null)
echo "${btc_time}s"

# Test Market Overview
echo -n "📈 Market Overview: "
market_time=$(curl -w "%{time_total}" -s "http://localhost:8001/api/market/overview" -o /dev/null)
echo "${market_time}s"

# Frontend Check
echo ""
echo "🖥️  Frontend Status:"
echo "------------------"
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000")
if [ "$frontend_status" = "200" ]; then
    echo "✅ Frontend: RUNNING (port 3000)"
else
    echo "❌ Frontend: HTTP $frontend_status"
fi

# Data Quality Check
echo ""
echo "📡 Data Quality:"
echo "---------------"
crypto_count=$(curl -s "http://localhost:8001/api/top100/crypto" | jq '.count // 0')
total_market_cap=$(curl -s "http://localhost:8001/api/top100/crypto" | jq '.total_market_cap // 0')

echo "📊 Cryptocurrencies: $crypto_count"
if [ "$crypto_count" = "100" ]; then
    echo "✅ Full dataset loaded"
else
    echo "⚠️  Partial dataset ($crypto_count/100)"
fi

if [ "$total_market_cap" != "0" ] && [ "$total_market_cap" != "null" ]; then
    market_cap_formatted=$(echo "$total_market_cap" | sed 's/\(.*\)\(...\)\(...\)\(...\)$/\1.\2T/')
    echo "💰 Total Market Cap: $market_cap_formatted"
    echo "✅ Market data healthy"
else
    echo "❌ Market cap data missing"
fi

echo ""
echo "🌟 Overall Engine Status:"
echo "========================"
if [ "$backend_status" = "healthy" ] && [ "$frontend_status" = "200" ] && [ "$crypto_count" = "100" ]; then
    echo "🏎️  ENGINE STATUS: WELL-OILED MACHINE! 🏎️"
    echo "🚀 All systems operational"
    echo "⚡ Performance optimized"
    echo "📊 Data feeds healthy"
else
    echo "⚠️  ENGINE STATUS: Needs Attention"
    echo "🔧 Some components need optimization"
fi

echo ""
echo "==================================================" 