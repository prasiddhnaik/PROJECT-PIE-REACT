'use client'

import { Metadata } from 'next'
import { useState, useEffect } from 'react'

export default function DashboardPage() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [marketStatus, setMarketStatus] = useState<'open' | 'closed' | 'pre-market'>('open')

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="dashboard-root">
      {/* Command Center Header */}
      <header className="dashboard-header">
        <div className="dashboard-header-content">
          <div className="dashboard-brand">
            <div className="dashboard-logo">CF</div>
            <div className="dashboard-title">
              <h1>CapitalFlow Intelligence</h1>
              <p className="dashboard-subtitle">Command Center</p>
            </div>
          </div>

          <div className="dashboard-status-bar">
            <div className="status-item">
              <span className="status-label">Market</span>
              <span className={`status-badge status-${marketStatus}`}>
                {marketStatus === 'open' ? '● LIVE' : marketStatus === 'pre-market' ? '◐ PRE' : '○ CLOSED'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Time</span>
              <span className="status-value">
                {currentTime.toLocaleTimeString('en-US', { hour12: false })}
              </span>
            </div>
          </div>

          <div className="dashboard-actions">
            <button className="action-btn action-btn-secondary">
              <span>⚙️</span>
            </button>
            <button className="action-btn action-btn-secondary">
              <span>🔔</span>
            </button>
            <button className="action-btn action-btn-primary">
              <span>👤</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Dashboard Grid */}
      <div className="dashboard-container">
        <aside className="dashboard-sidebar">
          <nav className="sidebar-nav">
            <a href="#" className="nav-item nav-item-active">
              <span className="nav-icon">📊</span>
              <span className="nav-label">Overview</span>
            </a>
            <a href="#" className="nav-item">
              <span className="nav-icon">📈</span>
              <span className="nav-label">Markets</span>
            </a>
            <a href="#" className="nav-item">
              <span className="nav-icon">💼</span>
              <span className="nav-label">Portfolio</span>
            </a>
            <a href="#" className="nav-item">
              <span className="nav-icon">⭐</span>
              <span className="nav-label">Watchlist</span>
            </a>
            <a href="#" className="nav-item">
              <span className="nav-icon">📰</span>
              <span className="nav-label">News</span>
            </a>
            <a href="#" className="nav-item">
              <span className="nav-icon">🔍</span>
              <span className="nav-label">Screener</span>
            </a>
            <a href="#" className="nav-item">
              <span className="nav-icon">📉</span>
              <span className="nav-label">Analytics</span>
            </a>
            <a href="#" className="nav-item">
              <span className="nav-icon">🎯</span>
              <span className="nav-label">Alerts</span>
            </a>
          </nav>

          <div className="sidebar-footer">
            <div className="system-status">
              <div className="status-indicator status-indicator-green"></div>
              <span className="status-text">All Systems Operational</span>
            </div>
          </div>
        </aside>

        <main className="dashboard-main">
          {/* Market Overview Section */}
          <section className="dashboard-section">
            <div className="section-header">
              <h2 className="section-title">Market Overview</h2>
              <div className="section-actions">
                <button className="btn-icon">↻</button>
                <button className="btn-icon">⋮</button>
              </div>
            </div>

            <div className="grid-3">
              <div className="metric-card metric-card-positive">
                <div className="metric-header">
                  <span className="metric-label">NIFTY 50</span>
                  <span className="metric-badge badge-live">LIVE</span>
                </div>
                <div className="metric-value">24,467.80</div>
                <div className="metric-change metric-change-up">
                  <span className="change-arrow">▲</span>
                  <span className="change-value">+284.50</span>
                  <span className="change-percent">(+1.18%)</span>
                </div>
                <div className="metric-sparkline">
                  <div className="sparkline sparkline-up"></div>
                </div>
              </div>

              <div className="metric-card metric-card-positive">
                <div className="metric-header">
                  <span className="metric-label">SENSEX</span>
                  <span className="metric-badge badge-live">LIVE</span>
                </div>
                <div className="metric-value">80,845.00</div>
                <div className="metric-change metric-change-up">
                  <span className="change-arrow">▲</span>
                  <span className="change-value">+624.30</span>
                  <span className="change-percent">(+0.78%)</span>
                </div>
                <div className="metric-sparkline">
                  <div className="sparkline sparkline-up"></div>
                </div>
              </div>

              <div className="metric-card metric-card-negative">
                <div className="metric-header">
                  <span className="metric-label">BANK NIFTY</span>
                  <span className="metric-badge badge-live">LIVE</span>
                </div>
                <div className="metric-value">51,234.50</div>
                <div className="metric-change metric-change-down">
                  <span className="change-arrow">▼</span>
                  <span className="change-value">-156.20</span>
                  <span className="change-percent">(-0.30%)</span>
                </div>
                <div className="metric-sparkline">
                  <div className="sparkline sparkline-down"></div>
                </div>
              </div>
            </div>
          </section>

          {/* Two Column Layout */}
          <div className="grid-2">
            {/* Portfolio Summary */}
            <section className="dashboard-section">
              <div className="section-header">
                <h2 className="section-title">Portfolio</h2>
                <a href="#" className="section-link">View All →</a>
              </div>

              <div className="portfolio-summary">
                <div className="portfolio-stat">
                  <span className="stat-label">Total Value</span>
                  <span className="stat-value stat-value-large">₹12,45,680</span>
                  <span className="stat-change stat-change-positive">+₹34,520 (2.85%)</span>
                </div>

                <div className="portfolio-grid">
                  <div className="portfolio-item">
                    <span className="item-label">Day P&L</span>
                    <span className="item-value item-value-positive">+₹8,450</span>
                  </div>
                  <div className="portfolio-item">
                    <span className="item-label">Total P&L</span>
                    <span className="item-value item-value-positive">+₹1,24,680</span>
                  </div>
                  <div className="portfolio-item">
                    <span className="item-label">Holdings</span>
                    <span className="item-value">23</span>
                  </div>
                  <div className="portfolio-item">
                    <span className="item-label">Invested</span>
                    <span className="item-value">₹11,21,000</span>
                  </div>
                </div>
              </div>

              <div className="holdings-list">
                <div className="holding-item">
                  <div className="holding-info">
                    <span className="holding-symbol">RELIANCE</span>
                    <span className="holding-shares">50 shares</span>
                  </div>
                  <div className="holding-values">
                    <span className="holding-price">₹2,845.50</span>
                    <span className="holding-change holding-change-positive">+2.3%</span>
                  </div>
                </div>

                <div className="holding-item">
                  <div className="holding-info">
                    <span className="holding-symbol">TCS</span>
                    <span className="holding-shares">30 shares</span>
                  </div>
                  <div className="holding-values">
                    <span className="holding-price">₹3,456.75</span>
                    <span className="holding-change holding-change-positive">+1.8%</span>
                  </div>
                </div>

                <div className="holding-item">
                  <div className="holding-info">
                    <span className="holding-symbol">INFY</span>
                    <span className="holding-shares">45 shares</span>
                  </div>
                  <div className="holding-values">
                    <span className="holding-price">₹1,534.20</span>
                    <span className="holding-change holding-change-negative">-0.5%</span>
                  </div>
                </div>
              </div>
            </section>

            {/* Watchlist */}
            <section className="dashboard-section">
              <div className="section-header">
                <h2 className="section-title">Watchlist</h2>
                <button className="btn-add">+ Add</button>
              </div>

              <div className="watchlist">
                <div className="watchlist-item">
                  <div className="watchlist-symbol">
                    <span className="symbol-name">HDFCBANK</span>
                    <span className="symbol-exchange">NSE</span>
                  </div>
                  <div className="watchlist-data">
                    <span className="data-price">₹1,678.45</span>
                    <span className="data-change data-change-positive">+1.2%</span>
                  </div>
                </div>

                <div className="watchlist-item">
                  <div className="watchlist-symbol">
                    <span className="symbol-name">ICICIBANK</span>
                    <span className="symbol-exchange">NSE</span>
                  </div>
                  <div className="watchlist-data">
                    <span className="data-price">₹1,123.80</span>
                    <span className="data-change data-change-positive">+0.9%</span>
                  </div>
                </div>

                <div className="watchlist-item">
                  <div className="watchlist-symbol">
                    <span className="symbol-name">SBIN</span>
                    <span className="symbol-exchange">NSE</span>
                  </div>
                  <div className="watchlist-data">
                    <span className="data-price">₹634.50</span>
                    <span className="data-change data-change-negative">-0.3%</span>
                  </div>
                </div>

                <div className="watchlist-item">
                  <div className="watchlist-symbol">
                    <span className="symbol-name">WIPRO</span>
                    <span className="symbol-exchange">NSE</span>
                  </div>
                  <div className="watchlist-data">
                    <span className="data-price">₹445.60</span>
                    <span className="data-change data-change-positive">+2.1%</span>
                  </div>
                </div>

                <div className="watchlist-item">
                  <div className="watchlist-symbol">
                    <span className="symbol-name">AXISBANK</span>
                    <span className="symbol-exchange">NSE</span>
                  </div>
                  <div className="watchlist-data">
                    <span className="data-price">₹1,089.25</span>
                    <span className="data-change data-change-positive">+1.5%</span>
                  </div>
                </div>
              </div>
            </section>
          </div>

          {/* Market News */}
          <section className="dashboard-section">
            <div className="section-header">
              <h2 className="section-title">Market Intelligence</h2>
              <div className="section-filters">
                <button className="filter-chip filter-chip-active">All</button>
                <button className="filter-chip">Markets</button>
                <button className="filter-chip">Stocks</button>
                <button className="filter-chip">Economy</button>
              </div>
            </div>

            <div className="news-grid">
              <article className="news-card">
                <div className="news-meta">
                  <span className="news-source">Economic Times</span>
                  <span className="news-time">12m ago</span>
                </div>
                <h3 className="news-title">Nifty hits fresh all-time high as IT stocks rally on strong Q3 earnings</h3>
                <p className="news-excerpt">
                  The benchmark index surged past 24,500 mark led by gains in technology heavyweights...
                </p>
                <div className="news-tags">
                  <span className="tag tag-positive">Bullish</span>
                  <span className="tag">Markets</span>
                </div>
              </article>

              <article className="news-card">
                <div className="news-meta">
                  <span className="news-source">Bloomberg</span>
                  <span className="news-time">1h ago</span>
                </div>
                <h3 className="news-title">RBI holds interest rates steady, maintains accommodative stance</h3>
                <p className="news-excerpt">
                  The central bank kept repo rate unchanged at 6.5% citing inflation concerns while supporting growth...
                </p>
                <div className="news-tags">
                  <span className="tag tag-neutral">Neutral</span>
                  <span className="tag">Economy</span>
                </div>
              </article>

              <article className="news-card">
                <div className="news-meta">
                  <span className="news-source">Moneycontrol</span>
                  <span className="news-time">2h ago</span>
                </div>
                <h3 className="news-title">FII inflows continue for fifth straight session, crosses ₹5,000 crore</h3>
                <p className="news-excerpt">
                  Foreign institutional investors pumped in significant capital across banking and pharma sectors...
                </p>
                <div className="news-tags">
                  <span className="tag tag-positive">Bullish</span>
                  <span className="tag">Markets</span>
                </div>
              </article>
            </div>
          </section>

          {/* Quick Stats */}
          <section className="dashboard-section">
            <div className="section-header">
              <h2 className="section-title">Market Statistics</h2>
            </div>

            <div className="stats-grid">
              <div className="stat-box">
                <span className="stat-icon">📊</span>
                <div className="stat-content">
                  <span className="stat-value">1,847</span>
                  <span className="stat-label">Advancing</span>
                </div>
                <span className="stat-trend stat-trend-up">+12%</span>
              </div>

              <div className="stat-box">
                <span className="stat-icon">📉</span>
                <div className="stat-content">
                  <span className="stat-value">1,234</span>
                  <span className="stat-label">Declining</span>
                </div>
                <span className="stat-trend stat-trend-down">-8%</span>
              </div>

              <div className="stat-box">
                <span className="stat-icon">⚖️</span>
                <div className="stat-content">
                  <span className="stat-value">156</span>
                  <span className="stat-label">Unchanged</span>
                </div>
                <span className="stat-trend">--</span>
              </div>

              <div className="stat-box">
                <span className="stat-icon">💹</span>
                <div className="stat-content">
                  <span className="stat-value">₹8.2T</span>
                  <span className="stat-label">Turnover</span>
                </div>
                <span className="stat-trend stat-trend-up">+15%</span>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  )
}
