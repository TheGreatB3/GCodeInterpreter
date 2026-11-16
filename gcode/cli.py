import argparse
import sys
from pathlib import Path
from typing import TextIO

from gcode.command_decoder import CommandDecoder
from gcode.lexer import lex_line
from gcode.parser import parse_line


def iter_parsed_lines(stream: TextIO):
    for line_number, source in enumerate(stream, start=1):
        try:
            tokens = lex_line(source)
            parsed = parse_line(tokens)

            yield line_number, parsed
        except SyntaxError as error:
            print(
                f"Error on line {line_number}: {error}",
                file=sys.stderr,
            )
            raise


def process_stream(stream: TextIO) -> int:
    decoder = CommandDecoder()

    try:
        for line_number, parsed in iter_parsed_lines(stream):
            command = decoder.decode(parsed, line_number=line_number)

            if command is None:
                continue

            # Do something useful with the command.
            print(f"{line_number}: {command!r}")

    except SyntaxError:
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
        return process_stream(sys.stdin)

    try:
        with args.file.open(encoding="utf-8") as stream:
            return process_stream(stream)
    except OSError as error:
        print(f"Cannot open {args.file}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
