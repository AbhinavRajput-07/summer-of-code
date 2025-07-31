from src.backtester import Order, OrderBook
from typing import List

class Trader:
    def run(self, state, current_position):
        result = {}
        orders: List[Order] = []
        order_depth: OrderBook = state.order_depth

        orders.append(Order("PRODUCT", 9998, 30))
        orders.append(Order("PRODUCT", 10002, -30))

        result["PRODUCT"] = orders
        return result