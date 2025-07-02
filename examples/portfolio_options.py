from ib_insync import *
import time
import pandas as pd


def main():
    ib = IB()
    try:
        ib.connect('127.0.0.1', 7496, clientId=10, readonly=True)
        #         ib.reqMarketDataType(2)  # this is key for after hours options greeks download

        # Ensure the contract details are fetched
        portfolio = ib.portfolio()
#         import IPython; IPython.embed(); import sys; sys.exit()

        # p = portfolio[0]
        # print(portfolio[0])
        #         contract = ib.qualifyContracts(p.contract)
#         print(contract)
#         # ticker = ib.reqMktData(* contract, '', True, False)  # useGreeks=True
#         # print(ticker)
#         ticker = ib.reqTickers(* contract)
#         print(ticker)

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
                data = {'Strike Price': [], 'Position Size': [], 'Option Type': [],
                'lastTradeDateOrContractMonth': [],
                                'Average Price': [],
                                'marketPrice': [],
                                'marketValue': [],
                                'unrealizedPNL': [],
                }
                for option_position in options:
                    data['Strike Price'].append(option_position.contract.strike)
                    data['Position Size'].append(option_position.position)
                    data['Option Type'].append(option_position.contract.right)
                    data['lastTradeDateOrContractMonth'].append(option_position.contract.lastTradeDateOrContractMonth)
                    data['Average Price'].append(option_position.averageCost)
                    data['marketPrice'].append(option_position.marketPrice)
                    data['marketValue'].append(option_position.marketValue)
                    data['unrealizedPNL'].append(option_position.unrealizedPNL)
                ticker_dataframes[ticker] = pd.DataFrame(data)
            return ticker_dataframes

        # Keep the script running to receive ticks (you might want to set a timeout or other stopping condition)
        time.sleep(5)
        # print(ticker)
        # print(organize_options_by_ticker(portfolio))
        return create_options_dataframe(organize_options_by_ticker(portfolio))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        ib.disconnect()


if __name__ == '__main__':
    options_by_ticker = main()
    import IPython; IPython.embed(); import sys; sys.exit()

