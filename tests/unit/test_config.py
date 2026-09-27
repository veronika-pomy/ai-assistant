"""Tests for configuration module."""

import os
import pytest
from config.settings import get_settings, get_model_name, Settings


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
        assert hasattr(settings, 'how_many_searches')
        assert hasattr(settings, 'session_type')

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

    def test_how_many_searches_is_positive_int(self):
        """HOW_MANY_SEARCHES must parse as a positive int."""
        settings = get_settings()
        assert isinstance(settings.how_many_searches, int)
        assert settings.how_many_searches > 0


class TestGetModelName:
    """Tests for the get_model_name() helper."""

    def test_get_model_name_returns_string(self):
        assert isinstance(get_model_name(), str)

    def test_get_model_name_matches_settings(self):
        assert get_model_name() == get_settings().model_name

    def test_get_model_name_honors_env_override(self, monkeypatch):
        # Prevent Settings.load from re-reading .env and clobbering the override.
        monkeypatch.setattr("config.settings.load_dotenv", lambda **_: None)
        monkeypatch.setenv("MODEL_NAME", "test-model-xyz")
        assert get_model_name() == "test-model-xyz"


class TestHowManySearchesWiring:
    """Verify HOW_MANY_SEARCHES actually reaches the planner schema."""

    def test_planner_schema_matches_configured_n(self, monkeypatch):
        monkeypatch.setattr("config.settings.load_dotenv", lambda **_: None)
        monkeypatch.setenv("HOW_MANY_SEARCHES", "3")
        from custom_agents.planner import build_search_plan_model

        model = build_search_plan_model(get_settings().how_many_searches)
        constraints = model.model_fields["searches"].metadata
        min_len = next(getattr(c, "min_length", None) for c in constraints
                       if getattr(c, "min_length", None) is not None)
        max_len = next(getattr(c, "max_length", None) for c in constraints
                       if getattr(c, "max_length", None) is not None)
        assert min_len == 3
        assert max_len == 3

    def test_planner_factory_uses_settings_by_default(self, monkeypatch):
        monkeypatch.setattr("config.settings.load_dotenv", lambda **_: None)
        monkeypatch.setenv("HOW_MANY_SEARCHES", "4")
        from custom_agents.planner import create_planner_agent

        agent = create_planner_agent()
        assert "exactly 4" in agent.instructions
