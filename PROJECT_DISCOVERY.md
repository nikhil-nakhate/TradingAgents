# Ticker Discovery & Screening Feature

## Project Status: IN PROGRESS
**Started:** 2026-01-02
**Current Phase:** Implementing lightweight analyzer
**Last Updated:** 2026-01-03

---

## Overview

Adding a ticker discovery and screening system to TradingAgents that allows users to:
1. Express trading intent in natural language (e.g., "tech stocks with AI focus")
2. Screen and filter tickers based on criteria (sector, market cap, fundamentals)
3. Perform lightweight analysis on discovered tickers before full multi-agent evaluation
4. Batch analyze multiple candidates efficiently

## Architecture

```
User Intent (Natural Language)
    ↓
[LLM Intent Interpreter] → Structured Criteria
    ↓
[Stock Screener] → Candidate Tickers (20-30)
    ↓
[Lightweight Analyzer] → Filtered Tickers (5-10)
    ↓
[Full Multi-Agent System] → Final Trade Decisions
```

## Components

### 1. Stock Screener ✅ COMPLETE
**File:** `tradingagents/dataflows/screeners.py`

**Functions:**
- `screen_yfinance(criteria)` - Free screening using yfinance + Wikipedia S&P 500
- `screen_finnhub(criteria, api_key)` - Finnhub API screening
- `get_fallback_ticker_list(criteria)` - Curated fallback lists by sector
- `discover_tickers_by_criteria(criteria)` - Main entry point with vendor fallback

**Features:**
- Filters by sector (12 major sectors supported)
- Market cap filtering (large/mid/small cap)
- Fallback mechanism: yfinance → finnhub → curated lists
- Returns 20-30 candidate tickers

**Sectors Supported:**
- Technology / Information Technology
- Healthcare / Health Care
- Financials / Financial Services
- Energy
- Consumer Discretionary / Consumer Staples
- Industrials
- Communication Services
- Utilities
- Real Estate
- Materials

### 2. Intent Interpreter ✅ COMPLETE
**File:** `tradingagents/discovery/ticker_screener.py`

**Functions:**
- `interpret_user_intent(description, llm)` - LLM-based natural language → criteria
- `_fallback_intent_extraction(description)` - Keyword-based fallback
- `discover_tickers(criteria)` - Wrapper with error handling

**Example Transformations:**
```python
"tech stocks with AI focus" → {
    "sectors": ["Technology"],
    "keywords": ["AI", "artificial intelligence"],
    "market_cap_min": 1_000_000_000
}

"large cap healthcare growth stocks" → {
    "sectors": ["Healthcare"],
    "market_cap_min": 10_000_000_000,
    "fundamentals": {"revenue_growth_min": 0.15}
}
```

### 3. Lightweight Analyzer ⚠️ IN PROGRESS
**File:** `tradingagents/discovery/lightweight_analyzer.py` **[MISSING - BUILDING NOW]**

**Required Functions:**
- `create_screening_config(base_config)` - Create minimal config for fast analysis
- `analyze_ticker_lightweight(ticker, date, config)` - Quick single-ticker analysis
- `batch_analyze_tickers(tickers, date, config)` - Parallel batch analysis
- `extract_screening_signals(analysis_result)` - Extract key signals/scores

**Design Goals:**
- Fast analysis (< 5 seconds per ticker)
- Minimal LLM calls (1-2 per ticker vs 10+ in full system)
- Use cheaper models (gpt-4o-mini)
- Focus on key signals:
  - Price momentum (trending up/down)
  - Volume patterns (increasing/decreasing)
  - Technical indicators (RSI, MACD)
  - Fundamental health score
  - News sentiment (positive/negative/neutral)
- Return screening score (0-100) to rank candidates

**Approach:**
- Reuse existing tool infrastructure (get_stock_data, get_indicators, etc.)
- Single-agent analysis (no debate loops)
- Simplified state management
- Batch processing with ThreadPoolExecutor for parallelization

### 4. Module Integration ✅ COMPLETE
**File:** `tradingagents/discovery/__init__.py`

Exports all discovery functions for easy import.

---

## Additional Changes

### LlamaCpp Support ✅ COMPLETE
Added local model support via llama.cpp for cost reduction during development.

**Files Modified:**
- `tradingagents/default_config.py` - Added llamacpp config keys
- `tradingagents/graph/trading_graph.py` - Added llamacpp provider logic
- `cli/utils.py` - Added llamacpp model selection in CLI

**Models Supported:**
- DeepSeek-R1-Distill series (8B, 32B, 70B)
- Qwen2.5 series
- Llama-3.3 series

**Usage:**
```python
config["llm_provider"] = "llamacpp"
config["llamacpp_server_url"] = "http://localhost:8000/v1"
```

---

## Implementation Checklist

- [x] Stock screener implementation
  - [x] yfinance screening
  - [x] finnhub screening
  - [x] Fallback curated lists
  - [x] Vendor fallback mechanism
- [x] Intent interpreter
  - [x] LLM-based extraction
  - [x] Keyword fallback
  - [x] Sector mapping
  - [x] Market cap detection
- [ ] **Lightweight analyzer** ← CURRENT FOCUS
  - [ ] create_screening_config()
  - [ ] analyze_ticker_lightweight()
  - [ ] batch_analyze_tickers()
  - [ ] extract_screening_signals()
- [ ] Integration & Testing
  - [ ] CLI integration (discovery mode)
  - [ ] Example/demo script
  - [ ] End-to-end test with real tickers
- [ ] Documentation
  - [ ] Update README.md with discovery usage
  - [ ] Add discovery examples
  - [ ] Document configuration options

---

## Current Task: Lightweight Analyzer Implementation

**What it needs to do:**

1. **create_screening_config(base_config)**
   - Take full trading config
   - Return stripped-down config for screening:
     - Use quick_think_llm only
     - Disable memory/reflection
     - Minimal debate rounds (0)
     - Fast vendor preferences (yfinance over alpha_vantage)

2. **analyze_ticker_lightweight(ticker, date, config)**
   - Fetch core data (price, volume, indicators)
   - Fetch fundamental snapshot (if available)
   - Fetch recent news sentiment
   - Single LLM call to synthesize signals
   - Return analysis dict with:
     - screening_score (0-100)
     - signals (dict of key metrics)
     - recommendation ("strong_buy", "buy", "hold", "avoid")
     - reasoning (brief explanation)

3. **batch_analyze_tickers(tickers, date, config)**
   - Use ThreadPoolExecutor for parallel analysis
   - Call analyze_ticker_lightweight() for each ticker
   - Return sorted list by screening_score
   - Handle errors gracefully (skip failed tickers)

4. **extract_screening_signals(analysis_result)**
   - Parse analysis dict
   - Extract numerical signals:
     - momentum_score (-100 to 100)
     - volume_trend (-1, 0, 1)
     - technical_score (0-100)
     - fundamental_score (0-100)
     - sentiment_score (-100 to 100)
   - Return signals dict

**Data to Use:**
- Price data: Last 30 days OHLCV
- Technical indicators: RSI, MACD, SMA(20, 50)
- Fundamentals: Market cap, P/E ratio (if available)
- News: Last 7 days (if available)

**LLM Prompt Strategy:**
```
You are a stock screening analyst. Analyze this ticker for preliminary screening.

Data:
- Price: [recent price action]
- Volume: [volume trends]
- RSI: [value]
- MACD: [signal]
- Fundamentals: [P/E, market cap if available]
- Recent News: [headlines/sentiment]

Provide:
1. Screening Score (0-100): How promising is this ticker?
2. Key Signals: momentum, volume_trend, technical_score, fundamental_score, sentiment
3. Recommendation: strong_buy, buy, hold, or avoid
4. Brief Reasoning: 1-2 sentences

Return as JSON.
```

---

## Testing Plan

Once lightweight_analyzer is complete:

1. **Unit Test:**
   ```python
   from tradingagents.discovery import *

   # Test intent interpretation
   criteria = interpret_user_intent("tech stocks with AI", llm)

   # Test ticker discovery
   tickers = discover_tickers(criteria)

   # Test lightweight analysis
   config = create_screening_config(DEFAULT_CONFIG)
   results = batch_analyze_tickers(tickers[:5], "2024-01-15", config)
   ```

2. **Integration Test:**
   - Run full pipeline: intent → discover → screen → analyze
   - Verify top 3 candidates pass to full trading graph
   - Compare performance (time, cost) vs full analysis

3. **End-to-End Demo:**
   - Create `examples/discovery_demo.py`
   - Show complete workflow with real data

---

## Usage Examples (Planned)

### Programmatic Usage
```python
from tradingagents.discovery import *
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 1. Interpret intent
llm = get_llm("gpt-4o-mini", DEFAULT_CONFIG)
criteria = interpret_user_intent("large cap tech stocks with AI focus", llm)

# 2. Discover candidates
candidates = discover_tickers(criteria)  # Returns ~20-30 tickers

# 3. Lightweight screening
screening_config = create_screening_config(DEFAULT_CONFIG)
analyzed = batch_analyze_tickers(candidates, "2024-01-15", screening_config)

# 4. Take top candidates for full analysis
top_tickers = [a['ticker'] for a in analyzed[:5] if a['screening_score'] > 60]

# 5. Run full multi-agent analysis
ta = TradingAgentsGraph(config=DEFAULT_CONFIG)
for ticker in top_tickers:
    result = ta.run(ticker, "2024-01-15")
    print(f"{ticker}: {result['final_trade_decision']}")
```

### CLI Usage (To Be Implemented)
```bash
# Interactive mode with discovery
python -m cli.main --discovery

# Prompts:
# > What type of stocks are you looking for?
# > "tech stocks focused on AI and cloud computing"
#
# [Discovering candidates...]
# Found 25 candidates, screening...
# Top 5 candidates:
# 1. NVDA (score: 87) - Strong momentum, positive sentiment
# 2. MSFT (score: 82) - Solid fundamentals, AI exposure
# 3. GOOGL (score: 78) - Cloud growth, AI investments
# ...
#
# Select tickers for full analysis: [1,2,3]
```

---

## Files Changed/Added

**New Files:**
- `tradingagents/dataflows/screeners.py` ✅
- `tradingagents/discovery/__init__.py` ✅
- `tradingagents/discovery/ticker_screener.py` ✅
- `tradingagents/discovery/lightweight_analyzer.py` ⚠️ IN PROGRESS
- `PROJECT_DISCOVERY.md` ✅ (this file)
- `configs/llamacpp_server.json` ✅
- `scripts/download_models.py` ✅
- `scripts/start_llamacpp_server.sh` ✅

**Modified Files:**
- `tradingagents/default_config.py` - Added llamacpp config
- `tradingagents/graph/trading_graph.py` - Added llamacpp provider
- `cli/utils.py` - Added llamacpp CLI options
- `README.md` - (pending) Add discovery documentation
- `requirements.txt` - (pending) Add finnhub-python if needed

**Documentation:**
- `docs/` - New directory (pending content)

---

## Next Steps (In Order)

1. ✅ Create project tracking doc (this file)
2. **→ Implement lightweight_analyzer.py** ← YOU ARE HERE
3. Test lightweight analyzer with sample tickers
4. Integrate into CLI with discovery mode
5. Create example/demo script
6. Update README.md with usage guide
7. Optional: Add unit tests

---

## Notes & Decisions

### Why Lightweight Analyzer?
- Full multi-agent analysis is expensive (10+ LLM calls, $0.10-0.50 per ticker)
- Screening 30 candidates would cost $3-15
- Lightweight analysis (1-2 LLM calls, $0.01-0.02 per ticker) = $0.20-0.60 for 30
- Filters down to top 5-10 for full analysis
- Total cost: ~$1-2 vs $3-15 (60-80% savings)

### Design Choices
- **Reuse existing tools:** Don't duplicate data fetching logic
- **Single agent:** No debate loops for speed
- **Parallel processing:** ThreadPoolExecutor for batch analysis
- **JSON output:** LLM returns structured data for easy parsing
- **Graceful degradation:** Continue if some tickers fail

### Future Enhancements
- Add more screening vendors (Polygon, IEX Cloud)
- ML-based scoring (train on historical performance)
- Real-time screening (market hours only)
- Watchlist tracking
- Scheduled screening jobs

---

## Questions/Issues

- [ ] Should lightweight analyzer use same memory system or separate?
  - **Decision:** No memory for screening (keep it stateless and fast)

- [ ] How to handle rate limits during batch analysis?
  - **Decision:** Add exponential backoff, skip failed tickers

- [ ] Should we cache screening results?
  - **Decision:** Yes, cache for 1 hour (screening is date-specific)

---

## Session Recovery Instructions

If session is interrupted, continue with:
1. Read `PROJECT_DISCOVERY.md` (this file) for context
2. Check current task in "Next Steps" section
3. Review implementation checklist for what's complete
4. Continue from last incomplete task

**Current state:** Implementing `lightweight_analyzer.py` - all 4 functions needed
