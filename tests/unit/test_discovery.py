"""
Unit tests for discovery functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from tradingagents.discovery import (
    interpret_user_intent,
    discover_tickers,
    create_screening_config,
    filter_top_candidates,
    extract_screening_signals,
)
from tradingagents.discovery.lightweight_analyzer import (
    analyze_ticker_lightweight,
    batch_analyze_tickers,
)
from tests.fixtures.mock_data import (
    MOCK_DISCOVERY_CRITERIA,
    MOCK_TICKER_LISTS,
    MOCK_ANALYSIS_RESULTS,
    get_test_date,
)


class TestInterpretUserIntent:
    """Test cases for interpret_user_intent function."""

    def test_interpret_user_intent_success(self, mock_llm):
        """Test interpret_user_intent with successful LLM response."""
        description = "tech stocks with AI focus"
        
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = '{"sectors": ["Technology"], "keywords": ["AI"], "market_cap_min": 1000000000}'
        mock_llm.invoke.return_value = mock_response
        
        criteria = interpret_user_intent(description, mock_llm)
        
        assert isinstance(criteria, dict)
        assert "sectors" in criteria
        assert criteria["sectors"] == ["Technology"]

    def test_interpret_user_intent_with_json_markdown(self, mock_llm):
        """Test interpret_user_intent handles JSON in markdown code blocks."""
        description = "healthcare stocks"
        
        mock_response = MagicMock()
        mock_response.content = '```json\n{"sectors": ["Healthcare"], "market_cap_min": 10000000000}\n```'
        mock_llm.invoke.return_value = mock_response
        
        criteria = interpret_user_intent(description, mock_llm)
        
        assert isinstance(criteria, dict)
        assert "sectors" in criteria

    def test_interpret_user_intent_fallback_on_error(self, mock_llm):
        """Test interpret_user_intent falls back on JSON decode error."""
        description = "tech stocks"
        
        mock_response = MagicMock()
        mock_response.content = "invalid json response"
        mock_llm.invoke.return_value = mock_response
        
        # Should use fallback extraction
        criteria = interpret_user_intent(description, mock_llm)
        
        assert isinstance(criteria, dict)
        # Fallback should still produce some criteria
        assert "market_cap_min" in criteria or "sectors" in criteria


class TestDiscoverTickers:
    """Test cases for discover_tickers function."""

    @patch("tradingagents.discovery.ticker_screener.discover_tickers_by_criteria")
    def test_discover_tickers_success(self, mock_discover, sample_discovery_criteria):
        """Test discover_tickers with successful discovery."""
        mock_discover.return_value = MOCK_TICKER_LISTS["technology"]
        
        tickers = discover_tickers(sample_discovery_criteria)
        
        assert isinstance(tickers, list)
        assert len(tickers) > 0
        mock_discover.assert_called_once()

    @patch("tradingagents.discovery.ticker_screener.discover_tickers_by_criteria")
    def test_discover_tickers_empty_result(self, mock_discover, sample_discovery_criteria):
        """Test discover_tickers handles empty results."""
        mock_discover.return_value = []
        
        tickers = discover_tickers(sample_discovery_criteria)
        
        # Should return fallback tickers
        assert isinstance(tickers, list)
        assert len(tickers) > 0

    @patch("tradingagents.discovery.ticker_screener.discover_tickers_by_criteria")
    def test_discover_tickers_exception_fallback(self, mock_discover, sample_discovery_criteria):
        """Test discover_tickers falls back on exception."""
        mock_discover.side_effect = Exception("Discovery failed")
        
        tickers = discover_tickers(sample_discovery_criteria)
        
        # Should return safe default list
        assert isinstance(tickers, list)
        assert len(tickers) > 0


class TestFilterTopCandidates:
    """Test cases for filter_top_candidates function."""

    def test_filter_top_candidates_basic(self):
        """Test filter_top_candidates filters by score."""
        results = MOCK_ANALYSIS_RESULTS.copy()
        results.append({
            "ticker": "LOW_SCORE",
            "screening_score": 30,
            "recommendation": "avoid",
        })
        
        top = filter_top_candidates(results, min_score=60, max_candidates=5)
        
        assert isinstance(top, list)
        assert len(top) <= 5
        assert "LOW_SCORE" not in top

    def test_filter_top_candidates_max_limit(self):
        """Test filter_top_candidates respects max_candidates limit."""
        results = [
            {"ticker": f"TICKER{i}", "screening_score": 80 - i} 
            for i in range(10)
        ]
        
        top = filter_top_candidates(results, min_score=60, max_candidates=3)
        
        assert len(top) == 3

    def test_filter_top_candidates_sorted(self):
        """Test filter_top_candidates returns sorted by score."""
        results = [
            {"ticker": "MID", "screening_score": 70},
            {"ticker": "HIGH", "screening_score": 90},
            {"ticker": "LOW", "screening_score": 65},
        ]
        
        top = filter_top_candidates(results, min_score=60, max_candidates=3)
        
        assert top[0] == "HIGH"  # Highest score first
        assert top[-1] == "LOW"  # Lowest score last

    def test_filter_top_candidates_empty_results(self):
        """Test filter_top_candidates with empty results."""
        results = []
        top = filter_top_candidates(results, min_score=60, max_candidates=5)
        
        assert isinstance(top, list)
        assert len(top) == 0


class TestExtractScreeningSignals:
    """Test cases for extract_screening_signals function."""

    def test_extract_screening_signals_complete(self, sample_analysis_result):
        """Test extract_screening_signals extracts all signals."""
        signals = extract_screening_signals(sample_analysis_result)
        
        assert "screening_score" in signals
        assert "momentum_score" in signals
        assert "volume_trend" in signals
        assert "technical_score" in signals
        assert "fundamental_score" in signals
        assert "sentiment_score" in signals

    def test_extract_screening_signals_defaults(self):
        """Test extract_screening_signals uses defaults for missing values."""
        incomplete_result = {
            "ticker": "TEST",
            "screening_score": 75,
            "signals": {
                "momentum_score": 50,
            },
        }
        
        signals = extract_screening_signals(incomplete_result)
        
        assert signals["screening_score"] == 75
        assert signals["momentum_score"] == 50
        assert signals["technical_score"] == 50  # Default
        assert signals["fundamental_score"] == 50  # Default
        assert signals["volume_trend"] == 0  # Default
        assert signals["sentiment_score"] == 0  # Default

    def test_extract_screening_signals_no_signals_key(self):
        """Test extract_screening_signals handles missing signals key."""
        result = {
            "ticker": "TEST",
            "screening_score": 80,
        }
        
        signals = extract_screening_signals(result)
        
        assert signals["screening_score"] == 80
        assert signals["momentum_score"] == 0  # Default


class TestCreateScreeningConfig:
    """Test cases for create_screening_config function."""

    def test_create_screening_config_optimizations(self, sample_config):
        """Test create_screening_config creates optimized config."""
        screening_config = create_screening_config(sample_config)
        
        assert screening_config["deep_think_llm"] == sample_config["quick_think_llm"]
        assert screening_config["max_debate_rounds"] == 0
        assert screening_config["max_risk_discuss_rounds"] == 0
        assert screening_config["use_memory"] == False
        assert screening_config["use_reflection"] == False


class TestAnalyzeTickerLightweight:
    """Test cases for analyze_ticker_lightweight function."""

    @patch("tradingagents.discovery.lightweight_analyzer.route_to_vendor")
    @patch("tradingagents.discovery.lightweight_analyzer._get_llm")
    def test_analyze_ticker_lightweight_success(self, mock_get_llm, mock_route, sample_config, sample_ticker, sample_date):
        """Test analyze_ticker_lightweight with successful analysis."""
        from tests.fixtures.mock_data import MOCK_STOCK_DATA
        
        # Mock data fetching
        mock_route.side_effect = [
            MOCK_STOCK_DATA[sample_ticker]["price_data"],
            MOCK_STOCK_DATA[sample_ticker]["indicators"],
            MOCK_STOCK_DATA[sample_ticker]["fundamentals"],
            MOCK_STOCK_DATA[sample_ticker]["news"],
        ]
        
        # Mock LLM
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"screening_score": 85, "signals": {"momentum_score": 70, "volume_trend": 1, "technical_score": 80, "fundamental_score": 75, "sentiment_score": 60}, "recommendation": "buy", "reasoning": "Strong indicators"}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        result = analyze_ticker_lightweight(sample_ticker, sample_date, sample_config)
        
        assert isinstance(result, dict)
        assert result["ticker"] == sample_ticker
        assert "screening_score" in result
        assert "signals" in result
        assert "recommendation" in result

    @patch("tradingagents.discovery.lightweight_analyzer.route_to_vendor")
    def test_analyze_ticker_lightweight_no_data(self, mock_route, sample_config, sample_ticker, sample_date):
        """Test analyze_ticker_lightweight handles missing data."""
        mock_route.return_value = None
        
        result = analyze_ticker_lightweight(sample_ticker, sample_date, sample_config)
        
        assert result["screening_score"] == 0
        assert result["recommendation"] == "avoid"
        assert "error" in result


class TestBatchAnalyzeTickers:
    """Test cases for batch_analyze_tickers function."""

    @patch("tradingagents.discovery.lightweight_analyzer.analyze_ticker_lightweight")
    def test_batch_analyze_tickers_success(self, mock_analyze, sample_config, sample_ticker_list, sample_date):
        """Test batch_analyze_tickers processes multiple tickers."""
        # Mock individual analysis results
        mock_results = [
            {"ticker": ticker, "screening_score": 80 - i, "recommendation": "buy"}
            for i, ticker in enumerate(sample_ticker_list[:3])
        ]
        mock_analyze.side_effect = mock_results
        
        results = batch_analyze_tickers(
            sample_ticker_list[:3],
            sample_date,
            sample_config,
            max_workers=2
        )
        
        assert isinstance(results, list)
        assert len(results) == 3
        # Should be sorted by score (highest first)
        assert results[0]["screening_score"] >= results[-1]["screening_score"]

    @patch("tradingagents.discovery.lightweight_analyzer.analyze_ticker_lightweight")
    def test_batch_analyze_tickers_handles_failures(self, mock_analyze, sample_config, sample_ticker_list, sample_date):
        """Test batch_analyze_tickers handles individual failures."""
        # First succeeds, second fails, third succeeds
        mock_analyze.side_effect = [
            {"ticker": "AAPL", "screening_score": 80},
            Exception("Analysis failed"),
            {"ticker": "MSFT", "screening_score": 75},
        ]
        
        results = batch_analyze_tickers(
            sample_ticker_list[:3],
            sample_date,
            sample_config,
            max_workers=2
        )
        
        assert len(results) == 3  # Includes error result
        # Check that failed ticker has error result
        error_result = next(r for r in results if r.get("error") == "analysis_failed")
        assert error_result is not None
