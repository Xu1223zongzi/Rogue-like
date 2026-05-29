import sys
import os
import json

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
map_folder = '第二张地图'

for seed in range(1, num_seeds + 1):
    try:
        # Pass the map_folder string which should match the directory name
        result = generate_room_graph(seed, floor_number=1, map_folder=map_folder)
        
        # Access attributes based on typical graph_map object structure
        main_path_ids = getattr(result, 'main_path_ids', [])
        backtrack_edges = getattr(result, 'backtrack_edges', [])
        
        edges_count = max(0, len(main_path_ids) - 1)
        backtrack_count = len(backtrack_edges)
        
        total_main_path_edges += edges_count
        total_backtrack_edges += backtrack_count
        total_main_path_length += len(main_path_ids)
    except Exception as e:
        print(f"Error for seed {seed}: {e}")

avg_backtrack = total_backtrack_edges / num_seeds
avg_main_path_len = total_main_path_length / num_seeds

print(f"Total Main Path Edges: {total_main_path_edges}")
print(f"Total Backtrack Edges: {total_backtrack_edges}")
print(f"Average Backtrack Edges per Map: {avg_backtrack:.2f}")
print(f"Average Main Path Length: {avg_main_path_len:.2f}")
