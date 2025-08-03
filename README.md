# romm-gog-custodian

A set of tooling specifically designed with Romm libraries in mind, to automate management of a GOG game library,
including torrent management, library cleanup, and logging.

## Features

- Automated torrent management and post-processing
- Game library cleanup and organization
- Configurable logging with log rotation
- Customizable settings via `config/config.cfg`
- Periodic execution with configurable wait time

## How to Run

### Python Environment

1. **Install requirements** (if any):
   ```
   pip install -r requirements.txt
   ```

2. **Configure the application**  
   Edit `config/config.cfg` to set your paths and preferences.

3. **Run the application**:
   ```
   python app.py
   ```

### Docker Environment

1. **Pull and run the container:**
   ```
   docker run -d \
     --name romm-gog-custodian \
     -v /path/to/your/library:/data/library \
     -v /path/to/your/torrents:/data/torrent \
     -v /path/to/your/logs:/app/logs \
     -v /path/to/your/config:/app/config \
     ghcr.io/maus-me/romm-gog-custodian:latest
   ```

## Logging

Logs are written to the file specified by `log_file_path`. The log file will automatically rotate when it reaches 5MB,
keeping up to 5 backup files.

---
