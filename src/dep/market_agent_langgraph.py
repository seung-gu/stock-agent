"""
Check market conditions to make trading decisions.
"""


import io
import os
import datetime
from PIL import Image
from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import finnhub

from langgraph.prebuilt import create_react_agent  # self-thought agent
from langgraph.graph import MessagesState
from langgraph.types import Command
from typing import Literal

from langchain.tools import tool

from langchain_community.agent_toolkits.polygon.toolkit import PolygonToolkit
from langchain_community.utilities.polygon import PolygonAPIWrapper
from pydantic import BaseModel

load_dotenv()

#llm = ChatOpenAI(model='gpt-4o', temperature=0.1)
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', temperature=0.1)
small_llm = ChatOpenAI(model='openai:gpt-4o', temperature=0.1)

# Finnhub API 클라이언트 초기화 (API 키는 환경변수에서 불러옴)
finnhub_client = finnhub.Client(api_key=os.getenv('FINNHUB_API_KEY'))

@tool
def get_stock_price_from_finnhub(ticker: str) -> dict:
    """Given a stock ticker, return the price data for the past 5 days using Finnhub API"""
    candles = finnhub_client.stock_candles(ticker, 'D', int((datetime.datetime.now() - datetime.timedelta(days=7)).timestamp()), int(datetime.datetime.now().timestamp()))
    return candles

@tool
def get_stock_price_from_yfinance(ticker: str) -> dict:
    """Given a stock ticker, return the stock price data for the past month using yfinance"""
    import yfinance as yf
    from curl_cffi import requests
   # session = requests.Session(impersonate="chrome")
   # ticker = yf.Ticker(ticker, session=session)
    stock_info = yf.download(ticker, period='1mo').to_dict()
    return stock_info


class LiquidityAgent:
    """A class to check liquidity of market."""
    prompt = """
    You are a financial analyst tasked with checking the liquidity of a stock.
    check liquidity of a stock. Given the following information.
    get a ticker of TBX (it's not a stock, it's a treasury) to get the liquidity of the stock.
    If the trend of a month is up, then the liquidity is good.
    If the trend of a month is down, then the liquidity is bad.
    """
    liquidity_agent = create_react_agent(
        llm, tools=[get_stock_price_from_yfinance], prompt=prompt
    )

    @classmethod
    def check_node(cls, state: MessagesState) -> Command[Literal["supervisor"]]:
        result = cls.liquidity_agent.invoke(state)
        return Command(
            update={'messages': [HumanMessage(content=result['messages'][-1].content, name='liquidity_check')]},
            goto='supervisor'
        )



class OilPriceAgent:
    """A class to check oil price of a stock."""
    prompt = """
    You are a financial analyst tasked with checking the oil price of market.
    check oil price given the following information.
    Get a ticker of WTI (it's not a stock) to get the oil price.
    Check the trend of oil price for a month.
    """
    oil_price_agent = create_react_agent(
        llm, tools=[get_stock_price_from_yfinance], prompt=prompt
    )

    @classmethod
    def check_node(cls, state: MessagesState) -> Command[Literal["supervisor"]]:
        result = cls.oil_price_agent.invoke(state)
        return Command(
            update={'messages': [HumanMessage(content=result['messages'][-1].content, name='oil_price_check')]},
            goto='supervisor'
        )

def oil_price_analysis(state: MessagesState):
    """
    국제 유가 상승 -> 미국 인플레이션 -> 미국 소비 지표 상승(FRED Real PCE)
    -> 한국 수출 증가 (한국 경제는 무역수지에 민감)
    :param state:
    :return:
    """
    get_stock_price_from_finnhub('')



from typing import Literal
from typing_extensions import TypedDict

from langgraph.graph import MessagesState, END
from langgraph.types import Command


members = ["oil_price_check", "liquidity_check"]
options = members + ["FINISH"]

system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    f" following workers: {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. "
    " Always respond with the worker name as keyword to act next,"
    " or FINISH if no further action is needed."
    " Do not respond with any other text or explanation. Always respond only with the worker name at all costs."
)


class Router(BaseModel):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal[*options]


def supervisor_node(state: MessagesState) -> Command[Literal[*members, "analyst"]]:
    """
    supervisor node입니다. 주어진 State를 기반으로 각 worker의 결과를 종합하고,
    다음에 수행할 worker를 결정합니다. 모든 작업이 완료되면 analyst node로 이동합니다.

    Args:
        state (MessagesState): 현재 메시지 상태를 나타내는 객체입니다.

    Returns:
        Command: 다음에 수행할 worker 또는 analyst node로 이동하기 위한 명령을 반환합니다.
    """
    messages = [
                   {"role": "system", "content": system_prompt},
               ] + state["messages"]
    #output_parser = PydanticOutputParser(pydantic_object=Router)
    response = llm.invoke(messages)
    print(response.usage_metadata)
    goto = response.content.strip()
    if goto == "FINISH":
        goto = "analyst"

    return Command(goto=goto)


from langchain_core.prompts import PromptTemplate





def analyst_node(state: MessagesState):
    """
    분석가 node입니다. 주어진 State를 기반으로 분석가 체인을 호출하고,
    결과 메시지를 반환합니다.

    Args:
        state (MessagesState): 현재 메시지 상태를 나타내는 객체입니다.
    Returns:
        dict: 분석 결과 메시지를 포함하는 딕셔너리를 반환합니다.
    """

    analyst_prompt = PromptTemplate.from_template(
        """You are a stock market analyst. Given the following information, 
    Please decide whether to invest stocks or not.
    Always explain in Korean.
    Information:
    {messages}"""
    )

    analyst_chain = analyst_prompt | llm
    result = analyst_chain.invoke({'messages': state['messages'][1:]})  # omit the system prompt

    return {'messages': [result]}


from langgraph.graph import StateGraph, START

graph_builder = StateGraph(MessagesState)

graph_builder.add_node("supervisor", supervisor_node)
graph_builder.add_node("liquidity_check", LiquidityAgent.check_node)
graph_builder.add_node("oil_price_check", OilPriceAgent.check_node)
graph_builder.add_node("analyst", analyst_node)

graph_builder.add_edge(START, "supervisor")
graph_builder.add_edge("analyst", END)

graph = graph_builder.compile()


img_bytes = graph.get_graph().draw_mermaid_png()
img = Image.open(io.BytesIO(img_bytes))
img.show()


for chunk in graph.stream({"messages": [("user", "Snowflake를 투자하려하는데, "
                                                 "시장 상황 조사를 해주세요. 시장의 유동성과 국제 유가를 체크해주세요.")]}, stream_mode="values"):
    chunk['messages'][-1].pretty_print()

