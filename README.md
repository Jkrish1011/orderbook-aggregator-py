# OrderBook Aggregator

This is a orderbook aggregator which helps you understand the best buy or sell price for BTC of a given quantity using the coinbase and gemini API.

## Pre-Requisites

1/ python3 -m venv venv

2/ source venv/bin/activate

3/ pip3 install -r requirements.txt

## Usage 

### Without Multi threading
python3 ratelimiter.py --qty 101898.2


### With Multi threading
python3 ratelimiter_mt.py --qty 101898.2


### Run tests

pytest -vv -s


### specific test cases

pytest tests/test_rate_limiter.py::TestMultiThreadFunctionalities::test_multi_thread_calls_to_system -vv -s
