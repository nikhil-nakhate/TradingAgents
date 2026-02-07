"""
Test script for ticker discovery and lightweight analysis.

This script demonstrates the complete discovery workflow:
1. Interpret user intent → structured criteria
2. Discover candidate tickers
3. Lightweight screening analysis
4. Filter top candidates
"""

import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tradingagents.discovery import (
    interpret_user_intent,
    discover_tickers,
    create_screening_config,
    analyze_ticker_lightweight,
    batch_analyze_tickers,
    filter_top_candidates,
)
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.discovery.lightweight_analyzer import _get_llm


def test_intent_interpretation():
    """Test natural language intent interpretation."""
    print("\n" + "="*80)
    print("TEST 1: Intent Interpretation")
    print("="*80)

    llm = _get_llm(DEFAULT_CONFIG["quick_think_llm"], DEFAULT_CONFIG)

    test_descriptions = [
        "tech stocks with AI focus",
        "large cap healthcare growth stocks",
        "mid cap energy companies",
        "value stocks in the financial sector",
    ]

    for desc in test_descriptions:
        print(f"\nInput: '{desc}'")
        try:
            criteria = interpret_user_intent(desc, llm)
            print(f"Output: {criteria}")
        except Exception as e:
            print(f"Error: {e}")

    print("\n✓ Intent interpretation test complete")


def test_ticker_discovery():
    """Test ticker discovery/screening."""
    print("\n" + "="*80)
    print("TEST 2: Ticker Discovery")
    print("="*80)

    test_criteria = [
        {"sectors": ["Technology"], "market_cap_min": 1_000_000_000},
        {"sectors": ["Healthcare"], "market_cap_min": 10_000_000_000},
    ]

    for criteria in test_criteria:
        print(f"\nCriteria: {criteria}")
        try:
            tickers = discover_tickers(criteria)
            print(f"Discovered {len(tickers)} tickers: {tickers[:10]}...")
        except Exception as e:
            print(f"Error: {e}")

    print("\n✓ Ticker discovery test complete")


def test_lightweight_analysis():
    """Test lightweight analysis on a single ticker."""
    print("\n" + "="*80)
    print("TEST 3: Lightweight Analysis (Single Ticker)")
    print("="*80)

    # Use recent date
    test_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    test_ticker = "AAPL"

    print(f"\nAnalyzing {test_ticker} on {test_date}...")

    try:
        config = create_screening_config(DEFAULT_CONFIG)
        print(f"Screening config created: quick_think_llm={config['quick_think_llm']}")

        result = analyze_ticker_lightweight(test_ticker, test_date, config)

        print(f"\nResults:")
        print(f"  Ticker: {result['ticker']}")
        print(f"  Screening Score: {result.get('screening_score', 'N/A')}")
        print(f"  Recommendation: {result.get('recommendation', 'N/A')}")
        print(f"  Reasoning: {result.get('reasoning', 'N/A')}")
        print(f"  Data Available: {result.get('data_available', {})}")

        if result.get('signals'):
            print(f"\n  Signals:")
            for key, value in result['signals'].items():
                print(f"    {key}: {value}")

        print("\n✓ Single ticker analysis test complete")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_batch_analysis():
    """Test batch analysis on multiple tickers."""
    print("\n" + "="*80)
    print("TEST 4: Batch Analysis (Multiple Tickers)")
    print("="*80)

    # Use recent date
    test_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    test_tickers = ["AAPL", "MSFT", "GOOGL"]

    print(f"\nAnalyzing {len(test_tickers)} tickers on {test_date}...")
    print(f"Tickers: {test_tickers}")

    try:
        config = create_screening_config(DEFAULT_CONFIG)

        results = batch_analyze_tickers(
            test_tickers,
            test_date,
            config,
            max_workers=3
        )

        print(f"\nResults (sorted by screening_score):")
        print("-" * 80)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['ticker']:6s} | "
                  f"Score: {result.get('screening_score', 0):3d} | "
                  f"Rec: {result.get('recommendation', 'N/A'):12s} | "
                  f"{result.get('reasoning', 'N/A')[:50]}...")

        # Test filtering
        print("\n\nFiltering top candidates (min_score=60, max=2)...")
        top = filter_top_candidates(results, min_score=60, max_candidates=2)
        print(f"Top candidates: {top}")

        print("\n✓ Batch analysis test complete")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_full_workflow():
    """Test complete end-to-end workflow."""
    print("\n" + "="*80)
    print("TEST 5: Full Discovery Workflow")
    print("="*80)

    user_intent = "tech stocks with AI and cloud focus"
    test_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    print(f"\nUser Intent: '{user_intent}'")
    print(f"Analysis Date: {test_date}")

    try:
        # Step 1: Interpret intent
        print("\n[Step 1/4] Interpreting intent...")
        llm = _get_llm(DEFAULT_CONFIG["quick_think_llm"], DEFAULT_CONFIG)
        criteria = interpret_user_intent(user_intent, llm)
        print(f"Criteria: {criteria}")

        # Step 2: Discover tickers
        print("\n[Step 2/4] Discovering candidate tickers...")
        candidates = discover_tickers(criteria)
        print(f"Found {len(candidates)} candidates: {candidates[:10]}...")

        # Step 3: Lightweight screening (limit to 5 for speed)
        print(f"\n[Step 3/4] Screening top {min(5, len(candidates))} candidates...")
        config = create_screening_config(DEFAULT_CONFIG)
        results = batch_analyze_tickers(
            candidates[:5],
            test_date,
            config,
            max_workers=3
        )

        # Step 4: Filter top picks
        print("\n[Step 4/4] Filtering top candidates...")
        top_tickers = filter_top_candidates(results, min_score=60, max_candidates=3)

        print("\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        print(f"\nTop {len(top_tickers)} candidates for full multi-agent analysis:")
        for i, result in enumerate([r for r in results if r['ticker'] in top_tickers], 1):
            print(f"\n{i}. {result['ticker']} (Score: {result.get('screening_score', 0)})")
            print(f"   Recommendation: {result.get('recommendation', 'N/A')}")
            print(f"   Reasoning: {result.get('reasoning', 'N/A')}")

        print("\n✓ Full workflow test complete")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*80)
    print("TICKER DISCOVERY & LIGHTWEIGHT ANALYSIS TEST SUITE")
    print("="*80)

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ WARNING: OPENAI_API_KEY not set. Some tests may fail.")
        print("Set your API key: export OPENAI_API_KEY='your-key-here'\n")

    # Run tests
    try:
        test_intent_interpretation()
        test_ticker_discovery()
        test_lightweight_analysis()
        test_batch_analysis()
        test_full_workflow()

        print("\n" + "="*80)
        print("ALL TESTS COMPLETE")
        print("="*80)

    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
