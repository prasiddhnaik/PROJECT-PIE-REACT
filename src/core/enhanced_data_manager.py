import json
import os
import pickle
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib

class EnhancedDataManager:
    """
    Advanced data management system for Financial Analytics Hub
    Features:
    - Multi-tier caching (Memory, File, Database)
    - Data validation and integrity checks
    - Automatic backup and recovery
    - Performance optimization
    - Thread-safe operations
    """
    
    def __init__(self, base_path: str = "data", enable_db: bool = True):
        self.base_path = Path(base_path)
        self.enable_db = enable_db
        
        # Initialize directory structure
        self._setup_directories()
        
        # Initialize logging
        self._setup_logging()
        
        # Memory cache with TTL
        self.memory_cache = {}
        self.cache_ttl = {}  # Time-to-live for cache items
        
        # Thread lock for thread-safe operations
        self._lock = threading.Lock()
        
        # Database connection (if enabled)
        self.db_path = self.base_path / "analytics.db"
        if self.enable_db:
            self._init_database()
        
        # Load existing caches
        self._load_persistent_cache()
        
        # Start background cleanup task
        self._start_cleanup_daemon()
        
        self.logger.info("EnhancedDataManager initialized successfully")
    
    def _setup_directories(self):
        """Create necessary directory structure"""
        directories = [
            self.base_path,
            self.base_path / "cache",
            self.base_path / "backups",
            self.base_path / "processed",
            self.base_path / "logs",
            self.base_path / "raw"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """Setup logging for data operations"""
        log_file = self.base_path / "logs" / f"data_manager_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('EnhancedDataManager')
    
    def _init_database(self):
        """Initialize SQLite database for persistent storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Market data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS market_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        data_type TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        price REAL,
                        volume REAL,
                        change_24h REAL,
                        market_cap REAL,
                        raw_data TEXT,
                        source TEXT,
                        checksum TEXT,
                        UNIQUE(symbol, data_type, timestamp)
                    )
                ''')
                
                # Cache metadata table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cache_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cache_key TEXT UNIQUE NOT NULL,
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL,
                        access_count INTEGER DEFAULT 0,
                        ttl_seconds INTEGER,
                        data_size INTEGER,
                        checksum TEXT
                    )
                ''')
                
                # API performance table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_name TEXT NOT NULL,
                        endpoint TEXT,
                        response_time REAL,
                        status_code INTEGER,
                        success BOOLEAN,
                        timestamp DATETIME NOT NULL,
                        error_message TEXT
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            self.enable_db = False
    
    def _load_persistent_cache(self):
        """Load persistent cache from file"""
        cache_file = self.base_path / "cache" / "persistent_cache.json"
        try:
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self.memory_cache = data.get('cache', {})
                    self.cache_ttl = {k: datetime.fromisoformat(v) for k, v in data.get('ttl', {}).items()}
                    self.logger.info(f"Loaded {len(self.memory_cache)} items from persistent cache")
        except Exception as e:
            self.logger.error(f"Failed to load persistent cache: {e}")
            self.memory_cache = {}
            self.cache_ttl = {}
    
    def _save_persistent_cache(self):
        """Save persistent cache to file"""
        cache_file = self.base_path / "cache" / "persistent_cache.json"
        try:
            with self._lock:
                data = {
                    'cache': self.memory_cache,
                    'ttl': {k: v.isoformat() for k, v in self.cache_ttl.items()},
                    'saved_at': datetime.now().isoformat()
                }
                
                # Atomic write with backup
                temp_file = cache_file.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                
                # Create backup before replacing
                if cache_file.exists():
                    backup_file = self.base_path / "backups" / f"cache_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    cache_file.rename(backup_file)
                
                temp_file.rename(cache_file)
                self.logger.info(f"Saved {len(self.memory_cache)} items to persistent cache")
                
        except Exception as e:
            self.logger.error(f"Failed to save persistent cache: {e}")
    
    def _start_cleanup_daemon(self):
        """Start background thread for cache cleanup and maintenance"""
        def cleanup_task():
            while True:
                try:
                    self._cleanup_expired_cache()
                    self._cleanup_old_backups()
                    self._save_persistent_cache()
                    time.sleep(300)  # Run every 5 minutes
                except Exception as e:
                    self.logger.error(f"Cleanup task error: {e}")
                    time.sleep(60)  # Retry in 1 minute on error
        
        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
        cleanup_thread.start()
        self.logger.info("Background cleanup daemon started")
    
    def _cleanup_expired_cache(self):
        """Remove expired items from memory cache"""
        current_time = datetime.now()
        expired_keys = []
        
        with self._lock:
            for key, expiry_time in self.cache_ttl.items():
                if current_time > expiry_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                if key in self.cache_ttl:
                    del self.cache_ttl[key]
        
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired cache items")
    
    def _cleanup_old_backups(self):
        """Remove backup files older than 7 days"""
        backup_dir = self.base_path / "backups"
        cutoff_time = datetime.now() - timedelta(days=7)
        
        for backup_file in backup_dir.glob("*.json"):
            try:
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_time:
                    backup_file.unlink()
                    self.logger.info(f"Removed old backup: {backup_file.name}")
            except Exception as e:
                self.logger.error(f"Error cleaning backup {backup_file}: {e}")
    
    def _generate_checksum(self, data: Any) -> str:
        """Generate checksum for data integrity verification"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def set_cache(self, key: str, data: Any, ttl_hours: int = 24, category: str = "general") -> bool:
        """
        Store data in multi-tier cache system
        
        Args:
            key: Cache key
            data: Data to cache
            ttl_hours: Time to live in hours
            category: Data category for organization
            
        Returns:
            bool: Success status
        """
        try:
            with self._lock:
                # Add metadata
                cache_data = {
                    'data': data,
                    'created_at': datetime.now().isoformat(),
                    'category': category,
                    'checksum': self._generate_checksum(data),
                    'access_count': 0
                }
                
                # Store in memory cache
                full_key = f"{category}:{key}"
                self.memory_cache[full_key] = cache_data
                self.cache_ttl[full_key] = datetime.now() + timedelta(hours=ttl_hours)
                
                # Store in database if enabled
                if self.enable_db:
                    self._store_in_database(key, data, category)
                
                self.logger.info(f"Cached {full_key} with {ttl_hours}h TTL")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to cache {key}: {e}")
            return False
    
    def get_cache(self, key: str, category: str = "general") -> Optional[Any]:
        """
        Retrieve data from cache with automatic fallback
        
        Args:
            key: Cache key
            category: Data category
            
        Returns:
            Cached data or None if not found/expired
        """
        try:
            full_key = f"{category}:{key}"
            current_time = datetime.now()
            
            # Check memory cache first
            with self._lock:
                if full_key in self.memory_cache and full_key in self.cache_ttl:
                    if current_time <= self.cache_ttl[full_key]:
                        cache_data = self.memory_cache[full_key]
                        cache_data['access_count'] += 1
                        cache_data['last_accessed'] = current_time.isoformat()
                        
                        # Verify data integrity
                        if self._verify_checksum(cache_data):
                            self.logger.info(f"Cache hit: {full_key}")
                            return cache_data['data']
                        else:
                            self.logger.warning(f"Checksum mismatch for {full_key}, removing from cache")
                            del self.memory_cache[full_key]
                            del self.cache_ttl[full_key]
            
            # Fallback to database
            if self.enable_db:
                db_data = self._retrieve_from_database(key, category)
                if db_data:
                    # Restore to memory cache
                    self.set_cache(key, db_data, ttl_hours=1, category=category)
                    return db_data
            
            self.logger.info(f"Cache miss: {full_key}")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve cache {key}: {e}")
            return None
    
    def _verify_checksum(self, cache_data: Dict) -> bool:
        """Verify data integrity using checksum"""
        try:
            stored_checksum = cache_data.get('checksum')
            current_checksum = self._generate_checksum(cache_data['data'])
            return stored_checksum == current_checksum
        except:
            return False
    
    def _store_in_database(self, key: str, data: Any, category: str):
        """Store data in SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract market data fields if applicable
                if isinstance(data, dict):
                    price = data.get('price_usd') or data.get('current_price')
                    change_24h = data.get('change_24h')
                    market_cap = data.get('market_cap_usd')
                    source = data.get('source', 'Unknown')
                else:
                    price = change_24h = market_cap = None
                    source = 'Unknown'
                
                cursor.execute('''
                    INSERT OR REPLACE INTO market_data 
                    (symbol, data_type, timestamp, price, change_24h, market_cap, raw_data, source, checksum)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    key, category, datetime.now(), price, change_24h, market_cap,
                    json.dumps(data, default=str), source, self._generate_checksum(data)
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Database storage failed for {key}: {e}")
    
    def _retrieve_from_database(self, key: str, category: str) -> Optional[Any]:
        """Retrieve data from SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT raw_data, checksum FROM market_data 
                    WHERE symbol = ? AND data_type = ?
                    ORDER BY timestamp DESC LIMIT 1
                ''', (key, category))
                
                result = cursor.fetchone()
                if result:
                    raw_data, stored_checksum = result
                    data = json.loads(raw_data)
                    
                    # Verify integrity
                    if self._generate_checksum(data) == stored_checksum:
                        return data
                    else:
                        self.logger.warning(f"Database checksum mismatch for {key}")
                
        except Exception as e:
            self.logger.error(f"Database retrieval failed for {key}: {e}")
        
        return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            with self._lock:
                total_items = len(self.memory_cache)
                categories = {}
                total_size = 0
                
                for key, data in self.memory_cache.items():
                    category = key.split(':', 1)[0]
                    categories[category] = categories.get(category, 0) + 1
                    
                    # Estimate size
                    try:
                        size = len(json.dumps(data, default=str))
                        total_size += size
                    except:
                        pass
                
                # Check database stats if enabled
                db_stats = {}
                if self.enable_db:
                    try:
                        with sqlite3.connect(self.db_path) as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT COUNT(*) FROM market_data")
                            db_stats['total_records'] = cursor.fetchone()[0]
                            
                            cursor.execute("SELECT data_type, COUNT(*) FROM market_data GROUP BY data_type")
                            db_stats['by_category'] = dict(cursor.fetchall())
                    except:
                        db_stats = {'error': 'Database unavailable'}
                
                return {
                    'memory_cache': {
                        'total_items': total_items,
                        'categories': categories,
                        'estimated_size_bytes': total_size,
                        'estimated_size_mb': round(total_size / (1024 * 1024), 2)
                    },
                    'database': db_stats,
                    'cache_file_exists': (self.base_path / "cache" / "persistent_cache.json").exists(),
                    'backup_count': len(list((self.base_path / "backups").glob("*.json")))
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get cache stats: {e}")
            return {'error': str(e)}
    
    def clear_cache(self, category: Optional[str] = None) -> bool:
        """
        Clear cache data
        
        Args:
            category: If specified, only clear items from this category
            
        Returns:
            bool: Success status
        """
        try:
            with self._lock:
                if category:
                    # Clear specific category
                    keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(f"{category}:")]
                    for key in keys_to_remove:
                        del self.memory_cache[key]
                        if key in self.cache_ttl:
                            del self.cache_ttl[key]
                    
                    self.logger.info(f"Cleared {len(keys_to_remove)} items from category {category}")
                else:
                    # Clear all
                    count = len(self.memory_cache)
                    self.memory_cache.clear()
                    self.cache_ttl.clear()
                    
                    self.logger.info(f"Cleared all {count} cache items")
                
                # Save changes
                self._save_persistent_cache()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return False
    
    def backup_data(self, backup_name: Optional[str] = None) -> str:
        """
        Create a comprehensive data backup
        
        Args:
            backup_name: Custom backup name (optional)
            
        Returns:
            str: Backup file path
        """
        try:
            if not backup_name:
                backup_name = f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_file = self.base_path / "backups" / f"{backup_name}.json"
            
            backup_data = {
                'created_at': datetime.now().isoformat(),
                'memory_cache': self.memory_cache,
                'cache_ttl': {k: v.isoformat() for k, v in self.cache_ttl.items()},
                'stats': self.get_cache_stats()
            }
            
            # Include database export if available
            if self.enable_db:
                backup_data['database_export'] = self._export_database()
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            self.logger.info(f"Created backup: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            raise
    
    def _export_database(self) -> Dict:
        """Export database data for backup"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Export market data
                market_df = pd.read_sql_query("SELECT * FROM market_data", conn)
                
                # Export metadata
                metadata_df = pd.read_sql_query("SELECT * FROM cache_metadata", conn)
                
                return {
                    'market_data': market_df.to_dict('records'),
                    'cache_metadata': metadata_df.to_dict('records'),
                    'exported_at': datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Database export failed: {e}")
            return {'error': str(e)}
    
    def restore_backup(self, backup_file: str) -> bool:
        """
        Restore data from backup
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            bool: Success status
        """
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            with self._lock:
                # Restore memory cache
                self.memory_cache = backup_data.get('memory_cache', {})
                ttl_data = backup_data.get('cache_ttl', {})
                self.cache_ttl = {k: datetime.fromisoformat(v) for k, v in ttl_data.items()}
                
                # Save restored data
                self._save_persistent_cache()
            
            self.logger.info(f"Restored data from backup: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup restoration failed: {e}")
            return False
    
    def optimize_storage(self) -> Dict[str, Any]:
        """
        Optimize storage by removing redundant data and compacting files
        
        Returns:
            Dict with optimization results
        """
        try:
            results = {
                'start_time': datetime.now().isoformat(),
                'actions_taken': [],
                'space_saved_bytes': 0,
                'errors': []
            }
            
            # Clean expired cache
            initial_count = len(self.memory_cache)
            self._cleanup_expired_cache()
            cleaned_count = initial_count - len(self.memory_cache)
            
            if cleaned_count > 0:
                results['actions_taken'].append(f"Removed {cleaned_count} expired cache items")
            
            # Optimize database
            if self.enable_db:
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        # Remove duplicate entries
                        cursor = conn.cursor()
                        cursor.execute('''
                            DELETE FROM market_data 
                            WHERE id NOT IN (
                                SELECT MAX(id) 
                                FROM market_data 
                                GROUP BY symbol, data_type, DATE(timestamp)
                            )
                        ''')
                        
                        duplicates_removed = cursor.rowcount
                        if duplicates_removed > 0:
                            results['actions_taken'].append(f"Removed {duplicates_removed} duplicate database records")
                        
                        # Vacuum database
                        cursor.execute("VACUUM")
                        results['actions_taken'].append("Database vacuumed")
                        
                        conn.commit()
                        
                except Exception as e:
                    results['errors'].append(f"Database optimization error: {e}")
            
            # Clean old backups
            initial_backups = len(list((self.base_path / "backups").glob("*.json")))
            self._cleanup_old_backups()
            final_backups = len(list((self.base_path / "backups").glob("*.json")))
            
            if final_backups < initial_backups:
                results['actions_taken'].append(f"Removed {initial_backups - final_backups} old backup files")
            
            # Save optimized cache
            self._save_persistent_cache()
            results['actions_taken'].append("Persistent cache saved")
            
            results['end_time'] = datetime.now().isoformat()
            results['success'] = len(results['errors']) == 0
            
            self.logger.info(f"Storage optimization completed: {len(results['actions_taken'])} actions taken")
            return results
            
        except Exception as e:
            self.logger.error(f"Storage optimization failed: {e}")
            return {'success': False, 'error': str(e)}

# Global instance for easy access
_global_data_manager = None

def get_data_manager() -> EnhancedDataManager:
    """Get global data manager instance"""
    global _global_data_manager
    if _global_data_manager is None:
        _global_data_manager = EnhancedDataManager()
    return _global_data_manager 