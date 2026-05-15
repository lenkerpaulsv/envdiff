"""Tests for envdiff.parser module."""

import os
import tempfile
import pytest

from envdiff.parser import parse_env_string, parse_env_file, _strip_quotes


class TestStripQuotes:
    def test_strips_double_quotes(self):
        assert _strip_quotes('"hello"') == 'hello'

    def test_strips_single_quotes(self):
        assert _strip_quotes("'world'") == 'world'

    def test_no_quotes_unchanged(self):
        assert _strip_quotes('plain') == 'plain'

    def test_mismatched_quotes_unchanged(self):
        assert _strip_quotes('"mixed\'') == '"mixed\''

    def test_empty_string(self):
        assert _strip_quotes('') == ''


class TestParseEnvString:
    def test_simple_key_value(self):
        result = parse_env_string('FOO=bar')
        assert result == {'FOO': 'bar'}

    def test_multiple_entries(self):
        content = 'FOO=bar\nBAZ=qux'
        result = parse_env_string(content)
        assert result == {'FOO': 'bar', 'BAZ': 'qux'}

    def test_ignores_comments(self):
        content = '# This is a comment\nFOO=bar'
        result = parse_env_string(content)
        assert result == {'FOO': 'bar'}

    def test_ignores_blank_lines(self):
        content = '\n\nFOO=bar\n\n'
        result = parse_env_string(content)
        assert result == {'FOO': 'bar'}

    def test_quoted_value(self):
        result = parse_env_string('SECRET="my secret value"')
        assert result == {'SECRET': 'my secret value'}

    def test_single_quoted_value(self):
        result = parse_env_string("TOKEN='abc123'")
        assert result == {'TOKEN': 'abc123'}

    def test_empty_value(self):
        result = parse_env_string('EMPTY=')
        assert result == {'EMPTY': ''}

    def test_value_with_equals_sign(self):
        result = parse_env_string('URL=http://example.com?foo=bar')
        assert result == {'URL': 'http://example.com?foo=bar'}

    def test_spaces_around_equals(self):
        result = parse_env_string('FOO = bar')
        assert result == {'FOO': 'bar'}

    def test_invalid_line_skipped(self):
        content = 'NOT-VALID\nFOO=bar'
        result = parse_env_string(content)
        assert result == {'FOO': 'bar'}


class TestParseEnvFile:
    def test_reads_file(self, tmp_path):
        env_file = tmp_path / '.env'
        env_file.write_text('FOO=bar\nBAZ=123\n')
        result = parse_env_file(str(env_file))
        assert result == {'FOO': 'bar', 'BAZ': '123'}

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            parse_env_file('/nonexistent/path/.env')
