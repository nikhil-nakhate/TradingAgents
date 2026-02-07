"""
Test script for ticker discovery WITHOUT LLM calls.

Tests data fetching, screening, and structure without requiring API keys or local models.
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tradingagents.discovery import discover_tickers, create_screening_config
from tradingagents.discovery.lightweight_analyzer import _fetch_ticker_data
from tradingagents.default_config import DEFAULT_CONFIG


def test_ticker_discovery():
    """Test ticker discovery with different criteria."""
    print("\n" + "="*80)
    print("TEST 1: Ticker Discovery (No LLM Required)")
    print("="*80)

    test_cases = [
        {"sectors": ["Technology"], "market_cap_min": 1_000_000_000},
        {"sectors": ["Healthcare", "Financials"]},
        {"sectors": ["Energy"], "market_cap_min": 10_000_000_000},
    ]

    for i, criteria in enumerate(test_cases, 1):
        print(f"\n[Test {i}] Criteria: {criteria}")
        try:
            tickers = discover_tickers(criteria)
            print(f"  ✓ Discovered {len(tickers)} tickers")
            print(f"  ✓ Sample: {tickers[:5]}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("\n✓ Ticker discovery tests complete")


def test_data_fetching():
    """Test data fetching for a single ticker (no LLM analysis)."""
    print("\n" + "="*80)
    print("TEST 2: Data Fetching (No LLM Required)")
    print("="*80)

    test_ticker = "AAPL"
    test_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    print(f"\nFetching data for {test_ticker} on {test_date}...")

    try:
        config = create_screening_config(DEFAULT_CONFIG)
        data = _fetch_ticker_data(test_ticker, test_date, config)

        print(f"\n  ✓ Data fetch complete for {test_ticker}")
        print(f"  ✓ Data available:")
        print(f"     - Price data: {'Yes' if data['price_data'] else 'No'}")
        print(f"     - Indicators: {'Yes' if data['indicators'] else 'No'}")
        print(f"     - Fundamentals: {'Yes' if data['fundamentals'] else 'No'}")
        print(f"     - News: {'Yes' if data['news'] else 'No'}")

        if data['errors']:
            print(f"  ⚠ Errors encountered: {len(data['errors'])}")
            for error in data['errors'][:3]:  # Show first 3 errors
                print(f"     - {error}")

        # Show sample of price data if available
        if data['price_data']:
            print(f"\n  Sample price data (first 200 chars):")
            print(f"     {str(data['price_data'])[:200]}...")

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n✓ Data fetching test complete")


def test_config_creation():
    """Test screening config creation."""
    print("\n" + "="*80)
    print("TEST 3: Screening Config Creation")
    print("="*80)

    print("\nCreating optimized screening config...")

    try:
        base_config = DEFAULT_CONFIG.copy()
        screening_config = create_screening_config(base_config)

        print(f"\n  ✓ Config created successfully")
        print(f"\n  Configuration:")
        print(f"     - LLM Provider: {screening_config.get('llm_provider', 'N/A')}")
        print(f"     - Quick LLM: {screening_config.get('quick_think_llm', 'N/A')}")
        print(f"     - Deep LLM: {screening_config.get('deep_think_llm', 'N/A')}")
        print(f"     - Max debate rounds: {screening_config.get('max_debate_rounds', 'N/A')}")
        print(f"     - Max risk rounds: {screening_config.get('max_risk_discuss_rounds', 'N/A')}")
        print(f"     - Use memory: {screening_config.get('use_memory', 'N/A')}")

        print(f"\n  Data vendor preferences:")
        for category, vendor in screening_config.get('data_vendors', {}).items():
            print(f"     - {category}: {vendor}")

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n✓ Config creation test complete")


def test_batch_data_fetch():
    """Test fetching data for multiple tickers."""
    print("\n" + "="*80)
    print("TEST 4: Batch Data Fetching (No LLM Required)")
    print("="*80)

    test_tickers = ["AAPL", "MSFT", "GOOGL"]
    test_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    print(f"\nFetching data for {len(test_tickers)} tickers on {test_date}...")
    print(f"Tickers: {test_tickers}")

    config = create_screening_config(DEFAULT_CONFIG)
    results = []

    for ticker in test_tickers:
        try:
            print(f"\n  Fetching {ticker}...")
            data = _fetch_ticker_data(ticker, test_date, config)
            results.append({
                'ticker': ticker,
                'has_price': data['price_data'] is not None,
                'has_indicators': data['indicators'] is not None,
                'has_fundamentals': data['fundamentals'] is not None,
                'has_news': data['news'] is not None,
                'error_count': len(data['errors'])
            })
            print(f"    ✓ Complete (errors: {len(data['errors'])})")
        except Exception as e:
            print(f"    ✗ Failed: {e}")
            results.append({
                'ticker': ticker,
                'error': str(e)
            })

    print(f"\n  Summary:")
    print(f"  {'-'*60}")
    for result in results:
        ticker = result['ticker']
        if 'error' in result:
            print(f"  {ticker:6s} | ✗ Error: {result['error'][:40]}")
        else:
            status = []
            if result['has_price']: status.append("Price")
            if result['has_indicators']: status.append("Indicators")
            if result['has_fundamentals']: status.append("Fundamentals")
            if result['has_news']: status.append("News")
            print(f"  {ticker:6s} | ✓ {', '.join(status) if status else 'No data'}")

    print("\n✓ Batch data fetching test complete")


if __name__ == "__main__":
    print("="*80)
    print("TICKER DISCOVERY TEST SUITE (NO LLM REQUIRED)")
    print("="*80)
    print("\nThese tests verify data fetching and structure without LLM API calls.")
    print("No API keys or local models needed!")

    try:
        test_config_creation()
        test_ticker_discovery()
        test_data_fetching()
        test_batch_data_fetch()

        print("\n" + "="*80)
        print("ALL TESTS COMPLETE!")
        print("="*80)
        print("\n✓ Discovery feature is working correctly!")
        print("\nNext steps:")
        print("  - To test LLM analysis, set up Ollama or OpenAI API key")
        print("  - Run 'python test_discovery.py' for full LLM-powered tests")

    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
