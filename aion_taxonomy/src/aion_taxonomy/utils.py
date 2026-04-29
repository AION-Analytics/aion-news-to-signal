# =============================================================================
# AION Taxonomy - Utilities
# =============================================================================
# Copyright (c) 2026 AION Contributors
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
"""
Utility functions for AION Taxonomy.

This module provides helper functions for date handling, text normalization,
and other common operations.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse a date string into a datetime object.

    Supports multiple formats:
        - YYYY-MM-DD
        - DD/MM/YYYY
        - DD-MM-YYYY
        - YYYY/MM/DD

    Args:
        date_str: Date string to parse.

    Returns:
        datetime object if parsing succeeds, None otherwise.
    """
    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
        '%d %b %Y',
        '%d %B %Y',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    logger.warning(f"Could not parse date: {date_str}")
    return None


def is_seasonal_event(
    event: Dict[str, Any],
    date: Optional[datetime] = None,
) -> bool:
    """
    Check if an event is seasonal (active only during certain periods).

    Args:
        event: Event dictionary from taxonomy.
        date: Date to check against. If None, uses current date.

    Returns:
        True if event is active, False otherwise.
    """
    if date is None:
        date = datetime.now()

    seasonal_activation = event.get('seasonal_activation', False)

    if not seasonal_activation:
        # Non-seasonal events are always active
        return True

    # TODO: Implement seasonal activation logic based on event configuration
    # For now, assume all seasonal events are active
    logger.debug(f"Seasonal event {event.get('id')} is active on {date}")
    return True


def normalize_ticker(ticker: str) -> str:
    """
    Normalize a ticker symbol for consistent lookup.

    Args:
        ticker: Raw ticker symbol.

    Returns:
        Normalized ticker symbol (uppercase, stripped).
    """
    return ticker.strip().upper()


def extract_tickers_from_headline(headline: str) -> List[str]:
    """
    Extract potential ticker symbols from a headline.

    Looks for patterns like:
        - Uppercase words (2-5 letters)
        - Known ticker patterns

    Args:
        headline: News headline text.

    Returns:
        List of potential ticker symbols.
    """
    # Pattern for uppercase words (potential tickers)
    pattern = r'\b([A-Z]{2,5})\b'
    matches = re.findall(pattern, headline)

    # Filter out common non-ticker words
    exclude_words = {'THE', 'AND', 'FOR', 'NOT', 'WITH', 'FROM', 'HAVE', 'BUT', 'ARE', 'WAS'}
    tickers = [m for m in matches if m not in exclude_words]

    return tickers


def compute_keyword_overlap(
    text: str,
    keywords: List[str],
) -> Tuple[int, List[str]]:
    """
    Compute keyword overlap between text and keyword list.

    Args:
        text: Text to search in.
        keywords: List of keywords to search for.

    Returns:
        Tuple of (match_count, matched_keywords).
    """
    text_lower = text.lower()
    matched = []

    for keyword in keywords:
        if keyword.lower() in text_lower:
            matched.append(keyword)

    return len(matched), matched


def format_signal(signal: float, decimals: int = 3) -> str:
    """
    Format a signal value for display.

    Args:
        signal: Signal value (-1 to 1).
        decimals: Number of decimal places.

    Returns:
        Formatted string with sign indicator.
    """
    if signal > 0:
        sign = '+'
    elif signal < 0:
        sign = '-'
    else:
        sign = ' '

    return f"{sign}{abs(signal):.{decimals}f}"


def get_signal_label(signal: float, threshold: float = 0.1) -> str:
    """
    Get a human-readable label for a signal value.

    Args:
        signal: Signal value (-1 to 1).
        threshold: Threshold for considering signal as positive/negative.

    Returns:
        Label string ('positive', 'neutral', or 'negative').
    """
    if signal > threshold:
        return 'positive'
    elif signal < -threshold:
        return 'negative'
    else:
        return 'neutral'
