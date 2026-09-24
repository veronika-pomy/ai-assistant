"""Tests for module imports and structure."""

import pytest


class TestCoreImports:
    """Test core module imports."""

    def test_import_task_manager(self):
        """Verify TaskManager can be imported."""
        from core.task_manager import TaskManager
        assert TaskManager is not None

    def test_import_task_type(self):
        """Verify TaskType enum can be imported."""
        from core.task_manager import TaskType
        assert TaskType is not None

    def test_import_session_manager(self):
        """Verify SessionManager can be imported."""
        from core.session import SessionManager
        assert SessionManager is not None

    def test_import_streaming_ui(self):
        """Verify StreamingUI can be imported."""
        from core.streaming import StreamingUI
        assert StreamingUI is not None


class TestConfigImports:
    """Test config module imports."""

    def test_import_settings(self):
        """Verify Settings can be imported."""
        from config.settings import Settings
        assert Settings is not None

    def test_import_get_settings(self):
        """Verify get_settings function can be imported."""
        from config.settings import get_settings
        assert get_settings is not None
        assert callable(get_settings)


class TestUIImports:
    """Test UI module imports."""

    def test_import_show_welcome(self):
        """Verify show_welcome can be imported."""
        from ui.banner import show_welcome
        assert show_welcome is not None
        assert callable(show_welcome)

    def test_import_prompt_user(self):
        """Verify prompt_user can be imported."""
        from ui.prompts import prompt_user
        assert prompt_user is not None
        assert callable(prompt_user)

    def test_import_is_exit_command(self):
        """Verify is_exit_command can be imported."""
        from ui.prompts import is_exit_command
        assert is_exit_command is not None
        assert callable(is_exit_command)

    def test_import_format_markdown_report(self):
        """Verify format_markdown_report can be imported."""
        from ui.formatters import format_markdown_report
        assert format_markdown_report is not None
        assert callable(format_markdown_report)

    def test_import_show_error(self):
        """Verify show_error can be imported."""
        from ui.formatters import show_error
        assert show_error is not None
        assert callable(show_error)


class TestCustomAgentImports:
    """Test custom agent imports."""

    def test_import_create_solver_agent(self):
        """Verify create_solver_agent can be imported."""
        from custom_agents.solver import create_solver_agent
        assert create_solver_agent is not None
        assert callable(create_solver_agent)

    def test_import_create_planner_agent(self):
        """Verify create_planner_agent can be imported."""
        from custom_agents.planner import create_planner_agent
        assert create_planner_agent is not None
        assert callable(create_planner_agent)

    def test_import_search_plan(self):
        """Verify SearchPlan can be imported."""
        from custom_agents.planner import SearchPlan
        assert SearchPlan is not None

    def test_import_create_searcher_agent(self):
        """Verify create_searcher_agent can be imported."""
        from custom_agents.searcher import create_searcher_agent
        assert create_searcher_agent is not None
        assert callable(create_searcher_agent)

    def test_import_create_writer_agent(self):
        """Verify create_writer_agent can be imported."""
        from custom_agents.writer import create_writer_agent
        assert create_writer_agent is not None
        assert callable(create_writer_agent)

    def test_import_report(self):
        """Verify Report can be imported."""
        from custom_agents.writer import Report
        assert Report is not None


class TestToolImports:
    """Test tool module imports."""

    def test_import_get_web_search_tool(self):
        """Verify get_web_search_tool can be imported."""
        from tools.web_search import get_web_search_tool
        assert get_web_search_tool is not None
        assert callable(get_web_search_tool)

    def test_import_base_tool(self):
        """Verify BaseTool can be imported."""
        from tools.base import BaseTool
        assert BaseTool is not None


class TestModuleStructure:
    """Test module structure and organization."""

    def test_all_core_modules_exist(self):
        """Verify all core modules can be imported."""
        import core
        assert hasattr(core, 'task_manager')
        assert hasattr(core, 'session')
        assert hasattr(core, 'streaming')

    def test_all_ui_modules_exist(self):
        """Verify all UI modules can be imported."""
        import ui
        assert hasattr(ui, 'banner')
        assert hasattr(ui, 'prompts')
        assert hasattr(ui, 'formatters')

    def test_all_custom_agent_modules_exist(self):
        """Verify all custom agent modules can be imported."""
        import custom_agents
        assert hasattr(custom_agents, 'solver')
        assert hasattr(custom_agents, 'planner')
        assert hasattr(custom_agents, 'searcher')
        assert hasattr(custom_agents, 'writer')

    def test_all_tool_modules_exist(self):
        """Verify all tool modules can be imported."""
        import tools
        assert hasattr(tools, 'base')
        assert hasattr(tools, 'web_search')

    def test_config_module_exists(self):
        """Verify config module can be imported."""
        import config
        assert hasattr(config, 'settings')
