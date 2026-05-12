from __future__ import annotations

from pathlib import Path

import pygame

from .audio import CombatAudio
from .config import BACKGROUND_BOTTOM, DISPLAY_HEIGHT, DISPLAY_WIDTH, FIXED_TIME_STEP, MAX_FRAME_TIME, TARGET_FPS, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from .core.input import InputState
from .core.scene import SceneManager
from .scenes.title_scene import TitleScene


class GameApp:
    def __init__(self) -> None:
        pygame.mixer.pre_init(44100, -16, 2, 256)
        pygame.init()
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
        except pygame.error:
            pass
        pygame.display.set_caption(WINDOW_TITLE)
        display_size = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
        display_flags = pygame.FULLSCREEN | pygame.SCALED
        try:
            self.screen = pygame.display.set_mode(display_size, display_flags, vsync=1)
        except TypeError:
            try:
                self.screen = pygame.display.set_mode(display_size, display_flags)
            except pygame.error:
                self.screen = pygame.display.set_mode(display_size, pygame.FULLSCREEN)
        except pygame.error:
            try:
                self.screen = pygame.display.set_mode(display_size, pygame.FULLSCREEN, vsync=1)
            except (TypeError, pygame.error):
                self.screen = pygame.display.set_mode(display_size, pygame.FULLSCREEN)
        self.render_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)).convert()
        self.clock = pygame.time.Clock()
        self.input = InputState()
        self.scene_manager = SceneManager(self)
        self.running = True
        self.font_cache: dict[tuple[int, bool], pygame.font.Font] = {}
        self.audio = CombatAudio()

        self.scene_manager.switch_to(TitleScene(self))

    def get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in self.font_cache:
            self.font_cache[key] = self._build_font(size, bold)
        return self.font_cache[key]

    def _build_font(self, size: int, bold: bool) -> pygame.font.Font:
        candidate_paths = [
            Path("C:/Windows/Fonts/msyh.ttc"),
            Path("C:/Windows/Fonts/msyhbd.ttc") if bold else Path("C:/Windows/Fonts/msyh.ttc"),
            Path("C:/Windows/Fonts/simhei.ttf"),
            Path("C:/Windows/Fonts/simsun.ttc"),
        ]
        for font_path in candidate_paths:
            if font_path.exists():
                return pygame.font.Font(str(font_path), size)

        font_name = pygame.font.match_font(["microsoftyahei", "simhei", "notosanssc", "arialunicodems", "consolas"], bold=bold)
        if font_name is not None:
            return pygame.font.Font(font_name, size)
        return pygame.font.SysFont("arial", size, bold=bold)

    def draw_background(self) -> None:
        self.render_surface.fill(BACKGROUND_BOTTOM)

    def present(self) -> None:
        if self.screen.get_size() == self.render_surface.get_size():
            self.screen.blit(self.render_surface, (0, 0))
            return
        if self.screen.get_width() == self.render_surface.get_width() * 2 and self.screen.get_height() == self.render_surface.get_height() * 2:
            scaled = pygame.transform.scale2x(self.render_surface)
        else:
            scaled = pygame.transform.smoothscale(self.render_surface, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))

    def run(self) -> None:
        accumulator = 0.0

        while self.running:
            frame_time = min(self.clock.tick(TARGET_FPS) / 1000.0, MAX_FRAME_TIME)
            accumulator += frame_time
            self.input.advance_time(frame_time)
            self.input.begin_frame()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                self.input.process_event(event)
                self.scene_manager.handle_event(event)

            while self.running and accumulator >= FIXED_TIME_STEP:
                self.scene_manager.update(FIXED_TIME_STEP)
                accumulator -= FIXED_TIME_STEP

            self.draw_background()
            self.scene_manager.render(self.render_surface)
            self.present()
            pygame.display.flip()

        pygame.quit()