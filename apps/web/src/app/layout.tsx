/**
 * @fileoverview Root layout component for the Crypto Analytics Platform
 * 
 * This file contains the root layout that wraps all pages in the Next.js application.
 * It sets up the HTML structure, global providers, styling, and metadata for the
 * entire crypto analytics platform.
 * 
 * @version 1.0.0
 */

import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import ReactQueryProvider from "../providers/ReactQueryProvider";
import { ThemeProvider } from "../components/ThemeProvider";
import ServiceWorkerRegistration from "../components/ServiceWorkerRegistration";
import styles from '@/styles/layouts.module.css';

// Configure the Inter font with Latin subset for optimal performance
// Inter is chosen for its excellent readability in financial data displays
const inter = Inter({ subsets: ["latin"] });

/**
 * Viewport configuration for responsive design
 * Separated from metadata per Next.js 15 requirements
 */
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

/**
 * Metadata configuration for the crypto analytics platform
 * Optimized for SEO and social media sharing
 */
export const metadata: Metadata = {
  title: "Crypto Analytics Hub - Advanced Cryptocurrency Market Analysis",
  description: "Professional cryptocurrency analytics platform with AI-powered insights, real-time market data, technical analysis, and comprehensive portfolio tracking.",
  keywords: ["cryptocurrency", "bitcoin", "ethereum", "market analysis", "crypto trading", "blockchain", "DeFi"],
  authors: [{ name: "Crypto Analytics Team" }],
  openGraph: {
    title: "Crypto Analytics Hub",
    description: "Advanced cryptocurrency market analysis with AI insights",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "Crypto Analytics Hub",
    description: "Advanced cryptocurrency market analysis with AI insights",
  },
  robots: {
    index: true,
    follow: true,
  },
};

/**
 * Props interface for the root layout component
 */
interface RootLayoutProps {
  /** Child components/pages to be rendered within the layout */
  children: React.ReactNode;
}

/**
 * Root layout component for the crypto analytics platform.
 * 
 * This component provides the foundational HTML structure and global providers
 * for the entire application. It wraps all pages and ensures consistent
 * styling, data management, and accessibility features across the platform.
 * 
 * @component
 * @param props - The layout props containing children to render
 * @returns The complete HTML document structure with providers
 * 
 * @accessibility
 * - Semantic HTML structure with proper lang attribute
 * - Viewport meta tag for responsive design
 * - Font loading optimization to prevent layout shift
 * - Screen reader compatible structure
 * 
 * @performance
 * - Inter font preloading for optimal text rendering
 * - React Query provider for efficient data caching
 * - Global CSS loading for consistent styling
 * 
 * @seo
 * - Comprehensive metadata for search engines
 * - Open Graph tags for social media sharing
 * - Twitter Card configuration
 * - Proper document structure for crawlers
 */
export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" className="scroll-smooth">
      {/* Document head is managed by Next.js metadata API */}
      <body className={`${inter.className} antialiased`} style={{background: 'var(--background)', color: 'var(--text-primary)'}}>
        {/* 
          ThemeProvider manages theme state and applies CSS variables
          - Supports light, dark, and crypto themes
          - Persists theme preference in localStorage
          - Provides theme context to all components
          - Handles system theme detection
        */}
        <ThemeProvider defaultTheme="dark">
          {/* 
            ReactQueryProvider wraps the entire application to provide:
            - Global state management for API data
            - Intelligent caching and background refetching
            - Optimistic updates for better UX
            - Error handling and retry mechanisms
            - Offline support and data synchronization
          */}
          <ReactQueryProvider>
            {/* 
              Main content area with proper semantic structure
              - Uses semantic main tag for accessibility
              - Full viewport height for proper layout
              - Flex layout for responsive design
            */}
            <main className={`${styles.minHeightScreen} ${styles.flexCol}`}>
              {children}
            </main>
          </ReactQueryProvider>
          
          {/* Service Worker Registration */}
          <ServiceWorkerRegistration />
        </ThemeProvider>
        
        {/* 
          Portal root for modals, tooltips, and overlays
          This div is used by React portals to render UI elements
          outside the normal component hierarchy when needed
        */}
        <div id="portal-root" />
      </body>
    </html>
  );
}
