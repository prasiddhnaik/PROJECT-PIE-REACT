# 📁 Financial Analytics Hub - Directory Structure

**Organized File Structure for Easy Navigation**

---

## 🎯 Overview

All files have been organized into logical directories for better project management and easier navigation. This structure separates documentation, configuration, tracking modules, and launchers into their respective folders.

---

## 📂 Directory Layout

```
nippon/
├── 📊 financial_analytics_hub.py          # Main dashboard (ROOT LEVEL)
├── 🚀 quick_start.sh                      # Simple launcher script
│
├── 📁 docs/                               # Documentation Files
│   ├── STEALTH_MODE_GUIDE.md             # Stealth operation guide
│   ├── BACKGROUND_TRACKER_SETUP.md       # Background tracker setup
│   ├── STOCK_TRACKER_GUIDE.md            # Stock tracker guide
│   ├── QUICK_START_GUIDE.md              # Quick start instructions
│   └── DIRECTORY_STRUCTURE.md            # This file
│
├── 📁 configs/                            # Configuration Files
│   ├── config.py                         # Main configuration (email, settings)
│   ├── requirements.txt                  # Python dependencies
│   └── requirements_stock_tracker.txt    # Stock tracker dependencies
│
├── 📁 trackers/                           # Stock Tracking Modules
│   ├── enhanced_stock_tracker.py         # Full-featured tracker
│   ├── background_stock_tracker.py       # Background tracker
│   ├── silent_background_tracker.py      # Stealth tracker
│   ├── easy_stock_tracker.py             # Simplified tracker
│   ├── test_stock_tracker.py             # Connection tester
│   └── demo_stock_tracker.py             # Demo with sample data
│
└── 📁 launchers/                          # Startup Scripts
    ├── start_analytics_hub.py            # Combined launcher (Python)
    ├── invisible_launcher.py             # Stealth launcher (Python)
    ├── launch_hub.sh                     # Combined launcher (Shell)
    └── stealth_start.sh                  # Stealth launcher (Shell)
```

---

## 🚀 Quick Start Options

### 1. Simple Launch (Root Level)
```bash
./quick_start.sh
```
**Interactive menu with 3 options:**
- Normal dashboard only
- Dashboard + background tracker
- Stealth mode (hidden tracker)

### 2. Direct Dashboard Launch
```bash
streamlit run financial_analytics_hub.py --server.port=8506
```

### 3. Background Tracker Mode
```bash
bash launchers/launch_hub.sh
```

### 4. Stealth Mode (Invisible Tracker)
```bash
bash launchers/stealth_start.sh
```

---

## 📁 Directory Details

### **docs/** - Documentation Hub
Contains all markdown documentation files:
- **STEALTH_MODE_GUIDE.md**: Complete guide for invisible stock tracking
- **BACKGROUND_TRACKER_SETUP.md**: Background tracker integration guide
- **STOCK_TRACKER_GUIDE.md**: Detailed stock tracker documentation
- **QUICK_START_GUIDE.md**: Quick setup instructions
- **DIRECTORY_STRUCTURE.md**: This file explaining the structure

### **configs/** - Configuration Center
All configuration and dependency files:
- **config.py**: Main configuration with email settings and tracking parameters
- **requirements.txt**: Main project dependencies
- **requirements_stock_tracker.txt**: Additional stock tracker dependencies

### **trackers/** - Stock Monitoring Modules
All stock tracking Python modules:
- **enhanced_stock_tracker.py**: Full-featured tracker with GUI and advanced features
- **background_stock_tracker.py**: Background tracker for integration with dashboard
- **silent_background_tracker.py**: Completely invisible stealth tracker
- **easy_stock_tracker.py**: Simplified pre-configured tracker
- **test_stock_tracker.py**: Connection and email testing utility
- **demo_stock_tracker.py**: Demo version with simulated data

### **launchers/** - Startup Scripts
All launcher scripts for different modes:
- **start_analytics_hub.py**: Python launcher for dashboard + background tracker
- **invisible_launcher.py**: Python launcher for stealth mode
- **launch_hub.sh**: Shell script for dashboard + background tracker
- **stealth_start.sh**: Shell script for stealth mode

---

## 🔧 Import Updates

All import statements have been updated to work with the new structure:

### Before (Old Structure):
```python
from config import EMAIL_CONFIG
from background_stock_tracker import start_tracker
```

### After (New Structure):
```python
from configs.config import EMAIL_CONFIG
from trackers.background_stock_tracker import start_tracker
```

---

## 🎮 Usage Examples

### Run from Root Directory:
```bash
# Interactive launcher
./quick_start.sh

# Direct dashboard
streamlit run financial_analytics_hub.py --server.port=8506

# Background tracker mode
bash launchers/launch_hub.sh

# Stealth mode
bash launchers/stealth_start.sh
```

### Run Individual Trackers:
```bash
# Enhanced tracker
python3 trackers/enhanced_stock_tracker.py

# Easy tracker
python3 trackers/easy_stock_tracker.py

# Test connection
python3 trackers/test_stock_tracker.py
```

### Access Documentation:
```bash
# View guides
cat docs/STEALTH_MODE_GUIDE.md
cat docs/QUICK_START_GUIDE.md

# View configuration
cat configs/config.py
```

---

## 🛡️ Benefits of New Structure

### ✅ **Organization**
- Clear separation of concerns
- Easy to find specific files
- Professional project structure

### ✅ **Maintainability**
- Easier updates and modifications
- Clear dependencies and imports
- Modular design

### ✅ **Usability**
- Simple root-level launcher
- Logical grouping of related files
- Clear documentation structure

### ✅ **Scalability**
- Easy to add new features
- Clean module separation
- Expandable architecture

---

## 📋 File Checklist

### Root Level:
- ✅ `financial_analytics_hub.py` - Main dashboard
- ✅ `quick_start.sh` - Interactive launcher

### docs/:
- ✅ All `.md` files moved and organized
- ✅ Complete documentation suite

### configs/:
- ✅ `config.py` - Main configuration
- ✅ `requirements*.txt` - Dependencies

### trackers/:
- ✅ All tracker modules organized
- ✅ Import paths updated

### launchers/:
- ✅ All launcher scripts organized
- ✅ Paths updated for new structure

---

## 🎯 Next Steps

1. **Use the interactive launcher**: `./quick_start.sh`
2. **Check documentation**: Browse `docs/` folder
3. **Customize configuration**: Edit `configs/config.py`
4. **Test functionality**: Run different modes to verify everything works

**Perfect! Your Financial Analytics Hub is now professionally organized and ready for production use.**

---

*Generated for prasiddhnaik40@gmail.com - Organized directory structure for optimal project management.* 