import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'FinanceFlow - Professional Financial Intelligence',
  description: 'Clean, professional financial intelligence platform with real-time market data, advanced analytics, and institutional-grade insights for serious traders.',
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      {/* Clean Navigation */}
      <nav className="fixed top-0 w-full z-50 nav-clean">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">F</span>
              </div>
              <span className="text-xl font-semibold text-gray-800">
                FinanceFlow
              </span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">Features</a>
              <a href="#markets" className="text-gray-600 hover:text-gray-900 transition-colors">Markets</a>
              <a href="#analytics" className="text-gray-600 hover:text-gray-900 transition-colors">Analytics</a>
              <a href="/dashboard" className="text-gray-600 hover:text-gray-900 transition-colors">Dashboard</a>
              <a href="/screener" className="text-gray-600 hover:text-gray-900 transition-colors">Screener</a>
                </div>
            <button className="clean-button text-sm px-4 py-2">
              Get Started
            </button>
            </div>
                    </div>
      </nav>

      {/* Clean Hero Section */}
      <section className="pt-24 pb-16 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 text-gray-900 leading-tight">
            Financial Intelligence
            <span className="block text-3xl md:text-5xl font-normal text-gray-600 mt-2">
              Platform
            </span>
          </h1>

          <p className="text-lg md:text-xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
            Real-time market data with advanced technical analysis.
            Professional-grade financial intelligence for serious traders.
          </p>

          {/* Hero Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="clean-card p-6 text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">$2.8T+</div>
              <div className="text-gray-600 text-sm">Market Cap Tracked</div>
                    </div>
            <div className="clean-card p-6 text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">99.9%</div>
              <div className="text-gray-600 text-sm">Uptime Guarantee</div>
                </div>
            <div className="clean-card p-6 text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">&lt;50ms</div>
              <div className="text-gray-600 text-sm">Data Latency</div>
                    </div>
                    </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="clean-button px-6 py-3">
              Get Started
            </button>
            <button className="clean-button-outline px-6 py-3">
              Learn More
            </button>
          </div>
                    </div>
      </section>

      {/* Clean Features Section */}
      <section id="features" className="py-16 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">
              Powerful Features
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Everything you need for professional-grade financial analysis and trading insights.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="clean-card p-6 text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-green-600 text-xl">📈</span>
              </div>
              <h3 className="text-lg font-semibold mb-3 text-gray-900">Real-Time Data</h3>
              <p className="text-gray-600 text-sm leading-relaxed">Live market data from multiple exchanges with sub-second latency</p>
              <div className="mt-3 text-green-600 text-xs font-medium">
                Alpha Vantage • Finnhub • Polygon
              </div>
            </div>

            <div className="clean-card p-6 text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-blue-600 text-xl">🧠</span>
              </div>
              <h3 className="text-lg font-semibold mb-3 text-gray-900">Technical Analysis</h3>
              <p className="text-gray-600 text-sm leading-relaxed">MACD, RSI, Bollinger Bands, and 50+ technical indicators</p>
              <div className="mt-3 text-blue-600 text-xs font-medium">
                Advanced Algorithms
              </div>
            </div>

            <div className="clean-card p-6 text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-purple-600 text-xl">📰</span>
              </div>
              <h3 className="text-lg font-semibold mb-3 text-gray-900">Market Intelligence</h3>
              <p className="text-gray-600 text-sm leading-relaxed">AI-powered news analysis and market sentiment tracking</p>
              <div className="mt-3 text-purple-600 text-xs font-medium">
                Real-Time Feeds
              </div>
            </div>

            <div className="clean-card p-6 text-center">
              <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-amber-600 text-xl">⚡</span>
              </div>
              <h3 className="text-lg font-semibold mb-3 text-gray-900">Lightning Fast</h3>
              <p className="text-gray-600 text-sm leading-relaxed">Next.js 15 with optimized API routes and caching layers</p>
              <div className="mt-3 text-amber-600 text-xs font-medium">
                High Performance
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Clean Market Data Section */}
      <section id="markets" className="py-16 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">
              Live Markets
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Real-time market data from global exchanges with institutional-grade accuracy.
            </p>
          </div>

          <div className="clean-card p-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="text-center p-6 bg-green-50 rounded-lg border border-green-200">
                <div className="text-3xl font-bold text-green-600 mb-2">24,467.80</div>
                <div className="text-gray-700 font-medium mb-1">NIFTY 50</div>
                <div className="text-green-600 text-sm font-medium">+1.2%</div>
              </div>

              <div className="text-center p-6 bg-blue-50 rounded-lg border border-blue-200">
                <div className="text-3xl font-bold text-blue-600 mb-2">80,845.00</div>
                <div className="text-gray-700 font-medium mb-1">SENSEX</div>
                <div className="text-blue-600 text-sm font-medium">+0.8%</div>
              </div>

              <div className="text-center p-6 bg-red-50 rounded-lg border border-red-200">
                <div className="text-3xl font-bold text-red-600 mb-2">51,234.50</div>
                <div className="text-gray-700 font-medium mb-1">BANK NIFTY</div>
                <div className="text-red-600 text-sm font-medium">-0.3%</div>
              </div>
            </div>

            <div className="text-center">
              <button className="clean-button-outline px-6 py-3">
                View Full Market Data
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Clean API Section */}
      <section id="analytics" className="py-16 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">
              Developer APIs
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Powerful REST APIs for seamless integration with your applications and trading systems.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div>
              <h3 className="text-2xl font-semibold mb-6 text-gray-900">Real-Time Endpoints</h3>
              <div className="space-y-4">
                <div className="clean-card p-4 border-l-4 border-green-500">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="bg-green-600 text-white px-2 py-1 rounded text-xs font-mono">GET</span>
                    <code className="text-blue-600 font-mono">/api/stock-data</code>
                  </div>
                  <p className="text-gray-600 text-sm">Real-time stock quotes with technical indicators</p>
                </div>

                <div className="clean-card p-4 border-l-4 border-blue-500">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="bg-blue-600 text-white px-2 py-1 rounded text-xs font-mono">GET</span>
                    <code className="text-blue-600 font-mono">/api/news</code>
                  </div>
                  <p className="text-gray-600 text-sm">Latest financial news from multiple sources</p>
                </div>

                <div className="clean-card p-4 border-l-4 border-purple-500">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="bg-purple-600 text-white px-2 py-1 rounded text-xs font-mono">GET</span>
                    <code className="text-blue-600 font-mono">/api/market-overview</code>
                  </div>
                  <p className="text-gray-600 text-sm">Market summary and major indices</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-2xl font-semibold mb-6 text-gray-900">Example Response</h3>
              <div className="clean-card p-6 bg-gray-800 text-gray-100">
                <pre className="text-sm overflow-x-auto">
{`{
  "symbol": "AAPL",
  "currentPrice": 253.85,
  "change": -1.62,
  "changePercent": -0.63,
  "indicators": {
    "rsi": 62.4,
    "macd": {
      "MACD": 1.23,
      "signal": 0.98,
      "histogram": 0.25
    }
  }
}`}
                </pre>
              </div>
              <div className="mt-4 text-center">
                <button className="clean-button-outline text-sm px-4 py-2">
                  View Documentation
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Clean CTA Section */}
      <section className="py-16 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6 text-gray-900">
            Ready to Get Started?
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Experience the future of financial data with our lightning-fast platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="clean-button px-6 py-3">
              Start Free Trial
            </button>
            <button className="clean-button-outline px-6 py-3">
              View Documentation
            </button>
          </div>
        </div>
      </section>

      {/* Clean Footer */}
      <footer className="bg-gray-800 text-white py-12 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                  <span className="text-gray-800 font-bold">F</span>
                </div>
                <span className="text-xl font-semibold">FinanceFlow</span>
              </div>
              <p className="text-gray-300 text-sm">
                Advanced financial intelligence platform powered by real-time market data.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4 text-white">Platform</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li><a href="#" className="hover:text-white transition-colors">Markets</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Analytics</a></li>
                <li><a href="#" className="hover:text-white transition-colors">News</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4 text-white">Resources</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Support</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Status</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4 text-white">Company</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-700 mt-8 pt-6 text-center text-gray-400 text-sm">
            © 2024 FinanceFlow. Real data • Advanced analytics • Lightning fast
          </div>
        </div>
      </footer>
    </div>
  )
}