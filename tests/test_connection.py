from src.config import load_config
from src.db import DatabaseConnection


def test_connection_initialization():

    config = load_config()

    local_config = config["local_database"]

    conn = DatabaseConnection(local_config)

    assert conn.config == local_config
    assert conn.connection is None
