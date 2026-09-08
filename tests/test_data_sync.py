"""Test data synchronization module"""

import pytest
from src.data_sync import DataSync


class TestDataSync:
    """Test data synchronization functionality"""

    def test_data_sync_initialization(self):
        """Test data sync initialization"""
        data_sync = DataSync(None, None, batch_size=1000)
        assert data_sync.master_conn is None
        assert data_sync.replica_conn is None
        assert data_sync.batch_size == 1000
