"""Tests for snowmeth.agents module."""

import pytest
from snowmeth.agents import clean_json_markdown


class TestUtilities:
    """Test utility functions."""
    
    def test_clean_json_markdown_basic(self):
        """Test basic JSON markdown cleaning."""
        input_text = '```json\n{"test": "value"}\n```'
        expected = '{"test": "value"}'
        assert clean_json_markdown(input_text) == expected
    
    def test_clean_json_markdown_no_markdown(self):
        """Test JSON cleaning when no markdown is present."""
        input_text = '{"test": "value"}'
        expected = '{"test": "value"}'
        assert clean_json_markdown(input_text) == expected
    
    def test_clean_json_markdown_partial_markdown(self):
        """Test JSON cleaning with only start or end markers."""
        # Only start marker
        input_text = '```json\n{"test": "value"}'
        expected = '{"test": "value"}'
        assert clean_json_markdown(input_text) == expected
        
        # Only end marker
        input_text = '{"test": "value"}\n```'
        expected = '{"test": "value"}'
        assert clean_json_markdown(input_text) == expected
    
    def test_clean_json_markdown_whitespace(self):
        """Test JSON cleaning handles whitespace properly."""
        input_text = '  ```json  \n  {"test": "value"}  \n  ```  '
        expected = '{"test": "value"}'
        assert clean_json_markdown(input_text) == expected