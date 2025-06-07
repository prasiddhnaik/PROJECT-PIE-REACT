# 🚀 Enhanced Stock Tracker Setup Guide

## 📊 **Reliance Industries Live Price Tracker with SMA & Email Alerts**

This advanced stock tracker monitors Reliance Industries (RELIANCE.NS) stock prices in real-time, calculates technical indicators, generates buy/sell signals, and sends email alerts.

---

## 🎯 **Features**

### **📈 Technical Analysis:**
- **Real-time price tracking** (1-minute intervals)
- **5-minute Simple Moving Average (SMA)** calculation
- **RSI (Relative Strength Index)** for momentum analysis
- **Volume analysis** with average comparison
- **Buy/Sell signal generation** based on multiple indicators

### **📧 Email Alerts:**
- **Automated email notifications** for trading signals
- **HTML formatted emails** with detailed analysis
- **Signal strength scoring** (1-5 scale)
- **Risk management warnings**
- **5-minute cooldown** to prevent spam

### **📊 Data Management:**
- **Historical data storage** in JSON format
- **Comprehensive logging** with timestamps
- **Visual charts** with technical indicators
- **Session persistence** across runs

### **⚠️ Risk Management:**
- **Multiple indicator confirmation** before signals
- **Volume confirmation** for signal strength
- **Automatic risk warnings** in emails
- **Signal strength scoring** for confidence

---

## 🛠️ **Setup Instructions**

### **Step 1: Install Required Packages**

```bash
# Install packages using pip
pip install -r requirements_stock_tracker.txt

# Or install manually:
pip install yfinance pandas numpy matplotlib seaborn plotly dash
```

### **Step 2: Gmail App Password Setup (for Email Alerts)**

**For Gmail users (recommended):**

1. **Enable 2-Step Verification:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable "2-Step Verification" if not already enabled

2. **Create App Password:**
   - In Security settings, find "App passwords"
   - Select "Mail" and "Other" (custom name)
   - Enter "Stock Tracker" as the name
   - Copy the 16-character password generated

3. **Use App Password:**
   - Use your regular Gmail address as sender
   - Use the **App Password** (not your regular password) when prompted

### **Step 3: Run the Tracker**

```bash
# Navigate to the directory containing the file
cd /path/to/your/directory

# Run the tracker
python enhanced_stock_tracker.py
```

---

## 🖥️ **Usage Guide**

### **When you run the script, you'll be prompted for:**

1. **Sender Email**: Your Gmail address
2. **Email Password**: Your Gmail App Password (16 characters)
3. **Recipient Email**: Where to send alerts (can be same as sender)
4. **Duration**: How long to run (in minutes, default: 60)

### **Example Configuration:**
```
Enter your email address: your.email@gmail.com
Enter your email password/app password: abcdwxyzefgh1234
Enter recipient email address: your.email@gmail.com
Enter tracking duration in minutes (default 60): 120
```

---

## 📊 **How It Works**

### **Signal Generation Logic:**

#### **BUY Signals (Score ≥ +2):**
- Price **above** 5-minute SMA (+1)
- RSI **below 30** (oversold) (+2)
- High volume (>1.5x average) (+1)

#### **SELL Signals (Score ≤ -2):**
- Price **below** 5-minute SMA (-1)
- RSI **above 70** (overbought) (-2)
- High volume (>1.5x average) (-1)

#### **HOLD Signals (-1 to +1):**
- Mixed or weak indicators
- No clear directional bias

### **Email Alert Triggers:**
- Only **BUY** and **SELL** signals trigger emails
- **5-minute cooldown** between emails
- No duplicate signals (won't repeat same signal type)

---

## 📁 **Output Files**

The tracker generates several files:

1. **`tracking_data.json`** - Historical signals and data
2. **`stock_tracker_YYYY-MM-DD.log`** - Detailed activity log
3. **`reliance_analysis_YYYY-MM-DD.png`** - Technical analysis chart

### **Chart Contents:**
- **Top Panel**: Price and SMA with buy/sell markers
- **Middle Panel**: RSI with overbought/oversold levels
- **Bottom Panel**: Volume ratio vs average

---

## 📧 **Email Alert Format**

### **Email Subject:**
```
🚨 BUY Signal: Reliance at ₹2,456.75
```

### **Email Content Includes:**
- **Signal Details**: Type, strength, timestamp
- **Price Information**: Current price, change %, SMA, high/low
- **Technical Indicators**: RSI, volume ratio, volume
- **Signal Reasoning**: Why the signal was generated
- **Risk Management**: Important disclaimers and warnings

---

## ⚙️ **Configuration Options**

### **Modify these variables in the code:**

```python
# In EnhancedStockTracker.__init__()
self.stock_symbol = "RELIANCE.NS"     # Stock to track
self.sma_period = 5                   # SMA period in minutes
self.volume_threshold = 1.5           # Volume spike threshold
self.price_change_threshold = 0.5     # Price change alert %
self.rsi_period = 14                  # RSI calculation period
```

### **Other Stocks You Can Track:**
```python
# Popular Indian stocks on NSE
"TCS.NS"        # Tata Consultancy Services
"INFY.NS"       # Infosys
"HDFCBANK.NS"   # HDFC Bank
"ICICIBANK.NS"  # ICICI Bank
"SBIN.NS"       # State Bank of India
"ITC.NS"        # ITC Limited
"LT.NS"         # Larsen & Toubro
"ONGC.NS"       # Oil & Natural Gas Corp
```

---

## 🚀 **Advanced Features**

### **Running in Background:**
```bash
# Run in background (Linux/Mac)
nohup python enhanced_stock_tracker.py &

# Check if running
ps aux | grep enhanced_stock_tracker
```

### **Scheduling with Cron:**
```bash
# Edit crontab
crontab -e

# Run every weekday at 9:30 AM (market open)
30 9 * * 1-5 cd /path/to/tracker && python enhanced_stock_tracker.py
```

### **Multiple Stock Tracking:**
- Modify the script to track multiple stocks
- Create separate instances for different stocks
- Use different email subjects for identification

---

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **"Authentication failed" error:**
- ✅ Use **App Password**, not regular password
- ✅ Enable 2-Step Verification first
- ✅ Check email address is correct

#### **"No data available" error:**
- ✅ Check if markets are open (NSE: 9:15 AM - 3:30 PM IST)
- ✅ Verify internet connection
- ✅ Check if stock symbol is correct

#### **"Permission denied" when saving files:**
- ✅ Run from a directory you have write permissions
- ✅ Check disk space availability

#### **Email not received:**
- ✅ Check spam/junk folder
- ✅ Verify recipient email address
- ✅ Ensure 5-minute cooldown has passed

### **Debug Mode:**
Add this to see more detailed output:
```python
# Add at the top of the script
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📈 **Sample Output**

```
🚀 Enhanced Stock Tracker Initialized
📊 Tracking: RELIANCE.NS
📈 SMA Period: 5 minutes
📧 Email alerts enabled for: your.email@gmail.com

🚀 Starting Enhanced Stock Tracker
⏰ Running for 60 minutes
📊 Monitoring RELIANCE.NS every minute
--------------------------------------------------

📊 Update #1 - 09:31:25
💰 Price: ₹2,456.75 (+0.32%)
📈 5-min SMA: ₹2,454.20
📊 RSI: 65.4
📦 Volume: 125,430 (1.2x avg)
🟡 Signal: HOLD (Strength: 0)
💡 Reasons: Price above SMA

📊 Update #2 - 09:32:25
💰 Price: ₹2,458.90 (+0.41%)
📈 5-min SMA: ₹2,455.80
📊 RSI: 28.7
📦 Volume: 245,670 (1.8x avg)
🟢 Signal: BUY (Strength: 3)
💡 Reasons: Price above SMA, Oversold (RSI: 28.7), High volume (1.8x avg)
📧 Email alert sent: BUY signal
```

---

## ⚠️ **Important Disclaimers**

### **Risk Warnings:**
- **This is for educational purposes only**
- **Not financial advice** - always do your own research
- **Test thoroughly** before using real money
- **Use proper risk management** (stop-loss, position sizing)
- **Markets can be unpredictable** - no system is 100% accurate

### **Technical Limitations:**
- **Data delays** may occur during high volatility
- **Internet connectivity** required for real-time data
- **Market hours only** - no data outside trading hours
- **Single stock focus** - diversification recommended

---

## 🎯 **Next Steps**

### **Enhancements You Can Make:**
1. **Multiple timeframes** (15-min, 1-hour SMA)
2. **Additional indicators** (MACD, Bollinger Bands)
3. **Portfolio tracking** (multiple stocks)
4. **Web dashboard** using Dash/Streamlit
5. **Database storage** instead of JSON
6. **Telegram/WhatsApp alerts** in addition to email
7. **Backtesting functionality** for strategy validation

### **Integration with Your Financial Hub:**
- Add this tracker to your existing dashboard
- Use the same email system for consistency
- Combine with portfolio analytics
- Create unified reporting

---

## 📞 **Support**

If you encounter issues:
1. Check the log file for detailed error messages
2. Verify all requirements are installed correctly
3. Test email configuration separately
4. Ensure markets are open during testing

**Happy Trading! 📈💰** 