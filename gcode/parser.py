from dataclasses import dataclass

from gcode.lexer import Word, Comment


@dataclass(frozen=True)
class ParsedLine:
    words: tuple[Word, ...]
    comments: tuple[Comment, ...] = ()
