import sys
import os

sys.path.append(os.getcwd())

from game.world.graph_map import generate_room_graph

seed = 1
floor_number = 1
map_folder = '第二张地图'

result = generate_room_graph(seed=seed, floor_number=floor_number, map_folder=map_folder)

print(f"Result type: {type(result)}")
print(f"Nodes type: {type(result.nodes)}")
if isinstance(result.nodes, dict):
    print(f"Nodes keys (first 5): {list(result.nodes.keys())[:5]}")
elif isinstance(result.nodes, list):
    print(f"Nodes length: {len(result.nodes)}")
    if len(result.nodes) > 0:
        print(f"First node: {result.nodes[0]}")

print(f"Main path IDs: {result.main_path_ids}")
