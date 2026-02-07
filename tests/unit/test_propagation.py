"""
Unit tests for state propagation functionality.
"""

import pytest
from tradingagents.graph.propagation import Propagator
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)


class TestPropagator:
    """Test cases for Propagator class."""

    def test_propagator_init(self):
        """Test Propagator initialization."""
        propagator = Propagator(max_recur_limit=50)
        assert propagator.max_recur_limit == 50

    def test_propagator_default_init(self):
        """Test Propagator initialization with default values."""
        propagator = Propagator()
        assert propagator.max_recur_limit == 100

    def test_create_initial_state_basic(self, sample_ticker, sample_date):
        """Test create_initial_state creates state with basic fields."""
        propagator = Propagator()
        state = propagator.create_initial_state(sample_ticker, sample_date)
        
        assert state["company_of_interest"] == sample_ticker
        assert state["trade_date"] == sample_date
        assert state["messages"] == [("human", sample_ticker)]
        assert state["sender"] == ""

    def test_create_initial_state_all_fields(self, sample_ticker, sample_date):
        """Test create_initial_state includes all required fields."""
        propagator = Propagator()
        state = propagator.create_initial_state(sample_ticker, sample_date)
        
        # Check all required fields exist
        required_fields = [
            "messages",
            "company_of_interest",
            "trade_date",
            "sender",
            "investment_debate_state",
            "investment_plan",
            "trader_investment_plan",
            "risk_debate_state",
            "final_trade_decision",
            "market_report",
            "fundamentals_report",
            "sentiment_report",
            "news_report",
        ]
        
        for field in required_fields:
            assert field in state, f"Missing required field: {field}"

    def test_create_initial_state_investment_debate_state(self, sample_ticker, sample_date):
        """Test investment_debate_state initialization."""
        propagator = Propagator()
        state = propagator.create_initial_state(sample_ticker, sample_date)
        
        invest_state = state["investment_debate_state"]
        assert isinstance(invest_state, dict)
        
        required_fields = [
            "bull_history",
            "bear_history",
            "history",
            "current_response",
            "judge_decision",
            "count",
        ]
        
        for field in required_fields:
            assert field in invest_state, f"Missing field in investment_debate_state: {field}"
        
        assert invest_state["bull_history"] == ""
        assert invest_state["bear_history"] == ""
        assert invest_state["history"] == ""
        assert invest_state["current_response"] == ""
        assert invest_state["judge_decision"] == ""
        assert invest_state["count"] == 0

    def test_create_initial_state_risk_debate_state(self, sample_ticker, sample_date):
        """Test risk_debate_state initialization."""
        propagator = Propagator()
        state = propagator.create_initial_state(sample_ticker, sample_date)
        
        risk_state = state["risk_debate_state"]
        assert isinstance(risk_state, dict)
        
        required_fields = [
            "risky_history",
            "safe_history",
            "neutral_history",
            "history",
            "latest_speaker",
            "current_risky_response",
            "current_safe_response",
            "current_neutral_response",
            "judge_decision",
            "count",
        ]
        
        for field in required_fields:
            assert field in risk_state, f"Missing field in risk_debate_state: {field}"
        
        assert risk_state["risky_history"] == ""
        assert risk_state["safe_history"] == ""
        assert risk_state["neutral_history"] == ""
        assert risk_state["history"] == ""
        assert risk_state["latest_speaker"] == ""
        assert risk_state["current_risky_response"] == ""
        assert risk_state["current_safe_response"] == ""
        assert risk_state["current_neutral_response"] == ""
        assert risk_state["judge_decision"] == ""
        assert risk_state["count"] == 0

    def test_create_initial_state_different_tickers(self, sample_date):
        """Test create_initial_state with different tickers."""
        propagator = Propagator()
        
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            state = propagator.create_initial_state(ticker, sample_date)
            assert state["company_of_interest"] == ticker
            assert state["messages"] == [("human", ticker)]

    def test_create_initial_state_different_dates(self, sample_ticker):
        """Test create_initial_state with different dates."""
        propagator = Propagator()
        
        dates = ["2024-01-15", "2024-02-20", "2024-03-10"]
        for date in dates:
            state = propagator.create_initial_state(sample_ticker, date)
            assert state["trade_date"] == date

    def test_get_graph_args(self):
        """Test get_graph_args returns correct structure."""
        propagator = Propagator(max_recur_limit=50)
        args = propagator.get_graph_args()
        
        assert isinstance(args, dict)
        assert "stream_mode" in args
        assert "config" in args
        assert args["stream_mode"] == "values"
        assert args["config"]["recursion_limit"] == 50

    def test_get_graph_args_default(self):
        """Test get_graph_args with default recursion limit."""
        propagator = Propagator()
        args = propagator.get_graph_args()
        
        assert args["config"]["recursion_limit"] == 100

    def test_initial_state_report_fields_empty(self, sample_ticker, sample_date):
        """Test that report fields are initialized as empty strings."""
        propagator = Propagator()
        state = propagator.create_initial_state(sample_ticker, sample_date)
        
        report_fields = [
            "market_report",
            "fundamentals_report",
            "sentiment_report",
            "news_report",
            "investment_plan",
            "trader_investment_plan",
            "final_trade_decision",
        ]
        
        for field in report_fields:
            assert state[field] == "", f"Field {field} should be empty string"
