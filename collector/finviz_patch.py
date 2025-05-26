"""
This module patches the finvizfinance library to increase timeout and add retry logic.
Import this before using finvizfinance.
"""
import time
from functools import wraps
import requests
from finvizfinance.util import web_scrap as original_web_scrap

# Store the original function
original_web_scrap_func = original_web_scrap

def web_scrap_with_retry(url, params=None, headers=None, timeout=30, max_retries=3, initial_delay=5):
    """
    Enhanced web_scrap function with retry logic
    
    Args:
        url (str): URL to scrape
        params (dict, optional): Request parameters
        headers (dict, optional): Request headers
        timeout (int): Request timeout in seconds
        max_retries (int): Maximum number of retries
        initial_delay (int): Initial delay between retries in seconds
        
    Returns:
        BeautifulSoup object
    """
    retries = 0
    last_exception = None
    
    while retries <= max_retries:
        try:
            return original_web_scrap_func(url, params, headers, timeout)
        except (requests.exceptions.Timeout, requests.exceptions.ReadTimeout) as e:
            last_exception = e
            retries += 1
            if retries > max_retries:
                print(f"Failed after {max_retries} retries")
                raise
            wait_time = initial_delay * (2 ** (retries - 1))  # Exponential backoff
            print(f"Request timed out. Retrying in {wait_time} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    # This should not be reached, but just in case
    raise last_exception

# Patch the web_scrap function in finvizfinance.util
import finvizfinance.util
finvizfinance.util.web_scrap = web_scrap_with_retry

print("Finvizfinance patched with increased timeout and retry logic")