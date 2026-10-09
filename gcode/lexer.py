from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Word:
    letter: str
    value: float | str


@dataclass(frozen=True)
class Comment:
    text: str


type Token = Word | Comment

TOKEN_PATTERN = re.compile(
    r"""
    (?P<whitespace>\s+)
    | (?P<semicolon_comment>;[^\n]*)
    | (?P<paren_comment>\([^)]*\))
    | (?P<word>
        [A-Za-z]
        (?:
            "(?:[^"\\]|\\.)*"
            |
            [+-]?(?:\d+(?:\.\d*)?|\.\d+)
        )
    )
    """,
    re.VERBOSE,
)


def lex_line(source: str) -> list[Token]:
    tokens: list[Token] = []
    position = 0

    while position < len(source):
        match = TOKEN_PATTERN.match(source, position)

        if match is None:
            raise SyntaxError(
                f"Unexpected character at column {position + 1}: "
                f"{source[position]!r}"
            )

        position = match.end()

        if match.lastgroup == "whitespace":
            continue

        if match.lastgroup == "semicolon_comment":
            tokens.append(Comment(match.group()[1:].strip()))
            break

        if match.lastgroup == "paren_comment":
            tokens.append(Comment(match.group()[1:-1].strip()))
            continue

        if match.lastgroup == "word":
            text = match.group()
            raw_value = text[1:]

            if raw_value.startswith('"'):
                value = raw_value[1:-1]
            else:
                value = float(raw_value)

            tokens.append(
                Word(
                    letter=text[0].upper(),
                    value=value,
                )
            )

    return tokens
