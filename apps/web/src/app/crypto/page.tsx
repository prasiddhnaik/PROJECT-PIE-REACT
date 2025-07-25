"use client";

import React from 'react';
import Link from 'next/link';
import CryptoDashboard from '@/components/CryptoDashboard';
import CryptoChart from '@/components/CryptoChart';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import styles from '@/styles/layouts.module.css';

export default function CryptoPage() {
  return (
    <div className={`${styles.minHeightScreen} ${styles.gradientSecondary}`}>
      <div className={`${styles.container} ${styles.py8}`}>
        {/* Breadcrumb Navigation */}
        <nav className={styles.my6}>
          <div className={`${styles.flexRow} ${styles.spaceX2}`} style={{fontSize: 'var(--text-sm)'}}>
            <Link href="/" style={{color: 'var(--primary-600)'}}>Home</Link>
            <span style={{color: 'var(--text-tertiary)'}}>/</span>
            <span style={{color: 'var(--text-secondary)'}}>Cryptocurrency</span>
          </div>
        </nav>

        {/* Header */}
        <div className={`${styles.my8} ${styles.textCenter}`}>
          <h1 className={`${styles.my4} text-gradient`} style={{fontSize: 'var(--text-4xl)', fontWeight: 'bold'}}>
            Cryptocurrency Analytics
          </h1>
          <p className={`${styles.containerTight} ${styles.mxAuto}`} style={{fontSize: 'var(--text-lg)', color: 'var(--text-secondary)'}}>
            Comprehensive cryptocurrency market analysis with real-time data, AI insights, and advanced charting tools.
          </p>
        </div>

        {/* Quick Actions Bar */}
        <Card variant="elevated" className={styles.my8}>
          <CardContent className={styles.p6}>
            <div className={`${styles.flexCol} ${styles.flexBetween} ${styles.spaceY4}`}>
              <div className={`${styles.flexRow} ${styles.spaceX2}`}>
                <Badge variant="success" pulse>
                  🔴 Live Data
                </Badge>
                <span style={{fontSize: 'var(--text-sm)', color: 'var(--text-secondary)'}}>
                  Updates every 30 seconds
                </span>
              </div>
              
              <div className={`${styles.flexCol} ${styles.spaceY3}`}>
                <Link href="/market">
                  <Button variant="outline" size="sm" className={styles.wFull}>
                    📊 Market Overview
                  </Button>
                </Link>
                
                <Link href="/ai-predictions">
                  <Button variant="outline" size="sm" className={styles.wFull}>
                    🤖 AI Predictions
                  </Button>
                </Link>
                
                <Link href="/crypto-analytics">
                  <Button variant="outline" size="sm" className={styles.wFull}>
                    📈 Advanced Analytics
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Market Overview Widget */}
        <div className={`${styles.gridCols1} ${styles.gridCols4} ${styles.my8}`}>
          <Card variant="elevated">
            <CardContent className={`${styles.p6} ${styles.textCenter}`}>
              <div className={styles.my2} style={{fontSize: 'var(--text-3xl)'}}>₿</div>
              <h3 className={styles.my2} style={{fontSize: 'var(--text-sm)', fontWeight: 500, color: 'var(--text-secondary)'}}>
                Bitcoin
              </h3>
              <p style={{fontSize: 'var(--text-lg)', fontWeight: 'bold', color: 'var(--text-primary)'}}>
                Live Price
              </p>
            </CardContent>
          </Card>

          <Card variant="elevated">
            <CardContent className={`${styles.p6} ${styles.textCenter}`}>
              <div className={styles.my2} style={{fontSize: 'var(--text-3xl)'}}>📊</div>
              <h3 className={styles.my2} style={{fontSize: 'var(--text-sm)', fontWeight: 500, color: 'var(--text-secondary)'}}>
                Market Cap
              </h3>
              <p style={{fontSize: 'var(--text-lg)', fontWeight: 'bold', color: 'var(--text-primary)'}}>
                Global Total
              </p>
            </CardContent>
          </Card>

          <Card variant="elevated">
            <CardContent className={`${styles.p6} ${styles.textCenter}`}>
              <div className={styles.my2} style={{fontSize: 'var(--text-3xl)'}}>📈</div>
              <h3 className={styles.my2} style={{fontSize: 'var(--text-sm)', fontWeight: 500, color: 'var(--text-secondary)'}}>
                24h Volume
              </h3>
              <p style={{fontSize: 'var(--text-lg)', fontWeight: 'bold', color: 'var(--text-primary)'}}>
                Trading Volume
              </p>
            </CardContent>
          </Card>

          <Card variant="elevated">
            <CardContent className={`${styles.p6} ${styles.textCenter}`}>
              <div className={styles.my2} style={{fontSize: 'var(--text-3xl)'}}>🔥</div>
              <h3 className={styles.my2} style={{fontSize: 'var(--text-sm)', fontWeight: 500, color: 'var(--text-secondary)'}}>
                Trending
              </h3>
              <p style={{fontSize: 'var(--text-lg)', fontWeight: 'bold', color: 'var(--text-primary)'}}>
                Hot Cryptos
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Featured Chart Section */}
        <Card variant="elevated" className={styles.my8}>
          <CardHeader>
            <div className={styles.flexBetween}>
              <h2 style={{fontSize: 'var(--text-2xl)', fontWeight: 'bold', color: 'var(--text-primary)'}}>
                Bitcoin Price Analysis
              </h2>
              <div className={`${styles.flexRow} ${styles.spaceX2}`}>
                <Button variant="outline" size="sm">1D</Button>
                <Button variant="primary" size="sm">7D</Button>
                <Button variant="outline" size="sm">30D</Button>
                <Button variant="outline" size="sm">1Y</Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className={styles.my4} style={{height: '24rem'}}>
              <CryptoChart 
                symbol="bitcoin" 
                days={7}
              />
            </div>
            <div className={`${styles.flexBetween}`} style={{fontSize: 'var(--text-sm)', color: 'var(--text-secondary)'}}>
              <span>Data provided by CoinGecko</span>
              <span>Last updated: {new Date().toLocaleTimeString()}</span>
            </div>
          </CardContent>
        </Card>

        {/* Main Dashboard Component */}
        <CryptoDashboard />

        {/* Additional Resources */}
        <div className={`${styles.my12} ${styles.gridCols1} ${styles.gridCols3}`}>
          <Card variant="outlined" interactive>
            <CardContent className={`${styles.p6} ${styles.textCenter}`}>
              <div className={styles.my4} style={{fontSize: 'var(--text-4xl)'}}>📚</div>
              <h3 className={styles.my2} style={{fontSize: 'var(--text-xl)', fontWeight: 'bold', color: 'var(--text-primary)'}}>
                Learn Crypto
              </h3>
              <p className={styles.my4} style={{color: 'var(--text-secondary)'}}>
                Educational resources and guides for cryptocurrency trading and investment.
              </p>
              <Button variant="outline" size="sm">
                Browse Guides
              </Button>
            </CardContent>
          </Card>

          <Card variant="outlined" interactive>
            <CardContent className={`${styles.p6} ${styles.textCenter}`}>
              <div className={styles.my4} style={{fontSize: 'var(--text-4xl)'}}>🔔</div>
              <h3 className={styles.my2} style={{fontSize: 'var(--text-xl)', fontWeight: 'bold', color: 'var(--text-primary)'}}>
                Price Alerts
              </h3>
              <p className={styles.my4} style={{color: 'var(--text-secondary)'}}>
                Set up custom alerts for price movements and market conditions.
              </p>
              <Button variant="outline" size="sm">
                Set Alerts
              </Button>
            </CardContent>
          </Card>

          <Card variant="outlined" interactive>
            <CardContent className={`${styles.p6} ${styles.textCenter}`}>
              <div className={styles.my4} style={{fontSize: 'var(--text-4xl)'}}>📱</div>
              <h3 className={styles.my2} style={{fontSize: 'var(--text-xl)', fontWeight: 'bold', color: 'var(--text-primary)'}}>
                Mobile App
              </h3>
              <p className={styles.my4} style={{color: 'var(--text-secondary)'}}>
                Take your crypto analysis on the go with our mobile application.
              </p>
              <Button variant="outline" size="sm">
                Coming Soon
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Footer Navigation */}
        <div className={`${styles.my12} ${styles.textCenter}`}>
          <Link href="/">
            <Button variant="ghost" size="lg">
              ← Back to Home
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
} 