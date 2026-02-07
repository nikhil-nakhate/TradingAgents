"""
Ticker discovery and intent interpretation.

This module uses LLMs to interpret natural language trading intent
and convert it to structured screening criteria.
"""

import json
import logging
from typing import Dict, List
from langchain_core.messages import SystemMessage, HumanMessage

from tradingagents.dataflows.screeners import discover_tickers_by_criteria

logger = logging.getLogger(__name__)


def interpret_user_intent(description: str, llm) -> Dict:
    """
    Use LLM to convert natural language description to structured screening criteria.

    Args:
        description: Natural language description (e.g., "tech stocks with AI focus")
        llm: Language model to use for interpretation

    Returns:
        Dict with structured criteria:
        {
            "sectors": ["Technology", "Communication Services"],
            "keywords": ["AI", "artificial intelligence"],
            "market_cap_min": 1_000_000_000,
            "fundamentals": {
                "pe_ratio_max": 30,
                "revenue_growth_min": 0.15
            }
        }
    """
    system_prompt = """You are a financial analyst assistant that interprets trading intent.

Given a user's description of what they're looking for in stocks, extract structured screening criteria.

SECTOR CATEGORIES (use these exact names):
- Technology / Information Technology
- Healthcare / Health Care
- Financials / Financial Services
- Energy
- Consumer Discretionary
- Consumer Staples
- Industrials
- Communication Services
- Utilities
- Real Estate
- Materials

Return a JSON object with these fields (all optional):
{
    "sectors": ["Technology"],  // Array of sector names from above list
    "keywords": ["AI", "cloud"],  // Key themes/technologies to look for
    "market_cap_min": 1000000000,  // Minimum market cap in dollars (1B for large cap, 300M for mid cap, 50M for small cap)
    "fundamentals": {
        "pe_ratio_max": 30,  // Maximum P/E ratio
        "revenue_growth_min": 0.15  // Minimum revenue growth rate (0.15 = 15%)
    }
}

Guidelines:
- If user mentions "large cap" or "big companies": set market_cap_min to 10B+
- If user mentions "mid cap": set market_cap_min to 2B-10B
- If user mentions "small cap": set market_cap_min to 300M-2B
- If user mentions "growth": set revenue_growth_min to 0.15+
- If user mentions "value": set pe_ratio_max to 20
- Default to large cap (1B+) if not specified
- Extract key themes as keywords (AI, cloud, renewable, etc.)

Return ONLY the JSON object, no other text."""

    user_prompt = f"""User's trading intent: "{description}"

Extract the structured screening criteria as JSON."""

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = llm.invoke(messages)
        content = response.content

        # Extract JSON from response
        # Handle cases where LLM adds markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        criteria = json.loads(content)

        logger.info(f"Interpreted criteria: {criteria}")
        return criteria

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.error(f"Response content: {content}")

        # Fallback to basic extraction
        return _fallback_intent_extraction(description)

    except Exception as e:
        logger.error(f"Error in intent interpretation: {e}")
        return _fallback_intent_extraction(description)


def _fallback_intent_extraction(description: str) -> Dict:
    """
    Fallback intent extraction using keyword matching.

    Used when LLM parsing fails.

    Args:
        description: User's description

    Returns: Basic criteria dict
    """
    description_lower = description.lower()
    criteria = {}

    # Sector detection
    sector_keywords = {
        "Technology": ["tech", "technology", "software", "ai", "artificial intelligence", "cloud", "saas"],
        "Healthcare": ["healthcare", "health", "pharma", "biotech", "medical", "hospital"],
        "Financials": ["financial", "bank", "insurance", "fintech"],
        "Energy": ["energy", "oil", "gas", "renewable", "solar", "wind"],
        "Consumer Discretionary": ["consumer", "retail", "ecommerce", "e-commerce"],
    }

    detected_sectors = []
    for sector, keywords in sector_keywords.items():
        if any(keyword in description_lower for keyword in keywords):
            detected_sectors.append(sector)

    if detected_sectors:
        criteria["sectors"] = detected_sectors

    # Market cap detection
    if any(word in description_lower for word in ["large", "big", "mega"]):
        criteria["market_cap_min"] = 10_000_000_000  # 10B
    elif "mid" in description_lower or "medium" in description_lower:
        criteria["market_cap_min"] = 2_000_000_000  # 2B
    elif "small" in description_lower:
        criteria["market_cap_min"] = 300_000_000  # 300M
    else:
        criteria["market_cap_min"] = 1_000_000_000  # 1B default

    # Extract keywords
    keywords = []
    keyword_patterns = ["ai", "cloud", "renewable", "electric", "autonomous", "blockchain", "quantum"]
    for pattern in keyword_patterns:
        if pattern in description_lower:
            keywords.append(pattern)

    if keywords:
        criteria["keywords"] = keywords

    # Growth vs value
    fundamentals = {}
    if "growth" in description_lower:
        fundamentals["revenue_growth_min"] = 0.15
    if "value" in description_lower:
        fundamentals["pe_ratio_max"] = 20

    if fundamentals:
        criteria["fundamentals"] = fundamentals

    logger.info(f"Fallback extraction produced criteria: {criteria}")
    return criteria


def discover_tickers(criteria: Dict) -> List[str]:
    """
    Discover tickers based on structured criteria.

    This is a wrapper around the screener functions that adds logging
    and error handling.

    Args:
        criteria: Structured screening criteria from interpret_user_intent()

    Returns: List of ticker symbols (typically 20-30 candidates)
    """
    logger.info(f"Discovering tickers with criteria: {criteria}")

    try:
        tickers = discover_tickers_by_criteria(criteria)

        if not tickers:
            logger.warning("No tickers discovered, using default fallback")
            # Ultimate fallback - popular diverse portfolio
            tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META",
                      "TSLA", "JPM", "JNJ", "XOM"]

        logger.info(f"Discovered {len(tickers)} candidate tickers: {tickers[:10]}...")
        return tickers

    except Exception as e:
        logger.error(f"Error discovering tickers: {e}")
        # Return safe default list
        return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
