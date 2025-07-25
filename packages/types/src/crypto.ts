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
  circulating_supply?: number;
  total_supply?: number;
  max_supply?: number | null;
  ath?: number;
  ath_change_percentage?: number;
  ath_date?: string;
  atl?: number;
  atl_change_percentage?: number;
  atl_date?: string;
  last_updated: string;
  asset_type: string;
}

export interface CryptoAnalysisData {
  symbol: string;
  current_price: number;
  change: number;
  change_percent: number;
  volume: number;
  high_24h?: number;
  low_24h?: number;
  market_cap?: number;
  timestamp: string;
}

export interface AIAnalysisResult {
  content: string;
  model_used: string;
  confidence: number;
  tokens_used: number;
  cost_estimate: number;
}

export interface CryptoAnalysisResponse {
  symbol: string;
  crypto_data?: CryptoAnalysisData;
  ai_analysis?: AIAnalysisResult;
  message?: string;
  timestamp: string;
}

export interface CryptoMarketData {
  trending_crypto: Top100Crypto[];
  top_crypto: Top100Crypto[];
  market_summary: {
    total_market_cap: number;
    total_volume: number;
    market_cap_change_24h: number;
    active_cryptocurrencies: number;
  };
  timestamp: string;
}

export interface CryptoServerStatus {
  status: string;
  server: string;
  port: number;
  timestamp: string;
  available_apis: string[];
}

export interface AIModel {
  id: string;
  name: string;
  provider: string;
  optimized_for: string;
}

export interface CryptoTechnicalIndicators {
  rsi: number;
  sma_20: number;
  sma_50: number;
  sma_200: number;
  bollinger_upper: number;
  bollinger_lower: number;
  macd: number;
  signal: number;
  volume_avg: number;
} 