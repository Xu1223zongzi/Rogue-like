import sys
import os

# Ensure we can import modules from the project root
sys.path.append('e:/py/pygame_roguelike')

try:
    from game.world.graph_map import generate_room_graph
    from game.world.assembled_world import assemble_embedded_world
except ImportError as e:
    print(f'Import Error: {e}')
    sys.exit(1)

def run_test(seed):
    try:
        graph_map = generate_room_graph(seed=seed, floor_number=1, map_folder='第二张地图')
        assemble_embedded_world(graph_map, 1)
        return True, None
    except Exception as e:
        import traceback
        return False, traceback.format_exc()

# 1) Test seed=1
success_1, error_1 = run_test(1)
if success_1:
    print('Seed=1: SUCCESS')
else:
    print(f'Seed=1: FAILED\n{error_1}')

# 2) Test seeds 1..50
success_count = 0
failure_count = 0
first_two_failures = []

for seed in range(1, 51):
    success, error = run_test(seed)
    if success:
        success_count += 1
    else:
        failure_count += 1
        if len(first_two_failures) < 2:
            first_two_failures.append((seed, error))

print(f'\nSummary: Total 50, Success: {success_count}, Failure: {failure_count}')
if failure_count > 0:
    print('\nFirst two failures:')
    for seed, error in first_two_failures:
        print(f'--- Seed {seed} ---')
        print(error)

