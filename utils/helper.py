from typing import Tuple, Iterator, List
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


def calculate_buy_price(merged_bids: Iterator[Tuple[Decimal, Decimal]], quantity: Decimal) -> Decimal:
    total_cost = Decimal(0)
    remaining_quantity = quantity

    for price, size in merged_bids:
        # check if the remaining quantity is less than the size of the current bid
        if remaining_quantity <= size:
            # calculate the cost for the remaining quantity
            cost = price * remaining_quantity
            total_cost += cost
            break
        # if the remaining quantity is greater than the size of the current bid, add the full price to the total cost
        else:
            total_cost += (price * size)
        
        remaining_quantity -= size

    return total_cost

def calculate_sell_price(merged_asks: Iterator[Tuple[Decimal, Decimal]], quantity: Decimal) -> Decimal:
    total_cost = Decimal(0)
    remaining_quantity = quantity

    for price, size in merged_asks:
        # check if the remaining quantity is less than the size of the current ask
        if remaining_quantity <= size:
            # calculate the proceeds for the remaining quantity
            cost = price * remaining_quantity
            total_cost += cost
            break
        # if the remaining quantity is greater than the size of the current ask, add the full price to the total proceeds
        else:
            total_cost += (price * size)

        remaining_quantity -= size
    
    return total_cost