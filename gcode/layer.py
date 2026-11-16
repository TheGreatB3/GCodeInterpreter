from dataclasses import dataclass, field

from gcode.parser import ParsedLine
from gcode.path import PathSegment, group_segments_by_layer


@dataclass(frozen=True)
class Layer:
    index: int
    z: float
    segments: tuple[PathSegment, ...]


@dataclass
class LayerTracker:
    layers: list[Layer] = field(default_factory=list)
    current_segments: list[PathSegment] = field(default_factory=list)
    current_z: float = 0.0
    saw_layer_change: bool = False
    pending_layer_change: bool = False

    def on_parsed(self, parsed: ParsedLine) -> None:
        for comment in parsed.comments:
            text = comment.text.strip()

            if text == "LAYER_CHANGE":
                self.finish_current_layer()
                self.saw_layer_change = True
                self.pending_layer_change = True
                continue

            if self.pending_layer_change and text.startswith("Z:"):
                self._set_pending_layer_z(text)

    def on_segments(self, segments: list[PathSegment]) -> None:
        self.current_segments.extend(segments)

    def finish(self, fallback_segments: list[PathSegment]) -> list[Layer]:
        self.finish_current_layer()

        if self.saw_layer_change:
            return self.layers

        return [
            Layer(
                index=index,
                z=z,
                segments=tuple(segments),
            )
            for index, (z, segments) in enumerate(group_segments_by_layer(fallback_segments))
        ]

    def finish_current_layer(self) -> None:
        if not self.current_segments:
            self.pending_layer_change = False
            return

        self.layers.append(
            Layer(
                index=len(self.layers),
                z=self.current_z,
                segments=tuple(self.current_segments),
            )
        )
        self.current_segments = []
        self.pending_layer_change = False

    def _set_pending_layer_z(self, text: str) -> None:
        try:
            self.current_z = float(text.removeprefix("Z:"))
        except ValueError:
            pass
