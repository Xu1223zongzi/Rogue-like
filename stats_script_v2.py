import sys
import os

sys.path.append('e:/py/pygame_roguelike')

try:
    from game.world.graph_map import generate_room_graph
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)

success_count = 0
failure_count = 0
total_main_path_edges = 0
total_backtracking_edges = 0

for seed in range(1, 81):
    try:
        result = generate_room_graph(seed, floor_number=1, map_folder='第二张地图')
        
        if result:
            success_count += 1
            # Main path edges
            main_path_edges = len(result.main_path_ids) - 1
            if main_path_edges < 0: main_path_edges = 0
            total_main_path_edges += main_path_edges
            
            # Count backtracking edges: outgoing_id < node_id (assuming node_id 
            # represents depth/order, though parent/child relationship is better)
            # Actually, a backtrack edge in this context likely means an edge to a node with smaller depth.
            backtrack_count = 0
            node_depths = {node.node_id: node.depth for node in result.nodes}
            for node in result.nodes:
                for out_id in node.outgoing_ids:
                    if node_depths.get(out_id, 0) <= node.depth:
                        backtrack_count += 1
            
            total_backtracking_edges += backtrack_count
        else:
            failure_count += 1
    except Exception as e:
        failure_count += 1

print(f'Success: {success_count}')
print(f'Failure: {failure_count}')
print(f'Total Main Path Edges: {total_main_path_edges}')
print(f'Total Backtracking Edges: {total_backtracking_edges}')
if success_count > 0:
    print(f'Avg Backtracking Edges: {total_backtracking_edges / success_count:.2f}')
    print(f'Avg Main Path Length: {total_main_path_edges / success_count:.2f}')
else:
    print('Avg Backtracking Edges: 0')
    print('Avg Main Path Length: 0')
