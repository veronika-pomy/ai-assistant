from agents import SQLiteSession


class SessionManager:
    """Manages conversation sessions using SQLiteSession.

    This wrapper provides a clean interface for session management
    and abstracts the underlying session implementation.
    """

    def __init__(self, name: str, storage: str = ":memory:"):
        """Initialize session manager.

        Args:
            name: Session name/identifier
            storage: Storage location (":memory:" for in-memory, or file path)
        """
        self.name = name
        self.storage = storage
        self._session = SQLiteSession(name, storage)

    def get_session(self) -> SQLiteSession:
        """Get the underlying session instance.

        Returns:
            SQLiteSession instance
        """
        return self._session

    def clear(self):
        """Clear session history (future implementation)."""
        # Future: implement session clearing
        pass

    def __repr__(self) -> str:
        return f"SessionManager(name='{self.name}', storage='{self.storage}')"
