"""Data synchronization module with UPSERT logic"""


def get_table_data(connection, schema_name, table_name):
    """
    Fetch all data from local table.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
    
    Returns:
        tuple: (column_names, rows)
    """
    query = f'SELECT * FROM "{schema_name}"."{table_name}"'
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
    
    return columns, rows


def get_table_data_by_pk(connection, schema_name, table_name, pk_columns):
    """
    Fetch all data from table, ordered by primary key.
    Useful for batch processing.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
        pk_columns: list - primary key column names
    
    Returns:
        tuple: (column_names, rows)
    """
    if not pk_columns:
        return get_table_data(connection, schema_name, table_name)
    
    order_by = ", ".join(f'"{col}"' for col in pk_columns)
    query = f'SELECT * FROM "{schema_name}"."{table_name}" ORDER BY {order_by}'
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
    
    return columns, rows


def record_exists_in_master(connection, schema_name, table_name, pk_columns, pk_values):
    """
    Check if record exists in master database using primary key.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
        pk_columns: list - primary key column names
        pk_values: tuple - primary key values
    
    Returns:
        bool: True if record exists
    """
    where_clauses = [f'"{col}" = %s' for col in pk_columns]
    where_string = " AND ".join(where_clauses)
    
    query = f'SELECT 1 FROM "{schema_name}"."{table_name}" WHERE {where_string}'
    
    with connection.cursor() as cursor:
        cursor.execute(query, pk_values)
        return cursor.fetchone() is not None


def insert_row(connection, schema_name, table_name, columns, row_data):
    """
    Insert a single row into master table.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
        columns: list - column names
        row_data: tuple - row values
    
    Returns:
        bool: True if successful
    """
    column_list = ", ".join(f'"{col}"' for col in columns)
    placeholders = ", ".join(["%%s"] * len(columns))
    
    query = f'INSERT INTO "{schema_name}"."{table_name}" ({column_list}) VALUES ({placeholders})'
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, row_data)
        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        return False


def insert_rows(connection, schema_name, table_name, columns, rows):
    """
    Insert multiple rows into master table.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
        columns: list - column names
        rows: list - row tuples
    
    Returns:
        int: number of rows inserted
    """
    if not rows:
        return 0
    
    column_list = ", ".join(f'"{col}"' for col in columns)
    placeholders = ", ".join(["%%s"] * len(columns))
    
    query = f'INSERT INTO "{schema_name}"."{table_name}" ({column_list}) VALUES ({placeholders})'
    
    inserted = 0
    
    try:
        with connection.cursor() as cursor:
            for row in rows:
                try:
                    cursor.execute(query, row)
                    inserted += 1
                except Exception as e:
                    # Log individual row errors but continue
                    pass
        connection.commit()
    except Exception as e:
        connection.rollback()
    
    return inserted


def update_row(connection, schema_name, table_name, pk_columns, pk_values, columns, row_data):
    """
    Update a single row in master table.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
        pk_columns: list - primary key column names
        pk_values: tuple - primary key values
        columns: list - all column names
        row_data: tuple - all row values
    
    Returns:
        bool: True if successful
    """
    # Find non-PK columns for SET clause
    pk_set = set(pk_columns)
    update_cols = [col for col in columns if col not in pk_set]
    
    if not update_cols:
        return True  # No columns to update
    
    set_clauses = [f'"{col}" = %s' for col in update_cols]
    set_string = ", ".join(set_clauses)
    
    where_clauses = [f'"{col}" = %s' for col in pk_columns]
    where_string = " AND ".join(where_clauses)
    
    # Get values for update columns (non-PK)
    update_values = tuple(
        row_data[columns.index(col)] for col in update_cols
    )
    
    query = f'UPDATE "{schema_name}"."{table_name}" SET {set_string} WHERE {where_string}'
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, update_values + pk_values)
        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        return False


def delete_row(connection, schema_name, table_name, pk_columns, pk_values):
    """
    Delete a single row from master table.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
        pk_columns: list - primary key column names
        pk_values: tuple - primary key values
    
    Returns:
        bool: True if successful
    """
    where_clauses = [f'"{col}" = %s' for col in pk_columns]
    where_string = " AND ".join(where_clauses)
    
    query = f'DELETE FROM "{schema_name}"."{table_name}" WHERE {where_string}'
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, pk_values)
        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        return False


def log_audit(connection, schema_name, table_name, operation, record_id, old_values=None, new_values=None):
    """
    Log data operation to audit table.
    
    Args:
        connection: psycopg connection object
        schema_name: str - schema name
        table_name: str - table name
        operation: str - 'INSERT', 'UPDATE', or 'DELETE'
        record_id: str - record identifier
        old_values: dict - old values (for UPDATE/DELETE)
        new_values: dict - new values (for INSERT/UPDATE)
    """
    try:
        query = """
            INSERT INTO sync_metadata.audit_log
            (schema_name, table_name, operation, record_id, old_values, new_values)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    schema_name,
                    table_name,
                    operation,
                    record_id,
                    old_values,
                    new_values
                )
            )
        connection.commit()
    except Exception as e:
        pass  # Audit failure should not stop sync
