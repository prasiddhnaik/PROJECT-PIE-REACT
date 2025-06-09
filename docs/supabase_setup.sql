-- Supabase Database Schema for Financial Analytics Hub
-- Execute these SQL commands in your Supabase SQL Editor

-- Create SIP calculations table
CREATE TABLE IF NOT EXISTS public.sip_calculations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    calculation_type TEXT NOT NULL,
    monthly_sip NUMERIC DEFAULT 0,
    annual_rate NUMERIC NOT NULL,
    time_years NUMERIC NOT NULL,
    final_value NUMERIC NOT NULL,
    total_invested NUMERIC NOT NULL,
    profit NUMERIC NOT NULL,
    total_return_percent NUMERIC NOT NULL,
    risk_level TEXT,
    fund_name TEXT,
    calculation_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create portfolios table
CREATE TABLE IF NOT EXISTS public.portfolios (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    portfolio_name TEXT NOT NULL,
    total_invested NUMERIC DEFAULT 0,
    current_value NUMERIC DEFAULT 0,
    holdings JSONB DEFAULT '[]'::jsonb,
    risk_tolerance TEXT DEFAULT 'moderate',
    investment_goals JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user preferences table
CREATE TABLE IF NOT EXISTS public.user_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    default_sip_amount NUMERIC DEFAULT 5000,
    preferred_investment_duration NUMERIC DEFAULT 10,
    risk_tolerance TEXT DEFAULT 'moderate',
    notification_preferences JSONB DEFAULT '{}'::jsonb,
    dashboard_layout JSONB DEFAULT '{}'::jsonb,
    favorite_funds JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sip_calculations_user_id ON public.sip_calculations(user_id);
CREATE INDEX IF NOT EXISTS idx_sip_calculations_created_at ON public.sip_calculations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON public.portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON public.user_preferences(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.sip_calculations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for sip_calculations
CREATE POLICY "Users can view their own calculations" ON public.sip_calculations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own calculations" ON public.sip_calculations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own calculations" ON public.sip_calculations
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own calculations" ON public.sip_calculations
    FOR DELETE USING (auth.uid() = user_id);

-- Create RLS policies for portfolios
CREATE POLICY "Users can view their own portfolios" ON public.portfolios
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own portfolios" ON public.portfolios
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own portfolios" ON public.portfolios
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own portfolios" ON public.portfolios
    FOR DELETE USING (auth.uid() = user_id);

-- Create RLS policies for user_preferences
CREATE POLICY "Users can view their own preferences" ON public.user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own preferences" ON public.user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own preferences" ON public.user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own preferences" ON public.user_preferences
    FOR DELETE USING (auth.uid() = user_id);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update timestamps
CREATE TRIGGER portfolios_updated_at
    BEFORE UPDATE ON public.portfolios
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER user_preferences_updated_at
    BEFORE UPDATE ON public.user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Grant necessary permissions (run as service role if needed)
-- GRANT ALL ON public.sip_calculations TO authenticated;
-- GRANT ALL ON public.portfolios TO authenticated;
-- GRANT ALL ON public.user_preferences TO authenticated; 