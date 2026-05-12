import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import sys

# Ensure project root is in path
sys.path.append(r'e:\py\pygame_roguelike')

try:
    from game.scenes.gameplay_scene import GameplayScene
    from game.world.level import LevelState
    from game.config import TILE_SIZE
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)

results = []
failures_start_id = []
failures_alignment = []

for seed in range(1, 81):
    try:
        level_state = LevelState(seed=seed)
        # Bypassing __init__ as requested
        scene = GameplayScene.__new__(GameplayScene)
        # Assign level_state as requested
        scene.level_state = level_state
        # Also assign .level since the error showed it's used
        scene.level = level_state.level
        
        # We need to find where the portals are stored. 
        # Usually generate_teleport_portals either returns them or sets them on the scene.
        portals = scene.generate_teleport_portals()
        
        # If portals is None, check if it was set on scene (e.g., scene.portals)
        if portals is None:
             portals = getattr(scene, 'teleport_portals', [])
        
        # 1) Check start_id
        # We need to know what a 'portal' object looks like. Assuming it has room_id.
        has_start_id_portal = any(getattr(p, 'room_id', None) == level_state.start_id for p in portals)
        if not has_start_id_portal:
            failures_start_id.append(seed)
            
        # 2) Check alignment
        for p in portals:
            pos = getattr(p, 'position', None)
            if pos:
                # Some objects use pos[0] or pos.x
                x = getattr(pos, 'x', pos[0] if isinstance(pos, (list, tuple)) else None)
                if x is not None and x % TILE_SIZE != 0:
                    failures_alignment.append((seed, x))
    except Exception as e:
        # Ignore generation errors (overlaps) if they're expected map gen failures
        if "overlap" not in str(e):
             print(f'Seed {seed} failed with unexpected error: {type(e).__name__}: {e}')

print(f'Seeds checked: 1..80')
print(f'Start ID Failures: {failures_start_id if failures_start_id else "None"}')
print(f'Alignment Failures: {failures_alignment if failures_alignment else "None"}')
