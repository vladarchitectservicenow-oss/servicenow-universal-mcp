# Copyright (c) 2026 Vlady
# SPDX-License-Identifier: AGPL-3.0-only

"""CLI entry point — запуск MCP сервера."""

import argparse
import logging
import sys

from .config import Config
from .client import ServiceNowClient
from .mcp_server import UniversalMCPServer


def main():
    parser = argparse.ArgumentParser(
        description="ServiceNow Universal MCP Server — LLM-agnostic",
    )
    parser.add_argument(
        "--stdio", action="store_true", help="STDIO mode (for MCP clients)"
    )
    parser.add_argument(
        "--http", action="store_true", help="HTTP mode (JSON-RPC over HTTP)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="HTTP server port (default: 8000)"
    )
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
        print(
            "Copy .env.example → .env and configure at least one LLM provider.",
            file=sys.stderr,
        )
        sys.exit(1)

    log = logging.getLogger(__name__)
    log.info("LLM: %s / %s", config.llm.provider, config.llm.model)
    log.info("ServiceNow: %s", config.sn.url)
    log.info("Mode: %s", "STDIO" if args.stdio else "HTTP")

    # Build
    sn_client = ServiceNowClient(config.sn)
    server = UniversalMCPServer(sn_client, config)

    # Run
    if args.stdio:
        server.run_stdio()
    else:
        server.run_http(port=args.port)


if __name__ == "__main__":
    main()
