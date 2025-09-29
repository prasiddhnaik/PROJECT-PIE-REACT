import { NextRequest, NextResponse } from 'next/server';

// Import technical indicators dynamically to avoid SSR issues
let MACD: any, RSI: any, BollingerBands: any, SMA: any, EMA: any;

async function loadIndicators() {
  if (!MACD) {
    const indicators = await import('technicalindicators');
    MACD = indicators.MACD;
    RSI = indicators.RSI;
    BollingerBands = indicators.BollingerBands;
    SMA = indicators.SMA;
    EMA = indicators.EMA;
  }
}

// In-memory response cache with 60s TTL
type CacheValue = { body: any; ts: number }
const RESPONSE_CACHE: Record<string, CacheValue> = {}
const CACHE_TTL_MS = 60 * 1000

function getFromCache(symbol: string) {
  const entry = RESPONSE_CACHE[symbol]
  if (!entry) return null
  if (Date.now() - entry.ts > CACHE_TTL_MS) return null
  return entry.body
}

function putInCache(symbol: string, body: any) {
  RESPONSE_CACHE[symbol] = { body, ts: Date.now() }
}

const ALPHA_VANTAGE_KEY = '22TNS9NWXVD5CPVF';
const FINNHUB_KEY = 'd16k039r01qvtdbj2gtgd16k039r01qvtdbj2gu0';
const POLYGON_KEY = 'SavZMeuTDTxjWJuFzBO6zES7mBFK68RJ';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const symbol = searchParams.get('symbol') || 'AAPL';

  try {
    // Simple in-memory cache per symbol for 60s
    const cached = getFromCache(symbol)
    if (cached) {
      return NextResponse.json(cached)
    }

    // Load technical indicators
    await loadIndicators();

    // Prefer Yahoo for NSE (.NS) symbols to ensure real historical data
    let data = symbol.endsWith('.NS') ? await fetchFromYahoo(symbol) : null;
    
    // Try multiple data sources in order for non-NSE symbols
    if (!data) data = await fetchFromFinnhub(symbol);
    if (!data) data = await fetchFromAlphaVantage(symbol);
    if (!data) data = await fetchFromYahoo(symbol);

    if (!data) {
      return NextResponse.json({ error: 'Failed to fetch data from all sources' }, { status: 500 });
    }

    // Calculate technical indicators
    const indicators = await calculateIndicators(data.prices);

    const responseBody = {
      symbol,
      currentPrice: data.currentPrice,
      change: data.change,
      changePercent: data.changePercent,
      prices: data.prices,
      timestamps: data.timestamps,
      indicators
    } as const

    putInCache(symbol, responseBody)
    return NextResponse.json(responseBody);

  } catch (error) {
    console.error('Stock data API error:', error);
    return NextResponse.json({ error: `Internal server error: ${error.message}` }, { status: 500 });
  }
}

async function fetchFromFinnhub(symbol: string) {
  try {
    // Get current quote
    const quoteRes = await fetch(`https://finnhub.io/api/v1/quote?symbol=${symbol}&token=${FINNHUB_KEY}`);
    const quote = await quoteRes.json();

    // Get historical data (1 month)
    const to = Math.floor(Date.now() / 1000);
    const from = to - (30 * 24 * 60 * 60); // 30 days ago
    
    const histRes = await fetch(`https://finnhub.io/api/v1/stock/candle?symbol=${symbol}&resolution=D&from=${from}&to=${to}&token=${FINNHUB_KEY}`);
    const hist = await histRes.json();

    if (hist.s !== 'ok') return null;

    return {
      currentPrice: quote.c,
      change: quote.d,
      changePercent: quote.dp,
      prices: hist.c,
      timestamps: hist.t.map((t: number) => new Date(t * 1000).toISOString())
    };
  } catch (error) {
    console.error('Finnhub error:', error);
    return null;
  }
}

async function fetchFromAlphaVantage(symbol: string) {
  try {
    // Get current quote
    const quoteRes = await fetch(`https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${ALPHA_VANTAGE_KEY}`);
    const quoteData = await quoteRes.json();
    const quote = quoteData['Global Quote'];

    // Get daily series
    const histRes = await fetch(`https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=${symbol}&outputsize=compact&apikey=${ALPHA_VANTAGE_KEY}`);
    const histData = await histRes.json();
    const series = histData['Time Series (Daily)'];

    if (!series) return null;

    const dates = Object.keys(series).sort();
    const prices = dates.map(date => parseFloat(series[date]['4. close']));
    const timestamps = dates.map(date => new Date(date).toISOString());

    return {
      currentPrice: parseFloat(quote['05. price']),
      change: parseFloat(quote['09. change']),
      changePercent: parseFloat(quote['10. change percent'].replace('%', '')),
      prices,
      timestamps
    };
  } catch (error) {
    console.error('Alpha Vantage error:', error);
    return null;
  }
}

async function fetchFromYahoo(symbol: string) {
  try {
    // Yahoo Finance real quote
    const quoteRes = await fetch(`https://query1.finance.yahoo.com/v7/finance/quote?symbols=${encodeURIComponent(symbol)}`);
    const quoteJson = await quoteRes.json();
    const quote = quoteJson.quoteResponse?.result?.[0];
    if (!quote) return null;

    // Yahoo Finance real historical chart (1 month daily)
    const chartRes = await fetch(
      `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?range=1mo&interval=1d`
    );
    const chartJson = await chartRes.json();
    const result = chartJson?.chart?.result?.[0];
    if (!result) return null;

    const timestampsRaw: number[] = result.timestamp || [];
    const quoteIndicators = result.indicators?.quote?.[0] || {};
    const closes: Array<number | null> = quoteIndicators.close || [];

    const prices: number[] = [];
    const timestamps: string[] = [];
    for (let i = 0; i < Math.min(timestampsRaw.length, closes.length); i++) {
      const close = closes[i];
      if (close !== null && typeof close === 'number') {
        prices.push(close);
        timestamps.push(new Date(timestampsRaw[i] * 1000).toISOString());
      }
    }

    if (prices.length === 0) return null;

    return {
      currentPrice: quote.regularMarketPrice,
      change: quote.regularMarketChange,
      changePercent: quote.regularMarketChangePercent,
      prices,
      timestamps
    };
  } catch (error) {
    console.error('Yahoo error:', error);
    return null;
  }
}

async function calculateIndicators(prices: number[]) {
  if (prices.length < 26) {
    return {
      sma20: [],
      ema50: [],
      macd: { MACD: [], signal: [], histogram: [] },
      rsi: [],
      bollingerBands: { upper: [], middle: [], lower: [] }
    };
  }

  const sma20 = SMA.calculate({ values: prices, period: 20 });
  const ema50 = EMA.calculate({ values: prices, period: 50 });
  
  const macd = MACD.calculate({
    values: prices,
    fastPeriod: 12,
    slowPeriod: 26,
    signalPeriod: 9,
    SimpleMAOscillator: false,
    SimpleMASignal: false
  });

  const rsi = RSI.calculate({ values: prices, period: 14 });
  
  const bollingerBands = BollingerBands.calculate({
    values: prices,
    period: 20,
    stdDev: 2
  });

  return {
    sma20,
    ema50,
    macd,
    rsi,
    bollingerBands
  };
}
