import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'CapitalFlow - Institutional Financial Platform',
  description: 'Professional-grade financial intelligence platform with real-time market data, advanced analytics, and institutional trading tools for serious investors.',
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Professional Navigation */}
      <nav className="financial-nav fixed top-0 w-full z-50">
        <div className="container-professional py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">CF</span>
              </div>
              <span className="text-2xl font-bold color-primary">
                CapitalFlow
              </span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-secondary hover:color-primary transition-colors font-medium">Features</a>
              <a href="#markets" className="text-secondary hover:color-primary transition-colors font-medium">Markets</a>
              <a href="#analytics" className="text-secondary hover:color-primary transition-colors font-medium">Analytics</a>
              <a href="/dashboard" className="text-secondary hover:color-primary transition-colors font-medium">Dashboard</a>
              <a href="/screener" className="text-secondary hover:color-primary transition-colors font-medium">Screener</a>
            </div>
            <button className="financial-button-primary">
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Professional Hero Section */}
      <section className="financial-hero section-padding">
        <div className="container-professional">
          <div className="text-center">
            <div className="inline-flex items-center px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm font-medium mb-8">
              🚀 Institutional-Grade Financial Intelligence
            </div>

            <h1 className="heading-primary mb-6">
              <span className="color-primary">CapitalFlow</span>
              <br />
              <span className="text-muted font-medium">Professional Trading Platform</span>
            </h1>

            <p className="text-professional text-xl mb-12 max-w-4xl mx-auto">
              Experience institutional-grade financial intelligence with lightning-fast market data,
              advanced analytics, and professional trading tools designed for serious investors.
            </p>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
              <div className="financial-stats-card">
                <div className="financial-metric financial-metric-positive">$2.8T+</div>
                <div className="text-muted">Market Cap Tracked</div>
              </div>

              <div className="financial-stats-card">
                <div className="financial-metric financial-metric-positive">99.9%</div>
                <div className="text-muted">Uptime Guarantee</div>
              </div>

              <div className="financial-stats-card">
                <div className="financial-metric financial-metric-positive">&lt;50ms</div>
                <div className="text-muted">Data Latency</div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="financial-button-primary px-8 py-4">
                Start Free Trial
              </button>
              <button className="financial-button-secondary px-8 py-4">
                Schedule Demo
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Professional Features Section */}
      <section className="section-padding bg-gray-50" id="features">
        <div className="container-professional">
          <div className="text-center mb-16">
            <h2 className="heading-secondary mb-6">
              <span className="color-primary">Professional</span> Trading Features
            </h2>
            <p className="text-professional text-xl max-w-4xl mx-auto">
              Comprehensive financial tools designed for institutional traders and serious investors.
            </p>
          </div>

          <div className="grid-professional">
            <div className="financial-card p-8 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <span className="text-green-600 text-2xl">📈</span>
              </div>
              <h3 className="text-xl font-bold mb-4 color-primary">Real-Time Market Data</h3>
              <p className="text-professional mb-4">
                Live market data from multiple global exchanges with sub-second latency and institutional-grade accuracy.
              </p>
              <div className="text-green-600 font-semibold text-sm bg-green-50 px-3 py-1 rounded-full inline-block">
                Alpha Vantage • Finnhub • Polygon
              </div>
            </div>

            <div className="financial-card p-8 text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <span className="text-blue-600 text-2xl">🧠</span>
              </div>
              <h3 className="text-xl font-bold mb-4 color-primary">Advanced Analytics</h3>
              <p className="text-professional mb-4">
                Professional technical indicators including MACD, RSI, Bollinger Bands, and 50+ institutional-grade tools.
              </p>
              <div className="text-blue-600 font-semibold text-sm bg-blue-50 px-3 py-1 rounded-full inline-block">
                Advanced Algorithms
              </div>
            </div>

            <div className="financial-card p-8 text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <span className="text-purple-600 text-2xl">📰</span>
              </div>
              <h3 className="text-xl font-bold mb-4 color-primary">Market Intelligence</h3>
              <p className="text-professional mb-4">
                AI-powered news analysis with real-time sentiment tracking and market impact assessment.
              </p>
              <div className="text-purple-600 font-semibold text-sm bg-purple-50 px-3 py-1 rounded-full inline-block">
                Real-Time Feeds
              </div>
            </div>

            <div className="financial-card p-8 text-center">
              <div className="w-16 h-16 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <span className="text-amber-600 text-2xl">⚡</span>
              </div>
              <h3 className="text-xl font-bold mb-4 color-primary">Enterprise Performance</h3>
              <p className="text-professional mb-4">
                Built on Next.js 15 with optimized API routes, advanced caching, and edge computing infrastructure.
              </p>
              <div className="text-amber-600 font-semibold text-sm bg-amber-50 px-3 py-1 rounded-full inline-block">
                Lightning Fast
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Professional Market Data Section */}
      <section className="section-padding" id="markets">
        <div className="container-professional">
          <div className="text-center mb-16">
            <h2 className="heading-secondary mb-6">
              <span className="color-primary">Live</span> Market Data
            </h2>
            <p className="text-professional text-xl max-w-4xl mx-auto">
              Real-time market data from global exchanges with institutional-grade accuracy and ultra-low latency.
            </p>
          </div>

          <div className="financial-card p-12">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
              <div className="text-center p-8 bg-green-50 rounded-2xl border border-green-200">
                <div className="financial-metric financial-metric-positive mb-3">24,467.80</div>
                <div className="text-lg font-semibold text-gray-800 mb-2">NIFTY 50</div>
                <div className="inline-flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-full font-medium">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  +1.2%
                </div>
              </div>

              <div className="text-center p-8 bg-blue-50 rounded-2xl border border-blue-200">
                <div className="financial-metric financial-metric-positive mb-3">80,845.00</div>
                <div className="text-lg font-semibold text-gray-800 mb-2">SENSEX</div>
                <div className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-700 rounded-full font-medium">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  +0.8%
                </div>
              </div>

              <div className="text-center p-8 bg-red-50 rounded-2xl border border-red-200">
                <div className="financial-metric financial-metric-negative mb-3">51,234.50</div>
                <div className="text-lg font-semibold text-gray-800 mb-2">BANK NIFTY</div>
                <div className="inline-flex items-center px-3 py-1 bg-red-100 text-red-700 rounded-full font-medium">
                  <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                  -0.3%
                </div>
              </div>
            </div>

            <div className="text-center">
              <button className="financial-button-primary px-8 py-4">
                📊 View Full Market Dashboard
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Professional API Section */}
      <section className="section-padding bg-white" id="analytics">
        <div className="container-professional">
          <div className="text-center mb-16">
            <h2 className="heading-secondary mb-6">
              <span className="color-primary">Enterprise</span> API Solutions
            </h2>
            <p className="text-professional text-xl max-w-4xl mx-auto">
              Robust REST APIs designed for seamless integration with institutional trading systems and applications.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
            <div>
              <h3 className="text-2xl font-bold mb-8 color-primary">Real-Time Endpoints</h3>
              <div className="space-y-6">
                <div className="financial-card p-6 border-l-4 border-green-500">
                  <div className="flex items-center gap-4 mb-4">
                    <span className="bg-green-600 text-white px-3 py-1 rounded-lg text-sm font-bold">GET</span>
                    <code className="text-blue-600 font-semibold text-lg">/api/stock-data</code>
                  </div>
                  <p className="text-professional">Real-time stock quotes with comprehensive technical indicators and market analysis</p>
                </div>

                <div className="financial-card p-6 border-l-4 border-blue-500">
                  <div className="flex items-center gap-4 mb-4">
                    <span className="bg-blue-600 text-white px-3 py-1 rounded-lg text-sm font-bold">GET</span>
                    <code className="text-blue-600 font-semibold text-lg">/api/news</code>
                  </div>
                  <p className="text-professional">Latest financial news and market sentiment from trusted global sources</p>
                </div>

                <div className="financial-card p-6 border-l-4 border-purple-500">
                  <div className="flex items-center gap-4 mb-4">
                    <span className="bg-purple-600 text-white px-3 py-1 rounded-lg text-sm font-bold">GET</span>
                    <code className="text-blue-600 font-semibold text-lg">/api/market-overview</code>
                  </div>
                  <p className="text-professional">Comprehensive market summary with major indices and sector performance</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-2xl font-bold mb-8 color-primary">Response Example</h3>
              <div className="financial-card p-8 bg-gray-900 text-gray-100">
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
                <button className="financial-button-secondary px-6 py-3">
                  📖 View Full Documentation
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Professional CTA Section */}
      <section className="section-padding bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 relative overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="container-professional relative">
          <div className="text-center">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
              Ready to Transform Your
              <span className="block bg-gradient-to-r from-yellow-300 to-orange-300 bg-clip-text text-transparent">
                Trading Experience?
              </span>
            </h2>
            <p className="text-xl md:text-2xl text-blue-100 mb-12 leading-relaxed max-w-4xl mx-auto">
              Join thousands of institutional traders who trust our platform for professional-grade market intelligence and lightning-fast execution.
            </p>
            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <button className="bg-white text-gray-900 px-10 py-4 rounded-2xl text-xl font-bold hover:bg-gray-100 transition-all duration-300 transform hover:scale-105 shadow-xl">
                🚀 Start Free Trial
              </button>
              <button className="border-2 border-white text-white px-10 py-4 rounded-2xl text-xl font-bold hover:bg-white hover:text-gray-900 transition-all duration-300">
                📊 Schedule Demo
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Professional Footer */}
      <footer className="bg-gray-900 text-white section-padding">
        <div className="container-professional">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 bg-primary rounded-2xl flex items-center justify-center">
                  <span className="text-white font-bold text-xl">CF</span>
                </div>
                <span className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  CapitalFlow
                </span>
              </div>
              <p className="text-gray-300 text-lg leading-relaxed mb-6">
                The most advanced institutional financial intelligence platform, powered by real-time market data and cutting-edge analytics.
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
                © 2024 CapitalFlow. Real data • Advanced analytics • Lightning fast
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