import json
import os
import requests
from dotenv import load_dotenv
from utils.logger import get_logger

logger = get_logger(__name__)
load_dotenv

API_SPORTS_BASE_URL = os.getenv("API_SPORTS_BASE_URL","")

class ApiFootballClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = API_SPORTS_BASE_URL
        self.session = requests.Session()
        self.headers = {
            'x-apisports-key': api_key
        }
        self.payload = {}
        logger.info("ApiFootballClient initialized.")
        
    def get_leagues(self) -> json:
        url = f"{self.base_url}/leagues"
        
        logger.info("Fetching info about all football leagues")
        
        try:
            resp = self.session.get(url, headers=self.headers) 
           
            if resp.status_code != 200:
               logger.error(f"{resp.text}")
               raise e
               
            logger.info("Successfully fetched league data")
            
            return resp.json()
        except Exception as e:
            logger.error(e)