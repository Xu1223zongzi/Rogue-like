import sys
import os

# Add project root to sys.path
sys.path.append('e:/py/pygame_roguelike')

try:
    from game.world.graph_map import generate_room_graph
    from game.world.assembled_world import assemble_embedded_world
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)

# Find AssemblyError location
# Assuming it might be in game.world.assembled_world or game.world.graph_map
AssemblyError = None
try:
    from game.world.assembled_world import AssemblyError
except ImportError:
    try:
        from game.world.graph_map import AssemblyError
    except ImportError:
        # If not found, use a generic Exception for catch and check name later
        pass

first_seed = None
exception_msg = ''
failed_graph_map = None

for seed in range(1, 201):
    try:
        graph_map = generate_room_graph(seed, floor_number=1, map_folder='第二张地图')
        assemble_embedded_world(graph_map, seed)
    except Exception as e:
        if e.__class__.__name__ == 'AssemblyError':
            first_seed = seed
            exception_msg = str(e)
            failed_graph_map = graph_map
            break

if first_seed is not None:
    print(f'Seed: {first_seed}')
    print(f'Error: {exception_msg}')
    
    # Try to find node 18
    node_18 = None
    if hasattr(failed_graph_map, 'nodes'):
        if isinstance(failed_graph_map.nodes, dict):
             node_18 = failed_graph_map.nodes.get(18)
        else:
             # Maybe it's a list or something else? Try iterating
             for node in failed_graph_map.nodes:
                 if getattr(node, 'node_id', None) == 18:
                     node_18 = node
                     break
    
    if node_18:
        props = ['role', 'branch_type', 'depth', 'lane', 'incoming_ids', 'outgoing_ids', 'map_file']
        for p in props:
            val = getattr(node_18, p, 'N/A')
            print(f'{p}: {val}')
    else:
        print('Node 18 not found in the graph map.')
        
    # main_path_ids
    main_path_ids = getattr(failed_graph_map, 'main_path_ids', 'N/A')
    print(f'main_path_ids: {main_path_ids}')
else:
    print('No AssemblyError found in seeds 1-200.')
