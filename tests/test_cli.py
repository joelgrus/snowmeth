"""Tests for CLI functionality."""

import pytest
from click.testing import CliRunner
from snowmeth.cli import cli


class TestCLI:
    """Test CLI commands."""
    
    def test_cli_help(self):
        """Test that CLI help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Snowflake Method writing assistant' in result.output
    
    def test_status_command_no_api_key(self):
        """Test status command works without API key."""
        runner = CliRunner()
        result = runner.invoke(cli, ['status'])
        # Should not crash, even without API key
        assert result.exit_code == 0
        assert 'System Status' in result.output or 'Default model' in result.output
    
    def test_list_command_empty(self):
        """Test list command with no stories."""
        runner = CliRunner()
        result = runner.invoke(cli, ['list'])
        # Should not crash with empty story list
        assert result.exit_code == 0