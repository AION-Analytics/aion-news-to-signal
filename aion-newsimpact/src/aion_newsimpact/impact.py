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
Historical news impact analysis using semantic search with FAISS.

This module provides the NewsImpact class for analyzing the potential
market impact of news headlines by finding semantically similar historical
headlines and their observed price effects.

Example:
    >>> import pandas as pd
    >>> from aion_newsimpact import NewsImpact
    >>>
    >>> # Create sample historical data
    >>> df = pd.DataFrame({
    ...     'headline': [
    ...         'Company reports strong earnings beat',
    ...         'Tech giant announces new product line',
    ...         'Market volatility increases amid uncertainty',
    ...     ],
    ...     'date': ['2025-01-15', '2025-02-20', '2025-03-10'],
    ...     'returns_1d': [0.025, 0.018, -0.012],
    ... })
    >>>
    >>> # Initialize NewsImpact with historical data
    >>> impact_analyzer = NewsImpact(df, text_column='headline')
    >>>
    >>> # Query for similar historical headlines
    >>> results = impact_analyzer.query('Company exceeds earnings expectations')
    >>> print(results)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

# Optional imports with helpful error messages
try:
    import faiss
except ImportError as e:
    raise ImportError(
        "FAISS is required for aion-newsimpact. "
        "Install with: pip install faiss-cpu"
    ) from e

try:
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    raise ImportError(
        "sentence-transformers is required for aion-newsimpact. "
        "Install with: pip install sentence-transformers"
    ) from e


@dataclass
class ImpactQueryResult:
    """
    Result of a news impact query.

    Contains the top-K similar historical headlines along with their
    similarity scores and observed market impacts.

    Attributes:
        headlines: List of similar historical headlines
        dates: List of dates when headlines occurred
        similarity_scores: Cosine similarity scores (0.0 to 1.0)
        returns_1d: List of 1-day returns following each headline
        tickers: List of associated ticker symbols (if available)
        metadata: Additional metadata for each result (if available)

    Example:
        >>> result = impact_analyzer.query('earnings report')
        >>> print(f"Found {len(result.headlines)} similar headlines")
        >>> print(f"Average 1-day return: {result.average_return:.2%}")
    """

    headlines: list[str]
    dates: list[str]
    similarity_scores: list[float]
    returns_1d: list[float]
    tickers: list[str | None] = None
    metadata: list[dict[str, Any] | None] = None

    def __post_init__(self) -> None:
        """Validate that all lists have the same length."""
        lengths = [
            len(self.headlines),
            len(self.dates),
            len(self.similarity_scores),
            len(self.returns_1d),
        ]
        if self.tickers is not None:
            lengths.append(len(self.tickers))
        if self.metadata is not None:
            lengths.append(len(self.metadata))

        if len(set(lengths)) != 1:
            raise ValueError("All result lists must have the same length")

    @property
    def average_return(self) -> float:
        """Calculate the average 1-day return across similar headlines."""
        if not self.returns_1d:
            return 0.0
        return float(np.mean(self.returns_1d))

    @property
    def return_std(self) -> float:
        """Calculate the standard deviation of 1-day returns."""
        if len(self.returns_1d) < 2:
            return 0.0
        return float(np.std(self.returns_1d, ddof=1))

    @property
    def average_similarity(self) -> float:
        """Calculate the average similarity score."""
        if not self.similarity_scores:
            return 0.0
        return float(np.mean(self.similarity_scores))

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert query results to a pandas DataFrame.

        Returns:
            DataFrame with columns: headline, date, similarity, returns_1d,
            ticker (if available)
        """
        data = {
            "headline": self.headlines,
            "date": self.dates,
            "similarity": self.similarity_scores,
            "returns_1d": self.returns_1d,
        }

        if self.tickers is not None:
            data["ticker"] = self.tickers

        return pd.DataFrame(data)

    def __len__(self) -> int:
        """Return the number of results."""
        return len(self.headlines)

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"ImpactQueryResult(n_results={len(self)}, "
            f"avg_return={self.average_return:.2%}, "
            f"avg_similarity={self.average_similarity:.2f})"
        )


class NewsImpact:
    """
    Analyze historical news impact using semantic search.

    This class builds a FAISS index over historical news headlines using
    sentence embeddings, enabling fast semantic similarity search to find
    historically similar headlines and their observed market impacts.

    The workflow is:
    1. Initialize with historical DataFrame containing headlines and returns
    2. Build FAISS index (automatic in __init__)
    3. Query with new headlines to find similar historical cases
    4. Analyze impact statistics from similar historical headlines

    Attributes:
        historical_df: The input DataFrame with historical data
        text_column: Name of the column containing headline text
        model_name: Name of the sentence-transformers model used
        embedding_dim: Dimension of the embedding vectors
        index: The FAISS index for similarity search

    Example:
        >>> import pandas as pd
        >>> from aion_newsimpact import NewsImpact
        >>>
        >>> # Prepare historical data
        >>> df = pd.DataFrame({
        ...     'headline': ['Earnings beat expectations', 'Revenue misses estimates'],
        ...     'date': ['2025-01-15', '2025-02-20'],
        ...     'returns_1d': [0.025, -0.018],
        ...     'ticker': ['AAPL', 'GOOGL']
        ... })
        >>>
        >>> # Initialize and build index
        >>> analyzer = NewsImpact(df, text_column='headline')
        >>>
        >>> # Query for similar headlines
        >>> results = analyzer.query('Company exceeds profit forecasts')
        >>> print(results.to_dataframe())
    """

    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(
        self,
        historical_df: pd.DataFrame,
        text_column: str = "headline",
        model_name: str = DEFAULT_MODEL,
    ) -> None:
        """
        Initialize NewsImpact with historical data.

        Args:
            historical_df: DataFrame containing historical news data with
                columns for headlines, dates, and returns
            text_column: Name of the column containing headline text
            model_name: Name of the sentence-transformers model to use for
                embeddings. Default is 'sentence-transformers/all-MiniLM-L6-v2'

        Raises:
            ValueError: If required columns are missing or data is invalid
            ImportError: If required dependencies are not installed

        Example:
            >>> df = pd.DataFrame({
            ...     'headline': ['News headline 1', 'News headline 2'],
            ...     'date': ['2025-01-01', '2025-01-02'],
            ...     'returns_1d': [0.01, -0.02]
            ... })
            >>> analyzer = NewsImpact(df, text_column='headline')
        """
        if not isinstance(historical_df, pd.DataFrame):
            raise TypeError(
                f"historical_df must be a pandas DataFrame, "
                f"got {type(historical_df).__name__}"
            )

        if text_column not in historical_df.columns:
            raise ValueError(
                f"Text column '{text_column}' not found in DataFrame. "
                f"Available columns: {list(historical_df.columns)}"
            )

        # Validate required data
        self._validate_dataframe(historical_df, text_column)

        self.historical_df = historical_df.copy()
        self.text_column = text_column
        self.model_name = model_name

        # Initialize embedding model
        self._model = SentenceTransformer(model_name)
        self.embedding_dim = self._model.get_sentence_embedding_dimension()

        # Build FAISS index
        self.index: faiss.IndexFlatIP | None = None
        self._embeddings: np.ndarray | None = None
        self.build_index()

    def _validate_dataframe(
        self, df: pd.DataFrame, text_column: str
    ) -> None:
        """
        Validate the input DataFrame.

        Args:
            df: DataFrame to validate
            text_column: Name of the text column

        Raises:
            ValueError: If validation fails
        """
        # Check for empty DataFrame
        if df.empty:
            raise ValueError("historical_df cannot be empty")

        # Check text column has valid strings
        if not df[text_column].apply(lambda x: isinstance(x, str)).all():
            raise ValueError(
                f"All values in '{text_column}' must be strings"
            )

        # Check for empty strings
        if (df[text_column].str.len() == 0).any():
            raise ValueError(
                f"Column '{text_column}' contains empty strings"
            )

        # Check for returns_1d column if present
        if "returns_1d" in df.columns:
            if not pd.api.types.is_numeric_dtype(df["returns_1d"]):
                raise ValueError("returns_1d column must be numeric")

    def build_index(self) -> None:
        """
        Build the FAISS index from historical headlines.

        This method computes sentence embeddings for all headlines and
        builds a FAISS index for efficient similarity search. It is called
        automatically during initialization but can be called manually to
        rebuild the index after adding new data.

        The index uses inner product (cosine similarity after normalization)
        for fast approximate nearest neighbor search.

        Example:
            >>> analyzer = NewsImpact(df, text_column='headline')
            >>> # Index is built automatically
            >>> # Rebuild after adding new data
            >>> analyzer.build_index()
        """
        # Extract headlines
        headlines = self.historical_df[self.text_column].tolist()

        # Compute embeddings
        self._embeddings = self._model.encode(
            headlines,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,  # For cosine similarity
        )

        # Build FAISS index (Inner Product = cosine similarity for normalized vectors)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(self._embeddings.astype("float32"))

    def query(
        self,
        new_headline: str,
        top_k: int = 5,
    ) -> ImpactQueryResult:
        """
        Find similar historical headlines and their impacts.

        Searches the historical index for headlines semantically similar
        to the query headline and returns their details along with observed
        market impacts.

        Args:
            new_headline: The headline to search for similar historical cases
            top_k: Number of similar headlines to return (default: 5)

        Returns:
            ImpactQueryResult containing similar headlines, dates, similarity
            scores, and observed returns

        Raises:
            ValueError: If new_headline is empty or top_k is invalid
            RuntimeError: If the index has not been built

        Example:
            >>> analyzer = NewsImpact(df, text_column='headline')
            >>> results = analyzer.query('Company reports strong earnings')
            >>> print(f"Found {len(results)} similar headlines")
            >>> print(f"Average 1-day return: {results.average_return:.2%}")
            >>> print(results.to_dataframe())
        """
        if not isinstance(new_headline, str) or not new_headline.strip():
            raise ValueError("new_headline must be a non-empty string")

        if not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer")

        if self.index is None or self._embeddings is None:
            raise RuntimeError(
                "Index not built. Call build_index() first."
            )

        # Limit top_k to available data
        top_k = min(top_k, len(self.historical_df))

        # Encode query
        query_embedding = self._model.encode(
            [new_headline.strip()],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        # Search index
        similarities, indices = self.index.search(query_embedding, top_k)

        # Extract results
        result_indices = indices[0].tolist()
        similarity_scores = similarities[0].tolist()

        # Get data from DataFrame
        df = self.historical_df.iloc[result_indices]

        headlines = df[self.text_column].tolist()
        dates = (
            df["date"].tolist()
            if "date" in df.columns
            else ["N/A"] * len(result_indices)
        )
        returns = (
            df["returns_1d"].tolist()
            if "returns_1d" in df.columns
            else [0.0] * len(result_indices)
        )
        tickers = (
            df["ticker"].tolist()
            if "ticker" in df.columns
            else [None] * len(result_indices)
        )

        # Build metadata if additional columns exist
        metadata = None
        extra_cols = [
            col
            for col in df.columns
            if col not in [self.text_column, "date", "returns_1d", "ticker"]
        ]
        if extra_cols:
            metadata = df[extra_cols].to_dict("records")

        return ImpactQueryResult(
            headlines=headlines,
            dates=dates,
            similarity_scores=similarity_scores,
            returns_1d=returns,
            tickers=tickers,
            metadata=metadata,
        )

    def get_impact_stats(self) -> dict[str, Any]:
        """
        Get aggregate impact statistics from historical data.

        Returns summary statistics about the historical impact of news
        headlines in the index, including average returns, volatility,
        and distribution by sentiment regime.

        Returns:
            Dictionary containing:
                - total_headlines: Total number of headlines in index
                - avg_return_1d: Average 1-day return across all headlines
                - std_return_1d: Standard deviation of 1-day returns
                - positive_impact_pct: Percentage of headlines with positive impact
                - negative_impact_pct: Percentage of headlines with negative impact
                - neutral_impact_pct: Percentage of headlines with neutral impact
                - min_return: Minimum 1-day return
                - max_return: Maximum 1-day return
                - date_range: Tuple of (min_date, max_date) if dates available

        Raises:
            ValueError: If returns_1d column is not available

        Example:
            >>> analyzer = NewsImpact(df, text_column='headline')
            >>> stats = analyzer.get_impact_stats()
            >>> print(f"Total headlines: {stats['total_headlines']}")
            >>> print(f"Average impact: {stats['avg_return_1d']:.2%}")
        """
        if "returns_1d" not in self.historical_df.columns:
            raise ValueError(
                "returns_1d column not available. Cannot compute impact statistics."
            )

        returns = self.historical_df["returns_1d"].dropna()

        stats: dict[str, Any] = {
            "total_headlines": len(self.historical_df),
        }

        if len(returns) > 0:
            stats.update(
                {
                    "avg_return_1d": float(returns.mean()),
                    "std_return_1d": float(returns.std()),
                    "min_return": float(returns.min()),
                    "max_return": float(returns.max()),
                    "positive_impact_pct": float((returns > 0).mean() * 100),
                    "negative_impact_pct": float((returns < 0).mean() * 100),
                    "neutral_impact_pct": float((returns == 0).mean() * 100),
                }
            )
        else:
            stats.update(
                {
                    "avg_return_1d": 0.0,
                    "std_return_1d": 0.0,
                    "min_return": 0.0,
                    "max_return": 0.0,
                    "positive_impact_pct": 0.0,
                    "negative_impact_pct": 0.0,
                    "neutral_impact_pct": 0.0,
                }
            )

        # Add date range if available
        if "date" in self.historical_df.columns:
            dates = pd.to_datetime(self.historical_df["date"], errors="coerce")
            valid_dates = dates.dropna()
            if len(valid_dates) > 0:
                stats["date_range"] = (
                    str(valid_dates.min().date()),
                    str(valid_dates.max().date()),
                )

        return stats

    def add_headlines(
        self,
        new_df: pd.DataFrame,
        rebuild_index: bool = True,
    ) -> None:
        """
        Add new headlines to the historical data.

        Args:
            new_df: DataFrame with new headlines to add (same schema as original)
            rebuild_index: Whether to rebuild the FAISS index immediately.
                If False, call build_index() manually after adding all data.

        Raises:
            ValueError: If new_df doesn't have required columns

        Example:
            >>> new_data = pd.DataFrame({
            ...     'headline': ['New headline'],
            ...     'date': ['2025-12-01'],
            ...     'returns_1d': [0.015]
            ... })
            >>> analyzer.add_headlines(new_data)
        """
        if self.text_column not in new_df.columns:
            raise ValueError(
                f"New DataFrame must contain '{self.text_column}' column"
            )

        self.historical_df = pd.concat(
            [self.historical_df, new_df], ignore_index=True
        )

        if rebuild_index:
            self.build_index()

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get the embedding vector for a given text.

        Args:
            text: The text to embed

        Returns:
            Numpy array of embedding vectors
        """
        return self._model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"NewsImpact(n_headlines={len(self.historical_df)}, "
            f"model={self.model_name.split('/')[-1]})"
        )
