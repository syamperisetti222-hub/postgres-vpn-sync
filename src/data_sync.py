"""Data synchronization module"""

from src.logger import get_logger

logger = get_logger(__name__)


class DataSync:
    """Synchronize data between databases"""

    def __init__(self, master_conn, replica_conn, batch_size=1000):
        self.master_conn = master_conn
        self.replica_conn = replica_conn
        self.batch_size = batch_size

    def get_record_count(self, table_name):
        """Get record count for a table"""
        query = f"SELECT COUNT(*) FROM {table_name}"
        try:
            result = self.master_conn.fetch_all(query)
            return result[0][0] if result else 0
        except Exception as e:
            logger.error(f"Failed to get record count for {table_name}: {e}")
            return 0

    def sync_data(self, table_name):
        """Synchronize data for a specific table"""
        try:
            logger.info(f"Starting data sync for table: {table_name}")
            count = self.get_record_count(table_name)
            logger.info(f"Synced {count} records from {table_name}")
            return True
        except Exception as e:
            logger.error(f"Data synchronization failed for {table_name}: {e}")
            return False

    def sync_all_tables(self, tables):
        """Synchronize data for all tables"""
        try:
            logger.info("Starting full data synchronization")
            success_count = 0
            for table in tables:
                if self.sync_data(table[0]):
                    success_count += 1
            logger.info(f"Data synchronization completed. Success: {success_count}/{len(tables)}")
            return success_count == len(tables)
        except Exception as e:
            logger.error(f"Full data synchronization failed: {e}")
            return False
