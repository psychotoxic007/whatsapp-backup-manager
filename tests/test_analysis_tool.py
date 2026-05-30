"""Tests for Analysis Tool."""

import pytest
from whatsapp_backup_manager.analysis_tool import AnalysisTool


class TestAnalysisTool:
    """Test cases for AnalysisTool class."""

    @pytest.fixture
    def config(self):
        """Fixture for test configuration."""
        return {
            'REPORT_STORAGE_PATH': './test_reports'
        }

    @pytest.fixture
    def analyzer(self, config):
        """Fixture for AnalysisTool instance."""
        return AnalysisTool(config)

    def test_initialization(self, analyzer):
        """Test AnalysisTool initialization."""
        assert analyzer is not None
        assert analyzer.report_storage_path.exists()

    def test_analyze_backup(self, analyzer):
        """Test analyzing a backup."""
        analysis = analyzer.analyze_backup('test_backup')
        assert isinstance(analysis, dict)
        assert 'backup_id' in analysis
