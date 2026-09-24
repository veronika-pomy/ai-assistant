"""Tests for task manager orchestration."""

import pytest
from core.task_manager import TaskManager, TaskType


class TestTaskTypeDetection:
    """Test task type classification from queries."""

    @pytest.mark.asyncio
    async def test_detect_research_task_with_research_keywords(self):
        """Verify 'research' keyword triggers research type."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("research AI frameworks")
        assert task_type == TaskType.RESEARCH

    @pytest.mark.asyncio
    async def test_detect_research_task_with_find_keywords(self):
        """Verify 'find out about' triggers research type."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("find out about Python")
        assert task_type == TaskType.RESEARCH

    @pytest.mark.asyncio
    async def test_detect_research_task_with_investigate_keyword(self):
        """Verify 'investigate' triggers research type."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("investigate market trends")
        assert task_type == TaskType.RESEARCH

    @pytest.mark.asyncio
    async def test_detect_research_task_with_search_keyword(self):
        """Verify 'search for' triggers research type."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("search for latest news")
        assert task_type == TaskType.RESEARCH

    @pytest.mark.asyncio
    async def test_detect_planning_task_with_plan_keyword(self):
        """Verify 'plan' keyword triggers planning type."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("plan my vacation")
        assert task_type == TaskType.PLANNING

    @pytest.mark.asyncio
    async def test_detect_planning_task_with_steps_keyword(self):
        """Verify 'steps to' triggers planning type."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("steps to learn Python")
        assert task_type == TaskType.PLANNING

    @pytest.mark.asyncio
    async def test_detect_planning_task_with_how_to_keyword(self):
        """Verify 'how to' triggers planning type."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("how to build a website")
        assert task_type == TaskType.PLANNING

    @pytest.mark.asyncio
    async def test_detect_planning_task_with_roadmap_keyword(self):
        """Verify 'roadmap' triggers planning type."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("roadmap for learning")
        assert task_type == TaskType.PLANNING

    @pytest.mark.asyncio
    async def test_detect_creative_task_with_design_keyword(self):
        """Verify 'design' keyword triggers creative type."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("design a distributed cache")
        assert task_type == TaskType.CREATIVE

    @pytest.mark.asyncio
    async def test_detect_creative_task_with_architect_keyword(self):
        """Verify 'architect' triggers creative type."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("architect a system")
        assert task_type == TaskType.CREATIVE

    @pytest.mark.asyncio
    async def test_detect_creative_task_with_create_keyword(self):
        """Verify 'create' triggers creative type."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("create a solution")
        assert task_type == TaskType.CREATIVE

    @pytest.mark.asyncio
    async def test_detect_creative_task_with_approach_keyword(self):
        """Verify 'approach to' triggers creative type."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("approach to problem solving")
        assert task_type == TaskType.CREATIVE

    @pytest.mark.asyncio
    async def test_detect_direct_task_simple_question(self):
        """Verify simple questions default to direct type."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("What is 5 + 5?")
        assert task_type == TaskType.DIRECT

    @pytest.mark.asyncio
    async def test_detect_direct_task_no_keywords(self):
        """Verify queries with no keywords default to direct."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("Tell me a joke")
        assert task_type == TaskType.DIRECT

    @pytest.mark.asyncio
    async def test_detect_direct_task_simple_statement(self):
        """Verify simple statements default to direct."""
        manager = TaskManager()
        task_type = await manager._analyze_task_type("Explain quantum computing")
        assert task_type == TaskType.DIRECT

    @pytest.mark.asyncio
    async def test_task_detection_case_insensitive(self):
        """Verify task detection is case insensitive."""
        manager = TaskManager()
        task_type1 = await manager._analyze_task_type("RESEARCH AI")
        task_type2 = await manager._analyze_task_type("research ai")
        task_type3 = await manager._analyze_task_type("Research AI")
        assert task_type1 == task_type2 == task_type3 == TaskType.RESEARCH


class TestTaskManagerInitialization:
    """Test task manager setup."""

    def test_task_manager_creates_successfully(self):
        """Verify TaskManager can be instantiated."""
        manager = TaskManager()
        assert manager is not None

    def test_task_manager_has_settings(self):
        """Verify TaskManager loads settings."""
        manager = TaskManager()
        assert hasattr(manager, 'settings')
        assert manager.settings is not None

    def test_task_manager_has_run_method(self):
        """Verify TaskManager has run method."""
        manager = TaskManager()
        assert hasattr(manager, 'run')
        assert callable(manager.run)


class TestTaskTypeEnum:
    """Test TaskType enum values."""

    def test_task_type_enum_has_research(self):
        """Verify TaskType has RESEARCH value."""
        assert TaskType.RESEARCH is not None
        assert TaskType.RESEARCH.value == "research"

    def test_task_type_enum_has_planning(self):
        """Verify TaskType has PLANNING value."""
        assert TaskType.PLANNING is not None
        assert TaskType.PLANNING.value == "planning"

    def test_task_type_enum_has_creative(self):
        """Verify TaskType has CREATIVE value."""
        assert TaskType.CREATIVE is not None
        assert TaskType.CREATIVE.value == "creative"

    def test_task_type_enum_has_direct(self):
        """Verify TaskType has DIRECT value."""
        assert TaskType.DIRECT is not None
        assert TaskType.DIRECT.value == "direct"

    def test_task_type_enum_all_values_unique(self):
        """Verify all TaskType values are unique."""
        values = [t.value for t in TaskType]
        assert len(values) == len(set(values))
