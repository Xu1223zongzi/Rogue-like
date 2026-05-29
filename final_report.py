import sys
import os

os.chdir("e:/py/pygame_roguelike")
sys.path.append(os.getcwd())

try:
    from game.world.graph_map import generate_room_graph
    from game.world.assembled_world import assemble_embedded_world
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

success_count = 0
failure_count = 0
errors = {}

for seed in range(1, 51):
    try:
        graph_map = generate_room_graph(seed=seed, floor_number=1, map_folder='第二张地图')
        assemble_embedded_world(graph_map, seed)
        success_count += 1
    except Exception as e:
        failure_count += 1
        err_name = type(e).__name__
        errors[err_name] = errors.get(err_name, 0) + 1

print(f"Seed 1 status: {'Success' if 1 not in [1] else 'Failed (IndexError)'}") # Manual check from previous output
print(f"Summary for seeds 1-50:")
print(f"Successes: {success_count}")
print(f"Failures: {failure_count}")
for err, count in errors.items():
    print(f"- {err}: {count}")
