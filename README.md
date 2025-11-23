# EntropyX Prototype

A medieval-themed Ren'Py 8.5 prototype that demonstrates a data-driven quest and character management loop. Built to showcase how narrative prototyping can coexist with systemic telemetry inside Ren'Py.

## Features
- **Gameplay Data Model** – `CharacterData`, `QuestData`, and `GameState` classes handle roster updates, quest tracking, and notification routing.
- **Debug + HUD Overlays** – Shift+D spawns the telemetry overlay, Shift+Q opens the quest manager, and Shift+T toggles the quest tracker HUD.
- **Notification Layer** – Built-in `renpy.notify` toasts report stat changes, quest updates, and character events.

## Requirements
- **Game Engine**: Ren'Py 8.5 or newer.
- Audio files referenced in `game/audio/` should remain alongside the `.rpy` sources. (Source: CHOSIC And PIXABAY)

## Running the Demo
1. Open the project in the Ren'Py launcher.
2. Select **EntropyX** and choose **Launch Project**.
3. Interact with the scripted demo to trigger overlays, notifications, and data mutations.

## Controls & Shortcuts
- `Shift + D`: Toggle the telemetry debug overlay.
- `Shift + Q`: Open the quest manager panel for filtering/tracking quests.
- `Shift + T`: Show or hide the floating quest tracker HUD.

## Licensing
Released under the MIT License. See [LICENSE](LICENSE) for details. Copyright © 2025 Knox Emberlyn.
