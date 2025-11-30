init python:
    import math
    import renpy.display.render as ren_render
    import renpy.display.pgrender as ren_pgrender
    import renpy.pygame as pygame
    from renpy.color import Color


    def _color_to_rgba_tuple(color_value):
        """Convert Ren'Py colors into an RGBA tuple pygame understands."""
        rgba = Color(color_value).rgba
        return (
            int(rgba[0] * 255),
            int(rgba[1] * 255),
            int(rgba[2] * 255),
            int(rgba[3] * 255),
        )


    class CircleDisplayable(renpy.Displayable):
        """Simple displayable that draws a circle using pygame primitives."""

        def __init__(self, radius, fill_color="#ffffff", border_color=None, border_thickness=0, **kwargs):
            super(CircleDisplayable, self).__init__(**kwargs)
            self.radius = max(1, int(radius))
            self.fill_color = fill_color
            self.border_color = border_color
            self.border_thickness = max(0, int(border_thickness))

        def render(self, width, height, st, at):
            diameter = self.radius * 2
            rv = ren_render.Render(diameter, diameter)

            surface = ren_pgrender.surface((diameter, diameter), True)
            surface = surface.convert_alpha()
            surface.fill((0, 0, 0, 0))

            if self.fill_color:
                pygame.draw.circle(
                    surface,
                    _color_to_rgba_tuple(self.fill_color),
                    (self.radius, self.radius),
                    self.radius,
                )

            if self.border_color and self.border_thickness > 0:
                pygame.draw.circle(
                    surface,
                    _color_to_rgba_tuple(self.border_color),
                    (self.radius, self.radius),
                    self.radius,
                    self.border_thickness,
                )

            rv.blit(surface, (0, 0))
            return rv

        def visit(self):
            return []


    class DashedCircleDisplayable(renpy.Displayable):
        def __init__(self, radius, dash_count=48, dash_ratio=0.5, color="#4dc0ff", thickness=4, rotation=0.0, **kwargs):
            super(DashedCircleDisplayable, self).__init__(**kwargs)
            self.radius = max(1, int(radius))
            self.dash_count = max(1, int(dash_count))
            self.dash_ratio = max(0.05, min(1.0, float(dash_ratio)))
            self.color = color
            self.thickness = max(1, int(thickness))
            self.rotation = float(rotation)

        def render(self, width, height, st, at):
            diameter = self.radius * 2
            size = diameter + self.thickness * 2
            rv = ren_render.Render(size, size)
            surface = ren_pgrender.surface((size, size), True)
            surface = surface.convert_alpha()
            surface.fill((0, 0, 0, 0))

            dash_span = 2 * math.pi / self.dash_count
            dash_length = dash_span * self.dash_ratio
            base = math.radians(self.rotation)
            center = size / 2.0
            radius = self.radius

            for i in range(self.dash_count):
                start = base + dash_span * i
                end = start + dash_length
                start_pos = (
                    center + math.cos(start) * radius,
                    center + math.sin(start) * radius,
                )
                end_pos = (
                    center + math.cos(end) * radius,
                    center + math.sin(end) * radius,
                )
                pygame.draw.line(
                    surface,
                    _color_to_rgba_tuple(self.color),
                    start_pos,
                    end_pos,
                    self.thickness,
                )

            rv.blit(surface, (0, 0))
            return rv

        def visit(self):
            return []


screen circle_demo_screen(fill_color="#5ecbff", border_color="#0f1925"):
    modal True
    add Solid("#000000aa")

    frame:
        align (0.5, 0.5)
        padding (28, 28)
        vbox:
            spacing 16
            text "Circle Demo" size 42
            fixed:
                xysize (320, 320)
                add DashedCircleDisplayable(radius=140, dash_count=56, dash_ratio=0.55, thickness=6, color="#2ac4ff", rotation=90) align (0.5, 0.5)
                add CircleDisplayable(radius=130, fill_color=None, border_color=border_color, border_thickness=12) align (0.5, 0.5)
            text "Click or press \"Enter\" to dismiss." size 24

    key "dismiss" action Return(None)


label show_circle_demo:
    "Launching the circle demo screen."
    call screen circle_demo_screen
    "Circle demo complete."
    return
