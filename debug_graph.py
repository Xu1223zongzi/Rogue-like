from game.world.graph_map import generate_room_graph
import sys

sys.path.append('E:/py/pygame_roguelike')

nodes, main_path_ids = generate_room_graph(1, floor_number=1, map_folder='第二张地图')
last_node = main_path_ids[-1]
print(f"Type: {type(last_node)}")
if hasattr(last_node, 'map_file'):
    print(f"Map file: {last_node.map_file}")
else:
    # If main_path_ids contains IDs, use them to index nodes
    # Assuming nodes is a dict or list
    actual_node = nodes[last_node] if isinstance(nodes, dict) else [n for n in nodes if n.id == last_node][0]
    print(f"Actual node map file: {actual_node.map_file}")

print(f"Main path IDs sample: {main_path_ids[:2]}")
