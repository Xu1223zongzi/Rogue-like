from __future__ import annotations

import pygame

from game.config import PANEL_BORDER, TEXT_COLOR
from game.systems.equipment import get_equipment


def draw_slot_glyph(app, surface: pygame.Surface, slot: str, item_id: str | None, center: tuple[int, int], radius: int) -> None:
    color = (86, 102, 126) if item_id is None else get_equipment(item_id).icon_color
    outline = PANEL_BORDER if item_id is None else TEXT_COLOR

    if hasattr(app, "resources") and app.resources.draw_ui_icon(surface, slot, item_id, center, radius):
        return

    if slot == "heart":
        points = [
            (center[0], center[1] + radius),
            (center[0] - radius, center[1] - 2),
            (center[0] - radius // 2, center[1] - radius),
            (center[0], center[1] - radius // 3),
            (center[0] + radius // 2, center[1] - radius),
            (center[0] + radius, center[1] - 2),
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, outline, points, width=2)
        return

    if slot == "brain":
        lobes = [
            (center[0] - radius // 2, center[1] - radius // 4),
            (center[0] + radius // 2, center[1] - radius // 4),
            (center[0] - radius // 3, center[1] + radius // 4),
            (center[0] + radius // 3, center[1] + radius // 4),
        ]
        for lobe in lobes:
            pygame.draw.circle(surface, color, lobe, max(4, radius // 2))
        pygame.draw.circle(surface, outline, center, radius, width=2)
        pygame.draw.line(surface, outline, (center[0], center[1] - radius + 4), (center[0], center[1] + radius - 4), width=2)
        return

    eye_rect = pygame.Rect(0, 0, radius * 2 + 4, radius + 8)
    eye_rect.center = center
    pygame.draw.ellipse(surface, color, eye_rect)
    pygame.draw.ellipse(surface, outline, eye_rect, width=2)
    iris_x = center[0] - radius // 4 if slot == "left_eye" else center[0] + radius // 4
    pygame.draw.circle(surface, (24, 28, 36), (iris_x, center[1]), max(4, radius // 3))
    pygame.draw.circle(surface, (235, 240, 248), (iris_x + (1 if slot == "right_eye" else -1), center[1] - 2), max(2, radius // 6))
