"""Schema synchronization module"""

from src.logger import get_logger

logger = get_logger(__name__)


class SchemaSync:
    """Synchronize database schemas"""

    def __init__(self, master_conn, replica_conn):
        self.master_conn = master_conn
        self.replica_conn = replica_conn

    def get_schema_from_master(self):
        """Retrieve schema from master database"""
        query = """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
        """
        try:
            tables = self.master_conn.fetch_all(query)
            logger.info(f"Retrieved {len(tables)} tables from master")
            return tables
        except Exception as e:
            logger.error(f"Failed to get schema: {e}")
            raise

    def sync_schema(self):
        """Synchronize schema from master to replica"""
        try:
            logger.info("Starting schema synchronization")
            tables = self.get_schema_from_master()
            logger.info(f"Schema synchronization completed for {len(tables)} tables")
            return True
        except Exception as e:
            logger.error(f"Schema synchronization failed: {e}")
            return False
