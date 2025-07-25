"""
Provider Registry - Loads and manages provider configurations from YAML
Supports filtering, validation, and hot-reloading of provider configurations
"""

import asyncio
import logging
import os
import time
import os
import time
import logging
from typing import Dict, List, Optional, Any

# YAML import with proper error handling
try:
    import yaml
except ImportError:
    yaml = None

from pydantic import BaseModel, validator

logger = logging.getLogger(__name__)

class ProviderConfig(BaseModel):
    """Pydantic model for provider configuration validation"""
    id: str
    name: str
    base_url: str
    health_endpoint: str
    auth_type: str = "none"
    rate_limits: Dict[str, int]
    priority_score: int
    category: str
    free_tier_limits: Dict[str, int]
    required_env_keys: List[str] = []
    
    @validator('auth_type')
    def validate_auth_type(cls, v):
        allowed_types = ['none', 'api_key', 'bearer', 'basic']
        if v not in allowed_types:
            raise ValueError(f'auth_type must be one of {allowed_types}')
        return v
    
    @validator('category')
    def validate_category(cls, v):
        allowed_categories = ['stock', 'crypto', 'forex', 'news', 'general']
        if v not in allowed_categories:
            raise ValueError(f'category must be one of {allowed_categories}')
        return v
    
    @validator('priority_score')
    def validate_priority_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('priority_score must be between 0 and 100')
        return v

class ProviderRegistry:
    """
    Provider registry loader and manager
    Reads YAML configuration and provides access to provider metadata
    """
    
    def __init__(self, registry_path: str):
        self.registry_path = registry_path
        self.providers: Dict[str, Dict[str, Any]] = {}
        self.last_loaded: Optional[float] = None
        self.file_mtime: Optional[float] = None
        
    async def load_registry(self, force_reload: bool = False):
        """Load provider registry from YAML file"""
        try:
            # Check if file exists
            if not os.path.exists(self.registry_path):
                logger.error(f"Provider registry file not found: {self.registry_path}")
                raise FileNotFoundError(f"Registry file not found: {self.registry_path}")
            
            # Check if we need to reload
            current_mtime = os.path.getmtime(self.registry_path)
            if not force_reload and self.file_mtime == current_mtime:
                return
            
            logger.info(f"Loading provider registry from {self.registry_path}")
            
            # Load YAML file
            with open(self.registry_path, 'r', encoding='utf-8') as file:
                raw_data = yaml.safe_load(file)
            
            if not raw_data:
                raise ValueError("Registry file is empty or invalid")
            
            # Parse and validate providers
            parsed_providers = {}
            
            # Process all provider categories
            for category_name, category_providers in raw_data.items():
                if category_name.endswith('_providers') or category_name == 'backup_providers':
                    if isinstance(category_providers, dict):
                        for provider_id, provider_data in category_providers.items():
                            try:
                                # Add provider_id to the data if not present
                                if 'id' not in provider_data:
                                    provider_data['id'] = provider_id
                                
                                # Validate provider configuration
                                validated_provider = ProviderConfig(**provider_data)
                                parsed_providers[provider_id] = validated_provider.dict()
                                
                            except Exception as e:
                                logger.warning(f"Invalid provider config for {provider_id}: {e}")
                                continue
            
            if not parsed_providers:
                raise ValueError("No valid providers found in registry")
            
            # Update registry
            self.providers = parsed_providers
            self.last_loaded = time.time()
            self.file_mtime = current_mtime
            
            logger.info(f"Loaded {len(self.providers)} providers from registry")
            
            # Log provider summary by category
            category_counts = {}
            for provider in self.providers.values():
                category = provider['category']
                category_counts[category] = category_counts.get(category, 0) + 1
            
            logger.info(f"Provider distribution: {category_counts}")
            
        except Exception as e:
            logger.error(f"Failed to load provider registry: {e}")
            raise
    
    async def reload_registry(self):
        """Hot-reload the provider registry"""
        try:
            await self.load_registry(force_reload=True)
            logger.info("Provider registry reloaded successfully")
        except Exception as e:
            logger.error(f"Failed to reload provider registry: {e}")
            raise
    
    def get_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get specific provider configuration by ID"""
        return self.providers.get(provider_id)
    
    def list_providers(self, 
                      category: Optional[str] = None, 
                      available_only: bool = False,
                      min_priority: int = 0) -> List[Dict[str, Any]]:
        """
        List providers with optional filtering
        
        Args:
            category: Filter by provider category (stock, crypto, forex, news)
            available_only: Only return providers with available API keys
            min_priority: Minimum priority score
        """
        filtered_providers = []
        
        for provider in self.providers.values():
            # Category filter
            if category and provider['category'] != category:
                continue
            
            # Priority filter
            if provider['priority_score'] < min_priority:
                continue
            
            # Availability filter (check if API keys are available)
            if available_only and not self._is_provider_available(provider):
                continue
            
            filtered_providers.append(provider.copy())
        
        return filtered_providers
    
    def get_providers_by_priority(self, 
                                 category: Optional[str] = None,
                                 limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get providers sorted by priority score (highest first)"""
        providers = self.list_providers(category=category)
        sorted_providers = sorted(providers, key=lambda p: p['priority_score'], reverse=True)
        
        if limit:
            return sorted_providers[:limit]
        
        return sorted_providers
    
    def get_categories(self) -> List[str]:
        """Get list of all available provider categories"""
        categories = set()
        for provider in self.providers.values():
            categories.add(provider['category'])
        return sorted(list(categories))
    
    def get_providers_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get providers grouped by category"""
        category_providers = {}
        
        for provider in self.providers.values():
            category = provider['category']
            if category not in category_providers:
                category_providers[category] = []
            category_providers[category].append(provider.copy())
        
        # Sort each category by priority
        for category in category_providers:
            category_providers[category].sort(key=lambda p: p['priority_score'], reverse=True)
        
        return category_providers
    
    def get_backup_providers(self, 
                           primary_provider_id: str, 
                           category: Optional[str] = None,
                           max_backups: int = 5) -> List[Dict[str, Any]]:
        """Get backup providers for a given primary provider"""
        primary_provider = self.get_provider(primary_provider_id)
        if not primary_provider:
            return []
        
        # Use same category as primary if not specified
        if not category:
            category = primary_provider['category']
        
        # Get all providers in the category except the primary
        backup_candidates = [
            p for p in self.list_providers(category=category, available_only=True)
            if p['id'] != primary_provider_id
        ]
        
        # Sort by priority and return top candidates
        backup_candidates.sort(key=lambda p: p['priority_score'], reverse=True)
        
        return backup_candidates[:max_backups]
    
    def _is_provider_available(self, provider: Dict[str, Any]) -> bool:
        """Check if provider has required API keys available"""
        required_keys = provider.get('required_env_keys', [])
        
        if not required_keys:
            return True  # No keys required
        
        # Check if at least one required key is available
        for key_name in required_keys:
            if os.getenv(key_name):
                return True
        
        return False
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get overall statistics about the provider registry"""
        total_providers = len(self.providers)
        available_providers = len([p for p in self.providers.values() if self._is_provider_available(p)])
        
        # Category distribution
        category_stats = {}
        for provider in self.providers.values():
            category = provider['category']
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'available': 0}
            
            category_stats[category]['total'] += 1
            if self._is_provider_available(provider):
                category_stats[category]['available'] += 1
        
        # Priority distribution
        priority_ranges = {
            'high': len([p for p in self.providers.values() if p['priority_score'] >= 80]),
            'medium': len([p for p in self.providers.values() if 50 <= p['priority_score'] < 80]),
            'low': len([p for p in self.providers.values() if p['priority_score'] < 50])
        }
        
        return {
            'total_providers': total_providers,
            'available_providers': available_providers,
            'unavailable_providers': total_providers - available_providers,
            'category_stats': category_stats,
            'priority_distribution': priority_ranges,
            'last_loaded': self.last_loaded,
            'registry_path': self.registry_path
        }
    
    def validate_provider_config(self, provider_data: Dict[str, Any]) -> bool:
        """Validate a provider configuration"""
        try:
            ProviderConfig(**provider_data)
            return True
        except Exception as e:
            logger.error(f"Provider validation failed: {e}")
            return False
    
    def get_failover_chain(self, 
                          category: str, 
                          max_providers: int = 5,
                          exclude_providers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get a failover chain of providers for a category"""
        exclude_providers = exclude_providers or []
        
        # Get available providers in category
        providers = [
            p for p in self.list_providers(category=category, available_only=True)
            if p['id'] not in exclude_providers
        ]
        
        # Sort by priority score (highest first)
        providers.sort(key=lambda p: p['priority_score'], reverse=True)
        
        return providers[:max_providers]
    
    def get_rate_limited_providers(self) -> List[str]:
        """Get list of provider IDs that are currently rate limited"""
        # This would typically check against Redis or other storage
        # For now, return empty list as placeholder
        return []
    
    def get_healthy_providers(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of currently healthy providers"""
        # This would typically check against Redis health cache
        # For now, return all available providers as placeholder
        return self.list_providers(category=category, available_only=True)
    
    async def auto_reload_check(self):
        """Check if registry file has been modified and reload if necessary"""
        try:
            if not os.path.exists(self.registry_path):
                return
            
            current_mtime = os.path.getmtime(self.registry_path)
            if self.file_mtime and current_mtime > self.file_mtime:
                logger.info("Registry file modified, reloading...")
                await self.reload_registry()
        except Exception as e:
            logger.error(f"Error checking registry file modification: {e}")
    
    def export_provider_list(self, format: str = 'json') -> str:
        """Export provider list in specified format"""
        import json
        
        if format.lower() == 'json':
            return json.dumps(list(self.providers.values()), indent=2)
        elif format.lower() == 'yaml':
            import yaml
            return yaml.dump(list(self.providers.values()), default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def search_providers(self, query: str) -> List[Dict[str, Any]]:
        """Search providers by name, category, or ID"""
        query = query.lower()
        matching_providers = []
        
        for provider in self.providers.values():
            if (query in provider['id'].lower() or 
                query in provider['name'].lower() or 
                query in provider['category'].lower()):
                matching_providers.append(provider.copy())
        
        return matching_providers 