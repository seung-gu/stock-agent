"""
Technical indicators for financial data analysis.

Provides functions for calculating various technical indicators including
moving averages, disparity (이격도), and market breadth metrics.
"""

import pandas as pd
import yfinance as yf
import random


def calculate_sma(data: pd.DataFrame, window: int, price_column: str = 'Close') -> pd.Series:
    """
    Calculate Simple Moving Average (SMA) for given data.
    
    Args:
        data: DataFrame with price data
        window: Moving average window (e.g., 20, 50, 200)
        price_column: Column name for price data (default: 'Close')
        
    Returns:
        Series with SMA values
    """
    return data[price_column].rolling(window=window).mean()


def calculate_ema(data: pd.DataFrame, window: int, price_column: str = 'Close') -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA) for given data.
    
    Args:
        data: DataFrame with price data
        window: Moving average window (e.g., 20, 50, 200)
        price_column: Column name for price data (default: 'Close')
        
    Returns:
        Series with EMA values
    """
    return data[price_column].ewm(span=window).mean()


def calculate_disparity(data: pd.DataFrame, window: int, price_column: str = 'Close') -> pd.Series:
    """
    Calculate disparity (이격도) for given data.
    
    Formula: (Current Price / SMA - 1) * 100
    
    Args:
        data: DataFrame with price data
        window: Moving average window (e.g., 20, 50, 200)
        price_column: Column name for price data (default: 'Close')
        
    Returns:
        Series with disparity values
    """
    sma = calculate_sma(data, window=window, price_column=price_column)
    return (data[price_column] / sma - 1) * 100


def calculate_rsi(data: pd.DataFrame, window: int = 14, price_column: str = 'Close') -> pd.Series:
    """
    Calculate Relative Strength Index (RSI) for given data.
    
    Args:
        data: DataFrame with price data
        window: RSI window (default: 14)
        price_column: Column name for price data (default: 'Close')
        
    Returns:
        Series with RSI values (0-100)
    """
    delta = data[price_column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, 
                   price_column: str = 'Close') -> dict[str, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence) for given data.
    
    Args:
        data: DataFrame with price data
        fast: Fast EMA window (default: 12)
        slow: Slow EMA window (default: 26)
        signal: Signal line EMA window (default: 9)
        price_column: Column name for price data (default: 'Close')
        
    Returns:
        Dictionary with 'macd', 'signal', and 'histogram' Series
    """
    ema_fast = calculate_ema(data, window=fast, price_column=price_column)
    ema_slow = calculate_ema(data, window=slow, price_column=price_column)
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def get_market_breadth_sample(sample_size: int = 50) -> dict[str, float]:
    """
    Calculate market breadth using random sample of S&P 500 stocks.
    
    Args:
        sample_size: Number of stocks to sample (default: 50)
        
    Returns:
        Dictionary with market breadth metrics
    """
    # Get S&P 500 list
    sp500 = pd.read_csv('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    tickers = random.sample(sp500['Symbol'].tolist(), sample_size)
    
    above_200ma = 0
    total_stocks = 0
    disparities = []
    
    for ticker in tickers:
        try:
            data = yf.download(ticker, period="1y", progress=False)
            if len(data) >= 200:
                # Calculate 200-day disparity
                disparity = calculate_disparity(data, window=200)
                current_disparity = disparity.iloc[-1]
                
                if not pd.isna(current_disparity):
                    disparities.append(current_disparity)
                    
                    # Check if above 200-day MA (disparity > 0)
                    if current_disparity > 0:
                        above_200ma += 1
                    total_stocks += 1
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    if total_stocks == 0:
        return {
            'percent_above_200ma': 0.0,
            'total_stocks': 0,
            'average_disparity': 0.0,
            'median_disparity': 0.0
        }
    
    return {
        'percent_above_200ma': (above_200ma / total_stocks) * 100,
        'total_stocks': total_stocks,
        'average_disparity': sum(disparities) / len(disparities) if disparities else 0.0,
        'median_disparity': sorted(disparities)[len(disparities)//2] if disparities else 0.0
    }


def get_sector_breadth(sectors: list = None) -> dict[str, dict[str, float]]:
    """
    Calculate market breadth for specific sectors.
    
    Args:
        sectors: List of sector ETFs (default: major sectors)
        
    Returns:
        Dictionary with sector breadth metrics
    """
    if sectors is None:
        sectors = ['XLK', 'XLF', 'XLV', 'XLE', 'XLI', 'XLY', 'XLP', 'XLU', 'XLRE', 'XLB', 'XLC']
    
    sector_breadth = {}
    
    for sector in sectors:
        try:
            data = yf.download(sector, period="1y", progress=False)
            if len(data) >= 200:
                disparity = calculate_disparity(data, window=200)
                current_disparity = disparity.iloc[-1]
                
                if not pd.isna(current_disparity):
                    sector_breadth[sector] = {
                        'disparity_200': current_disparity,
                        'above_200ma': current_disparity > 0,
                        'current_price': data['Close'].iloc[-1],
                        'sma_200': data['Close'].rolling(200).mean().iloc[-1]
                    }
        except Exception as e:
            print(f"Error processing {sector}: {e}")
            continue
    
    return sector_breadth
