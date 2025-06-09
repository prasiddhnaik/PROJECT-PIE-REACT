-- ⚡ HIGH-PERFORMANCE SUPABASE CACHE TABLES
-- Run this in your Supabase SQL Editor for MAXIMUM SPEED

-- 🚀 API Response Cache Table - Lightning Fast Data Retrieval
CREATE TABLE IF NOT EXISTS public.api_cache (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    cache_key TEXT UNIQUE NOT NULL,
    data_type TEXT NOT NULL, -- 'crypto', 'stock', 'forex'
    symbol TEXT NOT NULL,
    response_data JSONB NOT NULL,
    price_usd NUMERIC,
    change_24h NUMERIC,
    source TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '5 minutes')
);

-- 🔥 Pre-computed Financial Data - Instant Responses
CREATE TABLE IF NOT EXISTS public.precomputed_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    data_key TEXT UNIQUE NOT NULL,
    computation_type TEXT NOT NULL, -- 'sip_calculation', 'portfolio_analysis', 'risk_metrics'
    input_parameters JSONB NOT NULL,
    computed_results JSONB NOT NULL,
    computation_time_ms INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ⚡ Real-time Price Feed - Ultra Fast Price Updates
CREATE TABLE IF NOT EXISTS public.price_feed (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    symbol TEXT NOT NULL,
    data_type TEXT NOT NULL, -- 'crypto', 'stock', 'forex'
    current_price NUMERIC NOT NULL,
    change_24h NUMERIC DEFAULT 0,
    volume_24h NUMERIC DEFAULT 0,
    market_cap NUMERIC DEFAULT 0,
    source TEXT NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_live BOOLEAN DEFAULT true
);

-- 🚀 Performance Analytics - Track Speed Improvements
CREATE TABLE IF NOT EXISTS public.performance_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    endpoint TEXT NOT NULL,
    response_time_ms INTEGER NOT NULL,
    cache_hit BOOLEAN DEFAULT false,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL
);

-- 📊 Popular Calculations Cache - Instant Results for Common Queries
CREATE TABLE IF NOT EXISTS public.popular_calculations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    calculation_hash TEXT UNIQUE NOT NULL,
    calculation_type TEXT NOT NULL,
    input_params JSONB NOT NULL,
    results JSONB NOT NULL,
    usage_count INTEGER DEFAULT 1,
    avg_computation_time_ms INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 🔥 INDEXES for MAXIMUM SPEED
CREATE INDEX IF NOT EXISTS idx_api_cache_key ON public.api_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_api_cache_symbol ON public.api_cache(symbol, data_type);
CREATE INDEX IF NOT EXISTS idx_api_cache_expires ON public.api_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_precomputed_key ON public.precomputed_data(data_key);
CREATE INDEX IF NOT EXISTS idx_price_feed_symbol ON public.price_feed(symbol, data_type);
CREATE INDEX IF NOT EXISTS idx_price_feed_updated ON public.price_feed(last_updated DESC);
CREATE INDEX IF NOT EXISTS idx_popular_calculations_hash ON public.popular_calculations(calculation_hash);
CREATE INDEX IF NOT EXISTS idx_performance_endpoint ON public.performance_metrics(endpoint, timestamp DESC);

-- ⚡ REAL-TIME TRIGGERS for Automatic Updates
CREATE OR REPLACE FUNCTION public.update_cache_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER api_cache_updated_at
    BEFORE UPDATE ON public.api_cache
    FOR EACH ROW
    EXECUTE FUNCTION public.update_cache_timestamp();

CREATE TRIGGER precomputed_data_updated_at
    BEFORE UPDATE ON public.precomputed_data
    FOR EACH ROW
    EXECUTE FUNCTION public.update_cache_timestamp();

-- 🚀 AUTOMATIC CACHE CLEANUP for Performance
CREATE OR REPLACE FUNCTION public.cleanup_expired_cache()
RETURNS void AS $$
BEGIN
    -- Remove expired API cache entries
    DELETE FROM public.api_cache WHERE expires_at < NOW();
    
    -- Remove old performance metrics (keep last 7 days)
    DELETE FROM public.performance_metrics 
    WHERE timestamp < NOW() - INTERVAL '7 days';
    
    -- Update popular calculations stats
    UPDATE public.popular_calculations 
    SET usage_count = usage_count + 1, 
        last_accessed = NOW()
    WHERE last_accessed > NOW() - INTERVAL '1 hour';
END;
$$ LANGUAGE plpgsql;

-- 🔥 ENABLE ROW LEVEL SECURITY (Public read access for cache)
ALTER TABLE public.api_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.precomputed_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.price_feed ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.popular_calculations ENABLE ROW LEVEL SECURITY;

-- 📊 PUBLIC READ POLICIES for Maximum Speed
CREATE POLICY "Public read access for api_cache" ON public.api_cache FOR SELECT USING (true);
CREATE POLICY "Public read access for precomputed_data" ON public.precomputed_data FOR SELECT USING (true);
CREATE POLICY "Public read access for price_feed" ON public.price_feed FOR SELECT USING (true);
CREATE POLICY "Public read access for popular_calculations" ON public.popular_calculations FOR SELECT USING (true);

-- 🚀 INSERT POLICIES for System Updates
CREATE POLICY "System can insert api_cache" ON public.api_cache FOR INSERT WITH CHECK (true);
CREATE POLICY "System can update api_cache" ON public.api_cache FOR UPDATE USING (true);
CREATE POLICY "System can insert precomputed_data" ON public.precomputed_data FOR INSERT WITH CHECK (true);
CREATE POLICY "System can update precomputed_data" ON public.precomputed_data FOR UPDATE USING (true);
CREATE POLICY "System can insert price_feed" ON public.price_feed FOR INSERT WITH CHECK (true);
CREATE POLICY "System can update price_feed" ON public.price_feed FOR UPDATE USING (true);

-- Users can insert their own performance metrics
CREATE POLICY "Users can insert performance_metrics" ON public.performance_metrics 
FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- ⚡ SCHEDULE AUTOMATIC CLEANUP (Run every 5 minutes)
-- Note: This requires pg_cron extension - enable in Supabase Dashboard under Database > Extensions
-- SELECT cron.schedule('cleanup-cache', '*/5 * * * *', 'SELECT public.cleanup_expired_cache();');

-- 🔥 POPULATE WITH SAMPLE FAST DATA
INSERT INTO public.price_feed (symbol, data_type, current_price, change_24h, source, last_updated) VALUES
('bitcoin', 'crypto', 107650.00, 2.1, 'Supabase Cache', NOW()),
('ethereum', 'crypto', 3850.00, 1.8, 'Supabase Cache', NOW()),
('AAPL', 'stock', 203.92, 1.2, 'Supabase Cache', NOW()),
('TSLA', 'stock', 248.85, -0.8, 'Supabase Cache', NOW()),
('USD_EUR', 'forex', 0.877, 0.1, 'Supabase Cache', NOW())
ON CONFLICT DO NOTHING;

-- ⚡ SUCCESS MESSAGE
SELECT 'High-Performance Supabase Cache Tables Created Successfully! 🚀' as status; 