from __future__ import annotations

import json
import math
from pathlib import Path

import pygame


class RenderResources:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.manifests: dict[str, dict[str, object]] = {}
        self.image_cache: dict[str, pygame.Surface | None] = {}
        self.scaled_cache: dict[tuple[str, tuple[int, int], bool], pygame.Surface] = {}

    def load_manifest(self, name: str) -> dict[str, object]:
        if name in self.manifests:
            return self.manifests[name]
        manifest_path = self.root / "manifests" / f"{name}.json"
        if not manifest_path.exists():
            self.manifests[name] = {}
            return self.manifests[name]
        try:
            self.manifests[name] = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.manifests[name] = {}
        return self.manifests[name]

    def _resolve_path(self, relative_path: str | None) -> Path | None:
        if not relative_path:
            return None
        asset_path = self.root / relative_path
        if not asset_path.exists():
            return None
        return asset_path

    def load_image(self, relative_path: str | None) -> pygame.Surface | None:
        if not relative_path:
            return None
        if relative_path in self.image_cache:
            return self.image_cache[relative_path]
        asset_path = self._resolve_path(relative_path)
        if asset_path is None:
            self.image_cache[relative_path] = None
            return None
        try:
            self.image_cache[relative_path] = pygame.image.load(str(asset_path)).convert_alpha()
        except pygame.error:
            self.image_cache[relative_path] = None
        return self.image_cache[relative_path]

    def _scaled_image(self, relative_path: str, size: tuple[int, int], flip_x: bool) -> pygame.Surface | None:
        cache_key = (relative_path, size, flip_x)
        if cache_key in self.scaled_cache:
            return self.scaled_cache[cache_key]
        image = self.load_image(relative_path)
        if image is None:
            return None
        scaled = pygame.transform.smoothscale(image, size)
        if flip_x:
            scaled = pygame.transform.flip(scaled, True, False)
        self.scaled_cache[cache_key] = scaled
        return scaled

    def _manifest_image_list(self, entry: object) -> list[str]:
        if isinstance(entry, str) and entry:
            return [entry]
        if isinstance(entry, list):
            return [value for value in entry if isinstance(value, str) and value]
        return []

    def _resolve_layer_entry(self, entry: object) -> list[str]:
        direct_paths = self._manifest_image_list(entry)
        if direct_paths:
            return direct_paths
        if not isinstance(entry, dict):
            return []

        whole_paths = self._manifest_image_list(entry.get("whole"))
        if whole_paths:
            return whole_paths

        image_paths = self._manifest_image_list(entry.get("image"))
        if image_paths:
            return image_paths

        parts_entry = entry.get("parts", {})
        if not isinstance(parts_entry, dict):
            return []
        ordered_parts = entry.get("part_order", [])
        ordered_names: list[str] = []
        if isinstance(ordered_parts, list):
            ordered_names.extend([name for name in ordered_parts if isinstance(name, str) and name in parts_entry])
        ordered_names.extend([name for name in parts_entry.keys() if isinstance(name, str) and name not in ordered_names])
        resolved_paths: list[str] = []
        for name in ordered_names:
            resolved_paths.extend(self._resolve_layer_entry(parts_entry.get(name)))
        return resolved_paths

    def _resolve_manifest_item(self, manifest: dict[str, object], sections: list[str], item_key: str) -> object:
        for section in sections:
            section_entry = manifest.get(section, {})
            if not isinstance(section_entry, dict):
                continue
            if item_key in section_entry:
                return section_entry[item_key]
        return None

    def _resolve_visual_paths(self, manifest_name: str, section: str, visual_key: str, states: list[str] | None = None) -> list[str]:
        manifest = self.load_manifest(manifest_name)
        visual_entry = self._resolve_manifest_item(manifest, [section], visual_key)
        if visual_entry is None:
            return []
        return self._resolve_visual_entry(visual_entry, states)

    def _resolve_visual_entry(self, visual_entry: object, states: list[str] | None = None) -> list[str]:
        direct_paths = self._resolve_layer_entry(visual_entry)
        if direct_paths:
            return direct_paths
        if not isinstance(visual_entry, dict):
            return []
        state_entry = visual_entry.get("states", {})
        if isinstance(state_entry, dict) and states:
            for state in states:
                resolved = self._resolve_layer_entry(state_entry.get(state))
                if resolved:
                    return resolved
        return self._resolve_layer_entry(visual_entry.get("default"))

    def _draw_paths(
        self,
        surface: pygame.Surface,
        relative_paths: list[str],
        rect: pygame.Rect,
        flip_x: bool = False,
        alpha: int = 255,
    ) -> bool:
        if not relative_paths:
            return False
        size = (max(1, rect.width), max(1, rect.height))
        clamped_alpha = max(0, min(255, int(alpha)))
        drew_any = False
        for relative_path in relative_paths:
            sprite = self._scaled_image(relative_path, size, flip_x)
            if sprite is None:
                continue
            draw_sprite = sprite
            if clamped_alpha < 255:
                draw_sprite = sprite.copy()
                draw_sprite.set_alpha(clamped_alpha)
            surface.blit(draw_sprite, rect.topleft)
            drew_any = True
        return drew_any

    def _draw_oriented_paths(
        self,
        surface: pygame.Surface,
        relative_paths: list[str],
        center: tuple[int, int],
        size: tuple[int, int],
        angle_degrees: float,
        alpha: int = 255,
    ) -> bool:
        if not relative_paths:
            return False
        width = max(1, int(size[0]))
        height = max(1, int(size[1]))
        clamped_alpha = max(0, min(255, int(alpha)))
        drew_any = False
        for relative_path in relative_paths:
            image = self.load_image(relative_path)
            if image is None:
                continue
            scaled = pygame.transform.smoothscale(image, (width, height))
            rotated = pygame.transform.rotate(scaled, angle_degrees)
            if clamped_alpha < 255:
                rotated = rotated.copy()
                rotated.set_alpha(clamped_alpha)
            rect = rotated.get_rect(center=center)
            surface.blit(rotated, rect.topleft)
            drew_any = True
        return drew_any

    def draw_actor_sprite(
        self,
        surface: pygame.Surface,
        actor_key: str,
        states: list[str],
        rect: pygame.Rect,
        facing: int,
        alpha: int = 255,
    ) -> bool:
        manifest = self.load_manifest("actor_appearances")
        actor_entry = self._resolve_manifest_item(manifest, ["players", "enemies", "summons", "actors"], actor_key)
        if not isinstance(actor_entry, dict):
            return False
        states_entry = actor_entry.get("states", {})
        if not isinstance(states_entry, dict):
            return False
        relative_paths: list[str] = []
        for state in states:
            state_entry = states_entry.get(state)
            relative_paths = self._resolve_layer_entry(state_entry)
            if relative_paths:
                break
        if not relative_paths:
            relative_paths = self._resolve_layer_entry(actor_entry.get("default"))
        if not relative_paths:
            return False
        if not self._draw_paths(surface, relative_paths, rect, flip_x=facing < 0, alpha=alpha):
            return False
        return True

    def draw_scene_visual(
        self,
        surface: pygame.Surface,
        visual_key: str,
        rect: pygame.Rect,
        states: list[str] | None = None,
        flip_x: bool = False,
        alpha: int = 255,
    ) -> bool:
        relative_paths = self._resolve_visual_paths("scene_visuals", "visuals", visual_key, states=states)
        if not relative_paths:
            relative_paths = self._resolve_visual_paths("scene_visuals", "props", visual_key, states=states)
        if not relative_paths:
            relative_paths = self._resolve_visual_paths("scene_visuals", "gates", visual_key, states=states)
        if not relative_paths:
            relative_paths = self._resolve_visual_paths("scene_visuals", "portals", visual_key, states=states)
        if not relative_paths:
            relative_paths = self._resolve_visual_paths("scene_visuals", "combat", visual_key, states=states)
        if not relative_paths:
            relative_paths = self._resolve_visual_paths("scene_visuals", "overlays", visual_key, states=states)
        return self._draw_paths(surface, relative_paths, rect, flip_x=flip_x, alpha=alpha)

    def draw_scene_visual_centered(
        self,
        surface: pygame.Surface,
        visual_key: str,
        center: tuple[int, int],
        size: tuple[int, int],
        states: list[str] | None = None,
        flip_x: bool = False,
        alpha: int = 255,
    ) -> bool:
        rect = pygame.Rect(0, 0, max(1, size[0]), max(1, size[1]))
        rect.center = center
        return self.draw_scene_visual(surface, visual_key, rect, states=states, flip_x=flip_x, alpha=alpha)

    def draw_scene_visual_fullscreen(
        self,
        surface: pygame.Surface,
        visual_key: str,
        states: list[str] | None = None,
        alpha: int = 255,
    ) -> bool:
        rect = surface.get_rect()
        return self.draw_scene_visual(surface, visual_key, rect, states=states, alpha=alpha)

    def draw_scene_line_visual(
        self,
        surface: pygame.Surface,
        visual_key: str,
        start: tuple[int, int],
        end: tuple[int, int],
        thickness: int,
        states: list[str] | None = None,
        alpha: int = 255,
    ) -> bool:
        relative_paths = self._resolve_visual_paths("scene_visuals", "visuals", visual_key, states=states)
        if not relative_paths:
            return False
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length <= 1.0:
            return False
        angle_degrees = -math.degrees(math.atan2(dy, dx))
        center = (int((start[0] + end[0]) * 0.5), int((start[1] + end[1]) * 0.5))
        return self._draw_oriented_paths(surface, relative_paths, center, (max(1, int(length)), max(1, int(thickness))), angle_degrees, alpha=alpha)

    def draw_ui_panel(self, surface: pygame.Surface, panel_key: str, rect: pygame.Rect, alpha: int = 255) -> bool:
        manifest = self.load_manifest("ui_skin")
        entry = self._resolve_manifest_item(manifest, ["panels"], panel_key)
        relative_paths = self._resolve_layer_entry(entry)
        if not relative_paths:
            return False
        return self._draw_paths(surface, relative_paths, rect, alpha=alpha)

    def draw_ui_icon(self, surface: pygame.Surface, icon_key: str, item_id: str | None, center: tuple[int, int], radius: int) -> bool:
        manifest = self.load_manifest("ui_icons")
        entry = self._resolve_manifest_item(manifest, ["icons"], icon_key)
        if not isinstance(entry, dict):
            return False
        resolved_paths: list[str] = []
        item_entry = entry.get("items", {})
        if item_id and isinstance(item_entry, dict):
            resolved_paths = self._resolve_layer_entry(item_entry.get(item_id))
        if not resolved_paths:
            resolved_paths = self._resolve_visual_entry(entry)
        if not resolved_paths:
            return False
        size = max(4, radius * 2 + 8)
        rect = pygame.Rect(0, 0, size, size)
        rect.center = center
        return self._draw_paths(surface, resolved_paths, rect, alpha=255)


def draw_ui_panel_box(
    app,
    surface: pygame.Surface,
    panel_key: str,
    rect: pygame.Rect,
    fill_color: tuple[int, int, int],
    border_color: tuple[int, int, int],
    border_radius: int,
    border_width: int = 2,
    alpha: int = 255,
) -> None:
    if hasattr(app, "resources") and app.resources.draw_ui_panel(surface, panel_key, rect, alpha=alpha):
        return
    pygame.draw.rect(surface, fill_color, rect, border_radius=border_radius)
    pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=border_radius)
