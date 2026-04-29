#!/usr/bin/env python3
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
Setup script for AION NewsImpact package.

AION NewsImpact - Historical news impact analysis using semantic search
Part of the AION Open Source Ecosystem
"""

from setuptools import setup, find_packages

# Read the long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Package metadata
NAME = "aion-newsimpact"
VERSION = "0.1.0"
DESCRIPTION = "Historical news impact analysis using semantic search for the AION ecosystem"
AUTHOR = "AION Analytics"
AUTHOR_EMAIL = "opensource@aion-analytics.org"
URL = "https://github.com/aion-analytics/aion-newsimpact"
LICENSE = "Apache-2.0"
CLASSIFIERS = [
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
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Office/Business :: Financial :: Investment",
    "Typing :: Typed",
]
KEYWORDS = [
    "news",
    "impact",
    "sentiment",
    "faiss",
    "semantic-search",
    "finance",
    "analytics",
    "aion",
    "nlp",
    "embeddings",
]

# Dependencies
INSTALL_REQUIRES = [
    "sentence-transformers>=2.2.0",
    "faiss-cpu>=1.7.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
]

EXTRAS_REQUIRE = {
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "mypy>=1.0.0",
        "black>=23.0.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "jupyter>=1.0.0",
        "ipykernel>=6.0.0",
    ],
    "docs": [
        "sphinx>=6.0.0",
        "sphinx-rtd-theme>=1.2.0",
        "sphinx-autodoc-typehints>=1.23.0",
    ],
    "gpu": [
        "faiss-gpu>=1.7.0",
    ],
}

# Package configuration
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "aion_newsimpact": ["py.typed"],
    },
    python_requires=">=3.9",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    include_package_data=True,
    zip_safe=False,
)
