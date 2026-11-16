import turtle

from gcode.extrusion import TypedPathSegment, EXTRUSION_TYPE_COLORS
from gcode.layer import Layer
from gcode.path import PathSegment

window_width = 1920.0
window_height = 1080.0
padding = 80.0
legend_padding = 24.0
legend_item_height = 24.0
legend_swatch_size = 12.0


def view_layers(
        layers: list[Layer],
        *,
        initial_layer: int = 0,
        show_travel: bool = False,
) -> None:
    if not layers:
        print("No layers to view.")
        return

    turtle.colormode(255)

    layer_index = max(0, min(initial_layer, len(layers) - 1))

    screen = turtle.Screen()
    screen.setup(width=window_width, height=window_height)
    screen.tracer(0)

    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.penup()

    status_pen = turtle.Turtle()
    status_pen.hideturtle()
    status_pen.speed(0)
    status_pen.penup()

    legend_pen = turtle.Turtle()
    legend_pen.hideturtle()
    legend_pen.speed(0)
    legend_pen.penup()

    def drawable_segments_for(index: int) -> list[TypedPathSegment]:
        return [
            segment
            for segment in layers[index].segments
            if show_travel or segment.segment.extruding
        ]

    def draw_legend(index: int) -> None:
        layer = layers[index]
        extrusion_types = sorted(
            {
                typed_segment.extrusion_type
                for typed_segment in layer.segments
                if show_travel or typed_segment.segment.extruding
            },
            key=lambda extrusion_type: extrusion_type.value
        )

        legend_pen.clear()

        if not extrusion_types:
            return

        x = window_width / 2 - padding - 220
        y = window_height / 2 - padding - 8

        legend_pen.goto(x, y)
        legend_pen.color("black")
        legend_pen.write(
            "Extrusion types",
            align="left",
            font=("Arial", 12, "bold")
        )

        for row, extrusion_type in enumerate(extrusion_types, start=1):
            item_y = y - row * legend_item_height
            color = EXTRUSION_TYPE_COLORS[extrusion_type]

            legend_pen.penup()
            legend_pen.goto(x, item_y)
            legend_pen.color(color)
            legend_pen.begin_fill()
            legend_pen.pendown()
            for _ in range(4):
                legend_pen.forward(legend_swatch_size)
                legend_pen.right(90)
            legend_pen.end_fill()
            legend_pen.penup()

            legend_pen.goto(x + legend_swatch_size + 8, item_y - legend_swatch_size)
            legend_pen.color("black")
            legend_pen.write(
                extrusion_type.value,
                align="left",
                font=("Arial", 10, "normal"),
            )

    all_drawable_segments = [
        segment
        for layer_idx in range(len(layers))
        for segment in drawable_segments_for(layer_idx)
    ]

    if not all_drawable_segments:
        screen.update()
        return

    points = [
        point
        for typed_segment in all_drawable_segments
        for point in (typed_segment.segment.start, typed_segment.segment.end)
    ]

    min_x = min(point.x for point in points)
    max_x = max(point.x for point in points)
    min_y = min(point.y for point in points)
    max_y = max(point.y for point in points)

    width = max_x - min_x
    height = max_y - min_y
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0

    drawable_width = window_width - 2 * padding
    drawable_height = window_height - 2 * padding

    scale_x = drawable_width / width if width else 1.0
    scale_y = drawable_height / height if height else 1.0
    scale = min(scale_x, scale_y)

    def project(x: float, y: float) -> tuple[float, float]:
        projected_x = (x - center_x) * scale
        projected_y = (y - center_y) * scale
        return projected_x, projected_y

    def draw_status(index: int, drawable_count: int) -> None:
        layer = layers[index]

        status_pen.clear()
        status_pen.goto(-window_width / 2 + padding, window_height / 2 - padding)
        status_pen.color("black")
        status_pen.write(
            (
                f"Layer {index} / {len(layers) - 1}  "
                f"Z={layer.z :g}  "
                f"segments={len(layer.segments)}  "
                f"drawn={drawable_count}  "
                "controls: ←/p previous, →/n next, Home first, End last, q quit"
            ),
            align="left",
            font=("Arial", 12, "normal"),
        )

    def draw_layer(index: int) -> None:
        nonlocal layer_index

        layer_index = index
        layer = layers[layer_index]
        drawable_segments = drawable_segments_for(layer_index)

        screen.title(f"G-code layer {layer_index} at Z={layer.z:g}")
        pen.clear()
        draw_status(layer_index, len(drawable_segments))
        draw_legend(layer_index)

        if not drawable_segments:
            screen.update()
            return

        for typed_segment in drawable_segments:
            segment = typed_segment.segment
            color = EXTRUSION_TYPE_COLORS[typed_segment.extrusion_type]

            pen.color(color)
            pen.pensize(2 if segment.extruding else 1)

            start_x, start_y = project(segment.start.x, segment.start.y)
            end_x, end_y = project(segment.end.x, segment.end.y)

            pen.penup()
            pen.goto(start_x, start_y)
            pen.pendown()
            pen.goto(end_x, end_y)

        screen.update()

    def next_layer() -> None:
        draw_layer(min(layer_index + 1, len(layers) - 1))

    def previous_layer() -> None:
        draw_layer(max(layer_index - 1, 0))

    def first_layer() -> None:
        draw_layer(0)

    def last_layer() -> None:
        draw_layer(len(layers) - 1)

    def quit_viewer() -> None:
        turtle.bye()

    screen.listen()
    screen.onkeypress(next_layer, "Right")
    screen.onkeypress(next_layer, "Up")
    screen.onkeypress(next_layer, "n")
    screen.onkeypress(previous_layer, "Left")
    screen.onkeypress(previous_layer, "Down")
    screen.onkeypress(previous_layer, "p")
    screen.onkey(first_layer, "Home")
    screen.onkey(last_layer, "End")
    screen.onkey(quit_viewer, "q")
    screen.onkey(quit_viewer, "Escape")

    draw_layer(layer_index)

    screen.mainloop()
