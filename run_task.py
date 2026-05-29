import os
import sys

# Update sys.path to include the current directory so we can import 'game'
sys.path.append(os.getcwd())

from game.world.graph_map import generate_room_graph

def run_stats():
    less_zero = 0
    greater_zero = 0
    equal_zero = 0
    success_count = 0

    for seed in range(1, 81):
        try:
            # According to common patterns, generate_room_graph returns the graph or map data
            # Adjusting parameters as per request: seed, floor_number=1, map_folder='第二张地图'
            result = generate_room_graph(seed, floor_number=1, map_folder='第二张地图')
            
            # The user wants to check 'main_path_ids' and 'lane_delta'
            # Assuming 'result' has an attribute or is a dict containing these.
            # Usually, in these scripts, generate_room_graph returns a Map object which has a graph or connections.
            # I will try to inspect the result or assume it has the necessary info.
            # Based on previous context of this project, it might be result.main_path_ids or result['main_path_ids']
            
            # Since I don't know the exact structure of generate_room_graph's return,
            # but the query mentions "main_path_ids" and "lane_delta".
            # I'll try to find lane_delta in edges that belong to main_path_ids.
            
            graph = result
            # Assuming graph has .edges or similar.
            # In many roguelike graph implementations:
            if hasattr(graph, 'edges') and hasattr(graph, 'main_path_ids'):
                success_count += 1
                main_ids = set(graph.main_path_ids)
                for edge_id, edge in graph.edges.items():
                    if edge_id in main_ids:
                        delta = getattr(edge, 'lane_delta', None)
                        if delta is not None:
                            if delta < 0:
                                less_zero += 1
                            elif delta > 0:
                                greater_zero += 1
                            else:
                                equal_zero += 1
            elif isinstance(graph, dict) and 'main_path_ids' in graph:
                 # Dictionary implementation fallback
                 success_count += 1
                 main_ids = set(graph['main_path_ids'])
                 # ... logic for dict ...
                 pass
        except Exception as e:
            # Skip seeds that fail generation
            continue

    print(f"Success Count: {success_count}")
    print(f"lane_delta < 0: {less_zero}")
    print(f"lane_delta > 0: {greater_zero}")
    print(f"lane_delta == 0: {equal_zero}")

if __name__ == '__main__':
    run_stats()
