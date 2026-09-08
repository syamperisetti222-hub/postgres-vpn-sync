"""Schema synchronization module"""


def schema_exists(connection, schema_name):
    """
    Check if schema exists in PostgreSQL database.
    
    Args:
        connection: psycopg connection object
        schema_name: str - name of schema
    
    Returns:
        bool: True if schema exists
    """
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.schemata
            WHERE schema_name = %s
        );
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, (schema_name,))
        return cursor.fetchone()[0]


def create_schema(connection, schema_name):
    """
    Create schema in PostgreSQL database.
    
    Args:
        connection: psycopg connection object
        schema_name: str - name of schema to create
    """
    with connection.cursor() as cursor:
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
    
    connection.commit()


def get_schemas(connection):
    """
    Get list of all schemas in database.
    
    Args:
        connection: psycopg connection object
    
    Returns:
        list: schema names
    """
    query = """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
        ORDER BY schema_name;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]
