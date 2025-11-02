"""
Technical indicators for financial data analysis.

Provides functions for calculating various technical indicators including
moving averages, disparity (이격도), RSI, and MACD.
"""

import pandas as pd


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


