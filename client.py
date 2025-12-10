"""
Minimal OpenAI Agents REPL for the Workspace MCP server (stdio transport).

This example runs the MCP server as a child process over stdio so everything
stays local—no tunnels or public hosting required. It matches the "all-local"
behavior you had when the client and server shared the same container/process.
"""

import asyncio
import os
import sys
from typing import Final

try:
    import agents
    from agents import Agent, OpenAIResponsesModel
    from agents.mcp import MCPServerStdio, MCPServerStdioParams
    from agents.repl import run_demo_loop
    from openai import APIError, AsyncOpenAI
except ImportError:
    sys.exit(
        "The 'openai-agents' package is required. Install it with:\n"
        "  pip install openai-agents"
    )

API_KEY: Final[str | None] = os.environ.get("OPENAI_API_KEY")
SERVER_COMMAND: Final = os.environ.get("MCP_SERVER_COMMAND", "uvx")
SERVER_ARGS: Final = os.environ.get("MCP_SERVER_ARGS", "workspace-mcp --tool-tier core")
GOOGLE_CLIENT_ID: Final[str | None] = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET: Final[str | None] = os.environ.get("GOOGLE_CLIENT_SECRET")

if not API_KEY:
    sys.exit("Set OPENAI_API_KEY before running this script.")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    sys.exit(
        "Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET so the MCP server "
        "can authenticate with Google."
    )


async def main() -> None:
    client = AsyncOpenAI(api_key=API_KEY)

    server_params: MCPServerStdioParams = {
        "command": SERVER_COMMAND,
        "args": SERVER_ARGS.split(),
        "env": {
            **os.environ,
            "GOOGLE_OAUTH_CLIENT_ID": GOOGLE_CLIENT_ID,
            "GOOGLE_OAUTH_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
        },
    }

    server = MCPServerStdio(server_params, name="workspace-mcp")
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
                "\nThe MCP server failed to respond over stdio. Ensure it launches correctly, "
                "your OAuth vars are set, and the command is reachable."
            )
        else:
            print(f"\nOpenAI API error: {message}")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
    finally:
        await server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())