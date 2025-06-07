# 🚀 Quick Start Guide - Enhanced Stock Tracker

## ✅ **Setup Complete!**

Your Enhanced Stock Tracker is ready to use! Here's what you have:

### 📁 **Files Created:**
- `enhanced_stock_tracker.py` - Full tracker with email alerts
- `demo_stock_tracker.py` - Demo with simulated data (just ran successfully!)
- `test_stock_tracker.py` - Basic connection test
- `requirements_stock_tracker.txt` - Package dependencies
- `STOCK_TRACKER_GUIDE.md` - Complete documentation

---

## 🎯 **How to Run (2 Simple Steps)**

### **Step 1: Get Gmail App Password**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable "2-Step Verification" (if not already enabled)
3. Go to "App passwords" section
4. Create new app password:
   - Select "Mail"
   - Select "Other" and enter "Stock Tracker"
   - Copy the 16-character password (like: `abcd efgh ijkl mnop`)

### **Step 2: Run the Tracker**
```bash
python3 enhanced_stock_tracker.py
```

**You'll be prompted for:**
- Email address (pre-filled: `prasiddhnaik40@gmail.com`) - just press Enter
- App Password (paste the 16-character password from Step 1)
- Recipient email (just press Enter to use same email)
- Duration in minutes (default: 60 minutes)

---

## 🎉 **Demo Results**

✅ **Just ran successfully with simulated data:**
- Tracked Reliance stock price (₹2,434 → ₹2,460)
- Calculated 5-minute SMA
- Generated 1 BUY signal
- Simulated email alert to: `prasiddhnaik40@gmail.com`

---

## 📊 **What You'll Get**

### **Real-time Tracking:**
- ✅ Reliance stock price every minute
- ✅ 5-minute Simple Moving Average
- ✅ RSI technical indicator
- ✅ Volume analysis

### **Trading Signals:**
- 🟢 **BUY** when: Price > SMA + Oversold (RSI < 30) + High Volume
- 🔴 **SELL** when: Price < SMA + Overbought (RSI > 70) + High Volume
- 🟡 **HOLD** for mixed signals

### **Email Alerts:**
- 📧 HTML-formatted emails with detailed analysis
- 🎯 Only for BUY/SELL signals (no spam)
- ⏰ 5-minute cooldown between alerts
- 📊 Complete price and technical data

---

## 🔧 **If Real Data Fails**

If you get "no data available" errors:

### **Option 1: Try Different Times**
- Markets open: 9:15 AM - 3:30 PM IST
- Best results during market hours

### **Option 2: Change Stock Symbol**
Edit `enhanced_stock_tracker.py` line 37:
```python
self.stock_symbol = "TCS.NS"    # Tata Consultancy
# or
self.stock_symbol = "INFY.NS"   # Infosys
# or  
self.stock_symbol = "HDFCBANK.NS"  # HDFC Bank
```

### **Option 3: Run Demo Mode**
```bash
python3 demo_stock_tracker.py
```

---

## 📱 **Sample Email Alert**

**Subject:** 🚨 BUY Signal: Reliance at ₹2,456.75

**Content:**
```
🟢 Trading Signal Alert - Reliance Industries

📊 Signal Details
Signal: BUY (Strength: 3/5)
Timestamp: 2024-01-15 10:30:25

💰 Price Information  
Current Price: ₹2,456.75
Price Change: +₹12.30 (+0.51%)
5-min SMA: ₹2,442.50

📈 Technical Indicators
RSI: 28.5 (Oversold)
Volume: 2.1x average
Volume: 245,670

🎯 Signal Reasoning
• Price above SMA
• Oversold (RSI: 28.5) 
• High volume (2.1x avg)

⚠️ Risk Management
This is an automated signal. Please verify with additional analysis.
```

---

## 🎯 **Quick Commands**

```bash
# Run full tracker
python3 enhanced_stock_tracker.py

# Run demo (works offline)
python3 demo_stock_tracker.py

# Test connection only
python3 test_stock_tracker.py

# Install packages (if needed)
pip3 install yfinance pandas numpy matplotlib seaborn
```

---

## 📞 **Support**

### **Common Issues:**
- **"Authentication failed"** → Use App Password, not regular password
- **"No data found"** → Markets might be closed, try during 9:15 AM - 3:30 PM IST
- **"429 Too Many Requests"** → Wait a few minutes and try again

### **Files Generated:**
- `tracking_data.json` - Historical signals
- `stock_tracker_YYYY-MM-DD.log` - Activity log  
- `reliance_analysis_YYYY-MM-DD.png` - Price chart

---

## 🚀 **Ready to Go!**

Your tracker is configured for **prasiddhnaik40@gmail.com** and ready to monitor Reliance Industries with:

✅ Real-time price tracking  
✅ Technical analysis (SMA + RSI)  
✅ Buy/sell signal generation  
✅ Email alerts with detailed analysis  
✅ Risk management warnings  
✅ Data logging and visualization  

**Just get your Gmail App Password and run it!** 🎉

---

*Happy Trading! 📈💰* 