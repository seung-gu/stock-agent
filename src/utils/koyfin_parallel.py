"""Parallel execution helper for Koyfin chart capture."""

import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from .koyfin_chart_capture import KoyfinChartCapture


async def capture_ticker_async(
    ticker: str, 
    headless: bool = False,
    verbose: bool = False,
    period: str = '10Y'
) -> tuple[str, Optional[str], Optional[float]]:
    """
    Capture chart for a single ticker asynchronously.
    
    Args:
        ticker: Stock ticker symbol
        headless: Run in headless mode
        verbose: Print progress messages
        period: Chart period ('1Y', '3Y', '5Y', '10Y', '20Y')
    
    Returns:
        Tuple of (ticker, chart_path, pe_value)
    """
    loop = asyncio.get_event_loop()
    
    def _capture():
        capturer = KoyfinChartCapture(headless=headless, verbose=verbose)
        return capturer.capture(ticker, period=period)
    
    with ThreadPoolExecutor() as executor:
        chart_path, pe_value = await loop.run_in_executor(executor, _capture)
    
    return ticker, chart_path, pe_value


async def capture_multiple_parallel(
    tickers: list[str],
    headless: bool = False,
    verbose: bool = True,
    period: str = '10Y'
) -> dict[str, tuple[Optional[str], Optional[float]]]:
    """
    Capture charts for multiple tickers in parallel.
    
    Args:
        tickers: List of ticker symbols
        headless: Run in headless mode
        verbose: Print progress and summary
        period: Chart period ('1Y', '3Y', '5Y', '10Y', '20Y')
    
    Returns:
        Dictionary mapping tickers to (chart_path, pe_value) tuples
    """
    if verbose:
        print("\n⚡ PARALLEL MODE")
        print("=" * 80)
    
    start_time = time.time()
    
    # Create tasks for all tickers
    tasks = [
        capture_ticker_async(ticker, headless=headless, verbose=False, period=period)
        for ticker in tickers
    ]
    
    # Execute in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = time.time() - start_time
    
    # Process results
    output = {}
    for result in results:
        if isinstance(result, Exception):
            if verbose:
                print(f"❌ Error: {result}")
            continue
        ticker, (chart_path, pe_value) = result
        output[ticker] = (chart_path, pe_value)
    
    # Print summary
    if verbose:
        print("\n" + "=" * 80)
        print(f"📊 Summary ({elapsed:.1f}s):")
        for ticker in tickers:
            result = output.get(ticker)
            if result:
                chart_path, pe_value = result
                status = "✅" if chart_path else "❌"
                pe_str = f" | P/E: {pe_value:.2f}x" if pe_value else ""
                print(f"  {status} {ticker}: {chart_path or 'Failed'}{pe_str}")
            else:
                print(f"  ❌ {ticker}: Failed (not in results)")
        print("=" * 80)
    
    return output