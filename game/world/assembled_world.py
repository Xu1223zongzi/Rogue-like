from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import random

import pygame

from game.config import TILE_SIZE
from game.world.graph_map import GraphMapData, GraphRoomNode


EMPTY_TILE = 0
SOLID_TILE = 1
SEMISOLID_TILE = 2
START_TILE = 3
EXIT_TILE = 4

CANVAS_EMPTY = -1
WALL_VALUE = 0
OPEN_VALUE = 1
HALF_VALUE = 2
WALKABLE_VALUES = {OPEN_VALUE, HALF_VALUE}

CHAR_TO_TILE = {
    "0": WALL_VALUE,
    "1": OPEN_VALUE,
    "2": HALF_VALUE,
    "#": WALL_VALUE,
    ".": OPEN_VALUE,
    "=": HALF_VALUE,
}
TILE_TO_CHAR = {
    WALL_VALUE: "#",
    OPEN_VALUE: ".",
    HALF_VALUE: "=",
}


class AssemblyError(RuntimeError):
    pass


@dataclass
class ComponentDef:
    name: str
    category: str
    tile_grid: list[list[int]]
    sockets: dict[str, tuple[int, int] | None]
    junction: tuple[int, int]

    @property
    def width(self) -> int:
        return len(self.tile_grid[0])

    @property
    def height(self) -> int:
        return len(self.tile_grid)

    @property
    def open_sides(self) -> frozenset[str]:
        return frozenset(side for side, socket in self.sockets.items() if socket is not None)

    def socket(self, side: str) -> tuple[int, int]:
        socket = self.sockets.get(side)
        if socket is None:
            raise AssemblyError(f"Component {self.name} has no '{side}' socket")
        return socket


@dataclass
class EdgeBlueprint:
    source_id: int
    target_id: int


@dataclass
class RouteSegment:
    orientation: str
    start: tuple[int, int]
    end: tuple[int, int]


@dataclass
class PlacementRoom:
    node: GraphRoomNode
    component: ComponentDef
    left: int
    top: int
    sockets: dict[str, tuple[int, int] | None]

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.left, self.top, self.component.width, self.component.height)

    def socket_point(self, side: str) -> tuple[int, int]:
        socket = self.sockets.get(side)
        if socket is None:
            raise AssemblyError(f"Placed room {self.node.node_id} has no '{side}' socket")
        return socket


@dataclass
class EmbeddedAssemblyResult:
    full_map: list[list[int]]
    char_map: list[str]
    room_placements: dict[int, PlacementRoom]
    connector_placements: list[ConnectorPlacement]
    start_world: tuple[float, float]
    exit_rect: pygame.Rect
    debug_lines: list[str]


@dataclass(frozen=True)
class ConnectorPlacement:
    component: ComponentDef
    left: int
    top: int
    point: tuple[int, int]
    sides: frozenset[str]

    def global_socket(self, side: str) -> tuple[int, int] | None:
        socket = self.component.sockets.get(side)
        if socket is None:
            return None
        return (self.left + socket[0], self.top + socket[1])


@dataclass(frozen=True)
class OverlapIssue:
    x: int
    y: int
    existing_source: str
    new_source: str
    existing_value: int
    new_value: int


def _edge_horizontal_gap(base_gap: int, source_node: GraphRoomNode, target_node: GraphRoomNode) -> int:
    if target_node.room_type == "portal":
        return max(4, int(round(base_gap / 3.0)))
    if source_node.lane == target_node.lane and source_node.room_size != target_node.room_size:
        return max(4, int(round(base_gap * 0.5)))
    return base_gap


def _map_root(map_folder: str) -> Path:
    return Path(__file__).resolve().parents[2] / "maps" / map_folder


def _load_generation_rules(map_folder: str) -> dict[str, object]:
    definition = json.loads((_map_root(map_folder) / "地图.json").read_text(encoding="utf-8"))
    generation_rules = definition.get("generation_rules", {})
    if not isinstance(generation_rules, dict):
        raise AssemblyError("地图.json 中缺少 generation_rules")
    return generation_rules


def _decode_tile(char: str) -> int:
    return CHAR_TO_TILE.get(char, WALL_VALUE)


def _read_component_grid(path: Path) -> list[list[int]]:
    lines = [line.rstrip("\n\r") for line in path.read_text(encoding="utf-8").splitlines()]
    lines = [line for line in lines if line and not line.startswith("//") and not line.startswith(";")]
    if not lines:
        raise AssemblyError(f"Component file is empty: {path}")
    width = max(len(line) for line in lines)
    return [[_decode_tile(char) for char in line.ljust(width, "0")] for line in lines]


def _median_value(values: list[int]) -> int:
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def _walkable_indices(values: list[int]) -> list[int]:
    return [index for index, value in enumerate(values) if value in WALKABLE_VALUES]


def _detect_side_socket(tile_grid: list[list[int]], side: str) -> tuple[int, int] | None:
    height = len(tile_grid)
    width = len(tile_grid[0])
    if side == "left":
        candidates = _walkable_indices([tile_grid[row][0] for row in range(height)])
        return None if not candidates else (0, _median_value(candidates))
    if side == "right":
        candidates = _walkable_indices([tile_grid[row][width - 1] for row in range(height)])
        return None if not candidates else (width - 1, _median_value(candidates))
    if side == "top":
        candidates = _walkable_indices(tile_grid[0])
        return None if not candidates else (_median_value(candidates), 0)
    if side == "bottom":
        candidates = _walkable_indices(tile_grid[height - 1])
        return None if not candidates else (_median_value(candidates), height - 1)
    raise AssemblyError(f"Unknown side {side}")


def _detect_junction(component: ComponentDef) -> tuple[int, int]:
    vertical_xs = [socket[0] for side, socket in component.sockets.items() if side in {"top", "bottom"} and socket is not None]
    horizontal_ys = [socket[1] for side, socket in component.sockets.items() if side in {"left", "right"} and socket is not None]
    if not vertical_xs:
        left_socket = component.sockets.get("left")
        right_socket = component.sockets.get("right")
        if left_socket is not None and right_socket is not None:
            vertical_xs = [(left_socket[0] + right_socket[0]) // 2]
        else:
            vertical_xs = [component.width // 2]
    if not horizontal_ys:
        top_socket = component.sockets.get("top")
        bottom_socket = component.sockets.get("bottom")
        if top_socket is not None and bottom_socket is not None:
            horizontal_ys = [(top_socket[1] + bottom_socket[1]) // 2]
        else:
            horizontal_ys = [component.height // 2]
    return (_median_value(vertical_xs), _median_value(horizontal_ys))


def _analyze_component(name: str, category: str, tile_grid: list[list[int]]) -> ComponentDef:
    if _is_shaft_replacement_component_name(name):
        tile_grid = [row[:] for row in tile_grid]
        for row in tile_grid:
            if row[0] in WALKABLE_VALUES:
                row[0] = WALL_VALUE
            if row[-1] in WALKABLE_VALUES:
                row[-1] = WALL_VALUE
    component = ComponentDef(
        name=name,
        category=category,
        tile_grid=tile_grid,
        sockets={
            "left": _detect_side_socket(tile_grid, "left"),
            "right": _detect_side_socket(tile_grid, "right"),
            "top": _detect_side_socket(tile_grid, "top"),
            "bottom": _detect_side_socket(tile_grid, "bottom"),
        },
        junction=(0, 0),
    )
    if _is_shaft_replacement_component_name(name):
        component.sockets["left"] = None
        component.sockets["right"] = None
    component.junction = _detect_junction(component)
    return component


def _is_shaft_replacement_component_name(name: str) -> bool:
    return name.startswith("普通通道/竖井替换_")


def _shaft_variant_components(library: dict[str, ComponentDef]) -> list[ComponentDef]:
    return [library["普通通道/竖井_00"]]


def _choose_shaft_component(
    shaft_components: list[ComponentDef],
    rng: random.Random,
    replacement_probability: float = 0.12,
) -> ComponentDef:
    if len(shaft_components) <= 1 or rng.random() >= replacement_probability:
        return shaft_components[0]
    return shaft_components[1 + rng.randrange(len(shaft_components) - 1)]


def _load_component_library(map_folder: str) -> dict[str, ComponentDef]:
    library: dict[str, ComponentDef] = {}
    for category in ["房间组件", "普通通道", "基础连接通道", "特殊连接通道"]:
        for file_path in sorted((_map_root(map_folder) / category).glob("*.txt")):
            relative_name = f"{category}/{file_path.stem}"
            library[relative_name] = _analyze_component(relative_name, category, _read_component_grid(file_path))
    return library


def _room_component_key(node: GraphRoomNode) -> str:
    return node.map_file[:-4] if node.map_file.endswith(".txt") else node.map_file


def _make_edges(graph_map: GraphMapData) -> list[EdgeBlueprint]:
    edges: list[EdgeBlueprint] = []
    for node in graph_map.nodes:
        for child_id in node.child_ids:
            edges.append(EdgeBlueprint(source_id=node.node_id, target_id=child_id))
    return edges


def _depth_lane_rank(graph_map: GraphMapData) -> dict[int, int]:
    rank_by_id: dict[int, int] = {}
    depth_groups: dict[int, list[GraphRoomNode]] = {}
    for node in graph_map.nodes:
        depth_groups.setdefault(node.depth, []).append(node)
    for depth_nodes in depth_groups.values():
        for rank, node in enumerate(sorted(depth_nodes, key=lambda item: (item.lane, item.node_id))):
            rank_by_id[node.node_id] = rank
    return rank_by_id


def _anchor_side(node: GraphRoomNode, nodes_by_id: dict[int, GraphRoomNode], component: ComponentDef) -> str | None:
    if node.parent_id is not None:
        parent = nodes_by_id[node.parent_id]
        if parent.depth < node.depth and component.sockets["left"] is not None:
            return "left"
        if parent.depth > node.depth and component.sockets["right"] is not None:
            return "right"
    if any(nodes_by_id[child_id].depth > node.depth for child_id in node.child_ids) and component.sockets["right"] is not None:
        return "right"
    if any(nodes_by_id[child_id].depth < node.depth for child_id in node.child_ids) and component.sockets["left"] is not None:
        return "left"
    if component.sockets["left"] is not None:
        return "left"
    if component.sockets["right"] is not None:
        return "right"
    return None


def _component_body_span(component: ComponentDef, orientation: str) -> int:
    if orientation == "horizontal":
        start_socket = component.socket("left")[0]
        end_socket = component.socket("right")[0]
        body_start = min(start_socket, end_socket) + 1
        body_end = max(start_socket, end_socket) - 1
    else:
        start_socket = component.socket("top")[1]
        end_socket = component.socket("bottom")[1]
        body_start = min(start_socket, end_socket) + 1
        body_end = max(start_socket, end_socket)
    return max(1, body_end - body_start + 1)


def _max_supported_span(component: ComponentDef, orientation: str, segment_count: int) -> int:
    if segment_count <= 0:
        return 0
    component_span = component.width if orientation == "horizontal" else component.height
    body_span = _component_body_span(component, orientation)
    return component_span * 2 - 1 + body_span * max(0, segment_count - 2)


def _build_placement_room(node: GraphRoomNode, component: ComponentDef, left: int, top: int) -> PlacementRoom:
    return PlacementRoom(
        node=node,
        component=component,
        left=left,
        top=top,
        sockets={
            side: None if socket is None else (left + socket[0], top + socket[1])
            for side, socket in component.sockets.items()
        },
    )


def _shift_placements(placements: dict[int, PlacementRoom], offset_x: int, offset_y: int) -> dict[int, PlacementRoom]:
    if offset_x == 0 and offset_y == 0:
        return placements
    shifted: dict[int, PlacementRoom] = {}
    for node_id, placement in placements.items():
        shifted[node_id] = _build_placement_room(
            placement.node,
            placement.component,
            placement.left + offset_x,
            placement.top + offset_y,
        )
    return shifted


def _compute_room_placements(
    graph_map: GraphMapData,
    library: dict[str, ComponentDef],
    generation_rules: dict[str, object],
) -> dict[int, PlacementRoom]:
    straight = library["普通通道/直道_00"]
    shaft = library["普通通道/竖井_00"]
    corridor_rules = generation_rules.get("corridor_rules", {})
    if corridor_rules is None:
        corridor_rules = {}
    if not isinstance(corridor_rules, dict):
        raise AssemblyError("corridor_rules must be an object")

    route_gap = max(straight.width * 2, 12)
    horizontal_body_span = _component_body_span(straight, "horizontal")
    vertical_body_span = _component_body_span(shaft, "vertical")
    max_vertical_segments = max(1, int(corridor_rules.get("max_vertical_shaft_segments", 2)))
    max_straight_segments = max(1, int(corridor_rules.get("max_connected_straight_segments", 5)))
    start_left = 120
    start_top = 140
    padding = 64
    nodes_by_id = {node.node_id: node for node in graph_map.nodes}

    placements: dict[int, PlacementRoom] = {}
    start_node = nodes_by_id[graph_map.start_id]
    start_component = library[_room_component_key(start_node)]
    placements[start_node.node_id] = _build_placement_room(start_node, start_component, start_left, start_top)

    pending_ids = [start_node.node_id]
    while pending_ids:
        parent_id = pending_ids.pop(0)
        parent_room = placements[parent_id]
        parent_node = nodes_by_id[parent_id]

        for child_id in parent_node.child_ids:
            if child_id in placements:
                continue

            child_node = nodes_by_id[child_id]
            child_component = library[_room_component_key(child_node)]
            depth_delta = abs(child_node.depth - parent_node.depth)
            lane_delta = child_node.lane - parent_node.lane
            edge_gap = _edge_horizontal_gap(route_gap, parent_node, child_node)
            straight_steps = depth_delta if depth_delta > 0 else max_straight_segments
            if child_node.room_type == "portal":
                horizontal_span = 0
            else:
                horizontal_span = horizontal_body_span * min(max(1, straight_steps), max_straight_segments)
            vertical_span = 0
            if lane_delta != 0:
                vertical_steps = max_vertical_segments
                vertical_span = _max_supported_span(shaft, "vertical", vertical_steps)

            if child_node.depth >= parent_node.depth:
                parent_side = "right"
                child_side = "left"
                parent_socket = parent_room.socket_point(parent_side)
                child_socket = child_component.socket(child_side)
                direction = 1
            else:
                parent_side = "left"
                child_side = "right"
                parent_socket = parent_room.socket_point(parent_side)
                child_socket = child_component.socket(child_side)
                direction = -1

            if lane_delta > 0:
                target_socket_y = parent_socket[1] + vertical_span
            elif lane_delta < 0:
                target_socket_y = parent_socket[1] - vertical_span
            else:
                target_socket_y = parent_socket[1]

            target_socket_x = parent_socket[0] + direction * (edge_gap + horizontal_span)
            placements[child_id] = _build_placement_room(
                child_node,
                child_component,
                target_socket_x - child_socket[0],
                target_socket_y - child_socket[1],
            )
            pending_ids.append(child_id)

    min_left = min((placement.left for placement in placements.values()), default=0)
    min_top = min((placement.top for placement in placements.values()), default=0)
    offset_x = padding - min_left if min_left < padding else 0
    offset_y = padding - min_top if min_top < padding else 0
    return _shift_placements(placements, offset_x, offset_y)


def _validate_room_overlaps(placements: dict[int, PlacementRoom]) -> None:
    ordered = sorted(placements.values(), key=lambda room: room.node.node_id)
    conflicts: list[str] = []
    for index, room in enumerate(ordered):
        for other in ordered[index + 1 :]:
            if room.rect.colliderect(other.rect):
                conflicts.append(f"room {room.node.node_id} overlaps room {other.node.node_id}")
    if conflicts:
        raise AssemblyError("; ".join(conflicts[:6]))


def _add_incident(incidents: dict[tuple[int, int], set[str]], point: tuple[int, int], direction: str) -> None:
    incidents.setdefault(point, set()).add(direction)


def _pick_connection_sides(source_room: PlacementRoom, target_room: PlacementRoom) -> tuple[str, str]:
    if target_room.left >= source_room.left and source_room.sockets["right"] is not None and target_room.sockets["left"] is not None:
        return ("right", "left")
    if target_room.left < source_room.left and source_room.sockets["left"] is not None and target_room.sockets["right"] is not None:
        return ("left", "right")
    if source_room.sockets["right"] is not None and target_room.sockets["left"] is not None:
        return ("right", "left")
    if source_room.sockets["left"] is not None and target_room.sockets["right"] is not None:
        return ("left", "right")
    raise AssemblyError(f"Cannot find horizontal sockets between room {source_room.node.node_id} and room {target_room.node.node_id}")


def _build_routes(
    edges: list[EdgeBlueprint],
    placements: dict[int, PlacementRoom],
    library: dict[str, ComponentDef],
) -> tuple[list[RouteSegment], dict[tuple[int, int], set[str]], set[tuple[int, int]], list[str], dict[tuple[int, int], int]]:
    straight = library["普通通道/直道_00"]
    gap = max(straight.width * 2, 12)
    segments: list[RouteSegment] = []
    incidents: dict[tuple[int, int], set[str]] = {}
    room_anchor_points: set[tuple[int, int]] = set()
    debug_lines: list[str] = []
    multi_l_top_offsets: dict[tuple[int, int], int] = {}

    route_specs: list[tuple[EdgeBlueprint, PlacementRoom, PlacementRoom, str, str, tuple[int, int], tuple[int, int]]] = []
    room_side_usage: dict[int, dict[str, int]] = {}
    room_side_flows: dict[int, dict[str, dict[str, int]]] = {}

    for edge in edges:
        source_room = placements[edge.source_id]
        target_room = placements[edge.target_id]
        source_side, target_side = _pick_connection_sides(source_room, target_room)
        source_point = source_room.socket_point(source_side)
        target_point = target_room.socket_point(target_side)
        route_specs.append((edge, source_room, target_room, source_side, target_side, source_point, target_point))
        room_side_usage.setdefault(source_room.node.node_id, {}).setdefault(source_side, 0)
        room_side_usage[source_room.node.node_id][source_side] += 1
        room_side_usage.setdefault(target_room.node.node_id, {}).setdefault(target_side, 0)
        room_side_usage[target_room.node.node_id][target_side] += 1
        room_side_flows.setdefault(source_room.node.node_id, {}).setdefault(source_side, {"incoming": 0, "outgoing": 0})
        room_side_flows[source_room.node.node_id][source_side]["outgoing"] += 1
        room_side_flows.setdefault(target_room.node.node_id, {}).setdefault(target_side, {"incoming": 0, "outgoing": 0})
        room_side_flows[target_room.node.node_id][target_side]["incoming"] += 1

    def should_promote_room_side(node_id: int, side: str) -> bool:
        usage = room_side_usage.get(node_id, {}).get(side, 0)
        if usage <= 1:
            return False
        flows = room_side_flows.get(node_id, {}).get(side, {"incoming": 0, "outgoing": 0})
        if flows["incoming"] == 1 and flows["outgoing"] == 1:
            return False
        return True

    pass_through_side_route_x: dict[tuple[int, str], int] = {}
    for node_id, sides in room_side_flows.items():
        room = placements[node_id]
        for side, flows in sides.items():
            if room_side_usage.get(node_id, {}).get(side, 0) != 2:
                continue
            if flows["incoming"] != 1 or flows["outgoing"] != 1:
                continue
            anchor = room.socket_point(side)
            pass_through_side_route_x[(node_id, side)] = anchor[0] + (-gap if side == "left" else gap)

    for edge, source_room, target_room, source_side, target_side, source_point, target_point in route_specs:
        room_anchor_points.add(source_point)
        room_anchor_points.add(target_point)

        edge_gap = _edge_horizontal_gap(gap, source_room.node, target_room.node)
        horizontal_sign = -1 if source_side == "left" else 1
        default_route_x = source_point[0] + horizontal_sign * edge_gap
        route_x = pass_through_side_route_x.get((target_room.node.node_id, target_side))
        if route_x is None:
            route_x = pass_through_side_route_x.get((source_room.node.node_id, source_side), default_route_x)
        source_junction = (default_route_x, source_point[1])
        target_top_junction = (default_route_x, target_point[1])
        target_junction = (route_x, target_point[1])

        if route_x != default_route_x and (target_room.node.node_id, target_side) in pass_through_side_route_x:
            signed_offset = route_x - default_route_x
            current_offset = multi_l_top_offsets.get(target_junction)
            if current_offset is None or abs(signed_offset) > abs(current_offset):
                multi_l_top_offsets[target_junction] = signed_offset

        segments.append(RouteSegment("horizontal", source_point, source_junction))
        if source_junction[1] != target_top_junction[1]:
            segments.append(RouteSegment("vertical", source_junction, target_top_junction))
        if target_top_junction != target_junction:
            segments.append(RouteSegment("horizontal", target_top_junction, target_junction))
        segments.append(RouteSegment("horizontal", target_junction, target_point))

        if source_point != source_junction:
            _add_incident(incidents, source_junction, "left" if source_side == "right" else "right")
            if should_promote_room_side(source_room.node.node_id, source_side):
                _add_incident(incidents, source_junction, source_side)
        if source_junction[1] != target_top_junction[1]:
            _add_incident(incidents, source_junction, "down" if target_top_junction[1] > source_junction[1] else "up")
            _add_incident(incidents, target_top_junction, "up" if target_top_junction[1] > source_junction[1] else "down")
        if target_top_junction != target_junction:
            _add_incident(incidents, target_top_junction, "right" if target_junction[0] > target_top_junction[0] else "left")
            _add_incident(incidents, target_junction, "left" if target_junction[0] > target_top_junction[0] else "right")
        if target_junction != target_point:
            _add_incident(incidents, target_junction, "right" if target_side == "left" else "left")
            if should_promote_room_side(target_room.node.node_id, target_side):
                _add_incident(incidents, target_junction, target_side)

        debug_lines.append(
            f"edge {edge.source_id}->{edge.target_id} via {source_side}/{target_side} {source_point} -> {source_junction} -> {target_top_junction} -> {target_junction} -> {target_point}"
        )

    return segments, incidents, room_anchor_points, debug_lines, multi_l_top_offsets


def _choose_connector_by_sides(library: dict[str, ComponentDef], sides: frozenset[str]) -> ComponentDef:
    normalized_sides = frozenset("top" if side == "up" else "bottom" if side == "down" else side for side in sides)
    if normalized_sides == frozenset({"top", "bottom", "right"}):
        special_candidate = _choose_best_multi_l_component(library, None, None)
        if special_candidate is not None:
            return special_candidate
    candidates = [
        component
        for component in library.values()
        if component.category == "基础连接通道" and component.open_sides == normalized_sides
    ]
    if not candidates:
        raise AssemblyError(f"No connector component matches sides {sorted(normalized_sides)}")
    return candidates[0]


def _segment_other_point(segment: RouteSegment, point: tuple[int, int]) -> tuple[int, int] | None:
    if segment.start == point:
        return segment.end
    if segment.end == point:
        return segment.start
    return None


def _multi_l_sort_key(component: ComponentDef) -> tuple[int, int, str]:
    top_offset, _ = _multi_l_geometry(component)
    stem = component.name.rsplit("/", 1)[-1]
    suffix = stem.rsplit("_", 1)[-1]
    index = int(suffix) if suffix.isdigit() else 10**9
    return (abs(top_offset), index, stem)


def _is_multi_l_component_name(name: str) -> bool:
    return (
        name.startswith("特殊连接通道/多L_")
        or name.startswith("特殊连接通道/多L反_")
        or name.startswith("特殊连接通道/多L反2_")
    )


def _multi_l_components(library: dict[str, ComponentDef]) -> list[ComponentDef]:
    components: list[ComponentDef] = []
    for name, component in library.items():
        if not _is_multi_l_component_name(name):
            continue
        suffix = name.rsplit("_", 1)[-1]
        if suffix.isdigit():
            components.append(component)
    return sorted(components, key=_multi_l_sort_key)


def _multi_l_forward_components(library: dict[str, ComponentDef]) -> list[ComponentDef]:
    return [component for component in _multi_l_components(library) if component.name.startswith("特殊连接通道/多L_")]


def _normalize_incident_sides(sides: set[str] | frozenset[str]) -> frozenset[str]:
    return frozenset("top" if side == "up" else "bottom" if side == "down" else side for side in sides)


def _horizontal_run_from_point(point: tuple[int, int], segments: list[RouteSegment]) -> int:
    right_run = 0
    for segment in segments:
        if segment.orientation != "horizontal":
            continue
        if segment.start != point or segment.end[0] <= point[0]:
            continue
        right_run = max(right_run, segment.end[0] - point[0])
    return right_run


def _multi_l_anchor(component: ComponentDef) -> tuple[int, int]:
    if component.name.startswith("特殊连接通道/多L反_"):
        top_socket = component.sockets.get("top")
        if top_socket is not None:
            return (top_socket[0], component.junction[1])
    bottom_socket = component.sockets.get("bottom")
    if bottom_socket is not None:
        return (bottom_socket[0], component.junction[1])
    return component.junction


def _multi_l_geometry(component: ComponentDef) -> tuple[int, int]:
    top_socket = component.sockets.get("top")
    bottom_socket = component.sockets.get("bottom")
    right_socket = component.sockets.get("right")
    if top_socket is None or bottom_socket is None or right_socket is None:
        raise AssemblyError(f"Multi-L component is missing required sockets: {component.name}")
    anchor = _multi_l_anchor(component)
    if component.name.startswith("特殊连接通道/多L反_"):
        top_offset = top_socket[0] - bottom_socket[0]
    else:
        top_offset = anchor[0] - top_socket[0]
    right_span = right_socket[0] - anchor[0]
    return top_offset, right_span


def _choose_best_multi_l_component(
    library: dict[str, ComponentDef],
    top_offset_hint: int | None,
    right_run_hint: int | None,
) -> ComponentDef | None:
    multi_l_candidates = _multi_l_forward_components(library)
    return _choose_best_multi_l_component_from_candidates(multi_l_candidates, top_offset_hint, right_run_hint)


def _choose_best_multi_l_component_from_candidates(
    multi_l_candidates: list[ComponentDef],
    top_offset_hint: int | None,
    right_run_hint: int | None,
) -> ComponentDef | None:
    if not multi_l_candidates:
        return None

    max_right_span = max(_multi_l_geometry(component)[1] for component in multi_l_candidates)
    target_top_offset = top_offset_hint
    target_right_span = None if right_run_hint is None else min(max(0, right_run_hint), max_right_span)

    best_score: tuple[int, int, int, str] | None = None
    best_component: ComponentDef | None = None
    for component in multi_l_candidates:
        top_offset, right_span = _multi_l_geometry(component)
        top_penalty = 0 if target_top_offset is None else abs(top_offset - target_top_offset)
        right_penalty = 0 if target_right_span is None else abs(right_span - target_right_span)
        sign_penalty = 0
        if target_top_offset is not None and top_offset != 0:
            sign_penalty = 0 if (top_offset > 0) == (target_top_offset > 0) else 1
        score = (top_penalty, sign_penalty, right_penalty, component.name)
        if best_score is None or score < best_score:
            best_score = score
            best_component = component
    return best_component


def _compress_multi_l_incidents(
    library: dict[str, ComponentDef],
    segments: list[RouteSegment],
    incidents: dict[tuple[int, int], set[str]],
    room_anchor_points: set[tuple[int, int]],
) -> tuple[list[RouteSegment], dict[tuple[int, int], set[str]], dict[tuple[int, int], ComponentDef]]:
    multi_l_candidates = _multi_l_components(library)
    if not multi_l_candidates:
        return segments, incidents, {}

    compressed_incidents = {point: set(sides) for point, sides in incidents.items()}
    override_components: dict[tuple[int, int], ComponentDef] = {}
    removed_points: set[tuple[int, int]] = set()
    removed_segment_ids: set[int] = set()

    for segment_index, segment in enumerate(segments):
        if segment.orientation != "horizontal":
            continue
        if segment.start[1] != segment.end[1] or segment.start[0] == segment.end[0]:
            continue
        left_point, right_point = sorted((segment.start, segment.end), key=lambda point: point[0])
        if left_point in room_anchor_points or right_point in room_anchor_points:
            continue
        if left_point in removed_points or right_point in removed_points:
            continue

        left_sides = compressed_incidents.get(left_point)
        right_sides = compressed_incidents.get(right_point)
        if left_sides is None or right_sides is None:
            continue

        left_norm = _normalize_incident_sides(left_sides)
        right_norm = _normalize_incident_sides(right_sides)

        if left_norm in {frozenset({"right", "top"}), frozenset({"left", "right", "top"})} and right_norm == frozenset({"bottom", "left", "right"}):
            right_run = _horizontal_run_from_point(right_point, segments)
            top_offset = right_point[0] - left_point[0]
            special_candidate = _choose_best_multi_l_component(library, top_offset, right_run)
            if special_candidate is None:
                continue

            override_components[right_point] = special_candidate
            compressed_incidents[right_point] = {"up", "down", "right"}
            removed_points.add(left_point)
            removed_segment_ids.add(segment_index)
            continue

        if left_norm == frozenset({"right", "top"}) and right_norm == frozenset({"bottom", "left"}):
            continue

        if left_norm == frozenset({"bottom", "right"}) and right_norm == frozenset({"left", "top"}):
            right_run = _horizontal_run_from_point(left_point, segments)
            top_offset = left_point[0] - right_point[0]
            special_candidate = _choose_best_multi_l_component_from_candidates(
                [component for component in _multi_l_components(library) if component.name.startswith("特殊连接通道/多L反2_")],
                top_offset,
                right_run,
            )
            if special_candidate is None:
                continue

            override_components[left_point] = special_candidate
            compressed_incidents[left_point] = {"up", "down", "right"}
            removed_points.add(right_point)
            removed_segment_ids.add(segment_index)

    for point in removed_points:
        compressed_incidents.pop(point, None)

    compressed_segments = [segment for index, segment in enumerate(segments) if index not in removed_segment_ids]
    return compressed_segments, compressed_incidents, override_components


def _choose_connector_for_incident(
    library: dict[str, ComponentDef],
    point: tuple[int, int],
    sides: frozenset[str],
    segments: list[RouteSegment],
    multi_l_top_offset: int | None = None,
) -> ComponentDef:
    normalized_sides = frozenset("top" if side == "up" else "bottom" if side == "down" else side for side in sides)
    if normalized_sides != frozenset({"top", "bottom", "right"}):
        return _choose_connector_by_sides(library, normalized_sides)

    right_run = _horizontal_run_from_point(point, segments)
    special_candidate = _choose_best_multi_l_component(library, multi_l_top_offset, right_run if right_run > 0 else None)
    if special_candidate is not None:
        return special_candidate
    return _choose_connector_by_sides(library, normalized_sides)


def _connector_top_left(component: ComponentDef, point: tuple[int, int]) -> tuple[int, int]:
    anchor = _multi_l_anchor(component) if component.name.startswith("特殊连接通道/多L") else component.junction
    return (point[0] - anchor[0], point[1] - anchor[1])


def _canvas_bounds(placements: dict[int, PlacementRoom], segments: list[RouteSegment], library: dict[str, ComponentDef]) -> tuple[int, int]:
    max_x = 0
    max_y = 0
    for placement in placements.values():
        max_x = max(max_x, placement.left + placement.component.width + 32)
        max_y = max(max_y, placement.top + placement.component.height + 32)
    straight = library["普通通道/直道_00"]
    shaft = library["普通通道/竖井_00"]
    for segment in segments:
        extra_x = straight.width if segment.orientation == "horizontal" else shaft.width
        extra_y = straight.height if segment.orientation == "horizontal" else shaft.height
        max_x = max(max_x, max(segment.start[0], segment.end[0]) + extra_x + 32)
        max_y = max(max_y, max(segment.start[1], segment.end[1]) + extra_y + 32)
    return max_x + 64, max_y + 64


def _stamp_tile_grid(
    canvas: list[list[int]],
    owners: list[list[str | None]],
    tile_grid: list[list[int]],
    left: int,
    top: int,
    source: str,
    allowed_overlap_points: set[tuple[int, int]],
    overlap_issues: list[OverlapIssue],
) -> None:
    for row_index, row in enumerate(tile_grid):
        for col_index, value in enumerate(row):
            y = top + row_index
            x = left + col_index
            if not (0 <= y < len(canvas) and 0 <= x < len(canvas[0])):
                continue
            existing_value = canvas[y][x]
            existing_owner = owners[y][x]
            point = (x, y)
            if value == CANVAS_EMPTY:
                continue
            same_route_joint = (
                existing_value == value
                and existing_owner is not None
                and existing_owner != source
                and _is_route_primitive(existing_owner)
                and _is_route_primitive(source)
            )
            if _should_preserve_connector_walkable_overlap(point, existing_value, value, existing_owner, source, allowed_overlap_points):
                continue
            if _should_preserve_connector_half_tile(point, existing_value, value, existing_owner, source, allowed_overlap_points):
                continue
            if existing_value != CANVAS_EMPTY and existing_owner is not None and existing_owner != source and point not in allowed_overlap_points:
                if not same_route_joint:
                    overlap_issues.append(
                        OverlapIssue(
                            x=x,
                            y=y,
                            existing_source=existing_owner,
                            new_source=source,
                            existing_value=existing_value,
                            new_value=value,
                        )
                    )
            canvas[y][x] = value
            owners[y][x] = source


def _stamp_horizontal(
    canvas: list[list[int]],
    owners: list[list[str | None]],
    component: ComponentDef,
    start: tuple[int, int],
    end: tuple[int, int],
    source: str,
    allowed_overlap_points: set[tuple[int, int]],
    overlap_issues: list[OverlapIssue],
) -> None:
    start_side = "left" if start[0] <= end[0] else "right"
    end_side = "right" if start_side == "left" else "left"
    start_socket = component.socket(start_side)
    end_socket = component.socket(end_side)
    top = start[1] - start_socket[1]
    start_left = start[0] - start_socket[0]
    end_left = end[0] - end_socket[0]
    left_bound = min(start[0], end[0])
    right_bound = max(start[0], end[0])
    body_start = min(start_socket[0], end_socket[0]) + 1
    body_end = max(start_socket[0], end_socket[0]) - 1
    body_width = max(1, body_end - body_start + 1)

    for x in range(left_bound, right_bound + 1):
        if start_left <= x < start_left + component.width:
            source_col = x - start_left
        elif end_left <= x < end_left + component.width:
            source_col = x - end_left
        else:
            body_offset = (x - (start_left + component.width)) % body_width
            source_col = body_start + body_offset
        for row_index, row in enumerate(component.tile_grid):
            stamp_y = top + row_index
            if not (0 <= stamp_y < len(canvas) and 0 <= x < len(canvas[0])):
                continue
            value = row[source_col]
            if value == CANVAS_EMPTY:
                continue
            existing_value = canvas[stamp_y][x]
            existing_owner = owners[stamp_y][x]
            point = (x, stamp_y)
            same_route_joint = (
                existing_value == value
                and existing_owner is not None
                and existing_owner != source
                and _is_route_primitive(existing_owner)
                and _is_route_primitive(source)
            )
            if existing_value != CANVAS_EMPTY and existing_owner is not None and existing_owner != source and point not in allowed_overlap_points:
                if not same_route_joint:
                    overlap_issues.append(
                        OverlapIssue(
                            x=x,
                            y=stamp_y,
                            existing_source=existing_owner,
                            new_source=source,
                            existing_value=existing_value,
                            new_value=value,
                        )
                    )
            canvas[stamp_y][x] = value
            owners[stamp_y][x] = source


def _stamp_vertical(
    canvas: list[list[int]],
    owners: list[list[str | None]],
    component: ComponentDef,
    start: tuple[int, int],
    end: tuple[int, int],
    source: str,
    allowed_overlap_points: set[tuple[int, int]],
    overlap_issues: list[OverlapIssue],
) -> None:
    start_side = "top" if start[1] <= end[1] else "bottom"
    end_side = "bottom" if start_side == "top" else "top"
    start_socket = component.socket(start_side)
    end_socket = component.socket(end_side)
    left = start[0] - start_socket[0]
    start_top = start[1] - start_socket[1]
    end_top = end[1] - end_socket[1]
    top_bound = min(start[1], end[1])
    bottom_bound = max(start[1], end[1])
    body_start = min(start_socket[1], end_socket[1]) + 1
    pure_vertical = component.sockets["left"] is None and component.sockets["right"] is None
    if pure_vertical:
        body_end = max(start_socket[1], end_socket[1])
    else:
        body_end = max(start_socket[1], end_socket[1]) - 1
    body_height = max(1, body_end - body_start + 1)
    extension_start = body_start
    extension_end = body_end
    if pure_vertical and component.height >= 8:
        extension_start = 0
        extension_end = 7
    extension_height = max(1, extension_end - extension_start + 1)
    upper_component_bottom = min(start_top + component.height, end_top + component.height)
    lower_component_top = max(start_top, end_top)
    no_gap = pure_vertical and upper_component_bottom >= lower_component_top

    for y in range(top_bound, bottom_bound + 1):
        in_start_component = start_top <= y < start_top + component.height
        in_end_component = end_top <= y < end_top + component.height
        if no_gap and y == end[1]:
            continue
        if pure_vertical and y == start[1]:
            source_row = start_socket[1]
        elif pure_vertical and y == end[1]:
            source_row = end_socket[1]
        elif pure_vertical and upper_component_bottom <= y < lower_component_top:
            body_offset = (y - upper_component_bottom) % extension_height
            source_row = extension_end - body_offset
        elif in_start_component:
            source_row = y - start_top
        elif in_end_component:
            source_row = y - end_top
        elif y < start_top:
            body_offset = (start_top - 1 - y) % extension_height
            source_row = extension_end - body_offset
        else:
            body_offset = (y - (start_top + component.height)) % extension_height
            source_row = extension_end - body_offset
        for col_index, value in enumerate(component.tile_grid[source_row]):
            stamp_x = left + col_index
            if not (0 <= y < len(canvas) and 0 <= stamp_x < len(canvas[0])):
                continue
            if value == CANVAS_EMPTY:
                continue
            existing_value = canvas[y][stamp_x]
            existing_owner = owners[y][stamp_x]
            point = (stamp_x, y)
            same_route_joint = (
                existing_value == value
                and existing_owner is not None
                and existing_owner != source
                and _is_route_primitive(existing_owner)
                and _is_route_primitive(source)
            )
            if existing_value != CANVAS_EMPTY and existing_owner is not None and existing_owner != source and point not in allowed_overlap_points:
                if not same_route_joint:
                    overlap_issues.append(
                        OverlapIssue(
                            x=stamp_x,
                            y=y,
                            existing_source=existing_owner,
                            new_source=source,
                            existing_value=existing_value,
                            new_value=value,
                        )
                    )
            canvas[y][stamp_x] = value
            owners[y][stamp_x] = source


def _canvas_to_char_map(canvas: list[list[int]]) -> list[str]:
    rows: list[str] = []
    for row in canvas:
        chars = []
        for value in row:
            if value == CANVAS_EMPTY:
                chars.append(".")
            else:
                chars.append(TILE_TO_CHAR.get(value, "#"))
        rows.append("".join(chars))
    return rows


def _char_map_to_full_map(char_map: list[str]) -> list[list[int]]:
    full_map: list[list[int]] = []
    for row in char_map:
        converted: list[int] = []
        for char in row:
            if char == "#":
                converted.append(SOLID_TILE)
            elif char == "=":
                converted.append(SEMISOLID_TILE)
            elif char == "S":
                converted.append(START_TILE)
            elif char in {"E", "X"}:
                converted.append(EXIT_TILE)
            else:
                converted.append(EMPTY_TILE)
        full_map.append(converted)
    return full_map


def _find_ground_spawn(char_map: list[str], rect: pygame.Rect) -> tuple[float, float]:
    probe_x = max(rect.left, min(rect.centerx, rect.right - 1))
    for y in range(rect.top, min(len(char_map), rect.bottom + 40)):
        if char_map[y][probe_x] in {"#", "="}:
            return float(probe_x * TILE_SIZE), float((y - 1) * TILE_SIZE - 52)
    return float(probe_x * TILE_SIZE), float(rect.top * TILE_SIZE)


def _raise_overlap_issues(overlap_issues: list[OverlapIssue]) -> None:
    if not overlap_issues:
        return
    previews = [
        f"({issue.x},{issue.y}) {issue.existing_source} -> {issue.new_source}"
        for issue in overlap_issues[:8]
    ]
    raise AssemblyError("component overlap detected: " + "; ".join(previews))


def _horizontal_endpoint_footprint(component: ComponentDef, point: tuple[int, int]) -> set[tuple[int, int]]:
    local_y = component.socket("left")[1] if component.sockets["left"] is not None else component.socket("right")[1]
    top = point[1] - local_y
    return {(point[0], top + row_index) for row_index in range(component.height)}


def _vertical_endpoint_footprint(component: ComponentDef, point: tuple[int, int]) -> set[tuple[int, int]]:
    local_x = component.socket("top")[0] if component.sockets["top"] is not None else component.socket("bottom")[0]
    left = point[0] - local_x
    return {(left + col_index, point[1]) for col_index in range(component.width)}


def _component_footprint(component: ComponentDef, left: int, top: int) -> set[tuple[int, int]]:
    return {
        (left + col_index, top + row_index)
        for row_index in range(component.height)
        for col_index in range(component.width)
    }


def _aligned_component_footprint(component: ComponentDef, point: tuple[int, int], sides: tuple[str, ...]) -> set[tuple[int, int]]:
    points: set[tuple[int, int]] = set()
    for side in sides:
        socket = component.sockets.get(side)
        if socket is None:
            continue
        left = point[0] - socket[0]
        top = point[1] - socket[1]
        points.update(_component_footprint(component, left, top))
    return points


def _is_route_primitive(source: str) -> bool:
    return source.startswith("segment:") or source.startswith("connector:")


def _is_multi_l_connector_source(source: str) -> bool:
    return source.startswith("connector:特殊连接通道/多L")


def _should_preserve_connector_walkable_overlap(
    point: tuple[int, int],
    existing_value: int,
    new_value: int,
    existing_owner: str | None,
    source: str,
    allowed_overlap_points: set[tuple[int, int]],
) -> bool:
    return (
        point in allowed_overlap_points
        and source.startswith("connector:")
        and existing_owner is not None
        and existing_value in {OPEN_VALUE, HALF_VALUE}
        and new_value == WALL_VALUE
    )


def _should_preserve_connector_half_tile(
    point: tuple[int, int],
    existing_value: int,
    new_value: int,
    existing_owner: str | None,
    source: str,
    allowed_overlap_points: set[tuple[int, int]],
) -> bool:
    return (
        point in allowed_overlap_points
        and source.startswith("connector:")
        and not _is_multi_l_connector_source(source)
        and existing_owner is not None
        and existing_owner.startswith("segment:")
        and existing_value == HALF_VALUE
        and new_value == OPEN_VALUE
    )


def _resolve_segment_endpoint(
    orientation: str,
    point: tuple[int, int],
    other_point: tuple[int, int],
    connector_map: dict[tuple[int, int], ConnectorPlacement],
) -> tuple[int, int]:
    connector = connector_map.get(point)
    if connector is None:
        return point

    if orientation == "horizontal":
        side = "right" if other_point[0] > point[0] else "left"
    else:
        side = "bottom" if other_point[1] > point[1] else "top"
    return connector.global_socket(side) or point


def render_debug_surface(assembled: EmbeddedAssemblyResult, tile_scale: int = 4) -> pygame.Surface:
    scale = max(1, tile_scale)
    width = len(assembled.char_map[0]) * scale
    height = len(assembled.char_map) * scale
    surface = pygame.Surface((width, height))
    colors = {
        ".": (24, 28, 36),
        "#": (92, 104, 120),
        "=": (143, 172, 188),
        "S": (108, 206, 130),
        "E": (224, 116, 92),
    }
    for y, row in enumerate(assembled.char_map):
        for x, char in enumerate(row):
            pygame.draw.rect(surface, colors.get(char, (120, 80, 80)), pygame.Rect(x * scale, y * scale, scale, scale))

    room_colors = [
        (255, 210, 96),
        (108, 196, 255),
        (255, 142, 120),
        (126, 225, 160),
        (212, 166, 255),
    ]
    for index, placement in enumerate(sorted(assembled.room_placements.values(), key=lambda item: item.node.node_id)):
        tint = room_colors[index % len(room_colors)]
        rect = pygame.Rect(placement.left * scale, placement.top * scale, placement.component.width * scale, placement.component.height * scale)
        pygame.draw.rect(surface, tint, rect, width=max(1, scale))
        for socket in placement.sockets.values():
            if socket is None:
                continue
            center = (socket[0] * scale + scale // 2, socket[1] * scale + scale // 2)
            pygame.draw.circle(surface, (255, 255, 255), center, max(2, scale))
    return surface


def assemble_embedded_world(graph_map: GraphMapData, seed: int) -> EmbeddedAssemblyResult:
    generation_rules = graph_map.generation_rules or _load_generation_rules(graph_map.map_folder)
    library = _load_component_library(graph_map.map_folder)
    rng = random.Random(seed)
    placements = _compute_room_placements(graph_map, library, generation_rules)
    _validate_room_overlaps(placements)
    edges = _make_edges(graph_map)
    segments, incidents, room_anchor_points, route_debug, multi_l_top_offsets = _build_routes(edges, placements, library)
    segments, incidents, multi_l_overrides = _compress_multi_l_incidents(library, segments, incidents, room_anchor_points)
    canvas_width, canvas_height = _canvas_bounds(placements, segments, library)
    canvas = [[CANVAS_EMPTY for _ in range(canvas_width)] for _ in range(canvas_height)]
    owners: list[list[str | None]] = [[None for _ in range(canvas_width)] for _ in range(canvas_height)]
    overlap_issues: list[OverlapIssue] = []
    debug_lines: list[str] = []
    connector_placements: list[ConnectorPlacement] = []
    for point, sides in sorted(incidents.items()):
        if point in room_anchor_points or sides in {frozenset({"left", "right"}), frozenset({"up", "down"})}:
            continue
        component = multi_l_overrides.get(point) or _choose_connector_for_incident(
            library,
            point,
            frozenset(sides),
            segments,
            multi_l_top_offsets.get(point),
        )
        left, top = _connector_top_left(component, point)
        connector_placements.append(ConnectorPlacement(component=component, left=left, top=top, point=point, sides=frozenset(sides)))

    connector_map = {placement.point: placement for placement in connector_placements}

    allowed_overlap_points = set(room_anchor_points) | set(incidents)
    straight = library["普通通道/直道_00"]
    shaft = library["普通通道/竖井_00"]
    shaft_components = _shaft_variant_components(library)
    vertical_segment_components: dict[int, ComponentDef] = {}
    for segment_index, segment in enumerate(segments):
        if segment.orientation == "vertical":
            vertical_segment_components[segment_index] = _choose_shaft_component(shaft_components, rng)
    for segment_index, segment in enumerate(segments):
        if segment.orientation == "horizontal":
            allowed_overlap_points.update(_horizontal_endpoint_footprint(straight, segment.start))
            allowed_overlap_points.update(_horizontal_endpoint_footprint(straight, segment.end))
            allowed_overlap_points.update(_aligned_component_footprint(straight, segment.start, ("left", "right")))
            allowed_overlap_points.update(_aligned_component_footprint(straight, segment.end, ("left", "right")))
        else:
            segment_shaft = vertical_segment_components.get(segment_index, shaft)
            allowed_overlap_points.update(_vertical_endpoint_footprint(segment_shaft, segment.start))
            allowed_overlap_points.update(_vertical_endpoint_footprint(segment_shaft, segment.end))
            allowed_overlap_points.update(_aligned_component_footprint(segment_shaft, segment.start, ("top", "bottom")))
            allowed_overlap_points.update(_aligned_component_footprint(segment_shaft, segment.end, ("top", "bottom")))
    for placement in connector_placements:
        allowed_overlap_points.update(_component_footprint(placement.component, placement.left, placement.top))

    for node in graph_map.nodes:
        placement = placements[node.node_id]
        _stamp_tile_grid(
            canvas,
            owners,
            placement.component.tile_grid,
            placement.left,
            placement.top,
            source=f"room:{node.node_id}",
            allowed_overlap_points=allowed_overlap_points,
            overlap_issues=overlap_issues,
        )
        debug_lines.append(f"room {node.node_id} left={placement.left} top={placement.top} sockets={placement.sockets}")

    for segment_index, segment in enumerate(segments):
        start_point = _resolve_segment_endpoint(segment.orientation, segment.start, segment.end, connector_map)
        end_point = _resolve_segment_endpoint(segment.orientation, segment.end, segment.start, connector_map)
        if segment.orientation == "horizontal":
            _stamp_horizontal(
                canvas,
                owners,
                straight,
                start_point,
                end_point,
                source=f"segment:{segment_index}",
                allowed_overlap_points=allowed_overlap_points,
                overlap_issues=overlap_issues,
            )
        else:
            segment_shaft = vertical_segment_components.get(segment_index, shaft)
            _stamp_vertical(
                canvas,
                owners,
                segment_shaft,
                start_point,
                end_point,
                source=f"segment:{segment_index}",
                allowed_overlap_points=allowed_overlap_points,
                overlap_issues=overlap_issues,
            )

    for placement in connector_placements:
        _stamp_tile_grid(
            canvas,
            owners,
            placement.component.tile_grid,
            placement.left,
            placement.top,
            source=f"connector:{placement.component.name}:{placement.point[0]}:{placement.point[1]}",
            allowed_overlap_points=allowed_overlap_points,
            overlap_issues=overlap_issues,
        )
        debug_lines.append(
            f"connector {placement.component.name} at {placement.point} sides={sorted(placement.sides)} left={placement.left} top={placement.top} sockets={{'left': {placement.global_socket('left')}, 'right': {placement.global_socket('right')}, 'top': {placement.global_socket('top')}, 'bottom': {placement.global_socket('bottom')}}}"
        )

    _raise_overlap_issues(overlap_issues)

    char_map = _canvas_to_char_map(canvas)
    full_map = _char_map_to_full_map(char_map)
    start_rect_tiles = placements[graph_map.start_id].rect
    exit_rect_tiles = placements[graph_map.exit_id].rect
    start_world = _find_ground_spawn(char_map, start_rect_tiles)
    exit_rect = pygame.Rect(
        exit_rect_tiles.centerx * TILE_SIZE - TILE_SIZE,
        exit_rect_tiles.centery * TILE_SIZE - TILE_SIZE * 2,
        TILE_SIZE * 2,
        TILE_SIZE * 2,
    )
    debug_lines.extend(route_debug)
    debug_lines.append(f"full_map size={len(full_map[0])}x{len(full_map)}")
    return EmbeddedAssemblyResult(
        full_map=full_map,
        char_map=char_map,
        room_placements=placements,
        connector_placements=connector_placements,
        start_world=start_world,
        exit_rect=exit_rect,
        debug_lines=debug_lines,
    )