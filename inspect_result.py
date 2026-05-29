import os
import sys
sys.path.append(os.getcwd())
from game.world.graph_map import generate_room_graph

print("Testing seed 1...")
try:
    result = generate_room_graph(1, floor_number=1, map_folder='第二张地图')
    print(f"Type: {type(result)}")
    print(f"Attributes: {dir(result)}")
    if hasattr(result, 'edges'):
        print(f"Edges length: {len(result.edges)}")
        first_edge_id = list(result.edges.keys())[0]
        first_edge = result.edges[first_edge_id]
        print(f"Edge attributes: {dir(first_edge)}")
    if hasattr(result, 'main_path_ids'):
        print(f"Main path ids: {result.main_path_ids}")
except Exception as e:
    print(f"Error: {e}")
