"use client";

import React, { useEffect, useState, useCallback } from 'react';

interface PerformanceMetrics {
  pageLoadTime: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  cumulativeLayoutShift: number;
  apiResponseTimes: { [key: string]: number };
  memoryUsage?: number;
  renderCount: number;
}

interface PerformanceMonitorProps {
  enabled?: boolean;
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  showInProduction?: boolean;
}

export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  enabled = process.env.NODE_ENV === 'development',
  position = 'bottom-right',
  showInProduction = false
}) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    pageLoadTime: 0,
    firstContentfulPaint: 0,
    largestContentfulPaint: 0,
    cumulativeLayoutShift: 0,
    apiResponseTimes: {},
    renderCount: 0
  });
  const [isVisible, setIsVisible] = useState(false);
  
  // Don't show in production unless explicitly enabled
  const shouldShow = enabled && (process.env.NODE_ENV === 'development' || showInProduction);

  const updateMetrics = useCallback(() => {
    if (typeof window === 'undefined') return;

    try {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paint = performance.getEntriesByType('paint');
      
      const newMetrics: Partial<PerformanceMetrics> = {
        renderCount: metrics.renderCount + 1
      };

      // Page load time
      if (navigation) {
        newMetrics.pageLoadTime = navigation.loadEventEnd - navigation.fetchStart;
      }

      // Paint metrics
      paint.forEach((entry) => {
        if (entry.name === 'first-contentful-paint') {
          newMetrics.firstContentfulPaint = entry.startTime;
        }
      });

      // LCP using Performance Observer (if available)
      if ('PerformanceObserver' in window) {
        try {
          const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            if (lastEntry) {
              setMetrics(prev => ({
                ...prev,
                largestContentfulPaint: lastEntry.startTime
              }));
            }
          });
          observer.observe({ entryTypes: ['largest-contentful-paint'] });
        } catch (e) {
          console.warn('LCP monitoring not available:', e);
        }
      }

      // Memory usage (Chrome only)
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        newMetrics.memoryUsage = memory.usedJSHeapSize / 1024 / 1024; // MB
      }

      setMetrics(prev => ({ ...prev, ...newMetrics }));
    } catch (error) {
      console.warn('Performance monitoring error:', error);
    }
  }, [metrics.renderCount]);

  // Monitor API response times
  const monitorAPIRequests = useCallback(() => {
    if (typeof window === 'undefined') return;

    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const start = performance.now();
      const url = typeof args[0] === 'string' ? args[0] : 
                  args[0] instanceof URL ? args[0].href : 
                  args[0] instanceof Request ? args[0].url : 'unknown';
      
      try {
        const response = await originalFetch(...args);
        const end = performance.now();
        const responseTime = end - start;
        
        // Extract endpoint name from URL
        const endpointName = url.split('/').pop() || 'unknown';
        
        setMetrics(prev => ({
          ...prev,
          apiResponseTimes: {
            ...prev.apiResponseTimes,
            [endpointName]: responseTime
          }
        }));
        
        return response;
      } catch (error) {
        const end = performance.now();
        const responseTime = end - start;
        const endpointName = url.split('/').pop() || 'unknown';
        
        setMetrics(prev => ({
          ...prev,
          apiResponseTimes: {
            ...prev.apiResponseTimes,
            [`${endpointName}_error`]: responseTime
          }
        }));
        
        throw error;
      }
    };

    return () => {
      window.fetch = originalFetch;
    };
  }, []);

  useEffect(() => {
    if (!shouldShow) return;

    // Initial metrics collection
    updateMetrics();
    
    // Monitor API requests
    const cleanup = monitorAPIRequests();
    
    // Update metrics periodically
    const interval = setInterval(updateMetrics, 5000);
    
    return () => {
      clearInterval(interval);
      if (cleanup) cleanup();
    };
  }, [shouldShow, updateMetrics, monitorAPIRequests]);

  if (!shouldShow) return null;

  const positionClasses = {
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4'
  };

  const formatTime = (time: number) => {
    if (time === 0) return 'N/A';
    return time > 1000 ? `${(time / 1000).toFixed(2)}s` : `${time.toFixed(0)}ms`;
  };

  const formatMemory = (memory?: number) => {
    if (!memory) return 'N/A';
    return `${memory.toFixed(1)}MB`;
  };

  const getPerformanceColor = (metric: string, value: number) => {
    switch (metric) {
      case 'lcp':
        return value < 2500 ? '#10b981' : value < 4000 ? '#f59e0b' : '#ef4444';
      case 'fcp':
        return value < 1800 ? '#10b981' : value < 3000 ? '#f59e0b' : '#ef4444';
      case 'cls':
        return value < 0.1 ? '#10b981' : value < 0.25 ? '#f59e0b' : '#ef4444';
      case 'api':
        return value < 500 ? '#10b981' : value < 1000 ? '#f59e0b' : '#ef4444';
      default:
        return '#6b7280';
    }
  };

  return (
    <div 
      className={`fixed ${positionClasses[position]} z-50 transition-all duration-300`}
      style={{ 
        transform: isVisible ? 'translateY(0)' : 'translateY(10px)',
        opacity: isVisible ? 1 : 0.8
      }}
    >
      {/* Toggle Button */}
      <button
        onClick={() => setIsVisible(!isVisible)}
        className="mb-2 px-3 py-1 rounded-full text-xs font-bold text-white shadow-lg hover:scale-105 transition-transform"
        style={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          backdropFilter: 'blur(10px)'
        }}
      >
        📊 Perf
      </button>

      {/* Metrics Panel */}
      {isVisible && (
        <div 
          className="w-80 p-4 rounded-lg shadow-xl border backdrop-blur-sm"
          style={{ 
            background: 'rgba(0, 0, 0, 0.8)',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            color: 'white'
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-white">Performance Monitor</h3>
            <span 
              className="text-xs px-2 py-1 rounded"
              style={{ background: 'rgba(34, 197, 94, 0.2)', color: '#22c55e' }}
            >
              Live
            </span>
          </div>

          {/* Core Web Vitals */}
          <div className="space-y-2 mb-4">
            <div className="text-xs font-semibold text-gray-300 mb-2">Core Web Vitals</div>
            
            <div className="flex justify-between items-center">
              <span className="text-xs">FCP</span>
              <span 
                className="text-xs font-mono px-2 py-1 rounded"
                style={{ 
                  background: getPerformanceColor('fcp', metrics.firstContentfulPaint),
                  color: 'white'
                }}
              >
                {formatTime(metrics.firstContentfulPaint)}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-xs">LCP</span>
              <span 
                className="text-xs font-mono px-2 py-1 rounded"
                style={{ 
                  background: getPerformanceColor('lcp', metrics.largestContentfulPaint),
                  color: 'white'
                }}
              >
                {formatTime(metrics.largestContentfulPaint)}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-xs">Load Time</span>
              <span className="text-xs font-mono text-gray-300">
                {formatTime(metrics.pageLoadTime)}
              </span>
            </div>
          </div>

          {/* Memory Usage */}
          {metrics.memoryUsage && (
            <div className="mb-4">
              <div className="text-xs font-semibold text-gray-300 mb-2">Memory Usage</div>
              <div className="flex justify-between items-center">
                <span className="text-xs">JS Heap</span>
                <span className="text-xs font-mono text-blue-400">
                  {formatMemory(metrics.memoryUsage)}
                </span>
              </div>
            </div>
          )}

          {/* API Response Times */}
          {Object.keys(metrics.apiResponseTimes).length > 0 && (
            <div className="mb-4">
              <div className="text-xs font-semibold text-gray-300 mb-2">API Response Times</div>
              <div className="space-y-1 max-h-24 overflow-y-auto">
                {Object.entries(metrics.apiResponseTimes).slice(-5).map(([endpoint, time]) => (
                  <div key={endpoint} className="flex justify-between items-center">
                    <span className="text-xs truncate mr-2">{endpoint}</span>
                    <span 
                      className="text-xs font-mono px-1 py-0.5 rounded"
                      style={{ 
                        background: getPerformanceColor('api', time),
                        color: 'white'
                      }}
                    >
                      {formatTime(time)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Render Count */}
          <div className="text-xs text-gray-400 text-center pt-2 border-t border-gray-700">
            Renders: {metrics.renderCount}
          </div>
        </div>
      )}
    </div>
  );
};

export default PerformanceMonitor; 