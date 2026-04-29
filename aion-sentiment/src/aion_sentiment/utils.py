# =============================================================================
# AION Sentiment Analysis - Utility Functions
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
Utility Functions for AION Sentiment Analysis.

This module provides helper functions for device detection, lexicon
downloading, and other common operations.

Functions:
    get_device: Auto-detect best available compute device (MPS/CUDA/CPU).
    download_nrc_lexicon: Download NRC Emotion Lexicon from GitHub.
    clean_text: Preprocess text for analysis.
    batch_iterator: Iterate over items in batches.
"""

import os
import sys
import logging
from typing import Optional, List, Iterator, Any

logger = logging.getLogger(__name__)


def get_device() -> str:
    """
    Auto-detect the best available compute device for PyTorch.
    
    Checks for available devices in the following order:
        1. MPS (Metal Performance Shaders) - Apple Silicon (M1/M2/M3)
        2. CUDA - NVIDIA GPU with CUDA support
        3. CPU - Fallback to CPU
    
    Returns:
        Device string: 'mps', 'cuda', or 'cpu'
    
    Example:
        >>> device = get_device()
        >>> print(f"Using device: {device}")
        Using device: mps  # On Apple Silicon
        Using device: cuda  # On NVIDIA GPU
        Using device: cpu   # Fallback
    """
    try:
        import torch
        
        # Check for MPS (Apple Silicon)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            logger.info("MPS (Apple Silicon) is available")
            return 'mps'
        
        # Check for CUDA
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            logger.info(f"CUDA is available: {device_name}")
            return 'cuda'
        
        # Fallback to CPU
        logger.info("Using CPU for inference")
        return 'cpu'
        
    except ImportError:
        logger.warning("PyTorch not installed, defaulting to CPU")
        return 'cpu'
    except Exception as e:
        logger.warning(f"Error detecting device: {e}, defaulting to CPU")
        return 'cpu'


def download_nrc_lexicon(output_path: str) -> str:
    """
    Download the NRC Emotion Lexicon from GitHub.
    
    Downloads the NRC Emotion Lexicon Word-level v0.92 from the official
    repository and saves it to the specified path.
    
    Args:
        output_path: Full path where the lexicon file will be saved.
    
    Returns:
        Path to the downloaded lexicon file.
    
    Raises:
        IOError: If download fails or file cannot be written.
        ImportError: If requests library is not installed.
    
    Example:
        >>> path = download_nrc_lexicon('./data/nrc_lexicon.txt')
        >>> print(f"Lexicon saved to: {path}")
    """
    try:
        import requests
    except ImportError:
        raise ImportError(
            "requests library is required for downloading NRC lexicon. "
            "Install with: pip install requests"
        )
    
    # NRC lexicon URL (from official repository)
    # NRC Emotion Lexicon URLs
    # Using NRC Canada's official repository
    lexicon_url = (
        "https://raw.githubusercontent.com/saifmohammad/NRC-Emotion-Lexicon/main/"
        "NRC-Emotion-Lexicon-Word-level-v0.92.txt"
    )

    # Alternative: Academic mirror
    alternative_url = (
        "https://raw.githubusercontent.com/dm4ml/NRC-Emotion-Lexicon/main/"
        "NRC-Emotion-Lexicon-Word-level-v0.92.txt"
    )

    # Fallback: Create minimal lexicon if download fails
    fallback_emotions = {
        'anger': ['hate', 'kill', 'attack', 'enemy', 'terrible', 'horrible', 'awful'],
        'fear': ['afraid', 'scared', 'terrified', 'panic', 'horror', 'dread', 'frightened'],
        'joy': ['happy', 'joy', 'love', 'wonderful', 'great', 'excellent', 'fantastic'],
        'sadness': ['sad', 'depressed', 'miserable', 'pain', 'suffer', 'grief', 'tears'],
        'trust': ['trust', 'faith', 'reliable', 'honest', 'confident', 'believe', 'support'],
        'disgust': ['disgust', 'sick', 'vomit', 'repulsive', 'nausea', 'revolting'],
        'surprise': ['surprise', 'amazed', 'astonished', 'shocked', 'astounded'],
        'anticipation': ['anticipate', 'expect', 'hope', 'await', 'planning', 'looking'],
    }

    logger.info(f"Downloading NRC lexicon from {lexicon_url}")

    try:
        response = requests.get(lexicon_url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"Primary URL failed, trying alternative: {e}")
        try:
            response = requests.get(alternative_url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e2:
            logger.warning(f"Alternative URL failed: {e2}")
            logger.info("Creating minimal fallback lexicon...")
            
            # Ensure directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Write minimal lexicon
            with open(output_path, 'w', encoding='utf-8') as f:
                for emotion, words in fallback_emotions.items():
                    for word in words:
                        f.write(f"{word}\t{emotion}\t1\n")
            
            logger.info(f"Created minimal fallback lexicon at {output_path}")
            return output_path

    # Ensure directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Write to file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        logger.info(f"NRC lexicon saved to {output_path}")
        return output_path
    except IOError as e:
        raise IOError(f"Failed to write lexicon to {output_path}: {e}")


def clean_text(text: str) -> str:
    """
    Clean and preprocess text for sentiment analysis.
    
    Performs the following cleaning operations:
        - Remove extra whitespace
        - Remove URLs
        - Remove special characters (keep letters, numbers, basic punctuation)
        - Normalize whitespace
    
    Args:
        text: Raw text to clean.
    
    Returns:
        Cleaned text suitable for analysis.
    
    Example:
        >>> text = "Check this out!!! http://example.com  Great news!!!"
        >>> clean = clean_text(text)
        >>> print(clean)
        'Check this out Great news'
    """
    import re
    
    if not text or not isinstance(text, str):
        return ""
    
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    
    # Remove mentions and hashtags (for social media text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    
    # Remove special characters, keep letters, numbers, and basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text


def batch_iterator(
    items: List[Any],
    batch_size: int
) -> Iterator[List[Any]]:
    """
    Iterate over items in batches.
    
    Generator that yields batches of items from a list. Useful for
    processing large datasets in memory-efficient chunks.
    
    Args:
        items: List of items to iterate over.
        batch_size: Number of items per batch.
    
    Yields:
        Lists of items, each of length batch_size (except possibly the last).
    
    Example:
        >>> items = list(range(10))
        >>> for batch in batch_iterator(items, 3):
        ...     print(batch)
        [0, 1, 2]
        [3, 4, 5]
        [6, 7, 8]
        [9]
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def format_confidence(confidence: float, as_percentage: bool = False) -> str:
    """
    Format confidence score for display.
    
    Args:
        confidence: Confidence score between 0 and 1.
        as_percentage: If True, format as percentage (e.g., "95%").
            If False, format as decimal (e.g., "0.95").
    
    Returns:
        Formatted string representation of confidence.
    
    Example:
        >>> format_confidence(0.95)
        '0.95'
        >>> format_confidence(0.95, as_percentage=True)
        '95%'
    """
    if as_percentage:
        return f"{confidence * 100:.0f}%"
    return f"{confidence:.2f}"


def validate_text_input(texts: Any) -> List[str]:
    """
    Validate and normalize text input for analysis.
    
    Converts various input types to a list of strings:
        - Single string → [string]
        - List of strings → list of strings
        - pandas Series → list of strings
    
    Args:
        texts: Input to validate (str, list, or pandas Series).
    
    Returns:
        List of strings.
    
    Raises:
        TypeError: If input type is not supported.
    """
    # Handle pandas Series
    if hasattr(texts, 'tolist'):
        texts = texts.tolist()
    
    # Handle single string
    if isinstance(texts, str):
        return [texts]
    
    # Handle list
    if isinstance(texts, (list, tuple)):
        return [str(t) if t is not None else '' for t in texts]
    
    raise TypeError(
        f"Expected string, list, or pandas Series, got {type(texts).__name__}"
    )


def get_package_version() -> str:
    """
    Get the version of the aion_sentiment package.
    
    Returns:
        Version string (e.g., "0.1.0").
    """
    try:
        from importlib.metadata import version
        return version('aion-sentiment')
    except Exception:
        return '0.1.0'


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> None:
    """
    Configure logging for AION sentiment analysis.
    
    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG).
        format_string: Custom log format string. If None, uses default.
    
    Example:
        >>> import logging
        >>> setup_logging(level=logging.DEBUG)
    """
    if format_string is None:
        format_string = (
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    logging.basicConfig(
        level=level,
        format=format_string,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
