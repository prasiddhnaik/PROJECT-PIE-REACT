import React, { useState, useEffect, useRef } from 'react';

interface CryptoSearchResult {
  id: string;
  symbol: string;
  name: string;
  thumb?: string;
  market_cap_rank?: number;
}

interface CryptoSearchProps {
  onSelect: (crypto: CryptoSearchResult) => void;
  placeholder?: string;
  className?: string;
}

// Popular crypto symbols for quick suggestions
const POPULAR_CRYPTOS = [
  { id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', market_cap_rank: 1 },
  { id: 'ethereum', symbol: 'ETH', name: 'Ethereum', market_cap_rank: 2 },
  { id: 'binancecoin', symbol: 'BNB', name: 'BNB', market_cap_rank: 3 },
  { id: 'solana', symbol: 'SOL', name: 'Solana', market_cap_rank: 4 },
  { id: 'ripple', symbol: 'XRP', name: 'XRP', market_cap_rank: 5 },
  { id: 'dogecoin', symbol: 'DOGE', name: 'Dogecoin', market_cap_rank: 6 },
  { id: 'cardano', symbol: 'ADA', name: 'Cardano', market_cap_rank: 7 },
  { id: 'avalanche-2', symbol: 'AVAX', name: 'Avalanche', market_cap_rank: 8 },
  { id: 'chainlink', symbol: 'LINK', name: 'Chainlink', market_cap_rank: 9 },
  { id: 'polkadot', symbol: 'DOT', name: 'Polkadot', market_cap_rank: 10 },
  { id: 'polygon', symbol: 'MATIC', name: 'Polygon', market_cap_rank: 11 },
  { id: 'uniswap', symbol: 'UNI', name: 'Uniswap', market_cap_rank: 12 },
  { id: 'litecoin', symbol: 'LTC', name: 'Litecoin', market_cap_rank: 13 },
  { id: 'stellar', symbol: 'XLM', name: 'Stellar', market_cap_rank: 14 },
  { id: 'filecoin', symbol: 'FIL', name: 'Filecoin', market_cap_rank: 15 },
  { id: 'shiba-inu', symbol: 'SHIB', name: 'Shiba Inu', market_cap_rank: 16 },
  { id: 'monero', symbol: 'XMR', name: 'Monero', market_cap_rank: 17 },
  { id: 'bitcoin-cash', symbol: 'BCH', name: 'Bitcoin Cash', market_cap_rank: 18 },
  { id: 'internet-computer', symbol: 'ICP', name: 'Internet Computer', market_cap_rank: 19 },
  { id: 'toncoin', symbol: 'TON', name: 'Toncoin', market_cap_rank: 20 }
];

export default function CryptoSearch({ onSelect, placeholder = "Search cryptocurrencies...", className = "" }: CryptoSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<CryptoSearchResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<NodeJS.Timeout>();

  // Filter popular cryptos based on query
  const filterPopularCryptos = (searchQuery: string): CryptoSearchResult[] => {
    if (!searchQuery) return POPULAR_CRYPTOS.slice(0, 8);
    
    const lowerQuery = searchQuery.toLowerCase();
    return POPULAR_CRYPTOS.filter(crypto => 
      crypto.symbol.toLowerCase().includes(lowerQuery) ||
      crypto.name.toLowerCase().includes(lowerQuery) ||
      crypto.id.toLowerCase().includes(lowerQuery)
    ).slice(0, 8);
  };

  // Search function
  const searchCryptos = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults(filterPopularCryptos(''));
      return;
    }

    setIsLoading(true);
    
    try {
      // First, try filtering popular cryptos
      const popularResults = filterPopularCryptos(searchQuery);
      
      if (popularResults.length > 0) {
        setResults(popularResults);
      } else {
        // If no popular results, show a "not found" message with suggestions
        setResults([
          {
            id: 'not-found',
            symbol: 'N/A',
            name: `No results for "${searchQuery}"`,
            market_cap_rank: 0
          },
          ...POPULAR_CRYPTOS.slice(0, 5)
        ]);
      }
    } catch (error) {
      console.error('Search error:', error);
      setResults(filterPopularCryptos(''));
    } finally {
      setIsLoading(false);
    }
  };

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      if (isOpen) {
        searchCryptos(query);
      }
    }, 300);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [query, isOpen]);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    setSelectedIndex(-1);
    
    if (value.trim() && !isOpen) {
      setIsOpen(true);
    }
  };

  // Handle selection
  const handleSelect = (crypto: CryptoSearchResult) => {
    if (crypto.id === 'not-found') return;
    
    setQuery(`${crypto.symbol} - ${crypto.name}`);
    setIsOpen(false);
    setSelectedIndex(-1);
    onSelect(crypto);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) {
      if (e.key === 'Enter' || e.key === 'ArrowDown') {
        setIsOpen(true);
        searchCryptos(query);
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < results.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev > 0 ? prev - 1 : results.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && results[selectedIndex]) {
          handleSelect(results[selectedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setSelectedIndex(-1);
        inputRef.current?.blur();
        break;
    }
  };

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSelectedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={searchRef} className={`relative ${className}`}>
      {/* Search Input */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            setIsOpen(true);
            if (!query) searchCryptos('');
          }}
          placeholder={placeholder}
          className="w-full px-4 py-3 pl-12 pr-4 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-2"
          style={{
            backgroundColor: 'var(--background-primary)',
            borderColor: 'var(--border)',
            color: 'var(--text-primary)',
            fontSize: '16px'
          }}
        />
        
        {/* Search Icon */}
        <div className="absolute left-4 top-1/2 transform -translate-y-1/2">
          <svg
            className="w-5 h-5"
            style={{ color: 'var(--text-secondary)' }}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>

        {/* Loading Indicator */}
        {isLoading && (
          <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          </div>
        )}
      </div>

      {/* Results Dropdown */}
      {isOpen && (
        <div 
          className="absolute z-50 w-full mt-2 rounded-lg border shadow-lg max-h-96 overflow-y-auto"
          style={{
            backgroundColor: 'var(--background-primary)',
            borderColor: 'var(--border)'
          }}
        >
          {results.length > 0 ? (
            <div className="py-2">
              {results.map((crypto, index) => (
                <div
                  key={crypto.id}
                  onClick={() => handleSelect(crypto)}
                  className={`px-4 py-3 cursor-pointer transition-colors ${
                    index === selectedIndex ? 'bg-blue-50 dark:bg-blue-900/20' : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                  } ${crypto.id === 'not-found' ? 'cursor-default opacity-60' : ''}`}
                  style={{
                    backgroundColor: index === selectedIndex ? 'var(--background-secondary)' : undefined
                  }}
                >
                  <div className="flex items-center space-x-3">
                    {crypto.market_cap_rank && crypto.market_cap_rank > 0 ? (
                      <div 
                        className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white"
                        style={{ background: 'var(--gradient-primary)' }}
                      >
                        #{crypto.market_cap_rank}
                      </div>
                    ) : crypto.id !== 'not-found' ? (
                      <div 
                        className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white"
                        style={{ background: 'var(--gradient-primary)' }}
                      >
                        {crypto.symbol.slice(0, 1)}
                      </div>
                    ) : (
                      <div className="w-8 h-8 rounded-full flex items-center justify-center bg-gray-300">
                        ❓
                      </div>
                    )}
                    
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span 
                          className="font-semibold"
                          style={{ color: 'var(--text-primary)' }}
                        >
                          {crypto.symbol}
                        </span>
                        {crypto.market_cap_rank && crypto.market_cap_rank > 0 && (
                          <span 
                            className="text-xs px-2 py-1 rounded-full"
                            style={{ 
                              backgroundColor: 'var(--background-secondary)',
                              color: 'var(--text-secondary)'
                            }}
                          >
                            Rank #{crypto.market_cap_rank}
                          </span>
                        )}
                      </div>
                      <div 
                        className="text-sm"
                        style={{ color: 'var(--text-secondary)' }}
                      >
                        {crypto.name}
                      </div>
                    </div>

                    {crypto.id !== 'not-found' && (
                      <div>
                        <svg
                          className="w-4 h-4"
                          style={{ color: 'var(--text-secondary)' }}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 5l7 7-7 7"
                          />
                        </svg>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="px-4 py-8 text-center">
              <div 
                className="text-sm"
                style={{ color: 'var(--text-secondary)' }}
              >
                No cryptocurrencies found
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
} 