import os
import pygame
import sys
from pathlib import Path

# Add project root to sys.path
project_root = r'e:\py\pygame_roguelike'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Offscreen pygame setup
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

try:
    import game.ui.hud as hud_module
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_draw():
    # Mock route_map data
    route_map = {
        'world_width': 100,
        'world_height': 100,
        'solids': set([(10, 10), (11, 11)]), 
        'player_world_position': (50, 50),
        'fog_reveal_points': [(50, 50), (60, 60)],
        'fog_reveal_radius': 5
    }
    
    # Create surface and rect
    surface = pygame.Surface((200, 200))
    rect = pygame.Rect(0, 0, 200, 200)
    
    try:
        # Based on the error, _draw_world_map_view needs zoom and full_map
        # We'll try common values: zoom=1.0, full_map=False
        hud_module._draw_world_map_view(surface, rect, route_map, zoom=1.0, full_map=False)
        print("ok")
    except Exception as e:
        print(f"Execution Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_draw()
