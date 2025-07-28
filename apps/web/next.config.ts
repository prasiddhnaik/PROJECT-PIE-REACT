import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable static export for GitHub Pages
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  experimental: {
    // Enable React 19 features
    optimizeCss: true,
  },
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001',
  },
  typescript: {
    // Type checking during build
    ignoreBuildErrors: true,
  },
  eslint: {
    // Linting during build
    ignoreDuringBuilds: true,
  },

  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Enhanced CSS processing
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }

    // Optimize CSS for production
    if (!dev) {
      config.optimization = {
        ...config.optimization,
        usedExports: true,
        sideEffects: false,
      };
    }

    return config;
  },
  // CSS optimization
  productionBrowserSourceMaps: false,
  // Enable static optimization
  // Compression
  compress: true,
  // Power-ups for better performance
  poweredByHeader: false,
  reactStrictMode: true,
};

export default nextConfig;
