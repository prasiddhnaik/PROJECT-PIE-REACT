'use client'

import NSEStocksDashboard from '@/components/NSEStocksDashboard'

export default function NSEPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-green-50 p-4">
      <div className="container mx-auto max-w-7xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🇮🇳 NSE Stock Market Dashboard
          </h1>
          <p className="text-gray-600">
            Live data from National Stock Exchange of India - Real-time prices in Indian Rupees
          </p>
        </div>
        
        <NSEStocksDashboard />
        
        {/* Additional market info */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="crypto-card p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              📊 Market Information
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span>Exchange:</span>
                <span className="font-medium">National Stock Exchange (NSE)</span>
              </div>
              <div className="flex justify-between">
                <span>Trading Hours:</span>
                <span className="font-medium">9:15 AM - 3:30 PM IST</span>
              </div>
              <div className="flex justify-between">
                <span>Currency:</span>
                <span className="font-medium">Indian Rupee (₹)</span>
              </div>
              <div className="flex justify-between">
                <span>Data Source:</span>
                <span className="font-medium">Yahoo Finance, NSE India</span>
              </div>
            </div>
          </div>
          
          <div className="crypto-card p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              🎯 Major Indices
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span>NIFTY 50:</span>
                <span className="font-medium text-green-600">24,467 (+0.8%)</span>
              </div>
              <div className="flex justify-between">
                <span>SENSEX:</span>
                <span className="font-medium text-green-600">80,845 (+1.2%)</span>
              </div>
              <div className="flex justify-between">
                <span>BANK NIFTY:</span>
                <span className="font-medium text-green-600">51,234 (+1.5%)</span>
              </div>
              <div className="flex justify-between">
                <span>NIFTY IT:</span>
                <span className="font-medium text-red-600">32,156 (-0.5%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 