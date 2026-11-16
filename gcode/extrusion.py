from dataclasses import dataclass
from enum import Enum

from gcode.parser import ParsedLine


class GCodeExtrusionType(Enum):
    NONE = "Unknown"
    PERIMETER = "Inner wall"
    EXTERNAL_PERIMETER = "Outer wall"
    OVERHANG_PERIMETER = "Overhang wall"
    INTERNAL_INFILL = "Sparse infill"
    SOLID_INFILL = "Internal solid infill"
    TOP_SOLID_INFILL = "Top surface"
    IRONING = "Ironing"
    BRIDGE_INFILL = "Bridge"
    GAP_FILL = "Gap infill"
    SKIRT = "Skirt"
    SUPPORT_MATERIAL = "Support"
    SUPPORT_MATERIAL_INTERFACE = "Support interface"
    WIPE_TOWER = "Prime tower"
    CUSTOM = "Custom"
    BOTTOM_SURFACE = "Bottom surface"
    INTERNAL_BRIDGE_INFILL = "Internal bridge"
    BRIM = "Brim"
    SUPPORT_TRANSITION = "Support transition"
    MIXED = "Mixed"


EXTRUSION_TYPE_COLORS = {
    GCodeExtrusionType.NONE: (160, 160, 160),  # gray
    GCodeExtrusionType.PERIMETER: (66, 135, 245),  # blue
    GCodeExtrusionType.EXTERNAL_PERIMETER: (20, 85, 200),  # darker blue
    GCodeExtrusionType.OVERHANG_PERIMETER: (245, 90, 66),  # coral red
    GCodeExtrusionType.INTERNAL_INFILL: (120, 200, 80),  # green
    GCodeExtrusionType.SOLID_INFILL: (60, 160, 75),  # darker green
    GCodeExtrusionType.TOP_SOLID_INFILL: (255, 210, 70),  # yellow
    GCodeExtrusionType.IRONING: (255, 245, 150),  # pale yellow
    GCodeExtrusionType.BRIDGE_INFILL: (155, 90, 220),  # purple
    GCodeExtrusionType.GAP_FILL: (255, 145, 50),  # orange
    GCodeExtrusionType.SKIRT: (120, 120, 120),  # dark gray
    GCodeExtrusionType.SUPPORT_MATERIAL: (90, 200, 200),  # cyan
    GCodeExtrusionType.SUPPORT_MATERIAL_INTERFACE: (40, 150, 170),  # teal
    GCodeExtrusionType.WIPE_TOWER: (190, 120, 70),  # brown
    GCodeExtrusionType.CUSTOM: (255, 105, 180),  # pink
    GCodeExtrusionType.BOTTOM_SURFACE: (130, 90, 60),  # warm brown
    GCodeExtrusionType.INTERNAL_BRIDGE_INFILL: (180, 130, 230),  # lavender
    GCodeExtrusionType.BRIM: (80, 80, 80),  # charcoal
    GCodeExtrusionType.SUPPORT_TRANSITION: (130, 220, 220),  # light cyan
    GCodeExtrusionType.MIXED: (255, 255, 255),  # white
}


@dataclass
class ExtrusionTracker:
    current_extrusion_type: GCodeExtrusionType = GCodeExtrusionType.NONE

    def on_parsed(self, parsed: ParsedLine):
        for comment in parsed.comments:
            text = comment.text.strip()
            if text.startswith("TYPE:"):
                self.current_extrusion_type = GCodeExtrusionType(text.removeprefix("TYPE:"))
