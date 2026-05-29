import sys
import os

# Add project root to sys.path
project_root = 'E:/py/pygame_roguelike'
sys.path.append(project_root)

# Mock pygame before imports if necessary
import pygame
pygame.display.set_mode((1, 1), pygame.HIDDEN)

from game.world.level import LevelState
from game.scenes.gameplay_scene import GameplayScene

results = []

for seed in range(1, 21):
    level_state = LevelState(seed=seed, floor_number=1)
    # We need to create a GameplayScene instance. 
    # GameplayScene(app, level_state)
    # Since we only want to call generate_teleport_portals, let's see if we can instantiate it minimally.
    class MockApp:
        def __init__(self):
            self.screen = pygame.Surface((1,1))
            self.clock = pygame.time.Clock()
    
    app = MockApp()
    try:
        scene = GameplayScene(app, level_state)
        # Note: GameplayScene.__init__ might call generate_teleport_portals already.
        # Let's check connector_placements in level_state.world (AssembledWorld)
        world = level_state.world
        connector_placements = getattr(world, 'connector_placements', [])
        num_placements = len(connector_placements)
        
        # Count portals
        portals = getattr(scene, 'teleport_portals', [])
        # If teleport_portals is not populated in __init__, we call it.
        if not portals:
             portals = scene.generate_teleport_portals()
             
        connector_portals = [p for p in portals if getattr(p, 'portal_id', '').startswith('portal_connector_')]
        num_connector_portals = len(connector_portals)
        
        results.append({
            'seed': seed,
            'placements': num_placements,
            'portals': num_connector_portals
        })
    except Exception as e:
        results.append({'seed': seed, 'error': str(e)})

# Output results
total_placements = 0
total_portals = 0
anomalies = []

for res in results:
    if 'error' in res:
        print(f"Seed {res['seed']}: Error {res['error']}")
        continue
    
    total_placements += res['placements']
    total_portals += res['portals']
    if res['portals'] < res['placements']:
        anomalies.append(res['seed'])
    print(f"Seed {res['seed']}: Placements={res['placements']}, Portals={res['portals']}")

print(f"\nTotal Placements: {total_placements}")
print(f"Total Portals: {total_portals}")
print(f"Has anomaly: {'Yes' if anomalies else 'No'}")
if anomalies:
    print(f"First 3 anomalies: {anomalies[:3]}")
