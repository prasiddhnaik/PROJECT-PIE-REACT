#!/usr/bin/env python3
"""
Configuration file for Enhanced Stock Tracker
"""

# Email Configuration (Configure with your own credentials)
EMAIL_CONFIG = {
    'sender': 'your-email@gmail.com',
    'password': 'your-app-password',  # Use Gmail App Password for better security
    'recipient': 'your-email@gmail.com'
}

# Stock Configuration - Multiple Categories
STOCK_CATEGORIES = {
    'tech': {
        'name': 'Technology Companies',
        'stocks': {
            'TCS.NS': {'name': 'Tata Consultancy Services', 'sector': 'IT Services'},
            'INFY.NS': {'name': 'Infosys Limited', 'sector': 'IT Services'},
            'WIPRO.NS': {'name': 'Wipro Limited', 'sector': 'IT Services'},
            'HCLTECH.NS': {'name': 'HCL Technologies', 'sector': 'IT Services'},
            'TECHM.NS': {'name': 'Tech Mahindra', 'sector': 'IT Services'},
            'LTI.NS': {'name': 'L&T Infotech', 'sector': 'IT Services'}
        }
    },
    'banking': {
        'name': 'Banking & Finance',
        'stocks': {
            'HDFCBANK.NS': {'name': 'HDFC Bank', 'sector': 'Private Bank'},
            'ICICIBANK.NS': {'name': 'ICICI Bank', 'sector': 'Private Bank'},
            'SBIN.NS': {'name': 'State Bank of India', 'sector': 'Public Bank'},
            'AXISBANK.NS': {'name': 'Axis Bank', 'sector': 'Private Bank'},
            'KOTAKBANK.NS': {'name': 'Kotak Mahindra Bank', 'sector': 'Private Bank'},
            'INDUSINDBK.NS': {'name': 'IndusInd Bank', 'sector': 'Private Bank'}
        }
    },
    'pharma': {
        'name': 'Pharmaceutical',
        'stocks': {
            'SUNPHARMA.NS': {'name': 'Sun Pharmaceutical', 'sector': 'Pharmaceuticals'},
            'DRREDDY.NS': {'name': 'Dr. Reddys Laboratories', 'sector': 'Pharmaceuticals'},
            'CIPLA.NS': {'name': 'Cipla Limited', 'sector': 'Pharmaceuticals'},
            'DIVISLAB.NS': {'name': 'Divis Laboratories', 'sector': 'Pharmaceuticals'},
            'BIOCON.NS': {'name': 'Biocon Limited', 'sector': 'Biotechnology'},
            'LUPIN.NS': {'name': 'Lupin Limited', 'sector': 'Pharmaceuticals'}
        }
    },
    'energy': {
        'name': 'Energy & Oil',
        'stocks': {
            'RELIANCE.NS': {'name': 'Reliance Industries', 'sector': 'Oil & Gas'},
            'ONGC.NS': {'name': 'Oil & Natural Gas Corp', 'sector': 'Oil & Gas'},
            'IOC.NS': {'name': 'Indian Oil Corporation', 'sector': 'Oil Refining'},
            'BPCL.NS': {'name': 'Bharat Petroleum', 'sector': 'Oil Refining'},
            'GAIL.NS': {'name': 'GAIL India Limited', 'sector': 'Gas Distribution'},
            'POWERGRID.NS': {'name': 'Power Grid Corp', 'sector': 'Power Transmission'}
        }
    },
    'fmcg': {
        'name': 'FMCG & Consumer',
        'stocks': {
            'HINDUNILVR.NS': {'name': 'Hindustan Unilever', 'sector': 'FMCG'},
            'ITC.NS': {'name': 'ITC Limited', 'sector': 'FMCG'},
            'NESTLEIND.NS': {'name': 'Nestle India', 'sector': 'Food Products'},
            'BRITANNIA.NS': {'name': 'Britannia Industries', 'sector': 'Food Products'},
            'DABUR.NS': {'name': 'Dabur India', 'sector': 'Personal Care'},
            'GODREJCP.NS': {'name': 'Godrej Consumer Products', 'sector': 'Personal Care'}
        }
    },
    'auto': {
        'name': 'Automobile',
        'stocks': {
            'MARUTI.NS': {'name': 'Maruti Suzuki India', 'sector': 'Automobiles'},
            'TATAMOTORS.NS': {'name': 'Tata Motors', 'sector': 'Automobiles'},
            'M&M.NS': {'name': 'Mahindra & Mahindra', 'sector': 'Automobiles'},
            'BAJAJ-AUTO.NS': {'name': 'Bajaj Auto', 'sector': 'Two Wheelers'},
            'HEROMOTOCO.NS': {'name': 'Hero MotoCorp', 'sector': 'Two Wheelers'},
            'EICHERMOT.NS': {'name': 'Eicher Motors', 'sector': 'Automobiles'}
        }
    }
}

# Default tracking configuration - you can change this
STOCK_CONFIG = {
    'category': 'tech',  # Change this to track different categories
    'symbol': 'TCS.NS',  # Default stock within the category
    'sma_period': 5,
    'volume_threshold': 1.5
}

# Tracking Configuration
TRACKING_CONFIG = {
    'update_interval': 60,  # seconds between updates
    'default_duration': 60,  # minutes to run
    'email_cooldown': 300,  # 5 minutes between emails
    'min_signal_strength': 2,  # minimum strength for BUY/SELL
    'status_email_interval': 1800,  # 30 minutes = 1800 seconds for status emails
    'send_status_emails': True  # Enable regular status emails
}

# Alternative stocks you can track
ALTERNATIVE_STOCKS = {
    'TCS.NS': 'Tata Consultancy Services',
    'INFY.NS': 'Infosys',
    'HDFCBANK.NS': 'HDFC Bank',
    'ICICIBANK.NS': 'ICICI Bank',
    'SBIN.NS': 'State Bank of India',
    'ITC.NS': 'ITC Limited',
    'LT.NS': 'Larsen & Toubro',
    'ONGC.NS': 'Oil & Natural Gas Corp'
}

# Security Note
SECURITY_NOTE = """
⚠️ SECURITY RECOMMENDATION:
To use email features, configure your email credentials:
1. Replace 'your-email@gmail.com' with your actual email
2. Enable 2-Step Verification on your Google Account
3. Create an App Password specifically for this tracker
4. Replace 'your-app-password' with the 16-character App Password

This provides better security than using your main password.
"""

if __name__ == "__main__":
    print("📋 Enhanced Stock Tracker Configuration")
    print("=" * 50)
    print(f"📧 Email: {EMAIL_CONFIG['sender']}")
    print(f"📊 Stock: {STOCK_CONFIG['symbol']}")
    print(f"📈 SMA Period: {STOCK_CONFIG['sma_period']} minutes")
    print(f"⏰ Update Interval: {TRACKING_CONFIG['update_interval']} seconds")
    print("\n" + SECURITY_NOTE) 