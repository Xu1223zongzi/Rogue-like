from __future__ import annotations

from dataclasses import dataclass, field
import random

import pygame

from game.config import (
    ENEMY_ATTACK_ACTIVE,
    ENEMY_ATTACK_HEIGHT,
    ENEMY_ATTACK_RANGE,
    ENEMY_ATTACK_RECOVERY,
    ENEMY_ATTACK_WIDTH,
    ENEMY_ATTACK_WINDUP,
    ENEMY_CHASE_SPEED,
    ENEMY_CLOSE_NOTICE_RANGE,
    ENEMY_COLOR,
    ENEMY_DETECTION_RANGE,
    ENEMY_GRAVITY,
    ENEMY_HEIGHT,
    ENEMY_HIT_COLOR,
    ENEMY_HURT_STUN,
    ENEMY_IFRAMES,
    ENEMY_MEMORY_TIME,
    ENEMY_MAX_FALL_SPEED,
    ENEMY_MAX_HEALTH,
    ENEMY_MOVE_SPEED,
    ENEMY_TOUCH_DAMAGE,
    ENEMY_TOUCH_COOLDOWN,
    ENEMY_VIEW_ANGLE_DOT,
    ENEMY_VIEW_VERTICAL_RANGE,
    ENEMY_WIDTH,
    PLAYER_ATTACK_ACTIVE,
    PLAYER_ATTACK_BUFFER,
    PLAYER_ATTACK_COOLDOWN,
    PLAYER_ATTACK_DAMAGE,
    PLAYER_ATTACK_HEIGHT,
    PLAYER_ATTACK_REACH_EXTENSION,
    PLAYER_ATTACK_RECOVERY,
    PLAYER_ATTACK_STARTUP,
    PLAYER_ATTACK_WIDTH,
    PLAYER_BLOCK_BUFFER,
    PLAYER_BLOCK_COOLDOWN,
    PLAYER_BLOCK_TIME,
    PLAYER_COLOR,
    PLAYER_COYOTE_TIME,
    PLAYER_DASH_BUFFER,
    PLAYER_DASH_COOLDOWN,
    PLAYER_DASH_SPEED,
    PLAYER_DASH_TIME,
    PLAYER_GRAVITY,
    PLAYER_HEIGHT,
    PLAYER_HIT_COLOR,
    PLAYER_HURT_STUN,
    PLAYER_IFRAMES,
    PLAYER_JUMP_BUFFER,
    PLAYER_JUMP_SPEED,
    PLAYER_MAX_FALL_SPEED,
    PLAYER_MAX_HEALTH,
    TILE_SIZE,
    PLAYER_MAX_SPEED,
    PLAYER_MOVE_ACCEL,
    PLAYER_MOVE_DECEL,
    PLAYER_PARRY_INVULN,
    PLAYER_BASE_DEFENSE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    PLAYER_WIDTH,
)


Vec2 = pygame.Vector2

PARRY_WINDOW = 0.100
GUARD_RECOVERY = 0.16
DASH_STRIKE_DAMAGE = 28
DASH_STRIKE_HIT_COOLDOWN = 0.55
DASH_STRIKE_EXTEND_TIME = 0.06
BOSS_BLOCK_REDUCTION = 0.60
BOSS_DAMAGE_REMAINDER = 1.0 - BOSS_BLOCK_REDUCTION
BOSS_PERFECT_AVOID_TIME = 0.24
ANIMAL_SUMMON_JUMP_SPEED = PLAYER_JUMP_SPEED * 0.84
ANIMAL_SUMMON_JUMP_COOLDOWN = 0.38
ANIMAL_SUMMON_JUMP_SUMMON_GRACE = 0.28
ANIMAL_SUMMON_TELEPORT_COOLDOWN = 0.85
ANIMAL_SUMMON_TELEPORT_DISTANCE_X = WINDOW_WIDTH * 0.58
ANIMAL_SUMMON_TELEPORT_DISTANCE_Y = WINDOW_HEIGHT * 0.72
ANIMAL_SUMMON_PLATFORM_SCAN_HEIGHT = TILE_SIZE * 5.0
ANIMAL_SUMMON_PLATFORM_JUMP_MIN_TIME = 0.22
ANIMAL_SUMMON_PLATFORM_JUMP_MAX_TIME = 0.42
ANIMAL_SUMMON_PLATFORM_JUMP_ARC = 42.0
ANIMAL_SUMMON_AGGRO_RANGE = 190.0
ANIMAL_SUMMON_AGGRO_VERTICAL_RANGE = 150.0

ALLY_ELITE_JUMP_SPEED = ANIMAL_SUMMON_JUMP_SPEED
ALLY_ELITE_JUMP_COOLDOWN = ANIMAL_SUMMON_JUMP_COOLDOWN
ALLY_ELITE_JUMP_SUMMON_GRACE = ANIMAL_SUMMON_JUMP_SUMMON_GRACE
ALLY_ELITE_TELEPORT_COOLDOWN = ANIMAL_SUMMON_TELEPORT_COOLDOWN
ALLY_ELITE_TELEPORT_DISTANCE_X = ANIMAL_SUMMON_TELEPORT_DISTANCE_X
ALLY_ELITE_TELEPORT_DISTANCE_Y = ANIMAL_SUMMON_TELEPORT_DISTANCE_Y
ALLY_ELITE_PLATFORM_SCAN_HEIGHT = ANIMAL_SUMMON_PLATFORM_SCAN_HEIGHT
ALLY_ELITE_PLATFORM_JUMP_MIN_TIME = ANIMAL_SUMMON_PLATFORM_JUMP_MIN_TIME
ALLY_ELITE_PLATFORM_JUMP_MAX_TIME = ANIMAL_SUMMON_PLATFORM_JUMP_MAX_TIME
ALLY_ELITE_PLATFORM_JUMP_ARC = ANIMAL_SUMMON_PLATFORM_JUMP_ARC

ATTACK_PROFILES = {
    "jab": {
        "range": ENEMY_ATTACK_RANGE - 14.0,
        "width": ENEMY_ATTACK_WIDTH - 16.0,
        "height": ENEMY_ATTACK_HEIGHT - 2.0,
        "windup": ENEMY_ATTACK_WINDUP * 0.72,
        "active": ENEMY_ATTACK_ACTIVE * 0.70,
        "recovery": ENEMY_ATTACK_RECOVERY * 0.78,
        "damage": ENEMY_TOUCH_DAMAGE,
        "drive_speed": 0.0,
        "radius": 0.0,
    },
    "cleave": {
        "range": ENEMY_ATTACK_RANGE + 1.0,
        "width": ENEMY_ATTACK_WIDTH + 2.0,
        "height": ENEMY_ATTACK_HEIGHT + 8.0,
        "windup": ENEMY_ATTACK_WINDUP,
        "active": ENEMY_ATTACK_ACTIVE,
        "recovery": ENEMY_ATTACK_RECOVERY,
        "damage": ENEMY_TOUCH_DAMAGE + 4,
        "drive_speed": 0.0,
        "radius": 0.0,
    },
    "lunge": {
        "range": ENEMY_ATTACK_RANGE + 14.0,
        "width": ENEMY_ATTACK_WIDTH + 8.0,
        "height": ENEMY_ATTACK_HEIGHT,
        "windup": ENEMY_ATTACK_WINDUP * 1.15,
        "active": ENEMY_ATTACK_ACTIVE * 0.95,
        "recovery": ENEMY_ATTACK_RECOVERY * 1.20,
        "damage": ENEMY_TOUCH_DAMAGE + 6,
        "drive_speed": 240.0,
        "radius": 0.0,
    },
    "shot": {
        "range": 220.0,
        "width": 160.0,
        "height": 28.0,
        "windup": ENEMY_ATTACK_WINDUP * 1.20,
        "active": 0.08,
        "recovery": ENEMY_ATTACK_RECOVERY * 1.25,
        "damage": ENEMY_TOUCH_DAMAGE - 1,
        "drive_speed": 0.0,
        "radius": 9.0,
    },
    "rift": {
        "range": ENEMY_ATTACK_RANGE - 24.0,
        "width": ENEMY_ATTACK_WIDTH - 6.0,
        "height": ENEMY_ATTACK_HEIGHT + 26.0,
        "windup": ENEMY_ATTACK_WINDUP * 0.68,
        "active": ENEMY_ATTACK_ACTIVE * 0.98,
        "recovery": ENEMY_ATTACK_RECOVERY * 0.92,
        "damage": ENEMY_TOUCH_DAMAGE - 4,
        "drive_speed": 0.0,
        "radius": 0.0,
    },
}

ENEMY_ARCHETYPES = {
    "blade": {
        "label": "Blade Guard",
        "weapon": "blade",
        "body_color": (172, 88, 92),
        "detail_color": (232, 200, 118),
        "weapon_color": (218, 224, 232),
        "health": ENEMY_MAX_HEALTH,
        "move_speed": ENEMY_MOVE_SPEED,
        "chase_speed": ENEMY_CHASE_SPEED,
        "detection": ENEMY_DETECTION_RANGE,
        "preferred_range": ENEMY_ATTACK_RANGE,
        "allowed_profiles": ("jab", "cleave"),
        "ranged": False,
        "view_distance": 180.0,
        "view_spread": 110.0,
        "view_angle_dot": 0.10,
    },
    "lancer": {
        "label": "Lance Warden",
        "weapon": "lance",
        "body_color": (112, 128, 186),
        "detail_color": (244, 180, 118),
        "weapon_color": (232, 236, 241),
        "health": ENEMY_MAX_HEALTH + 10,
        "move_speed": ENEMY_MOVE_SPEED - 8.0,
        "chase_speed": ENEMY_CHASE_SPEED - 4.0,
        "detection": ENEMY_DETECTION_RANGE + 22.0,
        "preferred_range": ENEMY_ATTACK_RANGE + 28.0,
        "allowed_profiles": ("lunge", "cleave"),
        "ranged": False,
        "view_distance": 220.0,
        "view_spread": 74.0,
        "view_angle_dot": 0.34,
    },
    "archer": {
        "label": "Talon Archer",
        "weapon": "bow",
        "body_color": (86, 140, 114),
        "detail_color": (214, 238, 192),
        "weapon_color": (201, 169, 104),
        "health": ENEMY_MAX_HEALTH - 10,
        "move_speed": ENEMY_MOVE_SPEED - 18.0,
        "chase_speed": ENEMY_CHASE_SPEED - 28.0,
        "detection": ENEMY_DETECTION_RANGE + 54.0,
        "preferred_range": 180.0,
        "allowed_profiles": ("shot",),
        "ranged": True,
        "view_distance": 270.0,
        "view_spread": 52.0,
        "view_angle_dot": 0.48,
        "width": ENEMY_WIDTH,
        "height": ENEMY_HEIGHT,
    },
    "elite_knight": {
        "label": "Bound Elite",
        "weapon": "relic",
        "body_color": (128, 110, 188),
        "detail_color": (244, 214, 142),
        "weapon_color": (214, 236, 248),
        "health": (ENEMY_MAX_HEALTH * 7) // 2,
        "move_speed": PLAYER_MAX_SPEED - 24.0,
        "chase_speed": PLAYER_MAX_SPEED - 8.0,
        "detection": ENEMY_DETECTION_RANGE + 46.0,
        "preferred_range": 176.0,
        "allowed_profiles": ("shot", "lunge", "cleave"),
        "ranged": False,
        "view_distance": 260.0,
        "view_spread": 88.0,
        "view_angle_dot": 0.18,
        "width": ENEMY_WIDTH + 6,
        "height": ENEMY_HEIGHT + 8,
    },
    "boss": {
        "label": "Reliquary Warden",
        "weapon": "greatblade",
        "body_color": (148, 82, 122),
        "detail_color": (241, 214, 148),
        "weapon_color": (239, 242, 248),
        "health": ENEMY_MAX_HEALTH * 7,
        "move_speed": ENEMY_MOVE_SPEED - 4.0,
        "chase_speed": ENEMY_CHASE_SPEED + 30.0,
        "detection": 99999.0,
        "preferred_range": ENEMY_ATTACK_RANGE * 3.6,
        "allowed_profiles": ("lunge", "cleave", "jab", "rift"),
        "ranged": False,
        "view_distance": 99999.0,
        "view_spread": 1200.0,
        "view_angle_dot": -1.0,
        "width": ENEMY_WIDTH + 18,
        "height": ENEMY_HEIGHT + 26,
    },
}


def move_toward(current: float, target: float, delta: float) -> float:
    if current < target:
        return min(target, current + delta)
    return max(target, current - delta)


@dataclass
class PhysicsActor:
    rect: pygame.FRect
    velocity: Vec2 = field(default_factory=Vec2)
    on_ground: bool = False
    drop_through_timer: float = 0.0
    facing: int = 1
    health: int = 1
    max_health: int = 1
    invulnerability: float = 0.0
    flash_timer: float = 0.0
    movement_state: str = "idle"
    action_state: str = "neutral"

    @property
    def state(self) -> str:
        return self.action_state if self.action_state != "neutral" else self.movement_state

    def tick_timers(self, delta_time: float) -> None:
        self.invulnerability = max(0.0, self.invulnerability - delta_time)
        self.flash_timer = max(0.0, self.flash_timer - delta_time)
        self.drop_through_timer = max(0.0, self.drop_through_timer - delta_time)

    def center(self) -> Vec2:
        return Vec2(self.rect.centerx, self.rect.centery)

    def current_color(self, normal: tuple[int, int, int], hit: tuple[int, int, int]) -> tuple[int, int, int]:
        return hit if self.flash_timer > 0.0 else normal

    def take_damage(self, amount: int, invuln: float, ignore_invulnerability: bool = False) -> bool:
        if (self.invulnerability > 0.0 and not ignore_invulnerability) or self.health <= 0:
            return False
        self.health = max(0, self.health - amount)
        self.invulnerability = invuln
        self.flash_timer = 0.14
        return True

    @property
    def alive(self) -> bool:
        return self.health > 0


@dataclass
class EnemyProjectileSpawn:
    position: Vec2
    velocity: Vec2
    damage: int
    radius: float
    tint: tuple[int, int, int]
    source_enemy: "Enemy"


@dataclass
class PlayerUpdateResult:
    attack_became_active: bool = False
    dash_started: bool = False
    block_started: bool = False


@dataclass
class EnemyUpdateResult:
    damage: int = 0
    parried: bool = False
    guarded: bool = False
    attack_started: bool = False
    attack_profile: str = ""
    projectile_spawn: EnemyProjectileSpawn | None = None


@dataclass
class Player(PhysicsActor):
    attack_request_timer: float = 0.0
    attack_startup_timer: float = 0.0
    attack_timer: float = 0.0
    attack_recovery_timer: float = 0.0
    attack_cooldown: float = 0.0
    block_request_timer: float = 0.0
    block_timer: float = 0.0
    block_cooldown: float = 0.0
    guard_timer: float = 0.0
    parry_timer: float = 0.0
    jump_buffer: float = 0.0
    coyote_timer: float = 0.0
    dash_request_timer: float = 0.0
    dash_direction: int = 1
    dash_timer: float = 0.0
    dash_cooldown: float = 0.0
    hurt_timer: float = 0.0
    empowered_dash_timer: float = 0.0
    defense_multiplier: float = PLAYER_BASE_DEFENSE
    attack_speed_multiplier: float = 1.0
    attack_damage_bonus: int = 0
    attack_reach_multiplier: float = 1.0
    move_speed_multiplier: float = 1.0
    dash_locked: bool = False
    forced_move_speed: float = 0.0
    jump_multiplier: float = 1.0
    can_block: bool = False
    temporary_shield: int = 0
    shield_timer: float = 0.0
    death_ward_available: bool = False
    last_damage_taken: int = 0
    perfect_avoid_timer: float = 0.0
    boss_rift_bait_timer: float = 0.0
    boss_rift_bait_chance: float = 0.0
    boss_rift_bait_retry_timer: float = 0.0
    halo_barrier_hit_count: int = 0
    halo_barrier_timer: float = 0.0
    halo_barrier_radius: float = 0.0
    remaining_air_jumps: int = 1

    def __init__(self, position: Vec2) -> None:
        super().__init__(pygame.FRect(position.x, position.y, PLAYER_WIDTH, PLAYER_HEIGHT))
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.movement_state = "idle"
        self.action_state = "neutral"
        self.remaining_air_jumps = 1

    def request_jump(self) -> None:
        self.jump_buffer = PLAYER_JUMP_BUFFER

    def request_drop_through(self) -> None:
        self.drop_through_timer = max(self.drop_through_timer, 0.18)
        self.on_ground = False
        self.coyote_timer = 0.0
        self.rect.y += 8

    def queue_attack(self) -> None:
        self.attack_request_timer = PLAYER_ATTACK_BUFFER

    def queue_dash(self) -> None:
        self.dash_request_timer = PLAYER_DASH_BUFFER

    def queue_block(self) -> None:
        if not self.can_block:
            return
        self.block_request_timer = PLAYER_BLOCK_BUFFER

    def start_attack(self) -> bool:
        if not self.alive:
            return False
        if self.hurt_timer > 0.0 or self.dash_timer > 0.0 or self.block_timer > 0.0:
            return False
        if self.attack_cooldown > 0.0 or self.attack_startup_timer > 0.0 or self.attack_timer > 0.0 or self.attack_recovery_timer > 0.0:
            return False

        speed_scale = max(0.35, self.attack_speed_multiplier)
        self.attack_startup_timer = PLAYER_ATTACK_STARTUP / speed_scale
        self.attack_cooldown = PLAYER_ATTACK_COOLDOWN / speed_scale
        self.velocity.x *= 0.55
        self.action_state = "attack"
        return True

    def start_block(self) -> bool:
        if not self.alive:
            return False
        if not self.can_block:
            return False
        if self.hurt_timer > 0.0 or self.dash_timer > 0.0 or self.is_attack_locked():
            return False
        if self.block_cooldown > 0.0 or self.block_timer > 0.0:
            return False

        self.block_timer = PLAYER_BLOCK_TIME
        self.block_cooldown = PLAYER_BLOCK_COOLDOWN
        self.velocity.x *= 0.15
        self.action_state = "block"
        return True

    def begin_empowered_dash(self) -> None:
        self.empowered_dash_timer = max(self.empowered_dash_timer, self.dash_timer)

    def sustain_empowered_dash(self) -> None:
        self.empowered_dash_timer = max(self.empowered_dash_timer, self.dash_timer)
        self.dash_timer = max(self.dash_timer, DASH_STRIKE_EXTEND_TIME)

    def is_empowered_dash_active(self) -> bool:
        return self.empowered_dash_timer > 0.0 and self.dash_timer > 0.0

    def is_attack_locked(self) -> bool:
        return self.attack_startup_timer > 0.0 or self.attack_timer > 0.0 or self.attack_recovery_timer > 0.0

    def try_guard(self, attacker_x: float) -> str | None:
        if self.block_timer <= 0.0 or not self.alive:
            return None

        incoming_direction = 1 if attacker_x >= self.rect.centerx else -1
        if incoming_direction != self.facing:
            return None

        if self.block_timer >= PLAYER_BLOCK_TIME - PARRY_WINDOW:
            self.block_timer = 0.0
            self.parry_timer = 0.18
            self.invulnerability = max(self.invulnerability, PLAYER_PARRY_INVULN)
            self.action_state = "parry"
            return "parry"

        self.block_timer = 0.0
        self.guard_timer = GUARD_RECOVERY
        self.invulnerability = max(self.invulnerability, GUARD_RECOVERY)
        self.action_state = "guard"
        return "guard"

    def mark_perfect_avoid(self) -> None:
        self.perfect_avoid_timer = max(self.perfect_avoid_timer, BOSS_PERFECT_AVOID_TIME)

    def has_perfect_avoid(self) -> bool:
        return self.perfect_avoid_timer > 0.0

    def take_damage(self, amount: int, invuln: float, ignore_invulnerability: bool = False, true_damage: bool = False) -> bool:
        self.last_damage_taken = 0
        effective_amount = max(1, int(amount if true_damage else round(amount / max(0.25, self.defense_multiplier))))
        if self.temporary_shield > 0:
            absorbed = min(self.temporary_shield, effective_amount)
            self.temporary_shield -= absorbed
            effective_amount -= absorbed
            if self.temporary_shield <= 0:
                self.shield_timer = 0.0
        if effective_amount <= 0:
            self.invulnerability = max(self.invulnerability, invuln * 0.5)
            return False

        if self.death_ward_available and self.health - effective_amount <= 0:
            self.health = 1
            self.death_ward_available = False
            self.invulnerability = max(self.invulnerability, invuln)
            self.flash_timer = 0.2
            self.hurt_timer = PLAYER_HURT_STUN * 0.6
            self.last_damage_taken = effective_amount
            self.action_state = "hurt"
            return True

        took_damage = super().take_damage(effective_amount, invuln, ignore_invulnerability)
        if not took_damage:
            return False

        self.last_damage_taken = effective_amount
        if self.has_halo_barrier():
            self.halo_barrier_hit_count += 1
            if self.halo_barrier_hit_count >= 2:
                self.prime_boss_rift_bait(1.0, duration=max(self.halo_barrier_timer, 0.9))

        if self.alive:
            self.hurt_timer = PLAYER_HURT_STUN
            self.attack_startup_timer = 0.0
            self.attack_timer = 0.0
            self.attack_recovery_timer = 0.0
            self.block_timer = 0.0
            self.guard_timer = 0.0
            self.parry_timer = 0.0
            self.action_state = "hurt"
        else:
            self.action_state = "dead"
        return True

    def tear_barrier(self) -> bool:
        had_barrier = self.temporary_shield > 0 or self.shield_timer > 0.0
        self.temporary_shield = 0
        self.shield_timer = 0.0
        return had_barrier

    def set_halo_barrier(self, radius: float, duration: float) -> None:
        if self.halo_barrier_timer <= 0.0:
            self.halo_barrier_hit_count = 0
        self.halo_barrier_radius = max(self.halo_barrier_radius, radius)
        self.halo_barrier_timer = max(self.halo_barrier_timer, duration)

    def clear_halo_barrier(self) -> None:
        self.halo_barrier_hit_count = 0
        self.halo_barrier_timer = 0.0
        self.halo_barrier_radius = 0.0

    def has_halo_barrier(self) -> bool:
        return self.halo_barrier_timer > 0.0 and self.halo_barrier_radius > 0.0

    def prime_boss_rift_bait(self, chance: float, duration: float = 0.9) -> None:
        self.boss_rift_bait_timer = max(self.boss_rift_bait_timer, duration)
        self.boss_rift_bait_chance = max(self.boss_rift_bait_chance, chance)
        self.boss_rift_bait_retry_timer = 0.0

    def has_boss_rift_bait(self) -> bool:
        return self.boss_rift_bait_timer > 0.0 and self.boss_rift_bait_chance > 0.0

    def try_trigger_boss_rift_bait(self) -> bool:
        if not self.has_boss_rift_bait() or self.boss_rift_bait_retry_timer > 0.0:
            return False
        self.boss_rift_bait_retry_timer = 0.65
        if random.random() >= self.boss_rift_bait_chance:
            return False
        self.boss_rift_bait_timer = 0.0
        self.boss_rift_bait_chance = 0.0
        self.boss_rift_bait_retry_timer = 0.0
        self.halo_barrier_hit_count = 0
        return True

    def update(
        self,
        delta_time: float,
        axis: float,
        jump_held: bool,
        jump_released: bool,
        wants_dash: bool,
        wants_block: bool,
        level,
    ) -> PlayerUpdateResult:
        result = PlayerUpdateResult()
        self.tick_timers(delta_time)
        self.attack_request_timer = max(0.0, self.attack_request_timer - delta_time)
        self.attack_cooldown = max(0.0, self.attack_cooldown - delta_time)
        self.block_request_timer = max(0.0, self.block_request_timer - delta_time)
        self.block_timer = max(0.0, self.block_timer - delta_time)
        self.block_cooldown = max(0.0, self.block_cooldown - delta_time)
        self.guard_timer = max(0.0, self.guard_timer - delta_time)
        self.parry_timer = max(0.0, self.parry_timer - delta_time)
        self.perfect_avoid_timer = max(0.0, self.perfect_avoid_timer - delta_time)
        self.jump_buffer = max(0.0, self.jump_buffer - delta_time)
        self.dash_request_timer = max(0.0, self.dash_request_timer - delta_time)
        self.dash_cooldown = max(0.0, self.dash_cooldown - delta_time)
        self.hurt_timer = max(0.0, self.hurt_timer - delta_time)
        self.empowered_dash_timer = max(0.0, self.empowered_dash_timer - delta_time)
        self.shield_timer = max(0.0, self.shield_timer - delta_time)
        self.boss_rift_bait_timer = max(0.0, self.boss_rift_bait_timer - delta_time)
        self.boss_rift_bait_retry_timer = max(0.0, self.boss_rift_bait_retry_timer - delta_time)
        self.halo_barrier_timer = max(0.0, self.halo_barrier_timer - delta_time)
        if self.boss_rift_bait_timer <= 0.0:
            self.boss_rift_bait_chance = 0.0
            self.boss_rift_bait_retry_timer = 0.0
        if self.halo_barrier_timer <= 0.0:
            self.halo_barrier_hit_count = 0
            self.halo_barrier_radius = 0.0
        if self.shield_timer <= 0.0:
            self.temporary_shield = 0

        if wants_dash:
            self.queue_dash()
        if wants_block:
            self.queue_block()

        previous_attack_startup = self.attack_startup_timer
        previous_attack_active = self.attack_timer
        self.attack_startup_timer = max(0.0, self.attack_startup_timer - delta_time)
        self.attack_timer = max(0.0, self.attack_timer - delta_time)
        self.attack_recovery_timer = max(0.0, self.attack_recovery_timer - delta_time)

        if previous_attack_startup > 0.0 and self.attack_startup_timer == 0.0 and self.attack_timer == 0.0 and self.alive:
            self.attack_timer = PLAYER_ATTACK_ACTIVE / max(0.35, self.attack_speed_multiplier)
            result.attack_became_active = True
        elif previous_attack_active > 0.0 and self.attack_timer == 0.0 and self.attack_recovery_timer == 0.0 and self.alive:
            self.attack_recovery_timer = PLAYER_ATTACK_RECOVERY / max(0.35, self.attack_speed_multiplier)

        if not self.alive:
            self.velocity.x = move_toward(self.velocity.x, 0.0, PLAYER_MOVE_DECEL * delta_time)
            self.velocity.y = min(self.velocity.y + PLAYER_GRAVITY * delta_time, PLAYER_MAX_FALL_SPEED)
            level.move_actor(self, delta_time)
            self.action_state = "dead"
            self.movement_state = "idle"
            return result

        if self.on_ground:
            self.coyote_timer = PLAYER_COYOTE_TIME
            self.remaining_air_jumps = 1
        else:
            self.coyote_timer = max(0.0, self.coyote_timer - delta_time)

        if axis != 0.0:
            self.facing = 1 if axis > 0.0 else -1

        if self.block_request_timer > 0.0 and self.start_block():
            self.block_request_timer = 0.0
            result.block_started = True

        if self.attack_request_timer > 0.0 and self.start_attack():
            self.attack_request_timer = 0.0

        if self.hurt_timer > 0.0:
            target_speed = 0.0
            accel = PLAYER_MOVE_DECEL
        elif self.forced_move_speed > 0.0:
            target_speed = axis * self.forced_move_speed
            accel = PLAYER_MOVE_ACCEL
        elif self.block_timer > 0.0 or self.guard_timer > 0.0 or self.parry_timer > 0.0:
            target_speed = axis * PLAYER_MAX_SPEED * 0.18
            accel = PLAYER_MOVE_DECEL
        elif self.attack_startup_timer > 0.0 or self.attack_timer > 0.0:
            target_speed = axis * PLAYER_MAX_SPEED * 0.18
            accel = PLAYER_MOVE_DECEL
        elif self.attack_recovery_timer > 0.0:
            target_speed = axis * PLAYER_MAX_SPEED * 0.55
            accel = PLAYER_MOVE_ACCEL
        else:
            target_speed = axis * PLAYER_MAX_SPEED * self.move_speed_multiplier
            accel = PLAYER_MOVE_ACCEL if axis != 0.0 else PLAYER_MOVE_DECEL

        self.velocity.x = move_toward(self.velocity.x, target_speed, accel * delta_time)

        if not self.dash_locked and self.dash_request_timer > 0.0 and self.dash_cooldown <= 0.0 and self.hurt_timer <= 0.0 and self.block_timer <= 0.0 and not self.is_attack_locked():
            self.dash_timer = PLAYER_DASH_TIME
            self.dash_cooldown = PLAYER_DASH_COOLDOWN
            self.dash_request_timer = 0.0
            self.dash_direction = self.facing if axis == 0.0 else (1 if axis > 0.0 else -1)
            self.velocity.x = self.dash_direction * PLAYER_DASH_SPEED
            self.velocity.y = 0.0
            self.invulnerability = max(self.invulnerability, PLAYER_DASH_TIME)
            self.action_state = "dash"
            result.dash_started = True

        can_ground_jump = self.coyote_timer > 0.0
        can_air_jump = not self.on_ground and self.remaining_air_jumps > 0
        if self.jump_buffer > 0.0 and (can_ground_jump or can_air_jump) and self.hurt_timer <= 0.0 and self.block_timer <= 0.0 and self.dash_timer <= 0.0 and not self.is_attack_locked():
            self.velocity.y = -PLAYER_JUMP_SPEED * self.jump_multiplier
            self.on_ground = False
            if can_ground_jump:
                self.coyote_timer = 0.0
            else:
                self.remaining_air_jumps -= 1
            self.jump_buffer = 0.0

        if self.dash_timer > 0.0:
            self.dash_timer = max(0.0, self.dash_timer - delta_time)
            self.velocity.x = self.dash_direction * PLAYER_DASH_SPEED
            self.velocity.y = 0.0
        else:
            self.velocity.y = min(self.velocity.y + PLAYER_GRAVITY * delta_time, PLAYER_MAX_FALL_SPEED)

        level.move_actor(self, delta_time)
        self.refresh_state()
        return result

    def resolve_attack(self, enemies: list["Enemy"]) -> int:
        attack_rect = self.attack_hitbox()
        hits = 0

        for enemy in enemies:
            if not enemy.alive:
                continue
            if attack_rect.colliderect(enemy.rect) and enemy.take_damage(PLAYER_ATTACK_DAMAGE + self.attack_damage_bonus, ENEMY_IFRAMES):
                enemy.velocity.x = 180.0 * self.facing
                enemy.velocity.y = -120.0
                hits += 1

        return hits

    def refresh_state(self) -> None:
        if not self.alive:
            self.action_state = "dead"
            self.movement_state = "idle"
            return

        if self.hurt_timer > 0.0:
            self.action_state = "hurt"
        elif self.parry_timer > 0.0:
            self.action_state = "parry"
        elif self.guard_timer > 0.0:
            self.action_state = "guard"
        elif self.block_timer > 0.0:
            self.action_state = "block"
        elif self.dash_timer > 0.0:
            self.action_state = "dash"
        elif self.is_attack_locked():
            self.action_state = "attack"
        else:
            self.action_state = "neutral"

        if not self.on_ground and self.velocity.y < -10.0:
            self.movement_state = "jump"
        elif not self.on_ground:
            self.movement_state = "fall"
        elif abs(self.velocity.x) > 45.0:
            self.movement_state = "run"
        else:
            self.movement_state = "idle"

    def attack_hitbox(self) -> pygame.FRect:
        attack_width = (PLAYER_ATTACK_WIDTH + PLAYER_ATTACK_REACH_EXTENSION) * self.attack_reach_multiplier
        if self.facing > 0:
            offset_x = self.rect.right
        else:
            offset_x = self.rect.left - attack_width
        box_y = self.rect.y + (self.rect.height - PLAYER_ATTACK_HEIGHT) * 0.5
        return pygame.FRect(offset_x, box_y, attack_width, PLAYER_ATTACK_HEIGHT)


@dataclass
class Enemy(PhysicsActor):
    enemy_type: str = "blade"
    weapon_type: str = "blade"
    body_color: tuple[int, int, int] = ENEMY_COLOR
    detail_color: tuple[int, int, int] = (230, 210, 140)
    weapon_color: tuple[int, int, int] = (226, 230, 236)
    patrol_origin_x: float = 0.0
    patrol_radius: float = 96.0
    contact_cooldown: float = 0.0
    hurt_timer: float = 0.0
    patrol_timer: float = 0.0
    rest_timer: float = 0.0
    aggro_memory_timer: float = 0.0
    last_seen_position: Vec2 = field(default_factory=Vec2)
    attack_startup_timer: float = 0.0
    attack_timer: float = 0.0
    attack_recovery_timer: float = 0.0
    attack_has_hit: bool = False
    attack_profile: str = "cleave"
    rift_intent_timer: float = 0.0
    dash_hit_cooldown: float = 0.0
    base_max_health: int = 1
    move_speed: float = ENEMY_MOVE_SPEED
    chase_speed: float = ENEMY_CHASE_SPEED
    base_move_speed: float = ENEMY_MOVE_SPEED
    base_chase_speed: float = ENEMY_CHASE_SPEED
    damage_multiplier: float = 1.0
    detection_range: float = ENEMY_DETECTION_RANGE
    preferred_range: float = ENEMY_ATTACK_RANGE
    is_ranged: bool = False
    view_distance: float = ENEMY_DETECTION_RANGE
    view_spread: float = 86.0
    view_angle_dot: float = ENEMY_VIEW_ANGLE_DOT
    stun_timer: float = 0.0
    is_friendly: bool = False
    friendly_role: str = "hostile"
    halo_launch_timer: float = 0.0
    halo_launch_spin: float = 0.0
    halo_launch_origin: Vec2 = field(default_factory=Vec2)
    halo_launch_escape_radius: float = 0.0
    summon_timer: float = 0.0
    ally_jump_cooldown: float = 0.0
    ally_jump_grace_timer: float = 0.0
    ally_teleport_cooldown: float = 0.0
    ally_platform_snap_timer: float = 0.0
    ally_platform_jump_duration: float = 0.0
    ally_platform_jump_start: Vec2 | None = None
    ally_platform_target: Vec2 | None = None
    ally_platform_jump_arc: float = ALLY_ELITE_PLATFORM_JUMP_ARC

    def __init__(self, position: Vec2, enemy_type: str = "blade") -> None:
        archetype = ENEMY_ARCHETYPES.get(enemy_type, ENEMY_ARCHETYPES["blade"])
        width = archetype.get("width", ENEMY_WIDTH)
        height = archetype.get("height", ENEMY_HEIGHT)
        super().__init__(pygame.FRect(position.x, position.y - (height - ENEMY_HEIGHT), width, height))
        self.enemy_type = enemy_type if enemy_type in ENEMY_ARCHETYPES else "blade"
        self.weapon_type = archetype["weapon"]
        self.body_color = archetype["body_color"]
        self.detail_color = archetype["detail_color"]
        self.weapon_color = archetype["weapon_color"]
        self.health = archetype["health"]
        self.max_health = archetype["health"]
        self.base_max_health = archetype["health"]
        self.move_speed = archetype["move_speed"]
        self.chase_speed = archetype["chase_speed"]
        self.base_move_speed = archetype["move_speed"]
        self.base_chase_speed = archetype["chase_speed"]
        self.damage_multiplier = 1.0
        self.detection_range = archetype["detection"]
        self.preferred_range = archetype["preferred_range"]
        self.is_ranged = bool(archetype["ranged"])
        self.view_distance = archetype["view_distance"]
        self.view_spread = archetype["view_spread"]
        self.view_angle_dot = archetype["view_angle_dot"]
        self.patrol_origin_x = position.x
        self.facing = -1
        self.movement_state = "patrol"
        self.action_state = "neutral"
        self.patrol_timer = 1.1 + (int(position.x) % 70) / 100.0
        self.rest_timer = 0.0
        self.last_seen_position = self.center()
        self.attack_profile = self.pick_idle_profile()

    @property
    def is_boss(self) -> bool:
        return self.enemy_type == "boss"

    def is_summoned_ally(self) -> bool:
        return self.is_friendly and self.friendly_role == "summon"

    def is_controlled_ally(self) -> bool:
        return self.is_friendly and self.friendly_role == "controlled"

    def pick_idle_profile(self) -> str:
        profiles = ENEMY_ARCHETYPES[self.enemy_type]["allowed_profiles"]
        return profiles[int(self.rect.x // 48) % len(profiles)]

    def attack_stats(self) -> dict[str, float]:
        stats = ATTACK_PROFILES[self.attack_profile].copy()
        if self.is_boss:
            if self.attack_profile == "rift":
                stats["range"] *= 1.22
                stats["width"] *= 1.42
                stats["height"] *= 1.78
                stats["damage"] = max(50, int(stats["damage"] * 1.45))
                stats["windup"] *= 0.84
                stats["active"] *= 1.12
                stats["recovery"] *= 0.86
            else:
                stats["range"] *= 2.55
                stats["width"] *= 2.85
                stats["height"] *= 1.92
                stats["damage"] = int(stats["damage"] * 2.2)
                stats["drive_speed"] *= 1.35
                stats["windup"] *= 0.92
                stats["active"] *= 1.18
        stats["damage"] = max(1, int(stats["damage"] * self.damage_multiplier))
        return stats

    def eye_position(self) -> Vec2:
        return Vec2(self.rect.centerx, self.rect.y + self.rect.height * 0.32)

    def projectile_origin(self) -> Vec2:
        return Vec2(self.rect.centerx + self.facing * 16.0, self.rect.y + self.rect.height * 0.42)

    def can_see_player(self, player: Player, level) -> bool:
        if self.is_boss:
            return True
        to_player = player.center() - self.eye_position()
        distance = to_player.length()
        if distance <= 0.001 or distance > self.detection_range:
            return False
        if abs(to_player.y) > ENEMY_VIEW_VERTICAL_RANGE:
            return False

        if distance <= ENEMY_CLOSE_NOTICE_RANGE and level.has_line_of_sight(self.eye_position(), player.center()):
            return True

        facing_vector = Vec2(self.facing, 0.0)
        direction = to_player.normalize()
        if facing_vector.dot(direction) < self.view_angle_dot:
            return False

        return level.has_line_of_sight(self.eye_position(), player.center())

    def take_damage(self, amount: int, invuln: float, ignore_invulnerability: bool = False) -> bool:
        took_damage = super().take_damage(amount, invuln, ignore_invulnerability)
        if not took_damage:
            return False

        if self.alive:
            if self.is_boss:
                self.velocity.x *= 0.82
            else:
                self.rift_intent_timer = 0.0
                self.hurt_timer = ENEMY_HURT_STUN
                self.attack_startup_timer = 0.0
                self.attack_timer = 0.0
                self.attack_recovery_timer = 0.0
                self.attack_has_hit = False
                self.velocity.x *= 0.35
                self.action_state = "hurt"
        else:
            self.action_state = "dead"
        return True

    def on_parried(self) -> None:
        self.rift_intent_timer = 0.0
        self.attack_startup_timer = 0.0
        self.attack_timer = 0.0
        self.attack_recovery_timer = 0.0
        self.attack_has_hit = False
        self.velocity.xy = (0.0, 0.0)
        self.action_state = "stunned"
        self.movement_state = "stagger"

    def on_guarded(self, player_facing: int) -> None:
        self.rift_intent_timer = 0.0
        self.attack_startup_timer = 0.0
        self.attack_timer = 0.0
        self.attack_recovery_timer = 0.14
        self.attack_has_hit = False
        self.velocity.x = -player_facing * 120.0
        self.action_state = "recoil"
        self.movement_state = "stagger"

    def attack_hitbox(self) -> pygame.FRect:
        stats = self.attack_stats()
        width = stats["width"]
        height = stats["height"]
        body_overlap = min(self.rect.width * 0.62, width * 0.38)
        if self.facing > 0:
            offset_x = self.rect.right - body_overlap
        else:
            offset_x = self.rect.left - width + body_overlap
        box_y = self.rect.y + (self.rect.height - height) * 0.5
        return pygame.FRect(offset_x, box_y, width, height)

    def _within_attack_range(self, player: Player) -> bool:
        stats = self.attack_stats()
        delta = player.center() - self.center()
        if abs(delta.y) > 72.0:
            return False
        if abs(delta.x) > stats["range"]:
            return False
        return (delta.x >= 0.0 and self.facing > 0) or (delta.x <= 0.0 and self.facing < 0)

    def current_attack_is_ranged(self) -> bool:
        return self.is_ranged or self.attack_profile == "shot"

    def choose_attack_profile(self, player: Player) -> None:
        allowed_profiles = ENEMY_ARCHETYPES[self.enemy_type]["allowed_profiles"]
        if self.is_ranged:
            self.attack_profile = "shot"
            return

        delta_x = abs(player.center().x - self.center().x)
        if "shot" in allowed_profiles and delta_x > self.preferred_range * 1.12:
            self.attack_profile = "shot"
            return
        if self.is_boss and self.rift_intent_timer > 0.0 and player.has_halo_barrier():
            self.attack_profile = "rift"
            return
        if self.is_boss and "rift" in allowed_profiles and player.has_halo_barrier():
            barrier_distance = (player.center() - self.center()).length()
            invade_window = player.halo_barrier_radius * 1.42
            if barrier_distance <= invade_window and player.try_trigger_boss_rift_bait():
                self.rift_intent_timer = 2.4
                self.attack_profile = "rift"
                return
        if "lunge" in allowed_profiles and delta_x > ENEMY_ATTACK_RANGE + 12.0:
            self.attack_profile = "lunge"
        elif "jab" in allowed_profiles and delta_x < ENEMY_ATTACK_RANGE * 0.65:
            self.attack_profile = "jab"
        else:
            fallback_profiles = [profile for profile in allowed_profiles if profile != "rift"]
            self.attack_profile = fallback_profiles[-1] if fallback_profiles else allowed_profiles[-1]

    def _level_rect_is_clear(self, level, rect: pygame.FRect) -> bool:
        for solid in level.nearby_solids(rect):
            if rect.colliderect(solid):
                return False
        return True

    def _ally_should_teleport_to_player(self, player: Player) -> bool:
        if self.ally_teleport_cooldown > 0.0:
            return False
        delta = player.center() - self.center()
        return abs(delta.x) > ALLY_ELITE_TELEPORT_DISTANCE_X or abs(delta.y) > ALLY_ELITE_TELEPORT_DISTANCE_Y

    def _teleport_near_player(self, player: Player, level) -> bool:
        room = level.current_room
        candidate_offsets = (72.0, -72.0, 104.0, -104.0, 0.0)
        candidate_bottoms = (player.rect.bottom, player.rect.bottom - TILE_SIZE * 0.5, player.rect.bottom - TILE_SIZE)
        for offset_x in candidate_offsets:
            left = player.rect.centerx + offset_x - self.rect.width * 0.5
            left = max(0.0, min(left, room.world_width - self.rect.width))
            for bottom in candidate_bottoms:
                top = bottom - self.rect.height
                top = max(0.0, min(top, room.world_height - self.rect.height))
                candidate = pygame.FRect(left, top, self.rect.width, self.rect.height)
                if candidate.colliderect(player.rect):
                    continue
                if not self._level_rect_is_clear(level, candidate):
                    continue
                self.rect.x = candidate.x
                self.rect.y = candidate.y
                self.velocity.xy = (0.0, 0.0)
                self.on_ground = False
                self.ally_teleport_cooldown = ALLY_ELITE_TELEPORT_COOLDOWN
                self.ally_jump_cooldown = 0.0
                return True
        return False

    def _animal_summon_find_jump_landing_rect(self, destination: Vec2, level) -> pygame.FRect | None:
        if not self.on_ground or self.ally_jump_cooldown > 0.0 or self.ally_jump_grace_timer > 0.0:
            return None
        if abs(self.rect.bottom - destination.y) <= TILE_SIZE * 0.9 and abs(destination.x - self.rect.centerx) <= TILE_SIZE * 2.35:
            return None
        vertical_gap = self.rect.bottom - destination.y
        if vertical_gap < -18.0 or vertical_gap > ANIMAL_SUMMON_PLATFORM_SCAN_HEIGHT + 28.0:
            return None
        if abs(destination.x - self.rect.centerx) > TILE_SIZE * 5.4:
            return None
        horizontal_distance = abs(destination.x - self.rect.centerx)
        if horizontal_distance >= TILE_SIZE * 1.75 and abs(self.rect.bottom - destination.y) <= TILE_SIZE * 1.2 and not self._animal_summon_has_gap_between(destination.x, level):
            return None
        scan_left = min(self.rect.left, destination.x) - TILE_SIZE
        scan_top = self.rect.top - ANIMAL_SUMMON_PLATFORM_SCAN_HEIGHT
        scan_width = abs(destination.x - self.rect.centerx) + TILE_SIZE * 2
        scan_height = self.rect.height + ANIMAL_SUMMON_PLATFORM_SCAN_HEIGHT
        scan_rect = pygame.Rect(int(scan_left), int(scan_top), int(max(TILE_SIZE, scan_width)), int(max(TILE_SIZE, scan_height)))
        surfaces = level.nearby_semisolids(scan_rect) + level.nearby_solids(scan_rect)
        best_landing_rect: pygame.FRect | None = None
        best_score = float("inf")
        horizontal_trigger_range = TILE_SIZE * 5.2
        for surface in surfaces:
            surface_top = float(surface.top)
            relative_height = self.rect.bottom - surface_top
            if surface_top < self.rect.top - ANIMAL_SUMMON_PLATFORM_SCAN_HEIGHT or relative_height < -18.0 or relative_height > ANIMAL_SUMMON_PLATFORM_SCAN_HEIGHT + 12.0:
                continue
            if destination.x < surface.left - TILE_SIZE or destination.x > surface.right + TILE_SIZE:
                continue
            if self.rect.centerx < surface.left - horizontal_trigger_range or self.rect.centerx > surface.right + horizontal_trigger_range:
                continue
            if (
                abs(relative_height) <= 18.0
                and surface.left - 4.0 <= self.rect.centerx <= surface.right + 4.0
                and surface.left - 4.0 <= destination.x <= surface.right + 4.0
            ):
                continue

            candidate_center_x = max(surface.left + self.rect.width * 0.5, min(destination.x, surface.right - self.rect.width * 0.5))
            landing_rect = pygame.FRect(candidate_center_x - self.rect.width * 0.5, surface_top - self.rect.height, self.rect.width, self.rect.height)
            if not self._level_rect_is_clear(level, landing_rect):
                continue
            score = abs(candidate_center_x - destination.x) + abs(surface_top - destination.y) * 0.45 + abs(relative_height) * 0.08
            if score < best_score:
                best_score = score
                best_landing_rect = landing_rect
        return best_landing_rect

    def _animal_summon_supports_point(self, sample_x: float, sample_y: float, level) -> bool:
        probe_rect = pygame.Rect(int(sample_x), int(sample_y), 1, 1)
        for solid in level.nearby_solids(probe_rect):
            if solid.collidepoint(sample_x, sample_y):
                return True
        platform_query = pygame.Rect(int(sample_x - 2), int(sample_y - 12), 4, 24)
        for platform in level.nearby_semisolids(platform_query):
            if platform.left + 6 <= sample_x <= platform.right - 6 and abs(platform.top - sample_y) <= 10.0:
                return True
        return False

    def _animal_summon_has_gap_between(self, destination_x: float, level) -> bool:
        start_x = self.rect.centerx
        end_x = destination_x
        span = abs(end_x - start_x)
        if span < TILE_SIZE * 0.75:
            return False
        sample_y = self.rect.bottom + 6.0
        steps = max(3, int(span // (TILE_SIZE * 0.5)))
        unsupported_samples = 0
        for step in range(1, steps):
            sample_x = start_x + (end_x - start_x) * (step / steps)
            if not self._animal_summon_supports_point(sample_x, sample_y, level):
                unsupported_samples += 1
                if unsupported_samples >= 2:
                    return True
        return False

    def _find_jump_landing_rect(self, destination: Vec2, level) -> pygame.FRect | None:
        return self._animal_summon_find_jump_landing_rect(destination, level)

    def _start_animal_summon_platform_jump(self, landing_rect: pygame.FRect) -> None:
        start = Vec2(self.rect.x, self.rect.y)
        target = Vec2(landing_rect.x, landing_rect.y)
        horizontal_distance = abs(target.x - start.x)
        climb_height = max(0.0, start.y - target.y)
        drop_height = max(0.0, target.y - start.y)
        duration = ANIMAL_SUMMON_PLATFORM_JUMP_MIN_TIME + min(
            ANIMAL_SUMMON_PLATFORM_JUMP_MAX_TIME - ANIMAL_SUMMON_PLATFORM_JUMP_MIN_TIME,
            horizontal_distance / 620.0 + climb_height / 520.0 + drop_height / 760.0,
        )
        self.ally_platform_jump_arc = max(
            ANIMAL_SUMMON_PLATFORM_JUMP_ARC,
            climb_height * 0.72 + 18.0,
            horizontal_distance * 0.12 + climb_height * 0.30,
        )
        self.velocity.y = -(ANIMAL_SUMMON_JUMP_SPEED + min(82.0, climb_height * 0.42))
        self.ally_jump_cooldown = ANIMAL_SUMMON_JUMP_COOLDOWN
        self.ally_platform_snap_timer = duration
        self.ally_platform_jump_duration = duration
        self.ally_platform_jump_start = start
        self.ally_platform_target = target
        self.on_ground = False
        self.action_state = "ally"
        self.movement_state = "jump"

    def _start_ally_platform_jump(self, landing_rect: pygame.FRect) -> None:
        self._start_animal_summon_platform_jump(landing_rect)

    def _update_animal_summon_platform_jump(self, delta_time: float, level) -> bool:
        if self.ally_platform_target is None or self.ally_platform_jump_start is None:
            return False

        remaining = max(0.0, self.ally_platform_snap_timer)
        duration = max(0.001, self.ally_platform_jump_duration)
        progress = 1.0 - remaining / duration
        progress = max(0.0, min(1.0, progress))
        eased = progress * progress * (3.0 - 2.0 * progress)
        start = self.ally_platform_jump_start
        target = self.ally_platform_target
        self.rect.x = start.x + (target.x - start.x) * eased
        base_y = start.y + (target.y - start.y) * eased
        self.rect.y = base_y - self.ally_platform_jump_arc * 4.0 * progress * (1.0 - progress)
        self.velocity.x = (target.x - start.x) / duration
        self.velocity.y = -(self.ally_platform_jump_arc / max(0.12, duration)) if progress < 0.52 else ENEMY_GRAVITY * 0.22
        self.on_ground = False
        self.action_state = "ally"
        self.movement_state = "jump" if progress < 0.64 else "fall"

        if remaining > 0.0:
            return True

        landing_rect = pygame.FRect(target.x, target.y, self.rect.width, self.rect.height)
        if self._level_rect_is_clear(level, landing_rect):
            self.rect.x = landing_rect.x
            self.rect.y = landing_rect.y
        self.velocity.xy = (0.0, 0.0)
        self.on_ground = True
        self.ally_platform_target = None
        self.ally_platform_jump_start = None
        self.ally_platform_jump_duration = 0.0
        self.ally_platform_jump_arc = ANIMAL_SUMMON_PLATFORM_JUMP_ARC
        self.action_state = "ally"
        self.movement_state = "escort"
        return True

    def _update_ally_platform_jump(self, delta_time: float, level) -> bool:
        return self._update_animal_summon_platform_jump(delta_time, level)

    def _set_airborne_ally_state(self) -> None:
        if not self.on_ground:
            self.action_state = "ally"
            self.movement_state = "jump" if self.velocity.y < -20.0 else "fall"

    def update(
        self,
        delta_time: float,
        player: Player,
        level,
        hostiles: list["Enemy"] | None = None,
        distant_behavior: bool = False,
    ) -> EnemyUpdateResult:
        result = EnemyUpdateResult()
        self.tick_timers(delta_time)
        self.summon_timer = max(0.0, self.summon_timer - delta_time)
        self.contact_cooldown = max(0.0, self.contact_cooldown - delta_time)
        self.hurt_timer = max(0.0, self.hurt_timer - delta_time)
        self.ally_jump_cooldown = max(0.0, self.ally_jump_cooldown - delta_time)
        self.ally_jump_grace_timer = max(0.0, self.ally_jump_grace_timer - delta_time)
        self.ally_teleport_cooldown = max(0.0, self.ally_teleport_cooldown - delta_time)
        self.ally_platform_snap_timer = max(0.0, self.ally_platform_snap_timer - delta_time)
        self.patrol_timer = max(0.0, self.patrol_timer - delta_time)
        self.rest_timer = max(0.0, self.rest_timer - delta_time)
        self.aggro_memory_timer = max(0.0, self.aggro_memory_timer - delta_time)
        self.dash_hit_cooldown = max(0.0, self.dash_hit_cooldown - delta_time)
        self.stun_timer = max(0.0, self.stun_timer - delta_time)
        self.rift_intent_timer = max(0.0, self.rift_intent_timer - delta_time)
        self.halo_launch_timer = max(0.0, self.halo_launch_timer - delta_time)
        if self.is_boss and self.rift_intent_timer > 0.0:
            if not player.has_halo_barrier():
                self.rift_intent_timer = 0.0
            else:
                barrier_distance = (player.center() - self.center()).length()
                abandon_distance = max(player.halo_barrier_radius * 2.65, 340.0)
                if barrier_distance > abandon_distance:
                    self.rift_intent_timer = min(self.rift_intent_timer, 0.28)
                elif barrier_distance <= player.halo_barrier_radius * 1.18:
                    self.rift_intent_timer = max(self.rift_intent_timer, 0.85)

        bait_active = self.is_boss and player.has_boss_rift_bait()
        stats = self.attack_stats()
        previous_attack_startup = self.attack_startup_timer
        previous_attack_active = self.attack_timer
        self.attack_startup_timer = max(0.0, self.attack_startup_timer - delta_time)
        self.attack_timer = max(0.0, self.attack_timer - delta_time)
        self.attack_recovery_timer = max(0.0, self.attack_recovery_timer - delta_time)

        if previous_attack_startup > 0.0 and self.attack_startup_timer == 0.0 and self.attack_timer == 0.0:
            self.attack_timer = stats["active"]
            self.attack_has_hit = False
            result.attack_started = True
            result.attack_profile = self.attack_profile
        elif previous_attack_active > 0.0 and self.attack_timer == 0.0 and self.attack_recovery_timer == 0.0:
            self.attack_recovery_timer = stats["recovery"]

        if not self.alive:
            self.action_state = "dead"
            self.movement_state = "idle"
            return result

        if self.is_friendly and self.enemy_type == "elite_knight" and self.summon_timer <= 0.0:
            self.health = 0
            self.action_state = "dead"
            self.movement_state = "idle"
            return result

        if self.halo_launch_timer > 0.0:
            launch_delta = self.center() - self.halo_launch_origin
            launch_distance = launch_delta.length()
            if launch_distance <= 0.001:
                launch_direction = Vec2(self.facing if self.facing != 0 else 1.0, -0.12)
            else:
                launch_direction = launch_delta.normalize()
            if launch_direction.y > -0.05:
                launch_direction.y = -0.05
                launch_direction = launch_direction.normalize()

            if launch_distance < self.halo_launch_escape_radius:
                outward_speed = 360.0 if self.is_boss else 460.0
                self.velocity.x = move_toward(self.velocity.x, launch_direction.x * outward_speed, 1900.0 * delta_time)
                self.velocity.y = min(self.velocity.y, -118.0 if self.is_boss else -156.0)
            else:
                self.velocity.x = move_toward(self.velocity.x, self.velocity.x * 0.62, 980.0 * delta_time)

            self.velocity.y = min(self.velocity.y + ENEMY_GRAVITY * delta_time, ENEMY_MAX_FALL_SPEED)
            level.move_actor(self, delta_time)
            self.action_state = "recoil" if self.is_boss else "hurt"
            self.movement_state = "stagger"
            if self.on_ground and launch_distance >= self.halo_launch_escape_radius:
                self.halo_launch_timer = min(self.halo_launch_timer, 0.04)
            return result

        if self.stun_timer > 0.0:
            self.velocity.x = move_toward(self.velocity.x, 0.0, 520.0 * delta_time)
            self.velocity.y = min(self.velocity.y + ENEMY_GRAVITY * delta_time, ENEMY_MAX_FALL_SPEED)
            level.move_actor(self, delta_time)
            self.action_state = "stunned"
            self.movement_state = "stagger"
            return result

        if self.is_summoned_ally() and self._update_ally_platform_jump(delta_time, level):
            return result

        if self.is_summoned_ally():
            if self._ally_should_teleport_to_player(player) and self._teleport_near_player(player, level):
                self.action_state = "ally"
                self.movement_state = "escort"
                return result

            target = None
            if hostiles:
                visible_hostiles = [
                    enemy
                    for enemy in hostiles
                    if enemy.alive
                    and not enemy.is_friendly
                    and abs(enemy.center().y - self.center().y) <= ANIMAL_SUMMON_AGGRO_VERTICAL_RANGE
                    and (enemy.center() - self.center()).length() <= min(self.detection_range, ANIMAL_SUMMON_AGGRO_RANGE)
                ]
                if visible_hostiles:
                    target = min(visible_hostiles, key=lambda enemy: (enemy.center() - self.center()).length_squared())

            if target is not None:
                delta = target.center() - self.center()
                jump_destination = Vec2(target.rect.centerx, target.rect.bottom)
                if abs(delta.x) > 8.0:
                    self.facing = 1 if delta.x > 0.0 else -1
                self.choose_attack_profile(target)
                stats = self.attack_stats()
                distance_x = abs(delta.x)
                if self.current_attack_is_ranged():
                    if self.on_ground and self.contact_cooldown <= 0.0 and distance_x <= stats["range"] and abs(delta.y) < 90.0:
                        self.contact_cooldown = ENEMY_TOUCH_COOLDOWN + 0.18
                        self.attack_startup_timer = stats["windup"]
                        self.attack_has_hit = False
                        self.velocity.x = 0.0
                        self.action_state = "attack_windup"
                        self.movement_state = "ally_aim"
                        return result
                    if distance_x < self.preferred_range * 0.72:
                        target_speed = -self.facing * self.move_speed * 0.82
                        self.movement_state = "ally_reposition"
                    elif distance_x > self.preferred_range * 1.08:
                        target_speed = self.chase_speed * 0.94 if delta.x > 0.0 else -self.chase_speed * 0.94
                        self.movement_state = "ally_chase"
                    else:
                        target_speed = 0.0
                        self.movement_state = "ally_aim"
                    self.action_state = "ally"
                else:
                    if self._within_attack_range(target) and self.contact_cooldown <= 0.0 and self.on_ground:
                        self.contact_cooldown = ENEMY_TOUCH_COOLDOWN
                        self.attack_startup_timer = stats["windup"]
                        self.attack_has_hit = False
                        self.velocity.x = 0.0
                        self.action_state = "attack_windup"
                        self.movement_state = "ally_chase"
                        return result
                    target_speed = self.chase_speed * 0.96 if delta.x > 0.0 else -self.chase_speed * 0.96
                    self.action_state = "ally"
                    self.movement_state = "ally_chase"
                landing_rect = self._find_jump_landing_rect(jump_destination, level)
                if landing_rect is not None:
                    self._start_ally_platform_jump(landing_rect)
                    return result
            else:
                delta = player.center() - self.center()
                escort_destination = Vec2(player.rect.centerx, player.rect.bottom)
                if abs(delta.x) > 72.0:
                    self.facing = 1 if delta.x > 0.0 else -1
                target_speed = 0.0 if abs(delta.x) < 56.0 else self.move_speed * 0.92 * self.facing
                self.action_state = "ally"
                self.movement_state = "escort"
                should_try_escort_jump = abs(delta.x) > TILE_SIZE * 1.1 or self.rect.bottom - player.rect.bottom > TILE_SIZE * 0.75
                landing_rect = self._find_jump_landing_rect(escort_destination, level) if should_try_escort_jump else None
                if landing_rect is not None:
                    self._start_ally_platform_jump(landing_rect)
                    return result
            self.velocity.x = move_toward(self.velocity.x, target_speed, 960.0 * delta_time)
            self.velocity.y = min(self.velocity.y + ENEMY_GRAVITY * delta_time, ENEMY_MAX_FALL_SPEED)
            level.move_actor(self, delta_time)
            self._set_airborne_ally_state()
            return result

        if self.is_controlled_ally():
            target = None
            if hostiles:
                visible_hostiles = [enemy for enemy in hostiles if enemy.alive and not enemy.is_friendly]
                if visible_hostiles:
                    target = min(visible_hostiles, key=lambda enemy: (enemy.center() - self.center()).length_squared())

            if target is not None:
                delta = target.center() - self.center()
                if abs(delta.x) > 8.0:
                    self.facing = 1 if delta.x > 0.0 else -1
                self.choose_attack_profile(target)
                stats = self.attack_stats()
                distance_x = abs(delta.x)
                if self.current_attack_is_ranged():
                    if self.on_ground and self.contact_cooldown <= 0.0 and distance_x <= stats["range"] and abs(delta.y) < 90.0:
                        self.contact_cooldown = ENEMY_TOUCH_COOLDOWN + 0.18
                        self.attack_startup_timer = stats["windup"]
                        self.attack_has_hit = False
                        self.velocity.x = 0.0
                        self.action_state = "attack_windup"
                        self.movement_state = "ally_aim"
                        return result
                    if distance_x < self.preferred_range * 0.72:
                        target_speed = -self.facing * self.move_speed * 0.8
                        self.movement_state = "ally_reposition"
                    elif distance_x > self.preferred_range * 1.08:
                        target_speed = self.chase_speed * 0.84 if delta.x > 0.0 else -self.chase_speed * 0.84
                        self.movement_state = "ally_chase"
                    else:
                        target_speed = 0.0
                        self.movement_state = "ally_aim"
                    self.action_state = "ally"
                else:
                    if self._within_attack_range(target) and self.contact_cooldown <= 0.0 and self.on_ground:
                        self.contact_cooldown = ENEMY_TOUCH_COOLDOWN
                        self.attack_startup_timer = stats["windup"]
                        self.attack_has_hit = False
                        self.velocity.x = 0.0
                        self.action_state = "attack_windup"
                        self.movement_state = "ally_chase"
                        return result
                    target_speed = self.chase_speed * 0.9 if delta.x > 0.0 else -self.chase_speed * 0.9
                    self.action_state = "ally"
                    self.movement_state = "ally_chase"
            else:
                delta = player.center() - self.center()
                if abs(delta.x) > 72.0:
                    self.facing = 1 if delta.x > 0.0 else -1
                target_speed = 0.0 if abs(delta.x) < 56.0 else self.move_speed * 0.8 * self.facing
                self.action_state = "ally"
                self.movement_state = "escort"

            self.velocity.x = move_toward(self.velocity.x, target_speed, 960.0 * delta_time)
            self.velocity.y = min(self.velocity.y + ENEMY_GRAVITY * delta_time, ENEMY_MAX_FALL_SPEED)
            level.move_actor(self, delta_time)
            if not self.on_ground:
                self.movement_state = "fall" if self.velocity.y >= 0.0 else "jump"
            return result

        if self.hurt_timer > 0.0:
            self.velocity.x = move_toward(self.velocity.x, 0.0, 520.0 * delta_time)
            self.velocity.y = min(self.velocity.y + ENEMY_GRAVITY * delta_time, ENEMY_MAX_FALL_SPEED)
            level.move_actor(self, delta_time)
            self.action_state = "hurt"
            return result

        if distant_behavior and not self.is_friendly:
            self.aggro_memory_timer = 0.0
            self.last_seen_position = None
            self.action_state = "neutral"
            if self.rest_timer > 0.0:
                target_speed = 0.0
                self.movement_state = "rest"
            else:
                if abs(self.rect.x - self.patrol_origin_x) > self.patrol_radius:
                    self.facing *= -1
                    self.rest_timer = 0.7
                elif self.patrol_timer <= 0.0:
                    self.facing *= -1
                    self.patrol_timer = 1.0 + (int(self.patrol_origin_x) % 60) / 100.0
                    self.rest_timer = 0.85

                target_speed = 0.0 if self.rest_timer > 0.0 else self.move_speed * self.facing
                self.movement_state = "rest" if self.rest_timer > 0.0 else "patrol"

            self.velocity.x = move_toward(self.velocity.x, target_speed, 850.0 * delta_time)
            self.velocity.y = min(self.velocity.y + ENEMY_GRAVITY * delta_time, ENEMY_MAX_FALL_SPEED)
            level.move_actor(self, delta_time)
            return result

        has_visual = self.can_see_player(player, level)
        if has_visual:
            self.aggro_memory_timer = ENEMY_MEMORY_TIME
            self.last_seen_position = player.center()

        if self.attack_startup_timer > 0.0:
            self.velocity.x = move_toward(self.velocity.x, 0.0, 1400.0 * delta_time)
            self.velocity.y = min(self.velocity.y + ENEMY_GRAVITY * delta_time, ENEMY_MAX_FALL_SPEED)
            level.move_actor(self, delta_time)
            self.action_state = "attack_windup"
            self.movement_state = "brace"
            return result

        if self.attack_timer > 0.0:
            drive_speed = stats["drive_speed"]
            self.velocity.x = self.facing * drive_speed if drive_speed > 0.0 else 0.0
            self.velocity.y = min(self.velocity.y + ENEMY_GRAVITY * delta_time, ENEMY_MAX_FALL_SPEED)
            level.move_actor(self, delta_time)
            self.action_state = "attack"
            self.movement_state = "brace"

            barrier_blocks_hit = False
            if self.is_boss and player.has_halo_barrier():
                boss_distance = (player.center() - self.center()).length()
                if self.attack_profile == "rift":
                    barrier_blocks_hit = boss_distance > player.halo_barrier_radius * 1.02
                else:
                    barrier_blocks_hit = True

            if self.current_attack_is_ranged() and not self.attack_has_hit:
                origin = self.projectile_origin()
                result.projectile_spawn = EnemyProjectileSpawn(
                    position=origin,
                    velocity=Vec2(self.facing * 460.0, 0.0),
                    damage=int(stats["damage"]),
                    radius=float(stats["radius"]),
                    tint=self.weapon_color,
                    source_enemy=self,
                )
                self.attack_has_hit = True
                return result

            if not self.is_ranged and not barrier_blocks_hit and not self.attack_has_hit and self.attack_hitbox().colliderect(player.rect.inflate(-4, -4)):
                self.attack_has_hit = True
                guard_result = player.try_guard(self.center().x)
                if guard_result == "parry":
                    self.on_parried()
                    result.parried = True
                    return result
                if guard_result == "guard":
                    self.on_guarded(player.facing)
                    result.guarded = True
                    if self.attack_profile == "rift":
                        player.tear_barrier()
                    guard_damage = 60 if self.attack_profile == "rift" else max(1, int(stats["damage"] * BOSS_DAMAGE_REMAINDER))
                    if self.is_boss and player.take_damage(guard_damage, PLAYER_IFRAMES * 0.65, ignore_invulnerability=True, true_damage=self.attack_profile == "rift"):
                        player.velocity.x = 180.0 * self.facing
                        player.velocity.y = -150.0
                        result.damage = player.last_damage_taken
                    return result
                if self.is_boss and player.dash_timer > 0.0 and not player.has_perfect_avoid():
                    if self.attack_profile == "rift":
                        player.tear_barrier()
                    dash_damage = 60 if self.attack_profile == "rift" else max(1, int(stats["damage"] * BOSS_DAMAGE_REMAINDER))
                    if player.take_damage(dash_damage, PLAYER_IFRAMES * 0.55, ignore_invulnerability=True, true_damage=self.attack_profile == "rift"):
                        player.velocity.x = 180.0 * self.facing
                        player.velocity.y = -160.0
                        result.damage = player.last_damage_taken
                    return result
                if self.attack_profile == "rift":
                    player.tear_barrier()
                hit_damage = 60 if self.attack_profile == "rift" else int(stats["damage"])
                if player.take_damage(hit_damage, PLAYER_IFRAMES, true_damage=self.attack_profile == "rift"):
                    player.velocity.x = 240.0 * self.facing
                    player.velocity.y = -220.0
                    result.damage = player.last_damage_taken
            return result

        if self.attack_recovery_timer > 0.0:
            self.velocity.x = move_toward(self.velocity.x, 0.0, 820.0 * delta_time)
            self.velocity.y = min(self.velocity.y + ENEMY_GRAVITY * delta_time, ENEMY_MAX_FALL_SPEED)
            level.move_actor(self, delta_time)
            self.action_state = "attack_recovery"
            self.movement_state = "brace"
            return result

        self.action_state = "neutral"

        target_speed = 0.0
        if has_visual or self.aggro_memory_timer > 0.0:
            target_position = player.center() if has_visual else self.last_seen_position
            pursue_delta = target_position - self.center()
            if abs(pursue_delta.x) > 4.0:
                self.facing = 1 if pursue_delta.x > 0.0 else -1

            self.choose_attack_profile(player)
            stats = self.attack_stats()
            if self.current_attack_is_ranged():
                distance_x = abs(player.center().x - self.center().x)
                if has_visual and self.on_ground and self.contact_cooldown <= 0.0 and distance_x <= stats["range"] and abs(player.rect.centery - self.rect.centery) < 90.0:
                    self.contact_cooldown = ENEMY_TOUCH_COOLDOWN + 0.18
                    self.attack_startup_timer = stats["windup"]
                    self.attack_has_hit = False
                    self.velocity.x = 0.0
                    self.action_state = "attack_windup"
                    self.movement_state = "brace"
                    return result

                if distance_x < self.preferred_range * 0.78:
                    target_speed = -self.facing * self.move_speed
                    self.movement_state = "retreat"
                elif distance_x > self.preferred_range * 1.12:
                    target_speed = self.facing * self.move_speed
                    self.movement_state = "reposition"
                else:
                    target_speed = 0.0
                    self.movement_state = "aim"
            else:
                barrier_attack_ready = True
                barrier_inside = False
                rift_ready = True
                boss_distance = 0.0
                if self.is_boss and player.has_halo_barrier():
                    boss_distance = (player.center() - self.center()).length()
                    barrier_inside = boss_distance <= player.halo_barrier_radius
                    rift_ready = boss_distance <= player.halo_barrier_radius * 1.02
                    barrier_attack_ready = rift_ready if self.attack_profile == "rift" else False

                if self._within_attack_range(player) and self.contact_cooldown <= 0.0 and self.on_ground and self.aggro_memory_timer > 0.0:
                    if barrier_attack_ready:
                        self.contact_cooldown = ENEMY_TOUCH_COOLDOWN
                        self.attack_startup_timer = stats["windup"]
                        self.attack_has_hit = False
                        if self.attack_profile == "rift":
                            self.rift_intent_timer = 0.0
                        self.velocity.x = 0.0
                        self.action_state = "attack_windup"
                        self.movement_state = "brace"
                        return result

                rift_intent_active = self.is_boss and self.rift_intent_timer > 0.0 and player.has_halo_barrier()
                if rift_intent_active:
                    self.attack_profile = "rift"
                    self.rift_intent_timer = max(self.rift_intent_timer, 0.70)
                    player_motion_ratio = min(1.0, abs(player.velocity.x) / max(1.0, PLAYER_MAX_SPEED))
                    invade_speed_scale = 1.12 + player_motion_ratio * 1.08
                    if not barrier_inside:
                        target_speed = self.chase_speed * 1.18 * invade_speed_scale if pursue_delta.x > 0.0 else -self.chase_speed * 1.18 * invade_speed_scale
                        self.movement_state = "invade"
                    elif not barrier_attack_ready:
                        target_speed = self.chase_speed * 0.94 * invade_speed_scale if pursue_delta.x > 0.0 else -self.chase_speed * 0.94 * invade_speed_scale
                        self.movement_state = "invade"
                    elif not self._within_attack_range(player):
                        target_speed = self.chase_speed * 0.62 * invade_speed_scale if pursue_delta.x > 0.0 else -self.chase_speed * 0.62 * invade_speed_scale
                        self.movement_state = "invade"
                    else:
                        target_speed = self.chase_speed * 0.28 * invade_speed_scale if pursue_delta.x > 0.0 else -self.chase_speed * 0.28 * invade_speed_scale
                        self.movement_state = "invade"
                elif self.is_boss and player.has_halo_barrier():
                    boundary_buffer = 12.0
                    if barrier_inside:
                        target_speed = -self.facing * self.chase_speed * 0.52
                        self.movement_state = "retreat"
                    elif boss_distance <= player.halo_barrier_radius + boundary_buffer:
                        target_speed = 0.0
                        self.movement_state = "brace"
                    else:
                        target_speed = self.chase_speed if pursue_delta.x > 0.0 else -self.chase_speed
                        self.movement_state = "chase" if has_visual else "search"
                elif bait_active and self.is_boss and player.has_halo_barrier():
                    target_speed = self.chase_speed if pursue_delta.x > 0.0 else -self.chase_speed
                    self.movement_state = "chase"
                else:
                    target_speed = self.chase_speed if pursue_delta.x > 0.0 else -self.chase_speed
                    if not has_visual and abs(pursue_delta.x) < 18.0:
                        target_speed = 0.0
                        self.movement_state = "search"
                    else:
                        self.movement_state = "chase" if has_visual else "search"

            self.rest_timer = 0.0
            self.patrol_timer = 1.2
        else:
            if self.rest_timer > 0.0:
                target_speed = 0.0
                self.movement_state = "rest"
            else:
                if abs(self.rect.x - self.patrol_origin_x) > self.patrol_radius:
                    self.facing *= -1
                    self.rest_timer = 0.7
                elif self.patrol_timer <= 0.0:
                    self.facing *= -1
                    self.patrol_timer = 1.0 + (int(self.patrol_origin_x) % 60) / 100.0
                    self.rest_timer = 0.85

                target_speed = 0.0 if self.rest_timer > 0.0 else self.move_speed * self.facing
                self.movement_state = "rest" if self.rest_timer > 0.0 else "patrol"

        self.velocity.x = move_toward(self.velocity.x, target_speed, 1100.0 * delta_time)
        self.velocity.y = min(self.velocity.y + ENEMY_GRAVITY * delta_time, ENEMY_MAX_FALL_SPEED)
        level.move_actor(self, delta_time)
        return result


PLAYER_DRAW_COLORS = (PLAYER_COLOR, PLAYER_HIT_COLOR)
ENEMY_DRAW_COLORS = (ENEMY_COLOR, ENEMY_HIT_COLOR)
