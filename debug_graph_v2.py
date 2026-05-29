from game.world.graph_map import generate_room_graph
import sys

sys.path.append('E:/py/pygame_roguelike')

data = generate_room_graph(1, floor_number=1, map_folder='第二张地图')
print(f"Data attributes: {dir(data)}")

if hasattr(data, 'main_path_ids') and hasattr(data, 'nodes'):
    last_id = data.main_path_ids[-1]
    # Check if nodes is a dict or list
    if isinstance(data.nodes, dict):
        last_node = data.nodes[last_id]
    else:
        last_node = next(n for n in data.nodes if n.id == last_id)
    print(f"Last node map_file: {last_node.map_file}")
