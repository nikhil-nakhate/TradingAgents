"""
Integration tests for discovery workflow.
"""

import pytest
from unittest.mock import patch, MagicMock
from tradingagents.discovery import (
    interpret_user_intent,
    discover_tickers,
    create_screening_config,
    batch_analyze_tickers,
    filter_top_candidates,
)
from tests.fixtures.mock_data import (
    MOCK_DISCOVERY_CRITERIA,
    MOCK_TICKER_LISTS,
    MOCK_ANALYSIS_RESULTS,
    get_test_date,
)


class TestDiscoveryWorkflow:
    """Test cases for full discovery workflow."""

    @patch("tradingagents.discovery.ticker_screener.discover_tickers_by_criteria")
    @patch("tradingagents.discovery.lightweight_analyzer.route_to_vendor")
    @patch("tradingagents.discovery.lightweight_analyzer._get_llm")
    def test_full_discovery_pipeline(self, mock_get_llm, mock_route, mock_discover, sample_config):
        """Test complete discovery pipeline: intent → criteria → tickers → screening."""
        from tests.fixtures.mock_data import MOCK_STOCK_DATA
        
        user_intent = "tech stocks with AI focus"
        analysis_date = get_test_date(7)
        
        # Mock LLM for intent interpretation
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"sectors": ["Technology"], "keywords": ["AI"], "market_cap_min": 1000000000}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        # Mock ticker discovery
        mock_discover.return_value = MOCK_TICKER_LISTS["technology"][:5]
        
        # Mock data fetching
        def mock_route_side_effect(method, *args, **kwargs):
            ticker = args[0] if args else "AAPL"
            if method == "get_stock_data":
                return MOCK_STOCK_DATA.get(ticker, {}).get("price_data", "")
            elif method == "get_indicators":
                return MOCK_STOCK_DATA.get(ticker, {}).get("indicators", "")
            elif method == "get_fundamentals":
                return MOCK_STOCK_DATA.get(ticker, {}).get("fundamentals", "")
            elif method == "get_news":
                return MOCK_STOCK_DATA.get(ticker, {}).get("news", "")
            return ""
        
        mock_route.side_effect = mock_route_side_effect
        
        # Mock LLM for screening analysis
        mock_screening_response = MagicMock()
        mock_screening_response.content = '{"screening_score": 85, "signals": {"momentum_score": 70, "volume_trend": 1, "technical_score": 80, "fundamental_score": 75, "sentiment_score": 60}, "recommendation": "buy", "reasoning": "Strong indicators"}'
        mock_llm.invoke.return_value = mock_screening_response
        
        # Step 1: Interpret intent
        criteria = interpret_user_intent(user_intent, mock_llm)
        assert isinstance(criteria, dict)
        assert "sectors" in criteria
        
        # Step 2: Discover tickers
        tickers = discover_tickers(criteria)
        assert isinstance(tickers, list)
        assert len(tickers) > 0
        
        # Step 3: Screening
        screening_config = create_screening_config(sample_config)
        results = batch_analyze_tickers(
            tickers[:3],
            analysis_date,
            screening_config,
            max_workers=2
        )
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Step 4: Filter top candidates
        top_tickers = filter_top_candidates(results, min_score=60, max_candidates=3)
        assert isinstance(top_tickers, list)
        assert len(top_tickers) <= 3

    @patch("tradingagents.discovery.ticker_screener.discover_tickers_by_criteria")
    def test_discovery_fallback_on_empty_results(self, mock_discover):
        """Test discovery workflow handles empty ticker results."""
        mock_discover.return_value = []
        
        criteria = {"sectors": ["Technology"]}
        tickers = discover_tickers(criteria)
        
        # Should return fallback tickers
        assert isinstance(tickers, list)
        assert len(tickers) > 0

    @patch("tradingagents.discovery.ticker_screener.discover_tickers_by_criteria")
    def test_discovery_fallback_on_exception(self, mock_discover):
        """Test discovery workflow handles exceptions gracefully."""
        mock_discover.side_effect = Exception("Discovery service unavailable")
        
        criteria = {"sectors": ["Technology"]}
        tickers = discover_tickers(criteria)
        
        # Should return safe default list
        assert isinstance(tickers, list)
        assert len(tickers) > 0

    @patch("tradingagents.discovery.lightweight_analyzer.analyze_ticker_lightweight")
    def test_batch_analysis_handles_partial_failures(self, mock_analyze, sample_config, sample_ticker_list, sample_date):
        """Test batch analysis continues despite individual failures."""
        # Mix of success and failure
        mock_analyze.side_effect = [
            {"ticker": "AAPL", "screening_score": 80},
            Exception("Analysis failed for MSFT"),
            {"ticker": "GOOGL", "screening_score": 75},
        ]
        
        results = batch_analyze_tickers(
            sample_ticker_list[:3],
            sample_date,
            sample_config,
            max_workers=2
        )
        
        # Should have 3 results (including error result)
        assert len(results) == 3
        # Successful analyses should be present
        assert any(r.get("ticker") == "AAPL" for r in results)
        assert any(r.get("ticker") == "GOOGL" for r in results)
        # Error should be handled
        assert any(r.get("error") == "analysis_failed" for r in results)


class TestDiscoveryErrorHandling:
    """Test cases for discovery error handling."""

    def test_interpret_intent_json_error_fallback(self):
        """Test interpret_user_intent falls back on JSON decode error."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "not valid json"
        mock_llm.invoke.return_value = mock_response
        
        criteria = interpret_user_intent("tech stocks", mock_llm)
        
        # Should use fallback extraction
        assert isinstance(criteria, dict)

    @patch("tradingagents.discovery.lightweight_analyzer.route_to_vendor")
    def test_analyze_ticker_no_data_fallback(self, mock_route, sample_config, sample_ticker, sample_date):
        """Test analyze_ticker_lightweight handles missing data."""
        from tradingagents.discovery.lightweight_analyzer import analyze_ticker_lightweight
        
        mock_route.return_value = None
        
        result = analyze_ticker_lightweight(sample_ticker, sample_date, sample_config)
        
        assert result["screening_score"] == 0
        assert result["recommendation"] == "avoid"
        assert "error" in result
