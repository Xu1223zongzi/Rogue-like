import os
import sys
sys.path.append(os.getcwd())
from game.world.graph_map import generate_room_graph

try:
    result = generate_room_graph(1, floor_number=1, map_folder='第二张地图')
    print(f"Nodes type: {type(result.nodes)}")
    if isinstance(result.nodes, list) and len(result.nodes) > 0:
        first_node = result.nodes[0]
        print(f"First node attrs: {dir(first_node)}")
        # Look for lane or delta
        for attr in dir(first_node):
            if 'lane' in attr.lower() or 'delta' in attr.lower():
                print(f"Found match in node: {attr} = {getattr(first_node, attr)}")
        
        if hasattr(first_node, 'connections') and first_node.connections:
            first_conn = first_node.connections[0]
            print(f"First conn attrs: {dir(first_conn)}")
            for attr in dir(first_conn):
                if 'lane' in attr.lower() or 'delta' in attr.lower() or 'id' in attr.lower():
                    print(f"Found match in conn: {attr} = {getattr(first_conn, attr)}")
except Exception as e:
    import traceback
    traceback.print_exc()
