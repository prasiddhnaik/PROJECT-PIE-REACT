'use client'

import * as React from 'react';
import { useEffect } from 'react';
import './globals.css';

// Define types for better TypeScript support
interface StockData {
  symbol: string;
  name?: string;
  price: number;
  change: number;
  change_percent?: number;
  volume?: number;
  market_cap?: number;
  pe_ratio?: number;
  high?: number;
  low?: number;
  open?: number;
  prev_close?: number;
}

// Extend Window interface for global functions
declare global {
  interface Window {
    closeWindow: (windowId: string) => void;
    minimizeWindow: (windowId: string) => void;
    maximizeWindow: (windowId: string) => void;
    showConfirmation: (orderType: string) => void;
    executeOrder: () => void;
    updateOrderPreview: () => void;
    changeChartPeriod: (period: string) => void;
    switchPortfolioView: (view: string, searchTerm?: string) => void;
    showStockDetails: (symbol: string) => void;
    openOrderFromDetails: () => void;
    showNewsDetails: (index: number) => void;
    showStartMenu: () => void;
  }
}

export default function Home() {
  useEffect(() => {
    // Global variables
    let dragElement: HTMLElement | null = null;
    let dragOffset = { x: 0, y: 0 };
    let zIndexCounter = 100;
    let currentOrderType = '';
    let currentNewsIndex = 0;
    let stockDataCache: StockData[] = [];
    let currentView = 'all';

    const newsArticles = [
      { title: 'Reliance Industries Q3 Results', content: 'Reliance Industries reported strong Q3 results with revenue growth of 15% YoY, driven by robust performance in retail and telecom sectors. Jio added 12 million subscribers, while retail segment saw 25% revenue increase. EBIT margins improved to 18.5%.' },
      { title: 'TCS Digital Transformation', content: 'TCS announced 25% growth in digital transformation revenue, securing major deals in cloud and AI services. The company reported strong Q2 results with improved margins and optimistic outlook for FY2025.' },
      { title: 'HDFC Bank Merger', content: 'HDFC Bank successfully completed its merger, creating India\'s largest private sector bank. The combined entity reports strong asset quality and expanded retail presence across the country.' },
      { title: 'Infosys AI Services', content: 'Infosys launches new AI and cloud services platform, partnering with global tech giants. Q3 results show 18% growth in digital services revenue with several large deal wins.' },
      { title: 'Bharti Airtel 5G', content: 'Airtel accelerates 5G rollout in major cities, adding 15 million users. The company reports improved ARPU and strong growth in enterprise segment.' },
      { title: 'Adani Ports Q2 Revenue', content: 'Adani Ports reports 18% revenue growth in Q2, with increased cargo handling at Mundra port. Expansion plans include new terminals and logistics parks.' },
      { title: 'Wipro AI Initiative', content: 'Wipro launches comprehensive AI initiative with investments in generative AI and machine learning. Partners with leading tech firms for enterprise solutions.' }
    ];

    // Core functions
    function simulateLoading() {
      const loadingScreen = document.getElementById('loadingScreen');
      const progressBar = document.getElementById('loadingProgress');
      let progress = 0;
      
      const loadingInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 100) progress = 100;
        
        if (progressBar) {
          progressBar.style.width = progress + '%';
        }
        
        if (progress >= 100) {
          clearInterval(loadingInterval);
          setTimeout(() => {
            if (loadingScreen) {
              loadingScreen.style.display = 'none';
            }
            // Open initial windows
            const portfolioWindow = document.getElementById('portfolioWindow');
            const watchlistWindow = document.getElementById('watchlistWindow');
            if (portfolioWindow) portfolioWindow.style.display = 'block';
            if (watchlistWindow) watchlistWindow.style.display = 'block';
          }, 500);
        }
      }, 200);
    }

    function initializeDragAndDrop() {
      const windows = document.querySelectorAll('.xp-window');
      
      windows.forEach(window => {
        const titlebar = window.querySelector('.xp-titlebar') as HTMLElement | null;
        
        if (titlebar) {
          titlebar.addEventListener('mousedown', (e: Event) => {
            const mouseEvent = e as MouseEvent;
            const target = mouseEvent.target as HTMLElement;
            if (target && target.classList.contains('xp-titlebar-button')) return;
            
            dragElement = window as HTMLElement;
            dragOffset.x = mouseEvent.clientX - (window as HTMLElement).offsetLeft;
            dragOffset.y = mouseEvent.clientY - (window as HTMLElement).offsetTop;
            
            // Bring to front
            (window as HTMLElement).style.zIndex = String(++zIndexCounter);
            
            // Mark as active
            document.querySelectorAll('.xp-titlebar').forEach(tb => tb.classList.add('inactive'));
            titlebar.classList.remove('inactive');
            
            mouseEvent.preventDefault();
          });
        }
      });
      
      document.addEventListener('mousemove', (e: Event) => {
        const mouseEvent = e as MouseEvent;
        if (dragElement) {
          const newX = mouseEvent.clientX - dragOffset.x;
          const newY = mouseEvent.clientY - dragOffset.y;
          
          dragElement.style.left = Math.max(0, Math.min(newX, window.innerWidth - dragElement.offsetWidth)) + 'px';
          dragElement.style.top = Math.max(0, Math.min(newY, window.innerHeight - dragElement.offsetHeight - 30)) + 'px';
        }
      });
      
      document.addEventListener('mouseup', () => {
        dragElement = null;
      });
    }

    function updateClock() {
      const now = new Date();
      const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const clockElement = document.getElementById('clock');
      if (clockElement) {
        clockElement.textContent = timeString;
      }
    }

    // Window management functions
    function closeWindow(windowId: string) {
      const window = document.getElementById(windowId);
      if (window) {
        window.style.display = 'none';
      }
    }

    function minimizeWindow(windowId: string) {
      const window = document.getElementById(windowId);
      if (window) {
        window.style.display = 'none';
      }
    }

    function maximizeWindow(windowId: string) {
      const window = document.getElementById(windowId);
      if (window) {
        if (window.style.width === '100vw') {
          // Restore
          window.style.width = '';
          window.style.height = '';
          window.style.left = '';
          window.style.top = '';
        } else {
          // Maximize
          window.style.width = '100vw';
          window.style.height = 'calc(100vh - 30px)';
          window.style.left = '0';
          window.style.top = '0';
        }
      }
    }

    // Order functions
    function showConfirmation(orderType: string) {
      currentOrderType = orderType;
      const dialog = document.getElementById('confirmDialog');
      const message = document.getElementById('confirmMessage');
      
      if (dialog && message) {
        message.textContent = `Are you sure you want to place this ${orderType} order?`;
        dialog.style.display = 'block';
        dialog.style.zIndex = String(++zIndexCounter);
      }
    }

    function executeOrder() {
      const symbol = (document.getElementById('orderSymbol') as HTMLInputElement)?.value || 'RELIANCE';
      const quantity = (document.getElementById('orderQuantity') as HTMLInputElement)?.value || '10';
      const price = (document.getElementById('orderPrice') as HTMLInputElement)?.value || '2847.50';
      const orderType = (document.getElementById('orderType') as HTMLSelectElement)?.value || 'Market Order';
      
      alert(`${currentOrderType} order executed!\n\nDetails:\nSymbol: ${symbol}\nQuantity: ${quantity}\nPrice: ₹${price}\nType: ${orderType}\nTotal: ₹${(parseFloat(quantity) * parseFloat(price)).toFixed(2)}`);
      closeWindow('confirmDialog');
      closeWindow('orderDialog');
      
      // Simulate adding to portfolio
      alert(`Added to portfolio: ${quantity} shares of ${symbol}`);
    }

    function updateOrderPreview() {
      const symbol = (document.getElementById('orderSymbol') as HTMLInputElement)?.value || 'RELIANCE';
      const quantity = parseInt((document.getElementById('orderQuantity') as HTMLInputElement)?.value || '0');
      const price = parseFloat((document.getElementById('orderPrice') as HTMLInputElement)?.value || '0');
      const total = (quantity * price).toFixed(2);
      
      const previewElement = document.getElementById('orderPreview');
      if (previewElement) {
        previewElement.innerHTML = `${currentOrderType || 'Buy'} ${quantity} shares of ${symbol} at ₹${price.toFixed(2)}<br><strong>Total Cost: ₹${total}</strong>`;
      }
    }

    // Chart functions
    function changeChartPeriod(period: string) {
      const chartInfo = document.getElementById('chartInfo');
      const chartTitle = document.getElementById('chartTitle');
      const selectedStock = chartTitle?.textContent?.split(' - ')[1] || 'RELIANCE';
      
      // Simulate fetching period data
      const randomPrice = (Math.random() * 1000 + 1000).toFixed(2);
      const randomChange = parseFloat(((Math.random() - 0.5) * 5).toFixed(1));
      const isPositive = randomChange >= 0;
      
      if (chartInfo) {
        chartInfo.textContent = `${selectedStock}: ₹${randomPrice} (${isPositive ? '+' : ''}${randomChange}%) Volume: ${(Math.random() * 10).toFixed(1)}Cr | Period: ${period}`;
      }
      
      // Update technical indicators
      const indicatorsElement = document.getElementById('technicalIndicators');
      if (indicatorsElement) {
        indicatorsElement.innerHTML = `
          <span>RSI: ${(Math.random() * 100).toFixed(1)}</span>
          <span>MACD: ${(Math.random() * 10 - 5).toFixed(2)}</span>
          <span>MA(50): ₹${(Math.random() * 1000 + 1000).toFixed(2)}</span>
          <span>MA(200): ₹${(Math.random() * 1000 + 1000).toFixed(2)}</span>
        `;
      }
      
      alert(`Chart updated to ${period} period for ${selectedStock}`);
    }

    // Portfolio functions
    function switchPortfolioView(view: string, searchTerm = '') {
      currentView = view;
      console.log(`Switching to view: ${view}`);
      const portfolioList = document.getElementById('portfolioList');
      
      if (portfolioList) {
        while (portfolioList.children.length > 1) {
          const lastChild = portfolioList.lastChild;
          if (lastChild) portfolioList.removeChild(lastChild);
        }
        
        let viewStocks = stockDataCache.length > 0 ? stockDataCache : [
          { symbol: 'RELIANCE', price: 2847.50, change: 45.20, name: 'Reliance Industries' },
          { symbol: 'TCS', price: 4125.30, change: 87.50, name: 'Tata Consultancy Services' },
          { symbol: 'INFY', price: 1821.45, change: -21.40, name: 'Infosys Limited' },
          { symbol: 'HDFCBANK', price: 1742.85, change: 31.50, name: 'HDFC Bank' },
          { symbol: 'ITC', price: 425.60, change: 8.50, name: 'ITC Limited' },
          { symbol: 'ICICIBANK', price: 1045.20, change: -15.80, name: 'ICICI Bank' }
        ];
        
        if (view !== 'all' && view !== 'stocks' && view !== 'watchlist') {
          viewStocks = [];
        }
        
        if (searchTerm) {
          viewStocks = viewStocks.filter(stock => 
            stock.symbol.toLowerCase().includes(searchTerm) || 
            (stock.name && stock.name.toLowerCase().includes(searchTerm))
          );
        }
        
        console.log(`View stocks count: ${viewStocks.length}`);
        
        viewStocks.forEach(stock => {
          const row = document.createElement('div');
          row.className = 'xp-listview-row';
          row.onclick = () => showStockDetails(stock.symbol);
          row.innerHTML = `
            <div class="xp-listview-cell">${stock.symbol}</div>
            <div class="xp-listview-cell">100</div>
            <div class="xp-listview-cell">₹${stock.price.toFixed(2)}</div>
            <div class="xp-listview-cell">₹${(stock.price * 100).toLocaleString('en-IN')}</div>
            <div class="xp-listview-cell" style="color: ${stock.change >= 0 ? 'green' : 'red'};">${stock.change >= 0 ? '+' : ''}₹${stock.change.toFixed(2)}</div>
          `;
          portfolioList.appendChild(row);
        });
        
        alert(`Switched to ${view} view - showing ${viewStocks.length} items`);
      }
    }

    // Stock details functions
    function showStockDetails(symbol: string) {
      const stock = stockDataCache.find(s => s.symbol === symbol) || {
        symbol: symbol,
        price: 2847.50,
        pe_ratio: 25.4,
        market_cap: 1920000000000,
        high: 3025,
        low: 2221
      };
      
      const detailsTitle = document.getElementById('detailsTitle');
      const detailsSymbol = document.getElementById('detailsSymbol');
      const detailsPrice = document.getElementById('detailsPrice');
      const detailsPE = document.getElementById('detailsPE');
      const detailsMarketCap = document.getElementById('detailsMarketCap');
      const detailsHighLow = document.getElementById('detailsHighLow');
      
      if (detailsTitle) detailsTitle.textContent = `📈 Stock Details - ${symbol}`;
      if (detailsSymbol) detailsSymbol.textContent = stock.symbol;
      if (detailsPrice) detailsPrice.textContent = `₹${stock.price.toFixed(2)}`;
      if (detailsPE) detailsPE.textContent = (stock.pe_ratio || 0).toFixed(2);
      if (detailsMarketCap) detailsMarketCap.textContent = `₹${((stock.market_cap || 0) / 10000000000000).toFixed(2)} lakh Cr`;
      if (detailsHighLow) detailsHighLow.textContent = `₹${(stock.high || 0).toFixed(2)} / ₹${(stock.low || 0).toFixed(2)}`;
      
      const stockDetails = document.getElementById('stockDetails');
      if (stockDetails) {
        stockDetails.style.display = 'block';
        stockDetails.style.zIndex = String(++zIndexCounter);
      }
    }

    function openOrderFromDetails() {
      const symbol = document.getElementById('detailsSymbol')?.textContent || 'RELIANCE';
      const orderSymbol = document.getElementById('orderSymbol') as HTMLInputElement;
      const orderDialog = document.getElementById('orderDialog');
      
      if (orderSymbol) orderSymbol.value = symbol;
      if (orderDialog) {
        orderDialog.style.display = 'block';
        closeWindow('stockDetails');
        updateOrderPreview();
      }
    }

    // News functions
    function showNewsDetails(index: number) {
      currentNewsIndex = index;
      const newsTitle = document.getElementById('newsTitle');
      const newsContent = document.querySelector('#newsDetails p');
      const newsDetails = document.getElementById('newsDetails');
      
      if (newsTitle && newsArticles[index]) {
        newsTitle.textContent = newsArticles[index].title;
      }
      if (newsContent && newsArticles[index]) {
        newsContent.textContent = newsArticles[index].content;
      }
      if (newsDetails) {
        newsDetails.style.display = 'block';
        newsDetails.style.zIndex = String(++zIndexCounter);
      }
    }

    // Start menu function
    function showStartMenu() {
      const menu = document.getElementById('startMenu');
      if (menu) {
        menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
        menu.style.zIndex = String(++zIndexCounter);
      }
    }

    // NSE Data fetching functions
    const NSE_API_BASE = 'http://localhost:8002';
    
    async function fetchNSEData() {
      try {
        console.log('Fetching popular stocks...');
        const response = await fetch(`${NSE_API_BASE}/stocks/popular`);
        console.log('Response status:', response.status);
        if (response.ok) {
          const data = await response.json();
          console.log('Fetched stocks:', data.data.length);
          stockDataCache = data.data;
          updatePortfolioData(stockDataCache);
          updateWatchlistData(stockDataCache);
          updateHeatMap(stockDataCache);
        } else {
          console.error('Failed to fetch stocks:', response.statusText);
          updateWithMockData();
        }
        
        // Fetch market indices
        const indicesResponse = await fetch(`${NSE_API_BASE}/market/indices`);
        if (indicesResponse.ok) {
          const indicesData = await indicesResponse.json();
          updateTicker(indicesData.data);
        }
        
        // Fetch gainers/losers for news
        const glResponse = await fetch(`${NSE_API_BASE}/market/gainers-losers`);
        if (glResponse.ok) {
          const glData = await glResponse.json();
          updateNews(glData.data);
        }
        
      } catch (error) {
        console.error('Error fetching NSE data:', error);
        updateWithMockData();
      }
    }
    
    function updatePortfolioData(stocks: StockData[]) {
      const portfolioList = document.getElementById('portfolioList');
      if (!portfolioList) return;
      
      // Clear existing rows except header
      while (portfolioList.children.length > 1) {
        const lastChild = portfolioList.lastChild;
        if (lastChild) portfolioList.removeChild(lastChild);
      }
      
      let totalValue = 0;
      let totalChange = 0;
      
      stocks.forEach(stock => {
        const shares = Math.floor(Math.random() * 100) + 1; // Random shares for simulation
        const value = stock.price * shares;
        const changeValue = stock.change * shares;
        
        totalValue += value;
        totalChange += changeValue;
        
        const row = document.createElement('div');
        row.className = 'xp-listview-row';
        row.onclick = () => showStockDetails(stock.symbol);
        row.innerHTML = `
          <div class="xp-listview-cell">${stock.symbol}</div>
          <div class="xp-listview-cell">${shares}</div>
          <div class="xp-listview-cell">₹${stock.price.toFixed(2)}</div>
          <div class="xp-listview-cell">₹${value.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
          <div class="xp-listview-cell" style="color: ${changeValue >= 0 ? 'green' : 'red'};">${changeValue >= 0 ? '+' : ''}₹${Math.abs(changeValue).toFixed(2)}</div>
        `;
        portfolioList.appendChild(row);
      });
      
      const totalChangePercent = totalValue > 0 ? (totalChange / (totalValue - totalChange) * 100) : 0;
      const statusbar = document.querySelector('#portfolioWindow .xp-statusbar');
      if (statusbar) {
        statusbar.textContent = `Total Value: ₹${totalValue.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})} | Change: ${totalChange >= 0 ? '+' : ''}₹${totalChange.toFixed(2)} (${totalChangePercent.toFixed(1)}%) | ${stocks.length} positions`;
      }
    }
    
    function updateWatchlistData(stocks: StockData[]) {
      const watchlist = document.querySelector('#watchlistWindow .xp-listview');
      if (!watchlist) return;
      
      // Clear existing rows except header
      while (watchlist.children.length > 1) {
        const lastChild = watchlist.lastChild;
        if (lastChild) watchlist.removeChild(lastChild);
      }
      
      stocks.forEach(stock => {
        const row = document.createElement('div');
        row.className = 'xp-listview-row';
        row.onclick = () => showStockDetails(stock.symbol);
        row.innerHTML = `
          <div class="xp-listview-cell">${stock.symbol}</div>
          <div class="xp-listview-cell">₹${stock.price.toFixed(2)}</div>
          <div class="xp-listview-cell" style="color: ${stock.change >= 0 ? 'green' : 'red'};">${stock.change >= 0 ? '+' : ''}₹${stock.change.toFixed(2)} (${stock.change_percent?.toFixed(1) || '0.0'}%)</div>
        `;
        watchlist.appendChild(row);
      });
    }
    
    function updateHeatMap(stocks: StockData[]) {
      const heatMap = document.querySelector('.heat-map');
      if (!heatMap) return;
      
      heatMap.innerHTML = ''; // Clear existing cells
      
      stocks.forEach(stock => {
        const changePercent = stock.change_percent || 0;
        const cell = document.createElement('div');
        cell.className = 'heat-cell';
        if (changePercent > 0.5) cell.classList.add('positive');
        else if (changePercent < -0.5) cell.classList.add('negative');
        else cell.classList.add('neutral');
        cell.innerHTML = `${stock.symbol}<br>${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(1)}%`;
        heatMap.appendChild(cell);
      });
    }
    
    function updateTicker(indices: any) {
      const tickerContent = document.querySelector('.ticker-content');
      if (tickerContent && indices?.NIFTY50 && indices?.BANKNIFTY) {
        const nifty = indices.NIFTY50;
        const bankNifty = indices.BANKNIFTY;
        tickerContent.textContent = `📈 NIFTY 50: ${nifty.value.toFixed(0)} (${nifty.change_percent >= 0 ? '+' : ''}${nifty.change_percent.toFixed(1)}%) | BANK NIFTY: ${bankNifty.value.toFixed(0)} (${bankNifty.change_percent >= 0 ? '+' : ''}${bankNifty.change_percent.toFixed(1)}%) | 🏦 10Y Bond: 6.85% | 💰 Gold: ₹72,450/10g | 🛢️ Crude: ₹6,245/bbl | 💱 USD/INR: 84.52`;
      }
    }
    
    function updateNews(gainersLosers: any) {
      const newsList = document.querySelector('#newsWindow .xp-listview');
      if (!newsList) return;
      
      // Clear existing rows
      newsList.innerHTML = '';
      
      const allItems = [...(gainersLosers.gainers || []), ...(gainersLosers.losers || [])];
      allItems.forEach(item => {
        const row = document.createElement('div');
        row.className = 'xp-listview-row';
        row.onclick = () => showNewsDetails(0);
        row.innerHTML = `<div class="xp-listview-cell">📈 ${item.symbol} ${item.change_percent >= 0 ? 'gains' : 'drops'} ${Math.abs(item.change_percent).toFixed(1)}% - ₹${item.price.toFixed(2)}</div>`;
        newsList.appendChild(row);
      });
    }
    
    function updateWithMockData() {
      const priceElements = document.querySelectorAll('.xp-listview-cell');
      priceElements.forEach(element => {
        if (element.textContent && element.textContent.includes('₹') && !element.textContent.includes('%')) {
          const currentPrice = parseFloat(element.textContent.replace('₹', '').replace(',', ''));
          if (!isNaN(currentPrice)) {
            const change = (Math.random() - 0.5) * 20;
            const newPrice = Math.max(1, currentPrice + change);
            element.textContent = '₹' + newPrice.toFixed(2);
          }
        }
      });
    }

    // Initialize the application
    const initializeApp = () => {
      // Start loading sequence
      simulateLoading();
      
      // Update clock
      updateClock();
      setInterval(updateClock, 1000);
      
      // Add drag functionality to all windows
      initializeDragAndDrop();
      
      // Fetch real NSE data
      fetchNSEData();
      setInterval(fetchNSEData, 30000); // Update every 30 seconds
      
      // Add button event listeners
      const orderSymbol = document.getElementById('orderSymbol') as HTMLInputElement;
      const orderQuantity = document.getElementById('orderQuantity') as HTMLInputElement;
      const orderPrice = document.getElementById('orderPrice') as HTMLInputElement;
      
      if (orderSymbol) orderSymbol.addEventListener('input', updateOrderPreview);
      if (orderQuantity) orderQuantity.addEventListener('input', updateOrderPreview);
      if (orderPrice) orderPrice.addEventListener('input', updateOrderPreview);
      
      // Initial view
      switchPortfolioView('all');
    };

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initializeApp);
    } else {
      initializeApp();
    }

    // Add global functions to window object
    window.closeWindow = closeWindow;
    window.minimizeWindow = minimizeWindow;
    window.maximizeWindow = maximizeWindow;
    window.showConfirmation = showConfirmation;
    window.executeOrder = executeOrder;
    window.updateOrderPreview = updateOrderPreview;
    window.changeChartPeriod = changeChartPeriod;
    window.switchPortfolioView = switchPortfolioView;
    window.showStockDetails = showStockDetails;
    window.openOrderFromDetails = openOrderFromDetails;
    window.showNewsDetails = showNewsDetails;
    window.showStartMenu = showStartMenu;

    // Add search functionality
    const portfolioSearch = document.getElementById('portfolioSearch') as HTMLInputElement;
    if (portfolioSearch) {
      portfolioSearch.addEventListener('input', (e: Event) => {
        const target = e.target as HTMLInputElement;
        if (target) {
          const searchTerm = target.value.toLowerCase();
          switchPortfolioView(currentView || 'all', searchTerm);
        }
      });
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', (e: KeyboardEvent) => {
      if (e.ctrlKey) {
        switch(e.key) {
          case 'o':
            e.preventDefault();
            const orderDialog = document.getElementById('orderDialog');
            if (orderDialog) orderDialog.style.display = 'block';
            break;
          case 'p':
            e.preventDefault();
            const portfolioWindow = document.getElementById('portfolioWindow');
            if (portfolioWindow) portfolioWindow.style.display = 'block';
            break;
          case 'c':
            e.preventDefault();
            const chartWindow = document.getElementById('chartWindow');
            if (chartWindow) chartWindow.style.display = 'block';
            break;
        }
      }
    });

  }, []);

  return (
    <div className="xp-trading-platform">
      <style dangerouslySetInnerHTML={{ __html: `
        @import url('https://fonts.googleapis.com/css2?family=Tahoma:wght@400;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Tahoma', sans-serif;
            font-size: 11px;
        }

        body {
            background: linear-gradient(135deg, #235bd4 0%, #4b8df8 25%, #8db5f2 75%, #a8c8f5 100%);
            background-attachment: fixed;
            min-height: 100vh;
            cursor: default;
            overflow: hidden;
        }

        /* XP Window Base */
        .xp-window {
            position: absolute;
            background: #ece9d8;
            border: 2px outset #ece9d8;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
            min-width: 200px;
            min-height: 100px;
        }

        .xp-titlebar {
            height: 25px;
            background: linear-gradient(to bottom, #0054e3 0%, #0054e3 3%, #4e8cde 6%, #1c5dc7 10%, #0054e3 14%, #0054e3 86%, #1c5dc7 90%, #4e8cde 94%, #0054e3 97%, #0054e3 100%);
            color: white;
            display: flex;
            align-items: center;
            padding: 0 5px;
            cursor: move;
            user-select: none;
        }

        .xp-titlebar.inactive {
            background: linear-gradient(to bottom, #7a7a7a 0%, #a8a8a8 50%, #7a7a7a 100%);
        }

        .xp-titlebar-text {
            flex: 1;
            font-weight: bold;
            font-size: 11px;
            margin-left: 5px;
        }

        .xp-titlebar-buttons {
            display: flex;
            gap: 2px;
        }

        .xp-titlebar-button {
            width: 16px;
            height: 14px;
            background: linear-gradient(to bottom, #ffffff 0%, #ddd 50%, #bbb 100%);
            border: 1px outset #ddd;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 8px;
            font-weight: bold;
        }

        .xp-titlebar-button:hover {
            background: linear-gradient(to bottom, #f0f0f0 0%, #e0e0e0 50%, #d0d0d0 100%);
        }

        .xp-titlebar-button:active {
            border: 1px inset #ddd;
        }

        .xp-window-content {
            padding: 8px;
            background: #ece9d8;
            height: calc(100% - 25px);
            overflow: auto;
        }

        /* XP Buttons */
        .xp-button {
            background: linear-gradient(to bottom, #ffffff 0%, #ece9d8 50%, #d7d3c8 100%);
            border: 1px outset #ece9d8;
            padding: 4px 8px;
            cursor: pointer;
            font-family: 'Tahoma', sans-serif;
            font-size: 11px;
            user-select: none;
        }

        .xp-button:hover {
            background: linear-gradient(to bottom, #f8f8f8 0%, #e8e5d8 50%, #d0ccc0 100%);
        }

        .xp-button:active {
            border: 1px inset #ece9d8;
            background: linear-gradient(to bottom, #d7d3c8 0%, #ece9d8 50%, #ffffff 100%);
        }

        .xp-button.start-style {
            background: linear-gradient(to bottom, #4caf50 0%, #45a049 50%, #3d8b40 100%);
            color: white;
            font-weight: bold;
            padding: 6px 12px;
        }

        .xp-button.sell-style {
            background: linear-gradient(to bottom, #f44336 0%, #da190b 50%, #b71c1c 100%);
            color: white;
            font-weight: bold;
            padding: 6px 12px;
        }

        /* XP Input Fields */
        .xp-input {
            border: 2px inset #ece9d8;
            padding: 2px 4px;
            background: white;
            font-family: 'Tahoma', sans-serif;
            font-size: 11px;
        }

        .xp-input:focus {
            outline: none;
            background: #e6f3ff;
        }

        /* XP List View */
        .xp-listview {
            border: 2px inset #ece9d8;
            background: white;
            height: 200px;
            overflow: auto;
        }

        .xp-listview-header {
            background: linear-gradient(to bottom, #ffffff 0%, #ece9d8 100%);
            border-bottom: 1px solid #999;
            display: flex;
            font-weight: bold;
            height: 20px;
            align-items: center;
        }

        .xp-listview-column {
            padding: 2px 8px;
            border-right: 1px solid #999;
            flex: 1;
            cursor: pointer;
        }

        .xp-listview-column:hover {
            background: #f0f0f0;
        }

        .xp-listview-row {
            display: flex;
            border-bottom: 1px solid #eee;
            height: 18px;
            align-items: center;
            cursor: pointer;
        }

        .xp-listview-row:hover {
            background: #e6f3ff;
        }

        .xp-listview-row.selected {
            background: #316ac5;
            color: white;
        }

        .xp-listview-cell {
            padding: 2px 8px;
            border-right: 1px solid #eee;
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* XP Status Bar */
        .xp-statusbar {
            height: 20px;
            background: linear-gradient(to bottom, #ece9d8 0%, #d7d3c8 100%);
            border-top: 1px solid #999;
            display: flex;
            align-items: center;
            padding: 0 8px;
            font-size: 11px;
        }

        /* XP Progress Bar */
        .xp-progress {
            width: 100%;
            height: 20px;
            border: 2px inset #ece9d8;
            background: white;
            position: relative;
            overflow: hidden;
        }

        .xp-progress-bar {
            height: 100%;
            background: linear-gradient(to right, #0054e3 0%, #4e8cde 50%, #0054e3 100%);
            transition: width 0.3s ease;
            position: relative;
        }

        .xp-progress-bar::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, rgba(255,255,255,0.3) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.3) 50%, rgba(255,255,255,0.3) 75%, transparent 75%);
            background-size: 20px 20px;
            animation: progress-stripes 1s linear infinite;
        }

        @keyframes progress-stripes {
            0% { background-position: 0 0; }
            100% { background-position: 20px 0; }
        }

        /* XP Tree View */
        .xp-treeview {
            border: 2px inset #ece9d8;
            background: white;
            height: 300px;
            overflow: auto;
            font-size: 11px;
        }

        .xp-tree-item {
            padding: 2px 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .xp-tree-item:hover {
            background: #e6f3ff;
        }

        .xp-tree-item.selected {
            background: #316ac5;
            color: white;
        }

        .xp-tree-icon {
            width: 16px;
            height: 16px;
            background: #ffd700;
            border: 1px solid #999;
            display: inline-block;
        }

        /* Layout */
        .desktop {
            width: 100vw;
            height: 100vh;
            position: relative;
        }

        .taskbar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 30px;
            background: linear-gradient(to bottom, #245edb 0%, #1941a5 50%, #1941a5 100%);
            border-top: 1px solid #4b8df8;
            display: flex;
            align-items: center;
            padding: 0 4px;
            z-index: 1000;
        }

        .start-button {
            height: 24px;
            background: linear-gradient(to bottom, #4caf50 0%, #45a049 50%, #3d8b40 100%);
            color: white;
            border: 1px outset #4caf50;
            padding: 0 8px;
            cursor: pointer;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 11px;
        }

        .start-button:hover {
            background: linear-gradient(to bottom, #5cbf60 0%, #4fb54e 50%, #43a047 100%);
        }

        .ticker {
            flex: 1;
            margin: 0 10px;
            background: rgba(0,0,0,0.2);
            color: white;
            padding: 4px 8px;
            border: 1px inset #1941a5;
            overflow: hidden;
            white-space: nowrap;
        }

        .ticker-content {
            animation: scroll-left 30s linear infinite;
        }

        @keyframes scroll-left {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }

        .system-tray {
            display: flex;
            gap: 4px;
            align-items: center;
            color: white;
            font-size: 10px;
        }

        /* Dialog specific styles */
        .order-dialog {
            width: 400px;
            height: 300px;
            top: 20%;
            left: 30%;
        }

        .portfolio-window {
            width: 600px;
            height: 400px;
            top: 10%;
            left: 20%;
        }

        .chart-window {
            width: 500px;
            height: 350px;
            top: 15%;
            left: 40%;
        }

        .watchlist-window {
            width: 300px;
            height: 250px;
            top: 25%;
            left: 60%;
        }

        .news-window {
            width: 450px;
            height: 200px;
            top: 45%;
            left: 10%;
        }

        /* Chart placeholder */
        .chart-placeholder {
            width: 100%;
            height: 200px;
            background: linear-gradient(45deg, #f0f0f0 25%, transparent 25%, transparent 75%, #f0f0f0 75%), linear-gradient(45deg, #f0f0f0 25%, transparent 25%, transparent 75%, #f0f0f0 75%);
            background-size: 20px 20px;
            background-position: 0 0, 10px 10px;
            border: 2px inset #ece9d8;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            font-style: italic;
        }

        /* Tooltip */
        .xp-tooltip {
            position: absolute;
            background: #ffffcc;
            border: 1px solid #000;
            padding: 4px 8px;
            font-size: 11px;
            z-index: 1001;
            pointer-events: none;
            box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        /* Loading screen */
        .loading-screen {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: #ece9d8;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 2000;
        }

        .loading-logo {
            font-size: 24px;
            font-weight: bold;
            color: #0054e3;
            margin-bottom: 20px;
        }

        .loading-text {
            margin: 10px 0;
            color: #333;
        }

        /* Heat map */
        .heat-map {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 2px;
            margin: 10px 0;
        }

        .heat-cell {
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: bold;
            border: 1px solid #999;
        }

        .heat-cell.positive {
            background: linear-gradient(to bottom, #90ee90 0%, #32cd32 100%);
            color: #006400;
        }

        .heat-cell.negative {
            background: linear-gradient(to bottom, #ffb6c1 0%, #ff6b6b 100%);
            color: #8b0000;
        }

        .heat-cell.neutral {
            background: linear-gradient(to bottom, #f0f0f0 0%, #d0d0d0 100%);
            color: #666;
        }

        /* Form layouts */
        .form-row {
            display: flex;
            align-items: center;
            margin: 8px 0;
            gap: 8px;
        }

        .form-label {
            width: 80px;
            text-align: right;
        }

        .form-input {
            flex: 1;
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .xp-window {
                width: 90% !important;
                height: 70% !important;
                left: 5% !important;
                top: 10% !important;
            }
        }
      `}} />
      <div dangerouslySetInnerHTML={{ __html: `
        <div class="desktop" id="desktop">
            <!-- Loading Screen -->
            <div class="loading-screen" id="loadingScreen">
                <div class="loading-logo">🖥️ XP Trading Pro</div>
                <div class="loading-text">Starting Windows XP Trading Platform...</div>
                <div class="xp-progress" style="width: 300px; margin: 20px 0;">
                    <div class="xp-progress-bar" id="loadingProgress" style="width: 0%;"></div>
                </div>
                <div class="loading-text">Please wait...</div>
            </div>

            <!-- Portfolio Window -->
            <div class="xp-window portfolio-window" id="portfolioWindow">
                <div class="xp-titlebar">
                    <div class="xp-titlebar-text">📊 Portfolio Manager</div>
                    <div class="xp-titlebar-buttons">
                        <div class="xp-titlebar-button" onclick="minimizeWindow('portfolioWindow')">_</div>
                        <div class="xp-titlebar-button" onclick="maximizeWindow('portfolioWindow')">□</div>
                        <div class="xp-titlebar-button" onclick="closeWindow('portfolioWindow')">✕</div>
                    </div>
                </div>
                <div class="xp-window-content">
                    <div style="display: flex; gap: 8px; height: calc(100% - 25px);">
                        <div style="width: 150px;">
                            <div style="font-weight: bold; margin-bottom: 5px;">Portfolio Tree</div>
                            <div class="xp-treeview">
                                <div class="xp-tree-item selected" onclick="switchPortfolioView('all')">
                                    <span class="xp-tree-icon" style="background: #ffd700;">📁</span>
                                    My Portfolio
                                </div>
                                <div class="xp-tree-item" onclick="switchPortfolioView('stocks')">
                                    <span class="xp-tree-icon" style="background: #87ceeb;">📈</span>
                                    Stocks
                                </div>
                                <div class="xp-tree-item" onclick="switchPortfolioView('crypto')">
                                    <span class="xp-tree-icon" style="background: #98fb98;">💰</span>
                                    Crypto
                                </div>
                                <div class="xp-tree-item" onclick="switchPortfolioView('bonds')">
                                    <span class="xp-tree-icon" style="background: #dda0dd;">🏛️</span>
                                    Bonds
                                </div>
                                <div class="xp-tree-item" onclick="switchPortfolioView('watchlist')">
                                    <span class="xp-tree-icon" style="background: #f0e68c;">⭐</span>
                                    Watchlist
                                </div>
                            </div>
                        </div>
                        <div style="flex: 1;">
                            <input type="text" class="xp-input" id="portfolioSearch" placeholder="Search stocks..." style="width: 100%; margin-bottom: 8px;">
                            <div class="xp-listview" id="portfolioList">
                                <div class="xp-listview-header">
                                    <div class="xp-listview-column">Symbol</div>
                                    <div class="xp-listview-column">Shares</div>
                                    <div class="xp-listview-column">Price</div>
                                    <div class="xp-listview-column">Total Value</div>
                                    <div class="xp-listview-column">Gain/Loss</div>
                                </div>
                                <!-- More stocks added -->
                                <div class="xp-listview-row" onclick="showStockDetails('RELIANCE')">
                                    <div class="xp-listview-cell">RELIANCE</div>
                                    <div class="xp-listview-cell">100</div>
                                    <div class="xp-listview-cell">₹2,847.50</div>
                                    <div class="xp-listview-cell">₹2,84,750.00</div>
                                    <div class="xp-listview-cell" style="color: green;">+₹18,750.00</div>
                                </div>
                                <div class="xp-listview-row" onclick="showStockDetails('TCS')">
                                    <div class="xp-listview-cell">TCS</div>
                                    <div class="xp-listview-cell">50</div>
                                    <div class="xp-listview-cell">₹4,125.30</div>
                                    <div class="xp-listview-cell">₹2,06,265.00</div>
                                    <div class="xp-listview-cell" style="color: green;">+₹12,650.00</div>
                                </div>
                                <div class="xp-listview-row" onclick="showStockDetails('INFY')">
                                    <div class="xp-listview-cell">INFY</div>
                                    <div class="xp-listview-cell">75</div>
                                    <div class="xp-listview-cell">₹1,821.45</div>
                                    <div class="xp-listview-cell">₹1,36,608.75</div>
                                    <div class="xp-listview-cell" style="color: red;">-₹5,430.25</div>
                                </div>
                                <div class="xp-listview-row" onclick="showStockDetails('HDFCBANK')">
                                    <div class="xp-listview-cell">HDFCBANK</div>
                                    <div class="xp-listview-cell">40</div>
                                    <div class="xp-listview-cell">₹1,742.85</div>
                                    <div class="xp-listview-cell">₹69,714.00</div>
                                    <div class="xp-listview-cell" style="color: green;">+₹2,968.00</div>
                                </div>
                                <div class="xp-listview-row" onclick="showStockDetails('ITC')">
                                    <div class="xp-listview-cell">ITC</div>
                                    <div class="xp-listview-cell">200</div>
                                    <div class="xp-listview-cell">₹425.60</div>
                                    <div class="xp-listview-cell">₹85,120.00</div>
                                    <div class="xp-listview-cell" style="color: green;">+₹1,240.00</div>
                                </div>
                                <div class="xp-listview-row" onclick="showStockDetails('ICICIBANK')">
                                    <div class="xp-listview-cell">ICICIBANK</div>
                                    <div class="xp-listview-cell">80</div>
                                    <div class="xp-listview-cell">₹1,045.20</div>
                                    <div class="xp-listview-cell">₹83,616.00</div>
                                    <div class="xp-listview-cell" style="color: red;">-₹1,840.00</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="xp-statusbar">
                        Total Portfolio Value: ₹6,66,073.75 | Today's Change: +₹28,337.75 (+4.4%) | 6 positions
                    </div>
                </div>
            </div>

            <!-- Order Dialog -->
            <div class="xp-window order-dialog" id="orderDialog">
                <div class="xp-titlebar">
                    <div class="xp-titlebar-text">📋 Place Order</div>
                    <div class="xp-titlebar-buttons">
                        <div class="xp-titlebar-button" onclick="closeWindow('orderDialog')">✕</div>
                    </div>
                </div>
                <div class="xp-window-content">
                    <div class="form-row">
                        <label class="form-label">Symbol:</label>
                        <input type="text" class="xp-input form-input" id="orderSymbol" value="RELIANCE" placeholder="Enter NSE symbol">
                    </div>
                    <div class="form-row">
                        <label class="form-label">Quantity:</label>
                        <input type="number" class="xp-input form-input" id="orderQuantity" value="10" placeholder="Number of shares">
                    </div>
                    <div class="form-row">
                        <label class="form-label">Order Type:</label>
                        <select class="xp-input form-input" id="orderType">
                            <option>Market Order</option>
                            <option>Limit Order</option>
                            <option>Stop Loss</option>
                            <option>Cover Order</option>
                            <option>Bracket Order</option>
                        </select>
                    </div>
                    <div class="form-row">
                        <label class="form-label">Price:</label>
                        <input type="number" class="xp-input form-input" id="orderPrice" value="2847.50" step="0.05" placeholder="Price per share in INR">
                    </div>
                    <div class="form-row" style="margin-top: 20px; justify-content: center; gap: 20px;">
                        <button class="xp-button start-style" onclick="showConfirmation('BUY')">
                            💰 BUY ORDER
                        </button>
                        <button class="xp-button sell-style" onclick="showConfirmation('SELL')">
                            💸 SELL ORDER
                        </button>
                    </div>
                    <div class="form-row" style="margin-top: 15px;">
                        <div style="background: #f0f0f0; padding: 8px; border: 1px inset #ece9d8; width: 100%;">
                            <strong>Order Preview:</strong><br>
                            <span id="orderPreview">Buy 10 shares of RELIANCE at ₹2847.50<br>
                            <strong>Total Cost: ₹28,475.00</strong></span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Chart Window -->
            <div class="xp-window chart-window" id="chartWindow">
                <div class="xp-titlebar">
                    <div class="xp-titlebar-text" id="chartTitle">📈 Stock Chart - RELIANCE</div>
                    <div class="xp-titlebar-buttons">
                        <div class="xp-titlebar-button" onclick="minimizeWindow('chartWindow')">_</div>
                        <div class="xp-titlebar-button" onclick="maximizeWindow('chartWindow')">□</div>
                        <div class="xp-titlebar-button" onclick="closeWindow('chartWindow')">✕</div>
                    </div>
                </div>
                <div class="xp-window-content">
                    <div style="display: flex; gap: 5px; margin-bottom: 10px;">
                        <button class="xp-button" onclick="changeChartPeriod('1D')">1D</button>
                        <button class="xp-button" onclick="changeChartPeriod('5D')">5D</button>
                        <button class="xp-button" style="background: #316ac5; color: white;" onclick="changeChartPeriod('1M')">1M</button>
                        <button class="xp-button" onclick="changeChartPeriod('3M')">3M</button>
                        <button class="xp-button" onclick="changeChartPeriod('1Y')">1Y</button>
                        <button class="xp-button" onclick="changeChartPeriod('5Y')">5Y</button>
                    </div>
                    <div class="chart-placeholder">
                        📊 Interactive Chart Loading...<br>
                        <small id="chartInfo">RELIANCE: ₹2,847.50 (+1.6%) Volume: 2.5Cr</small>
                    </div>
                    <div style="margin-top: 10px;">
                        <strong>Technical Indicators:</strong>
                        <div id="technicalIndicators" style="display: flex; gap: 15px; margin-top: 5px; font-size: 10px;">
                            <span>RSI: 62.4</span>
                            <span>MACD: 1.23</span>
                            <span>MA(50): ₹2,889.92</span>
                            <span>MA(200): ₹2,781.45</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Watchlist Window -->
            <div class="xp-window watchlist-window" id="watchlistWindow">
                <div class="xp-titlebar">
                    <div class="xp-titlebar-text">⭐ Market Watchlist</div>
                    <div class="xp-titlebar-buttons">
                        <div class="xp-titlebar-button" onclick="minimizeWindow('watchlistWindow')">_</div>
                        <div class="xp-titlebar-button" onclick="closeWindow('watchlistWindow')">✕</div>
                    </div>
                </div>
                <div class="xp-window-content">
                    <div class="xp-listview" style="height: 150px;">
                        <div class="xp-listview-header">
                            <div class="xp-listview-column">Symbol</div>
                            <div class="xp-listview-column">Price</div>
                            <div class="xp-listview-column">Change</div>
                        </div>
                        <div class="xp-listview-row" onclick="showStockDetails('RELIANCE')">
                            <div class="xp-listview-cell">RELIANCE</div>
                            <div class="xp-listview-cell">₹2,847.50</div>
                            <div class="xp-listview-cell" style="color: green;">+₹45.20</div>
                        </div>
                        <div class="xp-listview-row" onclick="showStockDetails('TCS')">
                            <div class="xp-listview-cell">TCS</div>
                            <div class="xp-listview-cell">₹4,125.30</div>
                            <div class="xp-listview-cell" style="color: green;">+₹87.50</div>
                        </div>
                        <div class="xp-listview-row" onclick="showStockDetails('INFY')">
                            <div class="xp-listview-cell">INFY</div>
                            <div class="xp-listview-cell">₹1,821.45</div>
                            <div class="xp-listview-cell" style="color: red;">-₹21.40</div>
                        </div>
                        <div class="xp-listview-row" onclick="showStockDetails('HDFCBANK')">
                            <div class="xp-listview-cell">HDFCBANK</div>
                            <div class="xp-listview-cell">₹1,742.85</div>
                            <div class="xp-listview-cell" style="color: green;">+₹31.50</div>
                        </div>
                        <div class="xp-listview-row" onclick="showStockDetails('ITC')">
                            <div class="xp-listview-cell">ITC</div>
                            <div class="xp-listview-cell">₹425.60</div>
                            <div class="xp-listview-cell" style="color: green;">+₹8.50</div>
                        </div>
                        <div class="xp-listview-row" onclick="showStockDetails('ICICIBANK')">
                            <div class="xp-listview-cell">ICICIBANK</div>
                            <div class="xp-listview-cell">₹1,045.20</div>
                            <div class="xp-listview-cell" style="color: red;">-₹15.80</div>
                        </div>
                        <div class="xp-listview-row" onclick="showStockDetails('SBIN')">
                            <div class="xp-listview-cell">SBIN</div>
                            <div class="xp-listview-cell">₹652.40</div>
                            <div class="xp-listview-cell" style="color: green;">+₹12.30</div>
                        </div>
                        <div class="xp-listview-row" onclick="showStockDetails('BHARTIARTL')">
                            <div class="xp-listview-cell">BHARTIARTL</div>
                            <div class="xp-listview-cell">₹1,025.75</div>
                            <div class="xp-listview-cell" style="color: green;">+₹18.90</div>
                        </div>
                    </div>
                    <div style="margin-top: 10px;">
                        <div style="font-weight: bold; margin-bottom: 5px;">Market Heat Map:</div>
                        <div class="heat-map">
                            <div class="heat-cell positive">RELIANCE<br>+1.6%</div>
                            <div class="heat-cell positive">TCS<br>+2.2%</div>
                            <div class="heat-cell negative">INFY<br>-1.2%</div>
                            <div class="heat-cell positive">HDFCBANK<br>+1.8%</div>
                            <div class="heat-cell neutral">ITC<br>+0.1%</div>
                            <div class="heat-cell positive">ICICIBANK<br>+1.5%</div>
                            <div class="heat-cell negative">SBIN<br>-0.8%</div>
                            <div class="heat-cell positive">BHARTIARTL<br>+2.1%</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- News Window -->
            <div class="xp-window news-window" id="newsWindow">
                <div class="xp-titlebar">
                    <div class="xp-titlebar-text">📰 Market News</div>
                    <div class="xp-titlebar-buttons">
                        <div class="xp-titlebar-button" onclick="minimizeWindow('newsWindow')">_</div>
                        <div class="xp-titlebar-button" onclick="closeWindow('newsWindow')">✕</div>
                    </div>
                </div>
                <div class="xp-window-content">
                    <div class="xp-listview" style="height: 120px;">
                        <div class="xp-listview-row" onclick="showNewsDetails(0)">
                            <div class="xp-listview-cell">📈 Reliance Industries Q3 Results Beat Estimates</div>
                        </div>
                        <div class="xp-listview-row" onclick="showNewsDetails(1)">
                            <div class="xp-listview-cell">🏢 TCS Digital Transformation Revenue Grows 25%</div>
                        </div>
                        <div class="xp-listview-row" onclick="showNewsDetails(2)">
                            <div class="xp-listview-cell">🏦 HDFC Bank Announces Merger Completion</div>
                        </div>
                        <div class="xp-listview-row" onclick="showNewsDetails(3)">
                            <div class="xp-listview-cell">💎 Infosys AI & Cloud Services Demand Rises</div>
                        </div>
                        <div class="xp-listview-row" onclick="showNewsDetails(4)">
                            <div class="xp-listview-cell">📱 Bharti Airtel 5G Rollout Accelerates</div>
                        </div>
                        <div class="xp-listview-row" onclick="showNewsDetails(5)">
                            <div class="xp-listview-cell">🚀 Adani Ports Q2 Revenue Soars 18%</div>
                        </div>
                        <div class="xp-listview-row" onclick="showNewsDetails(6)">
                            <div class="xp-listview-cell">💼 Wipro Launches New AI Initiative</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Taskbar -->
            <div class="taskbar">
                <div class="start-button" onclick="showStartMenu()">
                    🖥️ Start
                </div>
                <div class="ticker">
                    <div class="ticker-content">
                        📈 NIFTY 50: 24,467 (+0.8%) | SENSEX: 80,845 (+1.2%) | BANK NIFTY: 51,234 (+1.5%) | 🏦 10Y Bond: 6.85% | 💰 Gold: ₹72,450/10g | 🛢️ Crude: ₹6,245/bbl | 💱 USD/INR: 84.52
                    </div>
                </div>
                <div class="system-tray">
                    <span>💹</span>
                    <span>🔊</span>
                    <span>📶</span>
                    <span id="clock">12:34 PM</span>
                </div>
            </div>

            <!-- Tooltip -->
            <div class="xp-tooltip" id="tooltip" style="display: none;"></div>

            <!-- Confirmation Dialog -->
            <div class="xp-window" id="confirmDialog" style="width: 350px; height: 180px; top: 35%; left: 35%; display: none;">
                <div class="xp-titlebar">
                    <div class="xp-titlebar-text">⚠️ Confirm Order</div>
                    <div class="xp-titlebar-buttons">
                        <div class="xp-titlebar-button" onclick="closeWindow('confirmDialog')">✕</div>
                    </div>
                </div>
                <div class="xp-window-content">
                    <div style="display: flex; align-items: center; gap: 10px; margin: 20px 0;">
                        <div style="font-size: 32px;">⚠️</div>
                        <div id="confirmMessage">Are you sure you want to place this BUY order?</div>
                    </div>
                    <div style="display: flex; justify-content: center; gap: 20px;">
                        <button class="xp-button start-style" onclick="executeOrder()">Yes</button>
                        <button class="xp-button sell-style" onclick="closeWindow('confirmDialog')">No</button>
                    </div>
                </div>
            </div>

            <!-- Start Menu -->
            <div class="xp-window" id="startMenu" style="width: 300px; height: 400px; position: fixed; bottom: 30px; left: 0; display: none;">
                <div class="xp-window-content" style="background: linear-gradient(to right, #4e8cde 0%, #0054e3 100%); color: white;">
                    <div style="background: #fff; color: #000; height: 100%;">
                        <div style="padding: 10px;">
                            <h3 style="font-size: 14px; font-weight: bold;">Trading Tools</h3>
                            <button class="xp-button" style="width: 100%; text-align: left; margin: 5px 0;" onclick="document.getElementById('portfolioWindow').style.display = 'block'; showStartMenu()">📊 Portfolio</button>
                            <button class="xp-button" style="width: 100%; text-align: left; margin: 5px 0;" onclick="document.getElementById('orderDialog').style.display = 'block'; showStartMenu()">📋 Place Order</button>
                            <button class="xp-button" style="width: 100%; text-align: left; margin: 5px 0;" onclick="document.getElementById('chartWindow').style.display = 'block'; showStartMenu()">📈 Charts</button>
                            <button class="xp-button" style="width: 100%; text-align: left; margin: 5px 0;" onclick="document.getElementById('watchlistWindow').style.display = 'block'; showStartMenu()">⭐ Watchlist</button>
                            <button class="xp-button" style="width: 100%; text-align: left; margin: 5px 0;" onclick="document.getElementById('newsWindow').style.display = 'block'; showStartMenu()">📰 News</button>
                            <button class="xp-button" style="width: 100%; text-align: left; margin: 5px 0;" onclick="showNewsDetails(0); showStartMenu()">📝 Reports</button>
                            <h3 style="font-size: 14px; font-weight: bold; margin-top: 20px;">System</h3>
                            <button class="xp-button" style="width: 100%; text-align: left; margin: 5px 0;" onclick="location.reload(); showStartMenu()">🔄 Restart</button>
                            <button class="xp-button" style="width: 100%; text-align: left; margin: 5px 0;" onclick="alert('System shutdown'); showStartMenu()">⏻ Shutdown</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Stock Details Dialog -->
            <div class="xp-window" id="stockDetails" style="width: 400px; height: 300px; top: 20%; left: 30%; display: none;">
                <div class="xp-titlebar">
                    <div class="xp-titlebar-text" id="detailsTitle">📈 Stock Details - RELIANCE</div>
                    <div class="xp-titlebar-buttons">
                        <div class="xp-titlebar-button" onclick="closeWindow('stockDetails')">✕</div>
                    </div>
                </div>
                <div class="xp-window-content">
                    <div class="form-row">
                        <label class="form-label">Symbol:</label>
                        <span id="detailsSymbol">RELIANCE</span>
                    </div>
                    <div class="form-row">
                        <label class="form-label">Price:</label>
                        <span id="detailsPrice">₹2,847.50</span>
                    </div>
                    <div class="form-row">
                        <label class="form-label">P/E Ratio:</label>
                        <span id="detailsPE">25.4</span>
                    </div>
                    <div class="form-row">
                        <label class="form-label">Market Cap:</label>
                        <span id="detailsMarketCap">₹19.2 lakh Cr</span>
                    </div>
                    <div class="form-row">
                        <label class="form-label">52W High/Low:</label>
                        <span id="detailsHighLow">₹3,025 / ₹2,221</span>
                    </div>
                    <div class="form-row" style="margin-top: 20px; justify-content: center;">
                        <button class="xp-button start-style" onclick="openOrderFromDetails()">💰 Buy</button>
                    </div>
                </div>
            </div>

            <!-- News Details Dialog -->
            <div class="xp-window" id="newsDetails" style="width: 450px; height: 250px; top: 25%; left: 25%; display: none;">
                <div class="xp-titlebar">
                    <div class="xp-titlebar-text">📰 News Article</div>
                    <div class="xp-titlebar-buttons">
                        <div class="xp-titlebar-button" onclick="closeWindow('newsDetails')">✕</div>
                    </div>
                </div>
                <div class="xp-window-content">
                    <div style="font-weight: bold; font-size: 12px; margin-bottom: 10px;" id="newsTitle">Reliance Industries Q3 Results</div>
                    <p style="font-size: 11px; line-height: 1.4;">
                        Reliance Industries reported strong Q3 results with revenue growth of 15% YoY, driven by robust performance in retail and telecom sectors. Jio added 12 million subscribers, while retail segment saw 25% revenue increase. EBIT margins improved to 18.5%.
                    </p>
                    <div style="margin-top: 15px; text-align: right;">
                        <button class="xp-button" onclick="closeWindow('newsDetails')">Close</button>
                    </div>
                </div>
            </div>

            <!-- Tooltip -->
            <div class="xp-tooltip" id="tooltip" style="display: none;"></div>
        </div>
      `}} />
    </div>
  );
}
