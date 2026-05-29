import sys
import os

# Ensure the project root is in sys.path
sys.path.append(os.getcwd())

# Mock arcade to skip dependency
class Mock:
    def __init__(self, *args, **kwargs): pass
sys.modules['arcade'] = Mock()

try:
    from game.world.graph_map import generate_room_graph
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

success_count = 0
fail_count = 0
total_main_path_edges = 0
total_backtrack_edges = 0

for seed in range(1, 81):
    try:
        result = generate_room_graph(seed, floor_number=1, map_folder='第二张地图')
        
        # Result unpacking depends on current implementation. 
        # Most implementations of this function for roguelikes return (graph, main_path, backtracks)
        # We will try to unpack dynamically.
        if isinstance(result, tuple):
            if len(result) >= 3:
                graph, main_path_ids, backtrack_edges = result[0], result[1], result[2]
            else:
                main_path_ids = result[1]
                backtrack_edges = [] # Default if missing
        else:
            # Assume it's an object/dict if not tuple
            main_path_ids = getattr(result, 'main_path_ids', [])
            backtrack_edges = getattr(result, 'backtrack_edges', [])

        success_count += 1
        total_main_path_edges += len(main_path_ids) - 1 if len(main_path_ids) > 0 else 0
        total_backtrack_edges += len(backtrack_edges)
    except Exception as e:
        fail_count += 1

avg_backtrack = total_backtrack_edges / success_count if success_count > 0 else 0
avg_main_path = total_main_path_edges / success_count if success_count > 0 else 0

print(f"成功: {success_count}")
print(f"失败: {fail_count}")
print(f"main_path_ids 总边数: {total_main_path_edges}")
print(f"回退边总数: {total_backtrack_edges}")
print(f"每张成功地图平均回退边数: {avg_backtrack:.2f}")
print(f"平均主路长度: {avg_main_path:.2f}")
