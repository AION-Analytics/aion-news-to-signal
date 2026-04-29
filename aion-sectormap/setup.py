#!/usr/bin/env python3
# =============================================================================
# AION Open-Source Project: AION SectorMap
# File: setup.py
# Description: Package installation configuration
# License: Apache License, Version 2.0
#
# Copyright 2026 AION Contributors
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
# AION Attribution: This file is part of the AION open-source ecosystem.
# Please visit https://github.com/aion for more information.
# =============================================================================
"""
Setup script for AION SectorMap package.

This script configures the installation of the aion-sectormap package,
which provides NSE ticker to sector/industry mapping functionality.

Usage:
    pip install .
    pip install -e .  # Development mode
    python setup.py install
    python setup.py sdist bdist_wheel
"""

import os
import re
from pathlib import Path

from setuptools import find_packages, setup

# Package metadata
PACKAGE_NAME = "aion-sectormap"
PACKAGE_DIR = "aion_sectormap"
DESCRIPTION = "NSE Ticker to Sector/Industry Mapping for AION"
AUTHOR = "AION Contributors"
AUTHOR_EMAIL = "aion-contributors@github.com"
URL = "https://github.com/aion/aion-sectormap"
LICENSE = "Apache-2.0"
KEYWORDS = [
    "nse",
    "sector",
    "industry",
    "mapping",
    "finance",
    "india",
    "stocks",
    "aion",
]

# Python version requirements
PYTHON_REQUIRES = ">=3.9"


def get_version() -> str:
    """
    Extract version from __init__.py.

    Returns:
        Version string.

    Raises:
        RuntimeError: If version not found.
    """
    init_file = Path(__file__).parent / "src" / PACKAGE_DIR / "__init__.py"
    content = init_file.read_text(encoding="utf-8")

    version_match = re.search(
        r'^__version__\s*=\s*["\']([^"\']+)["\']',
        content,
        re.MULTILINE,
    )

    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string")


def get_long_description() -> str:
    """
    Read long description from README.md.

    Returns:
        Long description text.
    """
    readme_file = Path(__file__).parent / "README.md"

    if readme_file.exists():
        return readme_file.read_text(encoding="utf-8")

    return DESCRIPTION


def get_requirements() -> list[str]:
    """
    Read runtime requirements from requirements.txt.

    Returns:
        List of requirement strings.
    """
    requirements_file = Path(__file__).parent / "requirements.txt"

    if requirements_file.exists():
        content = requirements_file.read_text(encoding="utf-8")
        return [
            line.strip()
            for line in content.splitlines()
            if line.strip() and not line.startswith("#")
        ]

    # Default requirements
    return [
        "pandas>=2.0.0",
    ]


def get_dev_requirements() -> list[str]:
    """
    Get development requirements.

    Returns:
        List of development requirement strings.
    """
    return [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "mypy>=1.0.0",
        "ruff>=0.1.0",
        "build>=1.0.0",
        "twine>=4.0.0",
    ]


def get_package_data() -> dict[str, list[str]]:
    """
    Specify package data files to include.

    Returns:
        Dictionary mapping package to data files.
    """
    return {
        PACKAGE_DIR: [
            "data/*.json",
            "py.typed",
        ],
    }


# Setup configuration
setup(
    # Basic information
    name=PACKAGE_NAME,
    version=get_version(),
    description=DESCRIPTION,
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,

    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data=get_package_data(),

    # Requirements
    python_requires=PYTHON_REQUIRES,
    install_requires=get_requirements(),
    extras_require={
        "dev": get_dev_requirements(),
        "requests": ["requests>=2.31.0"],
    },

    # Entry points
    entry_points={
        "console_scripts": [
            "aion-sectormap-update=aion_sectormap.scripts.update_map:main",
        ],
    },

    # Classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],

    # Keywords
    keywords=KEYWORDS,

    # Include data files
    include_package_data=True,
    zip_safe=False,

    # Project URLs
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Source": URL,
        "Documentation": f"{URL}#readme",
        "AION": "https://github.com/aion",
    },
)
