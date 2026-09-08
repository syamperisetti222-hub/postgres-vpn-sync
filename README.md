# PostgreSQL VPN Sync

A Python-based tool to synchronize data from a local PostgreSQL database to a central/master PostgreSQL database over a VPN connection.

## Architecture

```
┌──────────────────── Laptop 1 ────────────────────┐
│                                                  │
│  Local PostgreSQL ──► Python Sync Application   │
│                            │                    │
│                        VPN │                    │
└────────────────────────┼───┘
                         │
                         ▼
┌──────────────────── Master Server ──────────────┐
│                                                  │
│  PostgreSQL (Central Repository)                │
│    ├── schema1.table1                           │
│    ├── schema1.table2                           │
│    └── sync_metadata (audit & tracking)         │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Features

### Stage 1: Connectivity ✓
- Test local PostgreSQL connection
- Test master PostgreSQL connection (via VPN)
- Verify VPN is working and accessible

### Stage 2: Schema & Table Synchronization ✓
- Detect schemas in local database
- Create missing schemas in master
- Detect tables in local database
- Create table structures in master based on local
- Preserve column types, nullable constraints, and primary keys

### Stage 3: Data Synchronization ✓
- Read all data from local tables
- Use primary keys for comparison
- **UPSERT Logic**:
  - INSERT: If record doesn't exist in master
  - UPDATE: If record exists and data differs
- Batch processing for performance
- Audit logging of all operations

## Requirements

- Python 3.8+
- PostgreSQL 10+ (local and master)
- VPN connection to master server
- Network access to master PostgreSQL (default port 5432)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/syamperisetti222-hub/postgres-vpn-sync.git
cd postgres-vpn-sync
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Databases

Edit `config/config.yaml`:

```yaml
local_database:
  host: "localhost"          # Your laptop's PostgreSQL
  port: 5432
  database: "pos_local"
  username: "postgres"
  password: "local_password"

master_database:
  host: "10.10.10.10"        # Master server VPN IP
  port: 5432
  database: "pos_master"
  username: "sync_user"
  password: "master_password"

sync:
  schemas:
    - "public"              # Schemas to sync
  batch_size: 1000         # Records per batch
```

**Important**: Replace IP addresses and credentials with your actual values.

## Usage

### Prerequisites

1. **VPN Connection**: Ensure VPN is connected before running
   ```bash
   # Test VPN connectivity
   ping 10.10.10.10  # Should work if VPN is connected
   ```

2. **Database Access**: Verify direct PostgreSQL access
   ```bash
   # Test master database connection
   psql -h 10.10.10.10 -p 5432 -U sync_user -d pos_master
   ```

### Running Sync

```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# Run synchronization
python main.py
```

### Output

The script will:
1. Test connectivity to both databases
2. Create missing schemas
3. Create missing table structures
4. Insert new records
5. Update changed records
6. Generate detailed log file

```
============================================================
PostgreSQL VPN Sync - FULL SYNCHRONIZATION
============================================================

[STAGE 1] Testing Connectivity...
✓ Local PostgreSQL connection OK
✓ Master PostgreSQL connection OK (VPN working)

[STAGE 2] Synchronizing Schema: public
Creating schema: public
✓ Schema created: public

[STAGE 3] Synchronizing Tables in public...
Found 3 tables

  Table: public.customers
  ✓ Table created: public.customers

[STAGE 4] Synchronizing Data in public.customers
  → Found 1000 records in local database
  ✓ Inserted: 950, Updated: 50

...

============================================================
SYNCHRONIZATION SUMMARY
============================================================
Schemas Created: 1
Tables Created: 3
Records Inserted: 2850
Records Updated: 150
Errors: 0
============================================================

✓ SYNCHRONIZATION COMPLETED SUCCESSFULLY
```

## Log Files

Logs are saved in `logs/` directory with timestamps:

```
logs/
├── sync_20240115_143022.log
├── sync_20240115_150511.log
└── ...
```

Check logs for detailed information about each sync run.

## Advanced Configuration

### Multiple Schemas

```yaml
sync:
  schemas:
    - "public"
    - "crm"
    - "pos"
```

### Batch Size

Adjust for performance:

```yaml
sync:
  batch_size: 5000  # Larger = faster but more memory
```

## Troubleshooting

### VPN Connection Issues

```bash
# Verify VPN is connected
ping 10.10.10.10

# If ping fails, VPN is not connected
# Connect VPN and try again
```

### Database Connection Errors

```bash
# Test PostgreSQL connectivity directly
psql -h 10.10.10.10 -p 5432 -U sync_user -d pos_master

# If fails, check:
# 1. Master database is running
# 2. Credentials are correct
# 3. Firewall allows port 5432
# 4. VPN is connected
```

### Configuration Not Found

```bash
# Ensure config file exists
ls -la config/config.yaml

# If missing, create it with template values
```

## Security Considerations

⚠️ **Important**: Never commit `config/config.yaml` to Git (it contains passwords).

### Better Practices

1. **Use Environment Variables** (recommended):
   ```bash
   export DB_MASTER_PASSWORD=your_password
   export DB_LOCAL_PASSWORD=your_password
   ```
   
   Then update config loading to use these.

2. **Use Secrets Manager** (production):
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault

3. **Restrict File Permissions**:
   ```bash
   chmod 600 config/config.yaml
   ```

## Performance Tips

1. **Batch Size**: Increase for large tables
   ```yaml
   batch_size: 10000  # Processes 10k records at a time
   ```

2. **Network**: Ensure stable VPN connection

3. **Database**: Run during low-traffic periods

4. **Indexes**: Create indexes on primary keys (automatic)

## Future Enhancements

- [ ] Soft delete handling (mark as deleted instead of removing)
- [ ] Conflict resolution strategies
- [ ] Change Data Capture (CDC) for incremental syncs
- [ ] Scheduling/cron integration
- [ ] Web dashboard for monitoring
- [ ] Multi-master replication
- [ ] Compression for large data transfers

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Check logs in `logs/` directory
- Review this README
- Create an issue on GitHub

## Authors

- **Syam Perisetti** - Initial development

---

**Last Updated**: January 2024
