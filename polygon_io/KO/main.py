import logging
import backtrader as bt
import pandas as pd
import requests

import matplotlib

from EMACrossStrategyPoly import EMACrossStrategyPoly

matplotlib.use('Agg')

logging.basicConfig(
    filename='../trading.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logging.info("Starting the trading strategy")

api_key = 'LLElMA5jh7F5mYkXsBG28hMIRngnk060'  # Replace with your actual Polygon.io API key


def strategy():
    cerebro = bt.Cerebro()

    logging.info("Downloading SPY 1-hour data from Polygon.io")

    # Construct the URL for the API request
    url = f"https://api.polygon.io/v2/aggs/ticker/KO/range/1/day/2022-01-09/2024-08-28"
    params = {
        "adjusted": "true",
        "sort": "desc",
        "apiKey": api_key
    }

    # Make the API request
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an error if the request fails
    json_response = response.json()

    # Extract the data from the response
    bars = json_response['results']

    # Convert the data into a DataFrame
    data = pd.DataFrame([{
        'timestamp': pd.to_datetime(bar['t'], unit='ms'),
        'Open': bar['o'],
        'High': bar['h'],
        'Low': bar['l'],
        'Close': bar['c'],
        'Volume': bar['v'],
    } for bar in bars])

    print(data.columns)
    print(data)

    # Set the index to the timestamp
    data.set_index('timestamp', inplace=True)

    # Sort the data by index (date) to ensure it's ordered from earliest to latest
    data.sort_index(inplace=True)

    logging.info(f"Data before cleaning:\n{data.head()}")

    # Handle NaN values by forward filling, then backward filling as a fallback
    data.ffill(inplace=True)
    data.bfill(inplace=True)

    logging.info(f"Data after cleaning:\n{data.head()}")

    data_bt = bt.feeds.PandasData(dataname=data)

    cerebro.adddata(data_bt)

    logging.info("Adding strategy to Cerebro")
    cerebro.addstrategy(EMACrossStrategyPoly)

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
