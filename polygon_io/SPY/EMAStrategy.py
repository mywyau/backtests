import logging
import backtrader as bt

class EMAStrategy(bt.Strategy):
    params = (
        ('long_period', 10),  # Long-period EMA
        ('take_profit', 0.05),  # 5% profit target
        ('investment_fraction', 0.001),  # Initial fraction of capital to invest
        ('max_fractions', 50)  # Maximum number of fractions (up to 50)
    )

    def __init__(self):
        self.ema200 = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.long_period)
        self.orders = []  # To keep track of all pending orders, their target prices, and sizes

    def next(self):
        # Wait until there is enough data to calculate the EMA
        if len(self.data) < self.params.long_period:
            logging.info(f"Not enough data yet: {len(self.data)} periods available")
            return

        logging.info(f"Checking conditions on {self.data.datetime.date(0)} - Close Price: {self.data.close[0]}")

        # Check if there are any active positions
        for i, (order, target_price, size) in enumerate(self.orders):
            if self.data.close[0] >= target_price:  # Check if the target price has been reached
                self.sell(size=size)  # Sell the position associated with this order
                logging.info(f"SELL {size:.4f} shares at {self.data.close[0]} on {self.data.datetime.date(0)}")
                self.orders.pop(i)  # Remove the order from the list

        # If all fractions are already used, do not create a new buy order
        if len(self.orders) >= self.params.max_fractions:
            logging.info(f"Maximum of {self.params.max_fractions} fractions reached. Waiting for sell signals.")
            return

        # If no position is open, check the buy condition
        if self.data.close[0] < self.ema200[0]:
            # Calculate the amount of capital to invest based on the current fraction
            available_cash = self.broker.getcash()
            current_fraction = self.params.investment_fraction * (len(self.orders) + 1)  # Increment the fraction
            investment_amount = available_cash * current_fraction

            # Calculate the number of shares to buy (allowing fractional shares)
            size = investment_amount / self.data.close[0]

            if size > 0:
                order = self.buy(size=size)  # Place a buy order for the calculated number of shares
                target_price = self.data.close[0] * (1.0 + self.params.take_profit)
                self.orders.append((order, target_price, size))  # Track the order, its target price, and size
                logging.info(f"BUY {size:.4f} shares at {self.data.close[0]} on {self.data.datetime.date(0)}")
            else:
                logging.info(f"Insufficient cash to buy shares at {self.data.close[0]} on {self.data.datetime.date(0)}")

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return  # If the order is submitted/accepted, do nothing

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                logging.info(f"BUY EXECUTED at {order.executed.price} on {self.data.datetime.date(0)}")
            elif order.issell():
                logging.info(f"SELL EXECUTED at {order.executed.price} on {self.data.datetime.date(0)}")
                # The corresponding sell logic is handled in `next`, so no need to remove the order here.

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            logging.warning(f"Order Canceled/Margin/Rejected: {order.status}")
            # Optionally, remove the order from `self.orders` if it's been rejected or canceled.

