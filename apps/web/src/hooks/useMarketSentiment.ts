import { useQuery } from '@tanstack/react-query';

interface SentimentData {
  overall_sentiment: number; // -1 to 1 scale
  confidence: number; // 0 to 1
  sentiment_sources: {
    news: number;
    social_media: number;
    technical: number;
    fear_greed_index: number;
  };
  trend: 'improving' | 'declining' | 'stable';
  last_updated: string;
  data_freshness: 'fresh' | 'stale' | 'very_stale';
  source_breakdown: {
    source_name: string;
    sentiment_score: number;
    confidence: number;
    weight: number;
  }[];
}

interface MarketSentimentResponse {
  status: string;
  data: SentimentData;
  timestamp: string;
}

const fetchMarketSentiment = async (
  symbols?: string[], 
  timeframe: string = '24h', 
  sources?: string[]
): Promise<MarketSentimentResponse> => {
  const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  
  // Build query parameters
  const params = new URLSearchParams();
  
  if (symbols && symbols.length > 0) {
    params.append('symbols', symbols.join(','));
  }
  
  params.append('timeframe', timeframe);
  
  if (sources && sources.length > 0) {
    params.append('sources', sources.join(','));
  }

  const response = await fetch(`${baseUrl}/api/market/sentiment?${params.toString()}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    // Add timeout and error handling
    signal: AbortSignal.timeout(30000), // 30 second timeout
  });

  if (!response.ok) {
    throw new Error(`Sentiment API error: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  
  // Validate response structure
  if (!data.data || typeof data.data.overall_sentiment !== 'number') {
    throw new Error('Invalid sentiment data structure');
  }

  return data;
};

export const useMarketSentiment = (
  symbols?: string[], 
  timeframe: string = '24h',
  sources?: string[]
) => {
  return useQuery({
    queryKey: ['market-sentiment', symbols, timeframe, sources],
    queryFn: () => fetchMarketSentiment(symbols, timeframe, sources),
    staleTime: 15 * 60 * 1000, // 15 minutes
    cacheTime: 30 * 60 * 1000, // 30 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    refetchOnWindowFocus: true,
    
    // Error handling and fallback
    onError: (error) => {
      console.error('Market sentiment fetch failed:', error);
    },
    
    // Transform and validate data
    select: (data): SentimentData => {
      // Normalize sentiment scores
      const normalizedData = {
        ...data.data,
        overall_sentiment: Math.max(-1, Math.min(1, data.data.overall_sentiment)),
        confidence: Math.max(0, Math.min(1, data.data.confidence || 0)),
        sentiment_sources: {
          news: Math.max(-1, Math.min(1, data.data.sentiment_sources?.news || 0)),
          social_media: Math.max(-1, Math.min(1, data.data.sentiment_sources?.social_media || 0)),
          technical: Math.max(-1, Math.min(1, data.data.sentiment_sources?.technical || 0)),
          fear_greed_index: Math.max(-1, Math.min(1, data.data.sentiment_sources?.fear_greed_index || 0))
        }
      };

      return normalizedData;
    },

    // Provide fallback data when query fails
    placeholderData: {
      status: 'error',
      data: {
        overall_sentiment: 0,
        confidence: 0,
        sentiment_sources: {
          news: 0,
          social_media: 0,
          technical: 0,
          fear_greed_index: 0
        },
        trend: 'stable' as const,
        last_updated: new Date().toISOString(),
        data_freshness: 'very_stale' as const,
        source_breakdown: []
      },
      timestamp: new Date().toISOString()
    }
  });
};

// Additional hook for real-time sentiment updates
export const useRealTimeSentiment = (symbols?: string[]) => {
  const query = useMarketSentiment(symbols, '1h');
  
  // This could be extended with WebSocket connection for real-time updates
  // useEffect(() => {
  //   const ws = new WebSocket(`ws://localhost:8000/ws/sentiment`);
  //   ws.onmessage = (event) => {
  //     const sentimentUpdate = JSON.parse(event.data);
  //     // Update query data
  //   };
  //   return () => ws.close();
  // }, []);

  return query;
};

// Hook for sentiment history and trends
export const useSentimentHistory = (symbol: string, days: number = 7) => {
  return useQuery({
    queryKey: ['sentiment-history', symbol, days],
    queryFn: async () => {
      const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(
        `${baseUrl}/api/market/sentiment/history?symbol=${symbol}&days=${days}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch sentiment history');
      }
      
      return response.json();
    },
    staleTime: 60 * 60 * 1000, // 1 hour
    enabled: !!symbol
  });
}; 