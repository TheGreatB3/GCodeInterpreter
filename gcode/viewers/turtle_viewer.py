import turtle

from gcode.path import PathSegment


def view_layer(
        segments: list[PathSegment],
        *,
        title: str,
        show_travel: bool = False,
) -> None:
    drawable_segments = [
        segment
        for segment in segments
        if show_travel or segment.extruding
    ]

    if not drawable_segments:
        print("No drawable segments in this layer.")
        return

    min_x = min(min(segment.start.x, segment.end.x) for segment in drawable_segments)
    max_x = max(max(segment.start.x, segment.end.x) for segment in drawable_segments)
    min_y = min(min(segment.start.y, segment.end.y) for segment in drawable_segments)
    max_y = max(max(segment.start.y, segment.end.y) for segment in drawable_segments)

    width = max_x - min_x
    height = max_y - min_y

    screen = turtle.Screen()
    screen.title(title)
    screen.setup(width=1000, height=800)

    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.penup()

    margin = 40.0
    canvas_width = 920
    canvas_height = 720

    scale_x = canvas_width / width if width else 1.0
    scale_y = canvas_height / height if height else 1.0
    scale = min(scale_x, scale_y)

    def project(x: float, y: float) -> tuple[float, float]:
        projected_x = ((x - min_x) * scale) - (canvas_width / 2.0) + margin
        projected_y = ((y - min_y) * scale) - (canvas_height / 2.0) + margin
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

    screen.mainloop()
