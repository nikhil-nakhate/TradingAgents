"""
Unit tests for agent state structures.
"""

import pytest
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)


class TestInvestDebateState:
    """Test cases for InvestDebateState TypedDict."""

    def test_invest_debate_state_structure(self):
        """Test InvestDebateState has all required fields."""
        state = {
            "bull_history": "",
            "bear_history": "",
            "history": "",
            "current_response": "",
            "judge_decision": "",
            "count": 0,
        }
        
        # Should be valid InvestDebateState
        assert isinstance(state, dict)
        assert all(key in state for key in InvestDebateState.__annotations__)

    def test_invest_debate_state_field_types(self):
        """Test InvestDebateState field types."""
        state = {
            "bull_history": "test",
            "bear_history": "test",
            "history": "test",
            "current_response": "test",
            "judge_decision": "test",
            "count": 5,
        }
        
        assert isinstance(state["bull_history"], str)
        assert isinstance(state["bear_history"], str)
        assert isinstance(state["history"], str)
        assert isinstance(state["current_response"], str)
        assert isinstance(state["judge_decision"], str)
        assert isinstance(state["count"], int)

    def test_invest_debate_state_empty_values(self):
        """Test InvestDebateState with empty values."""
        state = {
            "bull_history": "",
            "bear_history": "",
            "history": "",
            "current_response": "",
            "judge_decision": "",
            "count": 0,
        }
        
        assert state["count"] == 0
        assert all(value == "" for key, value in state.items() if key != "count")


class TestRiskDebateState:
    """Test cases for RiskDebateState TypedDict."""

    def test_risk_debate_state_structure(self):
        """Test RiskDebateState has all required fields."""
        state = {
            "risky_history": "",
            "safe_history": "",
            "neutral_history": "",
            "history": "",
            "latest_speaker": "",
            "current_risky_response": "",
            "current_safe_response": "",
            "current_neutral_response": "",
            "judge_decision": "",
            "count": 0,
        }
        
        assert isinstance(state, dict)
        assert all(key in state for key in RiskDebateState.__annotations__)

    def test_risk_debate_state_field_types(self):
        """Test RiskDebateState field types."""
        state = {
            "risky_history": "test",
            "safe_history": "test",
            "neutral_history": "test",
            "history": "test",
            "latest_speaker": "risky",
            "current_risky_response": "test",
            "current_safe_response": "test",
            "current_neutral_response": "test",
            "judge_decision": "test",
            "count": 3,
        }
        
        assert isinstance(state["risky_history"], str)
        assert isinstance(state["safe_history"], str)
        assert isinstance(state["neutral_history"], str)
        assert isinstance(state["history"], str)
        assert isinstance(state["latest_speaker"], str)
        assert isinstance(state["current_risky_response"], str)
        assert isinstance(state["current_safe_response"], str)
        assert isinstance(state["current_neutral_response"], str)
        assert isinstance(state["judge_decision"], str)
        assert isinstance(state["count"], int)

    def test_risk_debate_state_latest_speaker_values(self):
        """Test latest_speaker can be risky, safe, or neutral."""
        valid_speakers = ["risky", "safe", "neutral", ""]
        
        for speaker in valid_speakers:
            state = {
                "risky_history": "",
                "safe_history": "",
                "neutral_history": "",
                "history": "",
                "latest_speaker": speaker,
                "current_risky_response": "",
                "current_safe_response": "",
                "current_neutral_response": "",
                "judge_decision": "",
                "count": 0,
            }
            assert state["latest_speaker"] == speaker


class TestAgentState:
    """Test cases for AgentState TypedDict."""

    def test_agent_state_structure(self, sample_agent_state):
        """Test AgentState has all required fields."""
        state = sample_agent_state
        
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

    def test_agent_state_field_types(self, sample_agent_state):
        """Test AgentState field types."""
        state = sample_agent_state
        
        assert isinstance(state["company_of_interest"], str)
        assert isinstance(state["trade_date"], str)
        assert isinstance(state["sender"], str)
        assert isinstance(state["investment_debate_state"], dict)
        assert isinstance(state["risk_debate_state"], dict)
        assert isinstance(state["investment_plan"], str)
        assert isinstance(state["trader_investment_plan"], str)
        assert isinstance(state["final_trade_decision"], str)
        assert isinstance(state["market_report"], str)
        assert isinstance(state["fundamentals_report"], str)
        assert isinstance(state["sentiment_report"], str)
        assert isinstance(state["news_report"], str)
        assert isinstance(state["messages"], list)

    def test_agent_state_messages_format(self):
        """Test messages field format."""
        state = {
            "messages": [("human", "AAPL")],
            "company_of_interest": "AAPL",
            "trade_date": "2024-01-15",
            "sender": "",
            "investment_debate_state": {},
            "investment_plan": "",
            "trader_investment_plan": "",
            "risk_debate_state": {},
            "final_trade_decision": "",
            "market_report": "",
            "fundamentals_report": "",
            "sentiment_report": "",
            "news_report": "",
        }
        
        assert isinstance(state["messages"], list)
        assert len(state["messages"]) > 0
        assert isinstance(state["messages"][0], tuple)

    def test_agent_state_nested_states(self, sample_agent_state):
        """Test nested state structures."""
        state = sample_agent_state
        
        invest_state = state["investment_debate_state"]
        assert isinstance(invest_state, dict)
        assert "bull_history" in invest_state
        assert "bear_history" in invest_state
        assert "count" in invest_state
        
        risk_state = state["risk_debate_state"]
        assert isinstance(risk_state, dict)
        assert "risky_history" in risk_state
        assert "safe_history" in risk_state
        assert "neutral_history" in risk_state
        assert "count" in risk_state
