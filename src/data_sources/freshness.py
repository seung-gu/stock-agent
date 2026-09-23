"""Tracks how old each source's latest data point is, so one run can report on all of them.

A scrape that fails falls back to cache (see WebDataSource._fetch_with_cache_and_scrape),
which keeps the report running but says nothing about how old the fallback is. With no
cache to fall back on it raises instead, and OrchestratorAgent.add_sub_agent swallows that
— the report simply comes out without that section. Both look like success from outside,
so a run declares what it needs up front and reports what it did not get.
"""

from pathlib import Path


# symbol -> (as_of, age_days, limit_days), for symbols a fetch actually reached
_seen: dict[str, tuple[str, int, int]] = {}

# symbols this run depends on, recorded before the fetch that may never return
_expected: set[str] = set()


def expect(symbol: str) -> None:
    """Declare that this run needs `symbol`, so a fetch that dies is still noticed."""
    _expected.add(symbol)


def record(symbol: str, as_of: str, age_days: int, limit_days: int | None) -> bool:
    """Record one fetch. Returns True when what it served is older than the source allows.

    Periods for one symbol are fetched concurrently and may not all take the same path —
    one can serve cache while another scrapes successfully. Keep the newest reading so the
    run's verdict does not depend on which thread finished last.
    """
    if limit_days is None:
        return False
    previous = _seen.get(symbol)
    if previous is None or as_of > previous[0]:
        _seen[symbol] = (as_of, age_days, limit_days)
    return age_days > limit_days


def stale() -> dict[str, tuple[str, int, int]]:
    """Symbols whose latest point is older than their source allows."""
    return {s: v for s, v in _seen.items() if v[1] > v[2]}


def missing() -> set[str]:
    """Symbols the run declared but never got a reading for."""
    return _expected - set(_seen)


def write_report(path: str | Path) -> list[str]:
    """Write one line per problem symbol. The file is empty when every source is current."""
    lines = [
        f"{symbol}: as of {as_of}, {age} days old (limit {limit})"
        for symbol, (as_of, age, limit) in sorted(stale().items())
    ] + [
        f"{symbol}: no data this run, the fetch never returned"
        for symbol in sorted(missing())
    ]
    Path(path).write_text(''.join(f"{line}\n" for line in lines))
    return lines
