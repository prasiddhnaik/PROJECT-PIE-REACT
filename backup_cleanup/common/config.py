"""
Shared configuration management for microservices.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
import json

class BaseServiceConfig(BaseSettings):
    """Base configuration for all services."""
    
    # Service identity
    service_name: str = Field(..., env="SERVICE_NAME")
    service_version: str = Field("1.0.0", env="SERVICE_VERSION")
    environment: str = Field("development", env="ENVIRONMENT")
    
    # Server configuration
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(..., env="PORT")
    workers: int = Field(1, env="WORKERS")
    
    # Redis configuration
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    
    # Security
    secret_key: str = Field("change-this-in-production", env="SECRET_KEY")
    allowed_origins: List[str] = Field(["*"], env="ALLOWED_ORIGINS")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("json", env="LOG_FORMAT")
    
    # Health check
    health_check_interval: int = Field(30, env="HEALTH_CHECK_INTERVAL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

class DataServiceConfig(BaseServiceConfig):
    """Configuration for data service."""
    
    service_name: str = "data-service"
    port: int = Field(8002, env="DATA_SERVICE_PORT")
    
    # External API configurations
    coingecko_api_url: str = Field("https://api.coingecko.com/api/v3", env="COINGECKO_API_URL")
    binance_api_url: str = Field("https://api.binance.com/api/v3", env="BINANCE_API_URL")
    yahoo_finance_api_url: str = Field("https://query1.finance.yahoo.com", env="YAHOO_FINANCE_API_URL")
    
    # API Keys
    alpha_vantage_api_key: Optional[str] = Field(None, env="ALPHA_VANTAGE_API_KEY")
    polygon_api_key: Optional[str] = Field(None, env="POLYGON_API_KEY")
    finnhub_api_key: Optional[str] = Field(None, env="FINNHUB_API_KEY")
    
    # Rate limiting for external APIs
    coingecko_rate_limit: int = Field(50, env="COINGECKO_RATE_LIMIT")
    binance_rate_limit: int = Field(1200, env="BINANCE_RATE_LIMIT")
    
    # Cache settings
    cache_ttl_crypto: int = Field(60, env="CACHE_TTL_CRYPTO")
    cache_ttl_market: int = Field(300, env="CACHE_TTL_MARKET")

class ChartServiceConfig(BaseServiceConfig):
    """Configuration for chart service."""
    
    service_name: str = "chart-service"
    port: int = Field(8003, env="CHART_SERVICE_PORT")
    
    # Data service URL
    data_service_url: str = Field("http://localhost:8002", env="DATA_SERVICE_URL")
    
    # Chart generation settings
    max_data_points: int = Field(1000, env="MAX_DATA_POINTS")
    default_timeframe: str = Field("1d", env="DEFAULT_TIMEFRAME")
    
    # Cache settings
    cache_ttl_charts: int = Field(600, env="CACHE_TTL_CHARTS")
    cache_ttl_indicators: int = Field(300, env="CACHE_TTL_INDICATORS")

class GraphServiceConfig(BaseServiceConfig):
    """Configuration for graph service."""
    
    service_name: str = "graph-service"
    port: int = Field(8004, env="GRAPH_SERVICE_PORT")
    
    # Data service URL
    data_service_url: str = Field("http://localhost:8002", env="DATA_SERVICE_URL")
    
    # Graph generation settings
    max_parallel_graphs: int = Field(5, env="MAX_PARALLEL_GRAPHS")
    graph_timeout: int = Field(30, env="GRAPH_TIMEOUT")
    
    # Cache settings
    cache_ttl_graphs: int = Field(1800, env="CACHE_TTL_GRAPHS")

class AIServiceConfig(BaseServiceConfig):
    """Configuration for AI service."""
    
    service_name: str = "ai-service"
    port: int = Field(8005, env="AI_SERVICE_PORT")
    
    # Data service URL
    data_service_url: str = Field("http://localhost:8002", env="DATA_SERVICE_URL")
    
    # OpenRouter configuration
    openrouter_api_key: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    openrouter_api_url: str = Field("https://openrouter.ai/api/v1", env="OPENROUTER_API_URL")
    
    # AI model settings
    default_model: str = Field("anthropic/claude-3-sonnet", env="DEFAULT_AI_MODEL")
    max_tokens: int = Field(4000, env="MAX_AI_TOKENS")
    temperature: float = Field(0.7, env="AI_TEMPERATURE")
    
    # Chat settings
    max_conversation_history: int = Field(20, env="MAX_CONVERSATION_HISTORY")
    conversation_ttl: int = Field(7200, env="CONVERSATION_TTL")  # 2 hours
    
    # Cache settings
    cache_ttl_ai: int = Field(1800, env="CACHE_TTL_AI")

class APIGatewayConfig(BaseServiceConfig):
    """Configuration for API Gateway."""
    
    service_name: str = "api-gateway"
    port: int = Field(8001, env="API_GATEWAY_PORT")
    
    # Service URLs
    data_service_url: str = Field("http://localhost:8002", env="DATA_SERVICE_URL")
    chart_service_url: str = Field("http://localhost:8003", env="CHART_SERVICE_URL")
    graph_service_url: str = Field("http://localhost:8004", env="GRAPH_SERVICE_URL")
    ai_service_url: str = Field("http://localhost:8005", env="AI_SERVICE_URL")
    
    # Gateway settings
    timeout: int = Field(30, env="GATEWAY_TIMEOUT")
    max_retries: int = Field(3, env="GATEWAY_MAX_RETRIES")
    circuit_breaker_threshold: int = Field(5, env="CIRCUIT_BREAKER_THRESHOLD")
    
    # Load balancing
    enable_load_balancing: bool = Field(False, env="ENABLE_LOAD_BALANCING")
    health_check_enabled: bool = Field(True, env="HEALTH_CHECK_ENABLED")

# Configuration factory
def get_config(service_name: str) -> BaseServiceConfig:
    """Get configuration for a specific service."""
    config_classes = {
        "data-service": DataServiceConfig,
        "chart-service": ChartServiceConfig,
        "graph-service": GraphServiceConfig,
        "ai-service": AIServiceConfig,
        "api-gateway": APIGatewayConfig,
    }
    
    config_class = config_classes.get(service_name, BaseServiceConfig)
    return config_class()

# Service discovery
class ServiceRegistry:
    """Simple service registry for microservices."""
    
    def __init__(self):
        self.services: Dict[str, Dict[str, Any]] = {}
    
    def register_service(self, name: str, url: str, health_check_url: str = None):
        """Register a service."""
        self.services[name] = {
            "url": url,
            "health_check_url": health_check_url or f"{url}/health",
            "registered_at": os.getenv("SERVICE_START_TIME", "unknown"),
            "status": "unknown"
        }
    
    def get_service_url(self, name: str) -> Optional[str]:
        """Get service URL."""
        service = self.services.get(name)
        return service["url"] if service else None
    
    def get_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered services."""
        return self.services.copy()
    
    def update_service_status(self, name: str, status: str):
        """Update service status."""
        if name in self.services:
            self.services[name]["status"] = status

# Global service registry
service_registry = ServiceRegistry()

# Initialize default service URLs
def init_service_registry():
    """Initialize service registry with default URLs."""
    services = {
        "data-service": os.getenv("DATA_SERVICE_URL", "http://localhost:8002"),
        "chart-service": os.getenv("CHART_SERVICE_URL", "http://localhost:8003"),
        "graph-service": os.getenv("GRAPH_SERVICE_URL", "http://localhost:8004"),
        "ai-service": os.getenv("AI_SERVICE_URL", "http://localhost:8005"),
        "api-gateway": os.getenv("API_GATEWAY_URL", "http://localhost:8001"),
    }
    
    for name, url in services.items():
        service_registry.register_service(name, url)

# Initialize on import
init_service_registry()

# Environment-specific configurations
DEVELOPMENT_CONFIG = {
    "debug": True,
    "reload": True,
    "log_level": "DEBUG"
}

PRODUCTION_CONFIG = {
    "debug": False,
    "reload": False,
    "log_level": "INFO",
    "workers": 4
}

def get_environment_config() -> Dict[str, Any]:
    """Get environment-specific configuration."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    if env == "production":
        return PRODUCTION_CONFIG
    return DEVELOPMENT_CONFIG 