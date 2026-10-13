"""Shared pytest configuration."""

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def pytest_addoption(parser):
    parser.addoption(
        "--run-integration", action="store_true", default=False,
        help="Run integration tests that hit real APIs (Postmark, DB)",
    )


@pytest.fixture
def mcp_upstream(monkeypatch):
    """Point the MCP server's HTTP client at recorded responses.
    Call it with {url substring: fixture file or status}; it returns the Upstream."""
    import httpx

    from mcp_server import config, core
    from tests.mcp_upstream import Upstream

    monkeypatch.delenv("EXA_API_KEY", raising=False)
    monkeypatch.delenv("LIETUVA_MCP_URL", raising=False)
    config.mcp_settings.cache_clear()
    core.reset()

    def install(routes):
        fake = Upstream(routes)
        core.set_transport(httpx.MockTransport(fake))
        return fake

    yield install
    core.set_transport(None)
    core.reset()
    config.mcp_settings.cache_clear()
