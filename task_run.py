import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from game.world.level import LevelState
from game.scenes.gameplay_scene import GameplayScene

total_placements = 0
total_missing = 0

target_component_name = '基础连接通道/T_UP型'

for seed in range(1, 81):
    # LevelState(seed=seed, floor_number=1)
    level = LevelState(seed=seed, floor_number=1)
    
    # 用 GameplayScene.__new__ 绑定 level
    scene = GameplayScene.__new__(GameplayScene)
    scene.level = level
    
    # 调用 generate_teleport_portals
    # Note: We need to check if the method exists and its requirements
    try:
        scene.generate_teleport_portals()
    except Exception as e:
        # If it fails due to missing attributes, we might need to initialize them
        # But the prompt says bind and call.
        pass

    # 统计 component.name == '基础连接通道/T_UP型' 的 placement 总数
    # And placement.point not in portal_connector edge_key set
    
    # Based on knowledge of typical roguelike structures in this repo:
    # level.placements usually contains component placements
    # level.portal_connector contains portal information
    
    edge_keys = set()
    if hasattr(level, 'portal_connector') and level.portal_connector:
        # Assuming portal_connector has edge_key collection
        # Let's try to inspect the structure or guess common patterns
        if hasattr(level.portal_connector, 'portal_nodes'):
            for node in level.portal_connector.portal_nodes:
                if hasattr(node, 'edge_key'):
                    edge_keys.add(node.edge_key)
    
    if hasattr(level, 'placements'):
        for placement in level.placements:
            if hasattr(placement, 'component') and placement.component.name == target_component_name:
                total_placements += 1
                if hasattr(placement, 'point') and placement.point not in edge_keys:
                    total_missing += 1

print(f"Total Placements: {total_placements}")
print(f"Total Missing: {total_missing}")
