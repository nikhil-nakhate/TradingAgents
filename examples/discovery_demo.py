"""
Discovery Feature Demo

This script demonstrates the complete ticker discovery and screening workflow.
"""

import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.discovery import (
    interpret_user_intent,
    discover_tickers,
    create_screening_config,
    batch_analyze_tickers,
    filter_top_candidates,
)
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.discovery.lightweight_analyzer import _get_llm


def main():
    print("="*80)
    print("TRADINGAGENTS DISCOVERY FEATURE DEMO")
    print("="*80)
    print()

    # Configuration
    # For llama.cpp local models:
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "llamacpp"
    config["quick_think_llm"] = "deepseek-r1-distill-llama-8b"
    config["llamacpp_server_url"] = "http://localhost:8000/v1"

    # For OpenAI (if you have API key):
    # config["llm_provider"] = "openai"
    # config["quick_think_llm"] = "gpt-4o-mini"

    print(f"Configuration:")
    print(f"  Provider: {config['llm_provider']}")
    print(f"  Model: {config['quick_think_llm']}")
    print()

    # Step 1: User intent
    user_intent = "tech stocks with AI and cloud focus"
    print(f"[Step 1/5] User Intent: '{user_intent}'")
    print()

    # Step 2: Interpret intent
    print("[Step 2/5] Interpreting intent with LLM...")
    try:
        llm = _get_llm(config["quick_think_llm"], config)
        criteria = interpret_user_intent(user_intent, llm)
        print(f"  ✓ Extracted criteria: {criteria}")
    except Exception as e:
        print(f"  ⚠ LLM interpretation failed, using fallback")
        print(f"  Error: {e}")
        criteria = {"sectors": ["Technology"], "market_cap_min": 1_000_000_000}
    print()

    # Step 3: Discover tickers
    print("[Step 3/5] Discovering candidate tickers...")
    candidates = discover_tickers(criteria)
    print(f"  ✓ Found {len(candidates)} candidates")
    print(f"  ✓ Sample: {candidates[:10]}")
    print()

    # Step 4: Lightweight screening
    test_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    num_to_screen = min(5, len(candidates))

    print(f"[Step 4/5] Screening top {num_to_screen} candidates (date: {test_date})...")
    screening_config = create_screening_config(config)

    try:
        results = batch_analyze_tickers(
            candidates[:num_to_screen],
            test_date,
            screening_config,
            max_workers=3
        )
        print(f"  ✓ Screening complete")
    except Exception as e:
        print(f"  ✗ Screening failed: {e}")
        print(f"  Note: Make sure llama.cpp server is running or OpenAI API key is set")
        return
    print()

    # Step 5: Filter top picks
    print("[Step 5/5] Filtering top candidates...")
    top_tickers = filter_top_candidates(results, min_score=60, max_candidates=3)

    print()
    print("="*80)
    print("FINAL RESULTS")
    print("="*80)
    print()
    print(f"Top {len(top_tickers)} candidates for full multi-agent analysis:")
    print()

    for i, result in enumerate([r for r in results if r['ticker'] in top_tickers], 1):
        print(f"{i}. {result['ticker']} (Score: {result.get('screening_score', 0)})")
        print(f"   Recommendation: {result.get('recommendation', 'N/A')}")
        print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
        print()

    print("="*80)
    print("NEXT STEPS")
    print("="*80)
    print()
    print("These top candidates can now be passed to the full TradingAgents")
    print("multi-agent system for comprehensive analysis:")
    print()
    print("  from tradingagents.graph.trading_graph import TradingAgentsGraph")
    print()
    print(f"  ta = TradingAgentsGraph(config=config)")
    print(f"  for ticker in {top_tickers}:")
    print(f"      result = ta.run(ticker, '{test_date}')")
    print(f"      print(f\"{{ticker}}: {{result['final_trade_decision']}}\")")
    print()


if __name__ == "__main__":
    main()
