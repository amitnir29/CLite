import argparse
import sys
from typing import Optional

from lang.interpreter import Interpreter


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="clite", description="Run clite programs")
    parser.add_argument("file", help="Path to source file (.cl)")
    parser.add_argument("--entry", "-e", default="main", help="Entrypoint function name (default: main)")
    parser.add_argument("--no-entry", action="store_true", help="Do not call entrypoint; run top-level only")

    args = parser.parse_args(argv)

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()
    except OSError as exc:
        print(f"error: cannot read {args.file}: {exc}", file=sys.stderr)
        return 2

    interp = Interpreter()
    entry = None if args.no_entry else args.entry
    try:
        result = interp.run_code(code, entrypoint=entry)
    except Exception as exc:
        print(f"runtime error: {exc}", file=sys.stderr)
        return 1

    if result is not None:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

