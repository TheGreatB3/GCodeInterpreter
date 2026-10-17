from dataclasses import dataclass

from gcode.vec3 import Vec3


@dataclass(frozen=True)
class MoveEvent:
    start: Vec3
    end: Vec3
    feed_rate: float
    extruding: bool
