import sys
import os

# 将项目根目录添加到 python 路径
sys.path.append(os.getcwd())

try:
    from game.world.graph_map import generate_room_graph
except ImportError as e:
    print(f"Error importing generate_room_graph: {e}")
    sys.exit(1)

seed = 1
floor_number = 1
map_folder = '第二张地图'

result = generate_room_graph(seed=seed, floor_number=floor_number, map_folder=map_folder)

# result 应该是 GraphMapData 对象。
# 根据函数签名，我们需要打印 main_path_ids 和 node 12..16 的信息。

nodes = result.nodes  # 假设 nodes 是字典或列表
main_path_ids = result.main_path_ids

def print_node_info(node_id):
    if node_id not in nodes:
        print(f"Node {node_id} not found.")
        return
    node = nodes[node_id]
    # 打印 node_id、role、branch_type、depth、lane、incoming_ids、outgoing_ids、map_file
    print(f"Node ID: {node.node_id}")
    print(f"  Role: {getattr(node, 'role', 'N/A')}")
    print(f"  Branch Type: {getattr(node, 'branch_type', 'N/A')}")
    print(f"  Depth: {getattr(node, 'depth', 'N/A')}")
    print(f"  Lane: {getattr(node, 'lane', 'N/A')}")
    print(f"  Incomings: {getattr(node, 'incoming_ids', 'N/A')}")
    print(f"  Outgoings: {getattr(node, 'outgoing_ids', 'N/A')}")
    print(f"  Map File: {getattr(node, 'map_file', 'N/A')}")
    print("-" * 20)

print("--- Main Path Nodes ---")
for nid in main_path_ids:
    print_node_info(nid)

print("\n--- Nodes 12 to 16 ---")
for nid in range(12, 17):
    print_node_info(nid)

