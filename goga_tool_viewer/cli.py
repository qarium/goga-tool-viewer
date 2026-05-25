from __future__ import annotations

import sys

from .server import run_server


def main(argv: list[str]) -> None:
    """Entry point for the goga tool viewer CLI.

    Loads cell graph data from a file or stdin and starts the visualization server.

    Args:
        argv: Command-line arguments. The first element is treated as the JSON
            file path. If empty, data is read from stdin.

    Raises:
        SystemExit: On file-not-found, invalid JSON, or OS errors.
    """
    json_path = argv[0] if argv else None

    try:
        run_server(json_path)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
