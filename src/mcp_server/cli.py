"""CLI entry point — запуск MCP сервера."""

import argparse
import asyncio
import logging
import sys

from .config import Config
from .client import ServiceNowClient
from .mcp_server import UniversalMCPServer


def main():
    parser = argparse.ArgumentParser(
        description="ServiceNow Universal MCP Server — LLM-agnostic",
    )
    parser.add_argument("--port", type=int, default=8000, help="MCP server port (default: 8000)")
    parser.add_argument("--stdio", action="store_true", help="STDIO mode (for Claude Desktop)")
    parser.add_argument("--sse", action="store_true", help="SSE mode (HTTP)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    # Load config
    try:
        config = Config()
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("Copy .env.example → .env and configure at least one LLM provider.", file=sys.stderr)
        sys.exit(1)

    log = logging.getLogger(__name__)
    log.info("LLM: %s / %s", config.llm.provider, config.llm.model)
    log.info("ServiceNow: %s", config.sn.url)
    log.info("Mode: %s", "STDIO" if args.stdio else "SSE (HTTP)")

    # Build
    sn_client = ServiceNowClient(config.sn)
    server = UniversalMCPServer(sn_client, config)

    # Run
    if args.stdio:
        server.run_stdio()
    else:
        server.run_sse(port=args.port)


if __name__ == "__main__":
    main()
