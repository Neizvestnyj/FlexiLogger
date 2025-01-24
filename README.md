# FlexiLogger

FlexiLogger is a customizable Python logging library that provides enhanced features for handling logs, including colorized console outputs, log file formatting, and detailed traceback management.

## Features

- Colorized console logging for better readability.
- File-based logging with customizable formats.
- Dynamic configuration via environment variables.
- Enhanced traceback extraction and logging.
- Customizable log level spaces for better alignment.

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

logger = Logger(__file__, log_file_path="app.log")
logger.info("This is an info message")
logger.error("This is an error message")
```

### Advanced Traceback Handling

FlexiLogger provides a `GetTraceback` class for managing exceptions:

```python
from FlexiLogger import GetTraceback

try:
    1 / 0
except Exception as e:
    traceback_handler = GetTraceback(__file__)
    traceback_handler.error("An error occurred", print_full_exception=True)
```

---

## Environment Variables

FlexiLogger uses several environment variables to customize its behavior:

| Variable Name              | Description                                                                                       | Default Value |
|----------------------------|---------------------------------------------------------------------------------------------------|---------------|
| `LOG_PATH`                 | Specifies the path to the log file. If not set, logging to a file is disabled.                   | None          |
| `LOGGER_CONSOLE_LOG_LEVEL` | Sets the console log level. Acceptable values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. | `DEBUG`       |
| `LOGGER_FILE_LOG_LEVEL`    | Sets the file log level. Acceptable values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.    | `DEBUG`       |
| `LOGGER_TIME_INFO`         | Enables or disables timestamps in log messages. Values: `true`/`1` or `false`/`0`.             | `true`        |

### Example

Set the environment variables before running your script:

```bash
export LOG_PATH="app.log"
export LOGGER_CONSOLE_LOG_LEVEL="INFO"
export LOGGER_FILE_LOG_LEVEL="ERROR"
export LOGGER_TIME_INFO="false"
```

---

## Project Structure

```
FlexiLogger/
├── __init__.py
├── logger.py
├── gettraceback.py
├── README.md
```

---

## License

FlexiLogger is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributions

Contributions are welcome! Feel free to open an issue or submit a pull request.
