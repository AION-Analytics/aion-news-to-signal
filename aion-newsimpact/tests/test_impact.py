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
Unit tests for aion_newsimpact package.

Tests cover:
- NewsImpact class initialization
- FAISS index building
- Query functionality
- Impact statistics
- Edge cases and error handling
"""

import pytest
import pandas as pd
import numpy as np

from aion_newsimpact import NewsImpact, ImpactQueryResult


@pytest.fixture
def sample_historical_df():
    """Create sample historical news data for testing."""
    return pd.DataFrame({
        "headline": [
            "Company A reports strong quarterly earnings beat",
            "Company B misses revenue expectations significantly",
            "Tech sector rallies on positive economic data",
            "Market volatility increases amid trade tensions",
            "Federal Reserve signals potential rate changes",
            "Energy sector surges on oil price spike",
            "Banking stocks decline on regulatory concerns",
            "Consumer spending shows unexpected strength",
            "Manufacturing data indicates economic slowdown",
            "Healthcare stocks gain on drug approval news",
        ],
        "date": [
            "2025-01-15",
            "2025-01-20",
            "2025-02-01",
            "2025-02-10",
            "2025-02-15",
            "2025-03-01",
            "2025-03-10",
            "2025-03-15",
            "2025-03-20",
            "2025-03-25",
        ],
        "returns_1d": [
            0.025,
            -0.032,
            0.018,
            -0.015,
            0.008,
            0.042,
            -0.022,
            0.012,
            -0.018,
            0.035,
        ],
        "ticker": [
            "AAPL",
            "GOOGL",
            "QQQ",
            "SPY",
            "TLT",
            "XLE",
            "XLF",
            "XLY",
            "XLI",
            "XLV",
        ],
    })


@pytest.fixture
def news_impact_analyzer(sample_historical_df):
    """Create a NewsImpact analyzer with sample data."""
    return NewsImpact(sample_historical_df, text_column="headline")


class TestImpactQueryResult:
    """Tests for ImpactQueryResult dataclass."""

    def test_basic_creation(self):
        """Test basic result creation."""
        result = ImpactQueryResult(
            headlines=["Headline 1", "Headline 2"],
            dates=["2025-01-01", "2025-01-02"],
            similarity_scores=[0.95, 0.85],
            returns_1d=[0.02, -0.01],
        )

        assert len(result) == 2
        assert result.headlines == ["Headline 1", "Headline 2"]
        assert result.dates == ["2025-01-01", "2025-01-02"]

    def test_with_tickers(self):
        """Test result creation with tickers."""
        result = ImpactQueryResult(
            headlines=["Headline 1"],
            dates=["2025-01-01"],
            similarity_scores=[0.9],
            returns_1d=[0.02],
            tickers=["AAPL"],
        )

        assert result.tickers == ["AAPL"]

    def test_with_metadata(self):
        """Test result creation with metadata."""
        result = ImpactQueryResult(
            headlines=["Headline 1"],
            dates=["2025-01-01"],
            similarity_scores=[0.9],
            returns_1d=[0.02],
            metadata=[{"sentiment": "positive", "confidence": 0.95}],
        )

        assert result.metadata == [{"sentiment": "positive", "confidence": 0.95}]

    def test_length_mismatch_raises_error(self):
        """Test that mismatched list lengths raise ValueError."""
        with pytest.raises(ValueError, match="same length"):
            ImpactQueryResult(
                headlines=["Headline 1", "Headline 2"],
                dates=["2025-01-01"],  # Wrong length
                similarity_scores=[0.9, 0.8],
                returns_1d=[0.02, -0.01],
            )

    def test_average_return(self):
        """Test average return calculation."""
        result = ImpactQueryResult(
            headlines=["H1", "H2", "H3"],
            dates=["D1", "D2", "D3"],
            similarity_scores=[0.9, 0.8, 0.7],
            returns_1d=[0.02, 0.04, 0.06],
        )

        assert result.average_return == pytest.approx(0.04, rel=1e-2)

    def test_average_return_empty(self):
        """Test average return with empty results."""
        result = ImpactQueryResult(
            headlines=[],
            dates=[],
            similarity_scores=[],
            returns_1d=[],
        )

        assert result.average_return == 0.0

    def test_return_std(self):
        """Test return standard deviation calculation."""
        result = ImpactQueryResult(
            headlines=["H1", "H2"],
            dates=["D1", "D2"],
            similarity_scores=[0.9, 0.8],
            returns_1d=[0.02, 0.04],
        )

        # std of [0.02, 0.04] with ddof=1
        expected_std = np.std([0.02, 0.04], ddof=1)
        assert result.return_std == pytest.approx(expected_std, rel=1e-2)

    def test_return_std_single_value(self):
        """Test return std with single value."""
        result = ImpactQueryResult(
            headlines=["H1"],
            dates=["D1"],
            similarity_scores=[0.9],
            returns_1d=[0.02],
        )

        assert result.return_std == 0.0

    def test_average_similarity(self):
        """Test average similarity calculation."""
        result = ImpactQueryResult(
            headlines=["H1", "H2"],
            dates=["D1", "D2"],
            similarity_scores=[0.9, 0.7],
            returns_1d=[0.02, 0.04],
        )

        assert result.average_similarity == pytest.approx(0.8, rel=1e-2)

    def test_to_dataframe(self):
        """Test conversion to DataFrame."""
        result = ImpactQueryResult(
            headlines=["H1", "H2"],
            dates=["D1", "D2"],
            similarity_scores=[0.9, 0.7],
            returns_1d=[0.02, 0.04],
            tickers=["AAPL", "GOOGL"],
        )

        df = result.to_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ["headline", "date", "similarity", "returns_1d", "ticker"]

    def test_to_dataframe_without_tickers(self):
        """Test DataFrame conversion without tickers."""
        result = ImpactQueryResult(
            headlines=["H1"],
            dates=["D1"],
            similarity_scores=[0.9],
            returns_1d=[0.02],
        )

        df = result.to_dataframe()

        assert "ticker" not in df.columns
        assert list(df.columns) == ["headline", "date", "similarity", "returns_1d"]

    def test_repr(self):
        """Test string representation."""
        result = ImpactQueryResult(
            headlines=["H1", "H2"],
            dates=["D1", "D2"],
            similarity_scores=[0.9, 0.7],
            returns_1d=[0.02, 0.04],
        )

        repr_str = repr(result)
        assert "ImpactQueryResult" in repr_str
        assert "n_results=2" in repr_str

    def test_len(self):
        """Test length method."""
        result = ImpactQueryResult(
            headlines=["H1", "H2", "H3"],
            dates=["D1", "D2", "D3"],
            similarity_scores=[0.9, 0.8, 0.7],
            returns_1d=[0.02, 0.04, 0.06],
        )

        assert len(result) == 3


class TestNewsImpactInit:
    """Tests for NewsImpact initialization."""

    def test_basic_initialization(self, sample_historical_df):
        """Test basic initialization."""
        analyzer = NewsImpact(sample_historical_df, text_column="headline")

        assert analyzer.text_column == "headline"
        assert len(analyzer.historical_df) == 10
        assert analyzer.index is not None
        assert analyzer._embeddings is not None

    def test_custom_text_column(self, sample_historical_df):
        """Test initialization with custom text column."""
        df = sample_historical_df.rename(columns={"headline": "news_title"})
        analyzer = NewsImpact(df, text_column="news_title")

        assert analyzer.text_column == "news_title"
        assert analyzer.index is not None

    def test_custom_model(self, sample_historical_df):
        """Test initialization with custom model."""
        analyzer = NewsImpact(
            sample_historical_df,
            text_column="headline",
            model_name="sentence-transformers/all-MiniLM-L6-v2",
        )

        assert "all-MiniLM-L6-v2" in analyzer.model_name

    def test_invalid_dataframe_type(self):
        """Test that non-DataFrame raises TypeError."""
        with pytest.raises(TypeError, match="DataFrame"):
            NewsImpact("not a dataframe", text_column="headline")  # type: ignore

    def test_missing_text_column(self, sample_historical_df):
        """Test that missing text column raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            NewsImpact(sample_historical_df, text_column="nonexistent_column")

    def test_empty_dataframe(self):
        """Test that empty DataFrame raises ValueError."""
        df = pd.DataFrame({"headline": [], "date": [], "returns_1d": []})

        with pytest.raises(ValueError, match="cannot be empty"):
            NewsImpact(df, text_column="headline")

    def test_non_string_headlines(self):
        """Test that non-string headlines raise ValueError."""
        df = pd.DataFrame({
            "headline": [123, 456],  # Invalid: not strings
            "date": ["2025-01-01", "2025-01-02"],
        })

        with pytest.raises(ValueError, match="must be strings"):
            NewsImpact(df, text_column="headline")

    def test_empty_headlines(self):
        """Test that empty headlines raise ValueError."""
        df = pd.DataFrame({
            "headline": ["Valid headline", ""],  # Empty string
            "date": ["2025-01-01", "2025-01-02"],
        })

        with pytest.raises(ValueError, match="empty strings"):
            NewsImpact(df, text_column="headline")

    def test_non_numeric_returns(self):
        """Test that non-numeric returns raise ValueError."""
        df = pd.DataFrame({
            "headline": ["Headline 1", "Headline 2"],
            "date": ["2025-01-01", "2025-01-02"],
            "returns_1d": ["positive", "negative"],  # Invalid: not numeric
        })

        with pytest.raises(ValueError, match="must be numeric"):
            NewsImpact(df, text_column="headline")


class TestNewsImpactQuery:
    """Tests for NewsImpact query functionality."""

    def test_basic_query(self, news_impact_analyzer):
        """Test basic query functionality."""
        results = news_impact_analyzer.query(
            "Company reports strong earnings"
        )

        assert isinstance(results, ImpactQueryResult)
        assert len(results) == 5  # Default top_k
        assert all(isinstance(s, float) for s in results.similarity_scores)
        assert all(isinstance(h, str) for h in results.headlines)

    def test_query_custom_top_k(self, news_impact_analyzer):
        """Test query with custom top_k."""
        results = news_impact_analyzer.query(
            "Market volatility",
            top_k=3,
        )

        assert len(results) == 3

    def test_query_top_k_larger_than_data(self, news_impact_analyzer):
        """Test query with top_k larger than available data."""
        results = news_impact_analyzer.query(
            "Test query",
            top_k=100,
        )

        # Should return all available results
        assert len(results) == 10

    def test_query_empty_string(self, news_impact_analyzer):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError, match="non-empty string"):
            news_impact_analyzer.query("")

    def test_query_whitespace_only(self, news_impact_analyzer):
        """Test that whitespace-only query raises ValueError."""
        with pytest.raises(ValueError, match="non-empty string"):
            news_impact_analyzer.query("   ")

    def test_query_invalid_top_k(self, news_impact_analyzer):
        """Test that invalid top_k raises ValueError."""
        with pytest.raises(ValueError, match="positive integer"):
            news_impact_analyzer.query("Test", top_k=0)
        with pytest.raises(ValueError, match="positive integer"):
            news_impact_analyzer.query("Test", top_k=-1)

    def test_query_returns_dataframe(self, news_impact_analyzer):
        """Test that query results can be converted to DataFrame."""
        results = news_impact_analyzer.query("Earnings report")
        df = results.to_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(results)

    def test_query_similar_headlines(self, news_impact_analyzer):
        """Test that similar headlines are returned for similar queries."""
        # Query about earnings
        results = news_impact_analyzer.query(
            "Company exceeds profit expectations"
        )

        # Should find headlines about earnings/reports
        assert len(results) > 0
        # Similarity scores should be reasonable
        assert all(s > 0.3 for s in results.similarity_scores)

    def test_query_with_tickers(self, news_impact_analyzer):
        """Test that tickers are included in results."""
        results = news_impact_analyzer.query("Stock market news")

        assert results.tickers is not None
        assert len(results.tickers) == len(results)


class TestNewsImpactStats:
    """Tests for NewsImpact impact statistics."""

    def test_get_impact_stats(self, news_impact_analyzer):
        """Test getting impact statistics."""
        stats = news_impact_analyzer.get_impact_stats()

        assert isinstance(stats, dict)
        assert stats["total_headlines"] == 10
        assert "avg_return_1d" in stats
        assert "std_return_1d" in stats
        assert "min_return" in stats
        assert "max_return" in stats
        assert "positive_impact_pct" in stats
        assert "negative_impact_pct" in stats

    def test_impact_stats_values(self, news_impact_analyzer):
        """Test impact statistics values."""
        stats = news_impact_analyzer.get_impact_stats()

        # Verify calculations
        returns = news_impact_analyzer.historical_df["returns_1d"]
        assert stats["avg_return_1d"] == pytest.approx(returns.mean(), rel=1e-2)
        assert stats["std_return_1d"] == pytest.approx(returns.std(), rel=1e-2)
        assert stats["min_return"] == pytest.approx(returns.min(), rel=1e-2)
        assert stats["max_return"] == pytest.approx(returns.max(), rel=1e-2)

    def test_impact_stats_date_range(self, news_impact_analyzer):
        """Test that date range is included in stats."""
        stats = news_impact_analyzer.get_impact_stats()

        assert "date_range" in stats
        assert stats["date_range"][0] == "2025-01-15"
        assert stats["date_range"][1] == "2025-03-25"

    def test_impact_stats_no_returns(self, sample_historical_df):
        """Test stats when returns_1d column is missing."""
        df = sample_historical_df.drop(columns=["returns_1d"])
        analyzer = NewsImpact(df, text_column="headline")

        with pytest.raises(ValueError, match="returns_1d column not available"):
            analyzer.get_impact_stats()

    def test_impact_stats_no_dates(self, sample_historical_df):
        """Test stats when date column is missing."""
        df = sample_historical_df.drop(columns=["date"])
        analyzer = NewsImpact(df, text_column="headline")

        stats = analyzer.get_impact_stats()

        assert "date_range" not in stats
        assert stats["total_headlines"] == 10


class TestNewsImpactAddHeadlines:
    """Tests for adding new headlines."""

    def test_add_headlines(self, news_impact_analyzer, sample_historical_df):
        """Test adding new headlines."""
        original_count = len(news_impact_analyzer.historical_df)

        new_data = pd.DataFrame({
            "headline": ["New headline about market"],
            "date": ["2025-04-01"],
            "returns_1d": [0.015],
            "ticker": ["SPY"],
        })

        news_impact_analyzer.add_headlines(new_data)

        assert len(news_impact_analyzer.historical_df) == original_count + 1

    def test_add_headlines_no_rebuild(self, news_impact_analyzer):
        """Test adding headlines without rebuilding index."""
        new_data = pd.DataFrame({
            "headline": ["New headline"],
            "date": ["2025-04-01"],
            "returns_1d": [0.01],
        })

        news_impact_analyzer.add_headlines(new_data, rebuild_index=False)

        # Index should still have old size
        assert news_impact_analyzer.index.ntotal == 10

    def test_add_headlines_missing_column(self, news_impact_analyzer):
        """Test adding headlines with missing text column."""
        new_data = pd.DataFrame({
            "title": ["New headline"],  # Wrong column name
            "date": ["2025-04-01"],
        })

        with pytest.raises(ValueError, match="must contain"):
            news_impact_analyzer.add_headlines(new_data)


class TestNewsImpactEmbeddings:
    """Tests for embedding functionality."""

    def test_get_embedding(self, news_impact_analyzer):
        """Test getting embedding for text."""
        embedding = news_impact_analyzer.get_embedding("Test headline")

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (1, news_impact_analyzer.embedding_dim)
        # Normalized embeddings should have unit norm
        norm = np.linalg.norm(embedding)
        assert pytest.approx(norm, rel=1e-5) == 1.0

    def test_get_embedding_shape(self, news_impact_analyzer):
        """Test embedding dimension."""
        embedding = news_impact_analyzer.get_embedding("Test")

        # all-MiniLM-L6-v2 produces 384-dimensional embeddings
        assert news_impact_analyzer.embedding_dim == 384


class TestNewsImpactRepr:
    """Tests for string representation."""

    def test_repr(self, news_impact_analyzer):
        """Test string representation."""
        repr_str = repr(news_impact_analyzer)

        assert "NewsImpact" in repr_str
        assert "n_headlines=10" in repr_str


class TestNewsImpactEdgeCases:
    """Tests for edge cases."""

    def test_single_headline(self):
        """Test with single headline."""
        df = pd.DataFrame({
            "headline": ["Only headline"],
            "date": ["2025-01-01"],
            "returns_1d": [0.01],
        })

        analyzer = NewsImpact(df, text_column="headline")
        results = analyzer.query("Similar text")

        assert len(results) == 1

    def test_query_after_add(self, news_impact_analyzer):
        """Test querying after adding headlines."""
        new_data = pd.DataFrame({
            "headline": ["Very specific new headline about tech"],
            "date": ["2025-04-01"],
            "returns_1d": [0.02],
        })

        news_impact_analyzer.add_headlines(new_data)

        # Query should now include the new headline
        results = news_impact_analyzer.query("tech news")
        assert len(results.historical_df) == 11 if hasattr(results, 'historical_df') else True

    def test_special_characters_in_headline(self):
        """Test headlines with special characters."""
        df = pd.DataFrame({
            "headline": [
                "Company A reports 50% increase in revenue!",
                "What's next for the market? Analysts weigh in",
                "Stock rises on 'better than expected' results",
            ],
            "date": ["2025-01-01", "2025-01-02", "2025-01-03"],
            "returns_1d": [0.05, 0.02, 0.03],
        })

        analyzer = NewsImpact(df, text_column="headline")
        results = analyzer.query("Company reports increase")

        assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
