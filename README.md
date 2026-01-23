# FlexiLogger

FlexiLogger is a customizable Python logging library that provides enhanced features for handling logs, including
colorized console outputs, structured JSON logging, log rotation, and context binding.

## Features

- **Structured JSON Logging**: Production-ready format for ELK/Datadog/Splunk.
- **Context Binding**: Add contextual data (user_id, request_id) to logs easily.
- **Automatic Log Rotation**: Prevents log files from growing indefinitely.
- **Colorized Console**: Better readability during development.
- **Dynamic Configuration**: Configure via environment variables.
- **Timezone Support**: UTC, Local, or custom offsets.

---

## Installation

You can install FlexiLogger using pip:

```bash
pip install FlexiLogger
```

---

## Usage

### Basic Usage

To use FlexiLogger in your project:

```python
from FlexiLogger import Logger

# Standard usage (defaults to UTC)
logger = Logger(__file__, log_file_path="app.log")
logger.info("This is an info message")

# Custom timezone and date format
logger_tz = Logger("CustomLogger", timezone="UTC+1", date_format="%Y-%m-%d %H:%M:%S")
logger_tz.info("This message uses UTC+1 and ISO format")
```

### JSON Logging and Context Binding (Production Mode)

Enable JSON logging for machine-readable output and bind context to track requests:

```python
# Enable JSON format (or set env LOGGER_JSON_FORMAT=true)
logger = Logger("AppLogger", log_file_path="app.json", json_format=True)

# Bind context (e.g., at the start of a request)
log = logger.bind(request_id="req-123", user_id=42)

log.info("Processing payment")
# Output: {"timestamp": "...", "level": "INFO", "message": "Processing payment", "request_id": "req-123", "user_id": 42, ...}

log.warning("Transaction slow", duration_ms=500)
# Output: {"timestamp": "...", "level": "WARNING", "message": "Transaction slow", "request_id": "req-123", "user_id": 42, "duration_ms": 500, ...}
```

### Log Rotation

Prevent disk overflow by setting max size and backup count:

```python
logger = Logger(
    "RotationLogger",
    log_file_path="app.log",
    max_bytes=10 * 1024 * 1024, # 10 MB
    backup_count=5
)
```

### Advanced Traceback Handling

FlexiLogger provides a `GetTraceback` class for managing exceptions:

```python
import os
from FlexiLogger import Logger, GetTraceback

logger = Logger(__file__)
traceback_handler = GetTraceback(logger)

try:
    1 / 0
except Exception as e:
    traceback_handler.error("An error occurred", print_full_exception=True)
```

---

## Environment Variables

FlexiLogger uses several environment variables to customize its behavior:

| Variable Name              | Description                                                                                                  | Default Value |
|----------------------------|--------------------------------------------------------------------------------------------------------------|---------------|
| `LOG_PATH`                 | Specifies the path to the log file. If not set, logging to a file is disabled.                               | `None`        |
| `LOGGER_JSON_FORMAT`       | Enables JSON output format. Values: `true`/`1` or `false`/`0`.                                               | `false`       |
| `LOG_TRACEBACK_PATH`       | Specifies the path where traceback will be saved. If not set, the file defined in the `Logger` will be used. | `None`        |
| `LOGGER_CONSOLE_LOG_LEVEL` | Sets the console log level. Acceptable values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.              | `DEBUG`       |
| `LOGGER_FILE_LOG_LEVEL`    | Sets the file log level. Acceptable values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.                 | `DEBUG`       |
| `LOGGER_TIME_INFO`         | Enables or disables timestamps in log messages. Values: `true`/`1` or `false`/`0`.                           | `true`        |
| `LOGGER_TIMEZONE`          | Sets the timezone for timestamps. Values: `UTC` (default), `LOCAL`, `UTC+3`, `UTC-05:00`, etc.               | `UTC`         |

### Example

Set the environment variables before running your script:

```bash
export LOG_PATH="app.log"
export LOGGER_JSON_FORMAT="true"
export LOGGER_CONSOLE_LOG_LEVEL="INFO"
export LOGGER_TIMEZONE="UTC+3"
```

---

## License

FlexiLogger is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
