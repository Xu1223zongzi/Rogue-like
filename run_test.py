import sys
import os

# Set environment
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
errors = []

for seed in range(1, 51):
    try:
        graph_map = generate_room_graph(seed=seed, floor_number=1, map_folder='第二张地图')
        assemble_embedded_world(graph_map, seed)
        success_count += 1
        if seed == 1:
            print("Seed 1: Success")
    except Exception as e:
        failure_count += 1
        errors.append((seed, type(e).__name__, str(e)))
        if seed == 1:
            print(f"Seed 1: Failed with {type(e).__name__}: {e}")

print(f"\nSummary:")
print(f"Total seeds tested: 50")
print(f"Successes: {success_count}")
print(f"Failures: {failure_count}")

if failure_count > 0:
    print("\nFailure Details (first 5):")
    for seed, err_type, err_msg in errors[:5]:
        print(f"Seed {seed}: {err_type} - {err_msg}")
