#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import os
import secrets
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Erzeugt einen 32-Byte-Schlüssel für den SCP-1356-Transport."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="transport.key",
        help="Zieldatei (Standard: transport.key)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Vorhandene Datei überschreiben",
    )
    args = parser.parse_args()

    path = Path(args.path).expanduser().resolve()
    if path.exists() and not args.force:
        parser.error(f"Datei existiert bereits: {path}. Nutze --force zum Überschreiben.")

    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = base64.b64encode(secrets.token_bytes(32)).decode("ascii")
    path.write_text(encoded + "\n", encoding="utf-8")

    try:
        os.chmod(path, 0o600)
    except OSError:
        pass

    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())