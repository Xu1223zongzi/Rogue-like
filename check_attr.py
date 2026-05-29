import sys
import os

sys.path.append('e:/py/pygame_roguelike')

from game.world.graph_map import generate_room_graph

result = generate_room_graph(1, floor_number=1, map_folder='第二张地图')
print(f'Type: {type(result)}')
print(f'Attributes: {dir(result)}')
if result:
    print(f'main_path_ids: {getattr(result, "main_path_ids", "N/A")}')
    print(f'backtracking_edges: {getattr(result, "backtracking_edges", "N/A")}')
    # Also check for other possible names
    print(f'edges count: {len(getattr(result, "edges", []))}')
