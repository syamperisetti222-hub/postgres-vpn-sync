"""Database connection module"""

import psycopg2
from psycopg2 import sql
from src.logger import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """Handle database connections"""

    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.config.get('host'),
                port=self.config.get('port'),
                database=self.config.get('database'),
                user=self.config.get('user'),
                password=self.config.get('password')
            )
            logger.info(f"Connected to database: {self.config.get('database')}")
            return self.connection
        except psycopg2.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def execute_query(self, query):
        """Execute a query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            logger.info("Query executed successfully")
            return cursor
        except psycopg2.Error as e:
            logger.error(f"Query execution failed: {e}")
            self.connection.rollback()
            raise

    def fetch_all(self, query):
        """Fetch all results from query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            return cursor.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Fetch query failed: {e}")
            raise
