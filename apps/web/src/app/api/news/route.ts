import { NextRequest, NextResponse } from 'next/server';

const ALPHA_VANTAGE_KEY = '22TNS9NWXVD5CPVF';
const FINNHUB_KEY = 'd16k039r01qvtdbj2gtgd16k039r01qvtdbj2gu0';

export async function GET(request: NextRequest) {
  try {
    // Try Finnhub news first
    let news = await fetchFromFinnhub();
    
    if (!news || news.length === 0) {
      // Fallback to Alpha Vantage
      news = await fetchFromAlphaVantage();
    }

    if (!news || news.length === 0) {
      // Final fallback to mock news
      news = getMockNews();
    }

    return NextResponse.json({ news });

  } catch (error) {
    console.error('News API error:', error);
    return NextResponse.json({ error: 'Failed to fetch news' }, { status: 500 });
  }
}

async function fetchFromFinnhub() {
  try {
    const res = await fetch(`https://finnhub.io/api/v1/news?category=general&token=${FINNHUB_KEY}`);
    const data = await res.json();

    return data.map((item: any) => ({
      title: item.headline,
      summary: item.summary,
      source: item.source,
      url: item.url,
      image: item.image,
      publishedAt: new Date(item.datetime * 1000).toISOString()
    })).slice(0, 20);

  } catch (error) {
    console.error('Finnhub news error:', error);
    return null;
  }
}

async function fetchFromAlphaVantage() {
  try {
    const res = await fetch(`https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=financial_markets&sort=LATEST&limit=50&apikey=${ALPHA_VANTAGE_KEY}`);
    const data = await res.json();

    if (!data.feed) return null;

    return data.feed.map((item: any) => ({
      title: item.title,
      summary: item.summary,
      source: item.source,
      url: item.url,
      image: item.banner_image,
      publishedAt: formatAlphaVantageDate(item.time_published)
    })).slice(0, 20);

  } catch (error) {
    console.error('Alpha Vantage news error:', error);
    return null;
  }
}

function formatAlphaVantageDate(timeStr: string): string {
  if (timeStr.length >= 8) {
    const year = timeStr.substring(0, 4);
    const month = timeStr.substring(4, 6);
    const day = timeStr.substring(6, 8);
    return new Date(`${year}-${month}-${day}`).toISOString();
  }
  return new Date().toISOString();
}

function getMockNews() {
  return [
    {
      title: "Markets Rally on Strong Earnings Reports",
      summary: "Major tech stocks surge after better-than-expected quarterly earnings, with analysts raising price targets across the sector.",
      source: "Financial Times",
      url: "#",
      image: null,
      publishedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString() // 30 minutes ago
    },
    {
      title: "Federal Reserve Signals Potential Rate Changes",
      summary: "Fed officials hint at policy adjustments in upcoming meetings, causing volatility in bond and currency markets.",
      source: "Reuters",
      url: "#",
      image: null,
      publishedAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString() // 2 hours ago
    },
    {
      title: "Cryptocurrency Market Sees Mixed Performance",
      summary: "Bitcoin and Ethereum show divergent trends as institutional adoption continues to grow despite regulatory concerns.",
      source: "Bloomberg",
      url: "#",
      image: null,
      publishedAt: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString() // 4 hours ago
    },
    {
      title: "Oil Prices Fluctuate on Supply Chain Updates",
      summary: "Energy markets respond to latest OPEC announcements and global supply chain developments affecting crude oil distribution.",
      source: "Wall Street Journal",
      url: "#",
      image: null,
      publishedAt: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString() // 6 hours ago
    },
    {
      title: "Green Energy Stocks Gain Momentum",
      summary: "Renewable energy companies see increased investor interest following new government incentives and climate commitments.",
      source: "CNBC",
      url: "#",
      image: null,
      publishedAt: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString() // 8 hours ago
    }
  ];
}
