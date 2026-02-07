# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

TradingAgents is a multi-agent LLM trading framework that uses specialized agents (analysts, researchers, risk managers, traders) to collaboratively evaluate market conditions and make trading decisions. Built with LangGraph for workflow orchestration and LangChain for LLM integration.

## Essential Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys (required)
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and ALPHA_VANTAGE_API_KEY
```

### Running the System
```bash
# Run with CLI interface (interactive ticker/date selection)
python -m cli.main

# Run programmatically with main.py
python main.py

# Run test script (performance benchmark for yfinance)
python test.py
```

### Development
```bash
# No formal test suite exists - test.py is a performance benchmark
# Manual testing is done via main.py or cli.main

# The framework makes extensive API calls, so use cheaper models for testing:
# In main.py or your code, set config["deep_think_llm"] = "gpt-4o-mini"
# and config["quick_think_llm"] = "gpt-4o-mini"
```

## Architecture Overview

### Multi-Agent System Hierarchy

The system uses a **debate-driven multi-agent architecture** with 5 agent categories:

1. **Analyst Agents** (`tradingagents/agents/analysts/`)
   - Market Analyst: Technical analysis (price, indicators)
   - Social Media Analyst: Sentiment analysis
   - News Analyst: News & geopolitical events
   - Fundamentals Analyst: Financial statements & company metrics
   - Each agent calls specific tools via LangChain ToolNode

2. **Researcher Agents** (`tradingagents/agents/researchers/`)
   - Bull Researcher: Optimistic investment perspective
   - Bear Researcher: Risk-focused counterargument
   - Engage in structured debate loops (max 2*N rounds)

3. **Management Agents** (`tradingagents/agents/managers/`)
   - Research Manager: Arbitrates analyst/researcher debate → investment plan
   - Risk Manager: Makes final decision after risk debate
   - Use "deep thinking" LLM for complex reasoning

4. **Risk Analysts** (`tradingagents/agents/risk_mgmt/`)
   - Aggressive Debator: High-reward focus
   - Conservative Debator: Capital preservation focus
   - Neutral Debator: Balanced perspective
   - 3-way rotating debate (max 3*N rounds)

5. **Trader Agent** (`tradingagents/agents/trader/`)
   - Executes final decision based on investment plan
   - Retrieves lessons from past trades via ChromaDB memory
   - Outputs: BUY/HOLD/SELL recommendation

### Execution Flow
```
[Analysts] → tool calls → analysis reports
    ↓
[Bull/Bear Researchers] ⟷ debate
    ↓
[Research Manager] → investment plan
    ↓
[Trader] → execution plan
    ↓
[Risk Analysts] ⟷ 3-way debate
    ↓
[Risk Manager] → FINAL DECISION
```

### Data Flow Architecture

**Vendor-Agnostic Abstraction Layer** (`tradingagents/dataflows/`)

The dataflows module routes tool calls to configured vendors with automatic fallback:

- **4 Data Categories:**
  - `core_stock_apis`: OHLCV price data
  - `technical_indicators`: Technical indicators (MACD, RSI, etc.)
  - `fundamental_data`: Financial statements
  - `news_data`: News, insider transactions

- **Supported Vendors:**
  - `yfinance`: Stock data, indicators, financials (default for prices/indicators)
  - `alpha_vantage`: Stock data, indicators, fundamentals, news (default for fundamentals/news)
  - `openai`: LLM-generated analysis
  - `google`: News search
  - `local`: Cached/simulated data (for offline testing)

- **Configuration Pattern:**
```python
config["data_vendors"] = {
    "core_stock_apis": "yfinance",           # Category-level default
    "technical_indicators": "yfinance",
    "fundamental_data": "alpha_vantage",
    "news_data": "alpha_vantage",
}
config["tool_vendors"] = {
    "get_news": "openai",  # Tool-level override (takes precedence)
}
```

- **Fallback Mechanism:** If primary vendor fails (rate limit, error), automatically tries fallback vendors

### LangGraph State Management

**State Definition** (`tradingagents/agents/utils/agent_states.py`):
```python
AgentState:
  - company_of_interest, trade_date
  - market_report, sentiment_report, news_report, fundamentals_report
  - investment_debate_state (bull/bear arguments, rounds)
  - risk_debate_state (risky/safe/neutral arguments, rounds)
  - investment_plan, trader_investment_plan
  - final_trade_decision
```

**Graph Topology** (`tradingagents/graph/setup.py`):
- START → Analyst Chain → Bull/Bear Debate → Research Manager → Trader → Risk Debate → Risk Manager → END
- Conditional edges route between debate loops and tool nodes
- Message history cleared between phases to manage LLM context

**Conditional Logic** (`tradingagents/graph/conditional_logic.py`):
- Tool execution detection: routes to ToolNode if agent requests tools
- Debate continuation: based on round count and last speaker
- Risk rotation: Risky → Safe → Neutral → Risky

### Memory & Learning System

**ChromaDB Vector Memory** (`tradingagents/agents/utils/memory.py`):
- 5 separate memories (bull, bear, trader, invest judge, risk manager)
- Stores past trading situations with OpenAI embeddings
- Agents retrieve similar situations (n_matches=2) during decision-making

**Reflection System** (`tradingagents/graph/reflection.py`):
```python
# After trading execution, reflect on outcome
ta.reflect_and_remember(position_returns)  # Update memories with lessons
```

## Configuration System

**3 Configuration Levels:**

1. **Default Config** (`tradingagents/default_config.py`)
   - LLM provider & models
   - Debate rounds, recursion limits
   - Data vendor defaults
   - Directory paths

2. **Runtime Config Override:**
```python
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "o4-mini"          # Deep reasoning (o1-mini/o4-mini/gpt-4o)
config["quick_think_llm"] = "gpt-4o-mini"     # Fast thinking
config["max_debate_rounds"] = 2               # Analyst/researcher debate rounds
config["max_risk_discuss_rounds"] = 2         # Risk debate rounds
config["llm_provider"] = "openai"             # openai, anthropic, google
config["backend_url"] = "https://api.openai.com/v1"  # Custom endpoint (OpenRouter, Ollama)
```

3. **Environment Variables:**
   - `OPENAI_API_KEY`: Required for LLM calls
   - `ALPHA_VANTAGE_API_KEY`: Required for fundamental/news data (default config)
   - `TRADINGAGENTS_RESULTS_DIR`: Output directory (default: `./results`)

## Key Implementation Patterns

### Adding New Agents

Agents follow a standard pattern:
```python
from langchain_core.messages import SystemMessage, HumanMessage
from tradingagents.agents.utils.agent_states import AgentState

def new_agent(state: AgentState, config: dict) -> dict:
    """Agent logic"""
    llm = get_llm(config["quick_think_llm"], config)  # or deep_think_llm

    # Retrieve from memory if needed
    memory = get_memory("agent_type", config)
    similar_cases = memory.retrieve_memory(query, n_matches=2)

    # Build messages
    messages = [
        SystemMessage(content="System prompt..."),
        HumanMessage(content=f"Analysis task for {state['company_of_interest']}...")
    ]

    # Call LLM
    response = llm.invoke(messages)

    return {"new_state_field": response.content}
```

### Adding New Tools

Tools route to vendors via `route_to_vendor()`:
```python
from langchain_core.tools import tool
from tradingagents.dataflows.interface import route_to_vendor

@tool
def new_data_tool(symbol: str, date: str) -> str:
    """Tool description for LLM"""
    return route_to_vendor("new_data_tool", symbol, date)
```

Then implement vendor-specific functions in `tradingagents/dataflows/<vendor>.py`:
```python
def new_data_tool_yfinance(symbol: str, date: str) -> str:
    # Implementation
    return result
```

Register in `interface.py` vendor mappings.

### Adding New Vendors

1. Create `tradingagents/dataflows/<vendor_name>.py`
2. Implement data fetching functions (matching tool signatures)
3. Register in `interface.py` VENDOR_MAPPINGS:
```python
VENDOR_MAPPINGS = {
    "new_vendor": {
        "get_stock_data": get_stock_data_newvendor,
        "get_indicators": get_indicators_newvendor,
        ...
    }
}
```
4. Add to FALLBACK_VENDORS if desired
5. Set in config: `config["data_vendors"]["core_stock_apis"] = "new_vendor"`

## Important Constraints

### API Usage & Costs
- The framework makes **many LLM API calls** per analysis (10+ agents per decision)
- For testing, use cheaper models: `gpt-4o-mini` instead of `o1-preview` or `gpt-4o`
- Alpha Vantage rate limits: 60 requests/minute for TradingAgents users (partnership)
- Default config uses yfinance (free, no API key) for price/indicators, Alpha Vantage for fundamentals/news

### Research Framework Warning
- This is a **research framework**, not production trading software
- No formal test suite exists (only performance benchmarks in test.py)
- Trading performance varies by LLM model, temperature, data quality, market conditions
- See disclaimer: https://tauric.ai/disclaimer/

### Non-Deterministic Behavior
- LLM-based decisions are non-deterministic (temperature, sampling)
- Debate outcomes vary between runs even with same inputs
- Memory system adds context-dependence (past trades influence future decisions)

## File Organization Patterns

```
tradingagents/
├── agents/
│   ├── analysts/         # 4 analyst types (market, social, news, fundamentals)
│   ├── researchers/      # Bull/Bear debate agents
│   ├── risk_mgmt/        # 3 risk perspective agents
│   ├── managers/         # Research Manager, Risk Manager
│   ├── trader/           # Trader execution agent
│   └── utils/
│       ├── agent_states.py      # State definitions
│       ├── memory.py            # ChromaDB memory system
│       ├── core_stock_tools.py  # Price data tools
│       ├── technical_indicators_tools.py
│       ├── fundamental_data_tools.py
│       └── news_data_tools.py
├── dataflows/
│   ├── interface.py      # Vendor routing logic
│   ├── config.py         # Global config management
│   ├── y_finance.py      # yfinance implementations
│   ├── alpha_vantage.py  # Alpha Vantage implementations
│   ├── openai_calls.py   # OpenAI LLM-based data
│   └── data_cache/       # Local cached data
├── graph/
│   ├── trading_graph.py  # Main TradingAgentsGraph class
│   ├── setup.py          # LangGraph topology definition
│   ├── conditional_logic.py  # Edge routing logic
│   └── reflection.py     # Memory update system
└── default_config.py     # Default configuration
```

## Common Modifications

### Change LLM Provider
```python
# Use Anthropic models
config["llm_provider"] = "anthropic"
config["deep_think_llm"] = "claude-3-5-sonnet-20241022"
config["quick_think_llm"] = "claude-3-5-sonnet-20241022"

# Use Google models
config["llm_provider"] = "google"
config["deep_think_llm"] = "gemini-2.0-flash-exp"
config["quick_think_llm"] = "gemini-2.0-flash-exp"

# Use local/OpenRouter
config["backend_url"] = "http://localhost:11434/v1"  # Ollama
config["backend_url"] = "https://openrouter.ai/api/v1"  # OpenRouter
```

### Adjust Debate Depth
```python
# More thorough analysis (more API calls, higher cost)
config["max_debate_rounds"] = 3          # Bull/Bear rounds (2*N messages)
config["max_risk_discuss_rounds"] = 3    # Risk debate rounds (3*N messages)

# Faster, cheaper analysis
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1
```

### Switch Data Sources
```python
# Use OpenAI for news instead of Alpha Vantage
config["data_vendors"]["news_data"] = "openai"

# Use Alpha Vantage for all data (requires API key)
config["data_vendors"] = {
    "core_stock_apis": "alpha_vantage",
    "technical_indicators": "alpha_vantage",
    "fundamental_data": "alpha_vantage",
    "news_data": "alpha_vantage",
}

# Use local cached data (offline mode)
config["data_vendors"] = {k: "local" for k in config["data_vendors"]}
```

## Debugging

Enable debug mode for detailed logging:
```python
ta = TradingAgentsGraph(debug=True, config=config)
```

This logs:
- Agent invocations and outputs
- Tool calls and results
- Debate progression
- State transitions
- LangGraph execution trace

Results are saved to `results/` directory (or `TRADINGAGENTS_RESULTS_DIR`) as JSON files.
