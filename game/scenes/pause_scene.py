from __future__ import annotations

import pygame

from game.config import ACCENT_COLOR, PANEL_BORDER, PANEL_COLOR, TEXT_COLOR, WINDOW_HEIGHT, WINDOW_WIDTH
from game.core.scene import Scene


class PauseScene(Scene):
    blocks_lower_render = False

    def update(self, delta_time: float) -> None:
        del delta_time
        if self.app.input.consume_action("pause"):
            self.app.scene_manager.pop()
            return
        if self.app.input.consume_action("confirm"):
            self.app.running = False

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((7, 10, 15, 165))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, 420, 210)
        panel.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=16)
        pygame.draw.rect(surface, PANEL_BORDER, panel, width=2, border_radius=16)

        title = self.app.get_font(34, bold=True).render("已暂停", True, TEXT_COLOR)
        line = self.app.get_font(22).render("按 Esc 返回游戏", True, ACCENT_COLOR)
        exit_line = self.app.get_font(20).render("按 Enter 退出游戏", True, TEXT_COLOR)
        surface.blit(title, title.get_rect(center=(panel.centerx, panel.top + 70)))
        surface.blit(line, line.get_rect(center=(panel.centerx, panel.top + 122)))
        surface.blit(exit_line, exit_line.get_rect(center=(panel.centerx, panel.top + 156)))