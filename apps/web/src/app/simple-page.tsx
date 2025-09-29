import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'ONI Financial Dashboard',
  description: 'Real-time financial market data and analysis',
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-cyan-400 mb-4">
            ONI Financial Dashboard
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Real-time market data with advanced technical analysis and Windows XP nostalgic interface
          </p>
        </header>

        {/* Status Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-slate-800/50 border border-cyan-500/30 rounded-lg p-6 backdrop-blur-sm">
            <h3 className="text-cyan-400 text-lg font-semibold mb-2">✅ Frontend</h3>
            <p className="text-gray-300">Next.js 15 with React</p>
            <p className="text-green-400 text-sm">Running on port 3000</p>
          </div>
          
          <div className="bg-slate-800/50 border border-cyan-500/30 rounded-lg p-6 backdrop-blur-sm">
            <h3 className="text-cyan-400 text-lg font-semibold mb-2">🔗 APIs</h3>
            <p className="text-gray-300">Real market data sources</p>
            <p className="text-yellow-400 text-sm">Alpha Vantage, Finnhub, Polygon</p>
          </div>
          
          <div className="bg-slate-800/50 border border-cyan-500/30 rounded-lg p-6 backdrop-blur-sm">
            <h3 className="text-cyan-400 text-lg font-semibold mb-2">📊 Analytics</h3>
            <p className="text-gray-300">Technical indicators</p>
            <p className="text-blue-400 text-sm">MACD, RSI, Bollinger Bands</p>
          </div>
        </div>

        {/* Features */}
        <div className="bg-slate-800/30 border border-cyan-500/20 rounded-xl p-8 backdrop-blur-sm">
          <h2 className="text-3xl font-bold text-cyan-400 mb-6 text-center">Features</h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-semibold text-white mb-4">📈 Real-Time Data</h3>
              <ul className="space-y-2 text-gray-300">
                <li>• Live stock quotes and market data</li>
                <li>• Multiple data provider fallbacks</li>
                <li>• No mock data - all real APIs</li>
                <li>• Automatic caching for performance</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-white mb-4">🔧 Technical Analysis</h3>
              <ul className="space-y-2 text-gray-300">
                <li>• MACD (Moving Average Convergence Divergence)</li>
                <li>• RSI (Relative Strength Index)</li>
                <li>• Bollinger Bands</li>
                <li>• Simple & Exponential Moving Averages</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-white mb-4">📰 Financial News</h3>
              <ul className="space-y-2 text-gray-300">
                <li>• Real-time market news</li>
                <li>• Multiple news sources</li>
                <li>• Sentiment analysis</li>
                <li>• Categorized by relevance</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-white mb-4">🎨 Windows XP Theme</h3>
              <ul className="space-y-2 text-gray-300">
                <li>• Nostalgic UI design</li>
                <li>• ONI-inspired dark theme</li>
                <li>• Modern functionality</li>
                <li>• Responsive design</li>
              </ul>
            </div>
          </div>
        </div>

        {/* API Endpoints */}
        <div className="mt-12 bg-slate-800/30 border border-cyan-500/20 rounded-xl p-8 backdrop-blur-sm">
          <h2 className="text-2xl font-bold text-cyan-400 mb-6 text-center">Available Endpoints</h2>
          
          <div className="grid gap-4 font-mono text-sm">
            <div className="bg-slate-900/50 border border-gray-600 rounded p-4">
              <span className="text-green-400">GET</span> <span className="text-blue-400">/api/stock-data?symbol=AAPL</span>
              <p className="text-gray-400 text-xs mt-1">Get real-time stock data with technical indicators</p>
            </div>
            
            <div className="bg-slate-900/50 border border-gray-600 rounded p-4">
              <span className="text-green-400">GET</span> <span className="text-blue-400">/api/news</span>
              <p className="text-gray-400 text-xs mt-1">Get latest financial news from multiple sources</p>
            </div>
            
            <div className="bg-slate-900/50 border border-gray-600 rounded p-4">
              <span className="text-green-400">GET</span> <span className="text-blue-400">/api/market-overview</span>
              <p className="text-gray-400 text-xs mt-1">Get market summary and major stock indices</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="text-center mt-12 text-gray-400">
          <p>🚀 PROJECT-PIE-REACT - Modern Financial Dashboard</p>
          <p className="text-sm mt-2">Real data • Technical analysis • Windows XP aesthetic</p>
        </footer>
      </div>
    </div>
  )
}
