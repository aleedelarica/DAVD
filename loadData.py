from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

# start_date = datetime.now() - timedelta(days=24*30)  # Hace 2 años
end_date = datetime.now()-timedelta(days=1)

start_date = pd.to_datetime('01/01/2020', format='%d/%m/%Y').strftime('%Y-%m-%d')


# Función para obtener datos históricos de yfinance
def get_historical_data(ticker):
    # Create a Ticker object for the given stock symbol
    stock_ticker = yf.Ticker(ticker)

    # Get historical market data for the specified period
    historical_data = stock_ticker.history(start=start_date, end=end_date)

    # Resetting the index to have 'Date' as a column instead of the index
    historical_data.reset_index(inplace=True)

    return historical_data

# Función para obtener datos históricos de yfinance
def get_historical_data_for_date(ticker,buy_date):
    # Create a Ticker object for the given stock symbol
    stock_ticker = yf.Ticker(ticker)

    if isinstance(buy_date, str):
        buy_date = pd.to_datetime(buy_date, format='%d/%m/%Y')

    # Formatear la fecha al formato esperado por yfinance
    buy_date = buy_date.strftime('%Y-%m-%d')

    # Get historical market data for the specified period
    historical_data = stock_ticker.history(start=buy_date, end=end_date)

    # Resetting the index to have 'Date' as a column instead of the index
    historical_data.reset_index(inplace=True)

    return historical_data

def get_historical_data_for_range(ticker,start_date,end_date):
    # Create a Ticker object for the given stock symbol
    stock_ticker = yf.Ticker(ticker)

    start_date = pd.to_datetime(start_date, format='%Y-%m-%d')
    end_date = pd.to_datetime(end_date, format='%Y-%m-%d')

    # Get historical market data for the specified period
    historical_data = stock_ticker.history(start=start_date, end=end_date)

    # Resetting the index to have 'Date' as a column instead of the index
    historical_data.reset_index(inplace=True)

    return historical_data

