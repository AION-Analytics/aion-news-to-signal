# =============================================================================
# AION Taxonomy - Event Classifier
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
Event Classifier - Keyword-based event classification.

This module provides functionality to classify headlines into taxonomy events
using keyword matching.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class EventClassifier:
    """
    Keyword-based event classifier for financial news headlines.

    This classifier matches headlines against event keywords defined in the
    taxonomy and returns the best-matching event with a confidence score.

    Attributes:
        taxonomy: Loaded taxonomy dictionary.
        event_index: Pre-computed index of events for faster lookup.

    Example:
        >>> classifier = EventClassifier(taxonomy)
        >>> result = classifier.classify("RBI hikes repo rate by 25 bps")
        >>> print(result['event_id'])
        'macro_rbi_repo_hike'
    """

    def __init__(self, taxonomy: Dict[str, Any]) -> None:
        """
        Initialize the EventClassifier.

        Args:
            taxonomy: Loaded taxonomy dictionary from loader.load_taxonomy().
        """
        self.taxonomy = taxonomy
        self.event_index = self._build_event_index()
        logger.info(f"EventClassifier initialized with {len(self.event_index)} events")

    def _build_event_index(self) -> List[Dict[str, Any]]:
        """
        Build an index of all events for efficient lookup.

        Returns:
            List of event dictionaries with pre-processed keywords.
        """
        event_index = []

        for category in self.taxonomy.get('categories', []):
            for subcategory in category.get('subcategories', []):
                for event in subcategory.get('events', []):
                    # Pre-process keywords
                    keywords = self._preprocess_keywords(event.get('keywords', []))
                    
                    # Store event with category context
                    event_entry = {
                        'event_id': event['id'],
                        'event_name': event.get('name', ''),
                        'category_id': category['id'],
                        'subcategory_id': subcategory['id'],
                        'keywords': keywords,
                        'keyword_count': len(keywords),
                        'base_impact': event.get('base_impact', {}),
                        'default_impact': event.get('default_impact', 'normal'),
                        'market_weight': event.get('market_weight', 1.0),
                        'sector_impacts': event.get('sector_impacts', {}),
                        'contextual_modifiers': event.get('contextual_modifiers', []),
                        'raw_event': event,
                    }
                    event_index.append(event_entry)

        return event_index

    def _preprocess_keywords(self, keywords: List[str]) -> List[str]:
        """
        Preprocess keywords for matching.

        Args:
            keywords: List of keyword phrases.

        Returns:
            List of lowercased, normalized keywords.
        """
        processed = []
        for kw in keywords:
            # Lowercase and normalize whitespace
            normalized = ' '.join(kw.lower().split())
            if normalized:
                processed.append(normalized)
        return processed

    def _normalize_text(self, text: str) -> str:
        """
        Normalize input text for matching.

        Args:
            text: Input text string.

        Returns:
            Lowercased, normalized text.
        """
        # Lowercase
        text = text.lower()
        # Normalize whitespace
        text = ' '.join(text.split())
        # Remove extra punctuation but keep important ones
        text = re.sub(r'[^\w\s\-\+]', ' ', text)
        return text

    def classify(self, headline: str) -> Dict[str, Any]:
        """
        Classify a headline to the best-matching event.

        Args:
            headline: News headline text to classify.

        Returns:
            Dictionary containing:
                - event_id: Matched event ID (or None if no match)
                - event_name: Matched event name
                - category_id: Parent category ID
                - subcategory_id: Parent subcategory ID
                - match_score: Confidence score (0-1)
                - matched_keywords: List of keywords that matched
                - base_impact: Event's base impact values
                - default_impact: Default impact level (mild/normal/severe)
                - market_weight: Event's market weight
                - sector_impacts: Sector-specific impact multipliers
        """
        normalized_headline = self._normalize_text(headline)

        best_match = None
        best_score = 0.0
        best_matched_keywords = []

        for event in self.event_index:
            score, matched_keywords = self._compute_match_score(
                normalized_headline, event
            )

            if score > best_score:
                best_score = score
                best_match = event
                best_matched_keywords = matched_keywords

        # Build result
        if best_match and best_score > 0:
            result = {
                'event_id': best_match['event_id'],
                'event_name': best_match['event_name'],
                'category_id': best_match['category_id'],
                'subcategory_id': best_match['subcategory_id'],
                'match_score': best_score,
                'matched_keywords': best_matched_keywords,
                'base_impact': best_match['base_impact'],
                'default_impact': best_match['default_impact'],
                'market_weight': best_match['market_weight'],
                'sector_impacts': best_match['sector_impacts'],
                'contextual_modifiers': best_match['contextual_modifiers'],
            }
        else:
            # No match found
            result = {
                'event_id': None,
                'event_name': None,
                'category_id': None,
                'subcategory_id': None,
                'match_score': 0.0,
                'matched_keywords': [],
                'base_impact': {},
                'default_impact': 'normal',
                'market_weight': 1.0,
                'sector_impacts': {},
                'contextual_modifiers': [],
            }

        return result

    def match_keywords(self, headline: str, keywords: List[str]) -> Tuple[bool, List[str]]:
        """
        Match keywords against headline using case-insensitive substring matching.

        Args:
            headline: Input headline text.
            keywords: List of keyword phrases to match.

        Returns:
            Tuple of (any_match, matched_keywords):
                - any_match: True if at least one keyword matches
                - matched_keywords: List of keywords that matched
        """
        headline_lower = headline.lower()
        matched = []
        
        for kw in keywords:
            if kw.lower() in headline_lower:
                matched.append(kw)
        
        return len(matched) > 0, matched

    def _compute_match_score(
        self, normalized_headline: str, event: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """
        Compute match score between headline and event keywords.

        Uses case-insensitive substring matching for each keyword.

        Args:
            normalized_headline: Preprocessed headline text.
            event: Event dictionary with preprocessed keywords.

        Returns:
            Tuple of (match_score, matched_keywords).
            match_score is between 0 and 1.
        """
        matched_keywords = []
        
        # Match each keyword as substring (case-insensitive)
        for keyword in event['keywords']:
            if keyword in normalized_headline:
                matched_keywords.append(keyword)
        
        if not matched_keywords:
            return 0.0, []
        
        # Compute score based on coverage
        # More matched keywords = higher score
        keyword_ratio = len(matched_keywords) / event['keyword_count']
        
        # Length bonus: longer matched phrases boost score
        matched_length = sum(len(kw) for kw in matched_keywords)
        total_keyword_length = sum(len(kw) for kw in event['keywords'])
        length_ratio = matched_length / max(total_keyword_length, 1)
        
        # Combined score (weighted average)
        score = 0.6 * keyword_ratio + 0.4 * length_ratio
        
        # Bonus for matching multiple keywords
        if len(matched_keywords) >= 2:
            score = min(1.0, score * 1.1)
        if len(matched_keywords) >= 3:
            score = min(1.0, score * 1.1)
        
        return score, matched_keywords

    def classify_batch(self, headlines: List[str]) -> List[Dict[str, Any]]:
        """
        Classify multiple headlines in batch.

        Args:
            headlines: List of headline strings.

        Returns:
            List of classification results (same format as classify()).
        """
        return [self.classify(headline) for headline in headlines]
