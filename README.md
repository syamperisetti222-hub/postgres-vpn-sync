# PostgreSQL VPN Sync

A Python-based tool to synchronize PostgreSQL databases across VPN connections.

## Features

- **Schema Synchronization**: Sync database schemas from master to replica
- **Table Synchronization**: Ensure all tables are synchronized
- **Data Synchronization**: Copy data from master to replica with batch processing
- **Logging**: Comprehensive logging for troubleshooting
- **Configuration**: YAML-based configuration management

## Project Structure

```
postgres-vpn-sync/
├── config/           # Configuration files
├── sql/              # SQL scripts
├── src/              # Source code
├── tests/            # Unit tests
├── main.py           # Main entry point
├── requirements.txt  # Python dependencies
├── .gitignore        # Git ignore rules
└── README.md         # This file
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/syamperisetti222-hub/postgres-vpn-sync.git
cd postgres-vpn-sync
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Edit `config/config.yaml` with your database credentials:

```yaml
master_db:
  host: your_master_host
  port: 5432
  database: your_database
  user: your_user
  password: your_password

replica_db:
  host: your_replica_host
  port: 5432
  database: your_database
  user: your_user
  password: your_password

sync:
  schema_sync: true
  table_sync: true
  data_sync: true
  batch_size: 1000
  log_level: INFO
```

## Usage

Run the synchronization:

```bash
python main.py
```

## Testing

Run unit tests:

```bash
pytest tests/
```

Run tests with coverage:

```bash
pytest tests/ --cov=src
```

## Logging

Logs are stored in the `logs/` directory. Check `logs/sync.log` for detailed information about sync operations.

## Requirements

- Python 3.7+
- PostgreSQL 10+
- VPN connection to both databases

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for your needs.

## Support

For issues and questions, please create an issue on GitHub.
