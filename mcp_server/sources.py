"""Every MCP tool by name. The server registers these; tools/mcp_tools.py calls them in-process."""

from mcp_server.companies import company_details, company_search, company_tax_data
from mcp_server.laws import law_consolidated, law_search
from mcp_server.rates import exchange_rate
from mcp_server.web import gov_web_search

TOOL_FUNCS = {f.__name__: f for f in (
    company_search, company_details, company_tax_data, law_search, law_consolidated, exchange_rate,
    gov_web_search)}
