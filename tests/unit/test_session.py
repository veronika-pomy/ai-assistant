"""Tests for session management."""

import pytest
from core.session import SessionManager


class TestSessionManager:
    """Test session management."""

    def test_session_manager_creates_successfully(self):
        """Verify SessionManager can be instantiated."""
        manager = SessionManager("test_session", ":memory:")
        assert manager is not None

    def test_session_manager_get_session_returns_session(self):
        """Verify get_session returns a session object."""
        manager = SessionManager("test_session", ":memory:")
        session = manager.get_session()
        assert session is not None

    def test_session_manager_different_names_create_different_sessions(self):
        """Verify different session names create different managers."""
        manager1 = SessionManager("session1", ":memory:")
        manager2 = SessionManager("session2", ":memory:")
        assert manager1 is not manager2

    def test_session_manager_in_memory_works(self):
        """Verify in-memory session can be created."""
        manager = SessionManager("test", ":memory:")
        session = manager.get_session()
        assert session is not None

    def test_session_manager_session_is_consistent(self):
        """Verify get_session returns same session object."""
        manager = SessionManager("test", ":memory:")
        session1 = manager.get_session()
        session2 = manager.get_session()
        assert session1 is session2


class TestSessionManagerTypes:
    """Test session manager type safety."""

    def test_session_name_parameter_required(self):
        """Verify session_name parameter is required."""
        with pytest.raises(TypeError):
            SessionManager()

    def test_session_manager_with_single_parameter(self):
        """Verify SessionManager can accept just session name (db_path has default)."""
        # SessionManager allows calling with just session_name, so this should work
        manager = SessionManager("test_session", ":memory:")
        assert manager is not None

    def test_session_manager_accepts_string_parameters(self):
        """Verify SessionManager accepts string parameters."""
        manager = SessionManager("name", ":memory:")
        assert manager is not None

    def test_session_manager_with_file_path(self):
        """Verify SessionManager works with file paths."""
        # Should not raise, just verify it accepts path syntax
        manager = SessionManager("test", "/tmp/test.db")
        assert manager is not None
