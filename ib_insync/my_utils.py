from ib_insync import IB, Stock, Ticker

def get_last_traded_price_sync(ib: IB, stock_contract: Stock):
    """
    Fetches the last traded price of a stock using ib_insync (synchronous).

    Args:
        ib (IB): An instance of the IB class (must be connected).
        stock_contract (Stock): The stock contract for which to fetch the price.

    Returns:
        float or None: The last traded price, or None if not received within timeout.
    """
    last_price = None
    received_price = False

    def on_tick(ticker: Ticker, tickList: list[TickData]):
        nonlocal last_price
        nonlocal received_price
        for tick in tickList:
            if tick.tickType == TickType.LAST or tick.tickType == TickType.DELAYED_LAST:
                print(f"Last Traded Price for {stock_contract.symbol}: {tick.price}")
                last_price = tick.price
                received_price = True

    ticker = ib.reqMktData(stock_contract, '', False, False)
    ticker.updateEvent += on_tick

    timeout = 5  # seconds
    start_time = time.time()
    while not received_price and time.time() - start_time < timeout:
        ib.sleep(0.1)  # Yield control to receive ticks

    ib.cancelMktData(ticker.contract)
    return last_price
