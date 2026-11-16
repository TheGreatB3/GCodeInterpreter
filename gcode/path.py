from dataclasses import dataclass
from math import isclose

from gcode.command import Command
from gcode.vec3 import Vec3


@dataclass(frozen=True)
class PathSegment:
    start: Vec3
    end: Vec3
    extruding: bool
    line_number: int
    feed_rate: float


@dataclass
class PathState:
    position: Vec3
    extrusion: float
    feed_rate: float
    absolute_xyz: bool
    absolute_extrusion: bool


class PathExtractor:
    def __init__(self):
        self.state = PathState(
            position=Vec3(0, 0, 0),
            extrusion=0,
            feed_rate=0,
            absolute_xyz=True,
            absolute_extrusion=True,
        )
        self.motion_mode: int | None = None

    def execute(self, command: Command) -> list[PathSegment]:
        if command.code is None:
            return self._execute_motion(command)

        if command.code.letter == "G":
            return self._execute_g(command)

        if command.code.letter == "M":
            self._execute_m(command)
            return []

        return []

    def _execute_g(self, command: Command) -> list[PathSegment]:
        code = int(command.code.number)

        if code in (0, 1):
            self.motion_mode = code
            return self._execute_motion(command)

        if code == 90:
            self.state.absolute_xyz = True
            return []

        if code == 91:
            self.state.absolute_xyz = False
            return []

        if code == 92:
            self._set_position(command)
            return []

        return []

    def _execute_m(self, command: Command) -> None:
        code = int(command.code.number)
        if code == 82:
            self.state.absolute_extrusion = True
        elif code == 83:
            self.state.absolute_extrusion = False

    def _execute_motion(self, command: Command) -> list[PathSegment]:
        if self.motion_mode not in (0, 1):
            return []

        start = self.state.position
        old_extrusion = self.state.extrusion

        x = start.x
        y = start.y
        z = start.z
        extrusion = old_extrusion
        feed_rate = self.state.feed_rate

        saw_motion_parameter = False

        for param in command.params:
            if not isinstance(param.value, float):
                continue

            if param.letter == "X":
                x = self._target_value(start.x, param.value, self.state.absolute_xyz)
                saw_motion_parameter = True
            elif param.letter == "Y":
                y = self._target_value(start.y, param.value, self.state.absolute_xyz)
                saw_motion_parameter = True
            elif param.letter == "Z":
                z = self._target_value(start.z, param.value, self.state.absolute_xyz)
                saw_motion_parameter = True
            elif param.letter == "E":
                extrusion = self._target_value(old_extrusion, param.value, self.state.absolute_extrusion)
                saw_motion_parameter = True
            elif param.letter == "F":
                feed_rate = param.value

        end = Vec3(x, y, z)
        self.state.position = end
        self.state.extrusion = extrusion
        self.state.feed_rate = feed_rate

        moved_xyz = not (
                isclose(start.x, end.x)
                and isclose(start.y, end.y)
                and isclose(start.z, end.z)
        )

        if not saw_motion_parameter or not moved_xyz:
            return []

        return [
            PathSegment(
                start=start,
                end=end,
                extruding=extrusion > old_extrusion,
                line_number=command.line_number,
                feed_rate=feed_rate,
            )
        ]

    def _set_position(self, command: Command) -> None:
        position = self.state.position
        x = position.x
        y = position.y
        z = position.z
        extrusion = self.state.extrusion

        for param in command.params:
            if not isinstance(param.value, float):
                continue

            if param.letter == "X":
                x = param.value
            elif param.letter == "Y":
                y = param.value
            elif param.letter == "Z":
                z = param.value
            elif param.letter == "E":
                extrusion = param.value

        self.state.position = Vec3(x, y, z)
        self.state.extrusion = extrusion

    @staticmethod
    def _target_value(current: float, value: float, absolute: bool) -> float:
        if absolute:
            return value
        return current + value


def group_segments_by_layer(
        segments: list[PathSegment],
        *,
        z_tolerance: float = 0.0001,
) -> list[tuple[float, list[PathSegment]]]:
    layers: list[tuple[float, list[PathSegment]]] = []

    for segment in segments:
        z = segment.end.z

        if not layers or abs(layers[-1][0] - z) > z_tolerance:
            layers.append((z, [segment]))
        else:
            layers[-1][1].append(segment)

    return layers
