"""
Integration tests for CLI functionality.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path
from cli.main import (
    get_user_selections,
    run_analysis,
    MessageBuffer,
    create_layout,
    update_display,
)
from cli.models import AnalystType
from tests.fixtures.mock_data import MOCK_TICKER_LISTS, MOCK_ANALYSIS_RESULTS


class TestGetUserSelections:
    """Test cases for get_user_selections function."""

    @patch("cli.utils.select_deep_thinking_agent")
    @patch("cli.utils.select_shallow_thinking_agent")
    @patch("cli.utils.select_llm_provider")
    @patch("cli.utils.select_research_depth")
    @patch("cli.utils.select_analysts")
    @patch("cli.utils.get_analysis_date")
    @patch("cli.utils.get_ticker")
    @patch("cli.main.typer.prompt")
    def test_get_user_selections_direct_mode(
        self,
        mock_prompt,
        mock_get_ticker,
        mock_get_date,
        mock_select_analysts,
        mock_select_depth,
        mock_select_provider,
        mock_select_shallow,
        mock_select_deep,
    ):
        """Test get_user_selections in direct mode."""
        # Mock all user inputs
        mock_prompt.return_value = "direct"  # Mode selection
        mock_get_ticker.return_value = "AAPL"
        mock_get_date.return_value = "2024-01-15"
        mock_select_analysts.return_value = [AnalystType.MARKET]
        mock_select_depth.return_value = 1
        mock_select_provider.return_value = ("OpenAI", "https://api.openai.com/v1")
        mock_select_shallow.return_value = "gpt-4o-mini"
        mock_select_deep.return_value = "gpt-4o-mini"
        
        selections = get_user_selections()
        
        assert selections["ticker"] == "AAPL"
        assert selections["analysis_date"] == "2024-01-15"
        assert len(selections["analysts"]) == 1
        assert selections["research_depth"] == 1
        assert selections["llm_provider"] == "openai"

    @patch("tradingagents.discovery.filter_top_candidates")
    @patch("tradingagents.discovery.batch_analyze_tickers")
    @patch("tradingagents.discovery.create_screening_config")
    @patch("tradingagents.discovery.discover_tickers")
    @patch("tradingagents.discovery.interpret_user_intent")
    @patch("tradingagents.discovery.lightweight_analyzer._get_llm")
    @patch("cli.utils.select_deep_thinking_agent")
    @patch("cli.utils.select_shallow_thinking_agent")
    @patch("cli.utils.select_llm_provider")
    @patch("cli.utils.select_research_depth")
    @patch("cli.utils.select_analysts")
    @patch("cli.utils.get_analysis_date")
    @patch("cli.main.typer.prompt")
    def test_get_user_selections_discovery_mode(
        self,
        mock_prompt,
        mock_get_date,
        mock_select_analysts,
        mock_select_depth,
        mock_select_provider,
        mock_select_shallow,
        mock_select_deep,
        mock_get_llm,
        mock_interpret,
        mock_discover,
        mock_create_screening_config,
        mock_batch_analyze_tickers,
        mock_filter_top_candidates,
    ):
        """Test get_user_selections in discovery mode."""
        # Mock mode selection and discovery inputs
        mock_prompt.side_effect = [
            "discovery",  # Mode
            "tech stocks with AI",  # Intent
            "AAPL",  # Ticker selection
        ]
        mock_get_date.return_value = "2024-01-15"
        mock_select_analysts.return_value = [AnalystType.MARKET]
        mock_select_depth.return_value = 1
        mock_select_provider.return_value = ("OpenAI", "https://api.openai.com/v1")
        mock_select_shallow.return_value = "gpt-4o-mini"
        mock_select_deep.return_value = "gpt-4o-mini"
        
        # Mock discovery functions
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_interpret.return_value = {"sectors": ["Technology"]}
        mock_discover.return_value = MOCK_TICKER_LISTS["technology"][:5]
        mock_create_screening_config.return_value = {}
        mock_batch_analyze_tickers.return_value = MOCK_ANALYSIS_RESULTS
        mock_filter_top_candidates.return_value = ["AAPL", "MSFT"]
        
        selections = get_user_selections()
        
        assert selections["ticker"] == "AAPL"
        assert "discovery_tickers" in selections


class TestRunAnalysis:
    """Test cases for run_analysis function."""

    @patch("cli.main.TradingAgentsGraph")
    @patch("cli.main.get_user_selections")
    @patch("cli.main.Path.mkdir")
    @patch("cli.main.Path.touch")
    def test_run_analysis_initialization(
        self,
        mock_touch,
        mock_mkdir,
        mock_get_selections,
        mock_graph_class,
    ):
        """Test run_analysis initializes correctly."""
        # Mock user selections
        mock_selections = {
            "ticker": "AAPL",
            "analysis_date": "2024-01-15",
            "analysts": [AnalystType.MARKET],
            "research_depth": 1,
            "llm_provider": "openai",
            "backend_url": "https://api.openai.com/v1",
            "shallow_thinker": "gpt-4o-mini",
            "deep_thinker": "gpt-4o-mini",
        }
        mock_get_selections.return_value = mock_selections
        
        # Mock graph
        mock_graph = MagicMock()
        mock_graph.propagator.create_initial_state.return_value = {}
        mock_graph.propagator.get_graph_args.return_value = {"stream_mode": "values"}
        mock_graph.graph.stream.return_value = iter([{"messages": []}])
        mock_graph.process_signal.return_value = "BUY"
        mock_graph_class.return_value = mock_graph
        
        # Mock display functions to avoid Rich rendering issues
        with patch("cli.main.create_layout"), patch("cli.main.update_display"), patch("cli.main.display_complete_report"):
            try:
                run_analysis()
            except StopIteration:
                # Expected when graph.stream is exhausted
                pass
        
        mock_graph_class.assert_called_once()
        mock_mkdir.assert_called()


class TestMessageBufferIntegration:
    """Test cases for MessageBuffer integration."""

    def test_message_buffer_workflow(self):
        """Test MessageBuffer workflow with multiple operations."""
        buffer = MessageBuffer()
        
        # Add messages
        buffer.add_message("System", "Starting analysis")
        buffer.add_message("Reasoning", "Analyzing market data")
        
        # Add tool calls
        buffer.add_tool_call("get_stock_data", {"ticker": "AAPL"})
        
        # Update agent status
        buffer.update_agent_status("Market Analyst", "in_progress")
        buffer.update_agent_status("Market Analyst", "completed")
        
        # Update reports
        buffer.update_report_section("market_report", "Market analysis complete")
        
        assert len(buffer.messages) == 2
        assert len(buffer.tool_calls) == 1
        assert buffer.agent_status["Market Analyst"] == "completed"
        assert buffer.report_sections["market_report"] == "Market analysis complete"
        assert buffer.current_report is not None
        assert buffer.final_report is not None

    def test_message_buffer_final_report_aggregation(self):
        """Test MessageBuffer aggregates all reports in final report."""
        buffer = MessageBuffer()
        
        buffer.update_report_section("market_report", "Market: Bullish")
        buffer.update_report_section("sentiment_report", "Sentiment: Positive")
        buffer.update_report_section("investment_plan", "Plan: Buy")
        buffer.update_report_section("final_trade_decision", "Decision: APPROVED")
        
        assert buffer.final_report is not None
        assert "Market: Bullish" in buffer.final_report
        assert "Sentiment: Positive" in buffer.final_report
        assert "Plan: Buy" in buffer.final_report
        assert "Decision: APPROVED" in buffer.final_report


class TestLayoutAndDisplay:
    """Test cases for layout and display functions."""

    def test_create_layout_structure(self):
        """Test create_layout creates correct structure."""
        layout = create_layout()
        
        assert "header" in layout
        assert "main" in layout
        assert "footer" in layout

    @patch("cli.main.message_buffer")
    def test_update_display_updates_all_panels(self, mock_buffer):
        """Test update_display updates all layout panels."""
        layout = create_layout()
        
        # Mock message buffer
        mock_buffer.agent_status = {
            "Market Analyst": "pending",
            "Social Analyst": "pending",
        }
        mock_buffer.messages = []
        mock_buffer.tool_calls = []
        mock_buffer.current_report = None
        mock_buffer.report_sections = {}
        
        # Should not raise error
        update_display(layout)
        
        # Check that layout was updated
        assert layout["header"] is not None
        assert layout["main"] is not None
