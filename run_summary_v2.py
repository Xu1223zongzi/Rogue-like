import sys
import os
from unittest.mock import MagicMock

sys.path.append('e:/py/pygame_roguelike')
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
        level = LevelState(seed=seed, floor_number=1)
        scene = GameplayScene.__new__(GameplayScene)
        scene.level = level
        
        if hasattr(scene, 'generate_teleport_portals'):
            scene.generate_teleport_portals()
        else:
            print(f'Seed {seed}: generate_teleport_portals not found')
            continue

        connector_placements = getattr(level, 'connector_placements', [])
        t_or_cross_count = 0
        non_base_l_connectors = []
        
        for p in connector_placements:
            name = p.component.name
            if name.startswith('??????/T_') or '??' in name:
                t_or_cross_count += 1
            if not name.startswith('??????/L_'):
                non_base_l_connectors.append(p)

        portals = getattr(level, 'portals', {})
        portal_connector_count = sum(1 for pid in portals if pid.startswith('portal_connector_'))
        
        print(f'Seed {seed}: T/Cross={t_or_cross_count}, PortalConnectors={portal_connector_count}')
        
        if portal_connector_count < len(non_base_l_connectors):
            print(f'  Warning: Portal count ({portal_connector_count}) < Non-Base-L count ({len(non_base_l_connectors)})')
            for p in non_base_l_connectors[:3]:
                print(f'  Sample: {p.component.name} at {getattr(p, "point", "N/A")}')

if __name__ == "__main__":
    run_task()
