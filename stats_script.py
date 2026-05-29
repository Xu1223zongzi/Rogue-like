import sys
import os

# Add current directory to path to import game
sys.path.append(os.getcwd())

try:
    from game.world.graph_map import generate_room_graph
except ImportError as e:
    print(f'ImportError: {e}')
    sys.exit(1)

success_count = 0
fail_count = 0
total_main_path_edges = 0
total_depth_back_edges = 0
total_lane_up_edges = 0
total_lane_down_edges = 0
total_main_path_length = 0

for seed in range(1, 81):
    try:
        # We assume the function returns something we can analyze
        # Based on the prompt, it likely returns a graph or an object with specific properties
        result = generate_room_graph(seed, floor_number=1, map_folder='第二张地图')
        success_count += 1
        
        # Analyze the result (graph)
        # Assuming result is the graph object or has nodes and edges attributes
        # We need to find main_path_ids, depth and lane attributes on nodes/edges
        
        main_path_ids = getattr(result, 'main_path_ids', [])
        if len(main_path_ids) > 1:
            total_main_path_edges += len(main_path_ids) - 1
            total_main_path_length += len(main_path_ids)

        nodes = getattr(result, 'nodes', {})
        if hasattr(result, 'edges'):
             edges = result.edges
        elif hasattr(result, 'graph') and hasattr(result.graph, 'edges'):
             edges = result.graph.edges
        else:
             # Fallback if result is a networkx graph
             edges = result.edges() if hasattr(result, 'edges') else []

        for u_id, v_id in edges:
            u = nodes.get(u_id)
            v = nodes.get(v_id)
            if u and v:
                # depth back edges: child.depth < parent.depth
                if getattr(v, 'depth', 0) < getattr(u, 'depth', 0):
                    total_depth_back_edges += 1
                
                # lane up: child.lane < parent.lane
                if getattr(v, 'lane', 0) < getattr(u, 'lane', 0):
                    total_lane_up_edges += 1
                
                # lane down: child.lane > parent.lane
                if getattr(v, 'lane', 0) > getattr(u, 'lane', 0):
                    total_lane_down_edges += 1
                    
    except Exception as e:
        fail_count += 1

print(f'Success: {success_count}')
print(f'Failure: {fail_count}')
print(f'Total Main Path Edges: {total_main_path_edges}')
print(f'Total Depth Back Edges: {total_depth_back_edges}')
print(f'Total Lane Up Edges: {total_lane_up_edges}')
print(f'Total Lane Down Edges: {total_lane_down_edges}')
avg_main_path = total_main_path_length / success_count if success_count > 0 else 0
print(f'Average Main Path Length: {avg_main_path:.2f}')
