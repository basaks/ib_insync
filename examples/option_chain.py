from ib_insync import *
import time

def main():
    ib = IB()
    try:
        ib.connect('127.0.0.1', 7496, clientId=10, readonly=True)

        contract = Option(symbol='AAPL', lastTradeDateOrContractMonth='20250718', strike=200,
                          right='C', exchange='SMART')
        print(contract)
        # Ensure the contract details are fetched
        ib.qualifyContracts(contract)
        print(contract)
        ib.reqMarketDataType(2)  # this is key for after hours options greeks download

        # ticker = ib.reqMktData(contract, '', True, False)  # useGreeks=True
        print(ib.reqMktData(contract, '', True, False)) # useGreeks=True)
        ticker = ib.reqTickers(contract)

        # Keep the script running to receive ticks (you might want to set a timeout or other stopping condition)
        time.sleep(5)
        print(ticker)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        ib.disconnect()


if __name__ == '__main__':
    main()