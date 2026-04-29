# =============================================================================
# AION Taxonomy Package
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
AION Taxonomy - Rule-based event classification and impact scoring for Indian equity markets.

This package provides:
    - Loading and validating YAML taxonomy files
    - Keyword-based event classification
    - Macro and sector signal computation
    - Confidence blending with model agreement

Main Classes:
    TaxonomyPipeline: Main entry point for processing headlines
    EventClassifier: Keyword-based event classification

Example:
    >>> from aion_taxonomy import TaxonomyPipeline
    >>> pipeline = TaxonomyPipeline(taxonomy_path="taxonomy_india_v2.yaml")
    >>> result = pipeline.process("RBI hikes repo rate by 25 bps")
    >>> print(result['macro_signal'])
"""

from .loader import load_taxonomy
from .classifier import EventClassifier
from .impact import get_macro_signal, get_sector_signal
from .confidence import compute_confidence
from .pipeline import TaxonomyPipeline

__version__ = "1.0.0"
__all__ = [
    "TaxonomyPipeline",
    "EventClassifier",
    "load_taxonomy",
    "get_macro_signal",
    "get_sector_signal",
    "compute_confidence",
]
