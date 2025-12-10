"""
Minimal OpenAI Agents REPL for the Workspace MCP server (streamable HTTP).

Connects to an already-running Workspace MCP server—perfect for Docker/
Compose setups that publish the HTTP transport on port 8000. The default URL is
``http://localhost:8000/mcp`` (matching ``docker compose up``), but you can
override it with ``MCP_SERVER_URL``.
"""

import asyncio
import os
import sys
from typing import Final

from dotenv import load_dotenv

load_dotenv()

try:
    import agents
    from agents import Agent, OpenAIResponsesModel
    from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
    from agents.repl import run_demo_loop
    from openai import APIError, AsyncOpenAI

except ImportError:
    sys.exit(
        "The 'openai-agents' package is required. Install it with:\n"
        "  pip install openai-agents"
    )

API_KEY: Final[str | None] = os.environ.get("OPENAI_API_KEY")
SERVER_URL: Final[str] = os.environ.get("MCP_SERVER_URL", "http://localhost:8000/mcp")
BEARER_TOKEN: Final[str | None] = os.environ.get("MCP_BEARER_TOKEN")

if not API_KEY:
    sys.exit("Set OPENAI_API_KEY before running this script.")

async def main() -> None:
    client = AsyncOpenAI(api_key=API_KEY)

    server_params: MCPServerStreamableHttpParams = {
        "url": SERVER_URL,
    }

    if BEARER_TOKEN:
        server_params["headers"] = {"Authorization": f"Bearer {BEARER_TOKEN}"}

    server = MCPServerStreamableHttp(server_params, name="workspace-mcp")
    await server.connect()

    agent = Agent(
        name="workspace-mcp",
        instructions="Use the MCP tools to help with Google Workspace tasks.",
        model=OpenAIResponsesModel("gpt-4.1-mini", openai_client=client),
        mcp_servers=[server],
    )

    print("Type a prompt (Ctrl+C to exit)")
    try:
        await run_demo_loop(agent, stream=True)
    except APIError as err:
        message = str(err)
        if "Error retrieving tool list" in message and getattr(err, "status_code", None) == 424:
            print(
                "\nThe MCP server failed to respond over streamable HTTP. Ensure the container "
                "is running on the expected port and your URL/headers are correct."
            )
        else:
            print(f"\nOpenAI API error: {message}")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
    finally:
        await server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
