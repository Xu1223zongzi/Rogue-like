import os
import sys
sys.path.append(os.getcwd())
from game.world.graph_map import generate_room_graph

def run_stats():
    less_zero = 0
    greater_zero = 0
    equal_zero = 0
    success_count = 0

    for seed in range(1, 81):
        try:
            result = generate_room_graph(seed, floor_number=1, map_folder='第二张地图')
            success_count += 1
            
            # Create a mapping for easy lookup
            node_map = {node.node_id: node for node in result.nodes}
            
            # The query mentions 'main_path_ids' which usually defines the sequence of node IDs.
            # Edges on the main path are (main_path_ids[i], main_path_ids[i+1])
            # lane_delta = child_node.lane - parent_node.lane
            
            path = result.main_path_ids
            for i in range(len(path) - 1):
                u_id = path[i]
                v_id = path[i+1]
                
                u_node = node_map[u_id]
                v_node = node_map[v_id]
                
                delta = v_node.lane - u_node.lane
                
                if delta < 0:
                    less_zero += 1
                elif delta > 0:
                    greater_zero += 1
                else:
                    equal_zero += 1
        except Exception as e:
            continue

    print(f"Success Count: {success_count}")
    print(f"lane_delta < 0: {less_zero}")
    print(f"lane_delta > 0: {greater_zero}")
    print(f"lane_delta == 0: {equal_zero}")

if __name__ == '__main__':
    run_stats()
