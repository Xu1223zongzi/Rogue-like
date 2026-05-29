from __future__ import annotations

from dataclasses import dataclass
import random

import pygame

from game.config import PLATFORM_COLOR, SOLID_COLOR, SOLID_EDGE, TILE_SIZE, WINDOW_HEIGHT, WINDOW_WIDTH
from game.world.assembled_world import AssemblyError, ConnectorPlacement, assemble_embedded_world
from game.world.graph_map import GraphMapData, GraphRoomNode, generate_room_graph, load_room_grid


Vec2 = pygame.Vector2
DEFAULT_MAP_FOLDER = "第二张地图"
MAP_REVEAL_SNAP = 48
MAP_REVEAL_RADIUS = min(WINDOW_WIDTH, WINDOW_HEIGHT) * 0.9
COLLISION_CHUNK_SIZE = TILE_SIZE * 8
LEVEL_BUILD_RETRY_LIMIT = 8

FIXTURE_MARKERS = {
    "h": {"slot": "heart", "item_id": "knight_heart", "context": "altar"},
    "s": {"slot": "brain", "item_id": "knight_brain_sword", "context": "library"},
    "n": {"slot": "brain", "item_id": "knight_brain_scripture", "context": "library"},
    "l": {"slot": "left_eye", "item_id": "knight_left_eye_halo", "context": "corridor_eye"},
    "m": {"slot": "left_eye", "item_id": "knight_left_eye_blade", "context": "corridor_eye"},
    "r": {"slot": "right_eye", "item_id": "knight_right_eye_rain", "context": "corridor_eye"},
    "k": {"slot": "right_eye", "item_id": "knight_right_eye_spirit", "context": "corridor_eye"},
}

FIXTURE_BASE_CHANCES = {
    "heart": 0.08,
    "brain": 1.0,
    "left_eye": 1.0,
    "right_eye": 1.0,
}

CORRIDOR_ENEMY_SPAWN_WIDTH = 28
CORRIDOR_ENEMY_SPAWN_HEIGHT = 42
CORRIDOR_INTERIOR_CEILING_SCAN_TILES = 7


@dataclass
class Room:
    index: int
    name: str
    role: str
    room_size: str
    tiles: list[str]
    solids: list[pygame.Rect]
    semisolids: list[pygame.Rect]
    player_spawn: Vec2
    enemy_spawns: list[tuple[Vec2, str]]
    item_spawns: list[tuple[Vec2, str, str | None, str | None]]
    exit_rect: pygame.Rect
    retreat_rect: pygame.Rect | None
    world_width: int
    world_height: int

    def draw(
        self,
        surface: pygame.Surface,
        camera: Vec2,
        background_blend_from: str | None = None,
        background_blend: float = 1.0,
    ) -> None:
        self.draw_background_layers(surface, camera, blend_from_role=background_blend_from, blend_ratio=background_blend)

        for solid in self.solids:
            shifted = solid.move(-int(camera.x), -int(camera.y))
            pygame.draw.rect(surface, SOLID_COLOR, shifted)
            pygame.draw.rect(surface, SOLID_EDGE, shifted, width=2)

        for platform in self.semisolids:
            shifted = platform.move(-int(camera.x), -int(camera.y))
            body = pygame.Rect(shifted.x, shifted.y + TILE_SIZE // 2, shifted.width, max(8, TILE_SIZE // 3))
            pygame.draw.rect(surface, PLATFORM_COLOR, body, border_radius=5)
            pygame.draw.line(surface, SOLID_EDGE, (body.left, body.top), (body.right, body.top), width=2)

    @staticmethod
    def _background_palette_for_role(role: str) -> tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]:
        layer_color_far = (24, 29, 37)
        layer_color_mid = (33, 39, 48)
        sky_color = (15, 18, 25)
        ground_color = (10, 12, 16)
        if role == "combat":
            sky_color = (14, 19, 24)
            layer_color_far = (26, 43, 46)
            layer_color_mid = (40, 62, 66)
            ground_color = (11, 15, 19)
        elif role in {"boss", "start"}:
            sky_color = (26, 12, 24)
            layer_color_far = (58, 24, 48)
            layer_color_mid = (88, 34, 70)
            ground_color = (18, 10, 18)
        elif role == "elite":
            sky_color = (22, 16, 18)
            layer_color_far = (62, 30, 26)
            layer_color_mid = (100, 46, 34)
            ground_color = (20, 12, 12)
        elif role == "rest":
            sky_color = (16, 24, 24)
            layer_color_far = (28, 52, 50)
            layer_color_mid = (42, 78, 74)
            ground_color = (12, 18, 18)
        elif role == "portal":
            sky_color = (14, 20, 28)
            layer_color_far = (24, 42, 60)
            layer_color_mid = (38, 66, 92)
            ground_color = (10, 16, 22)
        return layer_color_far, layer_color_mid, sky_color, ground_color

    @staticmethod
    def _lerp_color(start: tuple[int, int, int], end: tuple[int, int, int], t: float) -> tuple[int, int, int]:
        blend = max(0.0, min(1.0, t))
        return (
            int(round(start[0] + (end[0] - start[0]) * blend)),
            int(round(start[1] + (end[1] - start[1]) * blend)),
            int(round(start[2] + (end[2] - start[2]) * blend)),
        )

    def draw_background_layers(
        self,
        surface: pygame.Surface,
        camera: Vec2,
        role_override: str | None = None,
        blend_from_role: str | None = None,
        blend_ratio: float = 1.0,
    ) -> None:
        role = role_override if role_override is not None else self.role
        layer_color_far, layer_color_mid, sky_color, ground_color = self._background_palette_for_role(role)
        if blend_from_role is not None and blend_ratio < 0.999:
            prev_far, prev_mid, prev_sky, prev_ground = self._background_palette_for_role(blend_from_role)
            layer_color_far = self._lerp_color(prev_far, layer_color_far, blend_ratio)
            layer_color_mid = self._lerp_color(prev_mid, layer_color_mid, blend_ratio)
            sky_color = self._lerp_color(prev_sky, sky_color, blend_ratio)
            ground_color = self._lerp_color(prev_ground, ground_color, blend_ratio)

        surface.fill(ground_color)
        horizon = int(surface.get_height() * 0.34)
        pygame.draw.rect(surface, sky_color, (0, 0, surface.get_width(), horizon))
        pygame.draw.rect(surface, ground_color, (0, horizon, surface.get_width(), surface.get_height() - horizon))

        offset_far = int(camera.x * 0.18)
        offset_mid = int(camera.x * 0.36)
        for index in range(-1, 7):
            x_far = index * 260 - offset_far % 260
            x_mid = index * 190 - offset_mid % 190
            pygame.draw.polygon(surface, layer_color_far, [(x_far, surface.get_height()), (x_far + 90, 280), (x_far + 180, surface.get_height())])
            pygame.draw.polygon(surface, layer_color_mid, [(x_mid, surface.get_height()), (x_mid + 70, 360), (x_mid + 140, surface.get_height())])

    def clamp_camera(self, camera: Vec2) -> Vec2:
        max_x = max(0, self.world_width - WINDOW_WIDTH)
        max_y = max(0, self.world_height - WINDOW_HEIGHT)
        return Vec2(max(0, min(camera.x, max_x)), max(0, min(camera.y, max_y)))


class LevelState:
    def __init__(self, seed: int | None = None, floor_number: int = 1) -> None:
        self.seed = random.randrange(1, 999_999_999) if seed is None else seed
        self.generation_seed = self.seed
        self.floor_number = max(1, floor_number)
        self.loop_count = 0
        self.graph_map: GraphMapData | None = None
        self.graph_nodes: list[GraphRoomNode] = []
        self.grid_width = 0
        self.grid_height = 0
        self.start_cell = (0, 0)
        self.boss_cell = (0, 0)
        self.main_path: list[tuple[int, int]] = []
        self.branch_cells: set[tuple[int, int]] = set()
        self.room_cells: list[tuple[int, int]] = []
        self.is_embedded_world_map = False
        self.room_regions: dict[int, pygame.Rect] = {}
        self.connector_placements: list[ConnectorPlacement] = []
        self.corridor_enemy_spawns: list[tuple[Vec2, str]] = []
        self.floor_solid_spatial_index: dict[tuple[int, int], list[pygame.Rect]] = {}
        self.floor_semisolid_spatial_index: dict[tuple[int, int], list[pygame.Rect]] = {}
        self.corridor_conflicts: list[str] = []
        self.floor_room: Room | None = None
        self.rooms = self._build_rooms()
        self.current_room_index = self.graph_map.start_id if self.graph_map is not None else 0
        self.navigation_history = [self.current_room_index]
        self.explored_room_ids: set[int] = {self.current_room_index}
        self.revealed_map_points: set[tuple[int, int]] = set()

    def _build_rooms(self) -> list[Room]:
        graph_map: GraphMapData | None = None
        assembly = None
        build_seed = self.seed
        last_error: Exception | None = None
        for attempt in range(LEVEL_BUILD_RETRY_LIMIT):
            build_seed = self.seed + attempt
            try:
                graph_map = generate_room_graph(build_seed, self.floor_number, map_folder=DEFAULT_MAP_FOLDER)
                assembly = assemble_embedded_world(graph_map, build_seed)
                break
            except (AssemblyError, ValueError) as error:
                last_error = error
        if graph_map is None or assembly is None:
            raise RuntimeError(f"Failed to build level after {LEVEL_BUILD_RETRY_LIMIT} attempts") from last_error

        self.seed = build_seed
        self.generation_seed = build_seed
        generated_rooms: list[Room] = []
        for node in graph_map.nodes:
            room_grid = load_room_grid(graph_map, node.node_id)
            generated_rooms.append(
                build_room(
                    node.node_id,
                    node.room_name or f"Room {node.node_id}",
                    room_grid,
                    node.room_type,
                    node.room_size,
                    self.loop_count,
                    build_seed,
                )
            )

        self.graph_map = graph_map
        self.graph_nodes = graph_map.nodes[:]
        self.grid_width = graph_map.grid_width
        self.grid_height = graph_map.grid_height
        self.start_cell = graph_map.start_cell
        self.boss_cell = graph_map.exit_cell
        self.main_path = graph_map.main_path_cells
        self.branch_cells = graph_map.branch_cells
        self.room_cells = graph_map.room_cells

        self.connector_placements = assembly.connector_placements[:]
        world_width = len(assembly.char_map[0]) * TILE_SIZE
        world_height = len(assembly.char_map) * TILE_SIZE
        embedded_rooms: list[Room] = []
        self.room_regions = {}
        for room in generated_rooms:
            placement = assembly.room_placements[room.index]
            offset_x = placement.left * TILE_SIZE
            offset_y = placement.top * TILE_SIZE
            embedded_rooms.append(offset_room(room, offset_x, offset_y, world_width, world_height))
            self.room_regions[room.index] = pygame.Rect(
                placement.left * TILE_SIZE,
                placement.top * TILE_SIZE,
                placement.component.width * TILE_SIZE,
                placement.component.height * TILE_SIZE,
            )

        self.corridor_conflicts = assembly.debug_lines[:]
        self.floor_room = build_room(-1, "Embedded Floor", assembly.char_map, "start", "large", self.loop_count, build_seed)
        self.floor_room.player_spawn = Vec2(assembly.start_world)
        self.floor_room.exit_rect = assembly.exit_rect.copy()
        self.floor_room.retreat_rect = None
        self.floor_room.world_width = world_width
        self.floor_room.world_height = world_height
        self.floor_solid_spatial_index = build_collision_spatial_index(self.floor_room.solids)
        self.floor_semisolid_spatial_index = build_collision_spatial_index(self.floor_room.semisolids)
        self.corridor_enemy_spawns = generate_corridor_enemy_spawns(assembly.char_map, self.graph_nodes, self.room_regions, build_seed)
        self.is_embedded_world_map = True
        return embedded_rooms

    def nearby_solids(self, rect: pygame.Rect | pygame.FRect) -> list[pygame.Rect]:
        room = self.current_room
        if not self.is_embedded_world_map or self.floor_room is None or room is not self.floor_room:
            return room.solids
        return query_collision_spatial_index(self.floor_solid_spatial_index, rect)

    def nearby_semisolids(self, rect: pygame.Rect | pygame.FRect) -> list[pygame.Rect]:
        room = self.current_room
        if not self.is_embedded_world_map or self.floor_room is None or room is not self.floor_room:
            return room.semisolids
        return query_collision_spatial_index(self.floor_semisolid_spatial_index, rect)

    @property
    def current_room(self) -> Room:
        if self.is_embedded_world_map and self.floor_room is not None:
            active_room = self.rooms[self.current_room_index]
            self.floor_room.name = active_room.name
            self.floor_room.role = active_room.role
            self.floor_room.index = self.current_room_index
            self.floor_room.player_spawn = active_room.player_spawn.copy()
            self.floor_room.item_spawns = active_room.item_spawns[:]
            self.floor_room.exit_rect = active_room.exit_rect.copy()
            self.floor_room.retreat_rect = None if active_room.retreat_rect is None else active_room.retreat_rect.copy()
            return self.floor_room
        return self.rooms[self.current_room_index]

    def can_advance(self) -> bool:
        return bool(self.current_children())

    def can_retreat(self) -> bool:
        return self.current_parent() is not None

    def advance(self) -> Room:
        child_ids = self.current_children()
        if not child_ids:
            return self.current_room
        return self.travel_to(child_ids[0])

    def retreat(self) -> Room:
        parent_id = self.current_parent()
        if parent_id is None:
            return self.current_room
        return self.travel_to(parent_id)

    def current_children(self) -> list[int]:
        if not self.graph_nodes:
            return []
        return self.graph_nodes[self.current_room_index].child_ids[:]

    def current_parent(self) -> int | None:
        if not self.graph_nodes:
            return None
        return self.graph_nodes[self.current_room_index].parent_id

    def travel_to(self, room_index: int) -> Room:
        if room_index < 0 or room_index >= len(self.rooms):
            return self.current_room
        self.current_room_index = room_index
        self.navigation_history.append(room_index)
        self.explored_room_ids.add(room_index)
        return self.current_room

    def record_map_reveal(self, world_point: tuple[float, float] | None) -> None:
        if world_point is None:
            return
        snap_x = int(world_point[0] // MAP_REVEAL_SNAP)
        snap_y = int(world_point[1] // MAP_REVEAL_SNAP)
        self.revealed_map_points.add((snap_x, snap_y))

    def route_map_payload(self, player_position: Vec2 | None = None) -> dict[str, object]:
        room = self.floor_room if self.floor_room is not None else self.current_room
        player_world_position = (float(player_position.x), float(player_position.y)) if player_position is not None else None
        self.record_map_reveal(player_world_position)
        reveal_points = [
            (point_x * MAP_REVEAL_SNAP, point_y * MAP_REVEAL_SNAP)
            for point_x, point_y in sorted(self.revealed_map_points)
        ]
        if player_world_position is not None and not reveal_points:
            reveal_points.append(player_world_position)

        return {
            "seed": self.seed,
            "world_width": room.world_width,
            "world_height": room.world_height,
            "solids": room.solids,
            "semisolids": room.semisolids,
            "player_world_position": player_world_position,
            "fog_reveal_points": reveal_points,
            "fog_reveal_radius": MAP_REVEAL_RADIUS,
        }

    def update_active_room_from_position(self, position: Vec2) -> None:
        if not self.is_embedded_world_map or not self.room_regions:
            return
        position_tuple = (position.x, position.y)
        containing_room_id = next((room_id for room_id, region in self.room_regions.items() if region.collidepoint(position_tuple)), None)
        if containing_room_id is None:
            return
        self.current_room_index = containing_room_id
        self.explored_room_ids.add(containing_room_id)

    def move_actor(self, actor, delta_time: float) -> None:
        room = self.current_room
        actor.on_ground = False

        actor.rect.x += actor.velocity.x * delta_time
        for solid in self.nearby_solids(actor.rect):
            if actor.rect.colliderect(solid):
                if actor.velocity.x > 0.0:
                    actor.rect.right = solid.left
                elif actor.velocity.x < 0.0:
                    actor.rect.left = solid.right
                actor.velocity.x = 0.0

        previous_bottom = actor.rect.bottom
        actor.rect.y += actor.velocity.y * delta_time
        for solid in self.nearby_solids(actor.rect):
            if actor.rect.colliderect(solid):
                if actor.velocity.y > 0.0:
                    actor.rect.bottom = solid.top
                    actor.on_ground = True
                elif actor.velocity.y < 0.0:
                    actor.rect.top = solid.bottom
                actor.velocity.y = 0.0

        if actor.velocity.y >= 0.0 and getattr(actor, "drop_through_timer", 0.0) <= 0.0:
            platform_query = pygame.Rect(int(actor.rect.left - TILE_SIZE), int(actor.rect.top - TILE_SIZE), int(actor.rect.width + TILE_SIZE * 2), int(actor.rect.height + TILE_SIZE * 2))
            for platform in self.nearby_semisolids(platform_query):
                horizontal_overlap = actor.rect.right > platform.left + 6 and actor.rect.left < platform.right - 6
                crossed_platform = previous_bottom <= platform.top + 8 and actor.rect.bottom >= platform.top
                if horizontal_overlap and crossed_platform and actor.rect.top < platform.top:
                    actor.rect.bottom = platform.top
                    actor.velocity.y = 0.0
                    actor.on_ground = True
                    break

        actor.rect.left = max(0.0, actor.rect.left)
        actor.rect.right = min(room.world_width, actor.rect.right)
        if actor.rect.bottom > room.world_height:
            actor.rect.bottom = room.world_height
            actor.velocity.y = 0.0
            actor.on_ground = True

    def point_in_solid(self, point: Vec2) -> bool:
        probe_rect = pygame.Rect(int(point.x), int(point.y), 1, 1)
        for solid in self.nearby_solids(probe_rect):
            if solid.collidepoint(point.x, point.y):
                return True
        return False

    def has_line_of_sight(self, start: Vec2, end: Vec2) -> bool:
        delta = end - start
        distance = delta.length()
        if distance <= 1.0:
            return True

        steps = max(4, int(distance // (TILE_SIZE * 0.35)))
        for step in range(1, steps):
            point = start.lerp(end, step / steps)
            if self.point_in_solid(point):
                return False
        return True


def build_room(index: int, name: str, grid: list[str], role: str, room_size: str, loop_count: int, generation_seed: int = 0) -> Room:
    solids: list[pygame.Rect] = []
    semisolids: list[pygame.Rect] = []
    player_spawn = Vec2(80, 80)
    pending_player_spawn: tuple[int, int] | None = None
    enemy_spawns: list[tuple[Vec2, str]] = []
    item_spawns: list[tuple[Vec2, str, str | None, str | None]] = []
    pending_items: list[tuple[int, int, str, str, str]] = []
    exit_tiles: list[pygame.Rect] = []
    retreat_tiles: list[pygame.Rect] = []
    pending_enemies: list[tuple[int, int, str]] = []
    width = len(grid[0]) * TILE_SIZE
    height = len(grid) * TILE_SIZE

    for tile_y, row in enumerate(grid):
        for tile_x, cell in enumerate(row):
            tile_rect = pygame.Rect(tile_x * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if cell == "#":
                solids.append(tile_rect)
            elif cell == "=":
                semisolids.append(tile_rect)
            elif cell == "P":
                pending_player_spawn = (tile_x, tile_y)
            elif cell in {"M", "B", "L", "A", "G"}:
                enemy_type = {
                    "M": "blade",
                    "B": "blade",
                    "L": "lancer",
                    "A": "archer",
                    "G": "boss",
                }[cell]
                pending_enemies.append((tile_x, tile_y, enemy_type))
            elif cell in FIXTURE_MARKERS:
                marker = FIXTURE_MARKERS[cell]
                pending_items.append((tile_x, tile_y, marker["slot"], marker["item_id"], marker["context"]))
            elif cell == "X":
                exit_tiles.append(tile_rect.copy())
            elif cell == "Y":
                retreat_tiles.append(tile_rect.copy())

    if pending_player_spawn is not None:
        spawn_x, spawn_y = pending_player_spawn
        player_spawn = Vec2(spawn_x * TILE_SIZE + 8, find_fixture_ground_y(grid, spawn_x, spawn_y, height) - 52)
    else:
        player_spawn = find_player_spawn_position(grid, height)

    for tile_x, tile_y, enemy_type in pending_enemies:
        enemy_spawns.append((find_enemy_spawn_position(grid, tile_x, tile_y, height), enemy_type))
    if not enemy_spawns:
        enemy_spawns = generate_fallback_enemy_spawns(grid, height, player_spawn, role, room_size, index)

    rolled_fixtures: list[tuple[Vec2, str, str | None]] = []
    for tile_x, tile_y, slot, item_id, context in pending_items:
        rolled_item = roll_fixture_item(slot, item_id, role, loop_count, context)
        position = Vec2(tile_x * TILE_SIZE + TILE_SIZE * 0.5, find_fixture_ground_y(grid, tile_x, tile_y, height))
        rolled_fixtures.append((position, slot, rolled_item))

    heart_fixtures = [(position, slot, rolled_item) for position, slot, rolled_item in rolled_fixtures if slot == "heart"]
    organ_fixtures = [(position, slot, rolled_item) for position, slot, rolled_item in rolled_fixtures if slot != "heart" and rolled_item is not None]
    center_tile_x = max(1, min(len(grid[0]) - 2, len(grid[0]) // 2))
    center_tile_y = max(1, min(len(grid) - 3, len(grid) // 2))
    centered_fixture_position = Vec2(center_tile_x * TILE_SIZE + TILE_SIZE * 0.5, find_fixture_ground_y(grid, center_tile_x, center_tile_y, height))

    for _, slot, rolled_item in heart_fixtures:
        item_spawns.append((centered_fixture_position.copy(), slot, rolled_item, None))

    if organ_fixtures:
        fixture_rng = random.Random(f"fixture-organ:{generation_seed}:{index}:{name}:{role}:{room_size}:{loop_count}")
        _, slot, rolled_item = fixture_rng.choice(organ_fixtures)
        item_spawns.append((centered_fixture_position.copy(), slot, None, rolled_item))

    if not item_spawns:
        item_spawns.extend(generate_fallback_item_spawns(centered_fixture_position, role, room_size, index, generation_seed))

    if exit_tiles:
        exit_rect = exit_tiles[0].copy()
        for tile_rect in exit_tiles[1:]:
            exit_rect = exit_rect.union(tile_rect)
    else:
        exit_rect = pygame.Rect(width - TILE_SIZE, height - TILE_SIZE * 2, TILE_SIZE, TILE_SIZE)

    retreat_rect: pygame.Rect | None = None
    if retreat_tiles:
        retreat_rect = retreat_tiles[0].copy()
        for tile_rect in retreat_tiles[1:]:
            retreat_rect = retreat_rect.union(tile_rect)
    else:
        retreat_rect = pygame.Rect(0, height - TILE_SIZE * 2, TILE_SIZE, TILE_SIZE)

    return Room(
        index=index,
        name=name,
        role=role,
        room_size=room_size,
        tiles=grid,
        solids=solids,
        semisolids=semisolids,
        player_spawn=player_spawn,
        enemy_spawns=enemy_spawns,
        item_spawns=item_spawns,
        exit_rect=exit_rect,
        retreat_rect=retreat_rect,
        world_width=width,
        world_height=height,
    )


def offset_room(room: Room, offset_x: int, offset_y: int, world_width: int, world_height: int) -> Room:
    return Room(
        index=room.index,
        name=room.name,
        role=room.role,
        room_size=room.room_size,
        tiles=room.tiles[:],
        solids=[solid.move(offset_x, offset_y) for solid in room.solids],
        semisolids=[platform.move(offset_x, offset_y) for platform in room.semisolids],
        player_spawn=Vec2(room.player_spawn.x + offset_x, room.player_spawn.y + offset_y),
        enemy_spawns=[(Vec2(position.x + offset_x, position.y + offset_y), enemy_type) for position, enemy_type in room.enemy_spawns],
        item_spawns=[
            (Vec2(position.x + offset_x, position.y + offset_y), slot, item_id, hidden_item_id)
            for position, slot, item_id, hidden_item_id in room.item_spawns
        ],
        exit_rect=room.exit_rect.move(offset_x, offset_y),
        retreat_rect=None if room.retreat_rect is None else room.retreat_rect.move(offset_x, offset_y),
        world_width=world_width,
        world_height=world_height,
    )


def find_fixture_ground_y(grid: list[str], tile_x: int, tile_y: int, room_height: int) -> float:
    for probe_y in range(tile_y + 1, len(grid)):
        if grid[probe_y][tile_x] in {"#", "="}:
            return probe_y * TILE_SIZE
    return float(room_height - TILE_SIZE)


def find_enemy_spawn_position(grid: list[str], tile_x: int, tile_y: int, room_height: int) -> Vec2:
    if corridor_tile_is_interior(grid, tile_x, tile_y):
        return Vec2(tile_x * TILE_SIZE + 10, (tile_y + 1) * TILE_SIZE - 42)
    ground_y = find_fixture_ground_y(grid, tile_x, tile_y, room_height)
    return Vec2(tile_x * TILE_SIZE + 10, ground_y - 42)


def find_player_spawn_position(grid: list[str], room_height: int) -> Vec2:
    if not grid or not grid[0]:
        return Vec2(80, 80)

    preferred_x = max(2, min(len(grid[0]) - 3, len(grid[0]) // 5))
    preferred_y = max(2, min(len(grid) - 2, int(len(grid) * 0.68)))
    candidate_tiles: list[tuple[int, int]] = []

    for tile_y in range(2, len(grid) - 1):
        row = grid[tile_y]
        below_row = grid[tile_y + 1]
        for tile_x in range(1, len(row) - 1):
            if row[tile_x] != "." or below_row[tile_x] not in {"#", "="}:
                continue
            if any(grid[tile_y - offset][tile_x] != "." for offset in range(0, 3)):
                continue
            candidate_tiles.append((tile_x, tile_y))

    if not candidate_tiles:
        return Vec2(80, 80)

    chosen_x, chosen_y = min(
        candidate_tiles,
        key=lambda tile: (abs(tile[0] - preferred_x), abs(tile[1] - preferred_y), tile[0]),
    )
    ground_y = find_fixture_ground_y(grid, chosen_x, chosen_y, room_height)
    return Vec2(chosen_x * TILE_SIZE + 8, ground_y - 52)


def max_walkable_straight_run(grid: list[str]) -> int:
    longest_run = 0
    for tile_y in range(0, len(grid) - 1):
        row = grid[tile_y]
        below_row = grid[tile_y + 1]
        current_run = 0
        for tile_x in range(1, max(1, len(row) - 1)):
            if row[tile_x] == "." and below_row[tile_x] in {"#", "="}:
                current_run += 1
                longest_run = max(longest_run, current_run)
            else:
                current_run = 0
    return longest_run


def room_region_tile_bounds(room_regions: dict[int, pygame.Rect]) -> list[tuple[int, int, int, int]]:
    bounds: list[tuple[int, int, int, int]] = []
    for region in room_regions.values():
        left = max(0, int(region.left // TILE_SIZE))
        top = max(0, int(region.top // TILE_SIZE))
        right = max(left, int((region.right - 1) // TILE_SIZE))
        bottom = max(top, int((region.bottom - 1) // TILE_SIZE))
        bounds.append((left, top, right, bottom))
    return bounds


def tile_in_room_region(tile_x: int, tile_y: int, room_bounds: list[tuple[int, int, int, int]]) -> bool:
    return any(left <= tile_x <= right and top <= tile_y <= bottom for left, top, right, bottom in room_bounds)


def walkable_corridor_tiles_between(
    grid: list[str],
    room_bounds: list[tuple[int, int, int, int]],
    tile_x_start: int,
    tile_x_end: int,
    preferred_y: int,
) -> list[tuple[int, int]]:
    if not grid or tile_x_start > tile_x_end:
        return []
    max_row_index = max(0, len(grid) - 2)
    row_order = sorted(range(0, max_row_index + 1), key=lambda row_index: abs(row_index - preferred_y))
    for tile_y in row_order:
        row = grid[tile_y]
        below_row = grid[tile_y + 1]
        run: list[tuple[int, int]] = []
        for tile_x in range(max(1, tile_x_start), min(tile_x_end, len(row) - 2) + 1):
            is_walkable = row[tile_x] == "." and below_row[tile_x] in {"#", "="}
            if is_walkable and corridor_tile_is_interior(grid, tile_x, tile_y) and not tile_in_room_region(tile_x, tile_y, room_bounds):
                run.append((tile_x, tile_y))
            elif run:
                break
        if len(run) >= 6:
            return run
    return []


def corridor_tile_has_ceiling(grid: list[str], tile_x: int, tile_y: int) -> bool:
    if tile_y <= 0:
        return False
    left = max(1, tile_x - 1)
    right = min(len(grid[tile_y]) - 2, tile_x + 1)
    top_limit = max(0, tile_y - CORRIDOR_INTERIOR_CEILING_SCAN_TILES)
    for probe_y in range(tile_y - 1, top_limit - 1, -1):
        row = grid[probe_y]
        if any(row[probe_x] == "#" for probe_x in range(left, right + 1)):
            return True
    return False


def corridor_tile_is_interior(grid: list[str], tile_x: int, tile_y: int) -> bool:
    if tile_y < 0 or tile_y >= len(grid) - 1:
        return False
    row = grid[tile_y]
    below_row = grid[tile_y + 1]
    if row[tile_x] != "." or below_row[tile_x] not in {"#", "="}:
        return False
    return corridor_tile_has_ceiling(grid, tile_x, tile_y)


def corridor_tile_can_fit_enemy(grid: list[str], tile_x: int, tile_y: int) -> bool:
    if tile_y < 0 or tile_y >= len(grid) - 1:
        return False
    if not corridor_tile_is_interior(grid, tile_x, tile_y):
        return False
    left = max(1, tile_x - 1)
    right = min(len(grid[tile_y]) - 2, tile_x + 1)
    headroom_tiles = max(1, (CORRIDOR_ENEMY_SPAWN_HEIGHT + TILE_SIZE - 1) // TILE_SIZE)
    top_row = tile_y - headroom_tiles + 1
    if top_row < 0:
        return False
    for probe_y in range(top_row, tile_y + 1):
        row = grid[probe_y]
        for probe_x in range(left, right + 1):
            if row[probe_x] != ".":
                return False
    return True


def generate_corridor_enemy_spawns(
    grid: list[str],
    graph_nodes: list[GraphRoomNode],
    room_regions: dict[int, pygame.Rect],
    seed: int,
) -> list[tuple[Vec2, str]]:
    room_bounds = room_region_tile_bounds(room_regions)
    rng = random.Random(f"corridor-enemy:{seed}:{len(grid[0])}x{len(grid)}")
    enemy_spawns: list[tuple[Vec2, str]] = []
    enemy_types = ["blade", "blade", "lancer", "archer"]

    nodes_by_id = {node.node_id: node for node in graph_nodes}
    for node in graph_nodes:
        source_region = room_regions.get(node.node_id)
        if source_region is None:
            continue
        for child_id in node.child_ids:
            child = nodes_by_id.get(child_id)
            target_region = room_regions.get(child_id)
            if child is None or target_region is None:
                continue
            horizontal_span = abs(child.depth - node.depth)
            if horizontal_span <= 2 or rng.random() >= 0.45:
                continue

            corridor_left_px = min(source_region.right, target_region.right)
            corridor_right_px = max(source_region.left, target_region.left)
            tile_x_start = int(corridor_left_px // TILE_SIZE)
            tile_x_end = int((corridor_right_px - 1) // TILE_SIZE)
            preferred_y = int(((source_region.centery + target_region.centery) * 0.5) // TILE_SIZE)
            run = walkable_corridor_tiles_between(grid, room_bounds, tile_x_start, tile_x_end, preferred_y)
            if not run:
                continue
            run = [tile for tile in run if corridor_tile_can_fit_enemy(grid, tile[0], tile[1])]
            if len(run) < 3:
                continue

            spawn_total = rng.randint(1, 2)
            segment_length = max(1, len(run) // (spawn_total + 1))
            used_tiles: set[tuple[int, int]] = set()
            for spawn_index in range(spawn_total):
                segment_start = min(len(run) - 1, segment_length * spawn_index)
                segment_end = min(len(run), segment_length * (spawn_index + 2))
                candidate_slice = run[segment_start:segment_end]
                if not candidate_slice:
                    candidate_slice = run
                middle = candidate_slice[len(candidate_slice) // 2]
                candidate_order = sorted(candidate_slice, key=lambda tile: abs(tile[0] - middle[0]))
                chosen_tile = next((tile for tile in candidate_order if tile not in used_tiles), None)
                if chosen_tile is None:
                    continue
                used_tiles.add(chosen_tile)
                enemy_spawns.append((find_enemy_spawn_position(grid, chosen_tile[0], chosen_tile[1], len(grid) * TILE_SIZE), rng.choice(enemy_types)))

    return enemy_spawns


def generate_fallback_enemy_spawns(
    grid: list[str],
    room_height: int,
    player_spawn: Vec2,
    role: str,
    room_size: str,
    room_index: int,
) -> list[tuple[Vec2, str]]:
    if role in {"start", "portal"}:
        return []

    candidate_tiles: list[tuple[int, int]] = []
    for tile_y in range(0, len(grid) - 1):
        row = grid[tile_y]
        below_row = grid[tile_y + 1]
        for tile_x in range(1, max(1, len(row) - 1)):
            if row[tile_x] != ".":
                continue
            if below_row[tile_x] not in {"#", "="}:
                continue
            candidate_tiles.append((tile_x, tile_y))

    if not candidate_tiles:
        return []

    rng = random.Random(f"fallback-enemy:{room_index}:{role}:{len(grid[0])}x{len(grid)}")
    if role == "boss":
        enemy_plan = ["boss"]
    elif room_size == "large":
        if role == "rest":
            enemy_count = 4 + ((room_index + len(grid) + len(grid[0])) % 4)
            enemy_pool = ["blade", "blade", "lancer", "archer"]
            enemy_plan = [rng.choice(enemy_pool) for _ in range(enemy_count)]
        else:
            return []
    elif role == "elite":
        enemy_plan = ["lancer", "archer"]
    elif role == "rest":
        return []
    else:
        enemy_plan = ["blade", "lancer", "archer"][: 3 if len(grid[0]) >= 22 else 2]
        rng.shuffle(enemy_plan)

    chosen_spawns: list[tuple[Vec2, str]] = []
    reserved_xs: list[float] = []
    min_player_distance = TILE_SIZE * 3.5
    min_enemy_spacing = TILE_SIZE * 4.0

    ordered_candidates = candidate_tiles[:]
    if role == "boss":
        center_x = len(grid[0]) * 0.5
        ordered_candidates.sort(key=lambda item: abs(item[0] - center_x))
    else:
        rng.shuffle(ordered_candidates)

    for enemy_type in enemy_plan:
        chosen_tile: tuple[int, int] | None = None
        fallback_tile: tuple[int, int] | None = None
        for tile_x, tile_y in ordered_candidates:
            spawn_position = find_enemy_spawn_position(grid, tile_x, tile_y, room_height)
            if fallback_tile is None:
                fallback_tile = (tile_x, tile_y)
            if abs(spawn_position.x - player_spawn.x) < min_player_distance:
                continue
            if any(abs(spawn_position.x - reserved_x) < min_enemy_spacing for reserved_x in reserved_xs):
                continue
            chosen_tile = (tile_x, tile_y)
            break
        if chosen_tile is None:
            if fallback_tile is None:
                continue
            chosen_tile = fallback_tile
        spawn_position = find_enemy_spawn_position(grid, chosen_tile[0], chosen_tile[1], room_height)
        chosen_spawns.append((spawn_position, enemy_type))
        reserved_xs.append(spawn_position.x)
        ordered_candidates = [tile for tile in ordered_candidates if tile != chosen_tile]

    return chosen_spawns


def collision_chunk_span(rect: pygame.Rect | pygame.FRect) -> tuple[range, range]:
    left = int(rect.left // COLLISION_CHUNK_SIZE)
    right = int((max(rect.left, rect.right - 1)) // COLLISION_CHUNK_SIZE)
    top = int(rect.top // COLLISION_CHUNK_SIZE)
    bottom = int((max(rect.top, rect.bottom - 1)) // COLLISION_CHUNK_SIZE)
    return range(left, right + 1), range(top, bottom + 1)


def build_collision_spatial_index(rects: list[pygame.Rect]) -> dict[tuple[int, int], list[pygame.Rect]]:
    index: dict[tuple[int, int], list[pygame.Rect]] = {}
    for rect in rects:
        chunk_xs, chunk_ys = collision_chunk_span(rect)
        for chunk_x in chunk_xs:
            for chunk_y in chunk_ys:
                index.setdefault((chunk_x, chunk_y), []).append(rect)
    return index


def query_collision_spatial_index(
    index: dict[tuple[int, int], list[pygame.Rect]],
    rect: pygame.Rect | pygame.FRect,
) -> list[pygame.Rect]:
    chunk_xs, chunk_ys = collision_chunk_span(rect)
    nearby: list[pygame.Rect] = []
    seen_ids: set[int] = set()
    for chunk_x in chunk_xs:
        for chunk_y in chunk_ys:
            for candidate in index.get((chunk_x, chunk_y), []):
                candidate_id = id(candidate)
                if candidate_id in seen_ids:
                    continue
                seen_ids.add(candidate_id)
                nearby.append(candidate)
    return nearby


def generate_fallback_item_spawns(
    centered_fixture_position: Vec2,
    role: str,
    room_size: str,
    room_index: int,
    generation_seed: int,
) -> list[tuple[Vec2, str, str | None, str | None]]:
    equipment_cycle = [
        ("brain", "knight_brain_sword"),
        ("brain", "knight_brain_scripture"),
        ("left_eye", "knight_left_eye_halo"),
        ("left_eye", "knight_left_eye_blade"),
        ("right_eye", "knight_right_eye_rain"),
        ("right_eye", "knight_right_eye_spirit"),
    ]
    equipment_rng = random.Random(f"fallback-item:{generation_seed}:{room_index}:{role}:{room_size}")
    selected_slot, selected_item = equipment_rng.choice(equipment_cycle)
    if role == "portal":
        return []
    if role == "boss":
        return [(centered_fixture_position.copy(), "heart", None, None)]
    if room_size != "small":
        return []
    if role == "rest":
        return [(centered_fixture_position.copy(), selected_slot, selected_item, None)]
    if role == "combat":
        return [(centered_fixture_position.copy(), selected_slot, None, selected_item)]
    return []


def roll_fixture_item(slot: str, item_id: str, role: str, loop_count: int, context: str) -> str | None:
    del loop_count
    if slot == "heart":
        return None

    chance = FIXTURE_BASE_CHANCES[slot]
    if context in {"library", "corridor_eye"}:
        chance = 1.0
    elif role == "boss":
        chance = min(1.0, chance + 0.04)

    if random.random() <= chance:
        return item_id
    return None
