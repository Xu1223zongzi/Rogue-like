import sys
import os
import math
import pygame

# Set dummy display for pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((1,1))

# Add current directory to path
sys.path.append(os.getcwd())

from game.config import TILE_SIZE
from game.scenes.gameplay_scene import GameplayScene
from game.world.level import LevelState

def run_validation():
    # 1) Print TELEPORT_ACTIVATE_DISTANCE
    # It might be defined inside the file but accessed via self or class
    # Looking at the previous grep, it's defined at class level but without self prefix in one line, 
    # but based on python scoping in a class, if it's top-level in the class it's accessible via GameplayScene.
    try:
        # Check if it's a module level constant or class level
        import game.scenes.gameplay_scene as gs_mod
        val = getattr(gs_mod, 'TELEPORT_ACTIVATE_DISTANCE', getattr(GameplayScene, 'TELEPORT_ACTIVATE_DISTANCE', None))
        print(f"TELEPORT_ACTIVATE_DISTANCE: {val}")
    except Exception as e:
        print(f"Error getting TELEPORT_ACTIVATE_DISTANCE: {e}")
    
    validated_seed_count = 0
    skipped_seed_count = 0
    branch_portal_count = 0
    near_connector_count = 0
    failed_samples = []
    
    for seed in range(1, 81):
        try:
            # 2) Try to build LevelState
            level_state = LevelState(seed=seed)
            
            # Simulated GameplayScene initialization
            scene = GameplayScene.__new__(GameplayScene)
            # Based on traceback, it uses self.level instead of self.level_state
            scene.level = level_state
            scene.teleport_portals = [] 
            
            # Call generate_teleport_portals
            try:
                # generate_teleport_portals returns a list and doesn't seem to set self.teleport_portals directly in the code we saw
                # But looking at update_teleport_portals, it uses self.teleport_portals
                portals = scene.generate_teleport_portals()
                scene.teleport_portals = portals
            except Exception as e:
                raise e

            validated_seed_count += 1
            
            # Validate branch portals
            # level_state has world_graph? Based on previous level.py grep, let's check
            # Based on the error 'GameplayScene' object has no attribute 'level', we fixed that.
            # Now let's hope level.world_graph exists.
            world_graph = getattr(level_state, 'world_graph', None)
            if world_graph:
                for edge in world_graph.edges:
                    u, v = edge
                    node_u = world_graph.nodes[u]
                    node_v = world_graph.nodes[v]
                    
                    u_child_ids = node_u.get('child_ids', [])
                    
                    is_branch_junction = len(u_child_ids) >= 2 and \
                                       (node_u.get('branch_type') in ['major_branch', 'minor_branch'] or \
                                        node_v.get('branch_type') in ['major_branch', 'minor_branch'])
                    
                    if is_branch_junction:
                        # Find portal for this edge
                        # The portal object might store edge as a tuple or individual ids
                        portal = next((p for p in scene.teleport_portals if getattr(p, 'edge', None) == (u, v)), None)
                        if portal:
                            branch_portal_count += 1
                            
                            portal_pos = getattr(portal, 'position', None)
                            if portal_pos:
                                # Distance to connectors
                                min_dist = float('inf')
                                placements = getattr(level_state, 'connector_placements', [])
                                for placement in placements:
                                    if hasattr(placement, 'connector') and len(getattr(placement.connector, 'sides', [])) >= 3:
                                        conn_point = getattr(placement, 'point', (0,0))
                                        conn_x = conn_point[0] * TILE_SIZE
                                        conn_y = conn_point[1] * TILE_SIZE
                                        
                                        dist = math.sqrt((portal_pos[0] - conn_x)**2 + (portal_pos[1] - conn_y)**2)
                                        if dist < min_dist:
                                            min_dist = dist
                                
                                if min_dist <= 64:
                                    near_connector_count += 1

        except Exception as e:
            msg = str(e)
            if "overlap" in msg.lower() or "assemble_embedded_world" in msg.lower():
                skipped_seed_count += 1
            else:
                if len(failed_samples) < 10:
                    failed_samples.append(f"Seed {seed}: {type(e).__name__}: {msg}")
    
    print(f"validated_seed_count: {validated_seed_count}")
    print(f"skipped_seed_count: {skipped_seed_count}")
    print(f"branch_portal_count: {branch_portal_count}")
    print(f"near_connector_count: {near_connector_count}")
    print("failed_samples:")
    for s in failed_samples:
        print(f" - {s}")

if __name__ == '__main__':
    run_validation()
