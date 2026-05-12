from __future__ import annotations

import pygame


class Scene:
    blocks_lower_render = True

    def __init__(self, app) -> None:
        self.app = app

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, delta_time: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pass


class SceneManager:
    def __init__(self, app) -> None:
        self.app = app
        self._stack: list[Scene] = []

    @property
    def current(self) -> Scene | None:
        return self._stack[-1] if self._stack else None

    def switch_to(self, scene: Scene) -> None:
        while self._stack:
            self._stack.pop().exit()
        self._stack.append(scene)
        scene.enter()

    def push(self, scene: Scene) -> None:
        self._stack.append(scene)
        scene.enter()

    def pop(self) -> None:
        if not self._stack:
            return
        self._stack.pop().exit()
        if not self._stack:
            self.app.running = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.current is not None:
            self.current.handle_event(event)

    def update(self, delta_time: float) -> None:
        if self.current is not None:
            self.current.update(delta_time)

    def render(self, surface: pygame.Surface) -> None:
        if not self._stack:
            return

        start_index = len(self._stack) - 1
        while start_index > 0 and not self._stack[start_index].blocks_lower_render:
            start_index -= 1

        for scene in self._stack[start_index:]:
            scene.render(surface)