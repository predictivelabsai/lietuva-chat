"""Fake upstream for MCP tool tests: serves recorded responses through httpx.MockTransport."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote

import httpx

FIXTURES = Path(__file__).parent / "mcp_fixtures"


class Upstream:
    """Answers each request with the first route whose key is a substring of the decoded URL.
    A route value is a fixture filename (200) or an int status. Unmatched URLs get 404."""

    def __init__(self, routes: dict[str, str | int]):
        self.routes = routes
        self.requests: list[httpx.Request] = []

    @property
    def urls(self) -> list[str]:
        return [unquote(str(r.url)) for r in self.requests]

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        url = unquote(str(request.url))
        for needle, answer in self.routes.items():
            if needle in url:
                if isinstance(answer, int):
                    return httpx.Response(answer)
                return httpx.Response(200, content=(FIXTURES / answer).read_bytes())
        return httpx.Response(404, json={"errors": [{"message": f"no fixture for {url}"}]})
