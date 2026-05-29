import os
import sys
sys.path.append(os.getcwd())
from game.world.graph_map import generate_room_graph

print("Testing seed 1 nodes/connections...")
try:
    result = generate_room_graph(1, floor_number=1, map_folder='第二张地图')
    if result.nodes:
        first_node_id = list(result.nodes.keys())[0]
        first_node = result.nodes[first_node_id]
        print(f"Node attributes: {dir(first_node)}")
        if hasattr(first_node, 'connections'):
            print(f"First node connections: {first_node.connections}")
            if first_node.connections:
                first_conn = first_node.connections[0]
                print(f"Connection type: {type(first_conn)}")
                print(f"Connection attributes: {dir(first_conn)}")
except Exception as e:
    print(f"Error: {e}")
