"""Main synchronization orchestrator"""

from src.config import Config
from src.db import DatabaseConnection
from src.schema_sync import SchemaSync
from src.table_sync import TableSync
from src.data_sync import DataSync
from src.logger import get_logger

logger = get_logger(__name__)


class SyncOrchestrator:
    """Orchestrate the entire synchronization process"""

    def __init__(self, config_path=None):
        self.config = Config(config_path)
        self.master_conn = None
        self.replica_conn = None

    def initialize_connections(self):
        """Initialize database connections"""
        try:
            logger.info("Initializing database connections")
            master_config = self.config.get_master_db_config()
            replica_config = self.config.get_replica_db_config()

            self.master_conn = DatabaseConnection(master_config)
            self.replica_conn = DatabaseConnection(replica_config)

            self.master_conn.connect()
            self.replica_conn.connect()
            logger.info("Database connections initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize connections: {e}")
            raise

    def run_sync(self):
        """Run the complete synchronization process"""
        try:
            logger.info("Starting PostgreSQL VPN Sync")
            sync_config = self.config.get_sync_config()

            # Schema sync
            if sync_config.get('schema_sync', True):
                logger.info("Running schema synchronization")
                schema_sync = SchemaSync(self.master_conn, self.replica_conn)
                schema_sync.sync_schema()

            # Table sync
            if sync_config.get('table_sync', True):
                logger.info("Running table synchronization")
                table_sync = TableSync(self.master_conn, self.replica_conn)
                table_sync.sync_tables()

            # Data sync
            if sync_config.get('data_sync', True):
                logger.info("Running data synchronization")
                data_sync = DataSync(
                    self.master_conn,
                    self.replica_conn,
                    batch_size=sync_config.get('batch_size', 1000)
                )
                tables = table_sync.get_tables()
                data_sync.sync_all_tables(tables)

            logger.info("PostgreSQL VPN Sync completed successfully")
            return True
        except Exception as e:
            logger.error(f"Synchronization failed: {e}")
            return False
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        if self.master_conn:
            self.master_conn.disconnect()
        if self.replica_conn:
            self.replica_conn.disconnect()
