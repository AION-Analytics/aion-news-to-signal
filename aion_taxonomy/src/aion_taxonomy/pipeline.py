# =============================================================================
# AION Taxonomy - Main Pipeline
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
Taxonomy Pipeline - Main entry point for headline processing.

This module provides the TaxonomyPipeline class that integrates all components
for end-to-end headline processing.
"""

import logging
from typing import Any, Dict, List, Optional

from .loader import load_taxonomy
from .classifier import EventClassifier
from .impact import get_macro_signal, get_sector_signal, compute_all_sector_signals
from .confidence import compute_confidence, compute_agreement_score

logger = logging.getLogger(__name__)


class TaxonomyPipeline:
    """
    Main pipeline for processing headlines through the taxonomy.

    This class integrates:
        - Taxonomy loading and validation
        - Event classification
        - Macro and sector signal computation
        - Confidence blending with optional model agreement

    Attributes:
        taxonomy: Loaded taxonomy dictionary.
        classifier: EventClassifier instance.
        sector_mapper: Optional sector mapper for ticker-to-sector lookup.

    Example:
        >>> pipeline = TaxonomyPipeline(taxonomy_path="taxonomy_india_v2.yaml")
        >>> result = pipeline.process("RBI hikes repo rate by 25 bps")
        >>> print(result['macro_signal'])
    """

    def __init__(
        self,
        taxonomy_path: str,
        sector_mapper: Optional[Any] = None,
    ) -> None:
        """
        Initialize the TaxonomyPipeline.

        Args:
            taxonomy_path: Path to the taxonomy YAML file.
            sector_mapper: Optional sector mapper instance (from aion-sectormap).
                          If None, sector lookup by ticker is not available.
        """
        logger.info(f"Initializing TaxonomyPipeline with taxonomy: {taxonomy_path}")

        # Load taxonomy
        self.taxonomy = load_taxonomy(taxonomy_path)

        # Initialize classifier
        self.classifier = EventClassifier(self.taxonomy)

        # Store sector mapper (optional)
        self.sector_mapper = sector_mapper

        # Get flip threshold from config
        flip_config = self.taxonomy.get('config', {}).get('flip_threshold', {})
        self.flip_threshold = flip_config.get('fallback_static', 0.35)

        # Get confidence weights from config
        self.confidence_weights = self.taxonomy.get('config', {}).get(
            'confidence_weights', None
        )

        logger.info("TaxonomyPipeline initialized")

    def process(
        self,
        headline: str,
        ticker: Optional[str] = None,
        date: Optional[str] = None,
        model_output: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a headline through the taxonomy pipeline.

        Args:
            headline: News headline text.
            ticker: Optional ticker symbol for sector lookup.
            date: Optional date string (for future seasonal activation).
            model_output: Optional model output dict with keys:
                         - 'label': 'positive', 'neutral', or 'negative'
                         - 'confidence': float (0-1)

        Returns:
            Dictionary containing:
                - event: Event classification details
                - macro_signal: Float (-1 to 1)
                - sector_signals: Dict mapping sector_id to signal
                - active_sector_signal: Signal for ticker's sector (if ticker provided)
                - confidence: Overall confidence (0-1)
                - confidence_components: Breakdown of confidence components

        Example:
            >>> result = pipeline.process(
            ...     "RBI unexpectedly hikes repo rate by 25 bps",
            ...     ticker="HDFCBANK",
            ...     model_output={'label': 'negative', 'confidence': 0.85}
            ... )
        """
        # Step 1: Classify event
        event = self.classifier.classify(headline)

        # Step 2: Compute macro signal
        macro_signal, impact_level = get_macro_signal(event, headline)

        # Step 3: Compute sector signals
        sector_signals = compute_all_sector_signals(
            macro_signal, event, flip_threshold=self.flip_threshold
        )

        # Step 4: Get active sector signal (if ticker provided)
        active_sector_signal = None
        active_sector_id = None
        if ticker and self.sector_mapper:
            try:
                sector_id = self.sector_mapper.get_sector(ticker)
                active_sector_id = sector_id
                if sector_id in sector_signals:
                    active_sector_signal = sector_signals[sector_id]['sector_signal']
            except Exception as e:
                logger.debug(f"Could not map ticker {ticker} to sector: {e}")

        # Step 5: Compute confidence
        taxonomy_match = event.get('match_score', 0.0)
        data_quality = 0.9  # Default, could be computed from data source

        model_probability = None
        agreement_score = None

        if model_output:
            model_probability = model_output.get('confidence', 0.5)
            model_label = model_output.get('label', 'neutral')

            # Compute agreement between taxonomy and model
            agreement_score = compute_agreement_score(
                macro_signal, model_label, model_probability
            )

        confidence = compute_confidence(
            taxonomy_match=taxonomy_match,
            data_quality=data_quality,
            model_probability=model_probability,
            agreement_score=agreement_score,
            weights=self.confidence_weights,
        )

        # Build result
        result = {
            'event': event,
            'impact_level': impact_level,
            'macro_signal': macro_signal,
            'sector_signals': sector_signals,
            'active_sector_id': active_sector_id,
            'active_sector_signal': active_sector_signal,
            'confidence': confidence,
            'confidence_components': {
                'taxonomy_match': taxonomy_match,
                'data_quality': data_quality,
                'model_probability': model_probability,
                'agreement_score': agreement_score,
            },
            'metadata': {
                'headline': headline,
                'ticker': ticker,
                'date': date,
                'taxonomy_version': self.taxonomy.get('metadata', {}).get('version', 'unknown'),
            },
        }

        logger.debug(
            f"Processed headline: macro_signal={macro_signal:.3f}, "
            f"confidence={confidence:.3f}, event={event.get('event_id')}"
        )

        return result

    def process_batch(
        self,
        headlines: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Process multiple headlines in batch.

        Args:
            headlines: List of dicts, each containing:
                      - 'headline': str (required)
                      - 'ticker': str (optional)
                      - 'date': str (optional)
                      - 'model_output': dict (optional)

        Returns:
            List of result dicts (same format as process()).
        """
        results = []
        for item in headlines:
            result = self.process(
                headline=item.get('headline', ''),
                ticker=item.get('ticker'),
                date=item.get('date'),
                model_output=item.get('model_output'),
            )
            results.append(result)
        return results

    def get_event_details(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific event by ID.

        Args:
            event_id: Event ID to look up.

        Returns:
            Event dictionary if found, None otherwise.
        """
        for category in self.taxonomy.get('categories', []):
            for subcategory in category.get('subcategories', []):
                for event in subcategory.get('events', []):
                    if event['id'] == event_id:
                        return event
        return None

    def list_events(self) -> List[Dict[str, str]]:
        """
        List all events in the taxonomy.

        Returns:
            List of dicts with 'id', 'name', 'category', 'subcategory'.
        """
        events = []
        for category in self.taxonomy.get('categories', []):
            for subcategory in category.get('subcategories', []):
                for event in subcategory.get('events', []):
                    events.append({
                        'id': event['id'],
                        'name': event.get('name', ''),
                        'category': category['id'],
                        'subcategory': subcategory['id'],
                    })
        return events
