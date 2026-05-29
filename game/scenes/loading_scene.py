from __future__ import annotations

import random

import pygame

from game.config import ACCENT_COLOR, MUTED_TEXT, PANEL_BORDER, PANEL_COLOR, TEXT_COLOR, WINDOW_HEIGHT, WINDOW_WIDTH
from game.core.scene import Scene
from game.rendering import draw_ui_panel_box


class LoadingScene(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.ready_to_boot = False
        self.run_seed = random.randrange(1, 999_999_999)

    def update(self, delta_time: float) -> None:
        del delta_time
        if not self.ready_to_boot:
            self.ready_to_boot = True
            return

        from game.scenes.gameplay_scene import GameplayScene

        self.app.scene_manager.switch_to(GameplayScene(self.app, seed=self.run_seed))

    def render(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(0, 0, 480, 220)
        panel.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        draw_ui_panel_box(self.app, surface, "loading_panel", panel, PANEL_COLOR, PANEL_BORDER, border_radius=18)

        title = self.app.get_font(30, bold=True).render("Loading Room", True, TEXT_COLOR)
        subtitle = self.app.get_font(20).render("Preparing loadout slots, pickups, sanity, and camera state...", True, MUTED_TEXT)
        seed_text = self.app.get_font(20).render(f"Seed {self.run_seed}", True, TEXT_COLOR)
        prompt = self.app.get_font(18, bold=True).render("Please wait", True, ACCENT_COLOR)

        surface.blit(title, title.get_rect(center=(panel.centerx, panel.top + 58)))
        surface.blit(subtitle, subtitle.get_rect(center=(panel.centerx, panel.top + 100)))
        surface.blit(seed_text, seed_text.get_rect(center=(panel.centerx, panel.top + 138)))
        surface.blit(prompt, prompt.get_rect(center=(panel.centerx, panel.top + 176)))