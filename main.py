#!/usr/bin/env python3
"""
PostgreSQL VPN Sync - Main Entry Point

This script synchronizes data from a local PostgreSQL database
to a central/master PostgreSQL database over a VPN connection.

Stages:
1. Connectivity: Test connections to both databases
2. Schema/Table: Synchronize schema and table structures
3. Data: Synchronize data with UPSERT logic (INSERT/UPDATE)
"""

import sys
from pathlib import Path

from src.config import load_config, get_local_db_config, get_master_db_config, get_sync_config
from src.db import get_connection, test_connection
from src.logger import setup_logger
from src.sync import SyncEngine


def main():
    """
    Main execution function.
    """
    print("\n" + "="*60)
    print("PostgreSQL VPN Sync")
    print("="*60)
    
    # Setup logging
    logger = setup_logger()
    logger.info("\n" + "="*60)
    logger.info("PostgreSQL VPN Sync Started")
    logger.info("="*60)
    
    try:
        # =========================================================
        # Load Configuration
        # =========================================================
        logger.info("\nLoading configuration...")
        config = load_config()
        logger.info("✓ Configuration loaded")
        
        local_db_config = get_local_db_config(config)
        master_db_config = get_master_db_config(config)
        sync_config = get_sync_config(config)
        
        schemas_to_sync = sync_config.get("schemas", ["public"])
        logger.info(f"Schemas to sync: {', '.join(schemas_to_sync)}")
        
        # =========================================================
        # Connect to Databases
        # =========================================================
        logger.info("\nEstablishing database connections...")
        
        # Local database
        logger.info(f"Connecting to local database: {local_db_config['database']}")
        local_connection = get_connection(local_db_config)
        logger.info("✓ Local database connected")
        
        # Master database (via VPN)
        logger.info(f"Connecting to master database (VPN): {master_db_config['database']}")
        logger.info(f"  Host: {master_db_config['host']} (ensure VPN is connected)")
        master_connection = get_connection(master_db_config)
        logger.info("✓ Master database connected (VPN working)")
        
        # =========================================================
        # Run Synchronization
        # =========================================================
        sync_engine = SyncEngine(local_connection, master_connection, logger)
        
        success = sync_engine.run_full_sync(schemas_to_sync)
        
        # =========================================================
        # Cleanup
        # =========================================================
        logger.info("\nClosing connections...")
        local_connection.close()
        master_connection.close()
        logger.info("✓ Connections closed")
        
        if success:
            print("\n✓ Synchronization completed successfully!")
            logger.info("\n✓ Synchronization completed successfully!")
            return 0
        else:
            print("\n✗ Synchronization failed!")
            logger.error("\n✗ Synchronization failed!")
            return 1
    
    except FileNotFoundError as e:
        print(f"\n✗ Configuration error: {e}")
        logger.error(f"Configuration error: {e}")
        return 1
    
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
