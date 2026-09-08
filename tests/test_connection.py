"""Test database connection module"""

import pytest
from src.db import DatabaseConnection


class TestDatabaseConnection:
    """Test database connection functionality"""

    def test_connection_initialization(self):
        """Test connection initialization"""
        config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_password'
        }
        conn = DatabaseConnection(config)
        assert conn.config == config
        assert conn.connection is None
