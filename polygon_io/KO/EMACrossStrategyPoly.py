import logging

import backtrader as bt


class EMACrossStrategyPoly(bt.Strategy):
    params = (
        ('long_period', 10),  # Long-period EMA
        ('take_profit', 0.01),  # 5% profit target
        ('investment_fraction', 0.20)  # Fraction of capital to invest
    )

    def __init__(self):
        self.ema200 = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.long_period)
        self.order = None  # To keep track of pending orders

    def next(self):
        # Wait until there is enough data to calculate the EMA
        if len(self.data) < self.params.long_period:
            logging.info(f"Not enough data yet: {len(self.data)} periods available")
            return

        logging.info(f"Checking conditions on {self.data.datetime.date(0)} - Close Price: {self.data.close[0]}")

        if self.order:  # Check if an order is pending
            return  # If there is a pending order, do nothing

        if self.position:  # If we have an open position
            target_price = self.position.price * (1.0 + self.params.take_profit)
            logging.info(f"Current position open. Target price: {target_price}")

            # Only sell if the price reaches or exceeds the target price
            if self.data.close[0] >= target_price:
                self.order = self.sell(size=self.position.size)  # Sell the entire position
                logging.info(f"SELL at {self.data.close[0]} on {self.data.datetime.date(0)}")
        else:  # If no position is open, check the buy condition
            if self.data.close[0] < self.ema200[0]:  # Buy if the current price is below the long-period EMA
                # Calculate the amount of capital to invest (10% of available cash)
                available_cash = self.broker.getcash()
                investment_amount = available_cash * self.params.investment_fraction

                # Calculate the number of shares to buy (allowing fractional shares)
                size = investment_amount / self.data.close[0]

                if size > 0:
                    self.order = self.buy(size=size)  # Place a buy order for the calculated number of shares
                    logging.info(f"BUY {size:.4f} shares at {self.data.close[0]} on {self.data.datetime.date(0)}")
                else:
                    logging.info(
                        f"Insufficient cash to buy shares at {self.data.close[0]} on {self.data.datetime.date(0)}")

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return  # If the order is submitted/accepted, do nothing

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                logging.info(f"BUY EXECUTED at {order.executed.price} on {self.data.datetime.date(0)}")
            elif order.issell():
                logging.info(f"SELL EXECUTED at {order.executed.price} on {self.data.datetime.date(0)}")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            logging.warning(f"Order Canceled/Margin/Rejected: {order.status}")

        # Reset the order variable when the order completes to allow new orders
        self.order = None
