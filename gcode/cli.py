import argparse
import sys
from pathlib import Path
from typing import TextIO, Protocol

from gcode.command import Command
from gcode.command_decoder import CommandDecoder
from gcode.lexer import lex_line, Word, Comment
from gcode.parser import parse_line, ParsedLine
from gcode.path import PathExtractor, PathSegment, group_segments_by_layer
from gcode.viewers.turtle_viewer import view_layer


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


class PathMode(BaseMode):
    def __init__(self) -> None:
        self.extractor = PathExtractor()
        self.segments: list[PathSegment] = []

    def on_commands(self, line_number: int, commands: list[Command]) -> None:
        for command in commands:
            self.segments.extend(self.extractor.execute(command))


class TurtleMode(PathMode):
    def __init__(self, *, layer: int | None, show_travel: bool) -> None:
        super().__init__()
        self.layer = layer
        self.show_travel = show_travel
        self.comment_layers: list[tuple[float, list[PathSegment]]] = []
        self.current_layer_segments: list[PathSegment] = []
        self.current_layer_z = 0.0
        self.pending_layer_change = False
        self.saw_layer_change = False

    def on_parsed(self, line_number: int, parsed: ParsedLine) -> None:
        for comment in parsed.comments:
            text = comment.text.strip()

            if text == "LAYER_CHANGE":
                self._finish_current_comment_layer()
                self.pending_layer_change = True
                self.saw_layer_change = True
                continue

            if self.pending_layer_change and text.startswith("Z:"):
                try:
                    self.current_layer_z = float(text.removeprefix("Z:"))
                except ValueError:
                    pass

    def on_commands(self, line_number: int, commands: list[Command]) -> None:
        for command in commands:
            segments = self.extractor.execute(command)
            self.segments.extend(segments)
            self.current_layer_segments.extend(segments)

    def finish(self) -> None:
        self._finish_current_comment_layer()

        if self.saw_layer_change:
            layers = self.comment_layers
        else:
            layers = group_segments_by_layer(self.segments)

        if not layers:
            print("No path segments found.")
            return

        if self.layer is None:
            selected_layer = 0
        else:
            selected_layer = self.layer

        if selected_layer < 0 or selected_layer >= len(layers):
            print(
                f"Layer {selected_layer} is out of range. "
                f"Available layers: 0 to {len(layers) - 1}",
                file=sys.stderr,
            )
            return

        z, segments = layers[selected_layer]
        print(
            f"Viewing layer {selected_layer} / {len(layers) - 1} "
            f"at Z={z:g} with {len(segments)} segments",
        )

        view_layer(
            layers,
            initial_layer=selected_layer,
            show_travel=self.show_travel,
        )

    def _finish_current_comment_layer(self) -> None:
        if not self.current_layer_segments:
            return

        self.comment_layers.append((
            self.current_layer_z,
            self.current_layer_segments,
        ))

        self.current_layer_segments = []
        self.pending_layer_change = False


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
    if args.turtle:
        return TurtleMode(
            layer=args.layer,
            show_travel=args.show_travel,
        )
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
        "--turtle",
        action="store_true",
        help="View the filament path for one layer using Turtle graphics",
    )
    mode.add_argument(
        "--summary",
        action="store_true",
        help="Print a short file summary",
    )

    parser.add_argument(
        "--layer",
        type=int,
        default=None,
        help="Layer index to view with --turtle. Defaults to 0.",
    )
    parser.add_argument(
        "--show-travel",
        action="store_true",
        help="Show non-extruding travel moves in Turtle views.",
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
