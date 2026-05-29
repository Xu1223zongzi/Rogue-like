import sys
import os
import pygame

# Add current directory to path
sys.path.append(os.getcwd())

# Dummy pygame for headless execution
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((1, 1))

from game.world.level import LevelState
from game.scenes.gameplay_scene import GameplayScene

total_placements = 0
total_missing = 0
TARGET_NAME = '??????/T_UP?'

for seed in range(1, 81):
    try:
        level = LevelState(seed=seed, floor_number=1)
        scene = GameplayScene.__new__(GameplayScene)
        scene.level = level
        
        # In actual project, level generation might need a call
        # Check if LevelState needs to be initialized/generated
        # Assuming generate_teleport_portals triggers enough or level gen is in __init__
        scene.generate_teleport_portals()
        
        edge_keys = set()
        # Look for portal_connector in the scene or level
        pc = getattr(level, 'portal_connector', None)
        if pc and hasattr(pc, 'edge_key'):
            edge_keys = set(pc.edge_key)

        for placement in getattr(level, "connector_placements", []):
            name = getattr(placement.component, "name", "")
            if name == TARGET_NAME:
                total_placements += 1
                pt = getattr(placement, "point", None)
                if pt not in edge_keys:
                    total_missing += 1
    except Exception:
        pass

print(f"Total Placements: {total_placements}")
print(f"Total Missing: {total_missing}")
