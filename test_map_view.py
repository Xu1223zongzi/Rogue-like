import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(r"e:\py\pygame_roguelike").resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pygame

# Need to set video driver to dummy for offscreen testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

try:
    from game.ui.hud import _draw_world_map_view
    
    # Setup parameters
    surface = pygame.Surface((800, 600), pygame.SRCALPHA)
    bounds = pygame.Rect(50, 50, 700, 500)
    route_map = {
        "world_width": 1000.0,
        "world_height": 1000.0,
        "solids": [pygame.Rect(100, 100, 50, 50)],
        "player_world_position": (500, 500),
        "fog_reveal_points": [(120, 120), (240, 180)],
        "fog_reveal_radius": 160.0
    }
    zoom = 1.0
    full_map = True

    # Call the method
    _draw_world_map_view(surface, bounds, route_map, zoom, full_map)
    print("ok")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    pygame.quit()
