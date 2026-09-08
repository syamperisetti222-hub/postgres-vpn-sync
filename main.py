"""Main entry point for PostgreSQL VPN Sync"""

import sys
from pathlib import Path
from src.sync import SyncOrchestrator
from src.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main function"""
    try:
        config_path = Path(__file__).parent / "config" / "config.yaml"
        
        orchestrator = SyncOrchestrator(config_path)
        orchestrator.initialize_connections()
        
        success = orchestrator.run_sync()
        
        if success:
            logger.info("Sync completed successfully")
            return 0
        else:
            logger.error("Sync failed")
            return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
