"""Test table synchronization module"""

import pytest
from src.table_sync import TableSync


class TestTableSync:
    """Test table synchronization functionality"""

    def test_table_sync_initialization(self):
        """Test table sync initialization"""
        table_sync = TableSync(None, None)
        assert table_sync.master_conn is None
        assert table_sync.replica_conn is None
