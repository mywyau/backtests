import logging
import backtrader as bt
import pandas as pd
import yfinance as yf

from EMACrossStrategy import EMACrossStrategy

import matplotlib

matplotlib.use('Agg')

logging.basicConfig(
    filename='../trading.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logging.info("Starting the trading strategy")

# api_key = 'G2QJBD5924G3HMDB'
api_key = 'NSVOADF3A76T46S4'


def strategy():
    cerebro = bt.Cerebro()

    logging.info("Downloading SPY 1-hour data from Alpha Vantage")

    from alpha_vantage.timeseries import TimeSeries

    ts = TimeSeries(key=api_key, output_format='pandas')
    # data, meta_data = ts.get_intraday(symbol='SPY', interval='60min', outputsize='full')
    data, meta_data = ts.get_daily(symbol='SPY', outputsize='full')

    print(data.columns)

    # Convert the index to datetime
    data.index = pd.to_datetime(data.index)
    # Rename the columns to match what Backtrader expects
    data.rename(columns={'1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close', '5. volume': 'Volume'},
                inplace=True)

    # Sort the data by index (date) to ensure it's ordered from earliest to latest
    data.sort_index(inplace=True)

    print(data.columns)
    print(data)
    logging.info(f"Data before cleaning:\n{data.head()}")

    # Handle NaN values by forward filling, then backward filling as a fallback
    data.ffill(inplace=True)
    data.bfill(inplace=True)

    logging.info(f"Data after cleaning:\n{data.head()}")

    data_bt = bt.feeds.PandasData(dataname=data)

    cerebro.adddata(data_bt)

    logging.info("Adding strategy to Cerebro")
    cerebro.addstrategy(EMACrossStrategy)

    initial_cash = 10000.0
    cerebro.broker.setcash(initial_cash)
    logging.info(f"Initial capital set to: ${initial_cash}")

    cerebro.broker.setcommission(commission=0.001)
    logging.info("Commission set to 0.1% per trade")

    logging.info("Running the backtest")
    cerebro.run()

    final_value = cerebro.broker.getvalue()
    logging.info(f"Final Portfolio Value: {final_value}")

    try:
        logging.info("Plotting the results")
        cerebro.plot()
    except Exception as e:
        logging.error(f"Error while plotting: {e}")


if __name__ == '__main__':
    strategy()
