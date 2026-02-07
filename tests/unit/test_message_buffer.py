"""
Unit tests for MessageBuffer functionality.
"""

import pytest
from cli.main import MessageBuffer


class TestMessageBuffer:
    """Test cases for MessageBuffer class."""

    def test_message_buffer_init(self):
        """Test MessageBuffer initialization."""
        buffer = MessageBuffer(max_length=50)
        assert buffer.max_length == 50
        assert len(buffer.messages) == 0
        assert len(buffer.tool_calls) == 0
        assert buffer.current_report is None
        assert buffer.final_report is None

    def test_message_buffer_default_init(self):
        """Test MessageBuffer initialization with default max_length."""
        buffer = MessageBuffer()
        assert buffer.max_length == 100

    def test_add_message(self):
        """Test adding messages to buffer."""
        buffer = MessageBuffer()
        buffer.add_message("System", "Test message")
        
        assert len(buffer.messages) == 1
        timestamp, msg_type, content = buffer.messages[0]
        assert msg_type == "System"
        assert content == "Test message"
        assert isinstance(timestamp, str)

    def test_add_multiple_messages(self):
        """Test adding multiple messages."""
        buffer = MessageBuffer()
        buffer.add_message("System", "Message 1")
        buffer.add_message("Reasoning", "Message 2")
        buffer.add_message("Tool", "Message 3")
        
        assert len(buffer.messages) == 3

    def test_add_tool_call(self):
        """Test adding tool calls to buffer."""
        buffer = MessageBuffer()
        buffer.add_tool_call("get_stock_data", {"ticker": "AAPL"})
        
        assert len(buffer.tool_calls) == 1
        timestamp, tool_name, args = buffer.tool_calls[0]
        assert tool_name == "get_stock_data"
        assert args == {"ticker": "AAPL"}
        assert isinstance(timestamp, str)

    def test_add_multiple_tool_calls(self):
        """Test adding multiple tool calls."""
        buffer = MessageBuffer()
        buffer.add_tool_call("get_stock_data", {"ticker": "AAPL"})
        buffer.add_tool_call("get_indicators", {"ticker": "MSFT"})
        
        assert len(buffer.tool_calls) == 2

    def test_update_agent_status(self):
        """Test updating agent status."""
        buffer = MessageBuffer()
        buffer.update_agent_status("Market Analyst", "in_progress")
        
        assert buffer.agent_status["Market Analyst"] == "in_progress"
        assert buffer.current_agent == "Market Analyst"

    def test_update_agent_status_multiple(self):
        """Test updating multiple agent statuses."""
        buffer = MessageBuffer()
        buffer.update_agent_status("Market Analyst", "in_progress")
        buffer.update_agent_status("Market Analyst", "completed")
        buffer.update_agent_status("Social Analyst", "in_progress")
        
        assert buffer.agent_status["Market Analyst"] == "completed"
        assert buffer.agent_status["Social Analyst"] == "in_progress"

    def test_update_agent_status_invalid(self):
        """Test updating status for invalid agent."""
        buffer = MessageBuffer()
        original_status = buffer.agent_status.copy()
        buffer.update_agent_status("Invalid Agent", "in_progress")
        
        # Status should not change for invalid agent
        assert buffer.agent_status == original_status

    def test_update_report_section(self):
        """Test updating report sections."""
        buffer = MessageBuffer()
        buffer.update_report_section("market_report", "Market analysis content")
        
        assert buffer.report_sections["market_report"] == "Market analysis content"
        assert buffer.current_report is not None

    def test_update_multiple_report_sections(self):
        """Test updating multiple report sections."""
        buffer = MessageBuffer()
        buffer.update_report_section("market_report", "Market content")
        buffer.update_report_section("sentiment_report", "Sentiment content")
        
        assert buffer.report_sections["market_report"] == "Market content"
        assert buffer.report_sections["sentiment_report"] == "Sentiment content"

    def test_update_report_section_invalid(self):
        """Test updating invalid report section."""
        buffer = MessageBuffer()
        buffer.update_report_section("invalid_section", "Content")
        
        # Should not add invalid section
        assert "invalid_section" not in buffer.report_sections

    def test_update_current_report_formatting(self):
        """Test current report formatting."""
        buffer = MessageBuffer()
        buffer.update_report_section("market_report", "Test market analysis")
        
        assert buffer.current_report is not None
        assert "Market Analysis" in buffer.current_report
        assert "Test market analysis" in buffer.current_report

    def test_update_final_report_aggregation(self):
        """Test final report aggregates all sections."""
        buffer = MessageBuffer()
        buffer.update_report_section("market_report", "Market content")
        buffer.update_report_section("sentiment_report", "Sentiment content")
        buffer.update_report_section("investment_plan", "Investment plan")
        
        assert buffer.final_report is not None
        assert "Market content" in buffer.final_report
        assert "Sentiment content" in buffer.final_report
        assert "Investment plan" in buffer.final_report

    def test_message_buffer_max_length(self):
        """Test message buffer respects max_length limit."""
        buffer = MessageBuffer(max_length=3)
        
        buffer.add_message("System", "Message 1")
        buffer.add_message("System", "Message 2")
        buffer.add_message("System", "Message 3")
        buffer.add_message("System", "Message 4")
        
        assert len(buffer.messages) == 3
        # Should keep the last 3 messages
        assert buffer.messages[-1][2] == "Message 4"

    def test_tool_call_buffer_max_length(self):
        """Test tool call buffer respects max_length limit."""
        buffer = MessageBuffer(max_length=2)
        
        buffer.add_tool_call("tool1", {})
        buffer.add_tool_call("tool2", {})
        buffer.add_tool_call("tool3", {})
        
        assert len(buffer.tool_calls) == 2
        # Should keep the last 2 tool calls
        assert buffer.tool_calls[-1][1] == "tool3"

    def test_agent_status_initialization(self):
        """Test agent status is initialized correctly."""
        buffer = MessageBuffer()
        
        expected_agents = [
            "Market Analyst",
            "Social Analyst",
            "News Analyst",
            "Fundamentals Analyst",
            "Bull Researcher",
            "Bear Researcher",
            "Research Manager",
            "Trader",
            "Risky Analyst",
            "Neutral Analyst",
            "Safe Analyst",
            "Portfolio Manager",
        ]
        
        for agent in expected_agents:
            assert agent in buffer.agent_status
            assert buffer.agent_status[agent] == "pending"

    def test_report_sections_initialization(self):
        """Test report sections are initialized correctly."""
        buffer = MessageBuffer()
        
        expected_sections = [
            "market_report",
            "sentiment_report",
            "news_report",
            "fundamentals_report",
            "investment_plan",
            "trader_investment_plan",
            "final_trade_decision",
        ]
        
        for section in expected_sections:
            assert section in buffer.report_sections
            assert buffer.report_sections[section] is None

    def test_current_report_shows_latest_section(self):
        """Test current report shows the most recently updated section."""
        buffer = MessageBuffer()
        buffer.update_report_section("market_report", "Market 1")
        buffer.update_report_section("sentiment_report", "Sentiment 1")
        
        # Current report should show sentiment (most recent)
        assert "Sentiment" in buffer.current_report
        assert "Sentiment 1" in buffer.current_report
