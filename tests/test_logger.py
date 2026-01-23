import datetime
import json
import os
import sys

# Ensure we can import from src if not installed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from FlexiLogger import GetTraceback, Logger
from FlexiLogger.logger import _parse_timezone


def test_logger_init(tmp_path):
    log_file = tmp_path / "test.log"
    logger = Logger("TestLogger", log_file_path=str(log_file))

    assert logger.name == "TestLogger"
    assert logger.get_log_file_path() == str(log_file)
    assert os.path.exists(log_file)

    logger.info("Test message")

    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Test message" in content
        assert "INFO" in content


def test_logger_json(tmp_path):
    log_file = tmp_path / "test_json.log"
    logger = Logger("JSONLogger", log_file_path=str(log_file), json_format=True)

    logger.info("JSON Info Message")
    logger.warning("JSON Warning Message")

    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) >= 2

        # Parse first line
        log1 = json.loads(lines[0])
        assert log1["level"] == "INFO"
        assert log1["message"] == "JSON Info Message"
        assert log1["logger"] == "JSONLogger"
        assert "timestamp" in log1

        # Parse second line
        log2 = json.loads(lines[1])
        assert log2["level"] == "WARNING"


def test_logger_rotation(tmp_path):
    log_file = tmp_path / "rotate.log"
    # Set very small limit to trigger rotation
    logger = Logger("RotateLogger", log_file_path=str(log_file), max_bytes=50, backup_count=2)

    # Write enough data to trigger rotation
    for i in range(10):
        logger.info(f"Message {i} " * 5)

    # Check if backup files exist
    assert os.path.exists(log_file)
    assert os.path.exists(str(log_file) + ".1")


def test_get_traceback(tmp_path):
    log_file = tmp_path / "traceback.log"
    logger = Logger("TraceLogger", log_file_path=str(log_file))
    tb_handler = GetTraceback(logger)

    try:
        _ = 1 / 0
    except ZeroDivisionError:
        tb_handler.error("Caught zero division", print_full_exception=False)

    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
        # Should contain the message and line number info
        assert "Caught zero division" in content
        assert "in line -" in content


def test_timezone_parsing():
    # Test UTC
    logger = Logger("UTCLogger", timezone="UTC")
    assert logger._tz_object == datetime.timezone.utc


def test_parse_timezone_func():
    assert _parse_timezone("UTC") == datetime.timezone.utc
    assert _parse_timezone(None) == datetime.timezone.utc
    assert _parse_timezone("LOCAL") is None

    tz_plus_3 = _parse_timezone("UTC+3")
    assert tz_plus_3 is not None
    assert tz_plus_3.utcoffset(None) == datetime.timedelta(hours=3)

    tz_minus_5 = _parse_timezone("UTC-05:00")
    assert tz_minus_5 is not None
    assert tz_minus_5.utcoffset(None) == datetime.timedelta(hours=-5)
