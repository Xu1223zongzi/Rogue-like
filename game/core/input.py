from __future__ import annotations

from collections.abc import Iterable

import pygame


ACTION_BINDINGS = {
    "move_left": {"keys": (pygame.K_a, pygame.K_LEFT)},
    "move_right": {"keys": (pygame.K_d, pygame.K_RIGHT)},
    "move_up": {"keys": (pygame.K_w, pygame.K_UP)},
    "move_down": {"keys": (pygame.K_s, pygame.K_DOWN)},
    "jump": {"keys": (pygame.K_w, pygame.K_UP, pygame.K_SPACE)},
    "attack": {"keys": (pygame.K_j,), "mouse": (1,)},
    "block": {"keys": (pygame.K_k,), "mouse": (3,)},
    "dash": {"keys": (pygame.K_LSHIFT, pygame.K_RSHIFT)},
    "interact": {"keys": (pygame.K_e,)},
    "ultimate": {"keys": (pygame.K_q,)},
    "brain_skill": {"keys": (pygame.K_r,)},
    "skill_left": {"keys": (pygame.K_u,)},
    "skill_right": {"keys": (pygame.K_i,)},
    "minor_skill": {"keys": (pygame.K_l,)},
    "map_toggle": {"keys": (pygame.K_m,)},
    "map_zoom_out": {"keys": (pygame.K_q,)},
    "map_zoom_in": {"keys": (pygame.K_e,)},
    "teleport_confirm": {"keys": (pygame.K_SPACE,)},
    "inventory": {"keys": (pygame.K_TAB,)},
    "refresh_map": {"keys": (pygame.K_p,)},
    "confirm": {"keys": (pygame.K_RETURN,)},
    "pause": {"keys": (pygame.K_ESCAPE,)},
}

ACTION_BUFFER_TIMES = {
    "move_up": 0.14,
    "jump": 0.14,
    "attack": 0.18,
    "block": 0.18,
    "dash": 0.16,
    "interact": 0.18,
    "ultimate": 0.18,
    "brain_skill": 0.18,
    "skill_left": 0.18,
    "skill_right": 0.18,
    "minor_skill": 0.18,
    "map_toggle": 0.20,
    "map_zoom_out": 0.18,
    "map_zoom_in": 0.18,
    "teleport_confirm": 0.18,
    "inventory": 0.18,
    "refresh_map": 0.20,
    "confirm": 0.20,
    "pause": 0.20,
}


class InputState:
    def __init__(self) -> None:
        self.pressed_keys: set[int] = set()
        self.just_released_keys: set[int] = set()
        self.pressed_mouse: set[int] = set()
        self.action_timers: dict[str, float] = {action: 0.0 for action in ACTION_BINDINGS}

    def begin_frame(self) -> None:
        self.just_released_keys.clear()

    def advance_time(self, delta_time: float) -> None:
        for action, timer in self.action_timers.items():
            self.action_timers[action] = max(0.0, timer - delta_time)

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key not in self.pressed_keys:
                self._buffer_actions_for_key(event.key)
            self.pressed_keys.add(event.key)
        elif event.type == pygame.KEYUP:
            self.pressed_keys.discard(event.key)
            self.just_released_keys.add(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button not in self.pressed_mouse:
                self._buffer_actions_for_mouse(event.button)
            self.pressed_mouse.add(event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed_mouse.discard(event.button)

    def is_pressed(self, action: str) -> bool:
        return self._matches(action, self.pressed_keys, self.pressed_mouse)

    def is_just_pressed(self, action: str) -> bool:
        return self.action_timers.get(action, 0.0) > 0.0

    def consume_action(self, action: str) -> bool:
        if self.action_timers.get(action, 0.0) <= 0.0:
            return False
        self.action_timers[action] = 0.0
        return True

    def movement_axis(self) -> float:
        return float(self.is_pressed("move_right")) - float(self.is_pressed("move_left"))

    def jump_released(self) -> bool:
        binding = ACTION_BINDINGS["jump"]
        return any(key in self.just_released_keys for key in binding.get("keys", ()))

    def _matches(self, action: str, keys: Iterable[int], mouse: Iterable[int]) -> bool:
        binding = ACTION_BINDINGS.get(action, {})
        return any(key in keys for key in binding.get("keys", ())) or any(button in mouse for button in binding.get("mouse", ()))

    def _buffer_actions_for_key(self, key: int) -> None:
        for action, binding in ACTION_BINDINGS.items():
            if key in binding.get("keys", ()):
                self._buffer_action(action)

    def _buffer_actions_for_mouse(self, button: int) -> None:
        for action, binding in ACTION_BINDINGS.items():
            if button in binding.get("mouse", ()):
                self._buffer_action(action)

    def _buffer_action(self, action: str) -> None:
        duration = ACTION_BUFFER_TIMES.get(action, 0.12)
        self.action_timers[action] = max(self.action_timers.get(action, 0.0), duration)