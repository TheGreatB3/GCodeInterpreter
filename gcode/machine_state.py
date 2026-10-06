from dataclasses import dataclass
from enum import StrEnum

from gcode.vec3 import Vec3


class Units(StrEnum):
    INCHES = "IN"
    MM = "MM"


class MotionMode(StrEnum):
    G0 = "G0"
    G1 = "G1"
    G2 = "G2"
    G3 = "G3"


@dataclass
class MachineState:
    position: Vec3
    feed_rate: float
    spindle_speed: float
    absolute_mode: bool
    units: Units
    motion_mode: MotionMode
