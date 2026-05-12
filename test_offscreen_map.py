import os
import pygame
import sys

# Add the project root to sys.path
sys.path.append(r'e:\py\pygame_roguelike')

# Mock necessary environment for pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

try:
    from game.ui.hud import HUD
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

class MockHUD(HUD):
    def __init__(self):
        # We don't call super().__init__ to avoid complex dependencies
        pass

def test_draw():
    hud = MockHUD()
    # Mock route_map data
    route_map = {
        'world_width': 100,
        'world_height': 100,
        'solids': set(), # Empty set for simplicity
        'player_world_position': (50, 50),
        'fog_reveal_points': [(50, 50), (60, 60)],
        'fog_reveal_radius': 5
    }
    
    # Create a surface to draw on
    surface = pygame.Surface((800, 600))
    rect = pygame.Rect(0, 0, 800, 600)
    
    try:
        # Call the target method
        # Note: HUD._draw_world_map_view is likely an instance method
        HUD._draw_world_map_view(hud, surface, rect, route_map)
        print("ok")
    except Exception as e:
        print(f"Execution Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_draw()
