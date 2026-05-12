import sys
import pygame
import os

sys.path.append(r"e:\py\pygame_roguelike")

pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)

try:
    import game.ui.hud as hud

    # From previous signature check:
    # (surface: 'pygame.Surface', bounds: 'pygame.Rect', route_map: 'dict[str, object]', 
    # zoom: 'float', full_map: 'bool', view_focus: 'tuple[float, float] | None' = None)

    world_width, world_height = 1000, 1000
    route_map = {
        'world_width': world_width,
        'world_height': world_height,
        'solids': set([(100, 100), (200, 200)]),
        'player_world_position': (500, 500),
        'fog_reveal_points': [(500, 500), (520, 520)],
        'fog_reveal_radius': 100
    }
    
    surface = pygame.Surface((800, 600))
    bounds = pygame.Rect(50, 50, 700, 500)
    zoom = 1.0
    full_map = False
    view_focus = (500, 500)

    hud._draw_world_map_view(
        surface=surface, 
        bounds=bounds, 
        route_map=route_map, 
        zoom=zoom, 
        full_map=full_map, 
        view_focus=view_focus
    )
    print("ok")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    pygame.quit()
