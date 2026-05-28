"""Anexus MCP Server — verify AI Agent identity from any MCP-compatible client.

Usage (Claude Code / Codex / Cursor):
    Add to your MCP config:
    {
        "mcpServers": {
            "anexus": {
                "command": "python",
                "args": ["-m", "anexus_mcp.server"]
            }
        }
    }

Usage (direct):
    pip install git+https://github.com/Marsssssssssssdsss/nexus6-sdk.git#subdirectory=python
    python -m anexus_mcp.server
"""

import httpx
from mcp.server.fastmcp import FastMCP

ANEXUS_BASE_URL = "https://nexus-7xp6n.ondigitalocean.app"

mcp = FastMCP(
    "Anexus Identity",
    instructions=(
        "Verify any AI Agent's identity by their Agent ID. "
        "Use verify_identity to check if an agent is legitimate, "
        "and get_agent_info to look up an agent's public profile."
    )
)


@mcp.tool()
async def verify_identity(agent_id: str) -> str:
    """Verify an AI Agent's identity.

    Args:
        agent_id: The agent's identity token (format: nxs6_xxxxxxxxxx)

    Returns:
        Verification result with agent details if valid
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{ANEXUS_BASE_URL}/api/v1/identity/verify",
            json={"api_key": agent_id.strip()}
        )
        result = resp.json()

    if result.get("verified"):
        return (
            f"✅ Verified\n"
            f"Agent ID: {result.get('id', 'N/A')}\n"
            f"Name: {result.get('name', 'N/A')}\n"
            f"Type: {result.get('ai_type', 'N/A')}\n"
            f"Role: {result.get('role', 'N/A')}"
        )

    return f"❌ Verification failed\nReason: {result.get('error', 'unknown error')}"


@mcp.tool()
async def get_agent_info(agent_id: str) -> str:
    """Get an AI Agent's public information.

    Args:
        agent_id: The agent's internal ID (format: ai_xxxxxxxx)

    Returns:
        Public profile of the agent
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{ANEXUS_BASE_URL}/api/ai/{agent_id.strip()}"
        )
        agent = resp.json()

    if not agent or agent.get("error"):
        return f"Agent not found: {agent_id}"

    return (
        f"Name: {agent.get('name', 'N/A')}\n"
        f"Type: {agent.get('ai_type', 'N/A')}\n"
        f"Status: {agent.get('verification_status', 'unknown')}\n"
        f"Description: {agent.get('description', '') or ''}\n"
        f"Agent ID: {agent_id}"
    )


if __name__ == "__main__":
    print("Starting Anexus Identity MCP Server...")
    print(f"Backend: {ANEXUS_BASE_URL}")
    print("Tools available: verify_identity, get_agent_info")
    mcp.run()