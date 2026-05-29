import sys
import os
import inspect

# Add the project root to sys.path
project_root = r'E:/py/pygame_roguelike'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from game.entities.actors import Player, Enemy
    from game.scenes.gameplay_scene import GameplayScene
    print("SUCCESS: Imports successful.")
except Exception as e:
    import traceback
    print("FAILURE: Import failed.")
    traceback.print_exc()
    sys.exit(1)

def verify_player():
    try:
        # We need to inspect the code to find 'absorbed' hit/barrier logic in Player
        player_source = inspect.getsource(Player)
        print("--- Player Source Verification ---")
        # Look for halo/barrier logic
        if 'halo' in player_source.lower() or 'barrier' in player_source.lower():
            print("Found halo/barrier references in Player.")
            # Verify absorbed-hit count
            if 'absorbed' in player_source.lower() and ('count' in player_source.lower() or 'hit' in player_source.lower()):
                 print("Found 'absorbed' hit/count logic.")
            else:
                 print("WARNING: 'absorbed' hit logic not explicitly found in Player source.")
        else:
            print("WARNING: No halo/barrier logic found in Player.")
    except Exception as e:
        print(f"Error inspecting Player: {e}")

def verify_gameplay_scene():
    try:
        gs_source = inspect.getsource(GameplayScene.cast_knight_spirit)
        print("\n--- GameplayScene.cast_knight_spirit Verification ---")
        # Check tier >= 4 logic
        if 'tier' in gs_source and ('>= 4' in gs_source or '> 3' in gs_source):
            print("Found tier >= 4 logic.")
            if 'controlled' in gs_source and 'boss' in gs_source:
                print("Found logic to convert non-boss enemies to controlled.")
                if 'summon' in gs_source:
                     print("Note: 'summon' is mentioned in the method.")
            else:
                print("WARNING: Could not find 'controlled' or 'boss' logic in tier check.")
        else:
            print("WARNING: Tier >= 4 condition NOT found in cast_knight_spirit.")
        
        # print specific lines for verification
        lines = [line.strip() for line in gs_source.split('\n') if 'tier' in line or 'controlled' in line or 'boss' in line or 'summon' in line]
        for l in lines:
            print(f"Code line: {l}")

    except AttributeError:
        print("FAILURE: cast_knight_spirit not found in GameplayScene.")
    except Exception as e:
        print(f"Error inspecting GameplayScene: {e}")

verify_player()
verify_gameplay_scene()
