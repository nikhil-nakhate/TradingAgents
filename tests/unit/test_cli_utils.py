"""
Unit tests for CLI utility functions.
"""

import pytest
from unittest.mock import patch, MagicMock
from cli.utils import (
    get_ticker,
    get_analysis_date,
    select_analysts,
    select_research_depth,
    select_llm_provider,
    select_shallow_thinking_agent,
    select_deep_thinking_agent,
)
from cli.models import AnalystType


class TestGetTicker:
    """Test cases for get_ticker function."""

    @patch("cli.utils.questionary.text")
    def test_get_ticker_valid_input(self, mock_text):
        """Test get_ticker with valid input."""
        mock_text.return_value.ask.return_value = "AAPL"
        result = get_ticker()
        assert result == "AAPL"

    @patch("cli.utils.questionary.text")
    def test_get_ticker_uppercase_conversion(self, mock_text):
        """Test get_ticker converts to uppercase."""
        mock_text.return_value.ask.return_value = "aapl"
        result = get_ticker()
        assert result == "AAPL"

    @patch("cli.utils.questionary.text")
    def test_get_ticker_strips_whitespace(self, mock_text):
        """Test get_ticker strips whitespace."""
        mock_text.return_value.ask.return_value = "  AAPL  "
        result = get_ticker()
        assert result == "AAPL"

    @patch("cli.utils.questionary.text")
    @patch("cli.utils.exit")
    def test_get_ticker_empty_input(self, mock_exit, mock_text):
        """Test get_ticker handles empty input."""
        mock_text.return_value.ask.return_value = None
        with pytest.raises(SystemExit):
            get_ticker()
        mock_exit.assert_called_once_with(1)


class TestGetAnalysisDate:
    """Test cases for get_analysis_date function."""

    @patch("cli.utils.questionary.text")
    def test_get_analysis_date_valid_format(self, mock_text):
        """Test get_analysis_date with valid date format."""
        mock_text.return_value.ask.return_value = "2024-01-15"
        result = get_analysis_date()
        assert result == "2024-01-15"

    @patch("cli.utils.questionary.text")
    def test_get_analysis_date_strips_whitespace(self, mock_text):
        """Test get_analysis_date strips whitespace."""
        mock_text.return_value.ask.return_value = "  2024-01-15  "
        result = get_analysis_date()
        assert result == "2024-01-15"

    @patch("cli.utils.questionary.text")
    @patch("cli.utils.console")
    def test_get_analysis_date_invalid_format(self, mock_console, mock_text):
        """Test get_analysis_date rejects invalid format."""
        mock_text.return_value.ask.side_effect = ["invalid-date", "2024-01-15"]
        result = get_analysis_date()
        assert result == "2024-01-15"
        mock_console.print.assert_called()

    @patch("cli.utils.questionary.text")
    @patch("cli.utils.console")
    def test_get_analysis_date_future_date(self, mock_console, mock_text):
        """Test get_analysis_date rejects future dates."""
        from datetime import datetime, timedelta
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        mock_text.return_value.ask.side_effect = [future_date, past_date]
        result = get_analysis_date()
        assert result == past_date
        mock_console.print.assert_called()

    @patch("cli.utils.questionary.text")
    @patch("cli.utils.exit")
    def test_get_analysis_date_empty_input(self, mock_exit, mock_text):
        """Test get_analysis_date handles empty input."""
        mock_text.return_value.ask.return_value = None
        with pytest.raises(SystemExit):
            get_analysis_date()
        mock_exit.assert_called_once_with(1)


class TestSelectAnalysts:
    """Test cases for select_analysts function."""

    @patch("cli.utils.questionary.checkbox")
    def test_select_analysts_single_selection(self, mock_checkbox):
        """Test select_analysts with single selection."""
        mock_checkbox.return_value.ask.return_value = [AnalystType.MARKET]
        result = select_analysts()
        assert len(result) == 1
        assert AnalystType.MARKET in result

    @patch("cli.utils.questionary.checkbox")
    def test_select_analysts_multiple_selection(self, mock_checkbox):
        """Test select_analysts with multiple selections."""
        mock_checkbox.return_value.ask.return_value = [
            AnalystType.MARKET,
            AnalystType.SOCIAL,
            AnalystType.NEWS,
        ]
        result = select_analysts()
        assert len(result) == 3
        assert AnalystType.MARKET in result
        assert AnalystType.SOCIAL in result
        assert AnalystType.NEWS in result

    @patch("cli.utils.questionary.checkbox")
    @patch("cli.utils.exit")
    def test_select_analysts_empty_selection(self, mock_exit, mock_checkbox):
        """Test select_analysts handles empty selection."""
        mock_checkbox.return_value.ask.return_value = []
        with pytest.raises(SystemExit):
            select_analysts()
        mock_exit.assert_called_once_with(1)

    @patch("cli.utils.questionary.checkbox")
    @patch("cli.utils.exit")
    def test_select_analysts_none_selection(self, mock_exit, mock_checkbox):
        """Test select_analysts handles None selection."""
        mock_checkbox.return_value.ask.return_value = None
        with pytest.raises(SystemExit):
            select_analysts()
        mock_exit.assert_called_once_with(1)


class TestSelectResearchDepth:
    """Test cases for select_research_depth function."""

    @patch("cli.utils.questionary.select")
    def test_select_research_depth_shallow(self, mock_select):
        """Test select_research_depth with shallow option."""
        mock_select.return_value.ask.return_value = 1
        result = select_research_depth()
        assert result == 1

    @patch("cli.utils.questionary.select")
    def test_select_research_depth_medium(self, mock_select):
        """Test select_research_depth with medium option."""
        mock_select.return_value.ask.return_value = 3
        result = select_research_depth()
        assert result == 3

    @patch("cli.utils.questionary.select")
    def test_select_research_depth_deep(self, mock_select):
        """Test select_research_depth with deep option."""
        mock_select.return_value.ask.return_value = 5
        result = select_research_depth()
        assert result == 5

    @patch("cli.utils.questionary.select")
    @patch("cli.utils.exit")
    def test_select_research_depth_none(self, mock_exit, mock_select):
        """Test select_research_depth handles None selection."""
        mock_select.return_value.ask.return_value = None
        with pytest.raises(SystemExit):
            select_research_depth()
        mock_exit.assert_called_once_with(1)


class TestSelectLLMProvider:
    """Test cases for select_llm_provider function."""

    @patch("cli.utils.questionary.select")
    def test_select_llm_provider_openai(self, mock_select):
        """Test select_llm_provider with OpenAI."""
        mock_select.return_value.ask.return_value = ("OpenAI", "https://api.openai.com/v1")
        display, url = select_llm_provider()
        assert display == "OpenAI"
        assert url == "https://api.openai.com/v1"

    @patch("cli.utils.questionary.select")
    def test_select_llm_provider_anthropic(self, mock_select):
        """Test select_llm_provider with Anthropic."""
        mock_select.return_value.ask.return_value = ("Anthropic", "https://api.anthropic.com/")
        display, url = select_llm_provider()
        assert display == "Anthropic"
        assert url == "https://api.anthropic.com/"

    @patch("cli.utils.questionary.select")
    def test_select_llm_provider_llamacpp(self, mock_select):
        """Test select_llm_provider with LlamaCpp."""
        mock_select.return_value.ask.return_value = ("LlamaCpp (Local)", "http://localhost:8000/v1")
        display, url = select_llm_provider()
        assert display == "LlamaCpp (Local)"
        assert url == "http://localhost:8000/v1"

    @patch("cli.utils.questionary.select")
    @patch("cli.utils.exit")
    def test_select_llm_provider_none(self, mock_exit, mock_select):
        """Test select_llm_provider handles None selection."""
        mock_select.return_value.ask.return_value = None
        with pytest.raises(SystemExit):
            select_llm_provider()
        mock_exit.assert_called_once_with(1)


class TestSelectShallowThinkingAgent:
    """Test cases for select_shallow_thinking_agent function."""

    @patch("cli.utils.questionary.select")
    def test_select_shallow_thinking_agent_openai(self, mock_select):
        """Test select_shallow_thinking_agent with OpenAI provider."""
        mock_select.return_value.ask.return_value = "gpt-4o-mini"
        result = select_shallow_thinking_agent("openai")
        assert result == "gpt-4o-mini"

    @patch("cli.utils.questionary.select")
    def test_select_shallow_thinking_agent_anthropic(self, mock_select):
        """Test select_shallow_thinking_agent with Anthropic provider."""
        mock_select.return_value.ask.return_value = "claude-3-5-haiku-latest"
        result = select_shallow_thinking_agent("anthropic")
        assert result == "claude-3-5-haiku-latest"

    @patch("cli.utils.questionary.select")
    def test_select_shallow_thinking_agent_llamacpp(self, mock_select):
        """Test select_shallow_thinking_agent with LlamaCpp provider."""
        mock_select.return_value.ask.return_value = "deepseek-r1-distill-llama-8b"
        result = select_shallow_thinking_agent("llamacpp (local)")
        assert result == "deepseek-r1-distill-llama-8b"

    @patch("cli.utils.questionary.select")
    @patch("cli.utils.exit")
    def test_select_shallow_thinking_agent_none(self, mock_exit, mock_select):
        """Test select_shallow_thinking_agent handles None selection."""
        mock_select.return_value.ask.return_value = None
        with pytest.raises(SystemExit):
            select_shallow_thinking_agent("openai")
        mock_exit.assert_called_once_with(1)


class TestSelectDeepThinkingAgent:
    """Test cases for select_deep_thinking_agent function."""

    @patch("cli.utils.questionary.select")
    def test_select_deep_thinking_agent_openai(self, mock_select):
        """Test select_deep_thinking_agent with OpenAI provider."""
        mock_select.return_value.ask.return_value = "o4-mini"
        result = select_deep_thinking_agent("openai")
        assert result == "o4-mini"

    @patch("cli.utils.questionary.select")
    def test_select_deep_thinking_agent_anthropic(self, mock_select):
        """Test select_deep_thinking_agent with Anthropic provider."""
        mock_select.return_value.ask.return_value = "claude-sonnet-4-0"
        result = select_deep_thinking_agent("anthropic")
        assert result == "claude-sonnet-4-0"

    @patch("cli.utils.questionary.select")
    def test_select_deep_thinking_agent_llamacpp(self, mock_select):
        """Test select_deep_thinking_agent with LlamaCpp provider."""
        mock_select.return_value.ask.return_value = "deepseek-r1-distill-llama-70b"
        result = select_deep_thinking_agent("llamacpp (local)")
        assert result == "deepseek-r1-distill-llama-70b"

    @patch("cli.utils.questionary.select")
    @patch("cli.utils.exit")
    def test_select_deep_thinking_agent_none(self, mock_exit, mock_select):
        """Test select_deep_thinking_agent handles None selection."""
        mock_select.return_value.ask.return_value = None
        with pytest.raises(SystemExit):
            select_deep_thinking_agent("openai")
        mock_exit.assert_called_once_with(1)
