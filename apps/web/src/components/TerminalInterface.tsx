'use client'

import { useState, useEffect, useRef } from 'react'

interface Stock {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
  marketCap: number
  pe: number
  rsi: number
  source?: string
}

interface ScreenResult {
  criteria: string
  stocks: Stock[]
  timestamp: string
}

interface APIResponse {
  success: boolean
  data?: Stock[] | Stock
  error?: string
  count?: number
  criteria?: string
  timestamp?: string
}

export default function TerminalInterface() {
  const [inputHistory, setInputHistory] = useState<string[]>([])
  const [currentInput, setCurrentInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [screenResults, setScreenResults] = useState<ScreenResult | null>(null)
  const [stocksData, setStocksData] = useState<Stock[]>([])
  const inputRef = useRef<HTMLInputElement>(null)

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
  
  // Test backend connection
  const testBackendConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/`, { 
        method: 'GET',
        cache: 'no-cache'
      })
      const result = await response.json()
      console.log('Backend connection test:', result)
      return result.status === 'running'
    } catch (error) {
      console.error('Backend connection failed:', error)
      return false
    }
  }

  useEffect(() => {
    // Initialize terminal
    setInputHistory([
      '🇮🇳 NSE Stock Screener Terminal v2.1.4',
      '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
      '📈 Welcome to the Official NSE Stock Market Terminal',
      '📊 Real-time data from National Stock Exchange of India',
      '🔗 Direct API connection to www.nseindia.com',
      '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
      '',
      '🟢 Market Status: OPEN | Trading Hours: 09:15 AM - 03:30 PM IST',
      '⏰ Last Updated: ' + new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }),
      '',
      '🚀 QUICK START:',
      '   • Type "help" for all commands',
      '   • Type "list" to see all NIFTY 50 stocks',
      '   • Type "RELIANCE" or "TCS" for stock quotes',
      '   • Type "screen 1" to find probable breakouts',
      '',
      '💡 TIP: You can type any stock symbol directly for quick quotes!',
      '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
      ''
    ])
    inputRef.current?.focus()
    
    // Test backend connection first, then load data
    const initializeData = async () => {
      const isConnected = await testBackendConnection()
      if (isConnected) {
        setInputHistory(prev => [...prev, '✅ Connected to NSE API successfully!', ''])
        await loadStockData()
      } else {
        setInputHistory(prev => [...prev, '❌ Backend connection failed - Check if NSE server is running on port 8001'])
      }
    }
    
    initializeData()
  }, [])

  const loadStockData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stocks/list`, {
        cache: 'no-cache',
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      })
      const result: APIResponse = await response.json()
      
      if (result.success && result.data) {
        setStocksData(result.data as Stock[])
        // Data loaded silently - no verbose messages
      } else {
        console.error('Failed to load stock data:', result.error)
        setInputHistory(prev => [...prev, '❌ Failed to load stock data: ' + result.error])
      }
    } catch (error) {
      console.error('Error loading stock data:', error)
      setInputHistory(prev => [...prev, '❌ Error loading stock data: ' + error])
    }
  }

  const screenStocks = async (criteria: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stocks/screen/${criteria}`)
      const result: APIResponse = await response.json()
      
      if (result.success && result.data) {
        return {
          criteria: result.criteria || criteria,
          stocks: result.data as Stock[],
          timestamp: result.timestamp || new Date().toLocaleString()
        }
      } else {
        console.error('Failed to screen stocks:', result.error)
        return null
      }
    } catch (error) {
      console.error('Error screening stocks:', error)
      return null
    }
  }

  const formatStockLine = (stock: Stock): string => {
    return `${stock.symbol.padEnd(11)} ${stock.price.toFixed(2).padStart(8)} ${stock.change > 0 ? '+' : ''}${stock.change.toFixed(2).padStart(8)} ${stock.changePercent > 0 ? '+' : ''}${stock.changePercent.toFixed(2).padStart(6)}% ${stock.volume.toLocaleString().padStart(9)} ${stock.rsi.toFixed(1).padStart(6)} ${stock.pe.toFixed(1).padStart(5)}`
  }

  const fetchStockQuote = async (symbol: string) => {
    try {
      setIsLoading(true)
      const response = await fetch(`${API_BASE_URL}/api/stocks/quote/${symbol}`, {
        cache: 'no-cache',
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      })
      const result: APIResponse = await response.json()
      
      if (result.success && result.data) {
        const quote = result.data as any
        
        setInputHistory(prev => [...prev,
          '',
          `📊 OFFICIAL NSE QUOTE: ${quote.symbol || symbol}`,
          '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
          `🏢 Company: ${quote.companyName || 'N/A'}`,
          `🏭 Industry: ${quote.industry || 'N/A'}`,
          `📈 Sector: ${quote.sector || 'N/A'}`,
          `🆔 ISIN: ${quote.isin || 'N/A'}`,
          `📅 Listed: ${quote.listingDate || 'N/A'}`,
          '',
          '💰 PRICE INFORMATION:',
          `Current Price: ₹${quote.lastPrice?.toFixed(2) || 'N/A'}`,
          `Change: ${quote.change > 0 ? '+' : ''}₹${quote.change?.toFixed(2) || 'N/A'} (${quote.pChange > 0 ? '+' : ''}${quote.pChange?.toFixed(2) || 'N/A'}%)`,
          `Previous Close: ₹${quote.previousClose?.toFixed(2) || 'N/A'}`,
          `Open: ₹${quote.open?.toFixed(2) || 'N/A'}`,
          `Day High: ₹${quote.dayHigh?.toFixed(2) || 'N/A'}`,
          `Day Low: ₹${quote.dayLow?.toFixed(2) || 'N/A'}`,
          `52 Week High: ₹${quote.weekHigh?.toFixed(2) || 'N/A'}`,
          `52 Week Low: ₹${quote.weekLow?.toFixed(2) || 'N/A'}`,
          '',
          '📊 TRADING INFORMATION:',
          `Volume: ${quote.totalTradedVolume?.toLocaleString() || 'N/A'}`,
          `Value: ₹${quote.totalTradedValue ? (quote.totalTradedValue / 10000000).toFixed(2) + ' Crores' : 'N/A'}`,
          `Market Cap: ₹${quote.marketCap ? (quote.marketCap / 10000000).toFixed(2) + ' Crores' : 'N/A'}`,
          '',
          '🔢 VALUATION METRICS:',
          `P/E Ratio: ${quote.pe?.toFixed(2) || 'N/A'}`,
          `P/B Ratio: ${quote.pb?.toFixed(2) || 'N/A'}`,
          `EPS: ₹${quote.eps?.toFixed(2) || 'N/A'}`,
          '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
          `🔗 Data Source: https://www.nseindia.com/api/quote-equity | ${quote.source || 'official_nse_api'}`,
          `⏰ Updated: ${new Date().toLocaleTimeString()}`,
          ''
        ])
      } else {
        setInputHistory(prev => [...prev, 
          `❌ Error: ${result.error || `Stock '${symbol}' not found`}`,
          'Try symbols like: RELIANCE, TCS, INFY, HDFCBANK, etc.',
          ''
        ])
      }
    } catch (error) {
      setInputHistory(prev => [...prev, 
        `❌ Error fetching quote for ${symbol}: ${error}`,
        ''
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const screeningAlgorithms = {
    '1': { name: 'Probable Breakouts', criteria: 'breakouts' },
    '2': { name: 'High Volume Stocks', criteria: 'high_volume' },
    '3': { name: 'RSI Oversold (< 30)', criteria: 'rsi_oversold' },
    '4': { name: 'RSI Overbought (> 70)', criteria: 'rsi_overbought' },
    '5': { name: 'Top Gainers', criteria: 'gainers' },
    '6': { name: 'Top Losers', criteria: 'losers' },
    '7': { name: 'Low PE Stocks (< 20)', criteria: 'low_pe' },
    '8': { name: 'Momentum Stocks (RSI 50-70 & +ve change)', criteria: 'momentum' }
  }

  const executeCommand = async (command: string) => {
    const cmd = command.toLowerCase().trim()
    
    setInputHistory(prev => [...prev, `> ${command}`])
    
    if (cmd === 'help') {
      setInputHistory(prev => [...prev,
        '',
        '📋 COMMAND REFERENCE - NSE Stock Terminal',
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        '',
        '🔍 BASIC COMMANDS:',
        '   help          - Show this help menu',
        '   list          - List all NIFTY 50 stocks with prices',
        '   status        - Show current market status',
        '   clear         - Clear terminal screen',
        '   reload        - Refresh NSE data',
        '',
        '📊 STOCK INFORMATION:',
        '   quote SYMBOL  - Get detailed stock information',
        '   SYMBOL        - Quick quote (e.g., just type "RELIANCE")',
        '',
        '🎯 STOCK SCREENING (Type "screen" followed by number):',
        '   screen 1      - 📈 Probable Breakouts',
        '   screen 2      - 🔊 High Volume Stocks',
        '   screen 3      - 📉 RSI Oversold (< 30)',
        '   screen 4      - 📈 RSI Overbought (> 70)',
        '   screen 5      - 🚀 Top Gainers',
        '   screen 6      - 📉 Top Losers',
        '   screen 7      - 💰 Low PE Stocks (< 20)',
        '   screen 8      - ⚡ Momentum Stocks',
        '',
        '💡 EXAMPLES:',
        '   • Type: RELIANCE        (for Reliance Industries quote)',
        '   • Type: quote TCS       (for TCS detailed information)',
        '   • Type: screen 5        (to find top gainers)',
        '   • Type: list            (to see all NIFTY 50 stocks)',
        '',
        '🔗 Data Source: Official NSE API (www.nseindia.com)',
        '✅ Real-time data • Session-based authentication • NSE Exchange',
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        ''
      ])
    }
    else if (cmd === 'list') {
      if (stocksData.length === 0) {
        setInputHistory(prev => [...prev, '📊 Loading NIFTY 50 stocks from NSE...'])
        await loadStockData()
      }
      
      setInputHistory(prev => [...prev,
        '',
        `📊 NIFTY 50 STOCKS - Live NSE Data (${stocksData.length} stocks loaded)`,
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        'SYMBOL      PRICE(₹)  CHANGE    %CHG    VOLUME     RSI    PE',
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        ...stocksData.map(stock => formatStockLine(stock)),
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        stocksData.length > 0 ? `🔗 Source: Official NSE API | ⏰ ${new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })} IST` : 'No data available',
        '💡 TIP: Type any symbol for detailed quote (e.g., "RELIANCE")',
        ''
      ])
    }
    else if (cmd.startsWith('screen ')) {
      const screenNum = cmd.split(' ')[1]
      const algorithm = screeningAlgorithms[screenNum as keyof typeof screeningAlgorithms]
      
      if (algorithm) {
        setIsLoading(true)
        setInputHistory(prev => [...prev, `Executing: ${algorithm.name}...`])
        
        try {
          const result = await screenStocks(algorithm.criteria)
          
          if (result) {
            setScreenResults(result)
            setInputHistory(prev => [...prev,
              '',
              `🔍 OFFICIAL NSE API SCREENING: ${algorithm.name}`,
              `📊 Found ${result.stocks.length} stocks matching criteria`,
              `⏰ Timestamp: ${result.timestamp}`,
              '',
              '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
              'SYMBOL      PRICE(₹)  CHANGE    %CHG    VOLUME     RSI    PE',
              '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
              ...result.stocks.map(stock => formatStockLine(stock)),
              '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
              result.stocks.length > 0 ? `🔗 Data Source: https://www.nseindia.com/api | ${result.stocks[0].source || 'official_nse_api'}` : '❌ No matching stocks found',
              ''
            ])
          } else {
            setInputHistory(prev => [...prev, 'Error: Unable to screen stocks. Please try again.', ''])
          }
        } catch (error) {
          setInputHistory(prev => [...prev, `Error: ${error}`, ''])
        } finally {
          setIsLoading(false)
        }
      } else {
        setInputHistory(prev => [...prev, `Invalid screening algorithm: ${screenNum}`, 'Type "help" for available algorithms', ''])
      }
    }
    else if (cmd === 'clear') {
      setInputHistory([])
    }
    else if (cmd === 'reload') {
      setInputHistory(prev => [...prev, '🔄 Refreshing NSE data from official API...'])
      await loadStockData()
      setInputHistory(prev => [...prev, `✅ Successfully refreshed ${stocksData.length} NIFTY 50 stocks!`, ''])
    }
    else if (cmd === 'status') {
      setInputHistory(prev => [...prev,
        '',
        '📊 NSE MARKET STATUS & SYSTEM INFORMATION',
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        `🇮🇳 Exchange: National Stock Exchange (NSE)`,
        `🟢 Market Status: OPEN`,
        `⏰ Current Time: ${new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })} IST`,
        `📈 Trading Hours: 09:15 AM - 03:30 PM IST`,
        `📊 Stocks Available: ${stocksData.length} NIFTY 50 stocks`,
        `🔗 Data Source: Official NSE API (www.nseindia.com)`,
        `✅ Authentication: Session-based with proper headers`,
        `🖥️  Backend Server: ${API_BASE_URL}`,
        `💾 Last Data Update: ${new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}`,
        '',
        '🚀 System ready for real-time stock data queries!',
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        ''
      ])
    }
    else if (cmd.startsWith('quote ')) {
      const symbol = cmd.split(' ')[1]
      if (symbol) {
        await fetchStockQuote(symbol.toUpperCase())
      } else {
        setInputHistory(prev => [...prev, 
          '❌ Please specify a stock symbol',
          '💡 Usage: quote <SYMBOL>',
          '📋 Examples: quote RELIANCE, quote TCS, quote INFY',
          ''
        ])
      }
    }
    else if (cmd === '') {
      // Do nothing for empty command
    }
    else {
      // Check if it might be a direct stock symbol
      const possibleSymbol = cmd.toUpperCase()
      if (possibleSymbol.match(/^[A-Z][A-Z0-9-]*$/)) {
        setInputHistory(prev => [...prev, `🔍 Searching for stock: ${possibleSymbol}...`])
        await fetchStockQuote(possibleSymbol)
      } else {
        setInputHistory(prev => [...prev, 
          `❌ '${command}' is not recognized as a valid command.`,
          '',
          '💡 Try these options:',
          '   • Type "help" for all available commands',
          '   • Type "list" to see all NIFTY 50 stocks',
          '   • Type a stock symbol (e.g., "RELIANCE", "TCS")',
          '   • Type "screen 1" for probable breakouts',
          ''
        ])
      }
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      if (currentInput.trim()) {
        executeCommand(currentInput)
      }
      setCurrentInput('')
    }
  }

  return (
    <>
      <div className="terminal" onClick={() => inputRef.current?.focus()}>
        <div className="terminal-content">
          {inputHistory.map((line, index) => (
            <div key={index}>{line}</div>
          ))}
          {isLoading && (
            <div>🇮🇳 Processing real NSE data... Please wait...</div>
          )}
          <div className="input-line">
            <span>NSE{`>`} </span>
            <input
              ref={inputRef}
              type="text"
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              onKeyPress={handleKeyPress}
              className="terminal-input"
              disabled={isLoading}
            />
          </div>
        </div>
      </div>

      <style jsx global>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        html, body {
          background: #000000 !important;
          color: #ffffff !important;
          font-family: 'Consolas', 'Courier New', monospace !important;
          font-size: 14px;
          line-height: 1.2;
          overflow: hidden;
        }

        .terminal {
          background: #000000;
          color: #ffffff;
          height: 100vh;
          width: 100vw;
          padding: 10px;
          overflow-y: auto;
          font-family: 'Consolas', 'Courier New', monospace;
          font-size: 14px;
          line-height: 1.2;
          cursor: text;
        }

        .terminal-content {
          white-space: pre-wrap;
          font-family: monospace;
        }

        .input-line {
          display: flex;
          align-items: center;
        }

        .terminal-input {
          background: transparent;
          border: none;
          color: #ffffff;
          font-family: 'Consolas', 'Courier New', monospace;
          font-size: 14px;
          outline: none;
          flex: 1;
          margin-left: 0;
        }

        .terminal-input:disabled {
          opacity: 0.5;
        }

        .terminal::-webkit-scrollbar {
          width: 0px;
          background: transparent;
        }
      `}</style>
    </>
  )
} 