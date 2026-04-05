#!/usr/bin/env python3
# =============================================================================
# AION Sentiment Analysis - Setup Script
# =============================================================================
# Copyright (c) 2026 AION Open Source Contributors
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
# 
# AION Open Source Project - Financial News Sentiment Analysis
# =============================================================================
"""
Setup script for AION Sentiment Analysis package.

Install with:
    pip install -e .

Or for development:
    pip install -e ".[dev]"
"""

from setuptools import setup, find_packages
from pathlib import Path
import re

# Get the long description from README
def read_readme() -> str:
    """Read README.md for long description."""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding='utf-8')
    return ""


def get_version() -> str:
    """Extract version from __init__.py."""
    init_path = Path(__file__).parent / "src" / "aion_sentiment" / "__init__.py"
    if init_path.exists():
        content = init_path.read_text(encoding='utf-8')
        match = re.search(r"__version__ = ['\"]([^'\"]+)['\"]", content)
        if match:
            return match.group(1)
    return "0.1.0"


# Package metadata
NAME = "aion-sentiment"
VERSION = get_version()
DESCRIPTION = "AION Unified Sentiment Model for Indian Financial News - Multi-task transformer (95 events, 32 sectors, macro signal)"
AUTHOR = "AION Open Source Contributors"
AUTHOR_EMAIL = "contributors@aion.opensource"
URL = "https://github.com/aion-open-source/aion-sentiment"
LICENSE = "Apache-2.0"
KEYWORDS = [
    "sentiment-analysis",
    "aion-transformer",
    "financial-nlp",
    "emotion-detection",
    "nlp",
    "machine-learning",
    "pytorch",
    "transformers",
    "aion",
]

# Core dependencies
INSTALL_REQUIRES = [
    "transformers>=4.30.0",
    "torch>=2.0.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "requests>=2.31.0",
]

# Development dependencies
DEV_REQUIRES = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "flake8>=6.1.0",
    "mypy>=1.5.0",
    "types-requests>=2.31.0",
]

# Documentation dependencies
DOC_REQUIRES = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=1.3.0",
    "sphinx-autodoc-typehints>=1.24.0",
]

# All optional dependencies
ALL_REQUIRES = DEV_REQUIRES + DOC_REQUIRES

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    keywords=KEYWORDS,
    
    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Include package data
    package_data={
        "aion_sentiment": [
            "py.typed",
            "lexicons/*.txt",
        ],
    },
    
    # Data files
    include_package_data=True,
    
    # Dependencies
    install_requires=INSTALL_REQUIRES,
    extras_require={
        "dev": DEV_REQUIRES,
        "docs": DOC_REQUIRES,
        "all": ALL_REQUIRES,
    },
    
    # Python version requirement
    python_requires=">=3.9",
    
    # Entry points (if any CLI commands)
    entry_points={
        "console_scripts": [
            # "aion-sentiment=aion_sentiment.cli:main",  # Future CLI
        ],
    },
    
    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Financial",
        "Topic :: Text Processing :: Linguistic",
        "Typing :: Typed",
    ],
    
    # Project URLs
    project_urls={
        "Documentation": "https://github.com/aion-open-source/aion-sentiment#readme",
        "Source": "https://github.com/aion-open-source/aion-sentiment",
        "Tracker": "https://github.com/aion-open-source/aion-sentiment/issues",
        "AION Project": "https://github.com/aion-open-source",
    },
)
