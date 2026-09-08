import yaml
from pathlib import Path


def load_config():
    """
    Load configuration from YAML file.
    Returns: dict with local_database, master_database, and sync configs
    """
    config_path = Path("config/config.yaml")
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}. "
            "Please create config/config.yaml"
        )
    
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    
    return config


def get_local_db_config(config):
    """
    Get local database configuration.
    """
    return config.get("local_database", {})


def get_master_db_config(config):
    """
    Get master database configuration.
    """
    return config.get("master_database", {})


def get_sync_config(config):
    """
    Get sync configuration.
    """
    return config.get("sync", {})
