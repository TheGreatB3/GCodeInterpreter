import argparse
import sys
from pathlib import Path
from typing import TextIO, Protocol

from gcode.command import Command
from gcode.command_decoder import CommandDecoder
from gcode.lexer import lex_line, Word, Comment
from gcode.parser import parse_line, ParsedLine


class ProcessingMode(Protocol):
    def on_tokens(self, line_number: int, tokens: list[Word | Comment]) -> None:
        ...

    def on_parsed(self, line_number: int, parsed: ParsedLine) -> None:
        ...

    def on_commands(self, line_number: int, commands: list[Command]) -> None:
        ...

    def finish(self) -> None:
        ...


class BaseMode:
    def on_tokens(self, line_number: int, tokens: list[Word | Comment]) -> None:
        pass

    def on_parsed(self, line_number: int, parsed: ParsedLine) -> None:
        pass

    def on_commands(self, line_number: int, commands: list[Command]) -> None:
        pass

    def finish(self) -> None:
        pass


class TokenMode(BaseMode):
    def on_tokens(self, line_number: int, tokens: list[Word | Comment]) -> None:
        print(f"{line_number}: {tokens!r}")


class ParseMode(BaseMode):
    def on_parsed(self, line_number: int, parsed: ParsedLine) -> None:
        print(f"{line_number}: {parsed!r}")


class CommandMode(BaseMode):
    def on_commands(self, line_number: int, commands: list[Command]) -> None:
        print(f"{commands!r}")


class SummaryMode(BaseMode):
    def __init__(self) -> None:
        self.line_count = 0
        self.command_count = 0

    def on_parsed(self, line_number: int, parsed: ParsedLine) -> None:
        self.line_count = line_number

    def on_commands(self, line_number: int, commands: list[Command]) -> None:
        self.command_count += len(commands)

    def finish(self) -> None:
        print(f"Lines: {self.line_count}")
        print(f"Commands: {self.command_count}")


def process_stream(stream: TextIO, mode: ProcessingMode) -> int:
    decoder = CommandDecoder()

    for line_number, source in enumerate(stream, start=1):
        try:
            tokens = lex_line(source)
            mode.on_tokens(line_number, tokens)

            parsed = parse_line(tokens)
            mode.on_parsed(line_number, parsed)

            commands = decoder.decode(parsed, line_number=line_number)
            mode.on_commands(line_number, commands)

        except SyntaxError as error:
            print(
                f"Error on line {line_number}: {error}",
                file=sys.stderr,
            )
            return 1

    mode.finish()
    return 0


def create_mode(args: argparse.Namespace) -> ProcessingMode:
    if args.tokens:
        return TokenMode()
    if args.parse:
        return ParseMode()
    if args.commands:
        return CommandMode()
    return SummaryMode()


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
        help="Print lexer tokens",
    )
    mode.add_argument(
        "--parse",
        action="store_true",
        help="Print parsed lines",
    )
    mode.add_argument(
        "--commands",
        action="store_true",
        help="Print decoded commands",
    )
    mode.add_argument(
        "--summary",
        action="store_true",
        help="Print a short file summary",
    )

    args = parser.parse_args()
    processing_mode = create_mode(args)

    if str(args.file) == "-":
        return process_stream(sys.stdin, processing_mode)

    try:
        with args.file.open(encoding="utf-8") as stream:
            return process_stream(stream, processing_mode)
    except OSError as error:
        print(f"Cannot open {args.file}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
