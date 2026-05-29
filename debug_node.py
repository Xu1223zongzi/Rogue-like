from game.world.graph_map import generate_room_graph
import sys

sys.path.append('E:/py/pygame_roguelike')

data = generate_room_graph(1, floor_number=1, map_folder='第二张地图')
print(f"Nodes type: {type(data.nodes)}")
first_node = data.nodes[0]
print(f"Node attributes: {dir(first_node)}")
