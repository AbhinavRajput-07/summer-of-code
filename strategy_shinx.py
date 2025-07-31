from src.backtester import Order
from typing import Dict, List
import logging

from collections import deque
from typing import Dict, List

class Trader:
    def __init__(self, lookback: int = 50, trade_size: int = 7, position_limit: int = 60):
        self.lookback = lookback
        self.trade_size = trade_size
        self.position_limit = position_limit
        self.mid_price_histories: Dict[str, deque] = {}

    def run(self, state):
        orders: Dict[str, List[Order]] = {}
        max_pos = self.position_limit  # Tell the backtester the max position constraint

        for product, orderbook in state.order_depth.items():
            # Calculate best bid/ask and mid price
            if not orderbook.buy_orders or not orderbook.sell_orders:
                continue

            best_bid = max(orderbook.buy_orders.keys())
            best_ask = min(orderbook.sell_orders.keys())
            mid_price = (best_bid + best_ask) / 2

            # Track mid-price history
            if product not in self.mid_price_histories:
                self.mid_price_histories[product] = deque(maxlen=self.lookback + 1)

            price_history = self.mid_price_histories[product]
            price_history.append(mid_price)

            # Momentum calculation
            if len(price_history) > self.lookback:
                past_price = price_history[0]
                momentum = mid_price - past_price
                product_orders = []

                current_position = state.positions.get(product, 0)

                if momentum > 0 and current_position > -self.position_limit:
                    # Buy
                    product_orders.append(Order(symbol=product, price=int(best_ask), quantity=self.trade_size))
                elif momentum < 0 and current_position < self.position_limit:
                    # Sell
                    product_orders.append(Order(symbol=product, price=int(best_bid), quantity=-self.trade_size))

                orders[product] = product_orders

        return orders, max_pos
