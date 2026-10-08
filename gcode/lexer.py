from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Word:
    letter: str
    value: float


@dataclass(frozen=True)
class Comment:
    text: str


type Token = Word | Comment

TOKEN_PATTERN = re.compile(
    r"""
    (?P<whitespace>\s+)
    | (?P<semicolon_comment>;[^\n]*)
    | (?P<paren_comment>\([^)]*\))
    | (?P<word>[A-Za-z][+-]?(?:\d+(?:\.\d*)?|\.\d+))
    """,
    re.VERBOSE,
)
