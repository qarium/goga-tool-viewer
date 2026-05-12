from __future__ import annotations

import sys

from .server import run_server


def main(argv: list[str]) -> None:
    json_path = argv[0] if argv else None
    try:
        run_server(json_path)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
