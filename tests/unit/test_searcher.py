"""Tests for the searcher agent's structured output."""

import pytest

from custom_agents.searcher import SearchSummary, create_searcher_agent


class TestSearchSummaryModel:
    """Round-trip the SearchSummary pydantic model."""

    def test_construct_with_fields(self):
        s = SearchSummary(query="latest LLMs", summary="Two paragraphs.")
        assert s.query == "latest LLMs"
        assert s.summary == "Two paragraphs."

    def test_json_round_trip(self):
        s = SearchSummary(query="q", summary="body")
        parsed = SearchSummary.model_validate_json(s.model_dump_json())
        assert parsed == s

    def test_missing_field_rejected(self):
        with pytest.raises(Exception):
            SearchSummary(query="only")  # summary is required


class TestSearcherFactory:
    """Smoke test the searcher agent factory."""

    def test_factory_returns_agent(self):
        agent = create_searcher_agent()
        assert agent is not None
        assert agent.name == "Searcher"

    def test_factory_wires_search_summary_output(self):
        agent = create_searcher_agent()
        assert agent.output_type is SearchSummary

    def test_factory_wires_web_search_tool(self):
        agent = create_searcher_agent()
        assert len(agent.tools) == 1

    def test_factory_honors_model_override(self):
        agent = create_searcher_agent(model="test-model-x")
        assert agent.model == "test-model-x"
