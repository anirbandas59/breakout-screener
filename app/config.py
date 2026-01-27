# import os
import logging
# from pydantic import ValidationError
from pydantic_settings import BaseSettings
# from dotenv import load_dotenv


class Settings(BaseSettings):
    """
    Configuration class
    """

    # App configurations
    app_hostname: str
    app_port: int
    react_port: int

    # Database configuration
    database_url: str

    # NSE URLs
    nse_url_nifty_50: str
    nse_url_nifty_200: str
    nse_url_nifty_midcap_150: str
    nse_url_nifty_midsmallcap_400: str
    nse_url_nifty_smallcap_250: str

    # YFinance URLs
    yfin_hist_url: str

    # Redis configuration
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str

    # Timezone
    app_timezone: str

    @property
    def nse_urls(self) -> list[str]:
        """Returns a list"""
        return [
            self.nse_url_nifty_50,
            self.nse_url_nifty_200,
            self.nse_url_nifty_midcap_150,
            self.nse_url_nifty_midsmallcap_400,
            self.nse_url_nifty_smallcap_250,
        ]

    def get_safe_config(self) -> dict:
        """
        Return configuration with sensitive fields masked.
        Use this for logging instead of model_dump() to prevent credential exposure.

        Returns:
            dict: Configuration dictionary with passwords masked as '***'
        """
        config = self.model_dump()

        # Mask sensitive fields
        sensitive_fields = ['database_url', 'celery_broker_url', 'celery_result_backend', 'redis_url']
        for field in sensitive_fields:
            if field in config and config[field]:
                config[field] = self._mask_connection_string(config[field])

        return config

    @staticmethod
    def _mask_connection_string(url: str) -> str:
        """
        Mask password in connection string.

        Examples:
            postgresql://user:password@host/db -> postgresql://user:***@host/db
            redis://localhost:6379/0 -> redis://localhost:6379/0 (no password)

        Args:
            url: Connection string URL

        Returns:
            str: URL with masked password
        """
        import re
        # Pattern matches: ://username:password@
        # Group 1: ://username:
        # Group 2: password
        # Group 3: @
        pattern = r'(://[^:]+:)([^@]+)(@)'
        return re.sub(pattern, r'\1***\3', url)

    class Config:
        env_file = ".env"


# Instantiate settings
settings = Settings()

<<<<<<< HEAD
# Filter out sensitive fields before logging
_safe_settings = {
    k: v for k, v in settings.model_dump().items()
    if not any(sensitive in k.lower() for sensitive in ['password', 'secret', 'url'])
}
logging.info("Environment variables loaded successfully. %s", _safe_settings)
=======
# SECURITY FIX: Use safe config to prevent credential exposure in logs
safe_config = settings.get_safe_config()
logging.info("Environment variables loaded successfully. %s", safe_config)
print("Configuration loaded:", safe_config)
# print(settings.nse_urls)
>>>>>>> 05941eb (Implement critical performance optimizations and security hardening)
# except ValidationError as e:
# try:
#     logging.error("Error loading environment variables: %s", str(e))
#     print(repr(e.errors()[0]))


# Configure logging
LOG_FILE = "app/logs/app_logs.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
