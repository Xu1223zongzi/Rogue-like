import sys
sys.path.append(r"e:/py/pygame_roguelike")
from game.world.graph_map import generate_room_graph
graph = generate_room_graph(1, floor_number=1, map_folder='第二张地图')
print(f"Graph attributes: {dir(graph)}")
print(f"Graph nodes type: {type(graph.nodes)}")
if len(graph.nodes) > 0:
    print(f"Node sample: {graph.nodes[0]}")
    print(f"Node sample attributes: {dir(graph.nodes[0]) if not isinstance(graph.nodes[0], dict) else 'is dict'}")
if len(graph.edges) > 0:
    print(f"Edge sample: {graph.edges[0]}")
