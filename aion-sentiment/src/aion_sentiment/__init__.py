# =============================================================================
# AION Sentiment Analysis Package
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
AION Sentiment Analysis Package.

A comprehensive financial news sentiment analysis toolkit powered by transformer
models tuned on Indian market data and NRC emotion lexicon for detecting market
sentiment and emotional indicators.

Main Components:
    - SentimentAnalyzer: Transformer-based sentiment classification
    - EmotionAnalyzer: NRC lexicon-based emotion detection
    - AIONSentimentAnalyzer: Main API for DataFrame analysis

Example:
    >>> from aion_sentiment import AIONSentimentAnalyzer
    >>> import pandas as pd
    >>>
    >>> analyzer = AIONSentimentAnalyzer()
    >>> df = pd.DataFrame({
    ...     'headline': [
    ...         'Stock market reaches all-time high',
    ...         'Company files for bankruptcy'
    ...     ]
    ... })
    >>> results = analyzer.analyze(df, text_column='headline')
    >>> print(results)
"""

from .sentiment import SentimentAnalyzer
from .emotions import EmotionAnalyzer
from .utils import get_device, download_nrc_lexicon

import pandas as pd
import json
from typing import Optional


class AIONSentimentAnalyzer:
    """
    Main API for AION sentiment analysis on pandas DataFrames.

    This class provides a unified interface for analyzing financial news
    headlines and articles, combining sentiment classification with
    emotion detection.

    Attributes:
        sentiment_analyzer (SentimentAnalyzer): Transformer-based sentiment classifier
        emotion_analyzer (EmotionAnalyzer): NRC lexicon-based emotion detector

    Example:
        >>> analyzer = AIONSentimentAnalyzer()
        >>> df = pd.DataFrame({'headline': ['Market surges on positive earnings']})
        >>> results = analyzer.analyze(df)
        >>> print(results.columns.tolist())
        ['headline', 'sentiment_label', 'sentiment_confidence', 'emotions']
    """

    def __init__(
        self,
        model_name: str = "aion-analytics/aion-sentiment-in-v1",
        device: Optional[str] = None,
        lexicon_path: Optional[str] = None
    ) -> None:
        """
        Initialize the AION Sentiment Analyzer.

        Args:
            model_name: HuggingFace model name for sentiment analysis.
                Defaults to "aion-analytics/aion-sentiment-in-v1" (India-tuned).
            device: Device to run inference on ('cuda', 'mps', 'cpu').
                If None, auto-detects best available device.
            lexicon_path: Path to NRC lexicon file. If None, downloads
                automatically to data directory.
        """
        self.sentiment_analyzer = SentimentAnalyzer(
            model_name=model_name,
            device=device
        )
        self.emotion_analyzer = EmotionAnalyzer(lexicon_path=lexicon_path)
    
    def analyze(
        self,
        df: pd.DataFrame,
        text_column: str = 'headline'
    ) -> pd.DataFrame:
        """
        Analyze sentiment and emotions for texts in a DataFrame.
        
        Adds three new columns to the input DataFrame:
            - sentiment_label: 'positive', 'neutral', or 'negative'
            - sentiment_confidence: float between 0 and 1
            - emotions: JSON string with fear, greed, panic, optimism scores
        
        Args:
            df: pandas DataFrame containing text data.
            text_column: Name of the column containing text to analyze.
                Defaults to 'headline'.
        
        Returns:
            DataFrame with added sentiment and emotion columns.
        
        Raises:
            ValueError: If text_column is not found in DataFrame.
            TypeError: If df is not a pandas DataFrame.
        
        Example:
            >>> import pandas as pd
            >>> analyzer = AIONSentimentAnalyzer()
            >>> df = pd.DataFrame({
            ...     'headline': [
            ...         'Tech stocks rally on AI breakthrough',
            ...         'Oil prices crash amid demand concerns'
            ...     ]
            ... })
            >>> results = analyzer.analyze(df)
            >>> print(results['sentiment_label'].tolist())
            ['positive', 'negative']
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
        
        if text_column not in df.columns:
            raise ValueError(
                f"Column '{text_column}' not found in DataFrame. "
                f"Available columns: {df.columns.tolist()}"
            )
        
        # Create a copy to avoid modifying original
        result_df = df.copy()
        
        # Get texts to analyze
        texts = result_df[text_column].fillna('').astype(str).tolist()
        
        # Get sentiment predictions
        sentiment_results = self.sentiment_analyzer.predict(texts)
        
        # Extract labels and confidences
        labels = [result['label'] for result in sentiment_results]
        confidences = [result['confidence'] for result in sentiment_results]
        
        # Get emotion scores
        emotion_results = [
            self.emotion_analyzer.get_emotions(text) for text in texts
        ]
        emotion_jsons = [json.dumps(emotions) for emotions in emotion_results]
        
        # Add columns to DataFrame
        result_df['sentiment_label'] = labels
        result_df['sentiment_confidence'] = confidences
        result_df['emotions'] = emotion_jsons
        
        return result_df


__all__ = [
    'AIONSentimentAnalyzer',
    'SentimentAnalyzer',
    'EmotionAnalyzer',
    'get_device',
    'download_nrc_lexicon'
]

__version__ = '0.2.0'
__author__ = 'AION Open Source Contributors'
__license__ = 'Apache-2.0'
