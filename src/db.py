import psycopg
from psycopg import sql


def get_connection(config):
    """
    Establish a PostgreSQL connection.
    
    Args:
        config: dict with host, port, database, username, password
    
    Returns:
        psycopg connection object
    """
    try:
        connection = psycopg.connect(
            host=config["host"],
            port=config["port"],
            dbname=config["database"],
            user=config["username"],
            password=config["password"]
        )
        return connection
    except psycopg.Error as e:
        raise Exception(f"Database connection failed: {e}")


def test_connection(connection):
    """
    Test if connection is alive.
    
    Args:
        connection: psycopg connection object
    
    Returns:
        bool: True if connection is working
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception as e:
        return False
