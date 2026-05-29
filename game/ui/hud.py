from __future__ import annotations

import math
import sys
from pathlib import Path

import pygame

try:
    from game.config import ACCENT_COLOR, DANGER_COLOR, MUTED_TEXT, PANEL_BORDER, PANEL_COLOR, SANITY_COLOR, SANITY_DANGER_COLOR, SUCCESS_COLOR, TEXT_COLOR, WINDOW_HEIGHT, WINDOW_WIDTH
    from game.rendering import draw_ui_panel_box
    from game.ui.equipment_panel import draw_slot_glyph
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from game.config import ACCENT_COLOR, DANGER_COLOR, MUTED_TEXT, PANEL_BORDER, PANEL_COLOR, SANITY_COLOR, SANITY_DANGER_COLOR, SUCCESS_COLOR, TEXT_COLOR, WINDOW_HEIGHT, WINDOW_WIDTH
    from game.rendering import draw_ui_panel_box
    from game.ui.equipment_panel import draw_slot_glyph


def draw_hud(
    surface: pygame.Surface,
    app,
    room_name: str,
    room_index: int,
    room_total: int,
    player_health: int,
    player_max_health: int,
    player_movement_state: str,
    player_action_state: str,
    enemy_count: int,
    sanity: float,
    sanity_max: float,
    temporary_shield: int,
    equipment_tier: str,
    message: str,
    message_color: tuple[int, int, int],
    player_dead: bool,
    cooldown_icons: list[dict[str, object]],
    status_bars: list[dict[str, object]],
    equipped_items: dict[str, str | None],
    combo_hits: int,
    combo_goal: int,
    brain_cooldown: float,
    brain_max_cooldown: float,
    route_map: dict[str, object] | None = None,
) -> None:
    del room_name
    del room_index
    del room_total
    del player_movement_state
    del player_action_state
    del enemy_count
    del equipment_tier
    del combo_goal
    del brain_cooldown
    del brain_max_cooldown

    panel = pygame.Rect(18, 18, 334, 172)
    draw_ui_panel_box(app, surface, "hud_main", panel, PANEL_COLOR, PANEL_BORDER, border_radius=16)

    body_font = app.get_font(17)
    small_font = app.get_font(15)
    tiny_font = app.get_font(11, bold=True)

    hp_label = body_font.render("HP", True, TEXT_COLOR)
    surface.blit(hp_label, (panel.x + 16, panel.y + 34))
    bar = pygame.Rect(panel.x + 64, panel.y + 40, 170, 14)
    pygame.draw.rect(surface, (44, 52, 62), bar, border_radius=8)
    ratio = 0.0 if player_max_health <= 0 else max(0.0, min(1.0, player_health / player_max_health))
    fill = bar.copy()
    fill.width = max(0, int(bar.width * ratio))
    pygame.draw.rect(surface, SUCCESS_COLOR if ratio > 0.35 else DANGER_COLOR, fill, border_radius=8)
    strip_y = bar.y - 7
    for status in status_bars:
        strip = pygame.Rect(bar.x, strip_y, bar.width, 5)
        label_rect = pygame.Rect(strip.x - 24, strip.y - 1, 20, 7)
        status_ratio = max(0.0, min(1.0, float(status.get("ratio", 0.0))))
        status_fill = strip.copy()
        status_fill.width = max(0, int(strip.width * status_ratio))
        back_color = tuple(status.get("back_color", (38, 62, 106)))
        fill_color = tuple(status.get("fill_color", (86, 176, 255)))
        edge_color = tuple(status.get("edge_color", (166, 224, 255)))
        label = str(status.get("label", ""))[:2]
        value_text = str(status.get("value_text", ""))[:10]
        pygame.draw.rect(surface, back_color, label_rect, border_radius=4)
        pygame.draw.rect(surface, edge_color, label_rect, width=1, border_radius=4)
        if label:
            label_surface = tiny_font.render(label, True, TEXT_COLOR)
            surface.blit(label_surface, label_surface.get_rect(center=label_rect.center))
        pygame.draw.rect(surface, back_color, strip, border_radius=4)
        pygame.draw.rect(surface, fill_color, status_fill, border_radius=4)
        pygame.draw.rect(surface, edge_color, strip, width=1, border_radius=4)
        if value_text:
            value_surface = tiny_font.render(value_text, True, TEXT_COLOR)
            value_rect = value_surface.get_rect(midright=(strip.right - 4, strip.centery))
            shadow_rect = value_rect.move(1, 1)
            surface.blit(tiny_font.render(value_text, True, PANEL_BORDER), shadow_rect)
            surface.blit(value_surface, value_rect)
        strip_y -= 7
    pygame.draw.rect(surface, PANEL_BORDER, bar, width=2, border_radius=8)
    hp_text = body_font.render(f"{player_health}/{player_max_health}", True, TEXT_COLOR)
    surface.blit(hp_text, (bar.right + 12, panel.y + 32))

    san_label = body_font.render("SAN", True, TEXT_COLOR)
    surface.blit(san_label, (panel.x + 16, panel.y + 66))
    sanity_bar = pygame.Rect(panel.x + 64, panel.y + 72, 170, 12)
    pygame.draw.rect(surface, (44, 52, 62), sanity_bar, border_radius=7)
    sanity_ratio = 0.0 if sanity_max <= 0 else max(0.0, min(1.0, sanity / sanity_max))
    sanity_fill = sanity_bar.copy()
    sanity_fill.width = max(0, int(sanity_bar.width * sanity_ratio))
    pygame.draw.rect(surface, SANITY_COLOR if sanity_ratio > 0.5 else SANITY_DANGER_COLOR, sanity_fill, border_radius=7)
    pygame.draw.rect(surface, PANEL_BORDER, sanity_bar, width=2, border_radius=7)
    sanity_text = body_font.render(f"{int(sanity)}/{int(sanity_max)}", True, TEXT_COLOR)
    surface.blit(sanity_text, (sanity_bar.right + 12, panel.y + 61))

    slots = ["heart", "brain", "left_eye", "right_eye"]
    cooldown_lookup = {str(icon.get("slot")): icon for icon in cooldown_icons[:4]}
    for index, slot in enumerate(slots):
        slot_rect = pygame.Rect(panel.x + 18 + index * 64, panel.y + 102, 52, 44)
        pygame.draw.rect(surface, (24, 31, 44), slot_rect, border_radius=12)
        pygame.draw.rect(surface, ACCENT_COLOR if equipped_items.get(slot) is not None else PANEL_BORDER, slot_rect, width=2 if equipped_items.get(slot) is not None else 1, border_radius=12)
        draw_slot_glyph(surface, slot, equipped_items.get(slot), (slot_rect.centerx, slot_rect.y + 17), 9)
        icon = cooldown_lookup.get(slot)
        if icon is None or equipped_items.get(slot) is None:
            continue
        cooldown = float(icon["cooldown"])
        max_cooldown = max(0.001, float(icon["max_cooldown"]))
        if cooldown <= 0.01:
            continue
        if slot in {"brain", "left_eye", "right_eye"}:
            continue
        ratio = max(0.0, min(1.0, cooldown / max_cooldown))
        overlay_height = int(slot_rect.height * ratio)
        overlay = pygame.Surface(slot_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(overlay, (8, 11, 18, 150), (0, 0, slot_rect.width, slot_rect.height), border_radius=12)
        pygame.draw.rect(overlay, (6, 8, 14, 190), (0, 0, slot_rect.width, overlay_height), border_radius=12)
        surface.blit(overlay, slot_rect.topleft)

    active_slots = [
        ("heart", (232, 138, 120), (92, 44, 46), (255, 224, 214)),
        ("brain", (164, 132, 244), (62, 44, 104), (226, 212, 255)),
        ("left_eye", (120, 198, 255), (34, 62, 92), (216, 244, 255)),
        ("right_eye", (174, 152, 255), (56, 44, 96), (232, 224, 255)),
    ]
    for index, (slot, fill_color, back_color, edge_color) in enumerate(active_slots):
        slot_rect = pygame.Rect(panel.x + 18 + index * 64, panel.y + 102, 52, 44)
        segment = pygame.Rect(slot_rect.x, slot_rect.bottom + 6, slot_rect.width, 6)
        icon = cooldown_lookup.get(slot)
        item_id = equipped_items.get(slot)
        ratio = 0.0
        if item_id is not None and icon is not None:
            cooldown = max(0.0, float(icon.get("cooldown", 0.0)))
            max_cooldown = max(0.001, float(icon.get("max_cooldown", 1.0)))
            ratio = max(0.0, min(1.0, 1.0 - cooldown / max_cooldown))
        pygame.draw.rect(surface, back_color if item_id is not None else (36, 42, 54), segment, border_radius=4)
        if ratio > 0.0:
            fill_rect = segment.copy()
            fill_rect.width = max(1, int(segment.width * ratio))
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=4)
        pygame.draw.rect(surface, edge_color if item_id is not None else PANEL_BORDER, segment, width=1, border_radius=4)

    draw_route_minimap(surface, app, route_map)

    if combo_hits > 3:
        combo_font = app.get_font(36, bold=True)
        combo_text = combo_font.render(str(combo_hits), True, ACCENT_COLOR)
        combo_shadow = combo_font.render(str(combo_hits), True, PANEL_BORDER)
        combo_anchor = (surface.get_width() - 272, 192)
        surface.blit(combo_shadow, (combo_anchor[0] + 2, combo_anchor[1] + 2))
        surface.blit(combo_text, combo_anchor)

    if message:
        message_surface = body_font.render(message, True, message_color)
        surface.blit(message_surface, message_surface.get_rect(midtop=(surface.get_width() // 2, 18)))

    if player_dead:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((18, 5, 5, 160))
        surface.blit(overlay, (0, 0))

        title = app.get_font(42, bold=True).render("你已死亡", True, DANGER_COLOR)
        prompt = app.get_font(22).render("按 Enter 重新开始", True, ACCENT_COLOR)
        surface.blit(title, title.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 18)))
        surface.blit(prompt, prompt.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 28)))


MAP_BACKGROUND_COLOR = (18, 24, 34)
MAP_SOLID_COLOR = (94, 108, 126)
MAP_SOLID_EDGE = (138, 150, 166)
MAP_PLATFORM_COLOR = (122, 140, 160)
MAP_HOSTILE_COLOR = (210, 112, 112)
MAP_BOSS_COLOR = (255, 194, 120)
MINIMAP_VIEW_SCALE = 5.2


def _fit_world_map_rect(bounds: pygame.Rect, world_width: float, world_height: float) -> pygame.Rect:
    if world_width <= 0 or world_height <= 0:
        return bounds.copy()
    scale = min(bounds.width / world_width, bounds.height / world_height)
    draw_width = max(1, int(round(world_width * scale)))
    draw_height = max(1, int(round(world_height * scale)))
    return pygame.Rect(bounds.centerx - draw_width // 2, bounds.centery - draw_height // 2, draw_width, draw_height)


def _compute_world_view(
    bounds: pygame.Rect,
    world_width: float,
    world_height: float,
    focus: tuple[float, float] | None,
    zoom: float,
    full_map: bool,
) -> tuple[pygame.Rect, float, float, float, float, float]:
    if world_width <= 0 or world_height <= 0:
        return bounds.copy(), 1.0, 0.0, 0.0, max(1.0, world_width), max(1.0, world_height)

    if full_map:
        if zoom <= 1.001:
            view_width = world_width
            view_height = world_height
        else:
            view_width = max(world_width / zoom, 1.0)
            view_height = max(world_height / zoom, 1.0)
    else:
        view_width = min(world_width, WINDOW_WIDTH * MINIMAP_VIEW_SCALE)
        view_height = min(world_height, WINDOW_HEIGHT * MINIMAP_VIEW_SCALE)

    aspect = bounds.width / max(1, bounds.height)
    if view_width / max(1.0, view_height) > aspect:
        view_height = min(world_height, view_width / aspect)
    else:
        view_width = min(world_width, view_height * aspect)

    if focus is None:
        focus = (world_width * 0.5, world_height * 0.5)
    left = max(0.0, min(focus[0] - view_width * 0.5, world_width - view_width))
    top = max(0.0, min(focus[1] - view_height * 0.5, world_height - view_height))

    draw_rect = _fit_world_map_rect(bounds, view_width, view_height)
    scale = min(draw_rect.width / max(1.0, view_width), draw_rect.height / max(1.0, view_height))
    return draw_rect, scale, left, top, view_width, view_height


def _draw_world_map_view(
    surface: pygame.Surface,
    bounds: pygame.Rect,
    route_map: dict[str, object],
    zoom: float,
    full_map: bool,
    view_focus: tuple[float, float] | None = None,
) -> None:
    world_width = float(route_map.get("world_width", 0.0))
    world_height = float(route_map.get("world_height", 0.0))
    solids = route_map.get("solids", [])
    semisolids = route_map.get("semisolids", [])
    player_world_position = route_map.get("player_world_position")
    hostile_world_positions = route_map.get("hostile_world_positions", [])
    boss_world_positions = route_map.get("boss_world_positions", [])
    teleport_portals = route_map.get("teleport_portals", [])
    selected_teleport_portal_id = route_map.get("selected_teleport_portal_id")
    fog_reveal_points = route_map.get("fog_reveal_points", [])
    fog_reveal_radius = float(route_map.get("fog_reveal_radius", 0.0))
    player_focus = None
    if isinstance(player_world_position, (tuple, list)) and len(player_world_position) == 2:
        player_focus = (float(player_world_position[0]), float(player_world_position[1]))

    effective_focus = view_focus if view_focus is not None else player_focus
    draw_rect, scale, left, top, view_width, view_height = _compute_world_view(bounds, world_width, world_height, effective_focus, zoom, full_map)
    map_surface = pygame.Surface(draw_rect.size, pygame.SRCALPHA)
    map_surface.fill(MAP_BACKGROUND_COLOR)

    def world_to_local(x: float, y: float) -> tuple[int, int]:
        return (
            int(round((x - left) * scale)),
            int(round((y - top) * scale)),
        )

    def rect_to_local(rect: pygame.Rect) -> pygame.Rect:
        local_left = (rect.left - left) * scale
        local_top = (rect.top - top) * scale
        local_right = (rect.right - left) * scale
        local_bottom = (rect.bottom - top) * scale
        x = math.floor(local_left)
        y = math.floor(local_top)
        width = max(1, math.ceil(local_right) - x)
        height = max(1, math.ceil(local_bottom) - y)
        return pygame.Rect(x, y, width, height)

    view_rect_world = pygame.Rect(int(left), int(top), int(view_width) + 2, int(view_height) + 2)
    for solid in solids:
        if not view_rect_world.colliderect(solid):
            continue
        scaled = rect_to_local(solid)
        pygame.draw.rect(map_surface, MAP_SOLID_COLOR, scaled)
        pygame.draw.rect(map_surface, MAP_SOLID_EDGE, scaled, width=1)

    for platform in semisolids:
        if not view_rect_world.colliderect(platform):
            continue
        start = world_to_local(platform.left, platform.top)
        end = world_to_local(platform.right, platform.top)
        pygame.draw.line(map_surface, MAP_PLATFORM_COLOR, start, end, width=max(1, int(round(scale * 0.2))))

    enemy_radius = max(2, int(round(scale * 0.18)))
    for point in hostile_world_positions:
        if not isinstance(point, (tuple, list)) or len(point) != 2:
            continue
        enemy_pos = world_to_local(float(point[0]), float(point[1]))
        pygame.draw.circle(map_surface, PANEL_BORDER, enemy_pos, enemy_radius + 1)
        pygame.draw.circle(map_surface, MAP_HOSTILE_COLOR, enemy_pos, enemy_radius)

    boss_radius = max(enemy_radius + 1, int(round(scale * 0.26)))
    for point in boss_world_positions:
        if not isinstance(point, (tuple, list)) or len(point) != 2:
            continue
        boss_pos = world_to_local(float(point[0]), float(point[1]))
        pygame.draw.circle(map_surface, PANEL_BORDER, boss_pos, boss_radius + 2)
        pygame.draw.circle(map_surface, MAP_BOSS_COLOR, boss_pos, boss_radius)

    portal_radius = max(4, int(round(scale * 0.34)))
    for portal in teleport_portals:
        if not isinstance(portal, dict):
            continue
        point = portal.get("position")
        if not isinstance(point, (tuple, list)) or len(point) != 2:
            continue
        portal_pos = world_to_local(float(point[0]), float(point[1]))
        activated = bool(portal.get("activated", False))
        ring_color = (118, 204, 255) if activated else (98, 108, 124)
        edge_color = (236, 248, 255) if activated else (160, 166, 178)
        pygame.draw.circle(map_surface, edge_color, portal_pos, portal_radius + 3)
        pygame.draw.circle(map_surface, ring_color, portal_pos, portal_radius + 1, width=2)
        pygame.draw.circle(map_surface, MAP_BACKGROUND_COLOR, portal_pos, max(2, portal_radius - 2))
        if portal.get("portal_id") == selected_teleport_portal_id:
            marker = pygame.Rect(portal_pos[0] - portal_radius - 7, portal_pos[1] - portal_radius - 7, (portal_radius + 7) * 2, (portal_radius + 7) * 2)
            pygame.draw.rect(map_surface, (255, 238, 168), marker, width=2, border_radius=4)

    if player_focus is not None:
        player_pos = world_to_local(player_focus[0], player_focus[1])
        radius = max(3, int(round(scale * 0.22)))
        pygame.draw.circle(map_surface, TEXT_COLOR, player_pos, radius + 2)
        pygame.draw.circle(map_surface, ACCENT_COLOR, player_pos, radius)

    if fog_reveal_radius > 0.0:
        fog_surface = pygame.Surface(draw_rect.size, pygame.SRCALPHA)
        fog_surface.fill((0, 0, 0, 0))
        reveal_radius = max(8, int(round(fog_reveal_radius * scale)))
        for point in fog_reveal_points:
            if not isinstance(point, (tuple, list)) or len(point) != 2:
                continue
            reveal_pos = world_to_local(float(point[0]), float(point[1]))
            pygame.draw.circle(fog_surface, (0, 0, 0, 0), reveal_pos, reveal_radius)
        if player_focus is not None:
            reveal_pos = world_to_local(player_focus[0], player_focus[1])
            pygame.draw.circle(fog_surface, (0, 0, 0, 0), reveal_pos, reveal_radius)
        map_surface.blit(fog_surface, (0, 0))

    surface.blit(map_surface, draw_rect.topleft)


def draw_cooldown_icons(surface: pygame.Surface, app, cooldown_icons: list[dict[str, object]]) -> None:
    if not cooldown_icons:
        return

    panel = pygame.Rect(18, surface.get_height() - 68, 292, 64)
    draw_ui_panel_box(app, surface, "map_panel", panel, PANEL_COLOR, PANEL_BORDER, border_radius=14)

    for index, icon in enumerate(cooldown_icons[:4]):
        slot_rect = pygame.Rect(panel.x + 12 + index * 68, panel.y + 10, 56, 44)
        pygame.draw.rect(surface, (24, 31, 44), slot_rect, border_radius=12)
        pygame.draw.rect(surface, PANEL_BORDER, slot_rect, width=1, border_radius=12)

        slot = str(icon["slot"])
        item_id = icon.get("item_id")
        cooldown = float(icon["cooldown"])
        max_cooldown = max(0.001, float(icon["max_cooldown"]))
        ready = cooldown <= 0.01 and item_id is not None

        draw_slot_glyph(surface, slot, item_id if isinstance(item_id, str) else None, slot_rect.center, 10)

        if item_id is None:
            continue

        if not ready:
            ratio = max(0.0, min(1.0, cooldown / max_cooldown))
            overlay_height = int(slot_rect.height * ratio)
            overlay = pygame.Surface(slot_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(overlay, (8, 11, 18, 160), (0, 0, slot_rect.width, slot_rect.height), border_radius=12)
            pygame.draw.rect(overlay, (6, 8, 14, 185), (0, 0, slot_rect.width, overlay_height), border_radius=12)
            surface.blit(overlay, slot_rect.topleft)


def draw_route_minimap(surface: pygame.Surface, app, route_map: dict[str, object] | None) -> None:
    if not route_map:
        return

    if float(route_map.get("world_width", 0.0)) <= 0.0 or float(route_map.get("world_height", 0.0)) <= 0.0:
        return

    panel = pygame.Rect(surface.get_width() - 222, 18, 204, 142)
    pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=14)
    pygame.draw.rect(surface, PANEL_BORDER, panel, width=2, border_radius=14)

    title_font = app.get_font(16, bold=True)
    small_font = app.get_font(14)
    surface.blit(title_font.render("地图", True, TEXT_COLOR), (panel.x + 12, panel.y + 8))
    seed_text = small_font.render(str(route_map.get("seed", "")), True, MUTED_TEXT)
    surface.blit(seed_text, (panel.right - seed_text.get_width() - 12, panel.y + 10))
    hint_text = small_font.render("M 展开", True, MUTED_TEXT)
    surface.blit(hint_text, (panel.x + 12, panel.bottom - hint_text.get_height() - 8))

    map_rect = pygame.Rect(panel.x + 12, panel.y + 32, panel.width - 24, panel.height - 52)
    _draw_world_map_view(surface, map_rect, route_map, zoom=1.0, full_map=False)


def draw_world_map_overlay(
    surface: pygame.Surface,
    app,
    route_map: dict[str, object] | None,
    zoom: float,
    focus: tuple[float, float] | None = None,
) -> None:
    if not route_map or float(route_map.get("world_width", 0.0)) <= 0.0 or float(route_map.get("world_height", 0.0)) <= 0.0:
        return

    panel = pygame.Rect(surface.get_width() // 10, surface.get_height() // 10, surface.get_width() * 8 // 10, surface.get_height() * 8 // 10)
    draw_ui_panel_box(app, surface, "world_map_panel", panel, PANEL_COLOR, PANEL_BORDER, border_radius=18)

    title_font = app.get_font(24, bold=True)
    body_font = app.get_font(18)
    surface.blit(title_font.render("世界地图", True, TEXT_COLOR), (panel.x + 18, panel.y + 14))
    controls = body_font.render("M 关闭   Q 缩小   E 放大   WASD 地图/传送门   Space 传送", True, MUTED_TEXT)
    surface.blit(controls, (panel.right - controls.get_width() - 18, panel.y + 18))

    map_rect = pygame.Rect(panel.x + 20, panel.y + 56, panel.width - 40, panel.height - 76)
    pygame.draw.rect(surface, MAP_BACKGROUND_COLOR, _fit_world_map_rect(map_rect, float(route_map.get("world_width", 0.0)), float(route_map.get("world_height", 0.0))), border_radius=14)
    pygame.draw.rect(surface, PANEL_BORDER, map_rect, width=1, border_radius=14)
    _draw_world_map_view(surface, map_rect, route_map, zoom=max(1.0, zoom), full_map=True, view_focus=focus)
