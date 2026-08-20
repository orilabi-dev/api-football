from dotenv import load_dotenv
from ingestion.client import ApiFootballClient
from pathlib import Path
from utils.logger import get_logger
import json
import os
import pendulum

logger = get_logger(__name__)
load_dotenv()
api_key = os.getenv("API_SPORTS_KEY","")
data_dir = os.getenv("DATA_DIR","data")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / data_dir / "raw"

def main():
    if not api_key:
        logger.error("Please visit the base url to get your api key")
        return
        
    apiFootballClient = ApiFootballClient(api_key=api_key)
    
    data = apiFootballClient.get_leagues()
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = pendulum.now(tz="Europe/London").format("YYYY-MM-DD_HH-mm-ss")
    file_path = DATA_DIR / f"leagues_{timestamp}.json"
    
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
    
    logger.info("Leagues saved to %s", file_path)
    
if __name__ == "__main__":
    main()