from game.world.graph_map import generate_room_graph
import sys

sys.path.append('E:/py/pygame_roguelike')

data = generate_room_graph(1, floor_number=1, map_folder='第二张地图')
print(f"Main path IDs: {data.main_path_ids}")
for node in data.nodes:
    if node.node_id in data.main_path_ids:
        print(f"Main Path Node {node.node_id}: {node.map_file}")
