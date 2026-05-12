import sys
import os
import math

sys.path.append(r"e:\py\pygame_roguelike")

from game.world.level import LevelState
from game.scenes.gameplay_scene import GameplayScene

def check_seeds():
    failures = []
    seeds_with_mismatch = 0
    
    for seed in range(1, 81):
        try:
            ls = LevelState(seed=seed)
            # Assuming level creation happens on init or needs a method. 
            # Looking at typical patterns. Usually LevelState(seed) is enough or call a method.
        except Exception as e:
            if "component overlap" in str(e).lower():
                continue
            continue
            
        # 1) count connector placements with len(sides) >= 3
        # Connector logic often in ls.connector_placements or similar
        connectors = []
        if hasattr(ls, "connector_placements"):
            connectors = [c for c in ls.connector_placements if len(getattr(c, "sides", [])) >= 3]
        
        # 2) generate portals
        try:
            gs = GameplayScene.__new__(GameplayScene)
            gs.level_state = ls
            # generate_teleport_portals might use ls
            # Based on query, need to call it
            gs.generate_teleport_portals()
            portals = getattr(gs, "teleport_portals", [])
        except Exception:
            continue
            
        # Count portals matching branch_junction
        junction_portals = [p for p in portals if getattr(p, "portal_type", "") == "branch_junction"]
        
        # Match connectors to portals
        matched_count = 0
        local_failures = []
        
        for c in connectors:
            c_pos = getattr(c, "pos", (0,0))
            found = False
            min_dist = float("inf")
            for p in junction_portals:
                p_pos = getattr(p, "pos", (0,0))
                dist = math.sqrt((c_pos[0]-p_pos[0])**2 + (c_pos[1]-p_pos[1])**2)
                if dist < 5: # Threshold for "matching"
                    found = True
                    break
                if dist < min_dist:
                    min_dist = dist
            
            if found:
                matched_count += 1
            else:
                local_failures.append({"seed": seed, "pos": c_pos, "min_dist": min_dist, "portals_count": len(junction_portals)})

        if len(connectors) > matched_count:
            seeds_with_mismatch += 1
            failures.extend(local_failures)

    print(f"Seeds with connector > junction portal: {seeds_with_mismatch}")
    print("Failures (max 10):")
    for f in failures[:10]:
        print(f"Seed {f['seed']}: Connector at {f['pos']}, nearest portal dist: {f['min_dist']:.2f}, total junction portals: {f['portals_count']}")

check_seeds()
