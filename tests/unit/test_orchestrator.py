from custom_agents.orchestrator import create_orchestrator_agent


def test_orchestrator_exposes_expected_tools():
    # Planner is not exposed — it's an internal step inside run_research.
    agent = create_orchestrator_agent()
    tool_names = {t.name for t in agent.tools}
    assert tool_names == {"answer", "web_search", "run_research"}
