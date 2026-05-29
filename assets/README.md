# Art Resource Layout

This folder is the stable entry point for resource-driven visuals.

- `manifests/actor_appearances.json`: actor sprite paths keyed by actor type and state.
- `manifests/ui_skin.json`: panel and UI frame image paths keyed by panel name.
- `actors/`: future player, enemy, boss, summon sprite sheets or single-frame images.
- `ui/`: future HUD, panel, icon, and overlay images.

The runtime is already wired for `resource-first, code-fallback` rendering.
If a manifest entry is empty or the image file is missing, the old pygame-drawn fallback remains active.
