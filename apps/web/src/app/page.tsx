import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'FinanceFlow - Advanced Financial Intelligence Platform',
  description: 'Experience the future of financial markets with lightning-fast data, advanced analytics, and institutional-grade insights. Real-time market intelligence for professional traders.',
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 text-gray-900">
      {/* Modern Navigation */}
      <nav className="fixed top-0 w-full z-50 nav-modern">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">F</span>
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                FinanceFlow
              </span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-700 hover:text-blue-600 transition-all duration-300 font-medium">Features</a>
              <a href="#markets" className="text-gray-700 hover:text-blue-600 transition-all duration-300 font-medium">Markets</a>
              <a href="#analytics" className="text-gray-700 hover:text-blue-600 transition-all duration-300 font-medium">Analytics</a>
              <a href="/dashboard" className="text-gray-700 hover:text-blue-600 transition-all duration-300 font-medium">Dashboard</a>
              <a href="/screener" className="text-gray-700 hover:text-blue-600 transition-all duration-300 font-medium">Screener</a>
                </div>
            <button className="modern-button text-sm px-6 py-3">
              Get Started
            </button>
            </div>
                    </div>
      </nav>

      {/* Modern Hero Section */}
      <section className="pt-32 pb-20 px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10"></div>
        <div className="relative max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium mb-8">
            🚀 Real-time Market Intelligence Platform
          </div>

          <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold mb-8 leading-tight">
            <span className="bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent">
              Financial
            </span>
            <br />
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent font-extrabold">
              Intelligence
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-4xl mx-auto leading-relaxed">
            Experience the future of financial markets with lightning-fast data,
            advanced analytics, and institutional-grade insights. No delays, just pure intelligence.
          </p>

          {/* Hero Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <div className="modern-card p-8 text-center">
              <div className="text-5xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-3">$2.8T+</div>
              <div className="text-gray-600 font-medium">Market Cap Tracked</div>
                    </div>
            <div className="modern-card p-8 text-center">
              <div className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-3">99.9%</div>
              <div className="text-gray-600 font-medium">Uptime Guarantee</div>
                </div>
            <div className="modern-card p-8 text-center">
              <div className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-3">&lt;50ms</div>
              <div className="text-gray-600 font-medium">Data Latency</div>
                    </div>
                    </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button className="modern-button text-lg px-8 py-4">
              🚀 Start Trading Now
            </button>
            <button className="modern-button-outline text-lg px-8 py-4">
              📊 View Demo
            </button>
          </div>
                    </div>
      </section>

      {/* Modern Features Section */}
      <section id="features" className="py-24 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-6xl font-bold mb-6">
              <span className="bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                Powerful
              </span>
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Features</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Everything you need for professional-grade financial analysis and trading insights.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="group cursor-pointer">
              <div className="modern-card p-8 h-full flex flex-col justify-between text-center">
                <div className="mb-6">
                  <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                    <span className="text-2xl">📈</span>
                  </div>
                  <h3 className="text-2xl font-bold mb-4 text-gray-900">Real-Time Data</h3>
                  <p className="text-gray-600 leading-relaxed">Live market data from multiple exchanges with sub-second latency and institutional-grade accuracy</p>
                </div>
                <div className="text-green-600 font-semibold text-sm bg-green-50 px-3 py-1 rounded-full">
                  Alpha Vantage • Finnhub • Polygon
                </div>
              </div>
            </div>

            <div className="group cursor-pointer">
              <div className="modern-card p-8 h-full flex flex-col justify-between text-center">
                <div className="mb-6">
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                    <span className="text-2xl">🧠</span>
                  </div>
                  <h3 className="text-2xl font-bold mb-4 text-gray-900">Technical Analysis</h3>
                  <p className="text-gray-600 leading-relaxed">Advanced algorithms with MACD, RSI, Bollinger Bands, and 50+ professional indicators</p>
                </div>
                <div className="text-blue-600 font-semibold text-sm bg-blue-50 px-3 py-1 rounded-full">
                  Advanced Algorithms
                </div>
              </div>
            </div>

            <div className="group cursor-pointer">
              <div className="modern-card p-8 h-full flex flex-col justify-between text-center">
                <div className="mb-6">
                  <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                    <span className="text-2xl">📰</span>
                  </div>
                  <h3 className="text-2xl font-bold mb-4 text-gray-900">Market Intelligence</h3>
                  <p className="text-gray-600 leading-relaxed">AI-powered news analysis with real-time sentiment tracking and market impact assessment</p>
                </div>
                <div className="text-purple-600 font-semibold text-sm bg-purple-50 px-3 py-1 rounded-full">
                  Real-Time Feeds
                </div>
              </div>
            </div>

            <div className="group cursor-pointer">
              <div className="modern-card p-8 h-full flex flex-col justify-between text-center">
                <div className="mb-6">
                  <div className="w-16 h-16 bg-gradient-to-r from-amber-500 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                    <span className="text-2xl">⚡</span>
                  </div>
                  <h3 className="text-2xl font-bold mb-4 text-gray-900">Lightning Fast</h3>
                  <p className="text-gray-600 leading-relaxed">Built on Next.js 15 with optimized API routes, advanced caching, and edge computing</p>
                </div>
                <div className="text-amber-600 font-semibold text-sm bg-amber-50 px-3 py-1 rounded-full">
                  Blazing Performance
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Modern Market Data Section */}
      <section id="markets" className="py-24 px-6 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-6xl font-bold mb-6">
              <span className="bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                Live
              </span>
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Markets</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Real-time market data from global exchanges with institutional-grade accuracy and speed.
            </p>
          </div>

          <div className="modern-card p-12 rounded-3xl">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
              <div className="text-center p-8 bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl border border-green-100">
                <div className="text-4xl font-bold text-green-600 mb-3">24,467.80</div>
                <div className="text-gray-700 font-semibold text-lg mb-2">NIFTY 50</div>
                <div className="inline-flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  +1.2%
                </div>
              </div>

              <div className="text-center p-8 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl border border-blue-100">
                <div className="text-4xl font-bold text-blue-600 mb-3">80,845.00</div>
                <div className="text-gray-700 font-semibold text-lg mb-2">SENSEX</div>
                <div className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  +0.8%
                </div>
              </div>

              <div className="text-center p-8 bg-gradient-to-br from-red-50 to-rose-50 rounded-2xl border border-red-100">
                <div className="text-4xl font-bold text-red-600 mb-3">51,234.50</div>
                <div className="text-gray-700 font-semibold text-lg mb-2">BANK NIFTY</div>
                <div className="inline-flex items-center px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                  <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                  -0.3%
                </div>
              </div>
            </div>

            <div className="text-center">
              <button className="modern-button-outline px-10 py-4 text-lg">
                📈 View Full Market Dashboard
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Modern API Section */}
      <section id="analytics" className="py-24 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-6xl font-bold mb-6">
              <span className="bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                Developer
              </span>
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> APIs</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Powerful REST APIs for seamless integration with your applications and trading systems.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
            <div>
              <h3 className="text-3xl font-bold mb-8 text-gray-900">Real-Time Endpoints</h3>
              <div className="space-y-6">
                <div className="modern-card p-6 border-l-4 border-green-500">
                  <div className="flex items-center gap-4 mb-4">
                    <span className="bg-green-600 text-white px-3 py-1 rounded-lg text-sm font-mono font-bold">GET</span>
                    <code className="text-blue-600 font-mono text-lg">/api/stock-data</code>
                  </div>
                  <p className="text-gray-600">Real-time stock quotes with comprehensive technical indicators and market analysis</p>
                </div>

                <div className="modern-card p-6 border-l-4 border-blue-500">
                  <div className="flex items-center gap-4 mb-4">
                    <span className="bg-blue-600 text-white px-3 py-1 rounded-lg text-sm font-mono font-bold">GET</span>
                    <code className="text-blue-600 font-mono text-lg">/api/news</code>
                  </div>
                  <p className="text-gray-600">Latest financial news and market sentiment from trusted global sources</p>
                </div>

                <div className="modern-card p-6 border-l-4 border-purple-500">
                  <div className="flex items-center gap-4 mb-4">
                    <span className="bg-purple-600 text-white px-3 py-1 rounded-lg text-sm font-mono font-bold">GET</span>
                    <code className="text-blue-600 font-mono text-lg">/api/market-overview</code>
                  </div>
                  <p className="text-gray-600">Comprehensive market summary with major indices and sector performance</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-3xl font-bold mb-8 text-gray-900">Example Response</h3>
              <div className="modern-card p-8 bg-gray-900 text-gray-100">
                <pre className="text-sm overflow-x-auto leading-relaxed">
{`{
  "symbol": "AAPL",
  "currentPrice": 253.85,
  "change": -1.62,
  "changePercent": -0.63,
  "volume": 5833776,
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
  },
  "timestamp": "2025-09-29T19:25:34"
}`}
                </pre>
              </div>
              <div className="mt-6 text-center">
                <button className="modern-button-outline text-sm px-6 py-3">
                  📖 View Full Documentation
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Modern CTA Section */}
      <section className="py-24 px-6 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 relative overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-5xl mx-auto text-center">
          <h2 className="text-4xl md:text-6xl font-bold mb-8 text-white">
            Ready to Transform Your
            <span className="block bg-gradient-to-r from-yellow-300 to-orange-300 bg-clip-text text-transparent">
              Trading Experience?
            </span>
          </h2>
          <p className="text-xl md:text-2xl text-blue-100 mb-12 leading-relaxed">
            Join thousands of traders who trust our platform for institutional-grade market intelligence and lightning-fast execution.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
            <button className="bg-white text-gray-900 px-10 py-4 rounded-2xl text-xl font-bold hover:bg-gray-100 transition-all duration-300 transform hover:scale-105 shadow-xl">
              🚀 Start Free Trial
            </button>
            <button className="border-2 border-white text-white px-10 py-4 rounded-2xl text-xl font-bold hover:bg-white hover:text-gray-900 transition-all duration-300">
              📊 Schedule Demo
            </button>
          </div>
        </div>
      </section>

      {/* Modern Footer */}
      <footer className="bg-gray-900 text-white py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center">
                  <span className="text-white font-bold text-xl">F</span>
                </div>
                <span className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  FinanceFlow
                </span>
              </div>
              <p className="text-gray-300 text-lg leading-relaxed mb-6">
                The most advanced financial intelligence platform, powered by real-time market data and cutting-edge analytics.
                Trusted by professional traders worldwide.
              </p>
              <div className="flex space-x-4">
                <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center hover:bg-blue-700 transition-colors cursor-pointer">
                  <span className="text-white">📧</span>
                </div>
                <div className="w-10 h-10 bg-purple-600 rounded-xl flex items-center justify-center hover:bg-purple-700 transition-colors cursor-pointer">
                  <span className="text-white">🐦</span>
                </div>
                <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center hover:bg-indigo-700 transition-colors cursor-pointer">
                  <span className="text-white">💼</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-bold text-xl mb-6 text-white">Platform</h4>
              <ul className="space-y-3 text-gray-300">
                <li><a href="#" className="hover:text-blue-400 transition-colors text-lg">📈 Markets</a></li>
                <li><a href="#" className="hover:text-blue-400 transition-colors text-lg">🧠 Analytics</a></li>
                <li><a href="#" className="hover:text-blue-400 transition-colors text-lg">📰 News</a></li>
                <li><a href="#" className="hover:text-blue-400 transition-colors text-lg">🔌 API</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-xl mb-6 text-white">Resources</h4>
              <ul className="space-y-3 text-gray-300">
                <li><a href="#" className="hover:text-blue-400 transition-colors text-lg">📚 Documentation</a></li>
                <li><a href="#" className="hover:text-blue-400 transition-colors text-lg">🛠️ Support</a></li>
                <li><a href="#" className="hover:text-blue-400 transition-colors text-lg">📝 Blog</a></li>
                <li><a href="#" className="hover:text-blue-400 transition-colors text-lg">🔍 Status</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-700 mt-16 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400 text-lg">
                © 2024 FinanceFlow. Real data • Advanced analytics • Lightning fast
              </p>
              <div className="flex space-x-8 mt-4 md:mt-0">
                <a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy</a>
                <a href="#" className="text-gray-400 hover:text-white transition-colors">Terms</a>
                <a href="#" className="text-gray-400 hover:text-white transition-colors">Security</a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}