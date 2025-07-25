# API Quick Reference

## Your API Keys & Limits

| Service | Key (last 4) | Minute Limit | Daily Limit | Monthly Limit |
|---------|--------------|--------------|-------------|---------------|
| Yahoo Finance | No key needed | 100 calls* | Unlimited | Unlimited |
| Finnhub | Needs setup | 60 calls | Unlimited | Unlimited |
| Polygon | ...68RJ | 5 calls | Unlimited | Unlimited |
| Marketstack | ...825c | Unlimited | Unlimited | 100 calls |
| Alpha Vantage | ...LP5N | 5 calls | 500 calls | Unlimited |
| Twelve Data | ...7e9c | 8 calls | 800 calls | Unlimited |

\* Self-imposed limit to be respectful of the service

## Priority Order for API Usage
1. **Yahoo Finance** - No limits, no key needed (unofficial API)
2. **Finnhub** - 60/min (if you get a key)
3. **Twelve Data** - 8/min, 800/day
4. **Alpha Vantage** - 5/min, 500/day
5. **Polygon** - 5/min (end-of-day only)
6. **Marketstack** - Save for special cases (only 100/month!)

## Important Notes
- Marketstack uses HTTP (not HTTPS) for free tier
- Polygon only provides end-of-day data on free tier
- Yahoo Finance is unofficial but most reliable
- Alpha Vantage key: 0FHER7X1A6WKLP5N (backup: 3J52FQXN785RGJX0)

## How to Add More Keys

Add your keys to the `.env` file in the backend directory:

```
# Get a free Finnhub key (60 calls/min)
FINNHUB_KEY=your_finnhub_key_here

# Other services you might add
IEX_KEY=your_iex_key_here
FMP_KEY=your_fmp_key_here
```

## Testing Your Keys

Run the test script to check if your keys are working:

```
python test_all_apis.py
```

## Optimal API Strategy

The system automatically uses a cascading fallback approach:

1. Try Yahoo Finance first (unlimited, but unofficial)
2. If Yahoo fails, try Finnhub (if configured)
3. Then Twelve Data
4. Then Alpha Vantage
5. Then Polygon
6. Finally Marketstack (limited to 100/month)

This gives you effectively unlimited API calls while maintaining high reliability. 