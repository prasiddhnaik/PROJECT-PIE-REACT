import './globals.css';

import CryptoDashboard from '../components/CryptoDashboard';

export default function Home() {
  return (
    <div className="desktop">
      <div className="xp-window portfolio-window" id="portfolioWindow">
        <div className="xp-titlebar">
          <div className="xp-titlebar-text">📊 Crypto Dashboard</div>
          <div className="xp-titlebar-buttons">
            <div className="xp-titlebar-button">_</div>
            <div className="xp-titlebar-button">□</div>
            <div className="xp-titlebar-button">✕</div>
          </div>
        </div>
        <div className="xp-window-content">
          <CryptoDashboard />
        </div>
      </div>
      {/* Add taskbar */}
      <div className="taskbar">
        <div className="start-button">🖥️ Start</div>
        <div className="ticker">
          <div className="ticker-content">📈 Loading market data...</div>
        </div>
        <div className="system-tray">
          <span>💹</span>
          <span>🔊</span>
          <span>📶</span>
          <span id="clock">12:00 PM</span>
        </div>
      </div>
    </div>
  );
}
