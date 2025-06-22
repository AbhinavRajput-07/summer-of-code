from src.backtester import Order, OrderBook
from typing import List

class Trader:
    def __init__(self):
        self.lookback = 5  # Number of periods to calculate momentum
        self.trade_size = 10  # Number of shares to trade
        self.mid_price_history = []  # Track historical mid prices
        self.stop_loss_pct = 0.02  # 2% stop loss
        self.take_profit_pct = 0.00  # 4% take profit
        self.entry_price = None  # Track entry price for current position
        self.position = 0  # Track current position
        
    def run(self, state, current_position):
        orders = []
        order_depth = state.order_depth
        self.position = current_position  # Update current position
        
        # Calculate best bid/ask and mid price
        best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None
        best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
        
        if best_bid and best_ask:
            current_mid = (best_bid + best_ask) / 2
            self.mid_price_history.append(current_mid)
            
            # Only trade when we have enough historical data
            if len(self.mid_price_history) > self.lookback:
                # Calculate momentum (current price vs price 'lookback' periods ago)
                past_price = self.mid_price_history[-self.lookback-1]
                momentum = current_mid - past_price
                
                # Check if we need to exit position based on stop loss/take profit
                if self.position != 0 and self.entry_price is not None:
                    # Calculate current profit/loss percentage
                    if self.position > 0:  # Long position
                        pl_pct = (current_mid - self.entry_price) / self.entry_price
                    else:  # Short position
                        pl_pct = (self.entry_price - current_mid) / self.entry_price
                    
                    # Check stop loss condition
                    if pl_pct <= -self.stop_loss_pct:
                        # Exit entire position
                        exit_quantity = -self.position
                        exit_price = best_bid if exit_quantity < 0 else best_ask
                        orders.append(Order("PRODUCT", int(exit_price), exit_quantity))
                        self.entry_price = None  # Reset entry price
                        
                    # Check take profit condition
                    elif pl_pct >= self.take_profit_pct:
                        # Exit entire position
                        exit_quantity = -self.position
                        exit_price = best_bid if exit_quantity < 0 else best_ask
                        orders.append(Order("PRODUCT", int(exit_price), exit_quantity))
                        self.entry_price = None  # Reset entry price
                
                # Only enter new positions if not currently in a position
                if self.entry_price is None and self.position == 0:
                    # Generate signals based on momentum
                    if momentum > 0:  # Positive momentum - uptrend
                        # Buy if we're not at position limit
                        if self.position < 50:
                            entry_price = best_ask
                            orders.append(Order("PRODUCT", entry_price, self.trade_size))
                            self.entry_price = entry_price  # Set new entry price
                    
                    elif momentum < 0:  # Negative momentum - downtrend
                        # Sell if we're not at position limit
                        if self.position > -50:
                            entry_price = best_bid
                            orders.append(Order("PRODUCT", entry_price, -self.trade_size))
                            self.entry_price = entry_price  # Set new entry price

        return {"PRODUCT": orders}