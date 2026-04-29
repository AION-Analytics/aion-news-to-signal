# =============================================================================
# AION Taxonomy - Unit Tests
# =============================================================================
"""
Unit tests for AION Taxonomy package.

Run with: pytest tests/ -v
"""

import pytest
import yaml
from pathlib import Path

# Sample taxonomy for testing
SAMPLE_TAXONOMY = """
metadata:
  version: 1.0.0
  market: INDIA_EQUITY

config:
  impact_scale:
    POSITIVE: 1.0
    NEUTRAL: 0.0
    NEGATIVE: -1.0
  confidence_weights:
    model_probability: 0.4
    taxonomy_match: 0.3
    data_quality: 0.2
    agreement_score: 0.1
  flip_threshold:
    fallback_static: 0.35

sectors:
- id: Financial Services
  beta_default: 1.1
- id: Banks
  beta_default: 1.15
- id: IT
  beta_default: 0.9

categories:
- id: macro_economy
  name: Macro Economy
  subcategories:
  - id: monetary_policy
    name: Monetary Policy
    events:
    - id: macro_rbi_repo_hike
      name: RBI Repo Rate Hike
      keywords:
      - repo rate hike
      - rbi hikes repo
      - rate increase
      base_impact:
        mild: -0.25
        normal: -0.55
        severe: -0.85
      default_impact: normal
      market_weight: 0.9
      sector_impacts:
        Banks:
          multiplier: 1.15
          bias: inverse
          rationale: Funding costs rise
        Financial Services:
          multiplier: 1.1
          bias: inverse
          rationale: Funding costs rise
    - id: macro_rbi_repo_cut
      name: RBI Repo Rate Cut
      keywords:
      - repo rate cut
      - rbi cuts repo
      base_impact:
        mild: 0.25
        normal: 0.55
        severe: 0.85
      default_impact: normal
      market_weight: 0.9
      sector_impacts:
        Banks:
          multiplier: 1.15
          bias: aligned
          rationale: Funding costs fall
"""


@pytest.fixture
def sample_taxonomy(tmp_path):
    """Create a sample taxonomy file for testing."""
    taxonomy_file = tmp_path / "test_taxonomy.yaml"
    taxonomy_file.write_text(SAMPLE_TAXONOMY)
    return str(taxonomy_file)


class TestLoader:
    """Tests for loader.py"""

    def test_load_taxonomy_success(self, sample_taxonomy):
        """Test successful taxonomy loading."""
        from aion_taxonomy.loader import load_taxonomy
        
        taxonomy = load_taxonomy(sample_taxonomy)
        
        assert taxonomy['metadata']['version'] == '1.0.0'
        assert len(taxonomy['sectors']) == 3
        assert len(taxonomy['categories']) == 1

    def test_load_taxonomy_file_not_found(self):
        """Test loading non-existent file."""
        from aion_taxonomy.loader import load_taxonomy, TaxonomyValidationError
        
        with pytest.raises(FileNotFoundError):
            load_taxonomy("nonexistent_file.yaml")


class TestClassifier:
    """Tests for classifier.py"""

    def test_classify_repo_hike(self, sample_taxonomy):
        """Test classification of repo rate hike headline."""
        from aion_taxonomy.loader import load_taxonomy
        from aion_taxonomy.classifier import EventClassifier
        
        taxonomy = load_taxonomy(sample_taxonomy)
        classifier = EventClassifier(taxonomy)
        
        result = classifier.classify("RBI hikes repo rate by 25 bps")
        
        assert result['event_id'] == 'macro_rbi_repo_hike'
        assert result['match_score'] > 0
        assert 'repo rate' in ' '.join(result['matched_keywords']).lower()

    def test_classify_no_match(self, sample_taxonomy):
        """Test classification with no matching event."""
        from aion_taxonomy.loader import load_taxonomy
        from aion_taxonomy.classifier import EventClassifier
        
        taxonomy = load_taxonomy(sample_taxonomy)
        classifier = EventClassifier(taxonomy)
        
        result = classifier.classify("Company announces dividend")
        
        assert result['event_id'] is None
        assert result['match_score'] == 0.0


class TestImpact:
    """Tests for impact.py"""

    def test_get_macro_signal(self, sample_taxonomy):
        """Test macro signal computation."""
        from aion_taxonomy.loader import load_taxonomy
        from aion_taxonomy.classifier import EventClassifier
        from aion_taxonomy.impact import get_macro_signal
        
        taxonomy = load_taxonomy(sample_taxonomy)
        classifier = EventClassifier(taxonomy)
        
        event = classifier.classify("RBI hikes repo rate unexpectedly")
        macro_signal, impact_level = get_macro_signal(event, "RBI hikes repo rate unexpectedly")
        
        assert macro_signal < 0  # Negative impact
        assert -1.0 <= macro_signal <= 1.0

    def test_get_sector_signal(self, sample_taxonomy):
        """Test sector signal computation."""
        from aion_taxonomy.loader import load_taxonomy
        from aion_taxonomy.classifier import EventClassifier
        from aion_taxonomy.impact import get_macro_signal, get_sector_signal
        
        taxonomy = load_taxonomy(sample_taxonomy)
        classifier = EventClassifier(taxonomy)
        
        event = classifier.classify("RBI hikes repo rate")
        macro_signal, _ = get_macro_signal(event, "RBI hikes repo rate")
        
        sector_result = get_sector_signal(macro_signal, event, 'Banks')
        
        assert sector_result is not None
        assert sector_result['bias'] == 'inverse'
        # Inverse bias with negative macro = positive for banks
        assert sector_result['sector_signal'] > 0


class TestConfidence:
    """Tests for confidence.py"""

    def test_compute_confidence_basic(self):
        """Test basic confidence computation."""
        from aion_taxonomy.confidence import compute_confidence
        
        confidence = compute_confidence(
            taxonomy_match=0.8,
            data_quality=0.9,
            model_probability=0.85,
            agreement_score=1.0
        )
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.7  # Should be high with good inputs

    def test_compute_agreement_score(self):
        """Test agreement score computation."""
        from aion_taxonomy.confidence import compute_agreement_score
        
        # Full agreement
        agreement = compute_agreement_score(
            taxonomy_signal=0.6,
            model_label='positive',
            model_confidence=0.9
        )
        assert agreement > 0.8
        
        # Disagreement
        agreement = compute_agreement_score(
            taxonomy_signal=-0.6,
            model_label='positive',
            model_confidence=0.9
        )
        assert agreement < 0.3


class TestPipeline:
    """Tests for pipeline.py"""

    def test_pipeline_process(self, sample_taxonomy):
        """Test full pipeline processing."""
        from aion_taxonomy.pipeline import TaxonomyPipeline
        
        pipeline = TaxonomyPipeline(taxonomy_path=sample_taxonomy)
        result = pipeline.process("RBI hikes repo rate by 25 bps")
        
        assert result['event']['event_id'] == 'macro_rbi_repo_hike'
        assert result['macro_signal'] < 0
        assert 0.0 <= result['confidence'] <= 1.0

    def test_pipeline_with_model_output(self, sample_taxonomy):
        """Test pipeline with model agreement."""
        from aion_taxonomy.pipeline import TaxonomyPipeline
        
        pipeline = TaxonomyPipeline(taxonomy_path=sample_taxonomy)
        
        result = pipeline.process(
            headline="RBI hikes repo rate",
            model_output={'label': 'negative', 'confidence': 0.85}
        )
        
        # Agreement should boost confidence
        assert result['confidence_components']['agreement_score'] > 0.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
