# Copyright 2026 AION Analytics
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
"""
AION VolWeight - VIX-based sentiment confidence adjustment.

This package provides utilities for adjusting sentiment confidence scores
based on market volatility regimes using the VIX (Volatility Index).

AION Open Source Ecosystem
"""

from .volweight import (
    VIXRegime,
    get_regime,
    get_multiplier,
    adjust_confidence,
    weight_confidence,
    VIXRegimeConfig,
)

__version__ = "0.1.0"
__author__ = "AION Analytics"
__all__ = [
    "VIXRegime",
    "get_regime",
    "get_multiplier",
    "adjust_confidence",
    "weight_confidence",
    "VIXRegimeConfig",
]
