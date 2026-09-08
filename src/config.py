"""Configuration module for PostgreSQL VPN Sync"""

import yaml
import os
from pathlib import Path


class Config:
    """Configuration manager"""

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing config file: {e}")

    def get_master_db_config(self):
        """Get master database configuration"""
        return self.config.get('master_db', {})

    def get_replica_db_config(self):
        """Get replica database configuration"""
        return self.config.get('replica_db', {})

    def get_sync_config(self):
        """Get sync configuration"""
        return self.config.get('sync', {})
