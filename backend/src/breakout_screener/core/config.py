"""
Configuration management for Breakout Screener V2
Environment-based configuration using python-dotenv with security validation
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConfigurationError(Exception):
    """Raised when required configuration is missing"""
    pass


def get_required_env(key: str, error_msg: str = None) -> str:
    """Get required environment variable or raise error"""
    value = os.getenv(key)
    if value is None:
        msg = error_msg or f"Required environment variable '{key}' is not set"
        raise ConfigurationError(msg)
    return value


def get_optional_env(key: str, default: str = None) -> str | None:
    """Get optional environment variable with default"""
    return os.getenv(key, default)


def get_bool_env(key: str, default: bool = False) -> bool:
    """Get boolean environment variable"""
    return os.getenv(key, str(default)).lower() in ("true", "1", "yes")


def get_int_env(key: str, default: int = None) -> int:
    """Get integer environment variable"""
    value = os.getenv(key)
    if value is None:
        if default is None:
            raise ConfigurationError(f"Required environment variable '{key}' is not set")
        return default
    try:
        return int(value)
    except ValueError:
        raise ConfigurationError(f"Environment variable '{key}' must be an integer, got: {value}")


def get_float_env(key: str, default: float = None) -> float:
    """Get float environment variable"""
    value = os.getenv(key)
    if value is None:
        if default is None:
            raise ConfigurationError(f"Required environment variable '{key}' is not set")
        return default
    try:
        return float(value)
    except ValueError:
        raise ConfigurationError(f"Environment variable '{key}' must be a float, got: {value}")


class Config:
    """Base configuration class with environment variables"""

    # Application Settings
    PROJECT_NAME: str = get_optional_env("PROJECT_NAME", "Breakout Screener V2")
    VERSION: str = get_optional_env("VERSION", "2.0.0")
    DEBUG: bool = get_bool_env("DEBUG", False)
    TESTING: bool = get_bool_env("TESTING", False)
    ENVIRONMENT: str = get_optional_env("ENVIRONMENT", "development")

    # API Configuration - SECRET_KEY is required for security
    API_V1_STR: str = get_optional_env("API_V1_STR", "/api/v1")
    SECRET_KEY: str = get_required_env("SECRET_KEY", "SECRET_KEY must be set for security")
    ALGORITHM: str = get_optional_env("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = get_int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 30)

    # Database Configuration - All required for security
    DATABASE_HOST: str = get_required_env("DATABASE_HOST", "DATABASE_HOST is required")
    DATABASE_PORT: int = get_int_env("DATABASE_PORT", 5432)
    DATABASE_USER: str = get_required_env("DATABASE_USER", "DATABASE_USER is required")
    DATABASE_PASSWORD: str = get_required_env("DATABASE_PASSWORD", "DATABASE_PASSWORD is required")
    DATABASE_NAME: str = get_required_env("DATABASE_NAME", "DATABASE_NAME is required")

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components"""
        return get_optional_env(
            "DATABASE_URL",
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    # Redis Configuration
    REDIS_HOST: str = get_required_env("REDIS_HOST", "REDIS_HOST is required")
    REDIS_PORT: int = get_int_env("REDIS_PORT", 6379)
    REDIS_DB: int = get_int_env("REDIS_DB", 0)
    REDIS_PASSWORD: str | None = get_optional_env("REDIS_PASSWORD")

    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL from components"""
        return get_optional_env(
            "REDIS_URL",
            f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        )

    # Celery Configuration
    @property
    def CELERY_BROKER_URL(self) -> str:
        """Construct Celery broker URL"""
        return get_optional_env(
            "CELERY_BROKER_URL",
            f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"
        )

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        """Construct Celery result backend URL"""
        return get_optional_env(
            "CELERY_RESULT_BACKEND",
            f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/2"
        )

    # External APIs Configuration
    NSE_BASE_URL: str = get_optional_env("NSE_BASE_URL", "https://www.nseindia.com")
    NSE_TIMEOUT: int = get_int_env("NSE_TIMEOUT", 30)
    MAX_RETRIES: int = get_int_env("MAX_RETRIES", 3)

    # NSE Market Data URLs
    NSE_URL_NIFTY_50: str = get_optional_env(
        "NSE_URL_NIFTY_50",
        "https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%2050"
    )
    NSE_URL_NIFTY_200: str = get_optional_env(
        "NSE_URL_NIFTY_200",
        "https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%20200"
    )
    NSE_URL_NIFTY_MIDCAP_150: str = get_optional_env(
        "NSE_URL_NIFTY_MIDCAP_150",
        "https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%20MIDCAP%20150"
    )
    NSE_URL_NIFTY_MIDSMALLCAP_400: str = get_optional_env(
        "NSE_URL_NIFTY_MIDSMALLCAP_400",
        "https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%20MIDSMALLCAP%20400"
    )
    NSE_URL_NIFTY_SMALLCAP_250: str = get_optional_env(
        "NSE_URL_NIFTY_SMALLCAP_250",
        "https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%20SMALLCAP%20250"
    )

    # YFinance Configuration
    YFIN_HIST_URL: str = get_optional_env(
        "YFIN_HIST_URL",
        "https://query1.finance.yahoo.com/v7/finance/download"
    )

    # Logging Configuration
    LOG_LEVEL: str = get_optional_env("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5

    # Monitoring Configuration
    SENTRY_DSN: str | None = get_optional_env("SENTRY_DSN")
    SENTRY_TRACES_SAMPLE_RATE: float = get_float_env("SENTRY_TRACES_SAMPLE_RATE", 0.1)

    # Performance Configuration
    CONNECTION_POOL_SIZE: int = get_int_env("CONNECTION_POOL_SIZE", 20)
    CONNECTION_POOL_MAX_OVERFLOW: int = get_int_env("CONNECTION_POOL_MAX_OVERFLOW", 0)
    CONNECTION_POOL_TIMEOUT: int = get_int_env("CONNECTION_POOL_TIMEOUT", 30)
    CONNECTION_POOL_RECYCLE: int = get_int_env("CONNECTION_POOL_RECYCLE", 3600)

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = get_int_env("RATE_LIMIT_PER_MINUTE", 100)
    RATE_LIMIT_BURST: int = get_int_env("RATE_LIMIT_BURST", 200)

    # Caching Configuration
    CACHE_TTL_DEFAULT: int = get_int_env("CACHE_TTL_DEFAULT", 300)  # 5 minutes
    CACHE_TTL_STOCK_DATA: int = get_int_env("CACHE_TTL_STOCK_DATA", 60)  # 1 minute
    CACHE_TTL_ANALYSIS: int = get_int_env("CACHE_TTL_ANALYSIS", 600)  # 10 minutes

    # Security Configuration
    @property
    def ALLOWED_HOSTS(self) -> list[str]:
        """Get allowed hosts from environment"""
        hosts = get_optional_env("ALLOWED_HOSTS", "*")
        return [host.strip() for host in hosts.split(",")]

    # Development Configuration
    RELOAD: bool = get_bool_env("RELOAD", False)

    # Frontend Configuration
    NEXT_PUBLIC_API_URL: str = get_optional_env("NEXT_PUBLIC_API_URL", "http://localhost:8000")
    NEXT_PUBLIC_APP_NAME: str = get_optional_env("NEXT_PUBLIC_APP_NAME", "Breakout Screener V2")
    NEXT_PUBLIC_APP_VERSION: str = get_optional_env("NEXT_PUBLIC_APP_VERSION", "2.0.0")

    # Node Environment
    NODE_ENV: str = get_optional_env("NODE_ENV", "development")

    @classmethod
    def get_cors_origins(cls) -> list[str]:
        """Get CORS origins based on environment"""
        if cls.ENVIRONMENT == "production":
            return [
                "https://breakoutscreener.com",
                "https://www.breakoutscreener.com"
            ]
        elif cls.ENVIRONMENT == "staging":
            return [
                "https://staging.breakoutscreener.com"
            ]
        else:
            # Development
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
                cls.NEXT_PUBLIC_API_URL
            ]

    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return cls.ENVIRONMENT.lower() == "development"

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENVIRONMENT.lower() == "production"

    @classmethod
    def is_testing(cls) -> bool:
        """Check if running in testing mode"""
        return cls.TESTING

    @classmethod
    def validate_config(cls) -> None:
        """Validate critical configuration"""
        try:
            # Test database URL construction
            _ = cls.DATABASE_URL

            # Test Redis URL construction
            _ = cls.REDIS_URL

            # Test Celery URLs construction
            _ = cls.CELERY_BROKER_URL
            _ = cls.CELERY_RESULT_BACKEND

            # Validate log level
            valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if cls.LOG_LEVEL not in valid_log_levels:
                raise ConfigurationError(f"LOG_LEVEL must be one of {valid_log_levels}, got: {cls.LOG_LEVEL}")

            # Validate environment
            valid_environments = ["development", "staging", "production"]
            if cls.ENVIRONMENT.lower() not in valid_environments:
                raise ConfigurationError(f"ENVIRONMENT must be one of {valid_environments}, got: {cls.ENVIRONMENT}")

        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {str(e)}")


def get_config() -> Config:
    """Factory function to get configuration and validate it"""
    config = Config()
    config.validate_config()
    return config


# Global configuration instance
config = get_config()
