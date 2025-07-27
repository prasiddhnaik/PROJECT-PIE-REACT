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

const inter = Inter({ subsets: ["latin"] });

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export const metadata: Metadata = {
  title: "XP Trading Pro - Windows XP Style Trading Platform",
  description: "Windows XP-style trading platform with real-time NSE stock data, portfolio management, and interactive trading tools.",
  keywords: ["trading", "stocks", "NSE", "portfolio", "windows-xp", "trading-platform"],
  authors: [{ name: "XP Trading Team" }],
  openGraph: {
    title: "XP Trading Pro",
    description: "Windows XP-style trading platform with real-time NSE data",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "XP Trading Pro",
    description: "Windows XP-style trading platform with real-time NSE data",
  },
  robots: {
    index: true,
    follow: true,
  },
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <main>
          {children}
        </main>
      </body>
    </html>
  );
}
