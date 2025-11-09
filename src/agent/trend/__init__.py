"""Trend analysis agents"""

from .tnx_agent import TNXAgent
from .nfci_agent import NFCIAgent
from .dx_agent import DXAgent
from .equity_agent import EquityTrendAgent
from .market_breadth_agent import MarketBreadthAgent
from .bull_bear_spread_agent import BullBearSpreadAgent
from .put_call_agent import PutCallAgent
from .margin_debt_agent import MarginDebtAgent
from .high_yield_spread_agent import HighYieldSpreadAgent
from .vix_agent import VIXAgent

__all__ = [
    "TNXAgent",
    "NFCIAgent",
    "DXAgent",
    "EquityTrendAgent",
    "MarketBreadthAgent",
    "BullBearSpreadAgent",
    "PutCallAgent",
    "MarginDebtAgent",
    "HighYieldSpreadAgent",
    "VIXAgent"
]

