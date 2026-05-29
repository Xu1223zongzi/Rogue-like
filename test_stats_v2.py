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
        # In this codebase, if result is a RoomGraph, backtrack edges are likely in 'edges' 
        # but filtered for those not in the main path.
        # However, looking at the code (implied), result.edges likely contains all edges.
        # Let's check for a property called 'backtrack_edges' or calculate it.
        
        all_edges = getattr(result, 'edges', [])
        backtrack_edges = []
        
        # Build set of main path node pairs
        main_path_edges = set()
        for i in range(len(main_path_ids) - 1):
            u, v = main_path_ids[i], main_path_ids[i+1]
            main_path_edges.add(tuple(sorted((u, v))))
            
        for edge in all_edges:
            # edge might be (u, v, attr_dict) or (u, v)
            u, v = edge[0], edge[1]
            if tuple(sorted((u, v))) not in main_path_edges:
                backtrack_edges.append(edge)
        
        edges_count = max(0, len(main_path_ids) - 1)
        backtrack_count = len(backtrack_edges)
        
        total_main_path_edges += edges_count
        total_backtrack_edges += backtrack_count
        total_main_path_length += len(main_path_ids)
        success_count += 1
    except Exception:
        pass

if success_count > 0:
    avg_backtrack = total_backtrack_edges / success_count
    avg_main_path_len = total_main_path_length / success_count
    print(f"Total Main Path Edges (successful maps): {total_main_path_edges}")
    print(f"Total Backtrack Edges (successful maps): {total_backtrack_edges}")
    print(f"Average Backtrack Edges per Map: {avg_backtrack:.2f}")
    print(f"Average Main Path Length: {avg_main_path_len:.2f}")
    print(f"Successful Generations: {success_count}/{num_seeds}")
else:
    print("No maps were successfully generated.")
