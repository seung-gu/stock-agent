"""Parallel execution helper for Koyfin chart capture."""

import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from .koyfin_chart_capture import KoyfinChartCapture


async def capture_ticker_async(
    ticker: str, 
    headless: bool = False,
    verbose: bool = False
) -> tuple[str, Optional[str]]:
    """
    Capture chart for a single ticker asynchronously.
    
    Args:
        ticker: Stock ticker symbol
        headless: Run in headless mode
        verbose: Print progress messages
    
    Returns:
        Tuple of (ticker, output_path or None)
    """
    loop = asyncio.get_event_loop()
    
    def _capture():
        capturer = KoyfinChartCapture(headless=headless, verbose=verbose)
        return capturer.capture(ticker)
    
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, _capture)
    
    return ticker, result


async def capture_multiple_parallel(
    tickers: list[str],
    headless: bool = False,
    verbose: bool = True
) -> dict[str, Optional[str]]:
    """
    Capture charts for multiple tickers in parallel.
    
    Args:
        tickers: List of ticker symbols
        headless: Run in headless mode
        verbose: Print progress and summary
    
    Returns:
        Dictionary mapping tickers to their output paths (or None if failed)
    """
    if verbose:
        print("\n⚡ PARALLEL MODE")
        print("=" * 80)
    
    start_time = time.time()
    
    # Create tasks for all tickers
    tasks = [
        capture_ticker_async(ticker, headless=headless, verbose=False)
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
        ticker, path = result
        output[ticker] = path
    
    # Print summary
    if verbose:
        print("\n" + "=" * 80)
        print(f"📊 Summary ({elapsed:.1f}s):")
        for ticker in tickers:
            path = output.get(ticker)
            status = "✅" if path else "❌"
            print(f"  {status} {ticker}: {path or 'Failed'}")
        print("=" * 80)
    
    return output

