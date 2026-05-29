import sys
import os

sys.path.append(os.getcwd())

from game.world.graph_map import generate_room_graph

seed = 1
floor_number = 1
map_folder = '第二张地图'

result = generate_room_graph(seed=seed, floor_number=floor_number, map_folder=map_folder)

# 为了方便查找，建立一个映射
nodes_map = {node.node_id: node for node in result.nodes}

def print_node_info(node_id):
    if node_id not in nodes_map:
        print(f"Node {node_id} not found.")
        return
    node = nodes_map[node_id]
    
    # 属性可能是 role 或 room_type
    role = getattr(node, 'role', getattr(node, 'room_type', 'N/A'))
    
    print(f"Node ID: {node.node_id}")
    print(f"  Role: {role}")
    print(f"  Branch Type: {getattr(node, 'branch_type', 'N/A')}")
    print(f"  Depth: {getattr(node, 'depth', 'N/A')}")
    print(f"  Lane: {getattr(node, 'lane', 'N/A')}")
    print(f"  Incomings: {getattr(node, 'incoming_ids', 'N/A')}")
    print(f"  Outgoings: {getattr(node, 'outgoing_ids', 'N/A')}")
    print(f"  Map File: {getattr(node, 'map_file', 'N/A')}")
    print("-" * 20)

print("--- Main Path Nodes ---")
for nid in result.main_path_ids:
    print_node_info(nid)

print("\n--- Nodes 12 to 16 ---")
for nid in range(12, 17):
    print_node_info(nid)
