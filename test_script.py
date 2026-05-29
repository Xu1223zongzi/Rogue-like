import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

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
        
        # We need to ensure the level has necessary attributes for generate_teleport_portals
        # if the code relies on them. Based on the preview, it checks is_embedded_world_map etc.
        # But the prompt asks to call it directly.
        
        scene.generate_teleport_portals()
        
        # Check components in level.placements
        # Assuming LevelState has placements and portal_connector.edge_key
        
        # We need to find where placements are and how to access portal_connector.edge_key
        # Based on the prompt: count component.name == '??????/T_UP?'
        # And check if placement.point is in portal_connector edge_key set.
        
        edge_keys = set()
        if hasattr(level, 'portal_connector') and hasattr(level.portal_connector, 'edge_key'):
            edge_keys = set(level.portal_connector.edge_key)
        elif hasattr(level, 'portal_connectors'): # maybe it's plural?
             for pc in level.portal_connectors:
                 if hasattr(pc, 'edge_key'):
                     if isinstance(pc.edge_key, (list, set)):
                         edge_keys.update(pc.edge_key)
                     else:
                         edge_keys.add(pc.edge_key)

        if hasattr(level, 'placements'):
            for placement in level.placements:
                if hasattr(placement, 'component') and placement.component.name == TARGET_NAME:
                    total_placements += 1
                    if hasattr(placement, 'point'):
                        if placement.point not in edge_keys:
                            total_missing += 1
    except Exception as e:
        # print(f"Error for seed {seed}: {e}")
        pass

print(f"Total Placements: {total_placements}")
print(f"Total Missing: {total_missing}")
