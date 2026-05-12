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
        # Check if it's a top-level function in the module
        if hasattr(hud_module, '_draw_world_map_view'):
            hud_module._draw_world_map_view(surface, rect, route_map)
            print("ok")
        else:
            print("_draw_world_map_view not found in game.ui.hud")
            # If not module level, it might be inside draw_hud? No, it's defined with 'def'.
    except Exception as e:
        print(f"Execution Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_draw()
