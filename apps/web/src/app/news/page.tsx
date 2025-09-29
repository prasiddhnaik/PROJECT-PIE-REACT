'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function NewsPage() {
  const [news, setNews] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState('all')

  useEffect(() => {
    fetchNews()
  }, [])

  const fetchNews = async () => {
    try {
      const response = await fetch('/api/news')
      const data = await response.json()
      setNews(data.news || [])
      setLoading(false)
    } catch (error) {
      console.error('Error fetching news:', error)
      setLoading(false)
    }
  }

  const categories = [
    { id: 'all', name: 'All News' },
    { id: 'markets', name: 'Markets' },
    { id: 'tech', name: 'Technology' },
    { id: 'crypto', name: 'Cryptocurrency' },
    { id: 'global', name: 'Global' },
  ]

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)
    
    if (diffInSeconds < 60) return 'Just now'
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
    return `${Math.floor(diffInSeconds / 86400)}d ago`
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Navigation */}
      <nav className="border-b border-gray-800 bg-black/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold">FinanceOS</Link>
            <div className="flex items-center space-x-6">
              <Link href="/dashboard" className="hover:text-gray-300 transition-colors">Dashboard</Link>
              <Link href="/" className="hover:text-gray-300 transition-colors">Home</Link>
              <div className="text-sm text-gray-400">
                Live News • {new Date().toLocaleTimeString()}
              </div>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-5xl font-light mb-4">
            Market <span className="font-bold">Intelligence</span>
          </h1>
          <p className="text-xl text-gray-400">
            Real-time financial news and market analysis
          </p>
        </div>

        {/* Category Filter */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-3">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-md border transition-all ${
                  selectedCategory === category.id
                    ? 'bg-white text-black border-white'
                    : 'bg-black text-gray-300 border-gray-700 hover:border-gray-500'
                }`}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main News */}
            <div className="lg:col-span-2">
              <div className="space-y-6">
                {news.map((article, index) => (
                  <article
                    key={index}
                    className="group cursor-pointer bg-gray-900/30 border border-gray-800 rounded-lg p-6 hover:border-gray-600 transition-all"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h2 className="text-xl font-semibold mb-2 group-hover:text-gray-300 transition-colors line-clamp-2">
                          {article.title}
                        </h2>
                        <p className="text-gray-400 text-sm mb-3 line-clamp-3">
                          {article.summary}
                        </p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span>{article.source}</span>
                          <span>•</span>
                          <span>{formatTimeAgo(article.publishedAt)}</span>
                        </div>
                      </div>
                      {article.image && (
                        <div className="ml-4 flex-shrink-0">
                          <div className="w-24 h-16 bg-gray-800 rounded-md flex items-center justify-center">
                            <div className="text-2xl">📰</div>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="px-2 py-1 bg-blue-600/20 text-blue-400 text-xs rounded">
                          Markets
                        </span>
                      </div>
                      <button className="text-gray-400 hover:text-white transition-colors">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                    </div>
                  </article>
                ))}
              </div>

              {/* Load More */}
              <div className="mt-8 text-center">
                <button className="bg-white text-black px-8 py-3 rounded-md font-medium hover:bg-gray-200 transition-colors">
                  Load More Articles
                </button>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-8">
              {/* Market Summary */}
              <div className="bg-gray-900/30 border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Market Summary</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">NIFTY 50</span>
                    <div className="text-right">
                      <div className="font-semibold">24,467.80</div>
                      <div className="text-green-400 text-xs">+1.2%</div>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">SENSEX</span>
                    <div className="text-right">
                      <div className="font-semibold">80,845.00</div>
                      <div className="text-green-400 text-xs">+0.8%</div>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">BANK NIFTY</span>
                    <div className="text-right">
                      <div className="font-semibold">51,234.50</div>
                      <div className="text-red-400 text-xs">-0.3%</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Trending Topics */}
              <div className="bg-gray-900/30 border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Trending Topics</h3>
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm">🔥</span>
                    <span className="text-sm text-gray-300">AI & Machine Learning</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm">📈</span>
                    <span className="text-sm text-gray-300">Federal Reserve Policy</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm">💎</span>
                    <span className="text-sm text-gray-300">Cryptocurrency</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm">🌱</span>
                    <span className="text-sm text-gray-300">ESG Investing</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm">⚡</span>
                    <span className="text-sm text-gray-300">Energy Transition</span>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="bg-gray-900/30 border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <Link 
                    href="/dashboard"
                    className="block w-full bg-white text-black text-center py-2 rounded-md font-medium hover:bg-gray-200 transition-colors"
                  >
                    View Dashboard
                  </Link>
                  <button className="w-full border border-gray-600 hover:border-gray-500 text-white py-2 rounded-md transition-colors">
                    Set News Alerts
                  </button>
                  <button className="w-full border border-gray-600 hover:border-gray-500 text-white py-2 rounded-md transition-colors">
                    Export Data
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}


