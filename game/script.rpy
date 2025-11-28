define e = Character("Eileen")

default match_board = None
default match_selected_cell = None
default match_message = "Select two adjacent sigils to swap."
default match_score = 0
default match_turns = 0
default match_target_score = 12
default match_swap_cells = []
default match_match_cells = []
default match_pending_resolution = False
default match_board_locked = False

init python:
    import random

    class MiniMatchBoard(object):
        def __init__(self, size=3, tile_types=None):
            self.size = size
            self.tile_types = tile_types or ["A", "B", "C", "D", "E"]
            self._build_board()

        def _build_board(self):
            attempts = 0
            while True:
                self.grid = [[self._random_tile() for _ in range(self.size)] for _ in range(self.size)]
                if not self.find_matches() or attempts > 25:
                    break
                attempts += 1

        def _random_tile(self):
            return random.choice(self.tile_types)

        def swap_cells(self, a, b):
            (r1, c1), (r2, c2) = a, b
            self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]

        def are_adjacent(self, a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1

        def find_matches(self):
            matches = set()
            size = self.size
            for row in range(size):
                row_vals = self.grid[row]
                if row_vals[0] is not None and len(set(row_vals)) == 1:
                    matches.update((row, col) for col in range(size))

            for col in range(size):
                col_vals = [self.grid[row][col] for row in range(size)]
                if col_vals[0] is not None and len(set(col_vals)) == 1:
                    matches.update((row, col) for row in range(size))

            return matches

        def resolve_all_matches(self):
            cleared = 0
            while True:
                matches = self.find_matches()
                if not matches:
                    break

                for row, col in matches:
                    self.grid[row][col] = None

                cleared += len(matches)
                self._collapse_columns()

            return cleared

        def _collapse_columns(self):
            size = self.size
            for col in range(size):
                column = [self.grid[row][col] for row in range(size) if self.grid[row][col] is not None]
                missing = size - len(column)
                new_tiles = [self._random_tile() for _ in range(missing)]
                combined = new_tiles + column
                for row in range(size):
                    self.grid[row][col] = combined[row]

    MATCH_TILE_SIZE = 120
    MATCH_TILE_SPACING = 10
    MATCH_TILE_STEP = MATCH_TILE_SIZE + MATCH_TILE_SPACING

    def reset_match3_state():
        global match_board, match_selected_cell, match_message, match_score, match_turns
        global match_swap_cells, match_match_cells, match_pending_resolution, match_board_locked
        match_board = MiniMatchBoard()
        match_selected_cell = None
        match_message = "Select two adjacent sigils to swap."
        match_score = 0
        match_turns = 10
        match_swap_cells = []
        match_match_cells = []
        match_pending_resolution = False
        match_board_locked = False

    def handle_match_tile_click(row, col):
        global match_board, match_turns, match_selected_cell, match_message, match_score
        global match_swap_cells, match_match_cells, match_pending_resolution, match_board_locked
        board = match_board
        if not board or match_turns <= 0 or match_board_locked or match_pending_resolution:
            return

        pos = (row, col)

        if match_selected_cell is None:
            match_selected_cell = pos
            match_message = "Choose a neighboring sigil to swap."
            return

        if match_selected_cell == pos:
            match_selected_cell = None
            match_message = "Selection cleared."
            return

        if not board.are_adjacent(match_selected_cell, pos):
            match_selected_cell = None
            match_message = "Sigils must share an edge."
            return

        match_swap_cells = [
            {"start": match_selected_cell, "end": pos},
            {"start": pos, "end": match_selected_cell},
        ]
        board.swap_cells(match_selected_cell, pos)
        match_turns -= 1
        matches = board.find_matches()
        if matches:
            match_match_cells = list(matches)
            match_board_locked = True
            match_pending_resolution = True
            match_message = "Sigils resonating..."
            renpy.restart_interaction()
        else:
            board.swap_cells(match_selected_cell, pos)
            match_message = "No match formed."
        match_selected_cell = None

        if match_turns <= 0 and not match_pending_resolution:
            if match_score >= match_target_score:
                match_message = "Goal reached! Claim your spoils."
            else:
                match_message = "Out of turns. Final score: {}".format(match_score)

    def match_goal_met():
        return match_score >= match_target_score

    def finalize_match_resolution():
        global match_pending_resolution, match_board_locked, match_match_cells
        global match_score, match_message, match_turns
        if not match_pending_resolution or not match_board:
            return

        match_pending_resolution = False
        cleared = match_board.resolve_all_matches()
        if cleared:
            match_score += cleared
            match_message = "Matched {} sigils!".format(cleared)
        else:
            match_message = "Sigils stabilized."

        match_match_cells = []
        match_board_locked = False

        if match_turns <= 0:
            if match_score >= match_target_score:
                match_message = "Goal reached! Claim your spoils."
            else:
                match_message = "Out of turns. Final score: {}".format(match_score)

    def clear_match_swap_effect():
        global match_swap_cells
        match_swap_cells = []

    def get_tile_transforms(row, col):
        transforms = []
        for swap in match_swap_cells:
            if swap.get("end") == (row, col):
                dx = (swap["start"][1] - swap["end"][1]) * MATCH_TILE_STEP
                dy = (swap["start"][0] - swap["end"][0]) * MATCH_TILE_STEP
                transforms.append(match_swap_anim(dx=dx, dy=dy))

        if (row, col) in match_match_cells:
            transforms.append(match_success_anim)

        return tuple(transforms)

style match_tile_button is default:
    padding (16, 16)
    background Solid("#2b1c3d")
    hover_background Solid("#3e2556")
    selected_background Solid("#5b3580")
    xminimum 120
    yminimum 120

style match_tile_button_text is default:
    size 48
    color "#f3edff"

transform match_swap_anim(dx=0, dy=0):
    subpixel True
    xoffset dx
    yoffset dy
    easeout 0.18 xoffset 0 yoffset 0

transform match_success_anim:
    subpixel True
    linear 0.08 zoom 1.1
    linear 0.22 zoom 0.75 alpha 0.0

screen match_minigame():
    modal True
    tag menu
    zorder 200

    add Solid("#000000c8")

    if match_pending_resolution:
        timer 0.45 action Function(finalize_match_resolution)

    if match_swap_cells:
        timer 0.3 action Function(clear_match_swap_effect)

    frame:
        xalign 0.5
        yalign 0.5
        padding (32, 32)
        background Solid("#120b1c")

        vbox:
            spacing 18
            text "Sigil Array Trial" size 54
            text "Score: [match_score] / [match_target_score]" size 36
            text "Turns Remaining: [match_turns]" size 34
            text match_message size 28

            if match_board:
                grid match_board.size match_board.size spacing MATCH_TILE_SPACING:
                    for row in range(match_board.size):
                        for col in range(match_board.size):
                            $ tile = match_board.grid[row][col] or "?"
                            $ is_selected = match_selected_cell == (row, col)
                            $ tile_transforms = get_tile_transforms(row, col)
                            textbutton tile:
                                style_prefix "match_tile"
                                selected is_selected
                                at tile_transforms
                                action Function(handle_match_tile_click, row, col)
                                sensitive match_turns > 0 and not match_board_locked and not match_pending_resolution
            else:
                text "Preparing board..." size 32

            hbox:
                spacing 20
                textbutton "Reset Board" action Function(reset_match3_state)
                if match_turns <= 0:
                    textbutton "Complete Trial" action Return(True)
                else:
                    textbutton "Concede" action Return(False)

label match_minigame:
    $ reset_match3_state()
    $ result = renpy.call_screen("match_minigame")
    return result

transform splash_tag_reveal:
    alpha 0.0
    zoom 0.97
    on show:
        linear 0.6 alpha 1.0 zoom 1.0
    on hide:
        linear 0.4 alpha 0.0 zoom 1.03

transform splash_logo_reveal:
    alpha 0.0
    zoom 1.08
    on show:
        linear 0.9 alpha 1.0 zoom 1.0
    on hide:
        linear 0.4 alpha 0.0 zoom 1.1

transform splash_glow_pulse:
    alpha 0.0
    on show:
        linear 0.6 alpha 0.35
        linear 0.8 alpha 0.12
    on hide:
        linear 0.4 alpha 0.0

transform splash_glow_anchor:
    xalign 0.5
    yalign 0.5
    zoom 1.05

transform splash_tag_anchor:
    xalign 0.5
    yalign 0.32

transform splash_logo_anchor:
    xalign 0.5
    yalign 0.52


label splashscreen:
    # $ _preferences.fullscreen = True
    $ notifications_enabled = False
    scene black with Pause(0.25)
    pause 0.1
    play sound "audio/logo_reveal.mp3"

    show expression Solid("#ff6d3a1e") as splash_glow at splash_glow_anchor, splash_glow_pulse
    show expression Text("POWERED BY", size=48, color="#f7f7f7", outlines=[(3, "#120400", 0, 0)], kerning=3) as splash_tag at splash_tag_anchor, splash_tag_reveal
    pause 0.4
    show expression Text("REN'PY", size=138, color="#ffb347", outlines=[(8, "#2b0a00", 0, 0)]) as splash_logo at splash_logo_anchor, splash_logo_reveal

    pause 2.4

    hide splash_logo with Dissolve(0.45)
    hide splash_tag with Dissolve(0.4)
    hide splash_glow with Dissolve(0.6)

    stop sound fadeout 0.6

    return


label start:
    $ quick_menu = False
    $ toggle_quest_tracker_visibility()
    scene black with fade
    play music "audio/intro_music.mp3" fadein 1.5

    show text "ENTROPYX PROTOTYPE" at truecenter with dissolve
    pause 2.0
    show text "Developed by Knox Emberlyn" at truecenter with dissolve
    pause 1.8
    hide text with dissolve

    # stop music fadeout 1.0
    # $ quick_menu = True
    $ toggle_quest_tracker_visibility()
    $ notifications_enabled = True
    play music "audio/a-robust-crew.mp3" fadein 1.5

    scene cg1

    e "Welcome to Caer Entropy. Before the dignitaries arrive, we capture this overview of the fortress shimmering with fresh wards."

    scene cg2

    e "Here in the war room we brief investors—notice how the runic scryer mirrors any stat or quest they request."

    # scene bg room
    # show eileen happy

    e "Shift+D brings the telemetry overlay to life, while Shift+Q opens the quest ledger."

    e "Our GameState chronicles the keep's champions and vows. Let's stress it like a proper royal demonstration."

    menu:
        "Rally Lady Seris atop the watchtower":
            scene cg3:
                xsize 1920 ysize 1080
            e "Seris grips the banner and rallies the scouts. Loyalty swells along the wall."
            $ game_state.update_character_stat("Lady Seris", "trust", 3)
            $ game_state.update_quest_status("Fortify the Watchtower", "completed")
            e "The rune-shields hum to life; the crowd sees the quest flip to completed without further script edits."

        "Let Sir Galen test the barrow wards":
            scene cg4:
                xsize 1920 ysize 1080
            e "Galen draws on forbidden sigils—effective, if a touch unsettling."
            $ game_state.update_character_stat("Sir Galen", "corruption", 2)
            $ game_state.update_quest_status("Seal the Barrow Gate", "in_progress")
            e "The gate groans but holds, and you can watch its status move to in-progress on the tracker."

    e "Now let's highlight some of the new faces stored inside the data model."

    menu:
        "Consult Mistcaller Veya about the Whispering Mire routes":
            scene cg5:
                xsize 1920 ysize 1080
            e "Veya sketches safe passages through the mire with drifting will-o'-wisps."
            $ game_state.update_character_stat("Mistcaller Veya", "trust", 2)
            $ game_state.update_quest_status("Map the Whispering Mire", "in_progress")
            $ game_state.set_quest_tracking("Map the Whispering Mire", True)
            e "Watch the quest pop onto the HUD as soon as we flip tracking on."

        "Help Archivist Bren decode the Argent Manuscript":
            scene cg6:
                xsize 1920 ysize 1080
            e "Bren coaxes hidden sigils from the Argent Manuscript; the vault wards shiver."
            $ game_state.update_character_stat("Archivist Bren", "trust", 1)
            $ game_state.update_quest_status("Decode the Argent Manuscript", "in_progress")
            $ game_state.set_quest_tracking("Decode the Argent Manuscript", True)
            e "Since that vow was untracked before, the quest tracker immediately adds it now."

    e "Every choice mutates the data model, and the debug utilities echo those shifts instantly. Add more heroes or vows and the system scales without rewiring labels."

    e "If you want to prove that new data can be provisioned live, try one of these sandbox actions."

    menu:
        "Recruit Archer Lys on the fly":
            scene cg7:
                xsize 1920 ysize 1080
            $ lys_exists = game_state.get_character("Archer Lys")
            if not lys_exists:
                $ lys_card = CharacterData("Archer Lys", {"affection": 7, "trust": 6, "corruption": 0})
                $ game_state.add_character(lys_card)
                e "Archer Lys arrives with a fresh telemetry card generated entirely from this choice."
            else:
                e "Lys is already logged, so we just ping her stats panel."

            if not game_state.get_quest("Secure the Skybridge"):
                $ skybridge = QuestData(
                    "Secure the Skybridge",
                    "Clear the rope bridges of raiders so merchants can cross.",
                    status="in_progress",
                    requirements=["Sweep eastern parapet", "Reset warding beacons"],
                )
                $ game_state.add_quest(skybridge, track=True)
                e "The quest HUD instantly lists 'Secure the Skybridge' because we tracked it when adding."
            else:
                e "That quest already exists—feel free to toggle it via Shift+Q if needed."

        "Author a brand-new vow for the envoy":
            scene cg8:
                xsize 1920 ysize 1080
            $ vow_name = "Escort the Moon Envoy"
            if not game_state.get_quest(vow_name):
                $ envoy_quest = QuestData(
                    vow_name,
                    "Guarantee the moon envoy reaches the chapel with her starlit cargo.",
                    status="not_started",
                    requirements=["Brief honor guard", "Sanctify procession route"],
                )
                $ game_state.add_quest(envoy_quest, track=False)
                e "We spawned a vow without auto-tracking it. Open Shift+Q to toggle it when the team is ready."
            else:
                e "The moon envoy vow already sits in the database—we won't duplicate it."

            if not game_state.get_character("Shield-Bearer Otmar"):
                $ otmar = CharacterData("Shield-Bearer Otmar", {"affection": 5, "trust": 9, "corruption": 1})
                $ game_state.add_character(otmar)
                e "Otmar joins the roster to guard the envoy, giving the overlay another stat card without touching core scripts."
            else:
                e "Otmar's already guarding the envoy, so no duplicate entry is created."

    e "Before we adjourn, want to sanity check the rune-matrix that powers our candy-crush diversion?"

    menu:
        "Launch the sigil-matching mini-game":
            call match_minigame
            if match_goal_met():
                e "Nicely done. The telemetry flags the board as stable once you clear enough sigils."
            else:
                e "Even without the victory threshold, the board proves the systems are humming."

        "Skip the diversion for now":
            e "Very well—we can revisit the sigil arrays whenever the pitch needs more sparkle."

    return
