import sys
import os

sys.path.append('.')

from game.world.graph_map import generate_room_graph
from game.world.assembled_world import assemble_embedded_world

def run_test(seed):
    try:
        graph_map = generate_room_graph(seed=seed, floor_number=1, map_folder="第二张地图")
        assemble_embedded_world(graph_map, seed)
        return True, None
    except Exception as e:
        import traceback
        return False, str(e)

# Confirm seed=1
success_1, err_1 = run_test(1)

# Stats for 1..50
success_count = 0
failures = []

for seed in range(1, 51):
    success, err = run_test(seed)
    if success:
        success_count += 1
    else:
        if len(failures) < 2:
            failures.append((seed, err))

print(f"Seed 1 status: {'Success' if success_1 else 'Failed'}")
print(f"Total: 50, Success: {success_count}, Failure: {50 - success_count}")

if failures:
    print("Top 2 Failures:")
    for s, e in failures:
        print(f"Seed {s}: {e}")
