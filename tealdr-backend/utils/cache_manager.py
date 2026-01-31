import time
from collections import OrderedDict
from datetime import datetime, timedelta
from utils.logger import get_logger
import hashlib
import json

logger = get_logger(__name__)

class CacheManager:
    """In-memory cache with TTL (Time To Live) for embeddings and responses."""
    
    def __init__(self):
        self.embedding_cache = OrderedDict()
        self.response_cache = OrderedDict()
        self.stats_cache = OrderedDict()
        
        # Cache settings
        self.embedding_ttl = 3600  # 1 hour
        self.response_ttl = 1800   # 30 minutes
        self.stats_ttl = 300       # 5 minutes
        
        # Max cache sizes
        self.max_embedding_cache = 1000
        self.max_response_cache = 500
        self.max_stats_cache = 100
        
        # Statistics
        self.hits = 0
        self.misses = 0
        
        logger.info("Cache manager initialized")
    
    def _generate_key(self, data):
        """Generate a cache key from data."""
        if isinstance(data, str):
            return hashlib.md5(data.encode()).hexdigest()
        else:
            return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def _is_expired(self, timestamp, ttl):
        """Check if cache entry is expired."""
        return time.time() - timestamp > ttl
    
    def _cleanup_cache(self, cache, max_size):
        """Remove oldest entries if cache exceeds max size."""
        while len(cache) > max_size:
            cache.popitem(last=False)  # Remove oldest (FIFO)
    
    # Embedding cache methods
    def get_embedding(self, text):
        """Get cached embedding for text."""
        key = self._generate_key(text)
        
        if key in self.embedding_cache:
            entry = self.embedding_cache[key]
            
            if not self._is_expired(entry['timestamp'], self.embedding_ttl):
                self.hits += 1
                logger.debug(f"Embedding cache HIT for key: {key[:8]}...")
                return entry['embedding']
            else:
                # Expired, remove it
                del self.embedding_cache[key]
        
        self.misses += 1
        logger.debug(f"Embedding cache MISS for key: {key[:8]}...")
        return None
    
    def set_embedding(self, text, embedding):
        """Cache an embedding."""
        key = self._generate_key(text)
        
        self.embedding_cache[key] = {
            'embedding': embedding,
            'timestamp': time.time()
        }
        
        self._cleanup_cache(self.embedding_cache, self.max_embedding_cache)
        logger.debug(f"Cached embedding for key: {key[:8]}...")
    
    # Response cache methods
    def get_response(self, prompt):
        """Get cached AI response for prompt."""
        key = self._generate_key(prompt)
        
        if key in self.response_cache:
            entry = self.response_cache[key]
            
            if not self._is_expired(entry['timestamp'], self.response_ttl):
                self.hits += 1
                logger.debug(f"Response cache HIT for key: {key[:8]}...")
                return entry['response']
            else:
                del self.response_cache[key]
        
        self.misses += 1
        logger.debug(f"Response cache MISS for key: {key[:8]}...")
        return None
    
    def set_response(self, prompt, response):
        """Cache an AI response."""
        key = self._generate_key(prompt)
        
        self.response_cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
        
        self._cleanup_cache(self.response_cache, self.max_response_cache)
        logger.debug(f"Cached response for key: {key[:8]}...")
    
    # Stats cache methods
    def get_stats(self, stats_key):
        """Get cached statistics."""
        if stats_key in self.stats_cache:
            entry = self.stats_cache[stats_key]
            
            if not self._is_expired(entry['timestamp'], self.stats_ttl):
                self.hits += 1
                logger.debug(f"Stats cache HIT for key: {stats_key}")
                return entry['data']
            else:
                del self.stats_cache[stats_key]
        
        self.misses += 1
        logger.debug(f"Stats cache MISS for key: {stats_key}")
        return None
    
    def set_stats(self, stats_key, data):
        """Cache statistics data."""
        self.stats_cache[stats_key] = {
            'data': data,
            'timestamp': time.time()
        }
        
        self._cleanup_cache(self.stats_cache, self.max_stats_cache)
        logger.debug(f"Cached stats for key: {stats_key}")
    
    # Cache management
    def clear_all(self):
        """Clear all caches."""
        self.embedding_cache.clear()
        self.response_cache.clear()
        self.stats_cache.clear()
        logger.info("All caches cleared")
    
    def clear_expired(self):
        """Remove all expired entries from caches."""
        # Clear expired embeddings
        expired_keys = [
            key for key, entry in self.embedding_cache.items()
            if self._is_expired(entry['timestamp'], self.embedding_ttl)
        ]
        for key in expired_keys:
            del self.embedding_cache[key]
        
        # Clear expired responses
        expired_keys = [
            key for key, entry in self.response_cache.items()
            if self._is_expired(entry['timestamp'], self.response_ttl)
        ]
        for key in expired_keys:
            del self.response_cache[key]
        
        # Clear expired stats
        expired_keys = [
            key for key, entry in self.stats_cache.items()
            if self._is_expired(entry['timestamp'], self.stats_ttl)
        ]
        for key in expired_keys:
            del self.stats_cache[key]
        
        logger.info(f"Cleared {len(expired_keys)} expired cache entries")
    
    def get_stats_summary(self):
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'embedding_cache_size': len(self.embedding_cache),
            'response_cache_size': len(self.response_cache),
            'stats_cache_size': len(self.stats_cache)
        }
    
    def get_memory_usage(self):
        """Estimate memory usage of caches."""
        import sys
        
        embedding_size = sys.getsizeof(self.embedding_cache)
        response_size = sys.getsizeof(self.response_cache)
        stats_size = sys.getsizeof(self.stats_cache)
        
        total_mb = (embedding_size + response_size + stats_size) / (1024 * 1024)
        
        return {
            'embedding_cache_mb': embedding_size / (1024 * 1024),
            'response_cache_mb': response_size / (1024 * 1024),
            'stats_cache_mb': stats_size / (1024 * 1024),
            'total_mb': total_mb
        }

# Global cache instance
cache_manager = CacheManager()
