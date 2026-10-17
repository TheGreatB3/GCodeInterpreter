from gcode.command import Command, CommandCode
from gcode.lexer import Word
from gcode.parser import ParsedLine


class CommandDecoder:
    def decode(self, parsed_line: ParsedLine, *, line_number: int) -> list[Command]:
        commands: list[Command] = []
        current_code: CommandCode | None = None
        params: list[Word] = []

        return commands
