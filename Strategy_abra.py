from src.backtester import Order, OrderBook
from typing import List

class Trader:
    def run(self, state, current_position):
        result = {}
        orders: List[Order] = []
        order_depth: OrderBook = state.order_depth

        orders.append(Order("PRODUCT", 1921, 30))
        orders.append(Order("PRODUCT", 1928, -30))


      

        result["PRODUCT"] = orders
        return result
