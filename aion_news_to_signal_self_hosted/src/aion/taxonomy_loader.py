# =============================================================================
# AION Taxonomy - YAML Loader
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
Taxonomy YAML Loader.

This module provides functionality to load and validate the taxonomy YAML file.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

# Required top-level keys in the taxonomy YAML
REQUIRED_KEYS = ["metadata", "config", "sectors", "categories"]


class TaxonomyValidationError(Exception):
    """Raised when taxonomy validation fails."""
    pass


def load_taxonomy(yaml_path: str) -> Dict[str, Any]:
    """
    Load and validate the taxonomy YAML file.

    Args:
        yaml_path: Path to the taxonomy YAML file.

    Returns:
        Dictionary containing the validated taxonomy structure.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        TaxonomyValidationError: If required keys are missing.
        yaml.YAMLError: If the YAML is malformed.

    Example:
        >>> taxonomy = load_taxonomy("taxonomy_india_v2.yaml")
        >>> print(taxonomy['metadata']['version'])
    """
    yaml_path = Path(yaml_path)

    # Validate file existence
    if not yaml_path.exists():
        raise FileNotFoundError(f"Taxonomy file not found: {yaml_path}")

    logger.info(f"Loading taxonomy from: {yaml_path}")

    # Load YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        taxonomy = yaml.safe_load(f)

    # Validate structure
    _validate_taxonomy(taxonomy)

    logger.info(f"Taxonomy loaded successfully: {taxonomy['metadata']['version']}")
    logger.info(f"  Sectors: {len(taxonomy['sectors'])}")
    logger.info(f"  Categories: {len(taxonomy['categories'])}")

    return taxonomy


def _validate_taxonomy(taxonomy: Dict[str, Any]) -> None:
    """
    Validate the taxonomy structure.

    Args:
        taxonomy: Loaded taxonomy dictionary.

    Raises:
        TaxonomyValidationError: If required keys are missing or structure is invalid.
    """
    # Check required top-level keys
    missing_keys = [key for key in REQUIRED_KEYS if key not in taxonomy]
    if missing_keys:
        raise TaxonomyValidationError(
            f"Missing required top-level keys: {missing_keys}"
        )

    # Validate metadata
    _validate_metadata(taxonomy['metadata'])

    # Validate config
    _validate_config(taxonomy['config'])

    # Validate sectors
    _validate_sectors(taxonomy['sectors'])

    # Validate categories
    _validate_categories(taxonomy['categories'])

    logger.debug("Taxonomy validation passed")


def _validate_metadata(metadata: Dict[str, Any]) -> None:
    """Validate metadata section."""
    required = ["version", "market"]
    missing = [k for k in required if k not in metadata]
    if missing:
        raise TaxonomyValidationError(f"Metadata missing required keys: {missing}")


def _validate_config(config: Dict[str, Any]) -> None:
    """Validate config section."""
    required = ["impact_scale", "confidence_method"]
    missing = [k for k in required if k not in config]
    if missing:
        raise TaxonomyValidationError(f"Config missing required keys: {missing}")


def _validate_sectors(sectors: List[Dict[str, Any]]) -> None:
    """Validate sectors list."""
    if not sectors:
        raise TaxonomyValidationError("Sectors list is empty")

    for i, sector in enumerate(sectors):
        if 'id' not in sector:
            raise TaxonomyValidationError(f"Sector {i} missing 'id' field")
        if 'beta_default' not in sector:
            raise TaxonomyValidationError(f"Sector {sector.get('id', i)} missing 'beta_default'")


def _validate_categories(categories: List[Dict[str, Any]]) -> None:
    """Validate categories list."""
    if not categories:
        raise TaxonomyValidationError("Categories list is empty")

    event_count = 0
    for i, category in enumerate(categories):
        if 'id' not in category:
            raise TaxonomyValidationError(f"Category {i} missing 'id' field")
        if 'subcategories' not in category:
            raise TaxonomyValidationError(f"Category {category.get('id', i)} missing 'subcategories'")

        for j, subcat in enumerate(category['subcategories']):
            if 'id' not in subcat:
                raise TaxonomyValidationError(
                    f"Subcategory {j} in category {category['id']} missing 'id'"
                )
            if 'events' not in subcat:
                raise TaxonomyValidationError(
                    f"Subcategory {subcat.get('id', j)} missing 'events'"
                )

            for k, event in enumerate(subcat['events']):
                if 'id' not in event:
                    raise TaxonomyValidationError(
                        f"Event {k} in subcategory {subcat['id']} missing 'id'"
                    )
                if 'keywords' not in event:
                    raise TaxonomyValidationError(
                        f"Event {event.get('id', k)} missing 'keywords'"
                    )
                if 'base_impact' not in event:
                    raise TaxonomyValidationError(
                        f"Event {event.get('id', k)} missing 'base_impact'"
                    )

                event_count += 1

    logger.debug(f"Validated {event_count} events across {len(categories)} categories")


def get_sector_ids(taxonomy: Dict[str, Any]) -> List[str]:
    """
    Get list of all sector IDs from taxonomy.

    Args:
        taxonomy: Loaded taxonomy dictionary.

    Returns:
        List of sector ID strings.
    """
    return [sector['id'] for sector in taxonomy['sectors']]


def get_event_by_id(taxonomy: Dict[str, Any], event_id: str) -> Optional[Dict[str, Any]]:
    """
    Find an event by its ID.

    Args:
        taxonomy: Loaded taxonomy dictionary.
        event_id: Event ID to search for.

    Returns:
        Event dictionary if found, None otherwise.
    """
    for category in taxonomy['categories']:
        for subcategory in category.get('subcategories', []):
            for event in subcategory.get('events', []):
                if event['id'] == event_id:
                    return event
    return None
