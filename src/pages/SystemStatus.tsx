import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  CpuChipIcon,
  ServerIcon,
  CodeBracketIcon
} from '@heroicons/react/24/outline';

interface PackageStatus {
  name: string;
  version: string;
  status: 'working' | 'error' | 'warning';
  description: string;
  error?: string;
}

interface SystemInfo {
  nodeVersion: string;
  reactVersion: string;
  browserInfo: string;
  timestamp: string;
}

const SystemStatus: React.FC = () => {
  const [packages, setPackages] = useState<PackageStatus[]>([]);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkPackageStatus();
  }, []);

  const checkPackageStatus = async () => {
    setLoading(true);
    
    // Frontend packages to check (from your actual package.json)
    const packagesToCheck = [
      { name: 'React', module: 'react', description: 'Core React library', version: '^18.2.0' },
      { name: 'React DOM', module: 'react-dom', description: 'React DOM rendering', version: '^18.2.0' },
      { name: 'TypeScript', module: 'typescript', description: 'TypeScript support', version: '^4.7.4' },
      { name: 'Tailwind CSS', module: 'tailwindcss', description: 'Utility-first CSS framework', version: '^3.3.0' },
      { name: 'Framer Motion', module: 'framer-motion', description: 'Animation library', version: '^10.12.18' },
      { name: 'React Query', module: 'react-query', description: 'Data fetching and caching', version: '^3.39.3' },
      { name: 'Axios', module: 'axios', description: 'HTTP client', version: '^1.4.0' },
      { name: 'React Router', module: 'react-router-dom', description: 'Client-side routing', version: '^6.3.0' },
      { name: 'Heroicons', module: '@heroicons/react', description: 'Icon library', version: '^2.0.18' },
      { name: 'React Hot Toast', module: 'react-hot-toast', description: 'Toast notifications', version: '^2.4.1' },
      { name: 'Recharts', module: 'recharts', description: 'Chart library', version: '^2.7.2' },
      { name: 'Date-fns', module: 'date-fns', description: 'Date utility library', version: '^2.30.0' },
      { name: 'Plotly.js', module: 'plotly.js', description: 'Interactive charts', version: '^2.24.1' },
      { name: 'React Plotly', module: 'react-plotly.js', description: 'React wrapper for Plotly', version: '^2.6.0' },
      { name: 'Headless UI', module: '@headlessui/react', description: 'Unstyled UI components', version: '^1.7.15' },
      { name: 'Zustand', module: 'zustand', description: 'State management', version: '^4.3.9' },
      { name: 'PostCSS', module: 'postcss', description: 'CSS processing tool', version: '^8.4.24' },
      { name: 'Autoprefixer', module: 'autoprefixer', description: 'CSS vendor prefixes', version: '^10.4.14' }
    ];

    const packageStatuses: PackageStatus[] = [];

    for (const pkg of packagesToCheck) {
      try {
        // Try to dynamically import the package
        let version = 'unknown';
        let status: 'working' | 'error' | 'warning' = 'working';
        let error: string | undefined;

        try {
          // Special handling for different packages
          if (pkg.name === 'React') {
            version = React.version;
          } else if (pkg.name === 'Axios') {
            const axios = await import('axios');
            version = axios.default.VERSION || pkg.version;
          } else if (pkg.name === 'Tailwind CSS') {
            // Check if Tailwind classes are working
            const testElement = document.createElement('div');
            testElement.className = 'bg-blue-500';
            document.body.appendChild(testElement);
            const computedStyle = window.getComputedStyle(testElement);
            const backgroundColor = computedStyle.backgroundColor;
            document.body.removeChild(testElement);
            
            if (backgroundColor && backgroundColor !== 'rgba(0, 0, 0, 0)') {
              version = pkg.version;
            } else {
              status = 'warning';
              error = 'Styles may not be loading correctly';
              version = pkg.version;
            }
          } else {
            // Generic import attempt
            await import(pkg.module);
            version = pkg.version;
          }
        } catch (importError) {
          status = 'error';
          error = `Failed to load: ${importError}`;
          version = 'not found';
        }

        packageStatuses.push({
          name: pkg.name,
          version,
          status,
          description: pkg.description,
          error
        });
      } catch (err) {
        packageStatuses.push({
          name: pkg.name,
          version: 'unknown',
          status: 'error',
          description: pkg.description,
          error: `Check failed: ${err}`
        });
      }
    }

    // Get system information
    const systemInfo: SystemInfo = {
      nodeVersion: process.env.NODE_VERSION || 'unknown',
      reactVersion: React.version,
      browserInfo: navigator.userAgent,
      timestamp: new Date().toISOString()
    };

    setPackages(packageStatuses);
    setSystemInfo(systemInfo);
    setLoading(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'working':
        return <CheckCircleIcon className="h-5 w-5 text-green-400" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-400" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'working':
        return 'border-green-500/30 bg-green-500/10';
      case 'warning':
        return 'border-yellow-500/30 bg-yellow-500/10';
      case 'error':
        return 'border-red-500/30 bg-red-500/10';
      default:
        return 'border-gray-500/30 bg-gray-500/10';
    }
  };

  const workingCount = packages.filter(p => p.status === 'working').length;
  const warningCount = packages.filter(p => p.status === 'warning').length;
  const errorCount = packages.filter(p => p.status === 'error').length;
  const totalCount = packages.length;
  const healthPercentage = totalCount > 0 ? Math.round((workingCount / totalCount) * 100) : 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-4xl font-bold text-primary-50 mb-2">
          System Status
        </h1>
        <p className="text-lg text-primary-100/80">
          Frontend packages and system health monitoring
        </p>
      </motion.div>

      {/* Health Overview */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
      >
        <h2 className="text-2xl font-semibold text-primary-50 mb-6 flex items-center">
          <ServerIcon className="h-6 w-6 mr-2 text-accent-emerald" />
          System Health Overview
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-primary-900/50 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-primary-50">{healthPercentage}%</div>
            <div className="text-primary-400 text-sm">Overall Health</div>
          </div>
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-400">{workingCount}</div>
            <div className="text-green-300 text-sm">Working</div>
          </div>
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-yellow-400">{warningCount}</div>
            <div className="text-yellow-300 text-sm">Warnings</div>
          </div>
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-red-400">{errorCount}</div>
            <div className="text-red-300 text-sm">Errors</div>
          </div>
        </div>

        {/* Health Bar */}
        <div className="w-full bg-primary-800 rounded-full h-3 mb-4">
          <div 
            className="bg-gradient-to-r from-accent-emerald to-primary-500 h-3 rounded-full transition-all duration-1000"
            style={{ width: `${healthPercentage}%` }}
          ></div>
        </div>

        <div className="flex justify-between text-sm text-primary-400">
          <span>System Health</span>
          <span>{healthPercentage >= 80 ? '🟢 Excellent' : healthPercentage >= 60 ? '🟡 Good' : '🔴 Needs Attention'}</span>
        </div>
      </motion.section>

      {/* Package Status */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
      >
        <h2 className="text-2xl font-semibold text-primary-50 mb-6 flex items-center">
          <CodeBracketIcon className="h-6 w-6 mr-2 text-accent-emerald" />
          Package Status
          <button
            onClick={checkPackageStatus}
            disabled={loading}
            className="ml-auto px-4 py-2 bg-accent-emerald hover:bg-primary-500 text-white rounded-lg transition-colors disabled:opacity-50 text-sm"
          >
            {loading ? 'Checking...' : 'Refresh'}
          </button>
        </h2>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(12)].map((_, i) => (
              <div key={i} className="bg-primary-900/30 rounded-lg p-4 animate-pulse">
                <div className="h-4 bg-primary-800 rounded mb-2"></div>
                <div className="h-3 bg-primary-800 rounded mb-2 w-3/4"></div>
                <div className="h-3 bg-primary-800 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {packages.map((pkg, index) => (
              <motion.div
                key={pkg.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`rounded-lg p-4 border ${getStatusColor(pkg.status)}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-primary-50">{pkg.name}</h3>
                  {getStatusIcon(pkg.status)}
                </div>
                <p className="text-primary-300 text-sm mb-2">{pkg.description}</p>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-primary-400">v{pkg.version}</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    pkg.status === 'working' ? 'bg-green-500/20 text-green-400' :
                    pkg.status === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {pkg.status.toUpperCase()}
                  </span>
                </div>
                {pkg.error && (
                  <div className="mt-2 p-2 bg-red-500/10 border border-red-500/20 rounded text-xs text-red-300">
                    {pkg.error}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </motion.section>

      {/* System Information */}
      {systemInfo && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
        >
          <h2 className="text-2xl font-semibold text-primary-50 mb-6 flex items-center">
            <CpuChipIcon className="h-6 w-6 mr-2 text-accent-emerald" />
            System Information
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-primary-900/50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">Project Info</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-primary-400">Name:</span>
                  <span className="text-primary-50">Financial Analytics Hub</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-primary-400">Version:</span>
                  <span className="text-primary-50">v2.2.0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-primary-400">Total Packages:</span>
                  <span className="text-primary-50">{totalCount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-primary-400">Build Tool:</span>
                  <span className="text-primary-50">React Scripts 5.0.1</span>
                </div>
              </div>
            </div>

            <div className="bg-primary-900/50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">Runtime</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-primary-400">React Version:</span>
                  <span className="text-primary-50">{systemInfo.reactVersion}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-primary-400">Node Version:</span>
                  <span className="text-primary-50">{systemInfo.nodeVersion}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-primary-400">Last Check:</span>
                  <span className="text-primary-50">{new Date(systemInfo.timestamp).toLocaleTimeString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-primary-400">Environment:</span>
                  <span className="text-primary-50">{process.env.NODE_ENV || 'development'}</span>
                </div>
              </div>
            </div>

            <div className="bg-primary-900/50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-primary-50 mb-3">Browser</h3>
              <div className="text-sm text-primary-300 break-all">
                {systemInfo.browserInfo}
              </div>
            </div>
          </div>
        </motion.section>
      )}
    </div>
  );
};

export default SystemStatus; 