import sys
sys.path.append('e:/py/pygame_roguelike')
from game.world.graph_map import generate_room_graph
gm = generate_room_graph(1, floor_number=1, map_folder='第二张地图')
node_18 = gm.nodes[18]
props = ['role', 'branch_type', 'depth', 'lane', 'incoming_ids', 'outgoing_ids', 'map_file']
for p in props:
    print(f'{p}: {getattr(node_18, p, "N/A")}')
