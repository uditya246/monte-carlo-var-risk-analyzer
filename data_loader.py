import yfinance as yf
import pandas as pd

def fetch_data(ticker: str, period: str):
    """
    Downloads historical stock data using yfinance.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL').
        period (str): Historical period (e.g., '1Y', '3Y', '5Y').
        
    Returns:
        tuple: (pandas.Series of Close prices, str error_message)
    """
    # Map periods to yfinance acceptable format
    period_map = {'1Y': '1y', '3Y': '3y', '5Y': '5y'}
    yf_period = period_map.get(period, '1y')
    
    try:
        stock = yf.Ticker(ticker)
        # Fetch historical data
        hist = stock.history(period=yf_period)
        
        if hist.empty:
            return None, f"No data found for ticker '{ticker}'. Please check the symbol."
        
        # We'll use the 'Close' column for our calculations
        if 'Close' not in hist.columns:
            return None, "Close price data not available."
            
        return hist['Close'], None
        
    except Exception as e:
        return None, f"Error fetching data: {str(e)}"
