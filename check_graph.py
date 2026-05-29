import sys
sys.path.append(r"e:/py/pygame_roguelike")
from game.world.graph_map import generate_room_graph

hits = []
for seed in range(1, 201):
    try:
        graph = generate_room_graph(seed, floor_number=1, map_folder='第二张地图')
        nodes_dict = {node.node_id: node for node in graph.nodes}
        
        for node in graph.nodes:
            # A leaf in this directed structure has no children
            is_leaf = len(node.child_ids) == 0
            
            # Non-main-path leaf 'small' room
            if is_leaf and node.branch_type != 'main_path' and node.room_size == 'small':
                path = []
                current = node
                
                # Trace back to main path anchor
                branch_path = []
                while current:
                    branch_path.append((current.node_id, current.room_size, current.branch_type))
                    if current.branch_type == 'main_path':
                        # Found the anchor
                        # The branch path is nodes from leaf up to (but excluding or including?) anchor
                        # "从最近主路锚点到叶子的分支路径里 small 房数量 > 3"
                        # Usually the branch itself starts after the anchor.
                        # Let's count small rooms in the nodes that are NOT the anchor.
                        
                        small_count = sum(1 for step in branch_path if step[1] == 'small' and step[2] != 'main_path')
                        
                        if small_count > 3:
                            hits.append({
                                'seed': seed,
                                'path': list(reversed(branch_path)) # Anchor to leaf
                            })
                            # Break for this seed if found
                            break
                        break
                    
                    # Move to parent
                    if hasattr(current, 'parent_id') and current.parent_id is not None:
                        current = nodes_dict.get(current.parent_id)
                    else:
                        break
                
                if hits and hits[-1]['seed'] == seed:
                    break

    except Exception:
        pass

print(f"Hits: {len(hits)}")
print(f"Example seeds: {[h['seed'] for h in hits[:3]]}")
if hits:
    example_path = hits[0]['path']
    print("Example path (node_id/room_size/branch_type):")
    for step in example_path:
        print(f"{step[0]}/{step[1]}/{step[2]}")
