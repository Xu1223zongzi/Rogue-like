from __future__ import annotations

import pygame

from game.config import ACCENT_COLOR, MUTED_TEXT, PANEL_BORDER, PANEL_COLOR, TEXT_COLOR, WINDOW_HEIGHT, WINDOW_WIDTH
from game.core.scene import Scene
from game.scenes.loading_scene import LoadingScene


class TitleScene(Scene):
    def update(self, delta_time: float) -> None:
        del delta_time
        if self.app.input.consume_action("confirm"):
            self.app.scene_manager.switch_to(LoadingScene(self.app))

    def render(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(0, 0, 760, 440)
        panel.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=20)
        pygame.draw.rect(surface, PANEL_BORDER, panel, width=2, border_radius=20)

        title = self.app.get_font(42, bold=True).render("迷宫竞速", True, TEXT_COLOR)
        subtitle = self.app.get_font(24).render("装备、理智与分支地图的测试版本", True, MUTED_TEXT)
        prompt = self.app.get_font(28, bold=True).render("按 Enter 开始", True, ACCENT_COLOR)

        surface.blit(title, title.get_rect(center=(panel.centerx, panel.top + 82)))
        surface.blit(subtitle, subtitle.get_rect(center=(panel.centerx, panel.top + 134)))
        surface.blit(prompt, prompt.get_rect(center=(panel.centerx, panel.top + 208)))

        lines = [
            "移动：A / D 或 左右方向键",
            "跳跃：W / 上方向键 / 空格",
            "攻击：J 或 鼠标左键",
            "冲刺：Shift  |  交互：E  |  Tab",
            "心脏：Q  |  脑：R  |  左眼：U  |  右眼：I",
        ]
        font = self.app.get_font(20)
        for index, line in enumerate(lines):
            text = font.render(line, True, TEXT_COLOR)
            surface.blit(text, text.get_rect(center=(panel.centerx, panel.top + 290 + index * 30)))