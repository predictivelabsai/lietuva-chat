"""Remote mode: the chat wrappers talking to a real MCP server process over streamable HTTP.
Only inputs that are refused before any upstream call are used, so no network is needed."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def server_url():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    env = {**os.environ, "MCP_HOST": "127.0.0.1", "MCP_PORT": str(port), "MCP_ANON_RPM": "1000"}
    proc = subprocess.Popen([sys.executable, "-m", "mcp_server", "--transport", "http"], cwd=ROOT, env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1).read()
                break
            except OSError:
                time.sleep(0.1)
        else:
            pytest.fail("MCP server did not start")
        yield f"http://127.0.0.1:{port}/mcp"
    finally:
        proc.terminate()
        proc.wait(timeout=10)


async def test_remote_tool_error_follows_the_same_policy(server_url, monkeypatch):
    monkeypatch.setenv("LIETUVA_MCP_URL", server_url)
    from tools.mcp_tools import company_details
    out = json.loads(await company_details.ainvoke({"company_code": "38001010000"}))
    assert "7 to 9 digits" in out["error"] and "web_search" not in out["error"]
    assert "38001010000" not in out["error"]


async def test_remote_bad_input_is_reported_not_raised(server_url, monkeypatch):
    monkeypatch.setenv("LIETUVA_MCP_URL", server_url)
    from tools.mcp_tools import law_consolidated
    out = json.loads(await law_consolidated.ainvoke({"document_id": "TAR.C677663D2202", "on_date": "13/10/2026"}))
    assert "2026-10-13" in out["error"] and "web_search" in out["error"]
