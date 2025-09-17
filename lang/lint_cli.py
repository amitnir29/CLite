import argparse
import sys
from typing import Optional

from lang.lint import lint_code


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="clite-lint", description="Lint clite files for common issues")
    parser.add_argument("files", nargs="+", help="Source files to lint")
    parser.add_argument("--fail-on-warn", action="store_true", help="Exit non-zero if any warnings found")

    args = parser.parse_args(argv)

    total = 0
    for path in args.files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
        except OSError as exc:
            print(f"error: cannot read {path}: {exc}", file=sys.stderr)
            return 2

        warns = lint_code(code)
        total += len(warns)
        for w in warns:
            print(f"{path}:{w.line}:{w.column}: {w.code} {w.message}")

    if args.fail_on_warn and total > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

