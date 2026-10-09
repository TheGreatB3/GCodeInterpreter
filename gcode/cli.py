import argparse
import sys
from pathlib import Path
from typing import TextIO

from gcode.lexer import lex_line
from gcode.parser import parse_line


def process_stream(stream: TextIO, *, show_tokens: bool) -> int:
    for line_number, source in enumerate(stream, start=1):
        try:
            tokens = lex_line(source)
            parsed = parse_line(tokens)

            if show_tokens:
                print(f"{line_number}: {tokens!r}")
            else:
                print(f"{line_number}: {parsed!r}")

        except SyntaxError as error:
            print(
                f"Error on line {line_number}: {error}",
                file=sys.stderr,
            )
            return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="gcode",
        description="Parse and inspect G-code programs.",
    )

    parser.add_argument(
        "file",
        type=Path,
        help="G-code file to process, or '-' for stdin",
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--tokens",
        action="store_true",
        help="Print lexer tokens instead of parsed lines",
    )
    mode.add_argument(
        "--parse",
        action="store_true",
        help="Print parsed lines (the default)",
    )

    args = parser.parse_args()

    if str(args.file) == "-":
        return process_stream(sys.stdin, show_tokens=args.tokens)

    try:
        with args.file.open(encoding="utf-8") as stream:
            return process_stream(stream, show_tokens=args.tokens)
    except OSError as error:
        print(f"Cannot open {args.file}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
