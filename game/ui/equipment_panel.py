from __future__ import annotations

import pygame

from game.config import ACCENT_COLOR, DANGER_COLOR, MUTED_TEXT, PANEL_BORDER, PANEL_COLOR, PLAYER_PARRY_COLOR, SUCCESS_COLOR, TEXT_COLOR
from game.rendering import draw_ui_panel_box
from game.systems.equipment import EquipmentState, PassiveCardSummary, PassiveSummary, SLOT_LABELS, get_equipment, knight_minor_tier, major_is_active, passive_tier_details


MINOR_ARCHETYPE_META = {
    "sword": ("Sword", "Sword brain + blade eye", (186, 88, 92)),
    "shield": ("Shield", "Scripture brain + halo eye", (201, 176, 112)),
    "control": ("Control", "Rain eye", (144, 124, 240)),
    "summon": ("Summon", "Spirit eye", (96, 210, 194)),
}


def blend_color(start: tuple[int, int, int], end: tuple[int, int, int], ratio: float) -> tuple[int, int, int]:
    clamped_ratio = max(0.0, min(1.0, ratio))
    return tuple(int(round(start[index] + (end[index] - start[index]) * clamped_ratio)) for index in range(3))


def tier_visual_color(tier: int, base_color: tuple[int, int, int], neutral_color: tuple[int, int, int] = TEXT_COLOR) -> tuple[int, int, int]:
    if tier <= 1:
        return neutral_color
    ratio_map = {
        2: 0.42,
        3: 0.68,
        4: 0.90,
    }
    return blend_color(neutral_color, base_color, ratio_map.get(tier, 0.90))


def tier_from_label(tier_label: str) -> int:
    if not tier_label.startswith("T"):
        return 0
    try:
        return int(tier_label[1:])
    except ValueError:
        return 0


def passive_card_tier_color(card_summary: PassiveCardSummary) -> tuple[int, int, int]:
    tier = tier_from_label(card_summary.tier_label)
    if card_summary.key in MINOR_ARCHETYPE_META:
        return tier_visual_color(tier, MINOR_ARCHETYPE_META[card_summary.key][2])
    return tier_visual_color(tier, ACCENT_COLOR)


def draw_equipment_panel(surface: pygame.Surface, app, equipment: EquipmentState, passive_summary: PassiveSummary, nearby_item_id: str | None = None) -> None:
    panel = pygame.Rect(0, 0, 1120, 620)
    panel.center = (surface.get_width() // 2, surface.get_height() // 2)
    mouse_pos = pygame.mouse.get_pos()

    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((8, 10, 18, 198))
    surface.blit(overlay, (0, 0))

    back = pygame.Surface(panel.size, pygame.SRCALPHA)
    pygame.draw.rect(back, (18, 23, 34, 246), back.get_rect(), border_radius=28)
    pygame.draw.rect(back, (*PLAYER_PARRY_COLOR, 18), pygame.Rect(18, 18, panel.width - 36, 82), border_radius=22)
    pygame.draw.rect(back, (*ACCENT_COLOR, 18), pygame.Rect(18, 120, panel.width - 36, panel.height - 138), width=2, border_radius=24)
    surface.blit(back, panel.topleft)
    draw_ui_panel_box(app, surface, "equipment_main", panel, PANEL_COLOR, PANEL_BORDER, border_radius=28)

    title_font = app.get_font(32, bold=True)
    body_font = app.get_font(18)
    small_font = app.get_font(15)

    title = title_font.render("Organ Loadout", True, TEXT_COLOR)
    subtitle = body_font.render("Tab close  |  Empty slots auto-equip when you stand near a dropped organ", True, MUTED_TEXT)
    surface.blit(title, (panel.x + 28, panel.y + 24))
    surface.blit(subtitle, (panel.x + 28, panel.y + 64))

    left_rect = pygame.Rect(panel.x + 24, panel.y + 110, 332, 486)
    center_rect = pygame.Rect(panel.x + 372, panel.y + 110, 354, 486)
    right_rect = pygame.Rect(panel.x + 742, panel.y + 110, 354, 486)
    for rect in (left_rect, center_rect, right_rect):
        draw_ui_panel_box(app, surface, "equipment_column", rect, (18, 24, 34), PANEL_BORDER, border_radius=20, border_width=1)

    hovered_item_id = draw_left_column(surface, app, passive_summary, left_rect, mouse_pos)
    hovered_tier = draw_right_column(surface, app, equipment, passive_summary, right_rect, mouse_pos)
    draw_focus_column(surface, app, equipment, passive_summary, center_rect, hovered_item_id, hovered_tier, nearby_item_id)


def draw_left_column(surface: pygame.Surface, app, passive_summary: PassiveSummary, rect: pygame.Rect, mouse_pos: tuple[int, int]) -> str | None:
    title_font = app.get_font(22, bold=True)
    body_font = app.get_font(18)
    small_font = app.get_font(15)
    surface.blit(title_font.render("Passive Layout", True, TEXT_COLOR), (rect.x + 18, rect.y + 16))
    surface.blit(small_font.render("Left side only shows 1 major passive and 4 classified minor passives.", True, MUTED_TEXT), (rect.x + 18, rect.y + 46))

    if passive_summary.major_passive_card is None and not passive_summary.minor_passive_cards:
        empty = pygame.Rect(rect.x + 16, rect.y + 90, rect.width - 32, rect.height - 108)
        pygame.draw.rect(surface, (24, 31, 44), empty, border_radius=18)
        pygame.draw.rect(surface, PANEL_BORDER, empty, width=1, border_radius=18)
        surface.blit(body_font.render("No Organ Passives", True, TEXT_COLOR), (empty.x + 18, empty.y + 20))
        draw_wrapped_text(surface, app, "No classified passive is shown until at least one organ is equipped.", empty.x + 18, empty.y + 56, empty.width - 36, MUTED_TEXT, 16)
        return None

    hovered_item_id: str | None = None
    major_card = pygame.Rect(rect.x + 16, rect.y + 82, rect.width - 32, 112)
    hovered_item_id = draw_passive_card(surface, app, passive_summary.major_passive_card, major_card, mouse_pos, "Major Passive")

    minor_cards = passive_summary.minor_passive_cards[:4]
    for index, card_summary in enumerate(minor_cards):
        card = pygame.Rect(rect.x + 16, rect.y + 212 + index * 68, rect.width - 32, 58)
        current_hover = draw_passive_card(surface, app, card_summary, card, mouse_pos, "Minor Passive")
        if current_hover is not None:
            hovered_item_id = current_hover

    return hovered_item_id


def draw_passive_card(
    surface: pygame.Surface,
    app,
    card_summary: PassiveCardSummary | None,
    rect: pygame.Rect,
    mouse_pos: tuple[int, int],
    section_label: str,
) -> str | None:
    body_font = app.get_font(18)
    small_font = app.get_font(15)
    tiny_font = app.get_font(14)

    hovered = rect.collidepoint(mouse_pos)
    visible = card_summary is not None and card_summary.visible
    fill = (31, 40, 58) if hovered and visible else (24, 31, 44)
    border = ACCENT_COLOR if hovered and visible else (SUCCESS_COLOR if visible else PANEL_BORDER)
    pygame.draw.rect(surface, fill, rect, border_radius=16)
    pygame.draw.rect(surface, border, rect, width=2 if visible else 1, border_radius=16)
    surface.blit(tiny_font.render(section_label.upper(), True, MUTED_TEXT), (rect.x + 14, rect.y + 10))

    if card_summary is None or not card_summary.visible:
        surface.blit(body_font.render("None", True, DANGER_COLOR), (rect.x + 14, rect.y + 28))
        return None

    surface.blit(body_font.render(card_summary.title, True, TEXT_COLOR), (rect.x + 14, rect.y + 26))
    if card_summary.tier_label != "T0":
        tier_surface = small_font.render(card_summary.tier_label, True, passive_card_tier_color(card_summary))
        surface.blit(tier_surface, (rect.right - tier_surface.get_width() - 14, rect.y + 12))
    subtitle_color = ACCENT_COLOR if hovered else MUTED_TEXT
    draw_wrapped_text(surface, app, card_summary.subtitle, rect.x + 14, rect.y + 48, rect.width - 28, subtitle_color, 14)
    return card_summary.item_id if hovered else None


def draw_focus_column(
    surface: pygame.Surface,
    app,
    equipment: EquipmentState,
    passive_summary: PassiveSummary,
    rect: pygame.Rect,
    hovered_item_id: str | None,
    hovered_tier: int | None,
    nearby_item_id: str | None,
) -> None:
    title_font = app.get_font(22, bold=True)
    body_font = app.get_font(18)
    small_font = app.get_font(15)

    title, subtitle, lines, preview_item_id = resolve_focus_content(equipment, passive_summary, hovered_item_id, hovered_tier, nearby_item_id)
    surface.blit(title_font.render("Inspection", True, TEXT_COLOR), (rect.x + 18, rect.y + 16))
    hint_text = "Hover organs or set chips. Nearby drops also appear here." if nearby_item_id is not None else "Hover organs or set chips to inspect them."
    surface.blit(small_font.render(hint_text, True, MUTED_TEXT), (rect.x + 18, rect.y + 46))

    hero = pygame.Rect(rect.x + 18, rect.y + 82, rect.width - 36, 146)
    pygame.draw.rect(surface, (28, 36, 52), hero, border_radius=18)
    pygame.draw.rect(surface, ACCENT_COLOR, hero, width=2, border_radius=18)
    surface.blit(small_font.render(subtitle, True, MUTED_TEXT), (hero.x + 18, hero.y + 18))
    surface.blit(title_font.render(short_item_name(title), True, TEXT_COLOR), (hero.x + 18, hero.y + 42))
    if preview_item_id is not None:
        preview_item = get_equipment(preview_item_id)
        draw_slot_glyph(surface, preview_item.slot, preview_item_id, (hero.right - 50, hero.centery + 2), 26)
        surface.blit(small_font.render(preview_item.major_name, True, ACCENT_COLOR), (hero.x + 18, hero.y + 84))
    elif hovered_tier is not None:
        tier_surface = title_font.render(f"T{hovered_tier}", True, tier_visual_color(hovered_tier, PLAYER_PARRY_COLOR))
        surface.blit(tier_surface, (hero.right - tier_surface.get_width() - 18, hero.y + 38))

    notes = pygame.Rect(rect.x + 18, rect.y + 244, rect.width - 36, rect.height - 262)
    pygame.draw.rect(surface, (23, 29, 40), notes, border_radius=18)
    pygame.draw.rect(surface, PANEL_BORDER, notes, width=1, border_radius=18)
    surface.blit(body_font.render("Details", True, TEXT_COLOR), (notes.x + 16, notes.y + 14))
    cursor_y = notes.y + 46
    for line in lines[:7]:
        cursor_y = draw_wrapped_text(surface, app, line, notes.x + 16, cursor_y, notes.width - 32, TEXT_COLOR, 16) + 6

    footer = "Knight organs now signal their series in the world through a drop aura, not on the equipped body."
    draw_wrapped_text(surface, app, footer, notes.x + 16, notes.bottom - 54, notes.width - 32, MUTED_TEXT, 14)


def resolve_focus_content(
    equipment: EquipmentState,
    passive_summary: PassiveSummary,
    hovered_item_id: str | None,
    hovered_tier: int | None,
    nearby_item_id: str | None,
) -> tuple[str, str, list[str], str | None]:
    if hovered_item_id is not None:
        item = get_equipment(hovered_item_id)
        lines = [item.major_name, item.major_description]
        if item.minor_name and item.minor_description:
            lines.append(f"{item.minor_name}: {item.minor_description}")
        lines.append("State: active" if item.slot == "heart" or major_is_active(equipment, item.slot) else "State: dormant until the heart matches")
        return item.name, SLOT_LABELS[item.slot], lines, hovered_item_id

    if hovered_tier is not None:
        return f"Set Tier T{hovered_tier}", "Tier Preview", passive_tier_details(equipment, hovered_tier), None

    if nearby_item_id is not None:
        item = get_equipment(nearby_item_id)
        lines = ["Standing close to this dropped organ.", item.major_description]
        if item.minor_name and item.minor_description:
            lines.append(f"{item.minor_name}: {item.minor_description}")
        lines.append("Empty slot: this organ will auto-equip if you move onto it.")
        return item.name, "Nearby Organ", lines, nearby_item_id

    heart_id = equipment.equipped["heart"]
    if heart_id is not None:
        heart = get_equipment(heart_id)
        return heart.name, "Core Organ", [heart.major_name, heart.major_description, passive_summary.main_passive], heart_id
    return "No Heart Installed", "Inspection", ["The heart still controls which major organs are active.", "Minor passives are shown on the right and do not use the old body aura anymore."], None


def draw_right_column(surface: pygame.Surface, app, equipment: EquipmentState, passive_summary: PassiveSummary, rect: pygame.Rect, mouse_pos: tuple[int, int]) -> int | None:
    title_font = app.get_font(22, bold=True)
    body_font = app.get_font(18)
    small_font = app.get_font(15)
    tiny_font = app.get_font(14)
    active_tier = tier_from_label(passive_summary.tier_label)
    active_tier_color = tier_visual_color(active_tier, ACCENT_COLOR)

    surface.blit(title_font.render("Series Status", True, TEXT_COLOR), (rect.x + 18, rect.y + 16))
    series_surface = body_font.render(passive_summary.series_label, True, TEXT_COLOR)
    surface.blit(series_surface, (rect.x + 18, rect.y + 44))
    tier_surface = body_font.render(passive_summary.tier_label, True, active_tier_color if active_tier > 0 else MUTED_TEXT)
    surface.blit(tier_surface, (rect.x + 28 + series_surface.get_width(), rect.y + 44))
    surface.blit(small_font.render(passive_summary.main_passive, True, TEXT_COLOR), (rect.x + 18, rect.y + 70))

    hovered_tier: int | None = None
    chip_y = rect.y + 92
    for tier in range(1, 5):
        chip = pygame.Rect(rect.x + 18 + (tier - 1) * 78, chip_y, 64, 42)
        current = passive_summary.tier_label == f"T{tier}"
        unlocked = tier <= passive_summary.series_count
        chip_color = tier_visual_color(tier, ACCENT_COLOR)
        fill = blend_color((24, 31, 44), chip_color, 0.16) if unlocked and tier >= 2 else ((40, 52, 74) if unlocked else (24, 31, 44))
        border = chip_color if current or (unlocked and tier >= 2) else (TEXT_COLOR if current else (SUCCESS_COLOR if unlocked else PANEL_BORDER))
        pygame.draw.rect(surface, fill, chip, border_radius=12)
        pygame.draw.rect(surface, border, chip, width=2, border_radius=12)
        label_color = chip_color if unlocked else MUTED_TEXT
        label = body_font.render(f"T{tier}", True, label_color)
        surface.blit(label, label.get_rect(center=chip.center))
        if chip.collidepoint(mouse_pos):
            hovered_tier = tier

    summary = pygame.Rect(rect.x + 18, rect.y + 148, rect.width - 36, 86)
    pygame.draw.rect(surface, (24, 31, 44), summary, border_radius=16)
    pygame.draw.rect(surface, PANEL_BORDER, summary, width=1, border_radius=16)
    active_text = passive_summary.active_passives[0] if passive_summary.active_passives else "No active set bonus"
    draw_wrapped_text(surface, app, active_text, summary.x + 14, summary.y + 14, summary.width - 28, TEXT_COLOR, 16)
    draw_wrapped_text(surface, app, "Major organs still depend on the heart. Minor archetypes below do not.", summary.x + 14, summary.y + 48, summary.width - 28, MUTED_TEXT, 14)

    surface.blit(title_font.render("Minor Archetypes", True, TEXT_COLOR), (rect.x + 18, rect.y + 252))
    surface.blit(tiny_font.render("Only organs inside the same archetype raise that archetype tier.", True, MUTED_TEXT), (rect.x + 18, rect.y + 280))

    for index, archetype in enumerate(("sword", "shield", "control", "summon")):
        card = pygame.Rect(rect.x + 18 + (index % 2) * 160, rect.y + 312 + (index // 2) * 92, 150, 78)
        tier = knight_minor_tier(equipment, archetype)
        title, organs, color = MINOR_ARCHETYPE_META[archetype]
        tier_color = tier_visual_color(tier, color)
        hovered = card.collidepoint(mouse_pos)
        base_fill = (31, 40, 58) if hovered else (24, 31, 44)
        fill = blend_color(base_fill, tier_color, 0.14) if tier >= 2 else base_fill
        border = tier_color if tier > 0 else PANEL_BORDER
        pygame.draw.rect(surface, fill, card, border_radius=16)
        pygame.draw.rect(surface, border, card, width=2, border_radius=16)
        surface.blit(body_font.render(title, True, TEXT_COLOR), (card.x + 12, card.y + 12))
        surface.blit(body_font.render(f"T{tier}", True, tier_color if tier > 0 else MUTED_TEXT), (card.right - 40, card.y + 12))
        draw_wrapped_text(surface, app, organs, card.x + 12, card.y + 40, card.width - 24, TEXT_COLOR if tier > 0 else MUTED_TEXT, 14)

    return hovered_tier


def short_item_name(name: str) -> str:
    return name.split(": ", 1)[-1]


def draw_slot_glyph(surface: pygame.Surface, slot: str, item_id: str | None, center: tuple[int, int], radius: int) -> None:
    color = (86, 102, 126) if item_id is None else get_equipment(item_id).icon_color
    outline = PANEL_BORDER if item_id is None else TEXT_COLOR

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


def draw_wrapped_text(surface: pygame.Surface, app, text: str, x: int, y: int, width: int, color: tuple[int, int, int], size: int) -> int:
    font = app.get_font(size)
    words = text.split() if " " in text else list(text)
    line = ""
    cursor_y = y
    for word in words:
        separator = " " if " " in text else ""
        test = word if not line else f"{line}{separator}{word}"
        if font.size(test)[0] <= width:
            line = test
            continue
        if line:
            rendered = font.render(line, True, color)
            surface.blit(rendered, (x, cursor_y))
            cursor_y += rendered.get_height() + 2
        line = word
    if line:
        rendered = font.render(line, True, color)
        surface.blit(rendered, (x, cursor_y))
        cursor_y += rendered.get_height() + 2
    return cursor_y
