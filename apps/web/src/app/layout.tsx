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
import ReactQueryProvider from "./providers/ReactQueryProvider";

const inter = Inter({ subsets: ["latin"] });

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: "CapitalFlow Intelligence Platform",
  description:
    "Institutional-grade financial dashboard delivering live market coverage, analytics, portfolio insights, and research in a single command center.",
  keywords: [
    "capitalflow",
    "financial dashboard",
    "market analytics",
    "portfolio intelligence",
    "institutional trading",
  ],
  authors: [{ name: "CapitalFlow Team" }],
  openGraph: {
    title: "CapitalFlow Intelligence Platform",
    description:
      "Professional market intelligence with real-time data, algorithmic analytics, and actionable insights for institutional teams.",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "CapitalFlow Intelligence Platform",
    description:
      "Professional market intelligence with real-time data, algorithmic analytics, and actionable insights for institutional teams.",
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
        <ReactQueryProvider>
          <main>{children}</main>
        </ReactQueryProvider>
      </body>
    </html>
  );
}
