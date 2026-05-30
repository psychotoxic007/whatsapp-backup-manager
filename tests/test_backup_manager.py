"""Tests for Backup Manager."""

import pytest
from whatsapp_backup_manager.backup_manager import BackupManager


class TestBackupManager:
    """Test cases for BackupManager class."""

    @pytest.fixture
    def config(self):
        """Fixture for test configuration."""
        return {
            'BACKUP_STORAGE_PATH': './test_backups'
        }

    @pytest.fixture
    def manager(self, config):
        """Fixture for BackupManager instance."""
        return BackupManager(config)

    def test_initialization(self, manager):
        """Test BackupManager initialization."""
        assert manager is not None
        assert manager.backup_storage_path.exists()

    def test_list_local_backups(self, manager):
        """Test listing local backups."""
        backups = manager.list_local_backups()
        assert isinstance(backups, list)

    def test_list_cloud_backups(self, manager):
        """Test listing cloud backups."""
        backups = manager.list_cloud_backups()
        assert isinstance(backups, list)
