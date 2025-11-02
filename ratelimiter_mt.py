# Analyzing the result from Coinbase and Gemini, the bids and asks are already in desc and asc order respectively

# the data from coinbase is large and gemini is quite smaller comparitively

# using heapq to store because easy and effective to merge both the data sets 
# because heaps combines the data sets without re-sorting. This saves time.


from dotenv import load_dotenv
import os
import argparse
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.data_loader import get_coinbase_data, get_gemini_data
from utils.helper import merge_sorted_asks, merge_sorted_bids, calculate_buy_price, calculate_sell_price


# loads the environment variables from the .env file
load_dotenv()

COINBASE_API = os.getenv("COINBASE_API")
GEMINI_API = os.getenv("GEMINI_API")


def main(quantity):
    print("Fetching Coinbase and Gemini Data")
    coinbase_data = None
    gemini_data = None

    with ThreadPoolExecutor(max_workers=2) as executor:
        coinbase_future = executor.submit(get_coinbase_data, COINBASE_API)
        gemini_future = executor.submit(get_gemini_data, GEMINI_API)


        for future in as_completed([coinbase_future, gemini_future]):
            try:
                data = future.result()

                if future is coinbase_future:
                    print("Coinbase data fetched successfully")
                    coinbase_data = data
                else:
                    print("Gemini data fetched successfully")
                    gemini_data = data
            except Exception as e:
                print("Error : ", e)
                exit(1)
    
    if coinbase_data is None:
        print("Error: Failed to fetch data from Coinbase")
        exit(1)
    
    if 'bids' not in coinbase_data or 'asks' not in coinbase_data:
        print("Error: No bids or asks found in Coinbase")
        exit(1)

    if len(coinbase_data['bids']) == 0 or len(coinbase_data['asks']) == 0:
        print("Error: No bids or asks found in Coinbase")
        exit(1)
    
    if gemini_data is None:
        print("Error: Failed to fetch data from Gemini")
        exit(1)

    if 'bids' not in gemini_data or 'asks' not in gemini_data:
        print("Error: No bids or asks found in Gemini")
        exit(1)

    if len(gemini_data['bids']) == 0 or len(gemini_data['asks']) == 0:
        print("Error: No bids or asks found in Gemini")
        exit(1)
    
    # print(gemini_data)
    print("Loaded the data successfully from Coinbase and Gemini")
    print("Some status about the data")
    print("Coinbase bids: ", len(coinbase_data['bids']))
    print("Coinbase asks: ", len(coinbase_data['asks']))
    print("Gemini bids: ", len(gemini_data['bids']))
    print("Gemini asks: ", len(gemini_data['asks']))
    print("--------------------------------")

    print("Merging the dataset")
    merged_asks = None
    merged_bids = None

    with ThreadPoolExecutor(max_workers=2) as executor:
        merged_asks_future = executor.submit(merge_sorted_asks, coinbase_data['asks'], gemini_data['asks'])
        merged_bids_future = executor.submit(merge_sorted_bids, coinbase_data['bids'], gemini_data['bids'])


        for future in as_completed([merged_asks_future, merged_bids_future]):
            data = future.result()

            if future is merged_asks_future:
                print("Asks merged successfully!")
                merged_asks = data
            else:
                print("Bids merged successfully!")
                merged_bids = data

    # buy caculation
    with ThreadPoolExecutor(max_workers=2) as executor:
        calculate_bids_future = executor.submit(calculate_buy_price, merged_bids, quantity)
        calculate_asks_future = executor.submit(calculate_sell_price, merged_asks, quantity)

        for future in as_completed([calculate_bids_future, calculate_asks_future]):
            data = future.result()

            if future is calculate_bids_future:
                print(f"To buy {quantity} BTC: ${data:,.2f}")
            else:
                print(f"To sell {quantity} BTC: ${data:,.2f}")        
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='Orderbook Price Analyzer',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                    description='This program analyzes the orderbook price and prints the best bid and ask price',
                    epilog='This is a simple program to analyze the orderbook price and print the best bid and ask price')

    parser.add_argument('--qty',type=Decimal, default=Decimal(10.0),help='Quantity of BTC to buy/sell')

    args = parser.parse_args()

    if args.qty <= Decimal(0):
        print("Error: Quantity must be positive")
        exit(1)

    main(args.qty)
