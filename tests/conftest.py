"""
Shared pytest fixtures for TradingAgents tests.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock
from typing import Dict, Any

from tradingagents.default_config import DEFAULT_CONFIG
from tests.fixtures.mock_data import (
    MOCK_STOCK_DATA,
    MOCK_DISCOVERY_CRITERIA,
    MOCK_TICKER_LISTS,
    MOCK_ANALYSIS_RESULTS,
    MOCK_AGENT_STATE,
    MOCK_LLM_RESPONSES,
    get_test_date,
)


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Return a sample configuration dictionary."""
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "openai"
    config["deep_think_llm"] = "gpt-4o-mini"
    config["quick_think_llm"] = "gpt-4o-mini"
    config["backend_url"] = "https://api.openai.com/v1"
    return config


@pytest.fixture
def temp_results_dir():
    """Create a temporary directory for test results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_llm():
    """Create a mock LLM instance."""
    llm = MagicMock()
    
    # Mock invoke method to return a response with content
    def mock_invoke(messages):
        response = MagicMock()
        # Return appropriate content based on message content
        if messages and len(messages) > 0:
            last_msg = messages[-1]
            if isinstance(last_msg, dict):
                content = last_msg.get("content", "")
            else:
                content = getattr(last_msg, "content", "")
            
            if "intent" in str(content).lower() or "criteria" in str(content).lower():
                response.content = MOCK_LLM_RESPONSES["intent_interpretation"]["tech_ai"]
            elif "screening" in str(content).lower() or "analysis" in str(content).lower():
                response.content = MOCK_LLM_RESPONSES["screening_analysis"]
            else:
                response.content = '{"result": "test response"}'
        else:
            response.content = '{"result": "default response"}'
        
        return response
    
    llm.invoke = mock_invoke
    return llm


@pytest.fixture
def mock_openai_llm():
    """Create a mock OpenAI LLM."""
    from langchain_openai import ChatOpenAI
    
    llm = MagicMock(spec=ChatOpenAI)
    llm.model_name = "gpt-4o-mini"
    
    def mock_invoke(messages):
        response = MagicMock()
        response.content = '{"sectors": ["Technology"], "market_cap_min": 1000000000}'
        return response
    
    llm.invoke = mock_invoke
    return llm


@pytest.fixture
def mock_anthropic_llm():
    """Create a mock Anthropic LLM."""
    from langchain_anthropic import ChatAnthropic
    
    llm = MagicMock(spec=ChatAnthropic)
    llm.model = "claude-3-5-haiku-latest"
    
    def mock_invoke(messages):
        response = MagicMock()
        response.content = '{"sectors": ["Technology"], "market_cap_min": 1000000000}'
        return response
    
    llm.invoke = mock_invoke
    return llm


@pytest.fixture
def mock_google_llm():
    """Create a mock Google LLM."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    llm = MagicMock(spec=ChatGoogleGenerativeAI)
    llm.model_name = "gemini-2.0-flash"
    
    def mock_invoke(messages):
        response = MagicMock()
        response.content = '{"sectors": ["Technology"], "market_cap_min": 1000000000}'
        return response
    
    llm.invoke = mock_invoke
    return llm


@pytest.fixture
def sample_agent_state() -> Dict[str, Any]:
    """Return a sample agent state."""
    return MOCK_AGENT_STATE.copy()


@pytest.fixture
def sample_ticker() -> str:
    """Return a sample ticker symbol."""
    return "AAPL"


@pytest.fixture
def sample_date() -> str:
    """Return a sample date string."""
    return get_test_date(7)


@pytest.fixture
def sample_discovery_criteria() -> Dict[str, Any]:
    """Return sample discovery criteria."""
    return MOCK_DISCOVERY_CRITERIA["tech_ai"].copy()


@pytest.fixture
def sample_ticker_list() -> list:
    """Return a sample list of tickers."""
    return MOCK_TICKER_LISTS["technology"].copy()


@pytest.fixture
def sample_analysis_result() -> Dict[str, Any]:
    """Return a sample analysis result."""
    return MOCK_ANALYSIS_RESULTS[0].copy()


@pytest.fixture
def mock_stock_data():
    """Return mock stock data."""
    return MOCK_STOCK_DATA


@pytest.fixture
def mock_message_buffer():
    """Create a mock message buffer instance."""
    from cli.main import MessageBuffer
    
    buffer = MessageBuffer(max_length=100)
    return buffer


@pytest.fixture
def mock_propagator():
    """Create a Propagator instance."""
    from tradingagents.graph.propagation import Propagator
    
    return Propagator(max_recur_limit=100)


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "test-key")
    monkeypatch.setenv("TRADINGAGENTS_RESULTS_DIR", "./test_results")


@pytest.fixture
def mock_yfinance_data(monkeypatch):
    """Mock yfinance data fetching."""
    def mock_get_data(*args, **kwargs):
        return MOCK_STOCK_DATA.get("AAPL", {}).get("price_data", "")
    
    monkeypatch.setattr(
        "tradingagents.dataflows.y_finance.get_YFin_data_online",
        mock_get_data
    )


@pytest.fixture
def mock_route_to_vendor(monkeypatch):
    """Mock route_to_vendor function."""
    def mock_route(method, *args, **kwargs):
        if method == "get_stock_data":
            return MOCK_STOCK_DATA.get("AAPL", {}).get("price_data", "")
        elif method == "get_indicators":
            return MOCK_STOCK_DATA.get("AAPL", {}).get("indicators", "")
        elif method == "get_fundamentals":
            return MOCK_STOCK_DATA.get("AAPL", {}).get("fundamentals", "")
        elif method == "get_news":
            return MOCK_STOCK_DATA.get("AAPL", {}).get("news", "")
        return ""
    
    monkeypatch.setattr(
        "tradingagents.dataflows.interface.route_to_vendor",
        mock_route
    )


@pytest.fixture
def mock_discover_tickers(monkeypatch):
    """Mock discover_tickers function."""
    def mock_discover(criteria):
        return MOCK_TICKER_LISTS.get("technology", [])
    
    monkeypatch.setattr(
        "tradingagents.discovery.ticker_screener.discover_tickers_by_criteria",
        mock_discover
    )
