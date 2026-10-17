from gcode.command import Command, CommandCode
from gcode.lexer import Word
from gcode.parser import ParsedLine


class CommandDecoder:
    def decode(self, parsed_line: ParsedLine, *, line_number: int) -> list[Command]:
        commands: list[Command] = []
        current_code: CommandCode | None = None
        params: list[Word] = []

        for word in parsed_line.words:
            if word.letter in ("G", "M"):
                if not isinstance(word.value, (int, float)):
                    raise SyntaxError(
                        f"Command {word.letter} code must be a number, got {word.value!r}"
                    )

                # Finish the previous command, if any.
                if current_code is not None:
                    commands.append(
                        Command(
                            code=current_code,
                            params=tuple(params),
                            line_number=line_number,
                        )
                    )
                    params = []
                elif params:
                    # Parameters appeared before a command code.
                    commands.append(
                        Command(
                            code=None,
                            params=tuple(params),
                            line_number=line_number,
                        )
                    )
                    params = []

                current_code = CommandCode(
                    letter=word.letter,
                    number=word.value,
                )

            else:
                params.append(word)

        # Finish the final command or parameter-only line.
        if current_code is not None or params:
            commands.append(
                Command(
                    code=current_code,
                    params=tuple(params),
                    line_number=line_number,
                )
            )

        return commands
