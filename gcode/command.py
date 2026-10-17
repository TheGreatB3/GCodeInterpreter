from dataclasses import dataclass

from gcode.lexer import Word


@dataclass(frozen=True)
class CommandCode:
    letter: str  # "G" or "M"
    code: int | float


@dataclass(frozen=True)
class Command:
    code: CommandCode
    params: tuple[Word, ...]
    line_number: int
