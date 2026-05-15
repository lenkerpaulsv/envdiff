"""Parser module for reading and parsing .env files."""

import os
import re
from typing import Dict, Optional, Tuple


ENV_LINE_PATTERN = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
)
COMMENT_PATTERN = re.compile(r'^\s*#.*$')


def _strip_quotes(value: str) -> str:
    """Strip surrounding single or double quotes from a value."""
    if len(value) >= 2:
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
    return value


def parse_env_string(content: str) -> Dict[str, str]:
    """Parse a .env file content string into a key-value dictionary.

    Args:
        content: Raw string content of a .env file.

    Returns:
        Dictionary mapping environment variable names to their values.
    """
    result: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or COMMENT_PATTERN.match(line):
            continue
        match = ENV_LINE_PATTERN.match(line)
        if match:
            key = match.group('key')
            value = _strip_quotes(match.group('value').strip())
            result[key] = value
    return result


def parse_env_file(filepath: str) -> Dict[str, str]:
    """Read and parse a .env file from disk.

    Args:
        filepath: Path to the .env file.

    Returns:
        Dictionary mapping environment variable names to their values.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If the file cannot be read.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Env file not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return parse_env_string(content)
