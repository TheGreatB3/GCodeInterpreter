import turtle

from gcode.path import PathSegment

type Layer = tuple[float, list[PathSegment]]

window_width = 1000.0
window_height = 800.0
padding = 80.0


def view_layer(
        layers: list[Layer],
        *,
        initial_layer: int = 0,
        show_travel: bool = False,
) -> None:
    if not layers:
        print("No layers to view.")
        return

    layer_index = max(0, min(initial_layer, len(layers) - 1))

    screen = turtle.Screen()
    screen.setup(width=window_width, height=window_height)

    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.penup()

    status_pen = turtle.Turtle()
    status_pen.hideturtle()
    status_pen.speed(0)
    status_pen.penup()

    def drawable_segments_for(index: int) -> list[PathSegment]:
        return [
            segment
            for segment in layers[index][1]
            if show_travel or segment.extruding
        ]

    def draw_status(index: int, drawable_count: int) -> None:
        z, segments = layers[index]

        status_pen.clear()
        status_pen.goto(-480, 360)
        status_pen.color("black")
        status_pen.write(
            (
                f"Layer {index} / {len(layers) - 1}  "
                f"Z={z:g}  "
                f"segments={len(segments)}  "
                f"drawn={drawable_count}  "
                "controls: ←/p previous, →/n next, Home first, End last, q quit"
            ),
            align="left",
            font=("Arial", 12, "normal"),
        )

    def draw_layer(index: int) -> None:
        nonlocal layer_index

        layer_index = index
        z, _segments = layers[layer_index]
        drawable_segments = drawable_segments_for(layer_index)

        screen.title(f"G-code layer {layer_index} at Z={z:g}")
        pen.clear()
        draw_status(layer_index, len(drawable_segments))

        if not drawable_segments:
            screen.update()
            return

        min_x = min(min(segment.start.x, segment.end.x) for segment in drawable_segments)
        max_x = max(max(segment.start.x, segment.end.x) for segment in drawable_segments)
        min_y = min(min(segment.start.y, segment.end.y) for segment in drawable_segments)
        max_y = max(max(segment.start.y, segment.end.y) for segment in drawable_segments)

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

        for segment in drawable_segments:
            pen.color("red" if segment.extruding else "gray")
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
    screen.onkey(next_layer, "Right")
    screen.onkey(next_layer, "Up")
    screen.onkey(next_layer, "n")
    screen.onkey(previous_layer, "Left")
    screen.onkey(previous_layer, "Down")
    screen.onkey(previous_layer, "p")
    screen.onkey(first_layer, "Home")
    screen.onkey(last_layer, "End")
    screen.onkey(quit_viewer, "q")
    screen.onkey(quit_viewer, "Escape")

    draw_layer(layer_index)

    screen.mainloop()
