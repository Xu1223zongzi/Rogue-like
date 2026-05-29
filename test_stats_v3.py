import sys
import os

sys.path.append(os.getcwd())
try:
    from game.world.graph_map import generate_room_graph
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

total_main_path_edges = 0
total_backtrack_edges = 0
total_main_path_length = 0
num_seeds = 80
success_count = 0
map_folder = '第二张地图'

for seed in range(1, num_seeds + 1):
    try:
        result = generate_room_graph(seed, floor_number=1, map_folder=map_folder)
        main_path_ids = getattr(result, 'main_path_ids', [])
        
        # Check if the result has a graph object (like networkx)
        graph = getattr(result, 'graph', None)
        if graph:
            from networkx import edges
            all_edges = list(graph.edges())
        else:
            all_edges = getattr(result, 'edges', [])
            if hasattr(all_edges, 'edges'): # check if it's a networkx graph directly
                all_edges = list(all_edges.edges())

        main_path_edges = set()
        for i in range(len(main_path_ids) - 1):
            u, v = main_path_ids[i], main_path_ids[i+1]
            main_path_edges.add(tuple(sorted((u, v))))
            
        backtrack_count = 0
        for edge in all_edges:
            u, v = edge[0], edge[1]
            if tuple(sorted((u, v))) not in main_path_edges:
                backtrack_count += 1
        
        total_main_path_edges += max(0, len(main_path_ids) - 1)
        total_backtrack_edges += backtrack_count
        total_main_path_length += len(main_path_ids)
        success_count += 1
    except Exception as e:
        pass

if success_count > 0:
    print(f"Total Main Path Edges: {total_main_path_edges}")
    print(f"Total Backtrack Edges: {total_backtrack_edges}")
    print(f"Average Backtrack Edges per Map: {total_backtrack_edges / success_count:.2f}")
    print(f"Average Main Path Length: {total_main_path_length / success_count:.2f}")
    print(f"Success/Total: {success_count}/{num_seeds}")
