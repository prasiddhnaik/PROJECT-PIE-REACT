import { NextRequest, NextResponse } from 'next/server';

const ALPHA_VANTAGE_KEY = '22TNS9NWXVD5CPVF';
const FINNHUB_KEY = 'd16k039r01qvtdbj2gtgd16k039r01qvtdbj2gu0';

const MAJOR_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC'];

export async function GET(request: NextRequest) {
  try {
    const marketData = await fetchMarketOverview();
    return NextResponse.json(marketData);
  } catch (error) {
    console.error('Market overview API error:', error);
    return NextResponse.json({ error: 'Failed to fetch market data' }, { status: 500 });
  }
}

async function fetchMarketOverview() {
  const stocks = [];
  
  // Fetch data for major stocks
  for (const symbol of MAJOR_SYMBOLS) {
    try {
      let stockData = await fetchStockFromFinnhub(symbol);
      if (!stockData) {
        stockData = await fetchStockFromAlphaVantage(symbol);
      }
      if (!stockData) {
        stockData = generateMockStock(symbol);
      }
      stocks.push(stockData);
    } catch (error) {
      console.error(`Error fetching ${symbol}:`, error);
      stocks.push(generateMockStock(symbol));
    }
  }

  // Calculate market summary
  const totalStocks = stocks.length;
  const gainers = stocks.filter(s => s.changePercent > 0).length;
  const losers = stocks.filter(s => s.changePercent < 0).length;
  const unchanged = totalStocks - gainers - losers;

  const avgChange = stocks.reduce((sum, s) => sum + s.changePercent, 0) / totalStocks;

  return {
    stocks,
    summary: {
      totalStocks,
      gainers,
      losers,
      unchanged,
      avgChange: Number(avgChange.toFixed(2))
    },
    indices: generateMockIndices(),
    lastUpdated: new Date().toISOString()
  };
}

async function fetchStockFromFinnhub(symbol: string) {
  try {
    const res = await fetch(`https://finnhub.io/api/v1/quote?symbol=${symbol}&token=${FINNHUB_KEY}`);
    const data = await res.json();

    if (!data.c) return null;

    return {
      symbol,
      name: getCompanyName(symbol),
      price: Number(data.c.toFixed(2)),
      change: Number(data.d.toFixed(2)),
      changePercent: Number(data.dp.toFixed(2)),
      volume: Math.floor(Math.random() * 50000000), // Mock volume
      marketCap: calculateMockMarketCap(data.c)
    };
  } catch (error) {
    return null;
  }
}

async function fetchStockFromAlphaVantage(symbol: string) {
  try {
    const res = await fetch(`https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${ALPHA_VANTAGE_KEY}`);
    const data = await res.json();
    const quote = data['Global Quote'];

    if (!quote) return null;

    return {
      symbol,
      name: getCompanyName(symbol),
      price: Number(parseFloat(quote['05. price']).toFixed(2)),
      change: Number(parseFloat(quote['09. change']).toFixed(2)),
      changePercent: Number(parseFloat(quote['10. change percent'].replace('%', '')).toFixed(2)),
      volume: parseInt(quote['06. volume']) || Math.floor(Math.random() * 50000000),
      marketCap: calculateMockMarketCap(parseFloat(quote['05. price']))
    };
  } catch (error) {
    return null;
  }
}

function generateMockStock(symbol: string) {
  const basePrice = Math.random() * 300 + 50; // $50-$350
  const changePercent = (Math.random() - 0.5) * 10; // -5% to +5%
  const change = basePrice * (changePercent / 100);

  return {
    symbol,
    name: getCompanyName(symbol),
    price: Number(basePrice.toFixed(2)),
    change: Number(change.toFixed(2)),
    changePercent: Number(changePercent.toFixed(2)),
    volume: Math.floor(Math.random() * 50000000),
    marketCap: calculateMockMarketCap(basePrice)
  };
}

function getCompanyName(symbol: string): string {
  const names: { [key: string]: string } = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    'TSLA': 'Tesla Inc.',
    'NVDA': 'NVIDIA Corporation',
    'META': 'Meta Platforms Inc.',
    'NFLX': 'Netflix Inc.',
    'AMD': 'Advanced Micro Devices',
    'INTC': 'Intel Corporation'
  };
  return names[symbol] || `${symbol} Corp.`;
}

function calculateMockMarketCap(price: number): number {
  // Rough estimate based on typical share counts
  const shareMultipliers: { [key: string]: number } = {
    'AAPL': 15.5e9,
    'MSFT': 7.4e9,
    'GOOGL': 12.6e9,
    'AMZN': 10.5e9,
    'TSLA': 3.2e9,
    'NVDA': 24.7e9,
    'META': 2.5e9,
    'NFLX': 440e6,
    'AMD': 1.6e9,
    'INTC': 4.2e9
  };
  
  return Math.floor(price * (shareMultipliers['AAPL'] || 1e9)); // Default to 1B shares
}

function generateMockIndices() {
  return {
    'S&P 500': {
      value: 4750 + (Math.random() - 0.5) * 100,
      change: (Math.random() - 0.5) * 50,
      changePercent: (Math.random() - 0.5) * 2
    },
    'NASDAQ': {
      value: 15200 + (Math.random() - 0.5) * 200,
      change: (Math.random() - 0.5) * 80,
      changePercent: (Math.random() - 0.5) * 2.5
    },
    'DOW': {
      value: 38000 + (Math.random() - 0.5) * 300,
      change: (Math.random() - 0.5) * 150,
      changePercent: (Math.random() - 0.5) * 1.5
    }
  };
}
