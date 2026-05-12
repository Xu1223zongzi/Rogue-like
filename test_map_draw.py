import os
import sys

# Add the project root to sys.path
sys.path.append(r"e:\py\pygame_roguelike")

# Mock pygame before importing anything that might use it
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)

try:
    from game.ui.hud import HUD
    from unittest.mock import MagicMock

    # Create a mock HUD instance or just check if the function exists
    # Based on the prompt, we need to call game.ui.hud._draw_world_map_view
    # Usually this might be a static method or we need an instance
    
    # We will try to import it and call it. 
    # Since it starts with _, it might be a method of HUD or a module level function
    
    import game.ui.hud as hud_module

    # Prepare route_map data
    route_map = {
        'world_width': 100,
        'world_height': 100,
        'solids': set(), # or list of tuples
        'player_world_position': (50, 50),
        'fog_reveal_points': [(50, 50), (51, 51)],
        'fog_reveal_radius': 5
    }

    # Create a surface to draw on
    surface = pygame.Surface((800, 600))

    # Check if it is a method of HUD class or a function in the module
    if hasattr(hud_module, "_draw_world_map_view"):
        hud_module._draw_world_map_view(surface, route_map)
        print("ok")
    elif hasattr(HUD, "_draw_world_map_view"):
        # If it is an instance method, we might need a dummy instance
        hud_inst = MagicMock(spec=HUD)
        # Note: calling the unbound method with an instance if it's defined in the class
        HUD._draw_world_map_view(hud_inst, surface, route_map)
        print("ok")
    else:
        print("Error: _draw_world_map_view not found")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    pygame.quit()
