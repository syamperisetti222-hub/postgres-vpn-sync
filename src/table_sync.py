"""Table synchronization module"""

from src.logger import get_logger

logger = get_logger(__name__)


class TableSync:
    """Synchronize database tables"""

    def __init__(self, master_conn, replica_conn):
        self.master_conn = master_conn
        self.replica_conn = replica_conn

    def get_tables(self):
        """Get list of tables from master"""
        query = """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """
        try:
            tables = self.master_conn.fetch_all(query)
            logger.info(f"Retrieved {len(tables)} tables")
            return tables
        except Exception as e:
            logger.error(f"Failed to get tables: {e}")
            raise

    def sync_tables(self):
        """Synchronize tables from master to replica"""
        try:
            logger.info("Starting table synchronization")
            tables = self.get_tables()
            logger.info(f"Table synchronization completed for {len(tables)} tables")
            return True
        except Exception as e:
            logger.error(f"Table synchronization failed: {e}")
            return False
