"""
Redis connection management and utilities for Breakout Screener V2
"""

import json
from typing import Any, Optional, Union
import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import RedisError

from .config import config
from .logging import get_logger

logger = get_logger(__name__)


class RedisManager:
    """Redis connection manager with connection pooling"""
    
    def __init__(self):
        self._pool: Optional[ConnectionPool] = None
        self._redis: Optional[Redis] = None
    
    async def initialize(self) -> None:
        """Initialize Redis connection pool"""
        try:
            # Parse Redis URL to get connection parameters
            url_parts = config.REDIS_URL.replace('redis://', '').split('/')
            host_port = url_parts[0].split(':')
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 6379
            db = int(url_parts[1]) if len(url_parts) > 1 else 0
            
            # Create connection pool
            self._pool = ConnectionPool(
                host=host,
                port=port,
                db=db,
                password=config.REDIS_PASSWORD,
                encoding='utf-8',
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                health_check_interval=30
            )
            
            # Create Redis client
            self._redis = Redis(connection_pool=self._pool)
            
            # Test connection
            await self._redis.ping()
            logger.info("Redis connection initialized successfully", 
                       host=host, port=port, db=db)
            
        except Exception as e:
            logger.error("Failed to initialize Redis connection", error=str(e))
            raise
    
    async def close(self) -> None:
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")
    
    @property
    def redis(self) -> Redis:
        """Get Redis client instance"""
        if self._redis is None:
            raise RuntimeError("Redis not initialized. Call initialize() first.")
        return self._redis
    
    async def health_check(self) -> bool:
        """Check Redis connection health"""
        try:
            await self.redis.ping()
            return True
        except RedisError:
            return False


# Global Redis manager instance
redis_manager = RedisManager()


async def get_redis() -> Redis:
    """Get Redis client instance"""
    return redis_manager.redis


class CacheManager:
    """High-level cache management with JSON serialization"""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        try:
            serialized_value = json.dumps(value, default=str)
            result = await self.redis.set(key, serialized_value, ex=ttl)
            logger.debug("Cache set", key=key, ttl=ttl)
            return result
        except Exception as e:
            logger.error("Cache set failed", key=key, error=str(e))
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            
            result = json.loads(value)
            logger.debug("Cache hit", key=key)
            return result
        except json.JSONDecodeError:
            logger.error("Cache value is not valid JSON", key=key)
            await self.delete(key)  # Remove corrupted data
            return None
        except Exception as e:
            logger.error("Cache get failed", key=key, error=str(e))
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            result = await self.redis.delete(key)
            logger.debug("Cache delete", key=key)
            return bool(result)
        except Exception as e:
            logger.error("Cache delete failed", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            result = await self.redis.exists(key)
            return bool(result)
        except Exception as e:
            logger.error("Cache exists check failed", key=key, error=str(e))
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key"""
        try:
            result = await self.redis.expire(key, ttl)
            logger.debug("Cache expire set", key=key, ttl=ttl)
            return bool(result)
        except Exception as e:
            logger.error("Cache expire failed", key=key, error=str(e))
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value"""
        try:
            result = await self.redis.incrby(key, amount)
            logger.debug("Cache increment", key=key, amount=amount, new_value=result)
            return result
        except Exception as e:
            logger.error("Cache increment failed", key=key, error=str(e))
            return None
    
    async def set_hash(self, key: str, mapping: dict, ttl: Optional[int] = None) -> bool:
        """Set hash value in cache"""
        try:
            # Serialize all values in the mapping
            serialized_mapping = {k: json.dumps(v, default=str) for k, v in mapping.items()}
            
            result = await self.redis.hset(key, mapping=serialized_mapping)
            if ttl:
                await self.redis.expire(key, ttl)
            
            logger.debug("Cache hash set", key=key, fields=len(mapping), ttl=ttl)
            return bool(result)
        except Exception as e:
            logger.error("Cache hash set failed", key=key, error=str(e))
            return False
    
    async def get_hash(self, key: str) -> Optional[dict]:
        """Get hash value from cache"""
        try:
            result = await self.redis.hgetall(key)
            if not result:
                return None
            
            # Deserialize all values
            deserialized = {}
            for k, v in result.items():
                try:
                    deserialized[k] = json.loads(v)
                except json.JSONDecodeError:
                    deserialized[k] = v  # Keep as string if not JSON
            
            logger.debug("Cache hash hit", key=key, fields=len(deserialized))
            return deserialized
        except Exception as e:
            logger.error("Cache hash get failed", key=key, error=str(e))
            return None
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                result = await self.redis.delete(*keys)
                logger.info("Cache pattern cleared", pattern=pattern, count=result)
                return result
            return 0
        except Exception as e:
            logger.error("Cache pattern clear failed", pattern=pattern, error=str(e))
            return 0


async def get_cache() -> CacheManager:
    """Get cache manager instance"""
    redis_client = await get_redis()
    return CacheManager(redis_client)


# Cache key generators
class CacheKeys:
    """Cache key generators for consistent naming"""
    
    @staticmethod
    def stock_data(symbol: str, date: str) -> str:
        """Generate cache key for stock data"""
        return f"stock_data:{symbol}:{date}"
    
    @staticmethod
    def breakout_analysis(symbol: str, date: str) -> str:
        """Generate cache key for breakout analysis"""
        return f"breakout_analysis:{symbol}:{date}"
    
    @staticmethod
    def stock_list(group: str) -> str:
        """Generate cache key for stock list"""
        return f"stock_list:{group}"
    
    @staticmethod
    def nse_data(symbol: str) -> str:
        """Generate cache key for NSE data"""
        return f"nse_data:{symbol}"
    
    @staticmethod
    def user_session(user_id: str) -> str:
        """Generate cache key for user session"""
        return f"user_session:{user_id}"
    
    @staticmethod
    def rate_limit(identifier: str) -> str:
        """Generate cache key for rate limiting"""
        return f"rate_limit:{identifier}"
    
    @staticmethod
    def api_response(endpoint: str, params: str) -> str:
        """Generate cache key for API response"""
        return f"api_response:{endpoint}:{params}"