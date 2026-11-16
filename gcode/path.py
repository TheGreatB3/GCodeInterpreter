from dataclasses import dataclass

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
