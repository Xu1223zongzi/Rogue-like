import os
import sys
sys.path.append(os.getcwd())
from game.world.graph_map import generate_room_graph

try:
    result = generate_room_graph(1, floor_number=1, map_folder='第二张地图')
    if isinstance(result.nodes, list) and len(result.nodes) > 0:
        # Check start_id and end_id in result
        print(f"Start ID: {result.start_id}, Exit ID: {result.exit_id}")
        
    print("Listing nodes and their connections to find 'lane_delta'...")
    # Based on the user query, lane_delta seems to be an attribute of an 'edge' or 'connection'.
    # Since I don't see an explicit 'edges' list in GraphMapData (it had main_path_ids though),
    # let's look for connections again.
    
    # Wait, the previous inspect_v3 didn't show 'connections' in First node attrs.
    # It showed 'outgoing_ids' and 'incoming_ids'.
    
    # Maybe lane_delta is calculated as (child.lane - parent.lane)?
    # Or maybe there is another object?
    
    # Let me search for 'lane_delta' in the codebase to be sure.
