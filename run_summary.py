import sys
import os

# Add the project root to sys.path
sys.path.append('e:/py/pygame_roguelike')

# Mocking modules that might cause issues in a terminal environment (like pygame)
from unittest.mock import MagicMock
sys.modules['pygame'] = MagicMock()
sys.modules['pygame.mixer'] = MagicMock()

try:
    from game.world.level import LevelState
    from game.scenes.gameplay_scene import GameplayScene
except ImportError as e:
    print(f'Import Error: {e}')
    sys.exit(1)

def run_task():
    for seed in range(1, 21):
        # Create LevelState
        level = LevelState(seed=seed, floor_number=1)
        
        # Instantiate GameplayScene without calling __init__
        scene = GameplayScene.__new__(GameplayScene)
        scene.level = level
        
        # Call generate_teleport_portals
        if hasattr(scene, 'generate_teleport_portals'):
            scene.generate_teleport_portals()
        else:
            print(f'Seed {seed}: generate_teleport_portals not found in GameplayScene')
            continue

        # Stats
        connector_placements = getattr(level, 'connector_placements', [])
        
        t_or_cross_count = 0
        non_base_l_connectors = []
        
        for p in connector_placements:
            name = p.component.name
            if name.startswith('基础连接通道/T_') or '十字' in name:
                t_or_cross_count += 1
            
            # Identify non-base-L connectors (excluding T and Cross for finding 'missing' portals)
            # Query implies comparison between 'connector portals' and 'non-base-L connectors'
            # Let's check what '基础L连接件' means. Assume it is something like '基础连接通道/L_'
            if not (name.startswith('基础连接通道/L_')):
                non_base_l_connectors.append(p)

        portal_connector_count = 0
        portals = getattr(level, 'portals', [])
        for portal_id in portals:
            if portal_id.startswith('portal_connector_'):
                portal_connector_count += 1
        
        print(f'Seed {seed}: T/Cross={t_or_cross_count}, PortalConnectors={portal_connector_count}')
        
        if portal_connector_count < len(non_base_l_connectors):
            print(f'  Warning: Portal count ({portal_connector_count}) < Non-Base-L count ({len(non_base_l_connectors)})')
            # Find which ones are missing portals? The query asks for missing ones.
            # Assuming 'portal_connector_{placement_id}' or similar mapping
            # Just print the first few non-base-L placements as samples as requested.
            for p in non_base_l_connectors[:3]:
                print(f'  Sample Missing/Non-Base-L: {p.component.name} at {getattr(p, \"point\", \"N/A\")}')

if __name__ == '__main__':
    run_task()
