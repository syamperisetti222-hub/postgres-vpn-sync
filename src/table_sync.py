"""Table synchronization module"""


def table_exists(connection, schema_name, table_name):
    """
    Check if table exists in schema.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
    
    Returns:
        bool: True if table exists
    """
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_name = %s
        );
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, (schema_name, table_name))
        return cursor.fetchone()[0]


def get_tables(connection, schema_name):
    """
    Get list of all tables in schema.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
    
    Returns:
        list: table names
    """
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, (schema_name,))
        return [row[0] for row in cursor.fetchall()]


def get_columns(connection, schema_name, table_name):
    """
    Get column information for a table.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
    
    Returns:
        list: tuples of (column_name, data_type, is_nullable)
    """
    query = """
        SELECT
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        ORDER BY ordinal_position;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, (schema_name, table_name))
        return cursor.fetchall()


def get_column_names(connection, schema_name, table_name):
    """
    Get list of column names for a table.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
    
    Returns:
        list: column names
    """
    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        ORDER BY ordinal_position;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, (schema_name, table_name))
        return [row[0] for row in cursor.fetchall()]


def get_primary_keys(connection, schema_name, table_name):
    """
    Get primary key columns for a table.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
    
    Returns:
        list: primary key column names
    """
    query = """
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
         AND tc.table_name = kcu.table_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = %s
          AND tc.table_name = %s
        ORDER BY kcu.ordinal_position;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, (schema_name, table_name))
        return [row[0] for row in cursor.fetchall()]


def create_table_from_structure(connection, schema_name, table_name, columns):
    """
    Create table in master based on local table structure.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
        columns: list - tuples of (column_name, data_type, is_nullable)
    """
    # Ensure schema exists
    with connection.cursor() as cursor:
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
    
    # Build column definitions
    column_defs = []
    for col_name, data_type, is_nullable in columns:
        nullable_str = "" if is_nullable == "YES" else "NOT NULL"
        column_defs.append(f'"{col_name}" {data_type} {nullable_str}'.strip())
    
    # Create table
    column_list = ",\n    ".join(column_defs)
    create_query = f"""
        CREATE TABLE IF NOT EXISTS "{schema_name}"."{table_name}" (
            {column_list}
        );
    """
    
    with connection.cursor() as cursor:
        cursor.execute(create_query)
    
    connection.commit()


def get_table_record_count(connection, schema_name, table_name):
    """
    Get count of records in table.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
    
    Returns:
        int: record count
    """
    query = f'SELECT COUNT(*) FROM "{schema_name}"."{table_name}"'
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchone()[0]
