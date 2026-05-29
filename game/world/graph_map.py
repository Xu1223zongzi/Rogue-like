from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import json
from pathlib import Path
import random


@dataclass
class GraphRoomNode:
    node_id: int
    room_type: str
    room_size: str
    branch_type: str
    depth: int
    lane: int
    variant_index: int = 0
    room_name: str = ""
    map_file: str = ""
    incoming_ids: list[int] = field(default_factory=list)
    outgoing_ids: list[int] = field(default_factory=list)

    @property
    def child_ids(self) -> list[int]:
        return self.outgoing_ids

    @property
    def parent_id(self) -> int | None:
        return self.incoming_ids[0] if self.incoming_ids else None


@dataclass
class GraphMapData:
    seed: int
    nodes: list[GraphRoomNode]
    room_positions: dict[int, tuple[int, int]]
    start_id: int
    exit_id: int
    lane_min: int
    lane_max: int
    main_path_ids: list[int]
    map_folder: str
    generation_rules: dict[str, object] = field(default_factory=dict)

    @property
    def grid_width(self) -> int:
        return max((node.depth for node in self.nodes), default=0) + 1

    @property
    def grid_height(self) -> int:
        return self.lane_max - self.lane_min + 1

    @property
    def room_cells(self) -> list[tuple[int, int]]:
        return [(node.depth, node.lane - self.lane_min) for node in self.nodes]

    @property
    def start_cell(self) -> tuple[int, int]:
        node = self.nodes[self.start_id]
        return (node.depth, node.lane - self.lane_min)

    @property
    def exit_cell(self) -> tuple[int, int]:
        node = self.nodes[self.exit_id]
        return (node.depth, node.lane - self.lane_min)

    @property
    def main_path_cells(self) -> list[tuple[int, int]]:
        return [self.room_cells[node_id] for node_id in self.main_path_ids]

    @property
    def branch_cells(self) -> set[tuple[int, int]]:
        main_path_set = set(self.main_path_ids)
        return {
            self.room_cells[node.node_id]
            for node in self.nodes
            if node.node_id not in main_path_set
        }

    @property
    def major_branch_cells(self) -> set[tuple[int, int]]:
        return {
            self.room_cells[node.node_id]
            for node in self.nodes
            if node.branch_type == "major_branch"
        }

    @property
    def minor_branch_cells(self) -> set[tuple[int, int]]:
        return {
            self.room_cells[node.node_id]
            for node in self.nodes
            if node.branch_type == "minor_branch"
        }


def _maps_root() -> Path:
    return Path(__file__).resolve().parents[2] / "maps"


def _map_folder(map_folder: str) -> Path:
    return _maps_root() / map_folder


def _map_definition_path(map_folder: str) -> Path:
    return _map_folder(map_folder) / "地图.json"


def _load_map_definition(map_folder: str) -> dict[str, object]:
    definition_path = _map_definition_path(map_folder)
    if not definition_path.exists():
        raise FileNotFoundError(f"Map definition not found: {definition_path}")
    return json.loads(definition_path.read_text(encoding="utf-8"))


def load_room_grid(graph_map: GraphMapData, node_id: int) -> list[str]:
    node = graph_map.nodes[node_id]
    room_path = _map_folder(graph_map.map_folder) / node.map_file
    if not room_path.exists():
        raise FileNotFoundError(f"Room file not found: {room_path}")
    lines = [line.rstrip("\n\r") for line in room_path.read_text(encoding="utf-8").splitlines()]
    lines = [line for line in lines if line]
    if not lines:
        raise ValueError(f"Room file is empty: {room_path}")
    width = max(len(line) for line in lines)
    if any(len(line) != width for line in lines):
        raise ValueError(f"Room file rows must have equal width: {room_path}")
    return lines


def _normalize_generation_rules(definition: dict[str, object]) -> dict[str, object]:
    raw_rules = definition.get("generation_rules", {})
    if not isinstance(raw_rules, dict):
        raise ValueError("generation_rules must be an object")

    lane_rules = raw_rules.get("lane_rules", {})
    if not isinstance(lane_rules, dict):
        raise ValueError("generation_rules.lane_rules must be an object")

    corridor_rules = raw_rules.get("corridor_rules", {})
    if not isinstance(corridor_rules, dict):
        raise ValueError("generation_rules.corridor_rules must be an object")

    branch_rules = raw_rules.get("branch_rules", {})
    if not isinstance(branch_rules, dict):
        raise ValueError("generation_rules.branch_rules must be an object")

    random_layout_rules = raw_rules.get("random_layout", {})
    if not isinstance(random_layout_rules, dict):
        raise ValueError("generation_rules.random_layout must be an object")

    component_usage = corridor_rules.get("component_usage", {})
    if not isinstance(component_usage, dict):
        raise ValueError("generation_rules.corridor_rules.component_usage must be an object")

    socket_compatibility = corridor_rules.get("socket_compatibility", {"0": ["0", "2"], "1": ["1"], "2": ["0", "2"]})
    if not isinstance(socket_compatibility, dict):
        raise ValueError("generation_rules.corridor_rules.socket_compatibility must be an object")

    normalized_socket_compatibility: dict[str, list[str]] = {}
    for socket_type, allowed_types in socket_compatibility.items():
        if not isinstance(allowed_types, list):
            raise ValueError("generation_rules.corridor_rules.socket_compatibility values must be lists")
        normalized_socket_compatibility[str(socket_type)] = [str(allowed_type) for allowed_type in allowed_types]

    component_socket_types = corridor_rules.get("component_socket_types", {})
    if not isinstance(component_socket_types, dict):
        raise ValueError("generation_rules.corridor_rules.component_socket_types must be an object")

    normalized_component_socket_types = {
        str(component_name): str(socket_type)
        for component_name, socket_type in component_socket_types.items()
    }

    known_socket_types = set(normalized_socket_compatibility)
    unknown_socket_types = set(normalized_component_socket_types.values()) - known_socket_types
    if unknown_socket_types:
        raise ValueError(
            "generation_rules.corridor_rules.component_socket_types contains unknown socket types: "
            + ", ".join(sorted(unknown_socket_types))
        )

    referenced_socket_types = {
        allowed_type
        for allowed_types in normalized_socket_compatibility.values()
        for allowed_type in allowed_types
    }
    missing_socket_types = referenced_socket_types - known_socket_types
    if missing_socket_types:
        raise ValueError(
            "generation_rules.corridor_rules.socket_compatibility references unknown socket types: "
            + ", ".join(sorted(missing_socket_types))
        )

    return {
        "mode": str(raw_rules.get("mode", "fixed_layout")),
        "lane_rules": {
            "start_lane": int(lane_rules.get("start_lane", 0)),
            "large_room_lane_min": int(lane_rules.get("large_room_lane_min", -2)),
            "large_room_lane_max": int(lane_rules.get("large_room_lane_max", 2)),
            "small_room_ignores_lane_bounds": bool(lane_rules.get("small_room_ignores_lane_bounds", True)),
            "vertical_shaft_span_min": int(lane_rules.get("vertical_shaft_span_min", 2)),
            "vertical_shaft_span_max": int(lane_rules.get("vertical_shaft_span_max", 3)),
        },
        "corridor_rules": {
            "ordinary_corridor": str(corridor_rules.get("ordinary_corridor", "用于直连同层通道与标准竖井延长段")),
            "basic_connector": str(corridor_rules.get("basic_connector", "用于 L/T/十字等常规拐点与分叉连接")),
            "special_h_connector": str(corridor_rules.get("special_h_connector", "用于连接上下相邻的两个通道")),
            "max_vertical_shaft_segments": int(corridor_rules.get("max_vertical_shaft_segments", 2)),
            "max_connected_straight_segments": int(corridor_rules.get("max_connected_straight_segments", 5)),
            "socket_compatibility": normalized_socket_compatibility,
            "component_socket_types": normalized_component_socket_types,
            "component_usage": {str(key): str(value) for key, value in component_usage.items()},
        },
        "branch_rules": {
            "major_branch": str(branch_rules.get("major_branch", "长通道分支，通向地图末端或较远叶子房")),
            "minor_branch": str(branch_rules.get("minor_branch", "从主路或大分支之间分叉出去的短通道")),
        },
        "random_layout": {
            "min_large_rooms": int(random_layout_rules.get("min_large_rooms", 7)),
            "max_large_rooms": int(random_layout_rules.get("max_large_rooms", 15)),
            "min_small_rooms": int(random_layout_rules.get("min_small_rooms", 5)),
            "max_small_rooms": int(random_layout_rules.get("max_small_rooms", 11)),
            "min_branches": int(random_layout_rules.get("min_branches", 4)),
            "max_branches": int(random_layout_rules.get("max_branches", 8)),
            "min_branch_length": int(random_layout_rules.get("min_branch_length", 1)),
            "max_branch_length": int(random_layout_rules.get("max_branch_length", 3)),
        },
        "layout_notes": [str(note) for note in raw_rules.get("layout_notes", [])],
    }


def _room_file_for_sides(role: str, room_size: str, needs_left: bool, needs_right: bool, is_portal_room: bool = False) -> str:
    if role == "start":
        return "房间组件/房间_00.txt" if needs_right else "房间组件/房间_00_1.txt"

    if role == "boss":
        if needs_left and needs_right:
            return "房间组件/房间_02.txt"
        if needs_left and not needs_right:
            return "房间组件/Boss房_左.txt"
        return "房间组件/Boss房_右.txt"

    if role == "portal" or (is_portal_room and room_size == "large"):
        if needs_left and not needs_right:
            return "房间组件/传送门房_左.txt"
        if needs_right and not needs_left:
            return "房间组件/传送门房_右.txt"

    if room_size == "small":
        if needs_left and needs_right:
            return "房间组件/房间_01.txt"
        if needs_left:
            return "房间组件/房间_01_2.txt"
        if needs_right:
            return "房间组件/房间_01_1.txt"
        return "房间组件/房间_01.txt"

    if needs_left and needs_right:
        return "房间组件/房间_02.txt"
    if needs_left:
        return "房间组件/房间_02_2.txt"
    if needs_right:
        return "房间组件/房间_02_1.txt"
    return "房间组件/房间_02.txt"


def _named_room_file(definition: dict[str, object], room_name: str) -> str | None:
    room_specs = definition.get("rooms")
    if not isinstance(room_specs, list):
        return None
    for raw_spec in room_specs:
        if not isinstance(raw_spec, dict):
            continue
        if str(raw_spec.get("name", "")) != room_name:
            continue
        room_file = raw_spec.get("file")
        if room_file is None:
            return None
        return str(room_file)
    return None


def _random_room_role(rng: random.Random, room_size: str, is_boss: bool = False, prefer_combat: bool = False) -> str:
    if is_boss:
        return "boss"
    if room_size == "large":
        return "rest"
    if prefer_combat:
        return "combat"
    return "combat" if rng.random() < 0.58 else "rest"


def _candidate_lanes(current_lane: int, room_size: str, lane_rules: dict[str, object], max_vertical: int) -> list[int]:
    candidate_lanes = [current_lane + lane_delta for lane_delta in range(-max_vertical, max_vertical + 1)]
    if room_size != "large" or bool(lane_rules.get("small_room_ignores_lane_bounds", True)):
        return candidate_lanes

    lane_min = int(lane_rules.get("large_room_lane_min", -2))
    lane_max = int(lane_rules.get("large_room_lane_max", 2))
    return [lane for lane in candidate_lanes if lane_min <= lane <= lane_max]


def _has_position_clearance(
    occupied_cells: set[tuple[int, int]],
    depth: int,
    lane: int,
    ignored_cells: set[tuple[int, int]] | None = None,
) -> bool:
    skipped_cells = ignored_cells or set()
    return all(
        (other_depth, other_lane) in skipped_cells or abs(depth - other_depth) > 2 or abs(lane - other_lane) > 2
        for other_depth, other_lane in occupied_cells
    )


def _choose_open_position(
    rng: random.Random,
    occupied_cells: set[tuple[int, int]],
    start_depth: int,
    depth_direction: int,
    current_lane: int,
    room_size: str,
    lane_rules: dict[str, object],
    max_horizontal: int,
    max_vertical: int,
    node_specs: dict[int, dict[str, object]] | None = None,
    parent_id: int | None = None,
    reserved_future_large: int = 0,
) -> tuple[int, int]:
    parent_cell = (start_depth, current_lane)
    step_options = list(range(1, max_horizontal + 1))
    rng.shuffle(step_options)
    lane_options = _candidate_lanes(current_lane, room_size, lane_rules, max_vertical)
    rng.shuffle(lane_options)

    for step in step_options:
        next_depth = start_depth + depth_direction * step
        if next_depth < 0:
            continue
        for next_lane in lane_options:
            if (next_depth, next_lane) in occupied_cells:
                continue
            if not _has_position_clearance(occupied_cells, next_depth, next_lane, {parent_cell}):
                continue
            if not _horizontal_large_segment_allows_room(node_specs, parent_id, next_lane, room_size, reserved_future_large):
                continue
            return next_depth, next_lane

    raise ValueError("Unable to find an open room position that satisfies corridor rules")


def _same_lane_large_chain_count(node_specs: dict[int, dict[str, object]] | None, node_id: int | None, lane: int) -> int:
    if node_specs is None or node_id is None:
        return 0
    large_count = 0
    current_id = node_id
    while current_id is not None:
        spec = node_specs[current_id]
        if int(spec["lane"]) != lane:
            break
        if str(spec["size"]) == "large":
            large_count += 1
        incoming = spec.get("incoming", [])
        current_id = int(incoming[0]) if incoming else None
    return large_count


def _horizontal_large_segment_allows_room(
    node_specs: dict[int, dict[str, object]] | None,
    parent_id: int | None,
    next_lane: int,
    room_size: str,
    reserved_future_large: int = 0,
) -> bool:
    if room_size != "large":
        return True
    previous_large_count = _same_lane_large_chain_count(node_specs, parent_id, next_lane)
    return previous_large_count + 1 + max(0, reserved_future_large) <= 2


def _choose_straight_extension_position(
    occupied_cells: set[tuple[int, int]],
    start_depth: int,
    depth_direction: int,
    lane: int,
    max_horizontal: int,
    node_specs: dict[int, dict[str, object]] | None = None,
    parent_id: int | None = None,
) -> tuple[int, int]:
    parent_cell = (start_depth, lane)
    del max_horizontal
    step = 1
    next_depth = start_depth + depth_direction * step
    next_cell = (next_depth, lane)
    if (
        next_depth >= 0
        and next_cell not in occupied_cells
        and _has_position_clearance(occupied_cells, next_depth, lane, {parent_cell})
        and _horizontal_large_segment_allows_room(node_specs, parent_id, lane, "large")
    ):
        return next_depth, lane
    raise ValueError("Unable to find a straight extension position")


def _finalize_graph_map(
    seed: int,
    map_folder: str,
    generation_rules: dict[str, object],
    nodes: list[GraphRoomNode],
    start_id: int,
    exit_id: int,
    main_path_ids: list[int],
) -> GraphMapData:
    nodes.sort(key=lambda node: node.node_id)
    room_positions = {node.node_id: (node.depth, node.lane) for node in nodes}
    lane_min = min((node.lane for node in nodes), default=0)
    lane_max = max((node.lane for node in nodes), default=0)
    graph_map = GraphMapData(
        seed=seed,
        nodes=nodes,
        room_positions=room_positions,
        start_id=start_id,
        exit_id=exit_id,
        lane_min=lane_min,
        lane_max=lane_max,
        main_path_ids=main_path_ids,
        map_folder=map_folder,
        generation_rules=generation_rules,
    )
    _validate_branch_rules(graph_map)
    _validate_corridor_rules(graph_map)
    if not connectivity_check(graph_map):
        raise ValueError("Generated map graph is not fully connected")
    return graph_map


def _generate_random_room_graph(
    seed: int,
    floor_number: int,
    map_folder: str,
    generation_rules: dict[str, object],
    definition: dict[str, object],
) -> GraphMapData:
    rng = random.Random(seed + floor_number * 1_000_003)
    lane_rules = generation_rules.get("lane_rules", {})
    corridor_rules = generation_rules.get("corridor_rules", {})
    random_layout = generation_rules.get("random_layout", {})
    start_lane = int(lane_rules.get("start_lane", 0))
    max_vertical = int(corridor_rules.get("max_vertical_shaft_segments", 2))
    max_horizontal = int(corridor_rules.get("max_connected_straight_segments", 3))
    min_large_rooms = max(3, int(random_layout.get("min_large_rooms", 7)))
    max_large_rooms = max(min_large_rooms, int(random_layout.get("max_large_rooms", 15)))
    min_small_rooms = max(0, int(random_layout.get("min_small_rooms", 5)))
    max_small_rooms = max(min_small_rooms, int(random_layout.get("max_small_rooms", 11)))
    min_branches = max(0, int(random_layout.get("min_branches", 4)))
    max_branches = max(min_branches, int(random_layout.get("max_branches", 8)))
    min_branch_length = max(1, int(random_layout.get("min_branch_length", 1)))
    max_branch_length = max(min_branch_length, int(random_layout.get("max_branch_length", 3)))

    node_specs: dict[int, dict[str, object]] = {}
    occupied_cells: set[tuple[int, int]] = set()
    next_node_id = 0
    main_path_ids: list[int] = []
    target_large_rooms = rng.randint(min_large_rooms, max_large_rooms)
    target_small_rooms = rng.randint(min_small_rooms, max_small_rooms)
    branch_large_budget = min(max(2, target_large_rooms // 3), max(0, target_large_rooms - 3))
    branch_small_budget = min(max(2, target_small_rooms // 2), max(0, target_small_rooms - 1))
    main_large_target = max(3, target_large_rooms - branch_large_budget)
    main_small_target = max(1, target_small_rooms - branch_small_budget)
    large_room_count = 0
    small_room_count = 0

    def add_node(
        role: str,
        room_size: str,
        branch_type: str,
        depth: int,
        lane: int,
        room_name: str,
        count_towards_budget: bool = True,
    ) -> int:
        nonlocal next_node_id
        nonlocal large_room_count
        nonlocal small_room_count
        node_id = next_node_id
        next_node_id += 1
        occupied_cells.add((depth, lane))
        if count_towards_budget:
            if room_size == "large":
                large_room_count += 1
            else:
                small_room_count += 1
        node_specs[node_id] = {
            "role": role,
            "size": room_size,
            "branch_type": branch_type,
            "depth": depth,
            "lane": lane,
            "room_name": room_name,
            "portal_room": False,
            "counts_toward_budget": count_towards_budget,
            "children": [],
            "incoming": [],
        }
        return node_id

    def append_portal_room(parent_id: int, branch_type: str, room_name: str) -> int:
        parent_depth = int(node_specs[parent_id]["depth"])
        parent_lane = int(node_specs[parent_id]["lane"])
        next_depth, next_lane = _choose_straight_extension_position(
            occupied_cells,
            parent_depth,
            -1,
            parent_lane,
            max_horizontal,
            node_specs=node_specs,
            parent_id=parent_id,
        )
        next_id = add_node("portal", "large", branch_type, next_depth, next_lane, room_name, count_towards_budget=False)
        node_specs[next_id]["portal_room"] = True
        node_specs[parent_id]["children"].append(next_id)
        node_specs[next_id]["incoming"].append(parent_id)
        return next_id

    def leaf_should_append_portal(room_size: str, branch_room_count: int) -> bool:
        if room_size == "large":
            return True
        return branch_room_count >= 3

    start_id = add_node("start", "large", "main_path", 0, start_lane, "初始房间")
    main_path_ids.append(start_id)
    current_id = start_id
    main_index = 1
    while large_room_count < main_large_target or small_room_count < main_small_target:
        projected_large = large_room_count + 1
        needs_more_large = projected_large < main_large_target
        needs_more_small = small_room_count < main_small_target
        is_boss = not needs_more_large and not needs_more_small
        if is_boss:
            room_size = "large"
        elif needs_more_large and needs_more_small:
            room_size = "large" if large_room_count <= small_room_count else "small"
        elif needs_more_large:
            room_size = "large"
        else:
            room_size = "small"
        role = _random_room_role(rng, room_size, is_boss=is_boss, prefer_combat=main_index == 1)
        current_depth = int(node_specs[current_id]["depth"])
        current_lane = int(node_specs[current_id]["lane"])
        next_depth, next_lane = _choose_open_position(
            rng,
            occupied_cells,
            current_depth,
            1,
            current_lane,
            room_size,
            lane_rules,
            max_horizontal,
            max_vertical,
            node_specs=node_specs,
            parent_id=current_id,
        )
        room_name = "Boss房" if role == "boss" else (f"主路战斗房{main_index}" if role == "combat" else f"主路休整房{main_index}")
        next_id = add_node(role, room_size, "main_path", next_depth, next_lane, room_name)
        node_specs[current_id]["children"].append(next_id)
        node_specs[next_id]["incoming"].append(current_id)
        main_path_ids.append(next_id)
        current_id = next_id
        main_index += 1

    if node_specs[current_id]["role"] != "boss":
        node_specs[current_id]["role"] = "boss"
        node_specs[current_id]["room_name"] = "Boss房"

    branch_anchor_ids = [node_id for node_id in main_path_ids[1:-1] if int(node_specs[node_id]["depth"]) > 0]
    rng.shuffle(branch_anchor_ids)
    room_load = max(0, (target_large_rooms - 7)) + max(0, (target_small_rooms - 5))
    scaled_branch_min = min_branches + room_load // 3
    scaled_branch_max = max(max_branches, scaled_branch_min + 2)
    target_branch_count = rng.randint(scaled_branch_min, scaled_branch_max)
    created_branch_count = 0
    for anchor_id in branch_anchor_ids:
        if large_room_count >= target_large_rooms and small_room_count >= target_small_rooms:
            break
        if created_branch_count >= target_branch_count:
            break
        anchor_children = node_specs[anchor_id]["children"]
        anchor_depth = int(node_specs[anchor_id]["depth"])
        anchor_lane = int(node_specs[anchor_id]["lane"])
        has_left_child = any(int(node_specs[child_id]["depth"]) < anchor_depth for child_id in anchor_children)
        if has_left_child:
            continue

        remaining_large = max(0, target_large_rooms - large_room_count)
        remaining_small = max(0, target_small_rooms - small_room_count)
        remaining_total = remaining_large + remaining_small
        if remaining_total <= 0:
            break
        branch_length = min(rng.randint(min_branch_length, max_branch_length), remaining_total)
        branch_type = "major_branch" if branch_length >= 2 and remaining_large > 0 else "minor_branch"
        parent_id = anchor_id
        staged_node_ids: list[int] = []
        branch_failed = False
        branch_remaining_large = remaining_large
        branch_remaining_small = remaining_small
        branch_room_count = 0
        for branch_index in range(branch_length):
            is_leaf = branch_index == branch_length - 1
            if branch_type == "major_branch" and is_leaf:
                if branch_remaining_large <= 0:
                    branch_failed = True
                    break
                room_size = "large"
                branch_remaining_large -= 1
            elif is_leaf and branch_remaining_small > 0:
                room_size = "small"
                branch_remaining_small -= 1
            elif branch_remaining_large > 0 and branch_remaining_small <= 0:
                room_size = "large"
                branch_remaining_large -= 1
            elif branch_remaining_small > 0 and branch_remaining_large <= 0:
                room_size = "small"
                branch_remaining_small -= 1
            else:
                room_size = rng.choice(["small", "large"])
                if room_size == "large":
                    branch_remaining_large -= 1
                else:
                    branch_remaining_small -= 1
            role = _random_room_role(rng, room_size, prefer_combat=not is_leaf)
            parent_depth = int(node_specs[parent_id]["depth"])
            parent_lane = int(node_specs[parent_id]["lane"])
            next_branch_room_count = branch_room_count + 1
            try:
                next_depth, next_lane = _choose_open_position(
                    rng,
                    occupied_cells,
                    parent_depth,
                    -1,
                    parent_lane,
                    room_size,
                    lane_rules,
                    max_horizontal,
                    max_vertical,
                    node_specs=node_specs,
                    parent_id=parent_id,
                    reserved_future_large=1 if is_leaf and leaf_should_append_portal(room_size, next_branch_room_count) else 0,
                )
            except ValueError:
                branch_failed = True
                break
            room_name = f"{branch_type}_{anchor_id}_{branch_index}"
            next_id = add_node(role, room_size, branch_type, next_depth, next_lane, room_name)
            node_specs[parent_id]["children"].append(next_id)
            node_specs[next_id]["incoming"].append(parent_id)
            staged_node_ids.append(next_id)
            parent_id = next_id
            branch_room_count = next_branch_room_count
            if is_leaf and leaf_should_append_portal(room_size, branch_room_count):
                try:
                    portal_room_id = append_portal_room(next_id, branch_type, f"portal_room_{anchor_id}_{branch_index}")
                except ValueError:
                    branch_failed = True
                    break
                staged_node_ids.append(portal_room_id)
        if branch_failed:
            for staged_node_id in reversed(staged_node_ids):
                parent_ids = list(node_specs[staged_node_id]["incoming"])
                for parent_ref in parent_ids:
                    node_specs[parent_ref]["children"].remove(staged_node_id)
                if bool(node_specs[staged_node_id].get("counts_toward_budget", True)):
                    if str(node_specs[staged_node_id]["size"]) == "large":
                        large_room_count -= 1
                    else:
                        small_room_count -= 1
                occupied_cells.remove((int(node_specs[staged_node_id]["depth"]), int(node_specs[staged_node_id]["lane"])))
                del node_specs[staged_node_id]
                next_node_id -= 1
            continue
        created_branch_count += 1

    additional_anchor_ids = [
        node_id
        for node_id, spec in node_specs.items()
        if str(spec["branch_type"]) == "main_path" and node_id not in {start_id, main_path_ids[-1]}
    ]
    rng.shuffle(additional_anchor_ids)
    retry_budget = len(additional_anchor_ids) * 2
    while (large_room_count < target_large_rooms or small_room_count < target_small_rooms) and retry_budget > 0:
        retry_budget -= 1
        if not additional_anchor_ids:
            break
        anchor_id = additional_anchor_ids[retry_budget % len(additional_anchor_ids)]
        anchor_children = node_specs[anchor_id]["children"]
        anchor_depth = int(node_specs[anchor_id]["depth"])
        has_left_child = any(int(node_specs[child_id]["depth"]) < anchor_depth for child_id in anchor_children)
        if has_left_child:
            continue
        remaining_large = max(0, target_large_rooms - large_room_count)
        remaining_small = max(0, target_small_rooms - small_room_count)
        branch_length = min(max_branch_length, max(min_branch_length, remaining_large + remaining_small, 1))
        branch_type = "major_branch" if branch_length >= 2 and remaining_large > 0 else "minor_branch"
        parent_id = anchor_id
        staged_node_ids: list[int] = []
        branch_failed = False
        branch_room_count = 0
        for branch_index in range(branch_length):
            is_leaf = branch_index == branch_length - 1
            if branch_type == "major_branch" and is_leaf:
                if remaining_large <= 0:
                    branch_failed = True
                    break
                room_size = "large"
                remaining_large -= 1
            elif remaining_large > 0 and remaining_small <= 0:
                room_size = "large"
                remaining_large -= 1
            elif remaining_small > 0:
                room_size = "small"
                remaining_small -= 1
            else:
                break
            role = _random_room_role(rng, room_size, prefer_combat=not is_leaf)
            parent_depth = int(node_specs[parent_id]["depth"])
            parent_lane = int(node_specs[parent_id]["lane"])
            next_branch_room_count = branch_room_count + 1
            try:
                next_depth, next_lane = _choose_open_position(
                    rng,
                    occupied_cells,
                    parent_depth,
                    -1,
                    parent_lane,
                    room_size,
                    lane_rules,
                    max_horizontal,
                    max_vertical,
                    node_specs=node_specs,
                    parent_id=parent_id,
                    reserved_future_large=1 if is_leaf and leaf_should_append_portal(room_size, next_branch_room_count) else 0,
                )
            except ValueError:
                branch_failed = True
                break
            room_name = f"{branch_type}_{anchor_id}_extra_{branch_index}"
            next_id = add_node(role, room_size, branch_type, next_depth, next_lane, room_name)
            node_specs[parent_id]["children"].append(next_id)
            node_specs[next_id]["incoming"].append(parent_id)
            staged_node_ids.append(next_id)
            parent_id = next_id
            branch_room_count = next_branch_room_count
            if is_leaf and leaf_should_append_portal(room_size, branch_room_count):
                try:
                    portal_room_id = append_portal_room(next_id, branch_type, f"portal_room_{anchor_id}_extra_{branch_index}")
                except ValueError:
                    branch_failed = True
                    break
                staged_node_ids.append(portal_room_id)
        if branch_failed:
            for staged_node_id in reversed(staged_node_ids):
                parent_ids = list(node_specs[staged_node_id]["incoming"])
                for parent_ref in parent_ids:
                    node_specs[parent_ref]["children"].remove(staged_node_id)
                if bool(node_specs[staged_node_id].get("counts_toward_budget", True)):
                    if str(node_specs[staged_node_id]["size"]) == "large":
                        large_room_count -= 1
                    else:
                        small_room_count -= 1
                occupied_cells.remove((int(node_specs[staged_node_id]["depth"]), int(node_specs[staged_node_id]["lane"])))
                del node_specs[staged_node_id]
                next_node_id -= 1
            continue
        if staged_node_ids:
            created_branch_count += 1

    branch_boss_candidates: list[tuple[int, int, int, list[int]]] = []
    for node_id, spec in node_specs.items():
        if str(spec.get("branch_type", "")) != "major_branch":
            continue
        if bool(spec.get("portal_room", False)) or str(spec.get("size", "")) != "large":
            continue
        parent_ids = [int(parent_id) for parent_id in spec.get("incoming", [])]
        if not parent_ids:
            continue
        non_portal_children = [
            int(child_id)
            for child_id in spec.get("children", [])
            if not bool(node_specs[int(child_id)].get("portal_room", False))
        ]
        if non_portal_children:
            continue
        portal_children = [
            int(child_id)
            for child_id in spec.get("children", [])
            if bool(node_specs[int(child_id)].get("portal_room", False))
        ]
        if len(portal_children) > 1:
            continue

        endpoint_id = portal_children[0] if portal_children else node_id
        path_ids = [endpoint_id]
        current_ref = endpoint_id
        has_backtrack = False
        while True:
            incoming_ids = [int(parent_id) for parent_id in node_specs[current_ref].get("incoming", [])]
            if not incoming_ids:
                break
            parent_ref = incoming_ids[0]
            if int(node_specs[current_ref]["depth"]) < int(node_specs[parent_ref]["depth"]):
                has_backtrack = True
            path_ids.append(parent_ref)
            current_ref = parent_ref
        if current_ref != start_id or not has_backtrack:
            continue
        branch_boss_candidates.append(
            (
                len(path_ids),
                -int(spec["depth"]),
                abs(int(spec["lane"])),
                list(reversed(path_ids)),
            )
        )

    if branch_boss_candidates:
        new_main_path_ids = max(branch_boss_candidates)[3]
        old_boss_id = main_path_ids[-1]
        new_boss_id = new_main_path_ids[-1]
        if old_boss_id != new_boss_id:
            node_specs[old_boss_id]["role"] = "rest"
            node_specs[old_boss_id]["room_name"] = "主路休整房终点"
            node_specs[new_boss_id]["role"] = "boss"
            node_specs[new_boss_id]["room_name"] = "Boss房"
            node_specs[new_boss_id]["portal_room"] = False
            main_path_ids = new_main_path_ids
            main_path_set = set(main_path_ids)
            for node_id, spec in node_specs.items():
                if node_id in main_path_set:
                    spec["branch_type"] = "main_path"
                elif str(spec.get("branch_type", "")) == "main_path":
                    spec["branch_type"] = "major_branch" if str(spec.get("size", "")) == "large" else "minor_branch"

    nodes: list[GraphRoomNode] = []
    for node_id in sorted(node_specs):
        spec = node_specs[node_id]
        depth = int(spec["depth"])
        lane = int(spec["lane"])
        needs_left = any(int(node_specs[parent_id]["depth"]) < depth for parent_id in spec["incoming"]) or any(
            int(node_specs[child_id]["depth"]) < depth for child_id in spec["children"]
        )
        needs_right = any(int(node_specs[parent_id]["depth"]) > depth for parent_id in spec["incoming"]) or any(
            int(node_specs[child_id]["depth"]) > depth for child_id in spec["children"]
        )
        map_file = _room_file_for_sides(
            str(spec["role"]),
            str(spec["size"]),
            needs_left,
            needs_right,
            is_portal_room=bool(spec.get("portal_room", False)),
        )
        nodes.append(
            GraphRoomNode(
                node_id=node_id,
                room_type=str(spec["role"]),
                room_size=str(spec["size"]),
                branch_type=str(spec["branch_type"]),
                depth=depth,
                lane=lane,
                room_name=str(spec["room_name"]),
                map_file=map_file,
                incoming_ids=sorted(int(parent_id) for parent_id in spec["incoming"]),
                outgoing_ids=sorted(int(child_id) for child_id in spec["children"]),
            )
        )

    return _finalize_graph_map(seed, map_folder, generation_rules, nodes, start_id, main_path_ids[-1], main_path_ids)


def generate_room_graph(seed: int, floor_number: int = 1, map_folder: str = "初始地图") -> GraphMapData:
    definition = _load_map_definition(map_folder)
    generation_rules = _normalize_generation_rules(definition)
    if generation_rules.get("mode") == "random_layout":
        return _generate_random_room_graph(seed, floor_number, map_folder, generation_rules, definition)

    room_specs = definition.get("rooms")
    if not isinstance(room_specs, list) or not room_specs:
        raise ValueError("Map definition must contain a non-empty 'rooms' list")

    specs_by_id: dict[int, dict[str, object]] = {}
    for raw_spec in room_specs:
        if not isinstance(raw_spec, dict):
            raise ValueError("Each room spec must be an object")
        room_id = int(raw_spec["id"])
        specs_by_id[room_id] = raw_spec

    start_id = int(definition.get("start_id", min(specs_by_id)))
    exit_id = int(definition.get("exit_id", max(specs_by_id)))
    parents: dict[int, list[int]] = {room_id: [] for room_id in specs_by_id}
    nodes: list[GraphRoomNode] = []
    for room_id in sorted(specs_by_id):
        spec = specs_by_id[room_id]
        child_ids = [int(child_id) for child_id in spec.get("children", [])]
        for child_id in child_ids:
            if child_id not in specs_by_id:
                raise ValueError(f"Unknown child room id {child_id} referenced by room {room_id}")
            parents[child_id].append(room_id)
        position = spec.get("position", [0, 0])
        if not isinstance(position, list) or len(position) != 2:
            raise ValueError(f"Room {room_id} position must be [depth, lane]")
        nodes.append(
            GraphRoomNode(
                node_id=room_id,
                room_type=str(spec.get("role", "combat")),
                room_size=str(spec.get("size", "large")),
                branch_type=str(spec.get("branch", "main_path")),
                depth=int(position[0]),
                lane=int(position[1]),
                room_name=str(spec.get("name", f"Room {room_id}")),
                map_file=str(spec["file"]),
                incoming_ids=[],
                outgoing_ids=child_ids,
            )
        )

    nodes.sort(key=lambda node: node.node_id)
    for node in nodes:
        node.incoming_ids = sorted(parents[node.node_id])

    if start_id not in specs_by_id or exit_id not in specs_by_id:
        raise ValueError("start_id or exit_id references an unknown room")

    main_path_ids = [int(room_id) for room_id in definition.get("main_path_ids", [start_id])]
    if not main_path_ids:
        main_path_ids = [start_id]
    if main_path_ids[-1] != exit_id:
        main_path_ids.append(exit_id)

    return _finalize_graph_map(seed, map_folder, generation_rules, nodes, start_id, exit_id, main_path_ids)


def _validate_branch_rules(graph_map: GraphMapData) -> None:
    invalid_major_branch_leaves = [
        node.node_id
        for node in graph_map.nodes
        if node.branch_type == "major_branch" and not node.child_ids and node.room_size != "large"
    ]
    if invalid_major_branch_leaves:
        joined_ids = ", ".join(str(node_id) for node_id in invalid_major_branch_leaves)
        raise ValueError(f"major_branch leaf rooms must be large: {joined_ids}")


def _validate_corridor_rules(graph_map: GraphMapData) -> None:
    corridor_rules = graph_map.generation_rules.get("corridor_rules", {})
    if not isinstance(corridor_rules, dict):
        return

    max_vertical_shaft_segments = int(corridor_rules.get("max_vertical_shaft_segments", 2))
    max_connected_straight_segments = int(corridor_rules.get("max_connected_straight_segments", 3))
    nodes_by_id = {node.node_id: node for node in graph_map.nodes}
    violations: list[str] = []

    for node in graph_map.nodes:
        for child_id in node.child_ids:
            child = nodes_by_id[child_id]
            vertical_span = abs(child.lane - node.lane)
            horizontal_span = abs(child.depth - node.depth)
            if vertical_span > max_vertical_shaft_segments:
                violations.append(
                    f"edge {node.node_id}->{child_id} vertical span {vertical_span} exceeds {max_vertical_shaft_segments}"
                )
            if horizontal_span > max_connected_straight_segments:
                violations.append(
                    f"edge {node.node_id}->{child_id} horizontal span {horizontal_span} exceeds {max_connected_straight_segments}"
                )

    if violations:
        raise ValueError("corridor rules violated: " + "; ".join(violations[:8]))


def connectivity_check(graph_map: GraphMapData) -> bool:
    if not graph_map.nodes:
        return False
    reachable_ids = {graph_map.start_id}
    queue = deque([graph_map.start_id])
    while queue:
        node_id = queue.popleft()
        for child_id in graph_map.nodes[node_id].child_ids:
            if child_id in reachable_ids:
                continue
            reachable_ids.add(child_id)
            queue.append(child_id)
    return len(reachable_ids) == len(graph_map.nodes)
