from dataclasses import dataclass

from gcode.lexer import Word


@dataclass(frozen=True)
class CommandCode:
    letter: str  # "G" or "M"
    number: int | float


@dataclass(frozen=True)
class Command:
    code: CommandCode | None
    params: tuple[Word, ...]
    line_number: int
