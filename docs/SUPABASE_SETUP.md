# 🚀 Supabase Integration Setup Guide
## Financial Analytics Hub - User Authentication & Data Persistence

### 📋 Overview

Your Financial Analytics Hub now includes **Supabase integration** for:
- **🔐 User Authentication** (Sign up, Sign in, Session management)
- **💾 Data Persistence** (Save calculations, portfolios, preferences)
- **📊 Personal Dashboard** (Analytics, insights, portfolio tracking)
- **🔒 Secure Data** (Row Level Security, user isolation)

---

## 🎯 Quick Setup (5 Minutes)

### Step 1: Create Supabase Project

1. **Go to [supabase.com](https://supabase.com)**
2. **Click "Start your project"**
3. **Sign up/Login** with GitHub or email
4. **Create New Project**:
   - Project name: `financial-analytics-hub`
   - Database password: `[choose-strong-password]`
   - Region: Choose closest to your location
5. **Wait 1-2 minutes** for project setup

### Step 2: Get Your API Keys

1. **In your Supabase Dashboard**, go to **Settings** → **API**
2. **Copy these values**:
   ```
   Project URL: https://[your-project-id].supabase.co
   Anon (public) key: eyJ... [long string]
   Service role key: eyJ... [long string] (optional but recommended)
   ```

### Step 3: Setup Environment Variables

Create a `.env` file in your project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://[your-project-id].supabase.co
SUPABASE_KEY=eyJ... [your-anon-key]
SUPABASE_SERVICE_KEY=eyJ... [your-service-role-key]

# Your existing API keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINANCIAL_MODELING_PREP_API_KEY=your_fmp_key
```

### Step 4: Setup Database Schema

1. **In Supabase Dashboard**, go to **SQL Editor**
2. **Copy and paste** the contents of `docs/supabase_setup.sql`
3. **Click "Run"** to execute the SQL commands
4. **Verify tables** in **Table Editor**: `sip_calculations`, `portfolios`, `user_preferences`

### Step 5: Install Dependencies

```bash
pip install supabase python-dotenv
```

---

## 🎉 You're Ready!

Run your application:

```bash
streamlit run src/apps/api_dashboard.py
# or
streamlit run src/apps/compound_interest_app.py
```

**New Features Available:**
- 🔐 **Authentication sidebar** in API Dashboard
- 💾 **Save calculations** in SIP Calculator
- 👤 **Personal Dashboard** tab (when logged in)
- 📊 **Analytics & insights**
- ⚙️ **User preferences**

---

## 🔧 Features Overview

### 🔐 Authentication
- **Sign Up**: Create account with email verification
- **Sign In**: Secure login with session management
- **User Profiles**: Store user metadata and preferences
- **Sign Out**: Clean session termination

### 💾 Data Persistence
- **SIP Calculations**: Save and retrieve calculation history
- **Portfolios**: Track multiple investment portfolios
- **User Preferences**: Default settings, risk tolerance
- **Analytics**: Historical data analysis and insights

### 👤 Personal Dashboard
- **Portfolio Summary**: Total invested, current value, profit/loss
- **Recent Calculations**: Quick access to saved calculations
- **Activity Analytics**: Monthly calculation trends
- **Risk Distribution**: Investment pattern analysis
- **Quick Actions**: Fast navigation to tools

### 🔒 Security Features
- **Row Level Security (RLS)**: Users only see their own data
- **UUID Primary Keys**: Secure, non-guessable identifiers
- **Authentication Required**: Protected endpoints
- **Data Isolation**: Complete user data separation

---

## 📊 Database Schema

### Tables Created:

#### `sip_calculations`
```sql
- id (UUID, Primary Key)
- user_id (UUID, Foreign Key to auth.users)
- calculation_type (TEXT): 'annual_compound', 'monthly_sip', etc.
- monthly_sip (NUMERIC): Monthly SIP amount
- annual_rate (NUMERIC): Expected annual return
- time_years (NUMERIC): Investment duration
- final_value (NUMERIC): Calculated final portfolio value
- total_invested (NUMERIC): Total amount invested
- profit (NUMERIC): Profit or loss amount
- total_return_percent (NUMERIC): Return percentage
- risk_level (TEXT): 'Low', 'Medium', 'High', 'Very High'
- fund_name (TEXT): Optional fund name
- calculation_metadata (JSONB): Additional calculation data
- created_at (TIMESTAMP): When calculation was saved
```

#### `portfolios`
```sql
- id (UUID, Primary Key)
- user_id (UUID, Foreign Key)
- portfolio_name (TEXT): User-defined portfolio name
- total_invested (NUMERIC): Total invested amount
- current_value (NUMERIC): Current portfolio value
- holdings (JSONB): Array of portfolio holdings
- risk_tolerance (TEXT): User's risk preference
- investment_goals (JSONB): Array of investment goals
- created_at, updated_at (TIMESTAMP)
```

#### `user_preferences`
```sql
- id (UUID, Primary Key)
- user_id (UUID, Foreign Key, UNIQUE)
- default_sip_amount (NUMERIC): Default SIP amount
- preferred_investment_duration (NUMERIC): Default years
- risk_tolerance (TEXT): 'conservative', 'moderate', 'aggressive'
- notification_preferences (JSONB): Notification settings
- dashboard_layout (JSONB): UI layout preferences
- favorite_funds (JSONB): Array of favorite funds
- created_at, updated_at (TIMESTAMP)
```

---

## 🚀 Advanced Configuration

### Environment Variables Explained

```bash
# Required - Basic Supabase connection
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_KEY=eyJ... # Anon/public key for client-side operations

# Optional - Enhanced admin operations
SUPABASE_SERVICE_KEY=eyJ... # Service role key for admin operations

# Optional - Enhanced financial data
ALPHA_VANTAGE_API_KEY=your_key
FINANCIAL_MODELING_PREP_API_KEY=your_key
COINMARKETCAP_API_KEY=your_key
NEWS_API_KEY=your_key
```

### Supabase Dashboard Features

1. **Authentication**: Monitor users in **Authentication** → **Users**
2. **Database**: View/edit data in **Table Editor**
3. **SQL Editor**: Run custom queries
4. **API Documentation**: Auto-generated API docs
5. **Storage**: File uploads (future feature)
6. **Edge Functions**: Serverless functions (future feature)

### Row Level Security (RLS)

All tables have RLS enabled with policies ensuring:
- Users can only access their own data
- Automatic user_id filtering
- Secure by default
- No cross-user data leakage

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. "Could not import Supabase modules"
```bash
# Install missing dependencies
pip install supabase python-dotenv

# Verify installation
python -c "from supabase import create_client; print('Supabase installed successfully')"
```

#### 2. "Supabase configuration missing"
- Check `.env` file exists in project root
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are set
- Check for typos in environment variable names

#### 3. "Authentication failed"
- Verify API keys are correct
- Check if email confirmation is required
- Ensure RLS policies are properly set

#### 4. "Database connection failed"
- Verify project URL is correct
- Check if project is paused (Supabase pauses inactive projects)
- Ensure internet connectivity

#### 5. "Permission denied" errors
- Run the SQL schema setup commands
- Verify RLS policies are created
- Check user authentication status

### Demo Mode

If Supabase setup fails, the application gracefully falls back to **demo mode**:
- Authentication features disabled
- Calculations work normally
- No data persistence
- Banner shows "Running in demo mode"

---

## 🔮 Future Enhancements

### Planned Features:
- **📱 Real-time Notifications**: Portfolio alerts and updates
- **📊 Advanced Analytics**: Correlation analysis, risk metrics
- **🤖 AI Recommendations**: Personalized investment suggestions
- **📈 Live Portfolio Tracking**: Real-time NAV updates
- **👥 Social Features**: Share portfolios, compare performance
- **📱 Mobile App**: React Native app with same backend
- **🔌 API Webhooks**: External system integrations

### Scaling Considerations:
- **Performance**: Automatic caching and optimization
- **Security**: Advanced authentication (2FA, SSO)
- **Compliance**: Financial data regulations
- **Backup**: Automated daily backups
- **Monitoring**: Application performance monitoring

---

## 📞 Support

### Need Help?

1. **Check this guide** first
2. **Supabase Documentation**: [supabase.com/docs](https://supabase.com/docs)
3. **Project Issues**: Create GitHub issue
4. **Supabase Support**: [supabase.com/support](https://supabase.com/support)

### Resources:
- **Supabase Dashboard**: [app.supabase.com](https://app.supabase.com)
- **API Reference**: Available in your Supabase project
- **Python Client Docs**: [supabase-community.github.io/supabase-py](https://supabase-community.github.io/supabase-py/)

---

## ✅ Success Checklist

- [ ] Supabase project created
- [ ] API keys copied to `.env` file
- [ ] Database schema executed
- [ ] Dependencies installed (`supabase`, `python-dotenv`)
- [ ] Application starts without errors
- [ ] Can sign up new user
- [ ] Can sign in with user
- [ ] Can save calculations
- [ ] Personal dashboard loads
- [ ] Can sign out

**🎉 Congratulations! Your Financial Analytics Hub is now supercharged with Supabase!** 