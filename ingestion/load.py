import duckdb
import json
import os
import pendulum
from dotenv import load_dotenv
from pathlib import Path
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / os.getenv('DATA_DIR','data') / "raw"
DB_PATH = PROJECT_ROOT / os.getenv('DATA_DIR','data') / "apiFootball.duckdb"

def load_api_football_data(conn: duckdb.DuckDBPyConnection, file_name:str="leagues_2026-08-19_20-01-24.json"):
    file_path = DATA_RAW_DIR / file_name
    
    logger.info("Loading file: %s", file_path)

    if not file_path.exists():
        logger.error("File %s does not exist", file_name)
        return
    
    with open(file_path) as f:
        raw = json.load(f)
        
    total_results = raw.get("results",0)
    logger.info(
        "API response contains %s results; loading raw response.",
        total_results,
    )
    
    conn.execute("CREATE SCHEMA IF NOT EXISTS raw_api_football")
    
    # Create raw ingestion table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_api_football.leagues(
            source_file VARCHAR NOT NULL,
            ingested_at TIMESTAMP NOT NULL,
            payload JSON NOT NULL
        )
    """)
    
    conn.sql("SELECT * FROM raw_api_football.leagues").show()
    
    conn.execute("DELETE FROM raw_api_football.leagues")
    
    conn.execute(
        "INSERT INTO raw_api_football.leagues VALUES(?, ?, ?)",
        [file_path.name, pendulum.now(tz="Europe/London").format("YYYY-MM-DD HH:MM:SS"),raw]
    )
    
    conn.sql("SELECT * FROM raw_api_football.leagues").show()
    
def ingest_into_staging_table(conn: duckdb.DuckDBPyConnection):
    row_count = conn.execute("SELECT COUNT(*) FROM raw_api_football.leagues").fetchone()
    
    if row_count[0] == 1:
        logger.info(f"Data ingested, proceeding to populate staging table.")
        
        conn.execute("CREATE SCHEMA IF NOT EXISTS stg_api_football")
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stg_api_football.leagues(
                league_id VARCHAR PRIMARY KEY,
                league_name VARCHAR,
                league_type VARCHAR,
                league_logo VARCHAR,
                country_name VARCHAR,
                country_code VARCHAR,
                country_flag VARCHAR
            )             
        """)
        
        data = conn.execute("""
            SELECT
                response -> 'league' ->> 'id' AS league_id,
                response -> 'league' ->> 'name' AS league_name,
                response -> 'league' ->> 'type' AS league_type,
                response -> 'league' ->> 'logo' AS league_logo,
                response -> 'country' ->> 'name' AS country_name,
                response -> 'country' ->> 'code' AS country_code,
                response -> 'country' ->> 'flag' AS country_flag
            FROM raw_api_football.leagues,
            UNNEST(
                JSON_EXTRACT(payload, '$.response')::JSON[]
            ) AS t(response); 
        """).fetchall()
        
        conn.executemany(
            "INSERT INTO stg_api_football.leagues VALUES(?, ?, ?, ?, ?, ?, ?)",
            data
        )
        
        conn.sql("SELECT * FROM stg_api_football.leagues").show()
    else:
        logger.error(f"Data not yet ingested or more than one row available in loading table.")
    
def main():
    conn = duckdb.connect(DB_PATH)
    
    # load_api_football_data(conn=conn)
    ingest_into_staging_table(conn=conn)
    
    conn.close()
    
if __name__ == "__main__":
    main()