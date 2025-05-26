#%%
import os
import argparse
from pathlib import Path
import pandas as pd
from datetime import datetime
import pytz
import time
import requests
from finvizfinance.screener.overview import Overview
from finvizfinance.screener.valuation import Valuation
from finvizfinance.screener.financial import Financial
from finvizfinance.screener.ownership import Ownership

# Import the patch to modify finvizfinance behavior
try:
    from finviz_patch import *
    print("Using finviz patch with retry logic")
except ImportError:
    print("Finviz patch not found, using default settings")

class FinvizCollector:
    def __init__(self, data_folder='data'):
        self.data_folder = data_folder
        self.data_dir = str(self.find_folder(data_folder))
        self.dataframes = {}
        
    def find_folder(self, folder='data', create_if_missing=True):
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
            print(f"Searching {folder} folder at: {current}")
        
        # If folder not found and create_if_missing is True, create in script directory
        if create_if_missing:
            current = Path(os.path.dirname(os.path.abspath(__file__)))
            parent_dir = current.parent
            data_dir = parent_dir / folder
            data_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created new {folder} folder at: {data_dir}")
            return data_dir
        
        return current
    
    def collect_overview(self):
        """Collect overview data from finviz"""
        print("Downloading overview")
        try:
            df_screener_overview = Overview().screener_view(order='Market Cap.', ascend=False)
            eastern_time = datetime.now(pytz.timezone('America/New_York'))
            df_screener_overview['datetime'] = eastern_time.strftime('%Y-%m-%d %H:%M:%S')
            df_screener_overview.to_csv(f"{self.data_dir}/us_tickers_overview.csv", index=False)
            self.dataframes['overview'] = df_screener_overview
            return df_screener_overview
        except Exception as e:
            print(f"Error collecting overview data: {e}")
            raise
    
    def collect_valuation(self):
        """Collect valuation data from finviz"""
        print("Downloading valuation")
        try:
            df_screener_valuation = Valuation().screener_view(order='Market Cap.', ascend=False)
            eastern_time = datetime.now(pytz.timezone('America/New_York'))
            df_screener_valuation['datetime'] = eastern_time.strftime('%Y-%m-%d %H:%M:%S')
            df_screener_valuation.to_csv(f"{self.data_dir}/us_tickers_valuation.csv", index=False)
            self.dataframes['valuation'] = df_screener_valuation
            return df_screener_valuation
        except Exception as e:
            print(f"Error collecting valuation data: {e}")
            raise
    
    def collect_ownership(self):
        """Collect ownership data from finviz"""
        print("Downloading ownership")
        try:
            df_screener_ownership = Ownership().screener_view(order='Market Cap.', ascend=False)
            df_screener_ownership['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df_screener_ownership.to_csv(f"{self.data_dir}/us_tickers_ownership.csv", index=False)
            self.dataframes['ownership'] = df_screener_ownership
            return df_screener_ownership
        except Exception as e:
            print(f"Error collecting ownership data: {e}")
            raise
    
    def collect_financial(self):
        """Collect financial data from finviz"""
        print("Downloading financial")
        try:
            df_screener_financial = Financial().screener_view(order='Market Cap.', ascend=False)
            df_screener_financial['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df_screener_financial.to_csv(f"{self.data_dir}/us_tickers_financial.csv", index=False)
            self.dataframes['financial'] = df_screener_financial
            return df_screener_financial
        except Exception as e:
            print(f"Error collecting financial data: {e}")
            raise
    
    def merge_all_data(self):
        """Merge all collected dataframes into a single dataframe"""
        if not all(key in self.dataframes for key in ['overview', 'valuation', 'financial', 'ownership']):
            print("Not all data types have been collected. Collecting missing data...")
            if 'overview' not in self.dataframes:
                self.collect_overview()
            if 'valuation' not in self.dataframes:
                self.collect_valuation()
            if 'financial' not in self.dataframes:
                self.collect_financial()
            if 'ownership' not in self.dataframes:
                self.collect_ownership()
        
        # Create a base dataframe with the ticker column
        df_us = pd.DataFrame(columns=[self.dataframes['overview'].columns[0]])
        
        # Merge all dataframes
        for df_name, df in self.dataframes.items():
            df_us = df_us.merge(
                df,
                how='outer',
                on=self.dataframes['overview'].columns[0],
                suffixes=('', '__repeated')
            )
        
        # Add date and categorize by market cap
        df_us['date'] = pd.to_datetime(df_us['datetime'])
        df_us['date'] = df_us['date'].dt.date
        df_us['date'] = pd.to_datetime(df_us['date']).dt.tz_localize(pytz.timezone('America/New_York'))
        
        # Save the merged dataframe
        df_us.to_csv(f"{self.data_dir}/us_tickers.csv", index=False)
        print(f"Saved to {self.data_dir}/us_tickers.csv")
        return df_us
    
    def collect_all(self):
        """Collect all data types and merge them"""
        try:
            self.collect_overview()
            self.collect_valuation()
            self.collect_ownership()
            self.collect_financial()
            return self.merge_all_data()
        except Exception as e:
            print(f"Error in collect_all: {e}")
            # Try to save what we have so far
            if any(self.dataframes):
                print("Attempting to merge collected data so far...")
                return self.merge_all_data()
            raise

def main():
    parser = argparse.ArgumentParser(description='Collect US stock data from Finviz')
    parser.add_argument('--data-type', choices=['overview', 'valuation', 'ownership', 'financial', 'all'], 
                        default='all', help='Type of data to collect')
    parser.add_argument('--merge', action='store_true', help='Merge all data types into a single file')
    args = parser.parse_args()
    
    collector = FinvizCollector()
    
    if args.data_type == 'overview':
        collector.collect_overview()
    elif args.data_type == 'valuation':
        collector.collect_valuation()
    elif args.data_type == 'ownership':
        collector.collect_ownership()
    elif args.data_type == 'financial':
        collector.collect_financial()
    elif args.data_type == 'all':
        collector.collect_all()
    
    if args.merge:
        collector.merge_all_data()

if __name__ == "__main__":
    main()