from ib_insync import *
import time
from datetime import datetime
import numpy as np
import pandas as pd
from tabulate import tabulate
from ib_insync.my_utils import get_last_traded_price_sync


def markdown_printer_with_unique_index(df_with_repeated_indices, table_format):
    markdown_data = []
    previous_index = None
    first_index = True
    for idx, row in df_with_repeated_indices.iterrows():
        current_index = idx
        index_value = ""
        if current_index != previous_index:
            if not first_index:
                markdown_data.append(["-"*10] + ["-"*10] * len(df_with_repeated_indices.columns))
            index_value = current_index
            previous_index = current_index
            first_index = False
        row_values = row.tolist()
        markdown_data.append([index_value] + row_values)

    # Create a DataFrame from the processed data for cleaner markdown output
    markdown_df = pd.DataFrame(markdown_data, columns=["Expiry"] + df_with_repeated_indices.columns.tolist())

    # Use to_markdown with index=False to avoid default DataFrame index
    markdown_output = markdown_df.to_markdown(index=False, tablefmt=table_format)

    print(markdown_output)


def net_options(stock, expiry_date=None, with_display=True, table_format='pipe'):
    stock = stock.upper()
    t = options_by_ticker[stock]
    df = t.loc[expiry_date, :] if expiry_date is not None else t

    option_type_string_calls = f"{stock} extra Calls: "
    option_type_string_puts = f"{stock} extra Puts: "
    if with_display:
        # print(df.set_index('Expiry').to_markdown(index=True))
        markdown_printer_with_unique_index(df.set_index('Expiry'), table_format=table_format)
    print(option_type_string_calls, df[df['C/P'] == 'C'].Position.sum())
    print(option_type_string_puts, df[df['C/P'] == 'P'].Position.sum())
    return


def organize_contract_type_by_ticker(portfolio, contract_type='OPT'):
    """
    Organizes option contracts from a portfolio by their underlying ticker.

    Args:
        portfolio (list[Position]): A list of Position objects from ib_insync.ib.portfolio().

    Returns:
        dict: A dictionary where keys are underlying ticker symbols (str) and
              values are lists of Position objects for options on that ticker.
    """
    contracts_by_ticker = {}
    for pos in portfolio:
        if pos.contract.secType == contract_type:
            ticker = pos.contract.symbol
            if ticker not in contracts_by_ticker:
                contracts_by_ticker[ticker] = []
            contracts_by_ticker[ticker].append(pos)
    return contracts_by_ticker


def create_stocks_dataframe(stocks_by_tickers):
    """
    Converts the dictionary of stocks by ticker to a dictionary of pandas DataFrames.

    Args:
        stocks_by_tickers (dict): A dictionary where keys are underlying ticker symbols
                                  and values are lists of Position objects for stocks.

    Returns:
        dict: A dictionary where keys are underlying ticker symbols (str) and
              values are pandas DataFrames with "Strike Price" and "Position Size".
    """
    ticker_dataframes = {}
    for ticker, stocks in stocks_by_tickers.items():
        data = {}
        for stk_position in stocks:
            contract = stk_position.contract
            # stock_contract = Stock(contract.tradingClass, 'SMART', contract.currency)
            # last_traded_price_of_underlying = get_last_traded_price_sync(ib, stock_contract)
            data['Position'] = np.int32(stk_position.position)
            data['averageCost'] = stk_position.averageCost
            data['marketPrice'] = stk_position.marketPrice
            data['marketValue'] = stk_position.marketValue
            data['unrealizedPNL'] = stk_position.unrealizedPNL
        # data = pd.DataFrame(data)
        ticker_dataframes[ticker] = data
        # also availble for quick lookup
        # ticker_dataframes[ticker.lower()] = data

    return pd.DataFrame(ticker_dataframes).transpose()


def create_options_dataframe(options_by_the_tickers):
    """
    Converts the dictionary of options by ticker to a dictionary of pandas DataFrames.

    Args:
        options_by_the_tickers (dict): A dictionary where keys are underlying ticker symbols
                                  and values are lists of Position objects for options.

    Returns:
        dict: A dictionary where keys are underlying ticker symbols (str) and
              values are pandas DataFrames with "Strike Price" and "Position Size".
    """
    ticker_dataframes = {}
    for ticker, options in options_by_the_tickers.items():
        data = {
            'Strike': [],
            'Position': [],
            'C/P': [],
            'Expiry': [],
            'Expiry_date': [],
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
            data['Expiry_date'].append(
                datetime.strptime(contract.lastTradeDateOrContractMonth, '%Y%m%d').date()
            )
            data['averageCost'].append(option_position.averageCost)
            data['marketPrice'].append(option_position.marketPrice)
            data['marketValue'].append(option_position.marketValue)
            data['unrealizedPNL'].append(option_position.unrealizedPNL)
        data = pd.DataFrame(data)
        data.index = pd.DatetimeIndex(data['Expiry_date'])
        data.drop(['Expiry_date'], axis=1, inplace=True)
        ticker_dataframes[ticker] = data
        # also availble for quick lookup
        # ticker_dataframes[ticker.lower()] = data

    return ticker_dataframes


def main():
    ib = IB()
    try:
        ib.connect('127.0.0.1', 7496, clientId=10, readonly=True)
        # ib.reqMarketDataType(2)  # this is key for after hours options greeks download
        # ib.reqAccountUpdates()
        # Ensure the contract details are fetched
        portfolio = ib.portfolio()
        time.sleep(5)
        return portfolio, create_options_dataframe(organize_contract_type_by_ticker(portfolio))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        ib.disconnect()


if __name__ == '__main__':
    portfolio, options_by_ticker = main()
    closest_expiry = "2025-07-18"
    for ticker, tdf in options_by_ticker.items():
        print(f"===================={ticker}======================")
        if tdf[tdf['Expiry'] == closest_expiry].shape[0]:
            print(ticker, tdf.loc[closest_expiry])
            print(f"{ticker} latest profit: ", tdf.loc[closest_expiry].unrealizedPNL.sum())
        net_options(stock=ticker, expiry_date=None, with_display=False)

    stocks = create_stocks_dataframe(organize_contract_type_by_ticker(portfolio, contract_type='STK'))
    import IPython; IPython.embed(); import sys; sys.exit()
