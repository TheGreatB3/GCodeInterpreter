from typing import Protocol

from gcode.machine_event import MoveEvent


class MachineEventConsumer(Protocol):
    def on_move(self, event: MoveEvent) -> None:
        ...
