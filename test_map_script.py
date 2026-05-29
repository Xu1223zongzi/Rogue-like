import os
import sys
import pygame

# Set SDL to use dummy video driver for offscreen rendering
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Add project root to sys.path
sys.path.insert(0, 'E:/py/pygame_roguelike')

try:
    pygame.init()
    # Mock some basic pygame requirements for HUD if needed
    # (Usually hud.py might import constants or fonts)
    from game.ui.hud import _draw_world_map_view
    
    # Construct minimal route_map
    route_map = {
        "world_width": 1000.0,
        "world_height": 1000.0,
        "solids": [
            pygame.Rect(100, 100, 50, 50),
            pygame.Rect(200, 300, 100, 20)
        ],
        "player_world_position": (125, 125),
        "fog_reveal_points": [(120.0, 120.0)],
        "fog_reveal_radius": 160.0
    }
    
    # Create surface and bounds
    surface = pygame.Surface((800, 600))
    bounds = pygame.Rect(10, 10, 780, 580)
    
    # Call the function
    # Signature: surface, bounds, route_map, zoom, full_map, view_focus=None
    _draw_world_map_view(
        surface=surface,
        bounds=bounds,
        route_map=route_map,
        zoom=1.0,
        full_map=True
    )
    
    print("ok")
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    pygame.quit()
