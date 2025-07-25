'use client'

import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'

interface NSEStock {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
  volume: number
  timestamp: string
  source: string
  currency: string
  exchange: string
}

interface NSEResponse {
  success: boolean
  data: NSEStock[]
  count: number
  timestamp: string
}

const fetchNSEStocks = async (): Promise<NSEResponse> => {
  const response = await fetch('http://localhost:8002/stocks/popular')
  if (!response.ok) {
    throw new Error('Failed to fetch NSE data')
  }
  return response.json()
}

export default function NSEStocksDashboard() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['nse-stocks'],
    queryFn: fetchNSEStocks,
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: 2
  })

  const formatPrice = (price: number): string => {
    return `₹${price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  const formatChange = (change: number, changePercent: number): { value: string, className: string } => {
    const isPositive = change >= 0
    return {
      value: `${isPositive ? '+' : ''}₹${change.toFixed(2)} (${isPositive ? '+' : ''}${changePercent.toFixed(2)}%)`,
      className: isPositive ? 'text-green-600' : 'text-red-600'
    }
  }

  const formatVolume = (volume: number): string => {
    if (volume >= 10000000) {
      return `${(volume / 10000000).toFixed(1)}Cr`
    } else if (volume >= 100000) {
      return `${(volume / 100000).toFixed(1)}L`
    }
    return volume.toLocaleString('en-IN')
  }

  if (error) {
    return (
      <div className="crypto-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-red-600">🇮🇳 NSE Stocks - Connection Error</h2>
          <button 
            onClick={() => refetch()}
            className="btn-primary px-4 py-2 text-sm"
          >
            Retry
          </button>
        </div>
        <p className="text-gray-600">
          Unable to connect to NSE data service. Make sure the service is running on port 8002.
        </p>
        <div className="mt-4 p-4 bg-gray-100 rounded-lg">
          <p className="text-sm font-medium">To start NSE service:</p>
          <code className="text-sm text-blue-600 block mt-2">
            cd services/nse-service && python3 nse_data_fetcher.py
          </code>
        </div>
      </div>
    )
  }

  return (
    <div className="crypto-card p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          🇮🇳 NSE Live Stocks
          <span className="text-sm font-normal text-gray-500">
            Real-time Indian Market Data
          </span>
        </h2>
        <div className="flex items-center gap-3">
          {data && (
            <span className="text-sm text-gray-500">
              Last updated: {new Date(data.timestamp).toLocaleTimeString()}
            </span>
          )}
          <button 
            onClick={() => refetch()}
            className="btn-secondary px-3 py-1 text-sm"
            disabled={isLoading}
          >
            {isLoading ? '🔄' : '↻'} Refresh
          </button>
        </div>
      </div>

      {isLoading && !data ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="crypto-card p-4 animate-pulse">
              <div className="h-4 bg-gray-300 rounded mb-2"></div>
              <div className="h-6 bg-gray-300 rounded mb-2"></div>
              <div className="h-4 bg-gray-300 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="crypto-card p-4 bg-blue-50">
              <h3 className="font-semibold text-blue-700">Market Status</h3>
              <p className="text-2xl font-bold text-blue-600">
                {data?.data.length || 0} Stocks
              </p>
              <p className="text-sm text-blue-500">Live Data Available</p>
            </div>
            <div className="crypto-card p-4 bg-green-50">
              <h3 className="font-semibold text-green-700">Gainers</h3>
              <p className="text-2xl font-bold text-green-600">
                {data?.data.filter(stock => stock.change > 0).length || 0}
              </p>
              <p className="text-sm text-green-500">Stocks Rising</p>
            </div>
            <div className="crypto-card p-4 bg-red-50">
              <h3 className="font-semibold text-red-700">Losers</h3>
              <p className="text-2xl font-bold text-red-600">
                {data?.data.filter(stock => stock.change < 0).length || 0}
              </p>
              <p className="text-sm text-red-500">Stocks Falling</p>
            </div>
          </div>

          {/* Stock Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data?.data.map((stock) => {
              const changeData = formatChange(stock.change, stock.change_percent)
              return (
                <div key={stock.symbol} className="crypto-card p-4 hover:shadow-lg transition-shadow">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-bold text-lg">{stock.symbol}</h3>
                      <p className="text-sm text-gray-600 truncate" title={stock.name}>
                        {stock.name}
                      </p>
                    </div>
                    <span className="text-xs px-2 py-1 bg-orange-100 text-orange-600 rounded">
                      {stock.exchange}
                    </span>
                  </div>
                  
                  <div className="mb-3">
                    <p className="text-2xl font-bold text-gray-900">
                      {formatPrice(stock.price)}
                    </p>
                    <p className={`text-sm font-medium ${changeData.className}`}>
                      {changeData.value}
                    </p>
                  </div>

                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Volume: {formatVolume(stock.volume)}</span>
                    <span title={stock.source}>{stock.source}</span>
                  </div>

                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex justify-between items-center">
                      <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                        📊 Chart
                      </button>
                      <button className="text-green-600 hover:text-green-800 text-sm font-medium">
                        💰 Buy
                      </button>
                      <button className="text-purple-600 hover:text-purple-800 text-sm font-medium">
                        ⭐ Watch
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Footer Info */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="flex flex-wrap justify-between items-center text-sm text-gray-500">
              <div>
                <span className="font-medium">Data Sources:</span> NSE India, Yahoo Finance
              </div>
              <div>
                <span className="font-medium">Currency:</span> Indian Rupees (₹)
              </div>
              <div>
                <span className="font-medium">Market:</span> National Stock Exchange
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
} 