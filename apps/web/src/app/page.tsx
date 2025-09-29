import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Financial Dashboard - Real-Time Market Intelligence',
  description: 'Advanced financial analytics with real-time market data',
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 nav-clean">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold text-navy-800">FinanceOS</div>
            <div className="hidden md:flex space-x-8">
              <a href="#overview" className="text-gray-700 hover:text-blue-600 transition-colors">Overview</a>
              <a href="#markets" className="text-gray-700 hover:text-blue-600 transition-colors">Markets</a>
              <a href="#analytics" className="text-gray-700 hover:text-blue-600 transition-colors">Analytics</a>
              <a href="/dashboard" className="text-gray-700 hover:text-blue-600 transition-colors">Dashboard</a>
              <a href="/screener" className="text-gray-700 hover:text-blue-600 transition-colors">Screener</a>
                </div>
            <a href="/dashboard" className="financial-button">
              Get Started
            </a>
            </div>
                    </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-20 pb-16 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-6xl md:text-8xl font-light mb-8 leading-none text-gray-900">
            Financial
            <br />
            <span className="font-bold text-blue-600">Intelligence</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Real-time market data with advanced technical analysis.
            No mock data. Pure intelligence.
          </p>
          
          {/* Hero Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <div className="text-center p-6 bg-white rounded-lg shadow-sm">
              <div className="text-4xl font-bold text-green-600 mb-2">$2.8T</div>
              <div className="text-gray-600">Market Cap Tracked</div>
                    </div>
            <div className="text-center p-6 bg-white rounded-lg shadow-sm">
              <div className="text-4xl font-bold text-blue-600 mb-2">99.9%</div>
              <div className="text-gray-600">Uptime Guarantee</div>
                </div>
            <div className="text-center p-6 bg-white rounded-lg shadow-sm">
              <div className="text-4xl font-bold text-amber-600 mb-2">&lt;50ms</div>
              <div className="text-gray-600">Data Latency</div>
                    </div>
                    </div>

          <button className="financial-button text-lg px-12 py-4">
            Start Trading
                        </button>
                    </div>
      </section>

      {/* Features Grid */}
      <section id="overview" className="py-20 px-6 bg-gray-100">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-5xl font-light text-center mb-16 text-gray-900">
            Advanced <span className="font-bold text-blue-600">Analytics</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="group cursor-pointer">
              <div className="financial-card rounded-lg p-8 h-64 flex flex-col justify-between hover:shadow-lg transition-all">
                <div>
                  <div className="text-3xl mb-4">📈</div>
                  <h3 className="text-xl font-semibold mb-2 text-gray-900">Real-Time Data</h3>
                  <p className="text-gray-600 text-sm">Live market data from multiple exchanges with sub-second latency</p>
                        </div>
                <div className="text-green-600 font-mono text-sm">Alpha Vantage • Finnhub • Polygon</div>
                </div>
            </div>

            <div className="group cursor-pointer">
              <div className="financial-card rounded-lg p-8 h-64 flex flex-col justify-between hover:shadow-lg transition-all">
                <div>
                  <div className="text-3xl mb-4">🧠</div>
                  <h3 className="text-xl font-semibold mb-2 text-gray-900">Technical Analysis</h3>
                  <p className="text-gray-600 text-sm">MACD, RSI, Bollinger Bands, and 50+ technical indicators</p>
                    </div>
                <div className="text-blue-600 font-mono text-sm">Advanced Algorithms</div>
                </div>
                    </div>

            <div className="group cursor-pointer">
              <div className="financial-card rounded-lg p-8 h-64 flex flex-col justify-between hover:shadow-lg transition-all">
                <div>
                  <div className="text-3xl mb-4">📰</div>
                  <h3 className="text-xl font-semibold mb-2 text-gray-900">Market Intelligence</h3>
                  <p className="text-gray-600 text-sm">AI-powered news analysis and market sentiment tracking</p>
                    </div>
                <div className="text-purple-600 font-mono text-sm">Real-Time Feeds</div>
                </div>
            </div>

            <div className="group cursor-pointer">
              <div className="financial-card rounded-lg p-8 h-64 flex flex-col justify-between hover:shadow-lg transition-all">
                <div>
                  <div className="text-3xl mb-4">⚡</div>
                  <h3 className="text-xl font-semibold mb-2 text-gray-900">Lightning Fast</h3>
                  <p className="text-gray-600 text-sm">Next.js 15 with optimized API routes and caching layers</p>
                    </div>
                <div className="text-amber-600 font-mono text-sm">Blazing Performance</div>
                </div>
                        </div>
                        </div>
                        </div>
      </section>

      {/* Market Data Section */}
      <section id="markets" className="py-20 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-5xl font-light text-center mb-16 text-gray-900">
            Live <span className="font-bold text-blue-600">Markets</span>
          </h2>

          <div className="financial-card rounded-xl p-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
              <div className="text-center p-6 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600 mb-1">24,467.80</div>
                <div className="text-gray-600 text-sm">NIFTY 50</div>
                <div className="text-green-600 text-xs">+1.2%</div>
                    </div>
              <div className="text-center p-6 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600 mb-1">80,845.00</div>
                <div className="text-gray-600 text-sm">SENSEX</div>
                <div className="text-green-600 text-xs">+0.8%</div>
                </div>
              <div className="text-center p-6 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600 mb-1">51,234.50</div>
                <div className="text-gray-600 text-sm">BANK NIFTY</div>
                <div className="text-red-600 text-xs">-0.3%</div>
                </div>
            </div>

            <div className="text-center">
              <button className="financial-button-outline px-8 py-3">
                View Full Market Data
              </button>
                </div>
                    </div>
                </div>
      </section>

      {/* API Section */}
      <section id="analytics" className="py-20 px-6 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-5xl font-light text-center mb-16 text-gray-900">
            Developer <span className="font-bold text-blue-600">APIs</span>
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div>
              <h3 className="text-2xl font-semibold mb-6 text-gray-900">Real-Time Endpoints</h3>
              <div className="space-y-4">
                <div className="financial-card rounded-lg p-6">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="bg-green-600 text-white px-2 py-1 rounded text-xs font-mono">GET</span>
                    <code className="text-blue-600">/api/stock-data</code>
                    </div>
                  <p className="text-gray-600 text-sm">Real-time stock quotes with technical indicators</p>
                </div>

                <div className="financial-card rounded-lg p-6">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="bg-green-600 text-white px-2 py-1 rounded text-xs font-mono">GET</span>
                    <code className="text-blue-600">/api/news</code>
                    </div>
                  <p className="text-gray-600 text-sm">Latest financial news from multiple sources</p>
            </div>

                <div className="financial-card rounded-lg p-6">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="bg-green-600 text-white px-2 py-1 rounded text-xs font-mono">GET</span>
                    <code className="text-blue-600">/api/market-overview</code>
                        </div>
                  <p className="text-gray-600 text-sm">Market summary and major indices</p>
                    </div>
                </div>
            </div>

            <div>
              <h3 className="text-2xl font-semibold mb-6 text-gray-900">Example Response</h3>
              <div className="financial-card rounded-lg p-6">
                <pre className="text-sm text-gray-700 overflow-x-auto">
{`{
  "symbol": "AAPL",
  "currentPrice": 182.52,
  "change": 2.34,
  "changePercent": 1.30,
  "indicators": {
    "rsi": 62.4,
    "macd": {
      "MACD": 1.23,
      "signal": 0.98,
      "histogram": 0.25
    },
    "bollingerBands": {
      "upper": 185.67,
      "middle": 180.23,
      "lower": 174.79
    }
  }
}`}
                </pre>
                    </div>
                </div>
                    </div>
                    </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 bg-gray-100">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl font-light mb-8 text-gray-900">
            Ready to <span className="font-bold text-blue-600">Trade?</span>
          </h2>
          <p className="text-xl text-gray-600 mb-12">
            Experience the future of financial data with our lightning-fast platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="financial-button text-lg px-8 py-4">
              Start Free Trial
            </button>
            <button className="financial-button-outline text-lg px-8 py-4">
              View Documentation
            </button>
                    </div>
                    </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-12 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="text-xl font-bold mb-4 text-blue-600">FinanceOS</div>
              <p className="text-gray-600 text-sm">
                Advanced financial intelligence platform powered by real-time market data.
              </p>
                    </div>
            <div>
              <h4 className="font-semibold mb-4 text-gray-900">Platform</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-blue-600 transition-colors">Markets</a></li>
                <li><a href="#" className="hover:text-blue-600 transition-colors">Analytics</a></li>
                <li><a href="#" className="hover:text-blue-600 transition-colors">News</a></li>
                <li><a href="#" className="hover:text-blue-600 transition-colors">API</a></li>
              </ul>
                </div>
            <div>
              <h4 className="font-semibold mb-4 text-gray-900">Resources</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-blue-600 transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-blue-600 transition-colors">Support</a></li>
                <li><a href="#" className="hover:text-blue-600 transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-blue-600 transition-colors">Status</a></li>
              </ul>
                    </div>
            <div>
              <h4 className="font-semibold mb-4 text-gray-900">Company</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-blue-600 transition-colors">About</a></li>
                <li><a href="#" className="hover:text-blue-600 transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-blue-600 transition-colors">Privacy</a></li>
                <li><a href="#" className="hover:text-blue-600 transition-colors">Terms</a></li>
              </ul>
                </div>
            </div>
          <div className="border-t border-gray-200 mt-12 pt-8 text-center text-gray-600 text-sm">
            © 2024 FinanceOS. Real data • Advanced analytics • Lightning fast
        </div>
    </div>
      </footer>
    </div>
  )
}