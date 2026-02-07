"""
Integration tests for TradingAgentsGraph.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG


class TestTradingAgentsGraphInit:
    """Test cases for TradingAgentsGraph initialization."""

    @patch("tradingagents.graph.trading_graph.ChatOpenAI")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    @patch("tradingagents.graph.trading_graph.GraphSetup")
    @patch("tradingagents.graph.trading_graph.set_config")
    @patch("tradingagents.graph.trading_graph.os.makedirs")
    def test_init_with_default_config(self, mock_makedirs, mock_set_config, mock_graph_setup_class, mock_memory, mock_chat_openai):
        """Test TradingAgentsGraph initialization with default config."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Setup GraphSetup mock instance
        mock_graph_setup_instance = MagicMock()
        mock_graph_setup_instance.setup_graph.return_value = MagicMock()
        mock_graph_setup_class.return_value = mock_graph_setup_instance
        
        graph = TradingAgentsGraph()
        
        assert graph.debug == False
        assert graph.config == DEFAULT_CONFIG
        mock_set_config.assert_called_once()
        mock_graph_setup_class.assert_called_once()

    @patch("tradingagents.graph.trading_graph.ChatOpenAI")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    @patch("tradingagents.graph.trading_graph.GraphSetup")
    @patch("tradingagents.graph.trading_graph.set_config")
    @patch("tradingagents.graph.trading_graph.os.makedirs")
    def test_init_with_custom_config(self, mock_makedirs, mock_set_config, mock_graph_setup_class, mock_memory, mock_chat_openai, sample_config):
        """Test TradingAgentsGraph initialization with custom config."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Setup GraphSetup mock instance
        mock_graph_setup_instance = MagicMock()
        mock_graph_setup_instance.setup_graph.return_value = MagicMock()
        mock_graph_setup_class.return_value = mock_graph_setup_instance
        
        graph = TradingAgentsGraph(config=sample_config)
        
        assert graph.config == sample_config
        mock_set_config.assert_called_once_with(sample_config)

    @patch("tradingagents.graph.trading_graph.ChatOpenAI")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    @patch("tradingagents.graph.trading_graph.GraphSetup")
    @patch("tradingagents.graph.trading_graph.set_config")
    @patch("tradingagents.graph.trading_graph.os.makedirs")
    def test_init_with_selected_analysts(self, mock_makedirs, mock_set_config, mock_graph_setup_class, mock_memory, mock_chat_openai):
        """Test TradingAgentsGraph initialization with selected analysts."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Setup GraphSetup mock to return a mock instance with setup_graph method
        mock_graph_setup_instance = MagicMock()
        mock_graph_setup_instance.setup_graph.return_value = MagicMock()
        mock_graph_setup_class.return_value = mock_graph_setup_instance
        
        selected = ["market", "fundamentals"]
        graph = TradingAgentsGraph(selected_analysts=selected)
        
        mock_graph_setup_instance.setup_graph.assert_called_once_with(selected)

    @patch("tradingagents.graph.trading_graph.ChatOpenAI")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    @patch("tradingagents.graph.trading_graph.GraphSetup")
    @patch("tradingagents.graph.trading_graph.set_config")
    @patch("tradingagents.graph.trading_graph.os.makedirs")
    def test_init_with_debug_mode(self, mock_makedirs, mock_set_config, mock_graph_setup_class, mock_memory, mock_chat_openai):
        """Test TradingAgentsGraph initialization with debug mode."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Setup GraphSetup mock instance
        mock_graph_setup_instance = MagicMock()
        mock_graph_setup_instance.setup_graph.return_value = MagicMock()
        mock_graph_setup_class.return_value = mock_graph_setup_instance
        
        graph = TradingAgentsGraph(debug=True)
        
        assert graph.debug == True

    @patch("tradingagents.graph.trading_graph.ChatAnthropic")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    @patch("tradingagents.graph.trading_graph.GraphSetup")
    @patch("tradingagents.graph.trading_graph.set_config")
    @patch("tradingagents.graph.trading_graph.os.makedirs")
    def test_init_with_anthropic_provider(self, mock_makedirs, mock_set_config, mock_graph_setup_class, mock_memory, mock_chat_anthropic, sample_config):
        """Test TradingAgentsGraph initialization with Anthropic provider."""
        sample_config["llm_provider"] = "anthropic"
        mock_llm = MagicMock()
        mock_chat_anthropic.return_value = mock_llm
        
        # Setup GraphSetup mock instance
        mock_graph_setup_instance = MagicMock()
        mock_graph_setup_instance.setup_graph.return_value = MagicMock()
        mock_graph_setup_class.return_value = mock_graph_setup_instance
        
        graph = TradingAgentsGraph(config=sample_config)
        
        mock_chat_anthropic.assert_called()
        assert graph.config["llm_provider"] == "anthropic"

    @patch("tradingagents.graph.trading_graph.ChatGoogleGenerativeAI")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    @patch("tradingagents.graph.trading_graph.GraphSetup")
    @patch("tradingagents.graph.trading_graph.set_config")
    @patch("tradingagents.graph.trading_graph.os.makedirs")
    def test_init_with_google_provider(self, mock_makedirs, mock_set_config, mock_graph_setup_class, mock_memory, mock_chat_google, sample_config):
        """Test TradingAgentsGraph initialization with Google provider."""
        sample_config["llm_provider"] = "google"
        mock_llm = MagicMock()
        mock_chat_google.return_value = mock_llm
        
        # Setup GraphSetup mock instance
        mock_graph_setup_instance = MagicMock()
        mock_graph_setup_instance.setup_graph.return_value = MagicMock()
        mock_graph_setup_class.return_value = mock_graph_setup_instance
        
        graph = TradingAgentsGraph(config=sample_config)
        
        mock_chat_google.assert_called()
        assert graph.config["llm_provider"] == "google"

    @patch("tradingagents.graph.trading_graph.ChatOpenAI")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    @patch("tradingagents.graph.trading_graph.GraphSetup")
    @patch("tradingagents.graph.trading_graph.set_config")
    @patch("tradingagents.graph.trading_graph.os.makedirs")
    def test_init_invalid_provider(self, mock_makedirs, mock_set_config, mock_graph_setup, mock_memory, mock_chat_openai, sample_config):
        """Test TradingAgentsGraph initialization with invalid provider."""
        sample_config["llm_provider"] = "invalid_provider"
        
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            TradingAgentsGraph(config=sample_config)


class TestCreateToolNodes:
    """Test cases for _create_tool_nodes method."""

    @patch("tradingagents.graph.trading_graph.ChatOpenAI")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    @patch("tradingagents.graph.trading_graph.GraphSetup")
    @patch("tradingagents.graph.trading_graph.set_config")
    @patch("tradingagents.graph.trading_graph.os.makedirs")
    def test_create_tool_nodes_structure(self, mock_makedirs, mock_set_config, mock_graph_setup_class, mock_memory, mock_chat_openai):
        """Test _create_tool_nodes creates all required tool nodes."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Setup GraphSetup mock instance
        mock_graph_setup_instance = MagicMock()
        mock_graph_setup_instance.setup_graph.return_value = MagicMock()
        mock_graph_setup_class.return_value = mock_graph_setup_instance
        
        graph = TradingAgentsGraph()
        tool_nodes = graph._create_tool_nodes()
        
        assert isinstance(tool_nodes, dict)
        assert "market" in tool_nodes
        assert "social" in tool_nodes
        assert "news" in tool_nodes
        assert "fundamentals" in tool_nodes

    @patch("tradingagents.graph.trading_graph.ChatOpenAI")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    @patch("tradingagents.graph.trading_graph.GraphSetup")
    @patch("tradingagents.graph.trading_graph.set_config")
    @patch("tradingagents.graph.trading_graph.os.makedirs")
    def test_create_tool_nodes_types(self, mock_makedirs, mock_set_config, mock_graph_setup_class, mock_memory, mock_chat_openai):
        """Test _create_tool_nodes returns ToolNode instances."""
        from langgraph.prebuilt import ToolNode
        
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Setup GraphSetup mock instance
        mock_graph_setup_instance = MagicMock()
        mock_graph_setup_instance.setup_graph.return_value = MagicMock()
        mock_graph_setup_class.return_value = mock_graph_setup_instance
        
        graph = TradingAgentsGraph()
        tool_nodes = graph._create_tool_nodes()
        
        for node in tool_nodes.values():
            # ToolNode is a class, check if it's an instance
            assert hasattr(node, "tools") or hasattr(node, "__call__")


class TestPropagate:
    """Test cases for propagate method."""

    @patch("tradingagents.graph.trading_graph.ChatOpenAI")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    @patch("tradingagents.graph.trading_graph.GraphSetup")
    @patch("tradingagents.graph.trading_graph.set_config")
    @patch("tradingagents.graph.trading_graph.os.makedirs")
    def test_propagate_initializes_state(self, mock_makedirs, mock_set_config, mock_graph_setup_class, mock_memory, mock_chat_openai, sample_ticker, sample_date):
        """Test propagate initializes state correctly."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Mock graph.stream to return empty chunks
        mock_graph = MagicMock()
        mock_graph.stream.return_value = iter([{"messages": []}])
        
        # Setup GraphSetup mock instance
        mock_graph_setup_instance = MagicMock()
        mock_graph_setup_instance.setup_graph.return_value = mock_graph
        mock_graph_setup_class.return_value = mock_graph_setup_instance
        
        graph = TradingAgentsGraph(debug=True)
        graph.graph = mock_graph
        
        final_state, decision = graph.propagate(sample_ticker, sample_date)
        
        assert graph.ticker == sample_ticker
        assert graph.curr_state is not None

    @patch("tradingagents.graph.trading_graph.ChatOpenAI")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    @patch("tradingagents.graph.trading_graph.GraphSetup")
    @patch("tradingagents.graph.trading_graph.set_config")
    @patch("tradingagents.graph.trading_graph.os.makedirs")
    def test_propagate_returns_decision(self, mock_makedirs, mock_set_config, mock_graph_setup_class, mock_memory, mock_chat_openai, sample_ticker, sample_date):
        """Test propagate returns decision."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Mock final state
        mock_final_state = {
            "final_trade_decision": "BUY 100 shares",
            "company_of_interest": sample_ticker,
            "trade_date": sample_date,
        }
        
        mock_graph = MagicMock()
        mock_graph.stream.return_value = iter([{"messages": [], **mock_final_state}])
        
        # Setup GraphSetup mock instance
        mock_graph_setup_instance = MagicMock()
        mock_graph_setup_instance.setup_graph.return_value = mock_graph
        mock_graph_setup_class.return_value = mock_graph_setup_instance
        
        graph = TradingAgentsGraph(debug=True)
        graph.graph = mock_graph
        graph.process_signal = MagicMock(return_value="BUY")
        
        final_state, decision = graph.propagate(sample_ticker, sample_date)
        
        assert decision is not None
        graph.process_signal.assert_called_once()


class TestProcessSignal:
    """Test cases for process_signal method."""

    @patch("tradingagents.graph.trading_graph.ChatOpenAI")
    @patch("tradingagents.graph.trading_graph.FinancialSituationMemory")
    @patch("tradingagents.graph.trading_graph.GraphSetup")
    @patch("tradingagents.graph.trading_graph.set_config")
    @patch("tradingagents.graph.trading_graph.os.makedirs")
    def test_process_signal_delegates(self, mock_makedirs, mock_set_config, mock_graph_setup_class, mock_memory, mock_chat_openai):
        """Test process_signal delegates to SignalProcessor."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Setup GraphSetup mock instance
        mock_graph_setup_instance = MagicMock()
        mock_graph_setup_instance.setup_graph.return_value = MagicMock()
        mock_graph_setup_class.return_value = mock_graph_setup_instance
        
        graph = TradingAgentsGraph()
        graph.signal_processor.process_signal = MagicMock(return_value="BUY")
        
        result = graph.process_signal("Full signal text")
        
        assert result == "BUY"
        graph.signal_processor.process_signal.assert_called_once_with("Full signal text")
