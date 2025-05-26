import logging
import os
import requests
import json
import pandas as pd
from datetime import datetime
import pytz
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_folder(folder='data', create_if_missing=True):
    """
    Search for a specified folder and optionally create it if not found.
    Args:
        folder (str): Name of the folder to find (default: 'data')
        create_if_missing (bool): Whether to create folder if not found (default: True)
    Returns:
        Path: Path object of found or created folder
    """
    # Start from the script's directory
    current = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Search up the directory tree
    while current.parent != current:
        folders = list(current.glob(folder))
        if folders and any(f.is_dir() for f in folders):
            return folders[0]  # Return first found directory
        current = current.parent
        logger.info(f"Searching {folder} folder at: {current}")
    
    # If folder not found and create_if_missing is True, create in script directory
    if create_if_missing:
        current = Path(os.path.dirname(os.path.abspath(__file__)))
        parent_dir = current.parent
        data_dir = parent_dir / folder
        data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created new {folder} folder at: {data_dir}")
        return data_dir
    
    return current

def fetch_sgx_data():
    """Fetch Singapore market data from SGX API"""
    logger.info("Fetching SGX market data...")
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
    }
    
    try:
        req = requests.get(
            "https://api.sgx.com/securities/v1.1?",
            headers=HEADERS
        )
        
        if req.status_code != 200 or not req.text:
            logger.error(f"Failed to get valid response from SGX API: {req.status_code}")
            return None
        
        data_json = json.loads(req.text)
        df_sg = pd.json_normalize(data_json['data']['prices'])

        # Add timestamp
        df_sg['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df_sg['datetime_sg'] = datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S%z')
       
        logger.info(f"Retrieved spot info from SGX: {len(df_sg)} records")
        return df_sg
        
    except Exception as e:
        logger.error(f"Error fetching SGX data: {str(e)}")
        return None

def main():
    # Get root folder and data directory
    data_folder = find_folder('data')
    output_file = data_folder / 'sg_tickers_spot.csv'
    
    # Fetch SGX data
    df = fetch_sgx_data()
    
    if df is not None:
        # Save to CSV
        df.to_csv(output_file, index=False)
        logger.info(f"Data saved to {output_file}")
    else:
        logger.error("Failed to fetch SGX data")

    return df

if __name__ == "__main__":
    df = main()