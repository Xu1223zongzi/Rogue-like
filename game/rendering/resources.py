from __future__ import annotations

import json
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
        actors = manifest.get("actors", {})
        if not isinstance(actors, dict):
            return False
        actor_entry = actors.get(actor_key)
        if not isinstance(actor_entry, dict):
            return False
        states_entry = actor_entry.get("states", {})
        if not isinstance(states_entry, dict):
            return False
        relative_path: str | None = None
        for state in states:
            state_entry = states_entry.get(state)
            if isinstance(state_entry, str) and state_entry:
                relative_path = state_entry
                break
        if relative_path is None:
            default_entry = actor_entry.get("default")
            if isinstance(default_entry, str) and default_entry:
                relative_path = default_entry
        if relative_path is None:
            return False
        size = (max(1, rect.width), max(1, rect.height))
        sprite = self._scaled_image(relative_path, size, facing < 0)
        if sprite is None:
            return False
        draw_sprite = sprite
        clamped_alpha = max(0, min(255, int(alpha)))
        if clamped_alpha < 255:
            draw_sprite = sprite.copy()
            draw_sprite.set_alpha(clamped_alpha)
        surface.blit(draw_sprite, rect.topleft)
        return True

    def draw_ui_panel(self, surface: pygame.Surface, panel_key: str, rect: pygame.Rect, alpha: int = 255) -> bool:
        manifest = self.load_manifest("ui_skin")
        panels = manifest.get("panels", {})
        if not isinstance(panels, dict):
            return False
        entry = panels.get(panel_key)
        relative_path: str | None = None
        if isinstance(entry, str):
            relative_path = entry
        elif isinstance(entry, dict):
            image_value = entry.get("image")
            if isinstance(image_value, str):
                relative_path = image_value
        if not relative_path:
            return False
        sprite = self._scaled_image(relative_path, (max(1, rect.width), max(1, rect.height)), False)
        if sprite is None:
            return False
        draw_sprite = sprite
        clamped_alpha = max(0, min(255, int(alpha)))
        if clamped_alpha < 255:
            draw_sprite = sprite.copy()
            draw_sprite.set_alpha(clamped_alpha)
        surface.blit(draw_sprite, rect.topleft)
        return True


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
