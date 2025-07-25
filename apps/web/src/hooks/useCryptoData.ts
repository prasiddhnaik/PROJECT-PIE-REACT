import { useState, useEffect, useCallback, useRef } from 'react';

interface CryptoData {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  market_cap: number;
  market_cap_rank: number;
  price_change_percentage_24h: number;
  price_change_percentage_1h_in_currency?: number;
  price_change_percentage_7d_in_currency?: number;
  price_change_percentage_30d_in_currency?: number;
  price_change_percentage_1y_in_currency?: number;
  total_volume: number;
  circulating_supply?: number;
  total_supply?: number;
  ath?: number;
  ath_change_percentage?: number;
  atl?: number;
  atl_change_percentage?: number;
  high_24h?: number;
  low_24h?: number;
  source?: string;
  image?: {
    thumb?: string;
    small?: string;
    large?: string;
  };
  last_updated?: string;
}

interface UseCryptoDataResult {
  data: CryptoData | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
  isStale: boolean;
}

interface CacheEntry {
  data: CryptoData;
  timestamp: number;
  expiresAt: number;
}

// Cache configuration
const CACHE_DURATION = 30 * 1000; // 30 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// In-memory cache
const cache = new Map<string, CacheEntry>();

// Validate crypto data structure
const validateCryptoData = (data: any): data is CryptoData => {
  if (!data || typeof data !== 'object') return false;
  
  const requiredFields = ['id', 'symbol', 'name', 'current_price'];
  const hasRequiredFields = requiredFields.every(field => 
    data[field] !== undefined && data[field] !== null
  );
  
  if (!hasRequiredFields) return false;
  
  // Validate numeric fields
  const numericFields = ['current_price', 'market_cap', 'market_cap_rank', 'total_volume'];
  for (const field of numericFields) {
    if (data[field] !== undefined && (isNaN(data[field]) || data[field] < 0)) {
      return false;
    }
  }
  
  return true;
};

// Check if cache entry is valid
const isCacheValid = (entry: CacheEntry): boolean => {
  return Date.now() < entry.expiresAt;
};

// Get cached data if valid
const getCachedData = (symbol: string): CryptoData | null => {
  const entry = cache.get(symbol);
  if (entry && isCacheValid(entry)) {
    return entry.data;
  }
  
  // Remove expired entry
  if (entry) {
    cache.delete(symbol);
  }
  
  return null;
};

// Cache data with expiration
const setCachedData = (symbol: string, data: CryptoData): void => {
  const now = Date.now();
  const entry: CacheEntry = {
    data,
    timestamp: now,
    expiresAt: now + CACHE_DURATION,
  };
  
  cache.set(symbol, entry);
  
  // Cleanup old entries periodically
  if (cache.size > 100) {
    const cutoff = now - CACHE_DURATION * 2;
    for (const [key, value] of cache.entries()) {
      if (value.timestamp < cutoff) {
        cache.delete(key);
      }
    }
  }
};

// Sleep utility for retry delays
const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

export const useCryptoData = (symbol: string): UseCryptoDataResult => {
  const [data, setData] = useState<CryptoData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isStale, setIsStale] = useState(false);
  
  const abortControllerRef = useRef<AbortController | null>(null);
  const retryCountRef = useRef(0);
  const lastFetchRef = useRef<number>(0);

  const fetchCryptoData = useCallback(async (retryCount = 0): Promise<void> => {
    if (!symbol) {
      setError('Symbol is required');
      setIsLoading(false);
      return;
    }

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    try {
      setIsLoading(true);
      setError(null);

      // Check cache first
      const cachedData = getCachedData(symbol);
      if (cachedData && retryCount === 0) {
        setData(cachedData);
        setIsLoading(false);
        setIsStale(false);
        return;
      }

      // Add retry delay for subsequent attempts
      if (retryCount > 0) {
        const delay = RETRY_DELAY * Math.pow(2, retryCount - 1); // Exponential backoff
        await sleep(Math.min(delay, 10000)); // Max 10 seconds
      }

      const baseURL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001';
      const url = `${baseURL}/api/crypto/${encodeURIComponent(symbol)}`;

      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': Math.random().toString(36).substring(2),
        },
        signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const responseData = await response.json();
      
      // Handle different response formats
      let cryptoData: any;
      if (responseData.data) {
        cryptoData = responseData.data;
      } else if (responseData.result) {
        cryptoData = responseData.result;
      } else if (validateCryptoData(responseData)) {
        cryptoData = responseData;
      } else {
        throw new Error('Invalid response format');
      }

      // Validate data structure
      if (!validateCryptoData(cryptoData)) {
        throw new Error('Invalid crypto data structure');
      }

      // Normalize data
      const normalizedData: CryptoData = {
        id: cryptoData.id,
        symbol: cryptoData.symbol,
        name: cryptoData.name,
        current_price: Number(cryptoData.current_price || 0),
        market_cap: Number(cryptoData.market_cap || 0),
        market_cap_rank: Number(cryptoData.market_cap_rank || 0),
        price_change_percentage_24h: Number(cryptoData.price_change_percentage_24h || 0),
        price_change_percentage_1h_in_currency: cryptoData.price_change_percentage_1h_in_currency ? Number(cryptoData.price_change_percentage_1h_in_currency) : undefined,
        price_change_percentage_7d_in_currency: cryptoData.price_change_percentage_7d_in_currency ? Number(cryptoData.price_change_percentage_7d_in_currency) : undefined,
        price_change_percentage_30d_in_currency: cryptoData.price_change_percentage_30d_in_currency ? Number(cryptoData.price_change_percentage_30d_in_currency) : undefined,
        price_change_percentage_1y_in_currency: cryptoData.price_change_percentage_1y_in_currency ? Number(cryptoData.price_change_percentage_1y_in_currency) : undefined,
        total_volume: Number(cryptoData.total_volume || 0),
        circulating_supply: cryptoData.circulating_supply ? Number(cryptoData.circulating_supply) : undefined,
        total_supply: cryptoData.total_supply ? Number(cryptoData.total_supply) : undefined,
        ath: cryptoData.ath ? Number(cryptoData.ath) : undefined,
        ath_change_percentage: cryptoData.ath_change_percentage ? Number(cryptoData.ath_change_percentage) : undefined,
        atl: cryptoData.atl ? Number(cryptoData.atl) : undefined,
        atl_change_percentage: cryptoData.atl_change_percentage ? Number(cryptoData.atl_change_percentage) : undefined,
        image: cryptoData.image || undefined,
        last_updated: cryptoData.last_updated || new Date().toISOString(),
      };

      // Cache the data
      setCachedData(symbol, normalizedData);
      
      setData(normalizedData);
      setIsStale(false);
      retryCountRef.current = 0;
      lastFetchRef.current = Date.now();

    } catch (err) {
      // Don't set error for aborted requests
      if (signal.aborted) {
        return;
      }

      console.error(`Crypto data fetch error (attempt ${retryCount + 1}):`, err);

      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch crypto data';
      
      // Retry logic
      if (retryCount < MAX_RETRIES && !signal.aborted) {
        retryCountRef.current = retryCount + 1;
        await fetchCryptoData(retryCount + 1);
        return;
      }

      // Check if we have stale cached data to fall back to
      const staleData = cache.get(symbol);
      if (staleData) {
        setData(staleData.data);
        setIsStale(true);
        setError(`Using cached data: ${errorMessage}`);
      } else {
        setError(errorMessage);
      }
      
      retryCountRef.current = 0;
    } finally {
      setIsLoading(false);
    }
  }, [symbol]);

  const refetch = useCallback(() => {
    // Prevent rapid successive calls
    const now = Date.now();
    if (now - lastFetchRef.current < 1000) {
      return;
    }
    
    fetchCryptoData();
  }, [fetchCryptoData]);

  // Initial fetch and periodic updates
  useEffect(() => {
    if (!symbol) return;

    fetchCryptoData();

    // Set up periodic refresh
    const interval = setInterval(() => {
      if (document.visibilityState === 'visible') {
        fetchCryptoData();
      }
    }, CACHE_DURATION);

    // Cleanup function
    return () => {
      clearInterval(interval);
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [symbol, fetchCryptoData]);

  // Handle page visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && data) {
        // Check if data is stale when page becomes visible
        const cacheEntry = cache.get(symbol);
        if (!cacheEntry || !isCacheValid(cacheEntry)) {
          setIsStale(true);
          fetchCryptoData();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [data, symbol, fetchCryptoData]);

  return {
    data,
    isLoading,
    error,
    refetch,
    isStale,
  };
};

export function useServerStatus() {
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [latency, setLatency] = useState<number | null>(null);

  const checkConnection = useCallback(async () => {
    setLoading(true);
    const start = Date.now();

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001'}/test`);
      const responseTime = Date.now() - start;
      
      if (response.ok) {
        setIsConnected(true);
        setLatency(responseTime);
      } else {
        setIsConnected(false);
        setLatency(null);
      }
    } catch {
      setIsConnected(false);
      setLatency(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, [checkConnection]);

  return { isConnected, loading, latency, checkConnection };
} 