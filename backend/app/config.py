import os
import logging
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    # Database configuration
    database_url: str

    # NSE URLs
    nse_url_nifty_50: str
    nse_url_nifty_200: str
    nse_url_nifty_midcap_150: str
    nse_url_nifty_midsmallcap_400: str
    nse_url_nifty_smallcap_250: str

    @property
    def nse_urls(self):
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
logging.basicConfig(level=logging.INFO)

logging.info(settings.nse_urls)

# Access variables
DATABASE_URL = os.getenv("DATABASE_URL")
NSE_URL = os.getenv("NSE_URL")
