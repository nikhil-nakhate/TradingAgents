"""
Mock data for testing TradingAgents functionality.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List

# Sample stock data
MOCK_STOCK_DATA = {
    "AAPL": {
        "price_data": "AAPL stock price: $175.50\nVolume: 50M\nChange: +2.5%",
        "indicators": "RSI: 65\nMACD: Bullish\nSMA(20): $170\nSMA(50): $165",
        "fundamentals": "Market Cap: 2.8T\nP/E Ratio: 28.5\nRevenue Growth: 8.2%",
        "news": "Apple announces new AI features\nStrong Q4 earnings beat expectations",
    },
    "MSFT": {
        "price_data": "MSFT stock price: $420.30\nVolume: 25M\nChange: +1.8%",
        "indicators": "RSI: 70\nMACD: Bullish\nSMA(20): $415\nSMA(50): $400",
        "fundamentals": "Market Cap: 3.1T\nP/E Ratio: 32.1\nRevenue Growth: 12.5%",
        "news": "Microsoft Azure growth accelerates\nPartnership with OpenAI expands",
    },
    "GOOGL": {
        "price_data": "GOOGL stock price: $155.20\nVolume: 30M\nChange: +3.2%",
        "indicators": "RSI: 68\nMACD: Bullish\nSMA(20): $150\nSMA(50): $145",
        "fundamentals": "Market Cap: 1.9T\nP/E Ratio: 25.8\nRevenue Growth: 10.3%",
        "news": "Google Cloud revenue up 25%\nAI search features launch",
    },
}

# Sample discovery criteria
MOCK_DISCOVERY_CRITERIA = {
    "tech_ai": {
        "sectors": ["Technology"],
        "keywords": ["AI", "artificial intelligence"],
        "market_cap_min": 1_000_000_000,
    },
    "healthcare_growth": {
        "sectors": ["Healthcare"],
        "market_cap_min": 10_000_000_000,
        "fundamentals": {"revenue_growth_min": 0.15},
    },
    "energy": {
        "sectors": ["Energy"],
        "market_cap_min": 2_000_000_000,
    },
}

# Sample ticker lists
MOCK_TICKER_LISTS = {
    "technology": ["AAPL", "MSFT", "GOOGL", "NVDA", "META", "TSLA", "AMD"],
    "healthcare": ["JNJ", "UNH", "PFE", "ABBV", "TMO", "LLY"],
    "energy": ["XOM", "CVX", "COP", "SLB", "EOG"],
}

# Sample analysis results
MOCK_ANALYSIS_RESULTS = [
    {
        "ticker": "AAPL",
        "date": "2024-01-15",
        "screening_score": 85,
        "signals": {
            "momentum_score": 70,
            "volume_trend": 1,
            "technical_score": 80,
            "fundamental_score": 75,
            "sentiment_score": 60,
        },
        "recommendation": "buy",
        "reasoning": "Strong technical indicators with positive momentum",
        "data_available": {
            "price": True,
            "indicators": True,
            "fundamentals": True,
            "news": True,
        },
    },
    {
        "ticker": "MSFT",
        "date": "2024-01-15",
        "screening_score": 82,
        "signals": {
            "momentum_score": 65,
            "volume_trend": 1,
            "technical_score": 75,
            "fundamental_score": 80,
            "sentiment_score": 55,
        },
        "recommendation": "buy",
        "reasoning": "Cloud growth and strong fundamentals",
        "data_available": {
            "price": True,
            "indicators": True,
            "fundamentals": True,
            "news": True,
        },
    },
]

# Sample agent states
MOCK_AGENT_STATE = {
    "messages": [("human", "AAPL")],
    "company_of_interest": "AAPL",
    "trade_date": "2024-01-15",
    "sender": "",
    "investment_debate_state": {
        "bull_history": "Bull: Strong fundamentals and growth potential",
        "bear_history": "Bear: Market volatility concerns",
        "history": "Debate ongoing",
        "current_response": "",
        "judge_decision": "",
        "count": 2,
    },
    "investment_plan": "Invest in AAPL with 5% portfolio allocation",
    "trader_investment_plan": "Buy 100 shares at market price",
    "risk_debate_state": {
        "risky_history": "Risky: Aggressive position recommended",
        "safe_history": "Safe: Conservative approach preferred",
        "neutral_history": "Neutral: Balanced position",
        "history": "Risk debate ongoing",
        "latest_speaker": "neutral",
        "current_risky_response": "",
        "current_safe_response": "",
        "current_neutral_response": "",
        "judge_decision": "",
        "count": 3,
    },
    "final_trade_decision": "APPROVED: Buy 100 shares with stop-loss at $170",
    "market_report": "Market analysis shows bullish trend",
    "fundamentals_report": "Strong financials with growth potential",
    "sentiment_report": "Positive sentiment in social media",
    "news_report": "Recent news is favorable",
}

# Sample LLM responses
MOCK_LLM_RESPONSES = {
    "intent_interpretation": {
        "tech_ai": '{"sectors": ["Technology"], "keywords": ["AI"], "market_cap_min": 1000000000}',
        "healthcare": '{"sectors": ["Healthcare"], "market_cap_min": 10000000000}',
    },
    "screening_analysis": '{"screening_score": 85, "signals": {"momentum_score": 70, "volume_trend": 1, "technical_score": 80, "fundamental_score": 75, "sentiment_score": 60}, "recommendation": "buy", "reasoning": "Strong technical indicators"}',
}

# Sample dates
def get_test_date(days_ago: int = 7) -> str:
    """Get a test date string."""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d")
