import os
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import pandas as pd
from time import sleep
import logging

# Configuration
API_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
API_PARAMS = {
    'start': '1',
    'limit': '16',
    'convert': 'EUR'
}
API_KEY = '5cec0271-f035-4ec9-8b43-0a09a546d4e5'
CSV_FILE_PATH = r"C:\Users\radlm\OneDrive\Dokumente\Scripts\API.csv"
SLEEP_DURATION_SECONDS = 60
MAX_API_CALLS = 333


def api_call():
    session = Session()
    session.headers.update({
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    })

    try:
        response = session.get(API_URL, params=API_PARAMS)
        response.raise_for_status()  # Raise exception for non-200 status codes

        data = response.json()
        df = pd.json_normalize(data["data"])

        # Additional DataFrame operations
        df["timestamp"] = pd.to_datetime("now")
        df["quote.EUR.price"] = df["quote.EUR.price"].round(2)
        df["quote.EUR.volume_24h"] = df["quote.EUR.volume_24h"].round(2)
        df['max_supply'] = pd.to_numeric(df['max_supply'], errors='coerce')
        df['circulating_supply'] = pd.to_numeric(df['circulating_supply'], errors='coerce')
        df['total_supply'] = pd.to_numeric(df['total_supply'], errors='coerce')
        df = df.drop(columns=["tags", "platform", "cmc_rank", 
                              "tvl_ratio", "quote.EUR.tvl", "platform.id",	
                              "platform.name", "platform.symbol", "platform.slug",
                              "slug", "self_reported_circulating_supply", "self_reported_market_cap",
                              "last_updated", "date_added"], axis=1)

        # Writing to CSV file
        if not os.path.isfile(CSV_FILE_PATH):
            df.to_csv(CSV_FILE_PATH, header="column_names", sep=";")
        else:
            df.to_csv(CSV_FILE_PATH, mode="a", header=False, sep=";")
        logging.info("API call successful")
    except (ConnectionError, Timeout, TooManyRedirects, Exception) as e:
        logging.error(f"Error occurred: {e}")

# Main loop
for _ in range(MAX_API_CALLS):
    api_call()
    print("API Call completed")
    sleep(SLEEP_DURATION_SECONDS)