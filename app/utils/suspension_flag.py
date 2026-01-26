import redis
import logging
from app.config import settings

# Redis key for suspension flag
SUSPENSION_KEY = "breakout_screener:suspend_analysis"

# Redis client (lazy initialization)
_redis_client = None


def _get_redis_client():
    """Get or create Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url)
    return _redis_client


class SuspensionFlag:
    """
    Cross-process suspension flag using Redis.
    Provides an interface similar to threading.Event() for compatibility.
    """

    def set(self):
        """Set the suspension flag in Redis."""
        try:
            client = _get_redis_client()
            client.set(SUSPENSION_KEY, "1")
            logging.info("Suspension flag set in Redis.")
        except Exception as e:
            logging.error("Failed to set suspension flag in Redis: %s", str(e))
            raise

    def clear(self):
        """Clear the suspension flag in Redis."""
        try:
            client = _get_redis_client()
            client.delete(SUSPENSION_KEY)
            logging.info("Suspension flag cleared in Redis.")
        except Exception as e:
            logging.error("Failed to clear suspension flag in Redis: %s", str(e))
            raise

    def is_set(self):
        """Check if suspension flag is set in Redis."""
        try:
            client = _get_redis_client()
            value = client.get(SUSPENSION_KEY)
            return value is not None and value == b"1"
        except Exception as e:
            logging.error("Failed to check suspension flag in Redis: %s", str(e))
            return False


# Global suspension flag instance
SUSPEND_ANALYSIS = SuspensionFlag()
