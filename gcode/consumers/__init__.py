from typing import Protocol

from gcode.command import MoveEvent


class MachineEventConsumer(Protocol):
    def on_move(self, event: MoveEvent) -> None:
        ...
