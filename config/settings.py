import os
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings loaded from environment variables."""
    model_name: str
    orchestrator_model_name: str
    how_many_searches: int
    session_type: str
    session_name: str
    trace_workflow_name: str

    @classmethod
    def load(cls):
        """Load settings from environment variables with defaults."""
        load_dotenv(override=True)
        return cls(
            model_name=os.getenv("MODEL_NAME", "gpt-5.4-mini"),
            orchestrator_model_name=os.getenv("ORCHESTRATOR_MODEL", "gpt-5.5"),
            how_many_searches=int(os.getenv("HOW_MANY_SEARCHES", "5")),
            # TODO(T5.1): session_type is currently unused; consumed when the
            # persistent-session workflow lands.
            session_type=os.getenv("SESSION_TYPE", "memory"),
            session_name=os.getenv("SESSION_NAME", "nelle"),
            trace_workflow_name=os.getenv("TRACE_WORKFLOW_NAME", "Nelle"),
        )


def get_settings() -> Settings:
    """Get application settings."""
    return Settings.load()


def get_model_name() -> str:
    """Return the configured model name.

    Single source of truth for MODEL_NAME lookups so agent factories do not
    duplicate environment variable lookups.
    """
    return get_settings().model_name


def get_orchestrator_model_name() -> str:
    """Return the model to use for the routing orchestrator.

    Defaults to a stronger model than sub-agents because routing quality
    depends on the orchestrator picking the right tool the first time.
    """
    return get_settings().orchestrator_model_name
