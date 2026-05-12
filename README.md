# Side-Scrolling Action Roguelite Framework

This project is a 2D side-scrolling pygame framework aimed at games in the same broad direction as Dead Cells.
The focus is not cloning content. The goal is to give you a stable technical base for action-platform combat,
room progression, camera follow, and future roguelite systems.

## Current Scope

- Side-scrolling camera and room-based progression.
- Stable fixed-timestep update loop.
- Platformer movement with acceleration, jump buffer, coyote time, and gravity.
- Melee combat with action states, startup, active frames, recovery, hurt stun, and dash invulnerability.
- Enemy patrol/chase behavior.
- Room gating and linear progression through connected combat rooms.
- Placeholder visuals so the framework runs without art assets.

## Controls

- Move: A / D or Left / Right
- Jump: W / Up / Space
- Attack: J / Left Mouse Button
- Dash: Left Shift / Right Shift
- Pause: Esc
- Confirm: Enter

## Run

Run [main.py](main.py) with the configured Python interpreter.

## Suggested Next Steps

- Replace placeholder shapes with sprite animation and hit effects.
- Add wall jump, ledge drop, dodge i-frames, ranged skills, and loot.
- Move room and enemy definitions into external data files.
- Add procedural room pools, upgrades, and save/load meta progression.