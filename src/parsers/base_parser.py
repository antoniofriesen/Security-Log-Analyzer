"""Abstract base class and shared contract for all log parsers."""

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Abstract base class defining the required interface for all log parsers."""

    @abstractmethod
    def parse_line(self, line: str) -> dict | None:
        """Parse a single raw log line into a structured entry.

        Args:
            line: Raw log line string.

        Returns:
            Parsed entry as dict, or None if the line is invalid/skipped.
        """


    def parse_file(self, path: Path) -> Iterator[dict]:
        """Read a log file line by line and yield parsed entries.

        Args:
            path: Path to the log file.

        Yields:
            One parsed entry (dict) per valid line, in order.
        """

        with open(path, encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                parsed_entry = self.parse_line(line)
                if isinstance(parsed_entry, dict):
                    yield parsed_entry
                elif parsed_entry is None:
                    logger.warning("line_number=%s path=%s line=%s", line_number, path, line.rstrip())