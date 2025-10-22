from trend_agent import TrendAgent


instructions =  """
LIQUIDITY ANALYSIS FOCUS:
You are a liquidity analyst specializing in treasury yield analysis.

Key Interpretations:
- Rising yields = Tightening liquidity (negative for risk assets like stocks, crypto)
- Falling yields = Loosening liquidity (positive for risk assets)
- Yield volatility = Market uncertainty about liquidity conditions
- Compare yield movements with Fed policy expectations
- Assess implications for stock market, crypto, and risk assets

Focus Areas:
- How yield changes affect borrowing costs
- Impact on equity valuations (discount rates)
- Market liquidity conditions
- Risk appetite indicators
- Credit market implications

CRITICAL TECHNICAL ANALYSIS:
- Pay special attention when prices cross integer percentage levels (1%, 2%, 3%, 4%, etc.)
- These round numbers act as psychological support/resistance levels
- Crossing these levels in the trend direction signals momentum strength
- Breaking through integer levels often triggers increased volatility and trading activity
- Monitor if the price sustains above/below these key levels after crossing
- Example: If trending up from 3.8% to 4.2%, crossing 4% is a significant psychological barrier
"""

class LiquidityTrendAgent(TrendAgent):
    """
    Liquidity-focused trend analysis agent for treasury yields.
    
    Analyzes treasury yield movements with focus on liquidity conditions
    and their impact on risk assets.
    """
    
    def __init__(self, ticker: str):
        """
        Initialize liquidity trend agent.
        
        Args:
            ticker: Treasury ticker symbol (e.g., "^TNX", "^FVX")
        """
        agent_name = f"liquidity_agent_{ticker.replace('^', '').replace('-', '_')}"
        super().__init__(ticker, agent_name, instructions)


# Usage examples
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Example 1: Liquidity analysis (Treasury yields)
        print("=" * 80)
        print("Example 1: Liquidity Analysis (TNX)")
        print("=" * 80)
        tnx_agent = LiquidityTrendAgent("^TNX")
        result = await tnx_agent.run("TNX의 5일, 1개월, 6개월 추세를 분석하고 유동성 관점에서 해석해줘")
        print(result.final_output)
        
    asyncio.run(main())
