init python:
    import os
    import renpy.exports as renpy
    import renpy.loader as ren_loader
    import renpy.pygame as pygame

    from renpy import config as ren_config
    from renpy.display.core import Displayable
    from renpy.display.render import Render
    from renpy.store import Solid


    class SpaceRebellionDisplayable(Displayable):
        """Custom displayable that feeds the pygame-driven engine each frame."""

        def __init__(self, width=960, height=600, seed=None, **kwargs):
            super(SpaceRebellionDisplayable, self).__init__(**kwargs)
            self.width = int(width)
            self.height = int(height)
            self.focusable = True
            asset_root = _space_rebellion_asset_root()
            self.engine = SpaceRebellionEngine(asset_root=asset_root, width=self.width, height=self.height, seed=seed)
            self._input_state = {"left": False, "right": False, "up": False, "down": False}
            self._last_st = None

        def reset(self):
            self.engine.reset()
            self._last_st = None
            for key in self._input_state:
                self._input_state[key] = False
            self.engine.set_direction(0, 0)
            self.engine.set_keyboard_fire(False)
            self.engine.set_mouse_fire(False)

        def render(self, width, height, st, at):
            if self._last_st is None:
                dt = 0.0
            else:
                dt = st - self._last_st
            self._last_st = st
            self.engine.update(dt)
            frame = self.engine.render()
            rv = Render(self.width, self.height)
            rv.blit(frame, (0, 0))
            renpy.redraw(self, 0)
            return rv

        def event(self, ev, x, y, st):
            handled = False
            if ev.type in (pygame.KEYDOWN, pygame.KEYUP):
                handled = self._handle_key_event(ev)
            elif ev.type == pygame.MOUSEMOTION:
                local_x = ev.pos[0] - x
                local_y = ev.pos[1] - y
                self.engine.set_pointer((local_x, local_y), use_mouse=True)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self.engine.set_pointer((ev.pos[0] - x, ev.pos[1] - y), use_mouse=True)
                self.engine.set_mouse_fire(True)
                handled = True
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                self.engine.set_mouse_fire(False)
                handled = True
            # Prevent unhandled events from bubbling up and closing the screen.
            return None

        def _handle_key_event(self, ev):
            pressed = ev.type == pygame.KEYDOWN
            if ev.key in (pygame.K_a, pygame.K_LEFT):
                self._input_state["left"] = pressed
            elif ev.key in (pygame.K_d, pygame.K_RIGHT):
                self._input_state["right"] = pressed
            elif ev.key in (pygame.K_w, pygame.K_UP):
                self._input_state["up"] = pressed
            elif ev.key in (pygame.K_s, pygame.K_DOWN):
                self._input_state["down"] = pressed
            elif ev.key == pygame.K_SPACE:
                self.engine.set_keyboard_fire(pressed)
                return True
            else:
                return False
            dx = float(self._input_state["right"]) - float(self._input_state["left"])
            dy = float(self._input_state["down"]) - float(self._input_state["up"])
            self.engine.set_direction(dx, dy)
            return True


    def _space_rebellion_asset_root():
        relative = "minigames/spacerebellion/assets"
        try:
            return ren_loader.transfn(relative)
        except Exception:
            return os.path.join(ren_config.gamedir, relative)


    def _space_rebellion_finish(displayable, aborted):
        result = displayable.engine.result(aborted=aborted)
        print("Space Rebellion finish called:", aborted)
        renpy.return_statement(result)


screen space_rebellion_minigame(displayable=None):
    modal True
    tag menu
    zorder 200
    default stats = {"score": 0, "wave": 0, "health": 0, "max_health": 0,
        "double_shot": 0.0, "rapid_fire": 0.0, "shield": 0.0,
        "game_over": False, "wave_banner": 0.0, "boss_active": False}

    if displayable is None:
        $ displayable = SpaceRebellionDisplayable()
        $ displayable.reset()

    # Refresh stats without interrupting other interactions.
    timer 0.05 repeat True action SetScreenVariable("stats", displayable.engine.snapshot())

    key "K_ESCAPE" action Function(_space_rebellion_finish, displayable, True)
    key "dismiss" action NullAction()
    key "K_RETURN" action NullAction()
    key "K_SPACE" action NullAction()

    add Solid("#00050cdd")

    frame:
        xalign 0.5
        yalign 0.5
        padding (28, 28)
        background Solid("#050912")

        vbox:
            spacing 18
            xalign 0.5

            text "Space Rebellion" size 54
            text "Hold Space or Left Mouse Button to fire." size 24 color "#9ec8ff"

            fixed:
                xsize displayable.width
                ysize displayable.height
                add displayable xpos 0 ypos 0
                if stats["wave_banner"] > 0 and not stats["game_over"]:
                    $ banner_alpha = min(1.0, stats["wave_banner"] / 2.2)
                    $ banner_text = "Wave {}".format(stats["wave"]) if stats["wave"] else "Ready"
                    if stats["boss_active"]:
                        $ banner_text = "Boss Incoming"
                    frame:
                        xalign 0.5
                        yalign 0.5
                        padding (36, 18)
                        background Solid("#0c1f3ed0")
                        at Transform(alpha=banner_alpha)
                        text banner_text size 48 color "#ffffff"
                if stats["game_over"]:
                    frame:
                        xalign 0.5
                        yalign 0.5
                        padding (48, 32)
                        background Solid("#050912e6")
                        vbox:
                            spacing 16
                            text "Mission Failed" size 52 color "#ffc8c2"
                            text "Press Collect Debrief to exit." size 28 color "#dbe3ff"

            $ wave_label = "Wave {}".format(stats["wave"]) if stats["wave"] else "Deployment"

            hbox:
                spacing 40
                xalign 0.5
                text "Score: {0:,}".format(stats["score"]) size 32
                text wave_label size 32
                text "Health: {}/{}".format(stats["health"], stats["max_health"]) size 32
                if stats["rapid_fire"] > 0:
                    text "Rapid Fire {:.1f}s".format(stats["rapid_fire"]) size 32 color "#ffe07a"
                if stats["double_shot"] > 0:
                    text "Spread Shot {:.1f}s".format(stats["double_shot"]) size 32 color "#ffbcf5"
                if stats["shield"] > 0:
                    text "Shield {:.1f}s".format(stats["shield"]) size 32 color "#7cf5d4"
                if stats["boss_active"]:
                    text "Boss Active" size 32 color "#ff8d8d"

            if stats["game_over"]:
                text "Mission failed. Collect your debrief to exit." size 26 color "#ffaba5"
            else:
                text "Move with WASD or arrows. Clear endless waves, grab power-ups, and defeat every fifth-wave boss." size 26 color "#9fc6ff"

            hbox:
                spacing 20
                xalign 0.5
                textbutton "Abort Mission" action Function(_space_rebellion_finish, displayable, True)
                if stats["game_over"]:
                    textbutton "Collect Debrief" action Function(_space_rebellion_finish, displayable, False)
                else:
                    textbutton "Restart" action Function(displayable.reset)


label space_rebellion_minigame:
    $ renpy.pause(0.0, hard=True)
    python:
        displayable = SpaceRebellionDisplayable()
        displayable.reset()
    $ result = renpy.call_screen("space_rebellion_minigame", displayable=displayable)
    $ print("Space Rebellion minigame result:", result)
    return result
