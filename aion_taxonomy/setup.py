# =============================================================================
# AION Taxonomy - Setup Script
# =============================================================================
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aion-taxonomy",
    version="1.0.0",
    author="AION Contributors",
    author_email="aion@opensource.example.com",
    description="Rule-based event classification and impact scoring for Indian equity markets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aion-open-source/aion_taxonomy",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "Typing :: Typed",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "mypy>=1.0",
        ],
        "sectormap": [
            "aion-sectormap>=1.0",
        ],
        "sentiment": [
            "aion-sentiment-in>=2.0",
        ],
    },
    include_package_data=True,
    package_data={
        "aion_taxonomy": ["data/*.yaml", "data/*.json"],
    },
    entry_points={
        "console_scripts": [
            "aion-taxonomy=aion_taxonomy.pipeline:main",
        ],
    },
)
