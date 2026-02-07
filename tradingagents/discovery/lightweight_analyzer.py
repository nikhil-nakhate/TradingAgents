"""
Lightweight ticker analysis for screening.

This module provides fast, cost-efficient analysis of multiple tickers
before running the full multi-agent trading system. Uses minimal LLM calls
and simplified logic to quickly filter promising candidates.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from tradingagents.dataflows.interface import route_to_vendor

logger = logging.getLogger(__name__)


def _get_llm(model_name: str, config: Dict):
    """
    Create LLM instance based on provider configuration.

    Args:
        model_name: Name of the model to use
        config: Configuration dict with llm_provider and backend_url

    Returns:
        LLM instance (ChatOpenAI, ChatAnthropic, or ChatGoogleGenerativeAI)
    """
    provider = config.get("llm_provider", "openai").lower()

    if provider in ["openai", "ollama", "openrouter"]:
        return ChatOpenAI(
            model=model_name,
            base_url=config.get("backend_url", "https://api.openai.com/v1")
        )
    elif provider == "llamacpp":
        # Server mode (recommended)
        if config.get("llamacpp_model_path") is None:
            return ChatOpenAI(
                model=model_name,
                base_url=config.get("llamacpp_server_url", "http://localhost:8000/v1")
            )
        else:
            # Direct mode - load model in-process
            from langchain_community.chat_models import ChatLlamaCpp
            import multiprocessing
            return ChatLlamaCpp(
                model_path=config["llamacpp_model_path"],
                temperature=0.7,
                n_ctx=config.get("llamacpp_n_ctx", 4096),
                n_gpu_layers=config.get("llamacpp_n_gpu_layers", -1),
                n_batch=512,
                n_threads=config.get("llamacpp_n_threads") or (multiprocessing.cpu_count() - 1),
                verbose=False,
            )
    elif provider == "anthropic":
        return ChatAnthropic(
            model=model_name,
            base_url=config.get("backend_url", "https://api.anthropic.com/")
        )
    elif provider == "google":
        return ChatGoogleGenerativeAI(model=model_name)
    else:
        # Default to OpenAI
        logger.warning(f"Unknown provider '{provider}', defaulting to OpenAI")
        return ChatOpenAI(model=model_name)


def create_screening_config(base_config: Dict) -> Dict:
    """
    Create optimized config for fast screening.

    Takes a full TradingAgents config and returns a stripped-down version
    optimized for quick analysis:
    - Uses only quick_think_llm (cheaper model)
    - Disables memory/reflection
    - Minimal debate rounds
    - Fast data vendors

    Args:
        base_config: Full TradingAgents configuration dict

    Returns:
        Screening-optimized config dict
    """
    screening_config = base_config.copy()

    # Use cheap, fast model for screening
    screening_config["deep_think_llm"] = base_config["quick_think_llm"]

    # Disable expensive features
    screening_config["max_debate_rounds"] = 0
    screening_config["max_risk_discuss_rounds"] = 0
    screening_config["use_memory"] = False
    screening_config["use_reflection"] = False

    # Prefer fast, free data vendors
    screening_config["data_vendors"] = {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "yfinance",  # Fallback to yfinance for speed
        "news_data": "openai",  # LLM-generated is faster than API calls
    }

    # Increase timeouts for batch processing
    screening_config["api_timeout"] = 10
    screening_config["max_retries"] = 2

    logger.info("Created screening config with optimizations")
    return screening_config


def _fetch_ticker_data(ticker: str, date: str, config: Dict) -> Dict[str, Any]:
    """
    Fetch all required data for a ticker.

    Args:
        ticker: Stock ticker symbol
        date: Analysis date (YYYY-MM-DD)
        config: Configuration dict

    Returns:
        Dict with price_data, indicators, fundamentals, news
    """
    data = {
        "ticker": ticker,
        "date": date,
        "price_data": None,
        "indicators": None,
        "fundamentals": None,
        "news": None,
        "errors": []
    }

    # Get price data (last 30 days)
    try:
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=30)
        data["price_data"] = route_to_vendor(
            "get_stock_data",
            ticker,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
    except Exception as e:
        logger.warning(f"Failed to fetch price data for {ticker}: {e}")
        data["errors"].append(f"price_data: {str(e)}")

    # Get technical indicators
    try:
        data["indicators"] = route_to_vendor("get_indicators", ticker, date)
    except Exception as e:
        logger.warning(f"Failed to fetch indicators for {ticker}: {e}")
        data["errors"].append(f"indicators: {str(e)}")

    # Get fundamentals (best effort - may not be available)
    try:
        data["fundamentals"] = route_to_vendor("get_fundamentals", ticker, date)
    except Exception as e:
        logger.debug(f"Fundamentals not available for {ticker}: {e}")
        # Don't add to errors - fundamentals often unavailable

    # Get recent news (last 7 days)
    try:
        news_start = end_date - timedelta(days=7)
        data["news"] = route_to_vendor(
            "get_news",
            ticker,
            news_start.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
    except Exception as e:
        logger.debug(f"News not available for {ticker}: {e}")
        # Don't add to errors - news often unavailable

    return data


def _analyze_with_llm(ticker: str, data: Dict, llm) -> Dict[str, Any]:
    """
    Use LLM to analyze ticker data and generate screening score.

    Args:
        ticker: Stock ticker symbol
        data: Fetched data dict from _fetch_ticker_data()
        llm: Language model instance

    Returns:
        Analysis dict with screening_score, signals, recommendation, reasoning
    """
    system_prompt = """You are an expert stock screening analyst. Analyze the provided data and generate a preliminary screening assessment.

Your task is to evaluate this ticker and provide:
1. **Screening Score (0-100)**: Overall attractiveness (0=avoid, 100=highly promising)
2. **Key Signals**: Numerical indicators
   - momentum_score (-100 to 100): Price momentum trend
   - volume_trend (-1, 0, 1): Volume increasing(1), stable(0), or decreasing(-1)
   - technical_score (0-100): Technical indicator health
   - fundamental_score (0-100): Fundamental strength (if available)
   - sentiment_score (-100 to 100): News sentiment
3. **Recommendation**: One of: "strong_buy", "buy", "hold", "avoid"
4. **Reasoning**: 1-2 sentence explanation

Return ONLY a JSON object in this exact format:
{
    "screening_score": 75,
    "signals": {
        "momentum_score": 60,
        "volume_trend": 1,
        "technical_score": 70,
        "fundamental_score": 65,
        "sentiment_score": 50
    },
    "recommendation": "buy",
    "reasoning": "Strong technical indicators with positive momentum. Growing volume suggests institutional interest."
}

Be conservative - only give high scores (>70) to truly promising candidates.
If data is limited/missing, reflect that uncertainty in your score."""

    # Format the data for the LLM
    user_prompt = f"""Ticker: {ticker}
Analysis Date: {data['date']}

=== PRICE DATA ===
{data['price_data'] if data['price_data'] else "Not available"}

=== TECHNICAL INDICATORS ===
{data['indicators'] if data['indicators'] else "Not available"}

=== FUNDAMENTALS ===
{data['fundamentals'] if data['fundamentals'] else "Not available"}

=== RECENT NEWS (Last 7 days) ===
{data['news'] if data['news'] else "Not available"}

{"=== DATA ERRORS ===" if data.get('errors') else ""}
{chr(10).join(data['errors']) if data.get('errors') else ""}

Provide your screening analysis as JSON."""

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = llm.invoke(messages)
        content = response.content

        # Extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        analysis = json.loads(content)

        # Validate structure
        required_fields = ["screening_score", "signals", "recommendation", "reasoning"]
        if not all(field in analysis for field in required_fields):
            raise ValueError(f"Missing required fields in LLM response")

        # Add metadata
        analysis["ticker"] = ticker
        analysis["date"] = data["date"]
        analysis["data_available"] = {
            "price": data["price_data"] is not None,
            "indicators": data["indicators"] is not None,
            "fundamentals": data["fundamentals"] is not None,
            "news": data["news"] is not None,
        }

        logger.info(f"Analyzed {ticker}: score={analysis['screening_score']}, rec={analysis['recommendation']}")
        return analysis

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response for {ticker}: {e}")
        logger.error(f"Response content: {content}")
        return _fallback_analysis(ticker, data)

    except Exception as e:
        logger.error(f"Error analyzing {ticker} with LLM: {e}")
        return _fallback_analysis(ticker, data)


def _fallback_analysis(ticker: str, data: Dict) -> Dict[str, Any]:
    """
    Generate basic analysis when LLM fails.

    Uses simple heuristics based on available data.

    Args:
        ticker: Stock ticker symbol
        data: Fetched data dict

    Returns:
        Basic analysis dict
    """
    # Default conservative values
    analysis = {
        "ticker": ticker,
        "date": data["date"],
        "screening_score": 50,  # Neutral
        "signals": {
            "momentum_score": 0,
            "volume_trend": 0,
            "technical_score": 50,
            "fundamental_score": 50,
            "sentiment_score": 0,
        },
        "recommendation": "hold",
        "reasoning": "Unable to perform full analysis - insufficient data or analysis error",
        "data_available": {
            "price": data["price_data"] is not None,
            "indicators": data["indicators"] is not None,
            "fundamentals": data["fundamentals"] is not None,
            "news": data["news"] is not None,
        },
        "fallback": True
    }

    logger.warning(f"Using fallback analysis for {ticker}")
    return analysis


def analyze_ticker_lightweight(ticker: str, date: str, config: Dict) -> Dict[str, Any]:
    """
    Perform lightweight analysis on a single ticker.

    Fast, cost-efficient analysis using minimal LLM calls (1-2).
    Fetches key data and synthesizes into screening score.

    Args:
        ticker: Stock ticker symbol
        date: Analysis date in YYYY-MM-DD format
        config: Configuration dict (use create_screening_config() for optimization)

    Returns:
        Analysis dict with:
        - ticker: Ticker symbol
        - date: Analysis date
        - screening_score: 0-100 score
        - signals: Dict of key metrics
        - recommendation: "strong_buy", "buy", "hold", or "avoid"
        - reasoning: Brief explanation
        - data_available: Dict showing which data sources succeeded

    Example:
        >>> config = create_screening_config(DEFAULT_CONFIG)
        >>> result = analyze_ticker_lightweight("AAPL", "2024-01-15", config)
        >>> print(result["screening_score"])
        82
    """
    logger.info(f"Starting lightweight analysis: {ticker} on {date}")

    # Fetch all data
    data = _fetch_ticker_data(ticker, date, config)

    # Check if we have minimum viable data
    if not data["price_data"] and not data["indicators"]:
        logger.error(f"Insufficient data for {ticker} - cannot analyze")
        return {
            "ticker": ticker,
            "date": date,
            "screening_score": 0,
            "signals": {},
            "recommendation": "avoid",
            "reasoning": "Insufficient data available for analysis",
            "data_available": data.get("data_available", {}),
            "error": "no_data"
        }

    # Get LLM
    llm = _get_llm(config["quick_think_llm"], config)

    # Analyze with LLM
    analysis = _analyze_with_llm(ticker, data, llm)

    return analysis


def batch_analyze_tickers(
    tickers: List[str],
    date: str,
    config: Dict,
    max_workers: int = 5
) -> List[Dict[str, Any]]:
    """
    Analyze multiple tickers in parallel.

    Uses ThreadPoolExecutor to analyze tickers concurrently for speed.
    Gracefully handles failures - skips failed tickers and continues.

    Args:
        tickers: List of ticker symbols to analyze
        date: Analysis date in YYYY-MM-DD format
        config: Configuration dict (use create_screening_config())
        max_workers: Maximum parallel threads (default: 5)

    Returns:
        List of analysis dicts, sorted by screening_score (highest first)

    Example:
        >>> config = create_screening_config(DEFAULT_CONFIG)
        >>> tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "META"]
        >>> results = batch_analyze_tickers(tickers, "2024-01-15", config)
        >>> top_pick = results[0]  # Highest scoring ticker
        >>> print(f"{top_pick['ticker']}: {top_pick['screening_score']}")
        NVDA: 87
    """
    logger.info(f"Starting batch analysis of {len(tickers)} tickers with {max_workers} workers")

    results = []
    failed_tickers = []

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_ticker = {
            executor.submit(analyze_ticker_lightweight, ticker, date, config): ticker
            for ticker in tickers
        }

        # Collect results as they complete
        for i, future in enumerate(as_completed(future_to_ticker), 1):
            ticker = future_to_ticker[future]
            try:
                result = future.result()
                results.append(result)
                logger.info(f"[{i}/{len(tickers)}] Completed {ticker}: score={result.get('screening_score', 0)}")

            except Exception as e:
                logger.error(f"[{i}/{len(tickers)}] Failed to analyze {ticker}: {e}")
                failed_tickers.append(ticker)
                # Add error result
                results.append({
                    "ticker": ticker,
                    "date": date,
                    "screening_score": 0,
                    "signals": {},
                    "recommendation": "avoid",
                    "reasoning": f"Analysis failed: {str(e)}",
                    "error": "analysis_failed"
                })

    # Sort by screening score (highest first)
    results.sort(key=lambda x: x.get("screening_score", 0), reverse=True)

    logger.info(f"Batch analysis complete: {len(results) - len(failed_tickers)}/{len(tickers)} successful")
    if failed_tickers:
        logger.warning(f"Failed tickers: {failed_tickers}")

    return results


def extract_screening_signals(analysis_result: Dict[str, Any]) -> Dict[str, float]:
    """
    Extract numerical signals from analysis result.

    Convenience function to pull out key metrics for further processing,
    ranking, or ML model input.

    Args:
        analysis_result: Analysis dict from analyze_ticker_lightweight()

    Returns:
        Dict of numerical signals:
        - screening_score: 0-100
        - momentum_score: -100 to 100
        - volume_trend: -1, 0, or 1
        - technical_score: 0-100
        - fundamental_score: 0-100
        - sentiment_score: -100 to 100

    Example:
        >>> analysis = analyze_ticker_lightweight("AAPL", "2024-01-15", config)
        >>> signals = extract_screening_signals(analysis)
        >>> if signals["momentum_score"] > 50 and signals["technical_score"] > 70:
        ...     print("Strong technical setup!")
    """
    signals = analysis_result.get("signals", {})

    extracted = {
        "screening_score": analysis_result.get("screening_score", 0),
        "momentum_score": signals.get("momentum_score", 0),
        "volume_trend": signals.get("volume_trend", 0),
        "technical_score": signals.get("technical_score", 50),
        "fundamental_score": signals.get("fundamental_score", 50),
        "sentiment_score": signals.get("sentiment_score", 0),
    }

    return extracted


def filter_top_candidates(
    analysis_results: List[Dict[str, Any]],
    min_score: int = 60,
    max_candidates: int = 10
) -> List[str]:
    """
    Filter analysis results to top candidates.

    Helper function to select best tickers for full analysis.

    Args:
        analysis_results: List of analysis dicts from batch_analyze_tickers()
        min_score: Minimum screening_score threshold (default: 60)
        max_candidates: Maximum number of candidates to return (default: 10)

    Returns:
        List of ticker symbols for top candidates

    Example:
        >>> results = batch_analyze_tickers(tickers, date, config)
        >>> top_tickers = filter_top_candidates(results, min_score=65, max_candidates=5)
        >>> # Now run full multi-agent analysis on top_tickers
    """
    # Filter by minimum score
    qualified = [r for r in analysis_results if r.get("screening_score", 0) >= min_score]

    # Sort by score (highest first) and limit
    qualified.sort(key=lambda x: x.get("screening_score", 0), reverse=True)
    top_candidates = qualified[:max_candidates]

    tickers = [r["ticker"] for r in top_candidates]

    logger.info(f"Filtered to {len(tickers)} candidates (min_score={min_score}, max={max_candidates})")
    for i, result in enumerate(top_candidates, 1):
        logger.info(f"  {i}. {result['ticker']}: {result['screening_score']} - {result.get('recommendation', 'N/A')}")

    return tickers
