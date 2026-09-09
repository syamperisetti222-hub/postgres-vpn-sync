from src.config import load_config, get_local_db_config
from src.db import DatabaseConnection


def test_read_employee_table():

    # Load configuration
    config = load_config()

    # Get local database configuration
    local_config = get_local_db_config(config)

    # Create database connection
    db = DatabaseConnection(local_config)

    try:
        # Connect to local PostgreSQL
        db.connect()

        # Read employee table
        columns, rows = db.fetch_table(
            "public",
            "employee"
        )

        # Print results
        print("\nColumns:")
        print(columns)

        print("\nRows:")
        for row in rows:
            print(row)

        # Validate that data exists
        assert len(rows) > 0

    finally:
        # Always close connection
        db.close()
