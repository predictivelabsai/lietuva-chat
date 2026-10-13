"""The chat's web_search never sends a personal code to the search provider."""

from tools.search import web_search


def test_personal_code_never_reaches_the_search_provider():
    out = web_search.invoke({"query": "mano asmens kodas 38001010000 deklaracija"})
    assert "personal code" in out and "38001010000" not in out


def test_ordinary_numbers_are_fine():
    from mcp_server.uapi import refuse_personal_code
    assert refuse_personal_code("company 302767152, VAT LT100006918914, 2026 m.")
