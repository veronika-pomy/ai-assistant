"""Tests for configuration module."""

import os
import pytest
from config.settings import get_settings, Settings


class TestSettingsLoading:
    """Test configuration loading from environment."""

    def test_settings_loads_successfully(self):
        """Verify settings can be instantiated."""
        settings = get_settings()
        assert settings is not None
        assert isinstance(settings, Settings)

    def test_settings_has_required_attributes(self):
        """Verify settings has expected attributes."""
        settings = get_settings()
        assert hasattr(settings, 'model_name')
        assert hasattr(settings, 'session_name')

    def test_settings_model_name_not_empty(self):
        """Verify model name is configured."""
        settings = get_settings()
        assert settings.model_name
        assert isinstance(settings.model_name, str)
        assert len(settings.model_name) > 0

    def test_settings_session_name_not_empty(self):
        """Verify session name is configured."""
        settings = get_settings()
        assert settings.session_name
        assert isinstance(settings.session_name, str)

    def test_get_settings_returns_consistent_values(self):
        """Verify get_settings returns consistent values across calls."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1.model_name == settings2.model_name
        assert settings1.session_name == settings2.session_name

    def test_settings_values_are_strings(self):
        """Verify settings values are strings."""
        settings = get_settings()
        assert isinstance(settings.model_name, str)
        assert isinstance(settings.session_name, str)
