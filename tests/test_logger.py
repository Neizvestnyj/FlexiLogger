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


def test_logger_json_binding(tmp_path):
    log_file = tmp_path / "test_json_bind.log"
    logger = Logger("JSONBindLogger", log_file_path=str(log_file), json_format=True)

    # 1. Bind context
    bound_logger = logger.bind(request_id="123", user="alice")
    bound_logger.info("User login")

    # 2. Chain bind
    deep_logger = bound_logger.bind(action="delete", item_id=99)
    deep_logger.warning("Dangerous action")

    # 3. Regular log should not have context
    logger.error("System error")

    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 3

        # Check first log (bound)
        log1 = json.loads(lines[0])
        assert log1["message"] == "User login"
        assert log1["request_id"] == "123"
        assert log1["user"] == "alice"

        # Check second log (chained)
        log2 = json.loads(lines[1])
        assert log2["message"] == "Dangerous action"
        assert log2["request_id"] == "123"  # Inherited
        assert log2["action"] == "delete"

        # Check third log (original logger)
        log3 = json.loads(lines[2])
        assert log3["message"] == "System error"
        assert "request_id" not in log3


def test_logger_rotation(tmp_path):
    log_file = tmp_path / "rotate.log"
    logger = Logger("RotateLogger", log_file_path=str(log_file), max_bytes=50, backup_count=2)

    for i in range(10):
        logger.info(f"Message {i} " * 5)

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
        assert "Caught zero division" in content
        assert "in line -" in content


def test_timezone_parsing():
    logger = Logger("UTCLogger", timezone="UTC")
    assert logger._tz_object == datetime.timezone.utc


def test_parse_timezone_func():
    assert _parse_timezone("UTC") == datetime.timezone.utc
    assert _parse_timezone(None) == datetime.timezone.utc
    assert _parse_timezone("LOCAL") is None

    tz_plus_3 = _parse_timezone("UTC+3")
    assert tz_plus_3 is not None
    assert tz_plus_3.utcoffset(None) == datetime.timedelta(hours=3)
