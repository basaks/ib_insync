from ib_insync import *
import time
from datetime import datetime
import numpy as np
import pandas as pd
from ib_insync.my_utils import get_last_traded_price_sync


def organize_options_by_ticker(portfolio):
    """
    Organizes option contracts from a portfolio by their underlying ticker.

    Args:
        portfolio (list[Position]): A list of Position objects from ib_insync.ib.portfolio().

    Returns:
        dict: A dictionary where keys are underlying ticker symbols (str) and
              values are lists of Position objects for options on that ticker.
    """
    options_by_ticker = {}
    for pos in portfolio:
        if pos.contract.secType == "OPT":
            ticker = pos.contract.symbol
            if ticker not in options_by_ticker:
                options_by_ticker[ticker] = []
            options_by_ticker[ticker].append(pos)
    return options_by_ticker


def create_options_dataframe(options_by_ticker):
    """
    Converts the dictionary of options by ticker to a dictionary of pandas DataFrames.

    Args:
        options_by_ticker (dict): A dictionary where keys are underlying ticker symbols
                                  and values are lists of Position objects for options.

    Returns:
        dict: A dictionary where keys are underlying ticker symbols (str) and
              values are pandas DataFrames with "Strike Price" and "Position Size".
    """
    ticker_dataframes = {}
    for ticker, options in options_by_ticker.items():
        data = {
            'Strike': [],
            'Position': [],
            'C/P': [],
            'Expiry': [],
            'averageCost': [],
            'marketPrice': [],
            'marketValue': [],
            'unrealizedPNL': [],
        }
        for option_position in options:
            contract = option_position.contract
            # stock_contract = Stock(contract.tradingClass, 'SMART', contract.currency)
            # last_traded_price_of_underlying = get_last_traded_price_sync(ib, stock_contract)
            # import IPython; IPython.embed(); import sys; sys.exit()
            data['Strike'].append(contract.strike)
            data['Position'].append(np.int16(option_position.position))
            data['C/P'].append(contract.right)
            data['Expiry'].append(
                datetime.strptime(contract.lastTradeDateOrContractMonth, '%Y%m%d').date().isoformat()
            )
            data['averageCost'].append(option_position.averageCost)
            data['marketPrice'].append(option_position.marketPrice)
            data['marketValue'].append(option_position.marketValue)
            data['unrealizedPNL'].append(option_position.unrealizedPNL)
        ticker_dataframes[ticker] = pd.DataFrame(data)
        # also availble for quick lookup
        ticker_dataframes[ticker.lower()] = pd.DataFrame(data)

    return ticker_dataframes


def main():
    ib = IB()
    try:
        ib.connect('127.0.0.1', 7496, clientId=10, readonly=True)
        # ib.reqMarketDataType(2)  # this is key for after hours options greeks download

        # Ensure the contract details are fetched
        portfolio = ib.portfolio()
        time.sleep(2)
        # print(ticker)
        # print(organize_options_by_ticker(portfolio))
        return create_options_dataframe(organize_options_by_ticker(portfolio))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        ib.disconnect()


if __name__ == '__main__':
    options_by_ticker = main()
    for ticker, tdf in options_by_ticker.items():
        if (not ticker.islower()) and (tdf[tdf['Expiry'] == '2025-07-11'].shape[0]):
            print(f"===================={ticker}======================")
            print(ticker, tdf[tdf['Expiry'] == '2025-07-11'])
            print(f"{ticker} latest profit: ", tdf[tdf['Expiry'] == '2025-07-03'].unrealizedPNL.sum())
            print(f"net calls {ticker}: {tdf[tdf['C/P'] == 'C'].Position.sum()}, "
                  f"net puts {ticker}: {tdf[tdf['C/P'] == 'P'].Position.sum()}")
    import IPython; IPython.embed(); import sys; sys.exit()
