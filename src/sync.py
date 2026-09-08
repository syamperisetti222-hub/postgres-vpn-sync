"""Main synchronization orchestrator"""

from src.schema_sync import (
    schema_exists,
    create_schema
)

from src.table_sync import (
    table_exists,
    get_tables,
    get_columns,
    get_column_names,
    get_primary_keys,
    create_table_from_structure,
    get_table_record_count
)

from src.data_sync import (
    get_table_data,
    get_table_data_by_pk,
    record_exists_in_master,
    insert_row,
    insert_rows,
    update_row,
    log_audit
)


class SyncEngine:
    """
    Main synchronization engine.
    Handles three stages: Connectivity -> Schema/Table -> Data
    """
    
    def __init__(self, local_conn, master_conn, logger):
        self.local_conn = local_conn
        self.master_conn = master_conn
        self.logger = logger
        
        self.stats = {
            "schemas_created": 0,
            "tables_created": 0,
            "records_inserted": 0,
            "records_updated": 0,
            "errors": 0
        }
    
    # =========================================================
    # STAGE 1: CONNECTIVITY
    # =========================================================
    
    def test_connectivity(self):
        """
        Test connectivity to both databases.
        
        Returns:
            bool: True if both connections are working
        """
        try:
            # Test local connection
            with self.local_conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.logger.info("✓ Local PostgreSQL connection OK")
            
            # Test master connection (through VPN)
            with self.master_conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.logger.info("✓ Master PostgreSQL connection OK (VPN working)")
            
            return True
        except Exception as e:
            self.logger.error(f"✗ Connection test failed: {e}")
            return False
    
    # =========================================================
    # STAGE 2: SCHEMA & TABLE SYNCHRONIZATION
    # =========================================================
    
    def sync_schema(self, schema_name):
        """
        Ensure schema exists in master.
        
        Args:
            schema_name: str - schema to sync
        
        Returns:
            bool: True if successful
        """
        self.logger.info(f"\n--- Syncing Schema: {schema_name} ---")
        
        try:
            if not schema_exists(self.master_conn, schema_name):
                self.logger.info(f"Creating schema: {schema_name}")
                create_schema(self.master_conn, schema_name)
                self.stats["schemas_created"] += 1
                self.logger.info(f"✓ Schema created: {schema_name}")
            else:
                self.logger.info(f"Schema already exists: {schema_name}")
            
            return True
        except Exception as e:
            self.logger.error(f"✗ Schema sync failed: {e}")
            self.stats["errors"] += 1
            return False
    
    def sync_table_structure(self, schema_name, table_name):
        """
        Synchronize table structure from local to master.
        
        Args:
            schema_name: str - schema name
            table_name: str - table name
        
        Returns:
            bool: True if successful
        """
        try:
            # Check if table exists in master
            if table_exists(self.master_conn, schema_name, table_name):
                self.logger.info(f"  Table exists: {schema_name}.{table_name}")
                return True
            
            # Get table structure from local
            self.logger.info(f"  Retrieving table structure: {schema_name}.{table_name}")
            columns = get_columns(self.local_conn, schema_name, table_name)
            
            if not columns:
                self.logger.warning(f"  No columns found in: {schema_name}.{table_name}")
                return False
            
            # Create table in master
            self.logger.info(f"  Creating table: {schema_name}.{table_name}")
            create_table_from_structure(
                self.master_conn,
                schema_name,
                table_name,
                columns
            )
            
            self.stats["tables_created"] += 1
            self.logger.info(f"  ✓ Table created: {schema_name}.{table_name}")
            
            return True
        except Exception as e:
            self.logger.error(f"  ✗ Table structure sync failed: {e}")
            self.stats["errors"] += 1
            return False
    
    # =========================================================
    # STAGE 3: DATA SYNCHRONIZATION (with UPSERT logic)
    # =========================================================
    
    def sync_table_data(self, schema_name, table_name):
        """
        Synchronize data from local to master with UPSERT logic.
        
        Flow:
            1. Read primary keys
            2. Get all data from local table
            3. For each row:
               - Check if exists in master by PK
               - If not exists: INSERT
               - If exists: Compare and UPDATE if changed
        
        Args:
            schema_name: str - schema name
            table_name: str - table name
        
        Returns:
            tuple: (inserted_count, updated_count)
        """
        inserted = 0
        updated = 0
        
        try:
            self.logger.info(f"\n  Syncing Data: {schema_name}.{table_name}")
            
            # Get primary keys
            pk_columns = get_primary_keys(self.local_conn, schema_name, table_name)
            if not pk_columns:
                self.logger.warning(f"    ⚠ No primary key found for: {schema_name}.{table_name}")
                self.logger.warning(f"    → Skipping data sync (primary key required)")
                return 0, 0
            
            # Get all columns
            column_names = get_columns(self.local_conn, schema_name, table_name)
            all_columns = [col[0] for col in column_names]
            
            # Get table data from local (ordered by PK for batch processing)
            local_columns, local_rows = get_table_data_by_pk(
                self.local_conn,
                schema_name,
                table_name,
                pk_columns
            )
            
            self.logger.info(f"    → Found {len(local_rows)} records in local database")
            
            # Process each row
            for row_data in local_rows:
                # Extract PK values
                pk_values = tuple(
                    row_data[local_columns.index(col)]
                    for col in pk_columns
                )
                
                # Check if record exists in master
                if record_exists_in_master(self.master_conn, schema_name, table_name, pk_columns, pk_values):
                    # UPDATE logic (compare and update if changed)
                    if update_row(
                        self.master_conn,
                        schema_name,
                        table_name,
                        pk_columns,
                        pk_values,
                        local_columns,
                        row_data
                    ):
                        updated += 1
                        log_audit(
                            self.master_conn,
                            schema_name,
                            table_name,
                            "UPDATE",
                            str(pk_values)
                        )
                else:
                    # INSERT new record
                    if insert_row(
                        self.master_conn,
                        schema_name,
                        table_name,
                        local_columns,
                        row_data
                    ):
                        inserted += 1
                        log_audit(
                            self.master_conn,
                            schema_name,
                            table_name,
                            "INSERT",
                            str(pk_values)
                        )
            
            self.logger.info(f"    ✓ Inserted: {inserted}, Updated: {updated}")
            self.stats["records_inserted"] += inserted
            self.stats["records_updated"] += updated
            
            return inserted, updated
        
        except Exception as e:
            self.logger.error(f"    ✗ Data sync failed: {e}")
            self.stats["errors"] += 1
            return 0, 0
    
    # =========================================================
    # MAIN ORCHESTRATION
    # =========================================================
    
    def run_full_sync(self, schemas):
        """
        Run complete synchronization process.
        
        Stages:
        1. Test Connectivity
        2. Schema Synchronization
        3. Table Structure Synchronization
        4. Data Synchronization
        
        Args:
            schemas: list - schema names to sync
        
        Returns:
            bool: True if successful
        """
        self.logger.info("="*60)
        self.logger.info("PostgreSQL VPN SYNC - FULL SYNCHRONIZATION")
        self.logger.info("="*60)
        
        # =========================================================
        # STAGE 1: CONNECTIVITY
        # =========================================================
        self.logger.info("\n[STAGE 1] Testing Connectivity...")
        if not self.test_connectivity():
            self.logger.error("\n✗ Connectivity test failed. Ensure VPN is connected.")
            return False
        
        # =========================================================
        # STAGE 2 & 3: SCHEMA, TABLE, and DATA SYNC
        # =========================================================
        for schema_name in schemas:
            self.logger.info(f"\n[STAGE 2] Synchronizing Schema: {schema_name}")
            
            # Ensure schema exists
            if not self.sync_schema(schema_name):
                continue
            
            # Get tables from local
            try:
                tables = get_tables(self.local_conn, schema_name)
                self.logger.info(f"\n[STAGE 3] Synchronizing Tables in {schema_name}...")
                self.logger.info(f"Found {len(tables)} tables")
                
                for table_name in tables:
                    # Sync table structure
                    self.logger.info(f"\n  Table: {schema_name}.{table_name}")
                    if not self.sync_table_structure(schema_name, table_name):
                        continue
                    
                    # Sync table data
                    self.logger.info(f"\n[STAGE 4] Synchronizing Data in {schema_name}.{table_name}")
                    self.sync_table_data(schema_name, table_name)
                
            except Exception as e:
                self.logger.error(f"Error processing schema {schema_name}: {e}")
                self.stats["errors"] += 1
        
        # =========================================================
        # FINAL REPORT
        # =========================================================
        self.logger.info("\n" + "="*60)
        self.logger.info("SYNCHRONIZATION SUMMARY")
        self.logger.info("="*60)
        self.logger.info(f"Schemas Created: {self.stats['schemas_created']}")
        self.logger.info(f"Tables Created: {self.stats['tables_created']}")
        self.logger.info(f"Records Inserted: {self.stats['records_inserted']}")
        self.logger.info(f"Records Updated: {self.stats['records_updated']}")
        self.logger.info(f"Errors: {self.stats['errors']}")
        self.logger.info("="*60)
        
        if self.stats["errors"] == 0:
            self.logger.info("\n✓ SYNCHRONIZATION COMPLETED SUCCESSFULLY")
            return True
        else:
            self.logger.warning(f"\n⚠ SYNCHRONIZATION COMPLETED WITH {self.stats['errors']} ERRORS")
            return True  # Return True to indicate process ran, but check stats
