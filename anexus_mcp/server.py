"""Anexus MCP Server — AI Identity Verification via MCP

Let Claude, Codex, Cursor and other AI tools verify AI Agent identities through the MCP protocol.

Dependencies:
    pip install mcp httpx

Usage (Cursor):
    Add the following MCP Server in Cursor settings:
    {
        "mcpServers": {
            "anexus": {
                "command": "python",
                "args": ["-m", "anexus_mcp.server"]
            }
        }
    }

Usage (Claude Desktop):
    Add the following in claude_desktop_config.json:
    {
        "mcpServers": {
            "anexus": {
                "command": "python",
                "args": ["-m", "anexus_mcp.server"]
            }
        }
    }
"""

import httpx
from mcp.server.fastmcp import FastMCP

ANEXUS_BASE_URL = "https://nexus-7xp6n.ondigitalocean.app"

mcp = FastMCP("Anexus Identity", instructions="Anexus AI Identity Verification — verify any AI Agent's identity")


@mcp.tool()
async def verify_identity(api_key: str) -> str:
    """Verify an AI Agent's identity.

    Args:
        api_key: The AI Agent's API Key (format: nxs6_xxxxxxxxxx)

    Returns:
        JSON string containing verification result and identity info
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{ANEXUS_BASE_URL}/api/v1/identity/verify",
            json={"api_key": api_key}
        )
        result = resp.json()

    if result.get("verified"):
        return (
            f"Verified\n"
            f"Agent ID: {result.get('id', 'N/A')}\n"
            f"Name: {result.get('name', 'N/A')}\n"
            f"Type: {result.get('ai_type', 'N/A')}\n"
            f"Role: {result.get('role', 'N/A')}"
        )
    else:
        return f"Verification failed\nReason: {result.get('error', 'unknown error')}"


@mcp.tool()
async def get_agent_info(agent_id: str) -> str:
    """Get an AI Agent's public info.

    Args:
        agent_id: AI Agent ID (format: ai_xxxxxxxx)

    Returns:
        JSON string containing the Agent's public info
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{ANEXUS_BASE_URL}/api/ai/{agent_id}"
        )
        agent = resp.json()

    if not agent or agent.get("error"):
        return f"Agent not found: {agent_id}"

    name = agent.get("name", "N/A")
    ai_type = agent.get("ai_type", "N/A")
    verified = agent.get("verification_status", "unknown")
    desc = agent.get("description", "") or ""

    return (
        f"Name: {name}\n"
        f"Type: {ai_type}\n"
        f"Verification: {verified}\n"
        f"Description: {desc}\n"
        f"Agent ID: {agent_id}"
    )


if __name__ == "__main__":
    mcp.run()