"""Test the abstract base class and shared contract for all log parsers."""

from unittest.mock import mock_open, patch
from src.parsers.base_parser import BaseParser


class DummyParser(BaseParser):
    """Dummy parser for testing."""

    def parse_line(self, line: str) -> dict | None:
        """Parse a log line and return a dict with parsed data.

        Args:
            line: Raw log line string.

        Returns:
            Parsed entry as dict, or None if the line is invalid/skipped.
        """

        if line.startswith("GET"):
            return {"method": "GET", "line": line}
        else:
            return None

def test_base_parser(caplog):
    """Test the abstract base class and shared contract for all log parsers."""
    fake_content = "GET /index.html\nPOST /login\n"

    with patch("builtins.open", mock_open(read_data=fake_content)):
        parser = DummyParser()
        results = list(parser.parse_file("fake.log"))
        assert results == [{"method": "GET", "line": "GET /index.html\n"}]
        assert "POST /login" in caplog.text