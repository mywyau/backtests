import backtrader as bt
import logging

class EMACrossStrategy(bt.Strategy):
    params = (
        ('short_period', 30),
        ('medium_period', 60),
        ('long_period', 100),
        ('threshold', 0.01),
        ('take_profit', 0.01),  # 1% profit target
        ('investment_fraction', 0.01),  # Fraction of capital to invest
    )

    def __init__(self):
        self.ema50 = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.short_period)
        self.ema100 = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.medium_period)
        self.ema200 = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.long_period)
        self.buy_price = None  # To store the price at which we bought
        self.order = None  # To keep track of pending orders

    def next(self):
        # Wait until there is enough data to calculate all EMAs
        if len(self.data) < self.params.long_period:
            logging.info(f"Not enough data yet: {len(self.data)} periods available")
            return

        logging.info(f"Checking conditions on {self.data.datetime.date(0)} - Close Price: {self.data.close[0]}")

        if self.order:  # Check if an order is pending
            return  # If there is a pending order, do nothing

        if self.position:  # Check if we already have an open position
            if self.buy_price is not None:
                target_price = self.buy_price * (1.0 + self.params.take_profit)
                logging.info(f"Current position open. Buy price: {self.buy_price}, Target price: {target_price}")

                # Only sell if the price reaches or exceeds the target price
                if self.data.close[0] >= target_price:
                    self.order = self.sell()  # Sell the position at the target price
                    logging.info(f"SELL at {self.data.close[0]} on {self.data.datetime.date(0)}")
                    self.buy_price = None  # Reset buy price after selling

            else:
                logging.warning("Buy price is None when trying to calculate the target price.")

        else:  # If no position is open, check the buy condition
            if (abs(self.ema50[0] - self.ema200[0]) / self.ema200[0] <= self.params.threshold and
                    abs(self.ema100[0] - self.ema200[0]) / self.ema200[0] <= self.params.threshold):

                # Calculate the amount of capital to invest (1% of available cash)
                available_cash = self.broker.getcash()
                investment_amount = available_cash * self.params.investment_fraction

                # Calculate the number of shares to buy (allowing fractional shares)
                size = investment_amount / self.data.close[0]

                if size > 0:
                    self.order = self.buy(size=size)  # Place a buy order for the calculated number of shares
                    logging.info(f"BUY {size:.4f} shares at {self.data.close[0]} on {self.data.datetime.date(0)}")
                else:
                    logging.info(f"Insufficient cash to buy shares at {self.data.close[0]} on {self.data.datetime.date(0)}")

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return  # If the order is submitted/accepted, do nothing

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price  # Set buy price on order execution
                logging.info(f"BUY EXECUTED at {self.buy_price} on {self.data.datetime.date(0)}")
            elif order.issell():
                logging.info(f"SELL EXECUTED at {order.executed.price} on {self.data.datetime.date(0)}")
                self.buy_price = None  # Reset buy price after selling

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            logging.warning(f"Order Canceled/Margin/Rejected: {order.status}")

        # Reset the order variable when order completes
        self.order = None
