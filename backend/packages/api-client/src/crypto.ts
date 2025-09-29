// Type definitions for crypto API responses
export interface CryptoData {
  symbol: string;
  name: string;
  current_price: number;
  price_change_24h: number;
  volume_24h: number;
  market_cap?: number;
  high_24h?: number;
  low_24h?: number;
  timestamp: string;
  source: string;
  _cached?: boolean;
}

export interface Top100Crypto {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  market_cap: number;
  market_cap_rank: number;
  volume_24h: number;
  price_change_24h: number;
  price_change_percent_24h: number;
  price_change_percent_1h: number;
  price_change_percent_7d: number;
  last_updated: string;
  asset_type: string;
}

export interface CryptoAnalysisResponse {
  symbol: string;
  crypto_data?: any;
  ai_analysis?: any;
  message?: string;
  timestamp: string;
}

/**
 * Resolve backend URL used for API calls.
 *
 * Priority order:
 *   1. Explicit `NEXT_PUBLIC_BACKEND_URL` env variable (browser & Node)
 *   2. In the browser, current window origin (useful when the gateway is
 *      served from the same host) unless on localhost where we fall back to
 *      the default dev port `8001`.
 *   3. Hard-coded development default `http://localhost:8001`.
 */
const getBackendUrl = (): string => {
  // 1. Environment variable (works in both browser and Node)
  if (process.env.NEXT_PUBLIC_BACKEND_URL && process.env.NEXT_PUBLIC_BACKEND_URL.trim() !== '') {
    return process.env.NEXT_PUBLIC_BACKEND_URL.trim();
  }

  // 2. Browser context – derive from current origin
  if (typeof window !== 'undefined' && window?.location?.origin) {
    const origin = window.location.origin;
    if (origin.includes('localhost')) {
      // Development – assume backend exposed on port 8001
      return 'http://localhost:8001';
    }
    return origin;
  }

  // 3. Fallback
  return 'http://localhost:8001';
};

export interface CryptoApiResponse<T> {
  status: string;
  data?: T;
  error?: string;
  timestamp?: string;
}

export interface Top100CryptoResponse {
  data: Top100Crypto[];
  count: number;
  total_market_cap: number;
  timestamp: string;
}

/**
 * Fetch individual crypto data
 */
export async function fetchCryptoData(symbol: string): Promise<CryptoApiResponse<CryptoData>> {
  const response = await fetch(`${getBackendUrl()}/api/crypto/${symbol.toLowerCase()}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch crypto data for ${symbol}: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Fetch top 100 cryptocurrencies
 */
export async function fetchTop100Crypto(): Promise<Top100CryptoResponse> {
  const response = await fetch(`${getBackendUrl()}/api/top100/crypto`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch top 100 crypto: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Fetch trending cryptocurrencies
 */
export async function fetchTrendingCrypto(): Promise<CryptoApiResponse<Top100Crypto[]>> {
  const response = await fetch(`${getBackendUrl()}/api/crypto/trending`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch trending crypto: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Get AI analysis for a specific cryptocurrency
 */
export async function fetchCryptoAIAnalysis(
  symbol: string,
  includeAI: boolean = true,
  aiModel?: string
): Promise<CryptoAnalysisResponse> {
  const response = await fetch(`${getBackendUrl()}/api/ai/analyze/crypto`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      symbol,
      include_ai: includeAI,
      ai_model: aiModel
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get AI analysis for ${symbol}: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Check server status
 */
export async function checkCryptoServerStatus(): Promise<{ status: string; timestamp: string }> {
  const response = await fetch(`${getBackendUrl()}/test`);
  
  if (!response.ok) {
    throw new Error(`Server status check failed: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Get available AI models
 */
export async function fetchAvailableAIModels(): Promise<{ models: any[]; count: number }> {
  const response = await fetch(`${getBackendUrl()}/api/ai/models`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch AI models: ${response.status}`);
  }
  
  return response.json();
} 