from dataclasses import dataclass

from gcode.lexer import Word, Comment, Token


@dataclass(frozen=True)
class ParsedLine:
    words: tuple[Word, ...]
    comments: tuple[Comment, ...] = ()


def parse_line(tokens: list[Token]) -> ParsedLine:
    words = tuple(token for token in tokens if isinstance(token, Word))
    comments = tuple(token for token in tokens if isinstance(token, Comment))
    return ParsedLine(words, comments)
