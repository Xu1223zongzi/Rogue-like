# Art Resource Layout

This folder is the stable entry point for resource-driven visuals.

- `manifests/actor_appearances.json`: actors are now classified under `players`, `enemies`, and future `summons`.
- `manifests/ui_skin.json`: panel and UI frame image paths keyed by panel name.
- `manifests/ui_icons.json`: slot and organ icon image paths keyed by icon name and item id.
- `manifests/scene_visuals.json`: scene art is now classified under `props`, `gates`, `portals`, `combat`, and `overlays`.
- `actors/`: future player, enemy, boss, summon sprite sheets or single-frame images.
- `ui/`: future HUD, panel, icon, and overlay images.
- `scene/`: future pickups, gates, props, environment overlays, and gameplay effect images.

The runtime is wired for `resource-first, code-fallback` rendering.
If a manifest entry is empty or the image file is missing, the old pygame-drawn fallback remains active.

## Supported resource forms

Every visual entry can now be provided in either of these two forms:

1. Complete effect / complete sprite

```json
{
	"whole": ["scene/combat/slash_full.png"]
}
```

2. Split layers / connected parts

```json
{
	"parts": {
		"base": ["scene/combat/slash_base.png"],
		"glow": ["scene/combat/slash_glow.png"],
		"spark": ["scene/combat/slash_spark.png"]
	},
	"part_order": ["base", "glow", "spark"]
}
```

The resolver will use `whole` first when present. If `whole` is empty, it automatically connects and draws the split `parts` in `part_order`.

Legacy short forms still work:

```json
"default": ["actors/player/body.png", "actors/player/weapon.png"]
```

## Current classification

- Actor appearances: `players`, `enemies`
- Scene visuals: `props`, `gates`, `portals`, `combat`, `overlays`
- Combat visuals already routed through manifests include afterimages, projectile bodies/trails, slash lines, impact bursts, perfect dodge flash, parry flash, parry clash, finisher overlay, and execution flash.

## Common actor state keys

- Player: `brain_sword`, `brain_sword_attack`, `brain_scripture`, `brain_scripture_attack`, `fusion_brain_sword`, `steel_guard`, plus generic action and movement states.
- Boss: `boss_rift`, `boss_rift_attack`, `boss_rift_attack_windup`, `boss_invade`, plus generic action and movement states.
- Elite knight: `elite_knight_ranged`, `elite_knight_ranged_attack`, `elite_knight_melee`, `elite_knight_melee_attack`, `friendly`, plus generic action and movement states.
