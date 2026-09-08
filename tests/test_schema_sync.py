"""Test schema synchronization module"""

import pytest
from src.schema_sync import SchemaSync


class TestSchemaSync:
    """Test schema synchronization functionality"""

    def test_schema_sync_initialization(self):
        """Test schema sync initialization"""
        schema_sync = SchemaSync(None, None)
        assert schema_sync.master_conn is None
        assert schema_sync.replica_conn is None
