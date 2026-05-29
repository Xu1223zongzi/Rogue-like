from game.world.graph_map import generate_room_graph
import os
import sys

# Ensure search path is correct
sys.path.append('E:/py/pygame_roguelike')

boss_left_count = 0
boss_right_count = 0

for seed in range(1, 81):
    try:
        nodes, main_path_ids = generate_room_graph(seed, floor_number=1, map_folder='第二张地图')
        last_node = main_path_ids[-1]
        map_file = last_node.map_file
        if map_file == 'Boss房_左.txt':
            boss_left_count += 1
        elif map_file == 'Boss房_右.txt':
            boss_right_count += 1
    except Exception as e:
        pass

print(f"Boss房_左.txt: {boss_left_count}")
print(f"Boss房_右.txt: {boss_right_count}")
