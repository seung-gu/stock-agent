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
) -> tuple[str, Optional[str], Optional[str]]:
    """
    Capture chart for a single ticker asynchronously.
    
    Args:
        ticker: Stock ticker symbol
        headless: Run in headless mode
        verbose: Print progress messages
        period: Chart period ('1Y', '3Y', '5Y', '10Y', '20Y')
    
    Returns:
        Tuple of (ticker, chart_path, metrics_str)
    """
    loop = asyncio.get_event_loop()
    
    def _capture():
        capturer = KoyfinChartCapture(headless=headless, verbose=verbose)
        return capturer.capture(ticker, period=period)
    
    with ThreadPoolExecutor() as executor:
        chart_path, metrics = await loop.run_in_executor(executor, _capture)
    
    return ticker, chart_path, metrics


async def capture_multiple_parallel(
    tickers: list[str],
    headless: bool = False,
    verbose: bool = True,
    period: str = '10Y'
) -> dict[str, tuple[Optional[str], Optional[str]]]:
    """
    Capture charts for multiple tickers in parallel.
    
    Args:
        tickers: List of ticker symbols
        headless: Run in headless mode
        verbose: Print progress and summary
        period: Chart period ('1Y', '3Y', '5Y', '10Y', '20Y')
    
        Returns:
        Dictionary mapping tickers to (chart_path, metrics_str) tuples
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
        ticker, chart_path, metrics_str = result
        output[ticker] = (chart_path, metrics_str)
    
    # Print summary
    if verbose:
        print("\n" + "=" * 80)
        print(f"📊 Summary ({elapsed:.1f}s):")
        for ticker in tickers:
            result = output.get(ticker)
            if result:
                chart_path, metrics_str = result
                status = "✅" if chart_path else "❌"
                metrics_display = f" | {metrics_str}" if metrics_str else ""
                print(f"  {status} {ticker}: {chart_path or 'Failed'}{metrics_display}")
            else:
                print(f"  ❌ {ticker}: Failed (not in results)")
        print("=" * 80)
    
    return output