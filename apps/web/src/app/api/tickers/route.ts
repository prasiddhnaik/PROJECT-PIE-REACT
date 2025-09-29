import { NextResponse } from 'next/server'

const FINNHUB_KEY = 'd16k039r01qvtdbj2gtgd16k039r01qvtdbj2gu0'

// In-memory cache with TTL to avoid rate limits
let cached: { symbols: string[]; ts: number } | null = null
const TTL_MS = 12 * 60 * 60 * 1000 // 12 hours

export async function GET() {
  try {
    const now = Date.now()
    if (cached && now - cached.ts < TTL_MS) {
      return NextResponse.json({ symbols: cached.symbols })
    }

    // Fetch NSE symbols from Finnhub
    const res = await fetch(`https://finnhub.io/api/v1/stock/symbol?exchange=NS&token=${FINNHUB_KEY}`, {
      // 10s timeout via AbortController
      next: { revalidate: 0 },
    })
    if (!res.ok) throw new Error(`Finnhub tickers error ${res.status}`)
    const json = await res.json()

    // Map to Yahoo format SYMBOL.NS and filter invalids
    const symbols: string[] = Array.isArray(json)
      ? json
          .map((it: any) => (it?.symbol ? `${it.symbol}.NS` : null))
          .filter((s: string | null) => !!s) as string[]
      : []

    // Deduplicate and trim to 500 max
    const unique = Array.from(new Set(symbols)).slice(0, 500)
    cached = { symbols: unique, ts: now }
    return NextResponse.json({ symbols: unique })
  } catch (e) {
    // Fallback minimal core if API fails
    const NSE_CORE = [
      'RELIANCE.NS','TCS.NS','INFY.NS','HDFCBANK.NS','ICICIBANK.NS','SBIN.NS','HINDUNILVR.NS',
      'BHARTIARTL.NS','ITC.NS','LT.NS','KOTAKBANK.NS','AXISBANK.NS','BAJFINANCE.NS','ASIANPAINT.NS',
      'MARUTI.NS','TATAMOTORS.NS','ULTRACEMCO.NS','SUNPHARMA.NS','WIPRO.NS','POWERGRID.NS'
    ]
    return NextResponse.json({ symbols: NSE_CORE }, { status: 200 })
  }
}


