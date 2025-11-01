from typing import Tuple, Iterator, Any, List
from decimal import Decimal
import heapq

def merge_sorted_asks(coinbase_asks: List, gemini_asks: List) -> Iterator[Tuple[Decimal, Decimal]]:
    # data is already in the ascending order. Proceeding with the merge.
    coinbase_a = [(Decimal(price), Decimal(size)) for price, size, qty in coinbase_asks]
    gemini_a = [(Decimal(ask['price']), Decimal(ask['amount'])) for ask in gemini_asks]
    # avoiding re-sorting the data using heapq.merge
    return heapq.merge(coinbase_a, gemini_a)

def merge_sorted_bids(coinbase_bids: List, gemini_bids: List) -> Iterator[Tuple[Decimal, Decimal]]:
    # we need to get this in the descending order. 
    # idea is to negate the prices and then flip it backwards.
    coinbase_b = [(-Decimal(price), Decimal(size)) for price, size, qty in coinbase_bids]
    gemini_b = [(-Decimal(bid['price']), Decimal(bid['amount'])) for bid in gemini_bids]

    # avoiding re-sorting the data using heapq.merge
    merged_data = heapq.merge(coinbase_b, gemini_b)

    # flipping the data backwards to positive prices
    flipped_data = ((-price, size) for price, size in merged_data)
    return flipped_data