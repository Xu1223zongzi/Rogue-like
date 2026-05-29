import sys
import inspect

project_root = r'E:/py/pygame_roguelike'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from game.entities.actors import Player
from game.scenes.gameplay_scene import GameplayScene

def get_method_source(cls, method_name):
    try:
        method = getattr(cls, method_name)
        return inspect.getsource(method)
    except:
        return ""

print("--- Player Halo/Barrier Logic ---")
p_source = inspect.getsource(Player)
lines = [l.strip() for l in p_source.split('\n') if any(x in l.lower() for x in ['absorbed', 'barrier', 'halo', 'count'])]
for l in lines:
    print(l)

print("\n--- GameplayScene.cast_knight_spirit Deep Dive ---")
gs_source = get_method_source(GameplayScene, 'cast_knight_spirit')
print(gs_source)
