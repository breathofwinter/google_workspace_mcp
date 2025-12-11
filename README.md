# MCP workspace

This repository now uses a layout that keeps each MCP server isolated so you can add more servers alongside the existing Google Workspace implementation.

## Structure
- `servers/google_workspace/` – the Google Workspace MCP server (code, Docker/Compose files, packaging metadata, and documentation)
- `clients/agents_repl/` – a simple FastMCP-based REPL client you can point at any MCP server endpoint

## Google Workspace MCP server
Change into the server directory before running commands so all paths resolve correctly:

```bash
cd servers/google_workspace
```

From there, follow the server README for setup and deployment details, including the Docker and Docker Compose options.

## Sample client
Run the sample client from the repository root (or adjust the path if you are elsewhere):

```bash
python clients/agents_repl/client.py
```

Configure the client with `MCP_SERVER_URL` and, if needed, `MCP_BEARER_TOKEN` to target the server instance you want to test.
