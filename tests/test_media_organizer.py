"""Tests for Media Organizer."""

import pytest
from whatsapp_backup_manager.media_organizer import MediaOrganizer


class TestMediaOrganizer:
    """Test cases for MediaOrganizer class."""

    @pytest.fixture
    def config(self):
        """Fixture for test configuration."""
        return {
            'MEDIA_STORAGE_PATH': './test_media'
        }

    @pytest.fixture
    def organizer(self, config):
        """Fixture for MediaOrganizer instance."""
        return MediaOrganizer(config)

    def test_initialization(self, organizer):
        """Test MediaOrganizer initialization."""
        assert organizer is not None
        assert organizer.media_storage_path.exists()

    def test_get_media_statistics(self, organizer):
        """Test getting media statistics."""
        stats = organizer.get_media_statistics('test_backup')
        assert isinstance(stats, dict)
        assert 'total_files' in stats
