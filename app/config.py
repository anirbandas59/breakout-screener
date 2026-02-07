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

    class Config:
        env_file = ".env"


# Instantiate settings
settings = Settings()

# Filter out sensitive fields before logging
_safe_settings = {
    k: v for k, v in settings.model_dump().items()
    if not any(sensitive in k.lower() for sensitive in ['password', 'secret', 'url'])
}
logging.info("Environment variables loaded successfully. %s", _safe_settings)
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
