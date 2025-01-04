import os
import logging
from pydantic import ValidationError
from pydantic_settings import BaseSettings
# from dotenv import load_dotenv


class Settings(BaseSettings):
    # App configurations
    app_hostname: str
    app_port: int

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

    @property
    def nse_urls(self) -> list[str]:
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
logging.info("Environment variables loaded successfully. %s",
             settings.model_dump())
# print(settings.model_dump())
# print(settings.nse_urls)
# except ValidationError as e:
# try:
#     logging.error("Error loading environment variables: %s", str(e))
#     print(repr(e.errors()[0]))


# Configure logging
LOG_FILE = "app_logs.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
