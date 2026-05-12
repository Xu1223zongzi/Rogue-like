import sys
import os
import pygame

os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

try:
    from game.world.level import corridor_tile_is_interior
except ImportError as e:
    print(f'Import Error (level): {e}')
    sys.exit(1)

try:
    from game.scenes.gameplay_scene import GameplayScene
except ImportError as e:
    print(f'Import Error (scene): {e}')
    # List files to debug
    print('Available modules in game/scenes:')
    print(os.listdir('game/scenes'))
    sys.exit(1)

def test_corridor_interior():
    print('Testing corridor_tile_is_interior...')
    grid = [[1]*10 if y==0 or y==4 else [0]*10 for y in range(10)]
    is_interior_ground = corridor_tile_is_interior(grid, 5, 4)
    is_interior_roof = corridor_tile_is_interior(grid, 5, 0)
    print(f'Ground (5, 4) interior: {is_interior_ground}')
    print(f'Roof (5, 0) interior: {is_interior_roof}')
    assert is_interior_ground == True, 'Ground (under tiles) should be interior'
    assert is_interior_roof == False, 'Roof (outer surface) should not be interior'
    print('Corridor interior test passed.')

def test_sword_rain():
    print('Testing sword_rain_plane_y_for_x...')
    scene = GameplayScene.__new__(GameplayScene)
    class MockRoom:
        def __init__(self):
            self.solids = [
                pygame.Rect(0, 120, 100, 10),
                pygame.Rect(0, 280, 100, 10)
            ]
    class MockPlayer:
        def __init__(self):
            self.rect = pygame.Rect(40, 150, 20, 60) # bottom = 210
    scene.level = type('MockLevel', (), {'current_room': MockRoom()})()
    scene.player = MockPlayer()
    
    # Manually check if method exists, some classes might name it differently or it might be in a Mixin
    if not hasattr(scene, 'sword_rain_plane_y_for_x'):
        print('Error: sword_rain_plane_y_for_x method not found in GameplayScene')
        # Check available methods
        # print(dir(scene))
        sys.exit(1)

    target_y = scene.sword_rain_plane_y_for_x(50)
    print(f'Sword rain target Y for x=50: {target_y}')
    assert target_y == 280, f'Expected 280 (ground below player), got {target_y}'
    print('Sword rain plane test passed.')

if __name__ == '__main__':
    try:
        test_corridor_interior()
        test_sword_rain()
        print('All tests completed successfully.')
    except Exception as e:
        print(f'Test failed: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
