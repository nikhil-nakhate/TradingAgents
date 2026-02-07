"""
Stock screening implementations for various vendors.

This module provides functions to discover and filter tickers based on
screening criteria using different data providers.
"""

import logging
from typing import List, Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)


def screen_yfinance(criteria: dict) -> List[str]:
    """
    Screen stocks using yfinance and Wikipedia S&P 500 list.

    Args:
        criteria: {
            "sectors": ["Technology", "Healthcare"],
            "market_cap_min": 1_000_000_000,
            "keywords": ["AI", "cloud"],
            ...
        }

    Returns: List of ticker symbols matching criteria
    """
    tickers = []

    try:
        import yfinance as yf

        # Get S&P 500 tickers from Wikipedia
        logger.info("Fetching S&P 500 ticker list from Wikipedia...")
        sp500_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500_table = pd.read_html(sp500_url)[0]
        all_tickers = sp500_table['Symbol'].tolist()

        # Create sector mapping
        sector_map = sp500_table.set_index('Symbol')['GICS Sector'].to_dict()

        # Filter by sector if specified
        if 'sectors' in criteria and criteria['sectors']:
            logger.info(f"Filtering by sectors: {criteria['sectors']}")
            all_tickers = [
                t for t in all_tickers
                if sector_map.get(t) in criteria['sectors']
            ]
            logger.info(f"After sector filter: {len(all_tickers)} tickers")

        # Apply market cap filter if specified
        if 'market_cap_min' in criteria:
            logger.info(f"Applying market cap filter: ${criteria['market_cap_min']:,}+")
            filtered = []

            # Limit to first 50 for performance
            for ticker in all_tickers[:50]:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info

                    market_cap = info.get('marketCap', 0)
                    if market_cap >= criteria['market_cap_min']:
                        filtered.append(ticker)

                except Exception as e:
                    logger.warning(f"Failed to get info for {ticker}: {e}")
                    continue

            all_tickers = filtered
            logger.info(f"After market cap filter: {len(all_tickers)} tickers")

        # Limit results
        tickers = all_tickers[:30]
        logger.info(f"Returning {len(tickers)} candidate tickers")

    except Exception as e:
        logger.error(f"yfinance screening failed: {e}")
        # Fallback to curated list
        logger.info("Falling back to curated ticker list")
        tickers = get_fallback_ticker_list(criteria)

    return tickers


def screen_finnhub(criteria: dict, api_key: str) -> List[str]:
    """
    Screen stocks using Finnhub API.

    Args:
        criteria: Screening criteria dict
        api_key: Finnhub API key

    Returns: List of ticker symbols
    """
    try:
        import finnhub

        client = finnhub.Client(api_key=api_key)

        # Get US stock symbols
        symbols = client.stock_symbols('US')

        # Filter by criteria
        # This is a simplified implementation
        # Finnhub has more advanced screening capabilities

        tickers = []
        for symbol in symbols[:100]:  # Limit for performance
            ticker = symbol['symbol']

            # Basic filtering by type
            if symbol.get('type') == 'Common Stock':
                tickers.append(ticker)

        logger.info(f"Finnhub screening returned {len(tickers)} tickers")
        return tickers[:30]

    except Exception as e:
        logger.error(f"Finnhub screening failed: {e}")
        return get_fallback_ticker_list(criteria)


def get_fallback_ticker_list(criteria: dict) -> List[str]:
    """
    Curated fallback ticker list when APIs fail.

    Returns popular tickers by sector that are well-known and liquid.

    Args:
        criteria: Screening criteria (uses 'sectors' if present)

    Returns: List of ticker symbols
    """
    SECTOR_TICKERS = {
        "Technology": [
            "AAPL", "MSFT", "GOOGL", "NVDA", "META", "TSLA", "AMD", "INTC",
            "CRM", "ORCL", "ADBE", "CSCO", "AVGO", "QCOM", "TXN"
        ],
        "Information Technology": [  # Alias for Technology
            "AAPL", "MSFT", "NVDA", "AVGO", "CRM", "ORCL", "ADBE",
            "CSCO", "ACN", "AMD", "INTC", "IBM", "QCOM", "TXN"
        ],
        "Healthcare": [
            "JNJ", "UNH", "PFE", "ABBV", "TMO", "LLY", "MRK",
            "ABT", "DHR", "BMY", "AMGN", "CVS", "MDT", "GILD"
        ],
        "Health Care": [  # Alias for Healthcare
            "JNJ", "UNH", "LLY", "ABBV", "MRK", "TMO", "ABT",
            "DHR", "PFE", "BMY", "AMGN", "ISRG", "CVS", "CI"
        ],
        "Financials": [
            "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK",
            "SPGI", "AXP", "USB", "PNC", "TFC", "SCHW", "BK"
        ],
        "Financial Services": [  # Alias
            "BRK.B", "JPM", "V", "MA", "BAC", "WFC", "SPGI",
            "BLK", "C", "GS", "AXP", "MS", "USB", "PNC"
        ],
        "Energy": [
            "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX",
            "VLO", "OXY", "HES", "KMI", "WMB", "HAL", "DVN"
        ],
        "Consumer": [
            "AMZN", "WMT", "HD", "MCD", "NKE", "SBUX", "TGT",
            "LOW", "TJX", "COST", "PG", "KO", "PEP", "DIS"
        ],
        "Consumer Discretionary": [
            "AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "TGT",
            "LOW", "TJX", "BKNG", "CMG", "ORLY", "MAR", "GM"
        ],
        "Consumer Staples": [
            "WMT", "PG", "COST", "KO", "PEP", "PM", "MO",
            "CL", "MDLZ", "GIS", "KHC", "STZ", "SYY", "ADM"
        ],
        "Industrials": [
            "CAT", "UNP", "HON", "UPS", "RTX", "LMT", "BA",
            "GE", "MMM", "DE", "EMR", "ETN", "NSC", "CSX"
        ],
        "Communication Services": [
            "GOOGL", "META", "DIS", "NFLX", "CMCSA", "T", "VZ",
            "TMUS", "CHTR", "EA", "TTWO", "MTCH", "PARA", "OMC"
        ],
        "Utilities": [
            "NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE",
            "PEG", "XEL", "ED", "ES", "WEC", "DTE", "EIX"
        ],
        "Real Estate": [
            "PLD", "AMT", "CCI", "EQIX", "PSA", "WELL", "SPG",
            "O", "SBAC", "DLR", "CBRE", "AVB", "EQR", "VTR"
        ],
        "Materials": [
            "LIN", "APD", "SHW", "ECL", "DD", "NEM", "FCX",
            "NUE", "CTVA", "VMC", "MLM", "PPG", "ALB", "BALL"
        ],
    }

    sectors = criteria.get('sectors', ['Technology'])
    tickers = []

    for sector in sectors:
        sector_tickers = SECTOR_TICKERS.get(sector, [])
        tickers.extend(sector_tickers)

    # Remove duplicates while preserving order
    seen = set()
    unique_tickers = []
    for ticker in tickers:
        if ticker not in seen:
            seen.add(ticker)
            unique_tickers.append(ticker)

    logger.info(f"Fallback list returned {len(unique_tickers)} tickers for sectors: {sectors}")

    return unique_tickers[:20]


def discover_tickers_by_criteria(criteria: dict) -> List[str]:
    """
    Main entry point for ticker discovery.

    Uses vendor fallback pattern:
    1. Try yfinance screener (free, no API key)
    2. Fall back to finnhub if API key available
    3. Fall back to curated list

    Args:
        criteria: Screening criteria dict

    Returns: List of candidate ticker symbols
    """
    import os

    # Try yfinance first (free, no API key needed)
    try:
        tickers = screen_yfinance(criteria)
        if tickers and len(tickers) >= 5:
            logger.info(f"Successfully screened {len(tickers)} tickers using yfinance")
            return tickers
    except Exception as e:
        logger.warning(f"yfinance screening failed: {e}")

    # Try finnhub if API key available
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    if finnhub_key:
        try:
            tickers = screen_finnhub(criteria, finnhub_key)
            if tickers and len(tickers) >= 5:
                logger.info(f"Successfully screened {len(tickers)} tickers using Finnhub")
                return tickers
        except Exception as e:
            logger.warning(f"Finnhub screening failed: {e}")

    # Final fallback to curated list
    logger.info("Using curated fallback ticker list")
    return get_fallback_ticker_list(criteria)
