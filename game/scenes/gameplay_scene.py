from __future__ import annotations

from dataclasses import dataclass, field
import math
import random

import pygame

from game.config import (
    ACCENT_COLOR,
    ALLY_COLOR,
    ATTACK_COLOR,
    CAMERA_LOOK_AHEAD,
    CAMERA_SHAKE_DECAY,
    CAMERA_SHAKE_MAX,
    CAMERA_SMOOTHING,
    DANGER_COLOR,
    DASH_STRIKE_HITSTOP,
    ENEMY_ATTACK_COLOR,
    ENEMY_TELEGRAPH_COLOR,
    ENEMY_VISION_ALERT_COLOR,
    ENEMY_VISION_COLOR,
    EXECUTION_CAMERA_ZOOM,
    EXECUTION_FLASH_COLOR,
    EXECUTION_HITSTOP,
    EXECUTION_TIME,
    EQUIPMENT_GLOW,
    GUARD_HITSTOP,
    PALADIN_BLADE_COOLDOWN,
    PALADIN_BLADE_DAMAGE,
    PALADIN_BLADE_ROOT_TIME,
    PALADIN_FUSION_BONUS_DAMAGE,
    PALADIN_FUSION_COLLISION_DAMAGE,
    PALADIN_FUSION_COOLDOWN,
    PALADIN_FUSION_SHIELD,
    PALADIN_FUSION_SPEED,
    PALADIN_FUSION_TIME,
    PALADIN_HALO_COOLDOWN,
    PALADIN_HALO_HEAL_RATE,
    PALADIN_HALO_RADIUS,
    PALADIN_HALO_TIME,
    PALADIN_RAIN_COOLDOWN,
    PALADIN_RAIN_DAMAGE,
    PALADIN_RAIN_STUN_TIME,
    PALADIN_SCRIPTURE_COOLDOWN,
    PALADIN_SPIRIT_COOLDOWN,
    PANEL_BORDER,
    PARRY_HITSTOP,
    PARRY_FLASH_COLOR,
    PARRY_CLASH_TIME,
    PARRY_FULL_FLASH_COLOR,
    PARRY_FULL_FLASH_TIME,
    PARRY_IMPACT_TIME,
    PARRY_IMPACT_ZOOM,
    PARRY_SHADE_COLOR,
    PERFECT_DODGE_FLASH_COLOR,
    PERFECT_DODGE_FLASH_TIME,
    PERFECT_DODGE_RING_LIFETIME,
    PERFECT_DODGE_SLOW_SCALE,
    PERFECT_DODGE_SLOW_TIME,
    PERFECT_DODGE_SLASH_HITSTOP,
    PERFECT_DODGE_SLASH_LIFETIME,
    PERFECT_DODGE_ZOOM,
    SANITY_BLUR_MAX_SCALE,
    SANITY_BLUR_START,
    SANITY_BREAK_CHECK_TIME,
    SANITY_COLOR,
    SANITY_DAMAGE_LOSS,
    SANITY_DANGER_COLOR,
    SANITY_DANGER_THRESHOLD,
    SANITY_MAX,
    SANITY_PASSIVE_DRAIN,
    PLAYER_AFTERIMAGE_INTERVAL,
    PLAYER_AFTERIMAGE_LIFETIME,
    PLAYER_BLOCK_COLOR,
    PLAYER_PARRY_COLOR,
    PLAYER_ROOM_ENTRY_SPEED,
    SHADOW_COLOR,
    SUCCESS_COLOR,
    TEXT_COLOR,
    TELEPORT_FINISHER_FLASH_COLOR,
    TELEPORT_FINISHER_SHADE_COLOR,
    TELEPORT_FINISHER_TIME,
    TELEPORT_FINISHER_ZOOM,
    TELEPORT_SLASH_DAMAGE,
    TELEPORT_SLASH_HITSTOP,
    TELEPORT_SLASH_LIFETIME,
    TILE_SIZE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from game.core.scene import Scene
from game.entities.actors import (
    DASH_STRIKE_DAMAGE,
    DASH_STRIKE_HIT_COOLDOWN,
    ENEMY_IFRAMES,
    ENEMY_DRAW_COLORS,
    EnemyProjectileSpawn,
    PLAYER_ATTACK_DAMAGE,
    PLAYER_DRAW_COLORS,
    Enemy,
    Player,
)
from game.scenes.pause_scene import PauseScene
from game.systems.equipment import (
    EquipmentState,
    PassiveSummary,
    build_passive_summary,
    effective_tier_for_slot,
    get_equipment,
    is_knight_brain,
    is_knight_brain_scripture,
    is_knight_brain_sword,
    knight_minor_tier,
    knight_blade_combo_hits,
    knight_blade_height_px,
    knight_blade_reach_px,
    knight_defense_bonus_percent,
    knight_halo_radius_px,
    knight_rain_forward_px,
    knight_rain_hit_height_px,
    knight_rain_hit_width_px,
    knight_rain_spacing_px,
    knight_rain_strike_count,
    knight_shield_hit_goal,
    knight_size_bonus_percent,
    knight_spirit_range_px,
    knight_stun_seconds,
    knight_tier,
)
from game.ui.equipment_panel import draw_equipment_panel, draw_slot_glyph
from game.ui.hud import draw_hud, draw_world_map_overlay
from game.world.level import LevelState


Vec2 = pygame.Vector2
RIFT_SLASH_COLOR = (104, 188, 255)
RIFT_SLASH_ACCENT = (228, 244, 255)
RIFT_SLASH_SHADE = (54, 82, 118)
HALO_WAVE_COLOR = (255, 240, 182)
HALO_WAVE_ACCENT = (255, 252, 238)
COMBO_TIMEOUT_SECONDS = 5.5
COMBO_TIMEOUT_MULTIPLIER = 1.1
COMBO_TIMEOUT_PER_HIT = 0.1
COMBO_SPEED_START_HITS = 5
COMBO_SPEED_START_BONUS = 20.0
COMBO_SPEED_MAX_BONUS = 50.0
COMBO_SPEED_MAX_HITS = 25
ELITE_KNIGHT_SUMMON_CAP = 2
ELITE_KNIGHT_SUMMON_DURATION = 22.0
SWORD_BRAIN_SPEED_START_BONUS = 40.0
SWORD_BRAIN_MAX_SPEED_BONUS = 200.0
SCRIPTURE_BRAIN_HEAL_AMOUNT = 18
SCRIPTURE_BRAIN_SANITY_RESTORE = 24.0
SWORD_BRAIN_EFFECT_TIME = 0.42
SCRIPTURE_BRAIN_EFFECT_TIME = 0.65
SCRIPTURE_BRAIN_DAMAGE_REDUCTION_MULTIPLIER = 1.35
BOSS_EXIT_DOOR_DELAY = 4.0
BOSS_EXIT_DOOR_APPEAR_TIME = 1.15
BOSS_EXIT_DOOR_ENTER_TIME = 0.55
MINOR_SKILL_COOLDOWN = 20.0
TELEPORT_DEPART_TIME = 0.38
TELEPORT_ARRIVE_TIME = 0.44
TELEPORT_ACTIVATE_DISTANCE = max(WINDOW_WIDTH, WINDOW_HEIGHT) * 0.32
TELEPORT_PORTAL_RADIUS = TILE_SIZE
SWORD_MANIA_DURATION = 10.0
SWORD_MANIA_MOVE_SPEED_MULTIPLIER = 1.5
SHIELD_BASTION_INTERVAL = 30.0
SHIELD_BASTION_DURATION = 7.5
STEEL_GUARD_DURATION = 10.0
OPPRESSION_DURATION = 1.0
OPPRESSION_DAMAGE_RATIO = 0.50
OPPRESSION_FIELD_VISUAL_TIME = 1.15
OPPRESSION_FIELD_RADIUS = TILE_SIZE * 6.0
SWORD_MANIA_TINT = (118, 22, 26)
SWORD_MANIA_ACCENT = (24, 8, 10)
OPPRESSION_TINT = (156, 78, 220)
OPPRESSION_ACCENT = (228, 198, 255)
STEEL_GUARD_TINT = (164, 176, 192)
STEEL_GUARD_ACCENT = (242, 248, 255)
SUMMONER_TINT = (86, 220, 232)
SUMMONER_ACCENT = (206, 252, 255)
FUSION_COLLISION_DAMAGE = 40


def max_cooldown_for_item(item_id: str | None, fallback: float) -> float:
    if item_id == "knight_left_eye_halo":
        return PALADIN_HALO_COOLDOWN
    if item_id == "knight_left_eye_blade":
        return PALADIN_BLADE_COOLDOWN
    if item_id == "knight_right_eye_rain":
        return PALADIN_RAIN_COOLDOWN
    if item_id == "knight_right_eye_spirit":
        return PALADIN_SPIRIT_COOLDOWN
    if is_knight_brain_sword(item_id):
        return 0.0
    if is_knight_brain_scripture(item_id):
        return PALADIN_SCRIPTURE_COOLDOWN
    if item_id == "knight_heart":
        return PALADIN_FUSION_COOLDOWN
    return fallback


def combo_speed_bonus_percent(combo_hits: int) -> float:
    if combo_hits < COMBO_SPEED_START_HITS:
        return 0.0
    if combo_hits >= COMBO_SPEED_MAX_HITS:
        return COMBO_SPEED_MAX_BONUS
    growth_span = max(1, COMBO_SPEED_MAX_HITS - COMBO_SPEED_START_HITS)
    progress = (combo_hits - COMBO_SPEED_START_HITS) / growth_span
    return COMBO_SPEED_START_BONUS + (COMBO_SPEED_MAX_BONUS - COMBO_SPEED_START_BONUS) * progress


def combo_timeout_seconds(combo_hits: int) -> float:
    return COMBO_TIMEOUT_SECONDS * COMBO_TIMEOUT_MULTIPLIER + max(0, combo_hits) * COMBO_TIMEOUT_PER_HIT


def sword_brain_speed_bonus_percent(combo_hits: int) -> float:
    if combo_hits < COMBO_SPEED_START_HITS:
        return 0.0
    if combo_hits >= COMBO_SPEED_MAX_HITS:
        return SWORD_BRAIN_MAX_SPEED_BONUS
    growth_span = max(1, COMBO_SPEED_MAX_HITS - COMBO_SPEED_START_HITS)
    progress = (combo_hits - COMBO_SPEED_START_HITS) / growth_span
    return SWORD_BRAIN_SPEED_START_BONUS + (SWORD_BRAIN_MAX_SPEED_BONUS - SWORD_BRAIN_SPEED_START_BONUS) * progress


def scripture_brain_rescue_cooldown_seconds(tier: int) -> float:
    return (15.0, 15.0, 10.0, 6.0, 0.0)[max(0, min(4, tier))]


def knight_halo_activation_push_px(tier: int) -> float:
    return (0.0, 0.0, 84.0, 126.0, 172.0)[tier]


def knight_halo_wave_push_px(tier: int) -> float:
    return (0.0, 0.0, 0.0, 176.0, 228.0)[tier]


def knight_halo_wave_damage(tier: int) -> int:
    return (0, 0, 0, 0, 16)[tier]


@dataclass
class CombatProjectile:
    rect: pygame.FRect
    velocity: Vec2
    damage: int
    tint: tuple[int, int, int]
    source_enemy: Enemy
    life_timer: float = 2.6
    reflected: bool = False
    orbit_timer: float = 0.0
    orbit_duration: float = 0.0
    orbit_side: int = 1
    curve_phase: float = 0.0
    trail: list[Vec2] = field(default_factory=list)

@dataclass
class SlashEffect:
    start: Vec2
    end: Vec2
    center: Vec2
    life: float
    tint: tuple[int, int, int]
    max_life: float
    accent_tint: tuple[int, int, int]
    width_scale: float = 1.0


@dataclass
class ImpactBurst:
    center: Vec2
    life: float
    max_life: float
    tint: tuple[int, int, int]
    accent_tint: tuple[int, int, int]
    radius: float
    spoke_count: int = 10


@dataclass
class HaloShockwave:
    center: Vec2
    life: float
    max_life: float
    start_radius: float
    end_radius: float
    tint: tuple[int, int, int]
    accent_tint: tuple[int, int, int]
    width: int = 4
    finisher: bool = False


@dataclass
class FinisherOverlay:
    center: Vec2
    life: float
    max_life: float
    flash_color: tuple[int, int, int, int]
    shade_color: tuple[int, int, int, int]
    line_color: tuple[int, int, int]
    spoke_count: int = 18


@dataclass
class EquipmentPickup:
    position: Vec2
    slot: str
    fixture_kind: str
    item_id: str | None
    hidden_item_id: str | None = None
    reveal_timer: float = 0.0
    reveal_progress: float = 1.0


@dataclass
class RouteGate:
    target_room_index: int
    rect: pygame.FRect
    label: str
    role: str


@dataclass
class TeleportPortal:
    portal_id: str
    edge_key: tuple[int, int]
    position: Vec2
    source_room_id: int
    target_room_id: int
    room_id: int
    label: str
    activated: bool = False


@dataclass
class TeleportTransition:
    source_portal_id: str
    target_portal_id: str
    phase: str
    timer: float
    max_timer: float


@dataclass
class FallingSwordStrike:
    origin: Vec2
    target: Vec2
    life: float
    tint: tuple[int, int, int]
    accent_tint: tuple[int, int, int]
    explosion_radius: float = 0.0
    triggered: bool = False


@dataclass
class BladeCombo:
    targets: list[Enemy]
    range_px: float
    hits_remaining: int
    hit_interval: float
    damage: int
    stun_time: float
    full_screen: bool = False
    band_height: float = 0.0
    timer: float = 0.0
    sequence_index: int = 0


@dataclass
class RadiantJudgement:
    targets: list[Enemy]
    warmup: float
    max_warmup: float
    damage: int
    stun_time: float
    band_height: float
    flash_timer: float = 0.0
    max_flash: float = 0.22
    recovery: float = 0.0
    max_recovery: float = 0.18
    damage_applied: bool = False
    slash_start: Vec2 | None = None
    slash_end: Vec2 | None = None
    prep_played: bool = False
    released: bool = False


@dataclass
class HeartFlight:
    start: Vec2
    target: Vec2
    progress: float = 0.0
    duration: float = 0.9


@dataclass
class MinorParticle:
    position: Vec2
    velocity: Vec2
    life: float
    max_life: float
    tint: tuple[int, int, int]
    accent_tint: tuple[int, int, int]
    radius: float


@dataclass
class OppressionLift:
    enemy: Enemy
    ground_bottom: float
    duration: float
    lift_height: float
    elapsed: float = 0.0


@dataclass
class HudStatusBar:
    key: str
    label: str
    ratio: float
    fill_color: tuple[int, int, int]
    back_color: tuple[int, int, int]
    edge_color: tuple[int, int, int]
    value_text: str = ""


class GameplayScene(Scene):
    def __init__(self, app, seed: int | None = None) -> None:
        super().__init__(app)
        self.level = LevelState(seed=seed)
        self.player = Player(self.level.current_room.player_spawn.copy())
        self.active_embedded_room_id = self.level.current_room_index
        self.room_enemy_cache: dict[int, list[Enemy]] = {}
        self.room_pickup_cache: dict[int, list[EquipmentPickup]] = {}
        self.cleared_room_ids: set[int] = set()
        self.pending_boss_spawn: tuple[int, Vec2, str] | None = None
        self.boss_spawned_room_ids: set[int] = set()
        self.enemies: list[Enemy] = self.spawn_world_enemies() if self.level.is_embedded_world_map else self.spawn_room_enemies()
        self.projectiles: list[CombatProjectile] = []
        if self.level.is_embedded_world_map:
            for room in self.level.rooms:
                self.cached_room_pickups(room.index)
            self.pickups = self.cached_room_pickups(self.level.current_room_index)
        else:
            self.pickups = [self.spawn_pickup(position, slot, item_id, hidden_item_id) for position, slot, item_id, hidden_item_id in self.level.current_room.item_spawns]
        self.camera = Vec2()
        self.message = ""
        self.message_color = ACCENT_COLOR
        self.message_timer = 0.0
        self.room_clear_announced = False
        self.room_intro_active = False
        self.room_intro_start_x = 0.0
        self.room_intro_start_y = 0.0
        self.room_intro_target_x = 0.0
        self.room_intro_target_y = 0.0
        self.room_intro_camera = Vec2()
        self.room_intro_hold_timer = 0.0
        self.room_intro_door_timer = 0.0
        self.room_intro_door_duration = 0.0
        self.room_intro_player_visible = True
        self.bullet_time_timer = 0.0
        self.afterimage_timer = 0.0
        self.player_afterimages: list[dict[str, object]] = []
        self.slash_effects: list[SlashEffect] = []
        self.impact_bursts: list[ImpactBurst] = []
        self.halo_shockwaves: list[HaloShockwave] = []
        self.execution_timer = 0.0
        self.execution_enemy: Enemy | None = None
        self.execution_strike_applied = False
        self.execution_direction = 1
        self.execution_style = "blade"
        self.execution_player_origin = Vec2()
        self.execution_enemy_origin = Vec2()
        self.parry_clash_timer = 0.0
        self.parry_clash_enemy: Enemy | None = None
        self.parry_clash_direction = 1
        self.parry_clash_center = Vec2()
        self.parry_clash_player_origin = Vec2()
        self.parry_clash_enemy_origin = Vec2()
        self.screen_shake = 0.0
        self.impact_freeze_timer = 0.0
        self.perfect_dodge_flash_timer = 0.0
        self.perfect_dodge_zoom_timer = 0.0
        self.parry_full_flash_timer = 0.0
        self.finisher_overlay: FinisherOverlay | None = None
        self.parry_overlay: FinisherOverlay | None = None
        self.heart_flight: HeartFlight | None = None
        self.altar_awaken_timer = 0.0
        self.equipment = EquipmentState()
        self.inventory_open = False
        self.sanity = SANITY_MAX
        self.sanity_vignette_display_strength = 0.0
        self.sanity_break_timer = SANITY_BREAK_CHECK_TIME
        self.player_size_bonus = 0
        self.attack_chain_hits = 0
        self.brain_chain_hits = 0
        self.attack_chain_timeout = 0.0
        self.fusion_timer = 0.0
        self.fusion_cooldown = 0.0
        self.halo_timer = 0.0
        self.halo_cooldown = 0.0
        self.halo_cast_tier = 0
        self.halo_pulse_timer = 0.0
        self.halo_end_pulse_pending = False
        self.left_skill_cooldown = 0.0
        self.right_skill_cooldown = 0.0
        self.brain_skill_cooldown = 0.0
        self.brain_rescue_cooldown = 0.0
        self.brain_sword_fx_timer = 0.0
        self.brain_scripture_fx_timer = 0.0
        self.minor_skill_cooldown = 0.0
        self.sword_mania_timer = 0.0
        self.steel_guard_timer = 0.0
        self.shield_bastion_timer = SHIELD_BASTION_INTERVAL
        self.oppression_field_timer = 0.0
        self.oppression_field_duration = 0.0
        self.oppression_field_center = self.player.center().copy()
        self.oppression_field_radius = 0.0
        self.player_damage_multiplier = 1.0
        self.control_duration_multiplier = 1.0
        self.minor_particles: list[MinorParticle] = []
        self.oppression_lifts: list[OppressionLift] = []
        self.boss_exit_door_delay_timer = -1.0
        self.boss_exit_door_progress = 0.0
        self.boss_exit_door_enter_timer = 0.0
        self.boss_exit_door_entering = False
        self.teleport_map_mode = False
        self.teleport_anchor_portal_id: str | None = None
        self.selected_teleport_portal_id: str | None = None
        self.teleport_transition: TeleportTransition | None = None
        self.teleport_portals: list[TeleportPortal] = []
        self.sword_rain_strikes: list[FallingSwordStrike] = []
        self.blade_combos: list[BladeCombo] = []
        self.radiant_judgement: RadiantJudgement | None = None
        self.route_map_open = False
        self.route_map_zoom = 1.0
        self.route_map_focus: Vec2 | None = None
        self.teleport_portals: list[TeleportPortal] = []
        self.teleport_map_mode = False
        self.teleport_anchor_portal_id: str | None = None
        self.selected_teleport_portal_id: str | None = None
        self.teleport_transition: TeleportTransition | None = None
        self.route_map_dirty = True
        self.route_map_refresh_timer = 0.0
        self.last_route_map_player_center = self.player.center().copy()
        self.scene_surface_cache: pygame.Surface | None = None
        self.overlay_surface_cache: dict[str, pygame.Surface] = {}
        self.effect_surface_cache: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}
        self.developer_mode_enabled = False
        self.developer_minor_override: str | None = None
        self.developer_no_cooldown = False
        self.rebuild_teleport_portals()
        self.rebuild_teleport_portals()
        self.active_room_role = self.level.current_room.role
        self.previous_room_role: str | None = None
        self.room_role_transition = 1.0
        self.regen_bank = 0.0
        self.room_intro_entry_direction = 1
        self.begin_room_intro()
        self.refresh_route_map()
        self.set_message(f"Seed {self.level.seed}  |  Route {len(self.level.rooms)} rooms", ACCENT_COLOR, 1.45)

    def get_overlay_surface(self, surface: pygame.Surface, key: str) -> pygame.Surface:
        size = surface.get_size()
        overlay = self.overlay_surface_cache.get(key)
        if overlay is None or overlay.get_size() != size:
            overlay = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
            self.overlay_surface_cache[key] = overlay
        else:
            overlay.fill((0, 0, 0, 0))
        return overlay

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        pressed = self.app.input.pressed_keys
        if not self.developer_mode_enabled:
            if all(key in pressed for key in (pygame.K_q, pygame.K_e, pygame.K_z, pygame.K_c)):
                self.developer_mode_enabled = True
                self.developer_minor_override = None
                self.developer_no_cooldown = False
                self.app.input.action_timers["ultimate"] = 0.0
                self.app.input.action_timers["map_zoom_out"] = 0.0
                self.app.input.action_timers["interact"] = 0.0
                self.app.input.action_timers["map_zoom_in"] = 0.0
                self.set_message("Developer Mode  ON", SUCCESS_COLOR, 0.9)
            return

        if all(key in pressed for key in (pygame.K_6, pygame.K_7)):
            self.developer_mode_enabled = False
            self.developer_minor_override = None
            self.developer_no_cooldown = False
            self.set_message("Developer Mode  OFF", ACCENT_COLOR, 0.9)
            return

        override_map = {
            pygame.K_1: ("sword", "Dev Minor: Sword T4"),
            pygame.K_2: ("shield", "Dev Minor: Shield T4"),
            pygame.K_3: ("control", "Dev Minor: Control T4"),
            pygame.K_4: ("summon", "Dev Minor: Summon T4"),
        }
        override = override_map.get(event.key)
        if override is not None:
            self.developer_minor_override = override[0]
            self.set_message(override[1], SUCCESS_COLOR, 0.9)
        elif event.key == pygame.K_0:
            self.developer_minor_override = None
            self.set_message("Dev Minor Cleared", ACCENT_COLOR, 0.8)
        elif event.key == pygame.K_9:
            self.developer_no_cooldown = not self.developer_no_cooldown
            if self.developer_no_cooldown:
                self.clear_developer_cooldowns()
            self.set_message("Dev No CD  ON" if self.developer_no_cooldown else "Dev No CD  OFF", SUCCESS_COLOR if self.developer_no_cooldown else ACCENT_COLOR, 0.8)

    def get_effect_surface(self, size: tuple[int, int], key: str) -> pygame.Surface:
        normalized_size = (max(1, int(size[0])), max(1, int(size[1])))
        cache_key = (key, normalized_size)
        effect = self.effect_surface_cache.get(cache_key)
        if effect is None:
            effect = pygame.Surface(normalized_size, pygame.SRCALPHA).convert_alpha()
            self.effect_surface_cache[cache_key] = effect
        else:
            effect.fill((0, 0, 0, 0))
        return effect

    def clear_developer_cooldowns(self) -> None:
        self.fusion_cooldown = 0.0
        self.halo_cooldown = 0.0
        self.left_skill_cooldown = 0.0
        self.right_skill_cooldown = 0.0
        self.brain_skill_cooldown = 0.0
        self.brain_rescue_cooldown = 0.0
        self.minor_skill_cooldown = 0.0
        self.player.attack_cooldown = 0.0
        self.player.block_cooldown = 0.0
        self.player.dash_cooldown = 0.0

    def cached_room_pickups(self, room_id: int) -> list[EquipmentPickup]:
        pickups = self.room_pickup_cache.get(room_id)
        if pickups is None:
            room = self.level.rooms[room_id]
            pickups = [self.spawn_pickup(position, slot, item_id, hidden_item_id) for position, slot, item_id, hidden_item_id in room.item_spawns]
            self.room_pickup_cache[room_id] = pickups
        return pickups

    def visible_render_pickups(self, margin: float = 96.0) -> list[EquipmentPickup]:
        if not self.level.is_embedded_world_map:
            return self.pickups
        view_rect = self.camera_world_rect(margin)
        visible: list[EquipmentPickup] = []
        for room_id in range(len(self.level.rooms)):
            for pickup in self.cached_room_pickups(room_id):
                pickup_rect = pygame.FRect(pickup.position.x - 40.0, pickup.position.y - 84.0, 80.0, 104.0)
                if view_rect.colliderect(pickup_rect):
                    visible.append(pickup)
        return visible

    def reveal_room_pickups_immediately(self) -> None:
        for pickup in self.pickups:
            if pickup.item_id is not None or pickup.hidden_item_id is None:
                continue
            pickup.item_id = pickup.hidden_item_id
            pickup.hidden_item_id = None
            pickup.reveal_timer = 0.0
            pickup.reveal_progress = 1.0

    def active_content_room(self):
        if self.level.is_embedded_world_map:
            return self.level.rooms[self.level.current_room_index]
        return self.level.current_room

    def activate_embedded_room(self, room_id: int) -> None:
        if not self.level.is_embedded_world_map:
            return
        room = self.level.rooms[room_id]
        if room.role != self.active_room_role:
            self.previous_room_role = self.active_room_role
            self.active_room_role = room.role
            self.room_role_transition = 0.0
        self.active_embedded_room_id = room_id
        self.pickups = self.cached_room_pickups(room_id)
        if room_id in self.cleared_room_ids:
            self.reveal_room_pickups_immediately()
        self.spawn_boss_for_room(room_id)

    def refresh_route_map(self) -> None:
        self.route_map = self.level.route_map_payload(self.player.center())
        if self.route_map is not None:
            hostile_positions: list[tuple[float, float]] = []
            boss_positions: list[tuple[float, float]] = []
            for enemy in self.enemies:
                if not enemy.alive or enemy.is_friendly:
                    continue
                enemy_position = (float(enemy.rect.centerx), float(enemy.rect.centery))
                if enemy.is_boss:
                    boss_positions.append(enemy_position)
                else:
                    hostile_positions.append(enemy_position)
            self.route_map["hostile_world_positions"] = hostile_positions
            self.route_map["boss_world_positions"] = boss_positions
            self.route_map["teleport_portals"] = [
                {
                    "portal_id": portal.portal_id,
                    "position": (float(portal.position.x), float(portal.position.y)),
                    "activated": portal.activated,
                    "label": portal.label,
                }
                for portal in self.teleport_portals
            ]
            self.route_map["selected_teleport_portal_id"] = self.selected_teleport_portal_id if self.teleport_map_mode else None
        self.route_map_dirty = False
        self.route_map_refresh_timer = 0.0
        self.last_route_map_player_center = self.player.center().copy()

    def rebuild_teleport_portals(self) -> None:
        self.teleport_portals = self.generate_teleport_portals()
        self.teleport_map_mode = False
        self.teleport_anchor_portal_id = None
        self.selected_teleport_portal_id = self.teleport_portals[0].portal_id if self.teleport_portals else None
        self.teleport_transition = None
        self.invalidate_route_map()

    def generate_teleport_portals(self) -> list[TeleportPortal]:
        if not self.level.is_embedded_world_map or not self.level.graph_nodes or not self.level.room_regions:
            return []
        nodes_by_id = {node.node_id: node for node in self.level.graph_nodes}
        portals: dict[str, TeleportPortal] = {}
        start_portal = self.build_start_room_teleport_portal(nodes_by_id)
        if start_portal is not None:
            portals[start_portal.portal_id] = start_portal
        for portal in self.build_connector_teleport_portals(nodes_by_id):
            portals[portal.portal_id] = portal
        for node in self.level.graph_nodes:
            source_region = self.level.room_regions.get(node.node_id)
            if source_region is None:
                continue
            for child_id in node.child_ids:
                child = nodes_by_id.get(child_id)
                target_region = self.level.room_regions.get(child_id)
                if child is None or target_region is None:
                    continue
                branch_junction = len(node.child_ids) >= 2 and (node.branch_type in {"major_branch", "minor_branch"} or child.branch_type in {"major_branch", "minor_branch"})
                branch_large_leaf = child.room_size == "large" and len(child.child_ids) == 0 and child.branch_type in {"major_branch", "minor_branch"}
                branch_small_leaf = self.branch_small_leaf_needs_portal(child, nodes_by_id)
                if not branch_junction and not branch_large_leaf and not branch_small_leaf:
                    continue
                if branch_junction:
                    continue
                if self.node_uses_teleport_room(child) or branch_small_leaf:
                    portal = self.build_room_centered_teleport_portal(node, child, target_region)
                    if portal is not None:
                        portals[portal.portal_id] = portal
                    continue
                portal = self.build_teleport_portal(node, child, source_region, target_region)
                if portal is not None:
                    portals[portal.portal_id] = portal
        return sorted(portals.values(), key=lambda portal: (portal.position.x, portal.position.y, portal.portal_id))

    def branch_small_leaf_needs_portal(
        self,
        node: GraphRoomNode,
        nodes_by_id: dict[int, GraphRoomNode],
    ) -> bool:
        if node.branch_type not in {"major_branch", "minor_branch"}:
            return False
        if node.room_size != "small" or node.child_ids:
            return False
        return self.branch_room_count(node, nodes_by_id) >= 3

    def branch_room_count(
        self,
        node: GraphRoomNode,
        nodes_by_id: dict[int, GraphRoomNode],
    ) -> int:
        count = 0
        current: GraphRoomNode | None = node
        while current is not None and current.branch_type in {"major_branch", "minor_branch"}:
            count += 1
            parent_id = current.parent_id
            current = nodes_by_id.get(parent_id) if parent_id is not None else None
        return count

    def build_start_room_teleport_portal(self, nodes_by_id: dict[int, GraphRoomNode]) -> TeleportPortal | None:
        graph_map = self.level.graph_map
        if graph_map is None:
            return None
        start = nodes_by_id.get(graph_map.start_id)
        start_region = self.level.room_regions.get(graph_map.start_id)
        if start is None or start_region is None or not start.child_ids:
            return None

        target_id = next((node_id for node_id in graph_map.main_path_ids[1:] if node_id in start.child_ids), start.child_ids[0])
        target = nodes_by_id.get(target_id)
        if target is None:
            return None

        position = self.find_room_centered_portal_position(start_region)
        if position is None:
            return None

        return TeleportPortal(
            portal_id=f"portal_start_{start.node_id}_{target.node_id}",
            edge_key=(start.node_id, target.node_id),
            position=position,
            source_room_id=start.node_id,
            target_room_id=target.node_id,
            room_id=start.node_id,
            label=start.room_name or f"{start.node_id}->{target.node_id}",
        )

    def build_connector_teleport_portals(self, nodes_by_id: dict[int, GraphRoomNode]) -> list[TeleportPortal]:
        portals: list[TeleportPortal] = []
        for placement in getattr(self.level, "connector_placements", []):
            component_name = str(getattr(placement.component, "name", ""))
            if component_name.startswith("基础连接通道/L_"):
                continue
            portal = self.build_connector_placement_teleport_portal(placement, nodes_by_id)
            if portal is not None:
                portals.append(portal)
        return portals

    def nearest_room_id_for_point(self, point: Vec2) -> int | None:
        point_tuple = (float(point.x), float(point.y))
        containing_room_id = next((room_id for room_id, region in self.level.room_regions.items() if region.collidepoint(point_tuple)), None)
        if containing_room_id is not None:
            return containing_room_id
        best_score: tuple[float, int] | None = None
        best_room_id: int | None = None
        for room_id, region in self.level.room_regions.items():
            delta_x = point.x - float(region.centerx)
            delta_y = point.y - float(region.centery)
            score = (delta_x * delta_x + delta_y * delta_y, room_id)
            if best_score is None or score < best_score:
                best_score = score
                best_room_id = room_id
        return best_room_id

    def find_connector_portal_position(self, placement) -> Vec2 | None:
        component = placement.component
        junction_x, junction_y = component.junction
        candidate_cells: list[tuple[int, int, int]] = []
        for row_index, row in enumerate(component.tile_grid):
            for col_index, value in enumerate(row):
                if value not in {1, 2}:
                    continue
                distance = abs(col_index - junction_x) + abs(row_index - junction_y)
                candidate_cells.append((distance, col_index, row_index))
        candidate_cells.sort()

        for _, col_index, row_index in candidate_cells:
            candidate_x = float((placement.left + col_index) * TILE_SIZE)
            reference_y = float((placement.top + row_index) * TILE_SIZE)
            snapped_x = self.snap_portal_x(candidate_x)
            position = self.portal_position_for_x(snapped_x, reference_y)
            if self.portal_position_is_clear(position):
                return position
        return None

    def build_connector_placement_teleport_portal(
        self,
        placement,
        nodes_by_id: dict[int, GraphRoomNode],
    ) -> TeleportPortal | None:
        connector_x = float(placement.point[0] * TILE_SIZE)
        connector_y = float(placement.point[1] * TILE_SIZE)
        position = self.find_connector_portal_position(placement)
        if position is None:
            return None
        anchor_point = Vec2(connector_x, connector_y)
        room_id = self.nearest_room_id_for_point(anchor_point)
        if room_id is None:
            return None
        room_node = nodes_by_id.get(room_id)
        if room_node is None or not room_node.room_name:
            label = "连接通道"
        elif len(placement.sides) >= 3:
            label = f"{room_node.room_name} 分叉"
        else:
            label = f"{room_node.room_name} 连接"
        return TeleportPortal(
            portal_id=f"portal_connector_{placement.point[0]}_{placement.point[1]}",
            edge_key=(int(placement.point[0]), int(placement.point[1])),
            position=position,
            source_room_id=room_id,
            target_room_id=room_id,
            room_id=room_id,
            label=label,
        )

    def node_uses_teleport_room(self, node: GraphRoomNode) -> bool:
        return node.map_file in {"房间组件/传送门房_左.txt", "房间组件/传送门房_右.txt"}

    def snap_portal_x(self, world_x: float) -> float:
        return float(round(world_x / TILE_SIZE) * TILE_SIZE)

    def portal_position_for_x(self, world_x: float, reference_y: float) -> Vec2:
        snapped_x = self.snap_portal_x(world_x)
        ground_y = self.nearest_plane_y_for_x(snapped_x, reference_y)
        return Vec2(snapped_x, ground_y - TILE_SIZE * 1.5)

    def find_room_centered_portal_position(self, room_region: pygame.Rect) -> Vec2 | None:
        reference_y = float(room_region.centery)
        midpoint = float(room_region.centerx)
        seen_x: set[float] = set()
        for offset in (0.0, -TILE_SIZE, TILE_SIZE, -TILE_SIZE * 2.0, TILE_SIZE * 2.0):
            candidate_x = self.snap_portal_x(midpoint + offset)
            if candidate_x in seen_x:
                continue
            seen_x.add(candidate_x)
            if candidate_x < float(room_region.left + TILE_SIZE) or candidate_x > float(room_region.right - TILE_SIZE):
                continue
            if not self.portal_column_is_walkable(candidate_x, reference_y):
                continue
            position = self.portal_position_for_x(candidate_x, reference_y)
            if not room_region.collidepoint(position.x, position.y + TILE_SIZE * 0.5):
                continue
            if self.portal_position_is_clear(position):
                return position
        return None

    def build_room_centered_teleport_portal(
        self,
        source: GraphRoomNode,
        target: GraphRoomNode,
        target_region: pygame.Rect,
    ) -> TeleportPortal | None:
        position = self.find_room_centered_portal_position(target_region)
        if position is None:
            return None
        return TeleportPortal(
            portal_id=f"portal_{source.node_id}_{target.node_id}",
            edge_key=(source.node_id, target.node_id),
            position=position,
            source_room_id=source.node_id,
            target_room_id=target.node_id,
            room_id=target.node_id,
            label=target.room_name or f"{source.node_id}->{target.node_id}",
        )

    def build_teleport_portal(
        self,
        source: GraphRoomNode,
        target: GraphRoomNode,
        source_region: pygame.Rect,
        target_region: pygame.Rect,
    ) -> TeleportPortal | None:
        corridor_bounds = self.horizontal_portal_corridor_bounds(source_region, target_region)
        if corridor_bounds is None:
            return None

        position = self.find_horizontal_portal_position(corridor_bounds[0], corridor_bounds[1], source_region, target_region)
        if position is None:
            return None
        if not self.portal_position_is_clear(position):
            return None
        room_id = target.node_id if target.room_size == "large" else source.node_id
        label = target.room_name or f"{source.node_id}->{target.node_id}"
        return TeleportPortal(
            portal_id=f"portal_{source.node_id}_{target.node_id}",
            edge_key=(source.node_id, target.node_id),
            position=position,
            source_room_id=source.node_id,
            target_room_id=target.node_id,
            room_id=room_id,
            label=label,
        )

    def horizontal_portal_corridor_bounds(self, source_region: pygame.Rect, target_region: pygame.Rect) -> tuple[float, float] | None:
        portal_half_width = TILE_SIZE
        safety_margin = TILE_SIZE * 0.75
        if source_region.right <= target_region.left:
            left_x = float(source_region.right + safety_margin)
            right_x = float(target_region.left - safety_margin)
        elif target_region.right <= source_region.left:
            left_x = float(target_region.right + safety_margin)
            right_x = float(source_region.left - safety_margin)
        else:
            return None

        if right_x - left_x < portal_half_width * 2.0 + TILE_SIZE * 0.5:
            return None
        return left_x, right_x

    def find_horizontal_portal_position(
        self,
        left_x: float,
        right_x: float,
        source_region: pygame.Rect,
        target_region: pygame.Rect,
    ) -> Vec2 | None:
        reference_candidates = [float(source_region.centery)]
        if abs(target_region.centery - source_region.centery) > 1:
            reference_candidates.append(float(target_region.centery))
        average_y = (source_region.centery + target_region.centery) * 0.5
        if all(abs(reference_y - average_y) > 1 for reference_y in reference_candidates):
            reference_candidates.append(float(average_y))

        for reference_y in reference_candidates:
            candidate_x = self.find_horizontal_portal_x(left_x, right_x, reference_y)
            if candidate_x is None:
                continue
            position = self.portal_position_for_x(candidate_x, reference_y)
            if not self.portal_matches_corridor_band(position, reference_y):
                continue
            if self.portal_position_is_clear(position):
                return position
        return None

    def find_horizontal_portal_x(self, left_x: float, right_x: float, reference_y: float) -> float | None:
        midpoint = (left_x + right_x) * 0.5
        candidate_offsets = [0.0, -TILE_SIZE, TILE_SIZE, -TILE_SIZE * 2.0, TILE_SIZE * 2.0]
        seen_x: set[float] = set()
        for offset in candidate_offsets:
            candidate_x = self.snap_portal_x(midpoint + offset)
            if candidate_x in seen_x:
                continue
            seen_x.add(candidate_x)
            if candidate_x < left_x or candidate_x > right_x:
                continue
            if not self.portal_column_is_walkable(candidate_x, reference_y):
                continue
            position = self.portal_position_for_x(candidate_x, reference_y)
            if not self.portal_matches_corridor_band(position, reference_y):
                continue
            if self.portal_position_is_clear(position):
                return candidate_x

        snapped_left = math.ceil(left_x / TILE_SIZE) * TILE_SIZE
        snapped_right = math.floor(right_x / TILE_SIZE) * TILE_SIZE
        if snapped_left > snapped_right:
            return None
        for candidate_x in range(int(snapped_left), int(snapped_right) + 1, TILE_SIZE):
            if not self.portal_column_is_walkable(candidate_x, reference_y):
                continue
            position = self.portal_position_for_x(candidate_x, reference_y)
            if not self.portal_matches_corridor_band(position, reference_y):
                continue
            if self.portal_position_is_clear(position):
                return float(candidate_x)
        return None

    def portal_matches_corridor_band(self, position: Vec2, reference_y: float) -> bool:
        return abs(position.y - reference_y) <= TILE_SIZE * 1.35

    def portal_column_is_walkable(self, world_x: float, reference_y: float) -> bool:
        ground_y = self.nearest_plane_y_for_x(world_x, reference_y)
        left_ground = self.nearest_plane_y_for_x(world_x - TILE_SIZE * 0.7, reference_y)
        right_ground = self.nearest_plane_y_for_x(world_x + TILE_SIZE * 0.7, reference_y)
        if abs(left_ground - ground_y) > TILE_SIZE * 0.45:
            return False
        if abs(right_ground - ground_y) > TILE_SIZE * 0.45:
            return False
        return True

    def portal_position_is_clear(self, position: Vec2) -> bool:
        rect = pygame.FRect(position.x - TILE_SIZE, position.y - TILE_SIZE * 1.5, TILE_SIZE * 2.0, TILE_SIZE * 3.0)
        world_room = self.level.floor_room if self.level.floor_room is not None else self.level.current_room
        if rect.left < 0.0 or rect.top < 0.0 or rect.right > float(world_room.world_width) or rect.bottom > float(world_room.world_height):
            return False
        room = self.level.current_room
        for solid in room.solids:
            if rect.colliderect(solid):
                return False
        return True

    def portal_by_id(self, portal_id: str | None) -> TeleportPortal | None:
        if portal_id is None:
            return None
        return next((portal for portal in self.teleport_portals if portal.portal_id == portal_id), None)

    def portal_is_revealed_on_map(self, portal: TeleportPortal) -> bool:
        route_map = self.route_map if self.route_map is not None else self.level.route_map_payload(self.player.center())
        if route_map is None:
            return True
        reveal_radius = max(0.0, float(route_map.get("fog_reveal_radius", 0.0)))
        if reveal_radius <= 0.0:
            return True
        reveal_points = route_map.get("fog_reveal_points", [])
        radius_sq = reveal_radius * reveal_radius
        for point in reveal_points:
            if not isinstance(point, (tuple, list)) or len(point) != 2:
                continue
            delta_x = float(point[0]) - portal.position.x
            delta_y = float(point[1]) - portal.position.y
            if delta_x * delta_x + delta_y * delta_y <= radius_sq:
                return True
        return False

    def indexed_teleport_portals(self) -> list[TeleportPortal]:
        return [
            portal
            for portal in self.teleport_portals
            if portal.activated and self.portal_is_revealed_on_map(portal)
        ]

    def portal_interaction_rect(self, portal: TeleportPortal) -> pygame.FRect:
        return pygame.FRect(portal.position.x - TILE_SIZE, portal.position.y - TILE_SIZE * 1.5, TILE_SIZE * 2, TILE_SIZE * 3)

    def overlapping_teleport_portal(self) -> TeleportPortal | None:
        player_range = self.player.rect.inflate(20, 12)
        for portal in self.teleport_portals:
            if self.portal_interaction_rect(portal).colliderect(player_range):
                return portal
        return None

    def update_teleport_portals(self) -> None:
        player_center = self.player.center()
        for portal in self.teleport_portals:
            if portal.activated:
                continue
            if (portal.position - player_center).length() > TELEPORT_ACTIVATE_DISTANCE:
                continue
            portal.activated = True
            if self.selected_teleport_portal_id is None:
                self.selected_teleport_portal_id = portal.portal_id
            self.set_message("传送锚点已激活", ACCENT_COLOR, 0.65)
            self.invalidate_route_map()

    def open_teleport_map(self, portal: TeleportPortal) -> None:
        self.teleport_map_mode = True
        self.teleport_anchor_portal_id = portal.portal_id
        self.selected_teleport_portal_id = portal.portal_id
        self.route_map_open = True
        self.route_map_focus = portal.position.copy()
        self.clamp_route_map_focus()
        self.refresh_route_map_if_needed(force=True)

    def move_selected_teleport_portal(self, move_x: int, move_y: int) -> None:
        current = self.portal_by_id(self.selected_teleport_portal_id)
        if current is None:
            return
        if move_x == 0 and move_y == 0:
            return
        axis_is_horizontal = move_x != 0
        direction_sign = 1 if (move_x if axis_is_horizontal else move_y) > 0 else -1
        best_score: tuple[float, float, float] | None = None
        best_portal: TeleportPortal | None = None
        for portal in self.indexed_teleport_portals():
            if portal.portal_id == current.portal_id:
                continue
            delta = portal.position - current.position
            primary_offset = delta.x if axis_is_horizontal else delta.y
            cross_offset = abs(delta.y) if axis_is_horizontal else abs(delta.x)
            if primary_offset * direction_sign <= 1.0:
                continue
            distance = delta.length()
            if distance <= 0.001:
                continue
            score = (abs(primary_offset), cross_offset, distance)
            if best_score is None or score < best_score:
                best_score = score
                best_portal = portal
        if best_portal is None:
            return
        self.selected_teleport_portal_id = best_portal.portal_id
        self.route_map_focus = best_portal.position.copy()
        self.clamp_route_map_focus()

    def try_begin_selected_teleport(self) -> None:
        source = self.portal_by_id(self.teleport_anchor_portal_id)
        target = self.portal_by_id(self.selected_teleport_portal_id)
        if source is None or target is None:
            self.set_message("没有可用传送锚点", ACCENT_COLOR, 0.45)
            return
        if not target.activated:
            self.set_message("目标传送门未激活", ACCENT_COLOR, 0.45)
            return
        if source.portal_id == target.portal_id:
            self.route_map_open = False
            self.teleport_map_mode = False
            return
        self.route_map_open = False
        self.teleport_map_mode = False
        self.teleport_transition = TeleportTransition(source.portal_id, target.portal_id, "depart", TELEPORT_DEPART_TIME, TELEPORT_DEPART_TIME)
        self.player.velocity.xy = (0.0, 0.0)
        self.player.invulnerability = max(self.player.invulnerability, TELEPORT_DEPART_TIME + TELEPORT_ARRIVE_TIME)
        self.add_screen_shake(0.18)
        self.set_message("启动传送", ACCENT_COLOR, 0.5)

    def update_teleport_transition(self, delta_time: float) -> bool:
        if self.teleport_transition is None:
            return False
        source = self.portal_by_id(self.teleport_transition.source_portal_id)
        target = self.portal_by_id(self.teleport_transition.target_portal_id)
        if source is None or target is None:
            self.teleport_transition = None
            return False

        active_portal = source if self.teleport_transition.phase == "depart" else target
        self.player.rect.centerx = int(active_portal.position.x)
        self.player.rect.bottom = int(active_portal.position.y + TILE_SIZE * 1.5)
        self.player.velocity.xy = (0.0, 0.0)
        self.player.action_state = "enter"
        self.teleport_transition.timer = max(0.0, self.teleport_transition.timer - delta_time)
        if self.teleport_transition.timer > 0.0:
            return True

        if self.teleport_transition.phase == "depart":
            self.player.rect.centerx = int(target.position.x)
            self.player.rect.bottom = int(target.position.y + TILE_SIZE * 1.5)
            self.level.update_active_room_from_position(self.player.center())
            if self.level.is_embedded_world_map and self.level.current_room_index != self.active_embedded_room_id:
                self.activate_embedded_room(self.level.current_room_index)
                self.projectiles.clear()
                self.room_clear_announced = self.level.current_room_index in self.cleared_room_ids
            self.teleport_anchor_portal_id = target.portal_id
            self.selected_teleport_portal_id = target.portal_id
            self.route_map_focus = target.position.copy()
            self.clamp_route_map_focus()
            self.teleport_transition = TeleportTransition(source.portal_id, target.portal_id, "arrive", TELEPORT_ARRIVE_TIME, TELEPORT_ARRIVE_TIME)
            self.add_screen_shake(0.26)
            self.invalidate_route_map()
            return True

        self.teleport_transition = None
        self.player.action_state = "neutral"
        self.set_message("完成传送", SUCCESS_COLOR, 0.55)
        return False

    def invalidate_route_map(self) -> None:
        self.route_map_dirty = True

    def refresh_route_map_if_needed(self, delta_time: float = 0.0, force: bool = False) -> None:
        self.route_map_refresh_timer = max(0.0, self.route_map_refresh_timer - delta_time)
        if force:
            self.refresh_route_map()
            return
        moved_far_enough = (self.player.center() - self.last_route_map_player_center).length_squared() >= 48.0 * 48.0
        if self.route_map_open or (self.route_map_dirty and (moved_far_enough or self.route_map_refresh_timer <= 0.0)):
            self.refresh_route_map()
            return
        if moved_far_enough:
            self.route_map_dirty = True

    def rebuild_level_state(self, floor_number: int = 1, preserve_health: bool = True) -> None:
        carried_health = self.player.health if preserve_health else None
        self.level = LevelState(floor_number=floor_number)
        self.active_embedded_room_id = self.level.current_room_index
        self.room_enemy_cache.clear()
        self.room_pickup_cache.clear()
        self.cleared_room_ids.clear()
        self.pending_boss_spawn = None
        self.boss_spawned_room_ids.clear()
        self.enemies = self.spawn_world_enemies() if self.level.is_embedded_world_map else self.spawn_room_enemies()
        self.projectiles.clear()
        self.pickups = [self.spawn_pickup(position, slot, item_id, hidden_item_id) for position, slot, item_id, hidden_item_id in self.level.current_room.item_spawns]
        self.room_clear_announced = False
        self.active_room_role = self.level.current_room.role
        self.previous_room_role = None
        self.room_role_transition = 1.0
        self.route_map_open = False
        self.route_map_focus = None
        self.rebuild_teleport_portals()
        self.invalidate_route_map()
        self.begin_room_intro(carried_health, entry_direction=1)
        self.refresh_route_map_if_needed(force=True)
        self.set_message(f"Map refreshed  |  Seed {self.level.seed}", ACCENT_COLOR, 1.2)

    def reset_route_map_focus(self) -> None:
        self.route_map_focus = self.player.center().copy()

    def clamp_route_map_focus(self) -> None:
        if self.route_map_focus is None:
            return
        if self.route_map:
            world_width = float(self.route_map.get("world_width", 0.0))
            world_height = float(self.route_map.get("world_height", 0.0))
        else:
            world_room = self.level.floor_room if self.level.floor_room is not None else self.level.current_room
            world_width = float(world_room.world_width)
            world_height = float(world_room.world_height)
        self.route_map_focus.x = max(0.0, min(self.route_map_focus.x, max(0.0, world_width)))
        self.route_map_focus.y = max(0.0, min(self.route_map_focus.y, max(0.0, world_height)))

    def active_world_enemies(self) -> list[Enemy]:
        activation_rect = pygame.FRect(
            self.player.rect.centerx - WINDOW_WIDTH * 0.9,
            self.player.rect.centery - WINDOW_HEIGHT * 0.9,
            WINDOW_WIDTH * 1.8,
            WINDOW_HEIGHT * 1.8,
        )
        active: list[Enemy] = []
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            expanded = enemy.rect.inflate(max(160.0, enemy.detection_range * 0.55), max(120.0, enemy.view_spread * 0.45))
            if enemy.is_boss or enemy.is_friendly or expanded.colliderect(activation_rect):
                active.append(enemy)
        return active

    def is_enemy_far_from_player(self, enemy: Enemy) -> bool:
        if enemy.is_boss or enemy.is_friendly:
            return False
        far_rect = pygame.FRect(
            self.player.rect.centerx - WINDOW_WIDTH * 1.8,
            self.player.rect.centery - WINDOW_HEIGHT * 1.8,
            WINDOW_WIDTH * 3.6,
            WINDOW_HEIGHT * 3.6,
        )
        expanded = enemy.rect.inflate(max(220.0, enemy.detection_range * 0.8), max(160.0, enemy.view_spread * 0.6))
        return not expanded.colliderect(far_rect)

    def camera_world_rect(self, margin: float = 0.0) -> pygame.FRect:
        return pygame.FRect(
            self.camera.x - margin,
            self.camera.y - margin,
            WINDOW_WIDTH + margin * 2.0,
            WINDOW_HEIGHT + margin * 2.0,
        )

    def visible_hostile_enemies(self, margin: float = 48.0) -> list[Enemy]:
        view_rect = self.camera_world_rect(margin)
        return [enemy for enemy in self.enemies if enemy.alive and not enemy.is_friendly and view_rect.colliderect(enemy.rect)]

    def visible_render_enemies(self, margin: float = 96.0) -> list[Enemy]:
        view_rect = self.camera_world_rect(margin)
        return [enemy for enemy in self.enemies if enemy.alive and view_rect.colliderect(enemy.rect)]

    def spawn_enemy_instance(self, position: Vec2, enemy_type: str, room_id: int | None = None, invade_from_sky: bool = False) -> Enemy:
        enemy = Enemy(position.copy(), enemy_type=enemy_type)
        enemy.embedded_room_id = room_id
        if invade_from_sky and enemy.is_boss:
            enemy.rect.x = position.x
            enemy.rect.y = position.y
            enemy.velocity.xy = (0.0, 0.0)
            enemy.movement_state = "patrol"
            enemy.action_state = "neutral"
        return enemy

    def spawn_world_enemies(self) -> list[Enemy]:
        enemies: list[Enemy] = []
        self.pending_boss_spawn = None
        for room in self.level.rooms:
            for position, enemy_type in room.enemy_spawns:
                if enemy_type == "boss":
                    self.pending_boss_spawn = (room.index, position.copy(), enemy_type)
                    continue
                enemies.append(self.spawn_enemy_instance(position, enemy_type, room.index))
        for position, enemy_type in self.level.corridor_enemy_spawns:
            enemies.append(self.spawn_enemy_instance(position, enemy_type, None))
        return enemies

    def current_room_enemies(self) -> list[Enemy]:
        if not self.level.is_embedded_world_map:
            return self.enemies
        current_room_id = self.level.current_room_index
        return [enemy for enemy in self.enemies if getattr(enemy, "embedded_room_id", current_room_id) == current_room_id]

    def current_room_has_live_enemies(self) -> bool:
        if any(enemy.alive and not enemy.is_friendly for enemy in self.current_room_enemies()):
            return True
        return self.pending_boss_spawn is not None and self.pending_boss_spawn[0] == self.level.current_room_index

    def boss_room_locked(self, room_id: int | None = None) -> bool:
        target_room_id = self.level.current_room_index if room_id is None else room_id
        return any(enemy.is_boss and enemy.alive and getattr(enemy, "embedded_room_id", target_room_id) == target_room_id for enemy in self.enemies)

    def boss_gate_side(self, room_id: int) -> str | None:
        if room_id not in self.level.room_regions:
            return None
        parent_id = self.level.graph_nodes[room_id].parent_id
        if parent_id is None or parent_id not in self.level.room_regions:
            return "left"
        room_region = self.level.room_regions[room_id]
        parent_region = self.level.room_regions[parent_id]
        return "left" if parent_region.centerx < room_region.centerx else "right"

    def boss_gate_rect(self, room_id: int) -> pygame.FRect | None:
        room_region = self.level.room_regions.get(room_id)
        if room_region is None:
            return None
        side = self.boss_gate_side(room_id)
        gate_width = float(TILE_SIZE)
        gate_height = float(TILE_SIZE * 4)
        gate_top = room_region.bottom - float(TILE_SIZE * 7)
        if side == "right":
            return pygame.FRect(room_region.right - gate_width, gate_top, gate_width, gate_height)
        return pygame.FRect(room_region.left, gate_top, gate_width, gate_height)

    def boss_exit_spawn_point(self) -> Vec2 | None:
        room = self.level.rooms[self.level.current_room_index] if self.level.is_embedded_world_map else self.level.current_room
        for position, enemy_type in room.enemy_spawns:
            if enemy_type == "boss":
                return position.copy()
        return None

    def boss_exit_door_rect(self) -> pygame.FRect | None:
        spawn_point = self.boss_exit_spawn_point()
        if spawn_point is None:
            return None
        door_width = 50.0
        door_height = 92.0
        center_x = spawn_point.x + 20.0 + TILE_SIZE * 5.0
        if self.level.is_embedded_world_map:
            room = self.active_content_room()
            room_region = self.level.room_regions.get(self.level.current_room_index)
            ground_y = float(room_region.bottom - 8) if room_region is not None else float(room.world_height - 8)
            for solid in room.solids:
                if solid.left <= center_x <= solid.right and solid.top > ground_y - TILE_SIZE * 2.2:
                    ground_y = min(ground_y, float(solid.top))
        else:
            ground_y = self.standard_ground_y_for_x(center_x)
        door_top = ground_y - door_height - TILE_SIZE
        return pygame.FRect(center_x - door_width * 0.5, door_top, door_width, door_height)

    def reset_boss_exit_door(self) -> None:
        self.boss_exit_door_delay_timer = -1.0
        self.boss_exit_door_progress = 0.0
        self.boss_exit_door_enter_timer = 0.0
        self.boss_exit_door_entering = False

    def trigger_next_floor_from_boss(self) -> None:
        next_floor = max(1, self.level.floor_number + 1)
        self.rebuild_level_state(floor_number=next_floor, preserve_health=True)
        self.active_room_role = self.level.current_room.role
        self.previous_room_role = None
        self.room_role_transition = 1.0
        self.set_message(f"进入下一张 {next_floor} 号地图", ACCENT_COLOR, 1.2)

    def update_boss_exit_door(self, delta_time: float) -> bool:
        if self.level.current_room.role != "boss" or self.boss_room_locked() or self.room_intro_active:
            self.reset_boss_exit_door()
            return False
        door_rect = self.boss_exit_door_rect()
        if door_rect is None:
            return False
        if self.boss_exit_door_entering:
            self.boss_exit_door_enter_timer = max(0.0, self.boss_exit_door_enter_timer - delta_time)
            self.boss_exit_door_progress = max(0.0, self.boss_exit_door_enter_timer / max(0.001, BOSS_EXIT_DOOR_ENTER_TIME))
            self.player.rect.centerx = door_rect.centerx
            self.player.rect.bottom = door_rect.bottom
            self.player.velocity.xy = (0.0, 0.0)
            self.player.action_state = "enter"
            if self.boss_exit_door_enter_timer <= 0.0:
                self.trigger_next_floor_from_boss()
            return True
        if self.boss_exit_door_delay_timer < 0.0 and self.boss_exit_door_progress <= 0.0:
            self.boss_exit_door_delay_timer = BOSS_EXIT_DOOR_DELAY
        if self.boss_exit_door_delay_timer > 0.0:
            self.boss_exit_door_delay_timer = max(0.0, self.boss_exit_door_delay_timer - delta_time)
            return False
        self.boss_exit_door_progress = min(1.0, self.boss_exit_door_progress + delta_time / max(0.001, BOSS_EXIT_DOOR_APPEAR_TIME))
        if self.boss_exit_door_progress >= 0.999 and self.player.rect.colliderect(door_rect.inflate(-8, -8)):
            self.boss_exit_door_entering = True
            self.boss_exit_door_enter_timer = BOSS_EXIT_DOOR_ENTER_TIME
            self.player.velocity.xy = (0.0, 0.0)
            self.add_screen_shake(0.18)
            self.set_message("踏入离场之门", ACCENT_COLOR, 0.6)
            return True
        return self.boss_exit_door_progress > 0.0

    def room_intro_door_rect(self) -> pygame.FRect:
        door_width = 46.0
        door_height = 88.0
        ground_y = self.room_intro_target_y + self.player.rect.height
        door_top = ground_y - door_height
        door_left = self.room_intro_target_x + self.player.rect.width * 0.5 - door_width * 0.5
        return pygame.FRect(door_left, door_top, door_width, door_height)

    def spawn_boss_for_room(self, room_id: int) -> None:
        if self.pending_boss_spawn is None:
            return
        pending_room_id, position, enemy_type = self.pending_boss_spawn
        if pending_room_id != room_id or room_id in self.boss_spawned_room_ids:
            return
        boss = self.spawn_enemy_instance(position, enemy_type, room_id, invade_from_sky=True)
        self.enemies.append(boss)
        self.boss_spawned_room_ids.add(room_id)
        self.pending_boss_spawn = None
        self.projectiles.clear()
        self.add_screen_shake(0.42)
        self.set_message("Boss 降临", DANGER_COLOR, 1.1)

    def enforce_embedded_boss_barrier(self) -> None:
        if not self.level.is_embedded_world_map or self.level.current_room.role != "boss":
            return
        if not self.boss_room_locked():
            return
        room_id = self.level.current_room_index
        barrier = self.boss_gate_rect(room_id)
        if barrier is None:
            return
        gate_side = self.boss_gate_side(room_id)
        margin = 2.0
        if gate_side == "right" and self.player.rect.right >= barrier.left:
            self.player.rect.right = barrier.left - margin
            self.player.velocity.x = min(0.0, self.player.velocity.x)
        elif gate_side != "right" and self.player.rect.left <= barrier.right:
            self.player.rect.left = barrier.right + margin
            self.player.velocity.x = max(0.0, self.player.velocity.x)

    def draw_boss_room_barrier(self, surface: pygame.Surface) -> None:
        if not self.level.is_embedded_world_map or self.level.current_room.role != "boss" or not self.boss_room_locked():
            return
        barrier = self.boss_gate_rect(self.level.current_room_index)
        if barrier is None:
            return
        draw_rect = pygame.Rect(int(barrier.x - self.camera.x), int(barrier.y - self.camera.y), int(barrier.width), int(barrier.height))
        overlay = self.get_effect_surface((draw_rect.width + 20, draw_rect.height + 24), "boss_room_barrier")
        outer_rect = pygame.Rect(10, 10, draw_rect.width, draw_rect.height)
        pygame.draw.rect(overlay, (238, 170, 116, 82), outer_rect, border_radius=14)
        pygame.draw.rect(overlay, (255, 232, 184, 168), outer_rect, width=3, border_radius=12)
        surface.blit(overlay, (draw_rect.x - 10, draw_rect.y - 10))

    def draw_boss_exit_door(self, surface: pygame.Surface) -> None:
        if self.boss_exit_door_progress <= 0.0:
            return
        door_rect = self.boss_exit_door_rect()
        if door_rect is None:
            return
        draw_rect = pygame.Rect(int(door_rect.x - self.camera.x), int(door_rect.y - self.camera.y), int(door_rect.width), int(door_rect.height))
        if draw_rect.right < -8 or draw_rect.left > surface.get_width() + 8:
            return
        overlay = self.get_effect_surface((draw_rect.width + 18, draw_rect.height + 22), "boss_exit_door")
        overlay.fill((0, 0, 0, 0))
        arch_rect = pygame.Rect(9, 10, draw_rect.width, draw_rect.height)
        inner_rect = arch_rect.inflate(-10, -12)
        progress = max(0.0, min(1.0, self.boss_exit_door_progress))
        eased = 1.0 - (1.0 - progress) ** 3
        arch_fill = (40, 22, 18, int(228 * eased))
        arch_edge = (168, 124, 82, int(224 * eased))
        inner_fill = (12, 10, 16, int(196 * eased))
        pygame.draw.rect(overlay, arch_fill, arch_rect, border_radius=14)
        pygame.draw.rect(overlay, inner_fill, inner_rect, border_radius=10)
        pygame.draw.rect(overlay, arch_edge, arch_rect, width=4, border_radius=14)
        surface.blit(overlay, (draw_rect.x - 9, draw_rect.y - 10))

    def begin_room_intro(self, health: int | None = None, entry_direction: int = 1) -> None:
        self.reset_boss_exit_door()
        self.sword_mania_timer = 0.0
        self.steel_guard_timer = 0.0
        self.minor_particles.clear()
        self.oppression_lifts.clear()
        room = self.level.current_room
        target_position = room.player_spawn.copy()
        self.player = Player(target_position.copy())
        if health is not None:
            self.player.health = max(1, min(health, self.player.max_health))
        if self.level.is_embedded_world_map:
            self.player.facing = 1 if entry_direction >= 0 else -1
            self.room_intro_entry_direction = 1 if entry_direction >= 0 else -1
            target_camera = Vec2(target_position.x + CAMERA_LOOK_AHEAD - WINDOW_WIDTH * 0.5, target_position.y + self.player.rect.height * 0.5 - WINDOW_HEIGHT * 0.55)
            self.room_intro_camera = self.level.current_room.clamp_camera(target_camera)
            self.room_intro_target_x = target_position.x
            self.room_intro_target_y = target_position.y
            self.player.rect.x = target_position.x
            self.player.rect.y = target_position.y
            self.room_intro_start_x = target_position.x
            self.room_intro_start_y = target_position.y
            self.room_intro_active = True
            self.room_intro_hold_timer = 1.20
            self.room_intro_door_duration = 0.85
            self.room_intro_door_timer = self.room_intro_door_duration
            self.room_intro_player_visible = False
            self.player.on_ground = True
            self.player.movement_state = "idle"
            self.player.action_state = "enter"
            self.camera = self.room_intro_camera.copy()
            self.player_afterimages.clear()
            self.projectiles.clear()
            self.activate_embedded_room(self.level.current_room_index)
            self.blade_combos.clear()
            self.sword_rain_strikes.clear()
            self.halo_shockwaves.clear()
            self.halo_cast_tier = 0
            self.halo_pulse_timer = 0.0
            self.halo_end_pulse_pending = False
            self.radiant_judgement = None
            return
        self.player.facing = 1 if entry_direction >= 0 else -1
        self.room_intro_entry_direction = 1 if entry_direction >= 0 else -1
        target_camera = Vec2(target_position.x + CAMERA_LOOK_AHEAD - WINDOW_WIDTH * 0.5, target_position.y + self.player.rect.height * 0.5 - WINDOW_HEIGHT * 0.55)
        self.room_intro_camera = self.level.current_room.clamp_camera(target_camera)
        self.room_intro_target_x = target_position.x
        self.room_intro_target_y = target_position.y
        self.player.rect.x = target_position.x
        self.player.rect.y = target_position.y
        self.room_intro_start_x = target_position.x
        self.room_intro_start_y = target_position.y
        self.room_intro_active = True
        self.room_intro_hold_timer = 1.20
        self.room_intro_door_duration = 0.85
        self.room_intro_door_timer = self.room_intro_door_duration
        self.room_intro_player_visible = False
        self.player.on_ground = True
        self.player.movement_state = "idle"
        self.player.action_state = "enter"
        self.camera = self.room_intro_camera.copy()
        self.player_afterimages.clear()
        self.projectiles.clear()
        self.pickups = [self.spawn_pickup(position, slot, item_id, hidden_item_id) for position, slot, item_id, hidden_item_id in room.item_spawns]
        self.blade_combos.clear()
        self.sword_rain_strikes.clear()
        self.halo_shockwaves.clear()
        self.halo_cast_tier = 0
        self.halo_pulse_timer = 0.0
        self.halo_end_pulse_pending = False
        self.radiant_judgement = None

    def load_current_room(self, keep_health: bool = True, entry_direction: int = 1) -> None:
        carry_health = self.player.health if keep_health else None
        if self.level.current_room.role != self.active_room_role:
            self.previous_room_role = self.active_room_role
            self.active_room_role = self.level.current_room.role
            self.room_role_transition = 0.0
        if not self.level.is_embedded_world_map:
            self.enemies = self.spawn_room_enemies()
        self.projectiles.clear()
        self.room_clear_announced = False
        self.begin_room_intro(carry_health, entry_direction)
        if self.level.current_room_index in self.cleared_room_ids:
            self.reveal_room_pickups_immediately()

    def camera_target(self) -> Vec2:
        look_x = self.player.facing * CAMERA_LOOK_AHEAD
        target = Vec2(self.player.rect.centerx + look_x - WINDOW_WIDTH * 0.5, self.player.rect.centery - WINDOW_HEIGHT * 0.55)
        return self.level.current_room.clamp_camera(target)

    def spawn_room_enemies(self) -> list[Enemy]:
        room = self.active_content_room()
        safe_radius = 280.0
        enemies: list[Enemy] = []
        for position, enemy_type in room.enemy_spawns:
            spawn = position.copy()
            delta_x = spawn.x - room.player_spawn.x
            if abs(delta_x) < safe_radius and abs(spawn.y - room.player_spawn.y) < 140.0:
                preferred_sign = 1.0 if delta_x >= 0.0 else -1.0
                if preferred_sign == 0.0:
                    preferred_sign = 1.0
                spawn.x = max(24.0, min(room.world_width - 64.0, room.player_spawn.x + preferred_sign * safe_radius))
            enemies.append(self.spawn_enemy_instance(spawn, enemy_type, getattr(room, "index", None)))
        return enemies

    def ground_y_for_x(self, world_x: float) -> float:
        room = self.level.current_room
        probe_x = max(0.0, min(world_x, room.world_width - 1.0))
        nearest_top = float(room.world_height - 8)
        for solid in room.solids:
            if solid.left <= probe_x <= solid.right and solid.top < nearest_top:
                nearest_top = float(solid.top)
        return nearest_top

    def standard_ground_y_for_x(self, world_x: float) -> float:
        room = self.level.current_room
        probe_x = max(0.0, min(world_x, room.world_width - 1.0))
        ground_top = float(room.world_height - 8)
        for solid in room.solids:
            if solid.left <= probe_x <= solid.right and solid.top > ground_top - TILE_SIZE * 2.2:
                ground_top = min(ground_top, float(solid.top))
        return ground_top

    def nearest_plane_y_for_x(self, world_x: float, reference_y: float) -> float:
        room = self.level.current_room
        probe_x = max(0.0, min(world_x, room.world_width - 1.0))
        plane_tops: list[float] = []
        for solid in room.solids:
            if solid.left <= probe_x <= solid.right:
                plane_tops.append(float(solid.top))
        for platform in room.semisolids:
            if platform.left <= probe_x <= platform.right:
                plane_tops.append(float(platform.top))
        if not plane_tops:
            return self.standard_ground_y_for_x(world_x)
        return min(plane_tops, key=lambda plane_y: (abs(plane_y - reference_y), plane_y))

    def support_plane_y_for_x(self, world_x: float, reference_bottom: float) -> float:
        room = self.level.current_room
        probe_x = max(0.0, min(world_x, room.world_width - 1.0))
        plane_tops: list[float] = []
        for solid in room.solids:
            if solid.left <= probe_x <= solid.right:
                plane_tops.append(float(solid.top))
        for platform in room.semisolids:
            if platform.left <= probe_x <= platform.right:
                plane_tops.append(float(platform.top))
        if not plane_tops:
            return self.standard_ground_y_for_x(world_x)
        lower_planes = [plane_y for plane_y in plane_tops if plane_y >= reference_bottom - TILE_SIZE * 0.35]
        if lower_planes:
            return min(lower_planes)
        return min(plane_tops, key=lambda plane_y: abs(plane_y - reference_bottom))

    def sword_rain_plane_y_for_x(self, world_x: float) -> float:
        support_y = self.support_plane_y_for_x(self.player.center().x, self.player.rect.bottom)
        room = self.level.current_room
        probe_x = max(0.0, min(world_x, room.world_width - 1.0))
        plane_tops: list[float] = []
        for solid in room.solids:
            if solid.left <= probe_x <= solid.right:
                plane_tops.append(float(solid.top))
        for platform in room.semisolids:
            if platform.left <= probe_x <= platform.right:
                plane_tops.append(float(platform.top))
        if not plane_tops:
            return self.standard_ground_y_for_x(world_x)
        reachable_planes = [plane_y for plane_y in plane_tops if plane_y >= support_y - TILE_SIZE * 0.5]
        if reachable_planes:
            return min(reachable_planes, key=lambda plane_y: (abs(plane_y - support_y), plane_y))
        return min(plane_tops, key=lambda plane_y: (abs(plane_y - support_y), plane_y))

    def sword_rain_target_for_x(self, preferred_x: float) -> Vec2:
        room = self.level.current_room
        clamped_x = max(40.0, min(room.world_width - 40.0, preferred_x))
        reference_y = self.support_plane_y_for_x(self.player.center().x, self.player.rect.bottom)
        snapped_x = self.snap_portal_x(clamped_x)
        candidate_xs: list[float] = []
        for tile_offset in range(0, 5):
            offsets = (0.0,) if tile_offset == 0 else (-TILE_SIZE * tile_offset, TILE_SIZE * tile_offset)
            for offset in offsets:
                candidate_x = max(40.0, min(room.world_width - 40.0, snapped_x + offset))
                if any(abs(candidate_x - existing_x) < 1.0 for existing_x in candidate_xs):
                    continue
                candidate_xs.append(candidate_x)

        for candidate_x in candidate_xs:
            if not self.portal_column_is_walkable(candidate_x, reference_y):
                continue
            return Vec2(candidate_x, self.sword_rain_plane_y_for_x(candidate_x))
        return Vec2(clamped_x, self.sword_rain_plane_y_for_x(clamped_x))

    def point_segment_distance(self, point: Vec2, start: Vec2, end: Vec2) -> float:
        segment = end - start
        length_sq = segment.length_squared()
        if length_sq <= 0.001:
            return (point - start).length()
        projection = max(0.0, min(1.0, (point - start).dot(segment) / length_sq))
        closest = start + segment * projection
        return (point - closest).length()

    def displace_enemy_from_halo(self, enemy: Enemy, center: Vec2, halo_radius: float, push_distance: float) -> None:
        if enemy.has_unstoppable_boss_slash():
            return
        delta = enemy.center() - center
        distance = delta.length()
        if distance <= 0.001:
            direction = Vec2(1.0 if self.player.facing >= 0 else -1.0, 0.0)
            distance = 0.0
        else:
            direction = delta.normalize()
        push_scale = 0.6 if enemy.is_boss else 1.0
        target_distance = halo_radius + push_distance * push_scale
        correction = max(0.0, target_distance - distance)
        enemy.rect.x += direction.x * correction
        enemy.rect.y += direction.y * min(correction * 0.18, push_distance * 0.14)
        enemy.velocity.x = direction.x * (240.0 + 34.0 * max(1, self.halo_cast_tier)) * push_scale
        enemy.velocity.y = min(enemy.velocity.y, -58.0 - 10.0 * max(abs(direction.y), 0.35) * max(1, self.halo_cast_tier))
        enemy.stun_timer = max(enemy.stun_timer, 0.18 + 0.04 * max(0, self.halo_cast_tier - 1))

    def launch_enemy_from_halo(self, enemy: Enemy, center: Vec2, halo_radius: float, push_distance: float, tier: int) -> None:
        if enemy.has_unstoppable_boss_slash():
            return
        delta = enemy.center() - center
        distance = delta.length()
        if distance <= 0.001:
            direction = Vec2(1.0 if self.player.facing >= 0 else -1.0, -0.18)
        else:
            direction = delta.normalize()
        if direction.y > -0.12:
            direction.y = -0.12
            direction = direction.normalize()

        launch_scale = 0.62 if enemy.is_boss else 1.0
        enemy.velocity.x = direction.x * (380.0 + 58.0 * tier) * launch_scale
        enemy.velocity.y = -(188.0 + 30.0 * tier) * (0.80 if enemy.is_boss else 1.0)
        enemy.on_ground = False
        enemy.stun_timer = max(enemy.stun_timer, 0.26 + 0.05 * max(0, tier - 1))
        enemy.movement_state = "stagger"
        enemy.halo_launch_timer = max(enemy.halo_launch_timer, 0.24 + 0.03 * max(0, tier - 1))
        enemy.halo_launch_spin = direction.x * (1.08 + 0.14 * tier)
        enemy.halo_launch_origin = center.copy()
        enemy.halo_launch_escape_radius = halo_radius + max(22.0, push_distance * (0.64 if enemy.is_boss else 0.84))
        if enemy.is_boss:
            enemy.action_state = "recoil"
            enemy.attack_startup_timer = 0.0
        else:
            enemy.hurt_timer = max(enemy.hurt_timer, 0.16 + 0.04 * max(0, tier - 1))
            enemy.attack_startup_timer = 0.0
            enemy.attack_timer = 0.0
            enemy.attack_recovery_timer = 0.0
            enemy.attack_has_hit = False
            enemy.action_state = "hurt"

    def emit_halo_shockwave(self, tier: int, damage: int, push_distance: float, radius_scale: float = 1.0, life: float = 0.28, width: int = 4, finisher: bool = False) -> None:
        halo_radius = knight_halo_radius_px(tier) * radius_scale
        center = self.player.center()
        self.halo_shockwaves.append(
            HaloShockwave(
                center=center,
                life=life,
                max_life=life,
                start_radius=max(18.0, halo_radius * 0.26),
                end_radius=halo_radius + push_distance * 0.56,
                tint=HALO_WAVE_COLOR,
                accent_tint=HALO_WAVE_ACCENT,
                width=width,
                finisher=finisher,
            )
        )
        if damage > 0:
            self.play_sound("halo_shockwave", min(1.0, 0.66 + damage * 0.02))
        self.impact_bursts.append(
            ImpactBurst(
                center=center,
                life=min(0.18, life),
                max_life=min(0.18, life),
                tint=HALO_WAVE_COLOR,
                accent_tint=HALO_WAVE_ACCENT,
                radius=max(42.0, halo_radius * 0.34),
                spoke_count=12 + max(0, tier - 1) * 2,
            )
        )

        hits = 0
        for enemy in self.enemies:
            if not enemy.alive or enemy.is_friendly:
                continue
            delta = enemy.center() - center
            if delta.length() > halo_radius + max(enemy.rect.width, enemy.rect.height) * 0.45:
                continue
            unstoppable_boss_slash = enemy.has_unstoppable_boss_slash()
            took_wave_damage = False
            if damage > 0:
                reduced_damage = max(1, int(round(damage * (0.45 if enemy.is_boss else 1.0))))
                if self.damage_enemy(enemy, reduced_damage, 0.10, "halo_wave"):
                    if not unstoppable_boss_slash:
                        enemy.stun_timer = max(enemy.stun_timer, 0.20)
                    hits += 1
                    took_wave_damage = True
            elif enemy.is_boss:
                self.register_halo_boss_tag(enemy)
            self.launch_enemy_from_halo(enemy, center, halo_radius, push_distance, tier)
            if unstoppable_boss_slash:
                continue
            enemy.velocity.x *= 0.84 if enemy.is_boss else 0.90
            enemy.velocity.y *= 0.74 if enemy.is_boss else 0.82
            enemy.halo_launch_timer = max(enemy.halo_launch_timer, 0.22 + 0.02 * max(0, tier - 3))
            enemy.halo_launch_spin *= 0.92 if took_wave_damage else 0.96
        if finisher:
            self.add_screen_shake(0.18)
        elif damage > 0:
            self.add_screen_shake(0.24)

    def set_message(self, text: str, color: tuple[int, int, int], duration: float) -> None:
        self.message = text
        self.message_color = color
        self.message_timer = duration

    def update(self, delta_time: float) -> None:
        if self.app.input.consume_action("map_toggle"):
            self.route_map_open = not self.route_map_open
            if self.route_map_open:
                if self.teleport_map_mode:
                    selected_portal = self.portal_by_id(self.selected_teleport_portal_id)
                    self.route_map_focus = None if selected_portal is None else selected_portal.position.copy()
                else:
                    self.reset_route_map_focus()
            else:
                self.teleport_map_mode = False

        if self.route_map_open:
            self.app.input.consume_action("ultimate")
            self.app.input.consume_action("interact")
            if self.app.input.consume_action("map_zoom_out"):
                self.route_map_zoom = max(0.6, self.route_map_zoom - 0.2)
            if self.app.input.consume_action("map_zoom_in"):
                self.route_map_zoom = min(2.8, self.route_map_zoom + 0.2)
            if self.teleport_map_mode:
                if self.app.input.consume_action("move_left"):
                    self.move_selected_teleport_portal(-1, 0)
                if self.app.input.consume_action("move_right"):
                    self.move_selected_teleport_portal(1, 0)
                if self.app.input.consume_action("move_up"):
                    self.move_selected_teleport_portal(0, -1)
                if self.app.input.consume_action("move_down"):
                    self.move_selected_teleport_portal(0, 1)
                selected_portal = self.portal_by_id(self.selected_teleport_portal_id)
                if selected_portal is not None:
                    self.route_map_focus = selected_portal.position.copy()
                if self.app.input.consume_action("teleport_confirm"):
                    self.try_begin_selected_teleport()
            else:
                pan_x = float(self.app.input.is_pressed("move_right")) - float(self.app.input.is_pressed("move_left"))
                pan_y = float(self.app.input.is_pressed("move_down")) - float(self.app.input.is_pressed("move_up"))
                if self.route_map_focus is None:
                    self.reset_route_map_focus()
                pan_vector = Vec2(pan_x, pan_y)
                if pan_vector.length_squared() > 0.0 and self.route_map_focus is not None:
                    pan_vector = pan_vector.normalize()
                    self.route_map_focus += pan_vector * (920.0 / max(0.8, self.route_map_zoom)) * delta_time
                    self.clamp_route_map_focus()
            if self.app.input.consume_action("pause"):
                self.route_map_open = False
                self.teleport_map_mode = False
            self.refresh_route_map_if_needed(force=True)
            return

        if self.update_teleport_transition(delta_time):
            self.refresh_route_map_if_needed(force=True)
            return

        if self.app.input.consume_action("inventory"):
            self.inventory_open = not self.inventory_open
            return

        if self.app.input.consume_action("refresh_map"):
            self.rebuild_level_state(floor_number=self.level.floor_number, preserve_health=True)
            return

        if self.inventory_open:
            self.update_inventory()
            return

        if self.app.input.consume_action("pause"):
            self.app.scene_manager.push(PauseScene(self.app))
            return

        self.message_timer = max(0.0, self.message_timer - delta_time)
        self.bullet_time_timer = max(0.0, self.bullet_time_timer - delta_time)
        self.impact_freeze_timer = max(0.0, self.impact_freeze_timer - delta_time)
        self.perfect_dodge_flash_timer = max(0.0, self.perfect_dodge_flash_timer - delta_time)
        self.perfect_dodge_zoom_timer = max(0.0, self.perfect_dodge_zoom_timer - delta_time)
        self.parry_full_flash_timer = max(0.0, self.parry_full_flash_timer - delta_time)
        self.parry_clash_timer = max(0.0, self.parry_clash_timer - delta_time)
        self.altar_awaken_timer = max(0.0, self.altar_awaken_timer - delta_time)
        self.sanity_break_timer = max(0.0, self.sanity_break_timer - delta_time)
        self.fusion_timer = max(0.0, self.fusion_timer - delta_time)
        self.fusion_cooldown = max(0.0, self.fusion_cooldown - delta_time)
        self.halo_timer = max(0.0, self.halo_timer - delta_time)
        self.halo_cooldown = max(0.0, self.halo_cooldown - delta_time)
        self.left_skill_cooldown = max(0.0, self.left_skill_cooldown - delta_time)
        self.right_skill_cooldown = max(0.0, self.right_skill_cooldown - delta_time)
        self.brain_skill_cooldown = max(0.0, self.brain_skill_cooldown - delta_time)
        self.brain_rescue_cooldown = max(0.0, self.brain_rescue_cooldown - delta_time)
        self.brain_sword_fx_timer = max(0.0, self.brain_sword_fx_timer - delta_time)
        self.brain_scripture_fx_timer = max(0.0, self.brain_scripture_fx_timer - delta_time)
        self.minor_skill_cooldown = max(0.0, self.minor_skill_cooldown - delta_time)
        if self.developer_mode_enabled and self.developer_no_cooldown:
            self.clear_developer_cooldowns()
        self.sword_mania_timer = max(0.0, self.sword_mania_timer - delta_time)
        self.steel_guard_timer = max(0.0, self.steel_guard_timer - delta_time)
        self.oppression_field_timer = max(0.0, self.oppression_field_timer - delta_time)
        if self.attack_chain_hits > 0:
            self.attack_chain_timeout = max(0.0, self.attack_chain_timeout - delta_time)
            if self.attack_chain_timeout <= 0.0:
                self.attack_chain_hits = 0
                self.brain_chain_hits = 0
        self.screen_shake = max(0.0, self.screen_shake - CAMERA_SHAKE_DECAY * delta_time)
        if self.previous_room_role is not None:
            self.room_role_transition = min(1.0, self.room_role_transition + delta_time * 2.6)
            if self.room_role_transition >= 0.999:
                self.previous_room_role = None
                self.room_role_transition = 1.0
        self.update_finisher_overlay(delta_time)
        self.update_afterimages(delta_time)
        self.update_slash_effects(delta_time)
        self.update_parry_overlay(delta_time)
        self.update_impact_bursts(delta_time)
        self.update_halo_shockwaves(delta_time)
        self.update_heart_flight(delta_time)
        self.update_pickups(delta_time)
        self.auto_collect_pickups()
        self.apply_equipment_stats()
        self.update_sanity(delta_time)
        self.update_active_skill_effects(delta_time)

        if self.impact_freeze_timer > 0.0:
            return

        simulation_delta = delta_time * (PERFECT_DODGE_SLOW_SCALE if self.bullet_time_timer > 0.0 else 1.0)

        if self.room_intro_active:
            self.update_room_intro(simulation_delta)
            return

        if self.parry_clash_enemy is not None:
            self.update_parry_clash(delta_time)
            return

        if self.execution_timer > 0.0:
            self.update_execution(delta_time)
            return

        if self.player.health <= 0:
            if self.app.input.consume_action("confirm"):
                self.level = LevelState()
                self.active_embedded_room_id = self.level.current_room_index
                self.room_enemy_cache.clear()
                self.room_pickup_cache.clear()
                self.cleared_room_ids.clear()
                self.pending_boss_spawn = None
                self.boss_spawned_room_ids.clear()
                self.enemies = self.spawn_world_enemies() if self.level.is_embedded_world_map else self.spawn_room_enemies()
                self.projectiles.clear()
                self.room_clear_announced = False
                self.equipment = EquipmentState()
                self.active_room_role = self.level.current_room.role
                self.previous_room_role = None
                self.room_role_transition = 1.0
                self.sanity = SANITY_MAX
                self.sanity_break_timer = SANITY_BREAK_CHECK_TIME
                self.attack_chain_hits = 0
                self.brain_chain_hits = 0
                self.attack_chain_timeout = 0.0
                self.fusion_timer = 0.0
                self.fusion_cooldown = 0.0
                self.halo_timer = 0.0
                self.halo_cooldown = 0.0
                self.halo_cast_tier = 0
                self.halo_pulse_timer = 0.0
                self.halo_end_pulse_pending = False
                self.halo_shockwaves.clear()
                self.left_skill_cooldown = 0.0
                self.right_skill_cooldown = 0.0
                self.brain_skill_cooldown = 0.0
                self.brain_rescue_cooldown = 0.0
                self.minor_skill_cooldown = 0.0
                self.sword_mania_timer = 0.0
                self.steel_guard_timer = 0.0
                self.shield_bastion_timer = SHIELD_BASTION_INTERVAL
                self.oppression_field_timer = 0.0
                self.oppression_field_duration = 0.0
                self.oppression_field_radius = 0.0
                self.player_damage_multiplier = 1.0
                self.control_duration_multiplier = 1.0
                self.minor_particles.clear()
                self.oppression_lifts.clear()
                self.sword_rain_strikes.clear()
                self.route_map_focus = None
                self.teleport_map_mode = False
                self.teleport_anchor_portal_id = None
                self.selected_teleport_portal_id = None
                self.teleport_transition = None
                self.rebuild_teleport_portals()
                self.invalidate_route_map()
                self.refresh_route_map_if_needed(force=True)
                self.begin_room_intro()
            return

        self.handle_equipment_actions()
        self.update_teleport_portals()

        if self.app.input.consume_action("attack"):
            self.player.queue_attack()
        if self.app.input.consume_action("block"):
            self.player.queue_block()

        axis = self.app.input.movement_axis()
        if self.app.input.consume_action("jump"):
            if self.app.input.is_pressed("move_down"):
                self.player.request_drop_through()
            else:
                self.player.request_jump()

        player_result = self.player.update(
            delta_time=simulation_delta,
            axis=axis,
            jump_held=self.app.input.is_pressed("jump"),
            jump_released=self.app.input.jump_released(),
            wants_dash=self.app.input.consume_action("dash"),
            wants_block=False,
            level=self.level,
        )

        if player_result.dash_started:
            dodge_result = self.try_trigger_perfect_dodge()
            if dodge_result == "blink_cut":
                self.player.mark_perfect_avoid()
                self.set_message("Blink Cut", ATTACK_COLOR, 0.22)
            elif dodge_result == "perfect_dodge":
                self.player.mark_perfect_avoid()
                self.set_message("Perfect Dodge", SUCCESS_COLOR, 0.28)

        projectile_damage = self.update_projectiles(simulation_delta)

        if player_result.attack_became_active:
            hits = self.resolve_player_attack_hits()
            if hits > 0:
                self.set_message(f"Hit {hits} target" + ("s" if hits > 1 else ""), SUCCESS_COLOR, 0.3)

        dash_hits = self.apply_empowered_dash_hits()
        if dash_hits > 0:
            self.play_sound("dash_slice")
            self.add_screen_shake(0.38)
            self.set_hitstop(DASH_STRIKE_HITSTOP)
            self.set_message("Phantom Rush", PLAYER_PARRY_COLOR, 0.2)

        total_damage = 0
        active_enemies = self.active_world_enemies()
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            if self.oppression_lift_for(enemy) is not None:
                continue
            hostile_targets = [candidate for candidate in active_enemies if candidate is not enemy]
            enemy_result = enemy.update(
                simulation_delta,
                self.player,
                self.level,
                hostile_targets,
                distant_behavior=self.level.is_embedded_world_map and self.is_enemy_far_from_player(enemy),
            )
            if enemy_result.attack_started:
                self.play_sound(f"enemy_{enemy_result.attack_profile}")
                if enemy_result.attack_profile == "lunge":
                    self.add_screen_shake(0.12)
                elif enemy_result.attack_profile == "rift":
                    self.add_screen_shake(0.22)
                    self.set_message("Rift Slash", RIFT_SLASH_COLOR, 0.38)
                    self.trigger_boss_rift_effect(enemy)
            if enemy_result.projectile_spawn is not None:
                self.spawn_projectile(enemy_result.projectile_spawn)
            total_damage += enemy_result.damage
            if enemy_result.parried:
                self.play_sound("parry")
                self.trigger_parry_impact((self.player.center() + enemy.center()) * 0.5)
                self.add_screen_shake(0.3)
                self.set_hitstop(PARRY_HITSTOP)
                self.start_parry_clash(enemy)
                self.set_message("Parry Execution", ACCENT_COLOR, 0.45)
                break
            if enemy_result.guarded:
                self.play_sound("guard")
                self.add_screen_shake(0.16)
                self.set_hitstop(GUARD_HITSTOP)
                self.set_message("Guard", PLAYER_BLOCK_COLOR, 0.2)

        self.resolve_friendly_enemy_hits()
        self.trigger_boss_heart_release()
        expiring_elites = [enemy for enemy in self.enemies if not enemy.alive and enemy.is_friendly and enemy.enemy_type == "elite_knight" and enemy.summon_timer <= 0.0]
        for elite in expiring_elites:
            self.impact_bursts.append(
                ImpactBurst(
                    center=elite.center(),
                    life=0.30,
                    max_life=0.30,
                    tint=(112, 190, 176),
                    accent_tint=(202, 238, 228),
                    radius=46.0,
                    spoke_count=10,
                )
            )
        if self.execution_timer <= 0.0:
            self.enemies = [enemy for enemy in self.enemies if enemy.alive]

        total_damage += projectile_damage
        if total_damage > 0:
            death_ward_triggered = self.player.death_ward_triggered
            scripture_triggered = self.try_trigger_brain_rescue()
            self.apply_sanity_damage(total_damage)
            self.add_screen_shake(0.22)
            if death_ward_triggered:
                self.impact_bursts.append(
                    ImpactBurst(
                        center=self.player.center(),
                        life=0.32,
                        max_life=0.32,
                        tint=PLAYER_PARRY_COLOR,
                        accent_tint=RIFT_SLASH_ACCENT,
                        radius=96.0,
                        spoke_count=16,
                    )
                )
                self.player_afterimages.extend(
                    [
                        {"rect": self.player.rect.inflate(10, 6), "life": PLAYER_AFTERIMAGE_LIFETIME},
                        {"rect": self.player.rect.inflate(26, 14), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.72},
                    ]
                )
                self.set_message("Paladin Heart: Death Ward", PLAYER_PARRY_COLOR, 0.7)
            elif not scripture_triggered:
                self.set_message(f"Took {total_damage} damage", DANGER_COLOR, 0.35)
            self.player.death_ward_triggered = False

        if not self.current_room_has_live_enemies() and self.level.current_room_index not in self.cleared_room_ids:
            self.cleared_room_ids.add(self.level.current_room_index)
            self.awaken_room_pickups()
            self.room_clear_announced = True
            if self.level.current_room.role == "boss":
                self.set_message("Boss 已击败，继续前进", SUCCESS_COLOR, 1.15)
            else:
                self.set_message("房间已清空，继续前进", SUCCESS_COLOR, 1.0)

        self.level.update_active_room_from_position(self.player.center())
        if self.level.is_embedded_world_map and self.level.current_room_index != self.active_embedded_room_id:
            self.activate_embedded_room(self.level.current_room_index)
            self.projectiles.clear()
            self.room_clear_announced = self.level.current_room_index in self.cleared_room_ids
        self.enforce_embedded_boss_barrier()
        self.update_room_progression(simulation_delta)
        target = self.camera_target()
        blend = 1.0 - math.exp(-CAMERA_SMOOTHING * simulation_delta)
        self.camera = self.camera.lerp(target, blend)

    def update_inventory(self) -> None:
        if self.app.input.consume_action("inventory") or self.app.input.consume_action("confirm"):
            self.inventory_open = False

    def apply_equipment_stats(self) -> None:
        tier = knight_tier(self.equipment)
        brain_item = self.equipment.equipped["brain"]
        brain_tier = effective_tier_for_slot(self.equipment, "brain")
        sword_tier = self.minor_tier("sword")
        shield_tier = self.minor_tier("shield")
        control_tier = self.minor_tier("control")
        base_combo_bonus = combo_speed_bonus_percent(self.attack_chain_hits)
        self.player_size_bonus = knight_size_bonus_percent(tier)
        self.player.defense_multiplier = 1.0 + knight_defense_bonus_percent(tier) / 100.0
        self.player.attack_speed_multiplier = 1.0
        self.player.attack_reach_multiplier = 1.12 if self.equipment.equipped["left_eye"] == "knight_left_eye_blade" else 1.0
        self.player.move_speed_multiplier = 1.0 + base_combo_bonus / 100.0
        self.player_damage_multiplier = 1.0
        self.control_duration_multiplier = 1.0
        if is_knight_brain_sword(brain_item):
            target_bonus = sword_brain_speed_bonus_percent(self.attack_chain_hits)
            self.player.move_speed_multiplier += max(0.0, target_bonus - base_combo_bonus) / 100.0
        elif is_knight_brain_scripture(brain_item) and self.has_active_major("brain") and brain_tier >= 4:
            self.player.defense_multiplier *= SCRIPTURE_BRAIN_DAMAGE_REDUCTION_MULTIPLIER
        if sword_tier >= 3:
            self.player_damage_multiplier *= 1.35
            self.player.attack_reach_multiplier *= 1.3
        elif sword_tier >= 2:
            self.player_damage_multiplier *= 1.1
        if self.sword_mania_timer > 0.0:
            self.player_damage_multiplier *= 2.0
            self.player.move_speed_multiplier *= SWORD_MANIA_MOVE_SPEED_MULTIPLIER
        if shield_tier >= 3:
            self.player.defense_multiplier *= 1.25
        elif shield_tier >= 2:
            self.player.defense_multiplier *= 1.10
        if control_tier >= 3:
            self.control_duration_multiplier = 1.5
        elif control_tier >= 2:
            self.control_duration_multiplier = 1.3
        if self.fusion_timer <= 0.0 or self.halo_timer > 0.0 or self.equipment.equipped["heart"] != "knight_heart" or tier < 4:
            self.player.death_ward_available = False
        self.player.attack_damage_bonus = PALADIN_FUSION_BONUS_DAMAGE if self.fusion_timer > 0.0 else 0
        self.player.dash_locked = self.fusion_timer > 0.0
        self.player.forced_move_speed = PALADIN_FUSION_SPEED if self.fusion_timer > 0.0 else 0.0
        self.player.can_block = is_knight_brain(brain_item) and self.has_active_major("brain") and brain_tier >= 1
        if not self.player.can_block:
            self.player.block_request_timer = 0.0
            self.player.block_timer = 0.0
            self.player.block_cooldown = 0.0
            self.player.guard_timer = 0.0
            self.player.parry_timer = 0.0
        if self.fusion_timer > 0.0:
            self.player.move_speed_multiplier = max(1.0, PALADIN_FUSION_SPEED / 240.0)
        self.player.jump_multiplier = 0.62 if self.fusion_timer > 0.0 else 1.0

    def minor_tier(self, archetype: str) -> int:
        if self.developer_mode_enabled and self.developer_minor_override == archetype:
            return 4
        return knight_minor_tier(self.equipment, archetype)

    def player_damage_value(self, amount: int, source: str) -> int:
        if source in {"melee", "dash", "blink_cut", "execution", "blade_combo", "judgement"}:
            return max(1, int(round(amount * self.player_damage_multiplier)))
        return amount

    def emit_minor_particles(
        self,
        center: Vec2,
        tint: tuple[int, int, int],
        accent_tint: tuple[int, int, int],
        count: int,
        radius: float = 18.0,
        upward_bias: float = 0.0,
    ) -> None:
        for _ in range(count):
            angle = random.uniform(0.0, math.tau)
            speed = random.uniform(28.0, 118.0)
            offset = Vec2(math.cos(angle), math.sin(angle)) * random.uniform(0.0, radius)
            velocity = Vec2(math.cos(angle), math.sin(angle)) * speed
            velocity.y -= upward_bias + random.uniform(10.0, 56.0)
            self.minor_particles.append(
                MinorParticle(
                    position=center + offset,
                    velocity=velocity,
                    life=random.uniform(0.28, 0.54),
                    max_life=random.uniform(0.28, 0.54),
                    tint=tint,
                    accent_tint=accent_tint,
                    radius=random.uniform(2.0, 4.6),
                )
            )

    def update_minor_particles(self, delta_time: float) -> None:
        alive_particles: list[MinorParticle] = []
        for particle in self.minor_particles:
            particle.life = max(0.0, particle.life - delta_time)
            if particle.life <= 0.0:
                continue
            particle.position += particle.velocity * delta_time
            particle.velocity.x *= max(0.0, 1.0 - delta_time * 2.4)
            particle.velocity.y = particle.velocity.y * max(0.0, 1.0 - delta_time * 2.0) + 38.0 * delta_time
            alive_particles.append(particle)
        self.minor_particles = alive_particles

    def refresh_summoner_buffs(self, delta_time: float) -> None:
        summon_tier = self.minor_tier("summon")
        health_multiplier = 1.0
        move_multiplier = 1.0
        damage_multiplier = 1.0
        if summon_tier >= 3:
            health_multiplier = 1.4
            damage_multiplier = 1.3
        elif summon_tier >= 2:
            health_multiplier = 1.2
            move_multiplier = 1.1
        for enemy in self.enemies:
            if not enemy.is_friendly:
                continue
            if not (enemy.is_summoned_ally() or enemy.is_controlled_ally()):
                continue
            previous_max = max(1, enemy.max_health)
            health_ratio = enemy.health / previous_max if previous_max > 0 else 1.0
            target_max = max(1, int(enemy.base_max_health * health_multiplier))
            enemy.max_health = target_max
            enemy.health = max(1, min(target_max, int(round(target_max * health_ratio)))) if enemy.alive else 0
            enemy.move_speed = enemy.base_move_speed * move_multiplier
            enemy.chase_speed = enemy.base_chase_speed * move_multiplier
            enemy.damage_multiplier = damage_multiplier
            if summon_tier >= 2 and random.random() < min(1.0, delta_time * 7.5):
                self.emit_minor_particles(enemy.center(), SUMMONER_TINT, SUMMONER_ACCENT, 1, radius=14.0, upward_bias=22.0)

    def oppression_lift_for(self, enemy: Enemy) -> OppressionLift | None:
        return next((lift for lift in self.oppression_lifts if lift.enemy is enemy), None)

    def update_oppression_lifts(self, delta_time: float) -> None:
        active_lifts: list[OppressionLift] = []
        for lift in self.oppression_lifts:
            enemy = lift.enemy
            if not enemy.alive:
                continue
            lift.elapsed = min(lift.duration, lift.elapsed + delta_time)
            progress = lift.elapsed / max(0.001, lift.duration)
            if progress < 0.22:
                rise_ratio = 1.0 - (1.0 - progress / 0.22) ** 3
            elif progress < 0.82:
                rise_ratio = 1.0
            else:
                slam_ratio = min(1.0, (progress - 0.82) / 0.18)
                rise_ratio = max(0.0, 1.0 - slam_ratio ** 0.58)
            enemy.velocity.xy = (0.0, 0.0)
            enemy.action_state = "hurt"
            enemy.movement_state = "stagger"
            enemy.stun_timer = max(enemy.stun_timer, delta_time * 2.0)
            enemy.rect.bottom = lift.ground_bottom - lift.lift_height * rise_ratio
            if random.random() < min(1.0, delta_time * (18.0 if progress < 0.82 else 28.0)):
                orbit_center = Vec2(enemy.rect.centerx, enemy.rect.bottom - enemy.rect.height * 0.28)
                self.emit_minor_particles(orbit_center, OPPRESSION_TINT, OPPRESSION_ACCENT, 1, radius=16.0, upward_bias=8.0)
            if progress >= 1.0:
                enemy.rect.bottom = lift.ground_bottom
                slam_damage = max(1, int(enemy.max_health * OPPRESSION_DAMAGE_RATIO))
                self.damage_enemy(enemy, slam_damage, 0.20, "oppression", ignore_invulnerability=True)
                enemy.stun_timer = max(enemy.stun_timer, 0.45 * self.control_duration_multiplier)
                enemy.velocity.y = max(enemy.velocity.y, 260.0)
                self.impact_bursts.append(
                    ImpactBurst(
                        center=enemy.center(),
                        life=0.34,
                        max_life=0.34,
                        tint=OPPRESSION_TINT,
                        accent_tint=OPPRESSION_ACCENT,
                        radius=78.0,
                        spoke_count=14,
                    )
                )
                self.emit_minor_particles(enemy.center(), OPPRESSION_TINT, OPPRESSION_ACCENT, 18, radius=28.0, upward_bias=30.0)
                self.add_screen_shake(0.34)
                continue
            active_lifts.append(lift)
        self.oppression_lifts = active_lifts

    def update_minor_passives(self, delta_time: float) -> None:
        self.update_minor_particles(delta_time)
        self.update_oppression_lifts(delta_time)
        self.refresh_summoner_buffs(delta_time)

        sword_tier = self.minor_tier("sword")
        shield_tier = self.minor_tier("shield")

        if sword_tier >= 2 and random.random() < min(1.0, delta_time * (8.0 + sword_tier * 2.0 + (20.0 if self.sword_mania_timer > 0.0 else 0.0))):
            self.emit_minor_particles(
                self.player.center(),
                SWORD_MANIA_TINT,
                SWORD_MANIA_ACCENT,
                8 if self.sword_mania_timer > 0.0 else 1 + max(0, sword_tier - 2),
                radius=34.0 if self.sword_mania_timer > 0.0 else 22.0 + sword_tier * 5.0,
                upward_bias=30.0 if self.sword_mania_timer > 0.0 else 18.0,
            )

        if shield_tier >= 3:
            self.shield_bastion_timer = max(0.0, self.shield_bastion_timer - delta_time)
            if self.shield_bastion_timer <= 0.0:
                self.shield_bastion_timer = SHIELD_BASTION_INTERVAL
                self.player.temporary_shield = max(self.player.temporary_shield, 10)
                self.player.shield_timer = max(self.player.shield_timer, SHIELD_BASTION_DURATION)
                self.emit_minor_particles(self.player.center(), STEEL_GUARD_TINT, STEEL_GUARD_ACCENT, 10, radius=18.0, upward_bias=20.0)
                self.impact_bursts.append(
                    ImpactBurst(
                        center=self.player.center(),
                        life=0.26,
                        max_life=0.26,
                        tint=STEEL_GUARD_TINT,
                        accent_tint=STEEL_GUARD_ACCENT,
                        radius=58.0,
                        spoke_count=12,
                    )
                )
        else:
            self.shield_bastion_timer = SHIELD_BASTION_INTERVAL

        if self.steel_guard_timer > 0.0 and random.random() < min(1.0, delta_time * 14.0):
            self.emit_minor_particles(self.player.center(), STEEL_GUARD_TINT, STEEL_GUARD_ACCENT, 2, radius=20.0, upward_bias=14.0)

    def activate_sword_mania(self) -> bool:
        self.sword_mania_timer = max(self.sword_mania_timer, SWORD_MANIA_DURATION)
        current_health = self.player.health
        self.player.health = max(1, int(math.floor(current_health * 0.5)))
        self.emit_minor_particles(self.player.center(), SWORD_MANIA_TINT, SWORD_MANIA_ACCENT, 54, radius=46.0, upward_bias=36.0)
        self.impact_bursts.append(
            ImpactBurst(
                center=self.player.center(),
                life=0.32,
                max_life=0.32,
                tint=SWORD_MANIA_TINT,
                accent_tint=SWORD_MANIA_ACCENT,
                radius=86.0,
                spoke_count=18,
            )
        )
        self.add_screen_shake(0.28)
        return True

    def activate_oppression_field(self) -> int:
        radius = OPPRESSION_FIELD_RADIUS
        affected = 0
        field_center_x = self.player.center().x
        field_ground_y = self.support_plane_y_for_x(field_center_x, self.player.rect.bottom)
        self.oppression_field_center = Vec2(field_center_x, field_ground_y)
        self.oppression_field_radius = radius
        self.oppression_field_duration = OPPRESSION_FIELD_VISUAL_TIME
        self.oppression_field_timer = OPPRESSION_FIELD_VISUAL_TIME
        for enemy in self.enemies:
            if not enemy.alive or enemy.is_friendly:
                continue
            if self.oppression_lift_for(enemy) is not None:
                continue
            if (enemy.center() - self.player.center()).length() > radius:
                continue
            self.oppression_lifts.append(
                OppressionLift(
                    enemy=enemy,
                    ground_bottom=enemy.rect.bottom,
                    duration=OPPRESSION_DURATION,
                    lift_height=random.uniform(TILE_SIZE * 6.8, TILE_SIZE * 9.6),
                )
            )
            affected += 1
        if affected > 0:
            self.emit_minor_particles(self.oppression_field_center, OPPRESSION_TINT, OPPRESSION_ACCENT, 26, radius=radius * 0.42, upward_bias=24.0)
            self.add_screen_shake(0.24)
        return affected

    def format_status_seconds(self, seconds: float) -> str:
        if seconds >= 10.0:
            return f"{seconds:.0f}s"
        if seconds >= 1.0:
            return f"{seconds:.1f}s"
        return f"{seconds:.2f}s"

    def hud_status_bars(self) -> list[HudStatusBar]:
        bars: list[HudStatusBar] = []
        if is_knight_brain_sword(self.equipment.equipped["brain"]) and self.has_active_major("brain"):
            hit_goal = knight_shield_hit_goal(max(1, effective_tier_for_slot(self.equipment, "brain")))
            if hit_goal > 0:
                progress_hits = max(0, min(hit_goal, self.brain_chain_hits))
                bars.append(
                    HudStatusBar(
                        key="brain_hits",
                        label="",
                        ratio=max(0.0, min(1.0, progress_hits / hit_goal)),
                        fill_color=(255, 206, 118),
                        back_color=(94, 68, 22),
                        edge_color=(255, 238, 182),
                    )
                )
        if self.player.has_halo_barrier():
            barrier_hit_goal = 2
            barrier_hits = max(0, min(barrier_hit_goal, self.player.halo_barrier_hit_count))
            bars.append(
                HudStatusBar(
                    key="halo_hits",
                    label="",
                    ratio=max(0.0, min(1.0, barrier_hits / barrier_hit_goal)),
                    fill_color=(120, 198, 255),
                    back_color=(34, 62, 92),
                    edge_color=(216, 244, 255),
                )
            )
        return bars

    def draw_sword_mania_border(self, surface: pygame.Surface) -> None:
        if self.sword_mania_timer <= 0.0:
            return
        overlay = self.get_overlay_surface(surface, "sword_mania_border")
        ratio = self.sword_mania_timer / SWORD_MANIA_DURATION if SWORD_MANIA_DURATION > 0.0 else 0.0
        pulse = 0.45 + 0.55 * math.sin(pygame.time.get_ticks() * 0.014)
        width = max(10, int(16 + 14 * pulse))
        edge_alpha = int(56 + 92 * ratio * pulse)
        accent_alpha = int(34 + 84 * ratio)
        w = surface.get_width()
        h = surface.get_height()
        pygame.draw.rect(overlay, (8, 0, 0, edge_alpha), pygame.Rect(0, 0, w, h), width=width, border_radius=22)
        pygame.draw.rect(overlay, (*SWORD_MANIA_TINT, accent_alpha), pygame.Rect(8, 8, w - 16, h - 16), width=max(4, width // 3), border_radius=18)
        for offset in range(0, w, 64):
            spike_height = int(10 + 16 * pulse)
            pygame.draw.line(overlay, (*SWORD_MANIA_TINT, int(44 + 58 * pulse)), (offset, 0), (offset + 28, spike_height), width=2)
            pygame.draw.line(overlay, (*SWORD_MANIA_ACCENT, int(62 + 48 * ratio)), (offset, h), (offset + 24, h - spike_height), width=2)
        for offset in range(0, h, 72):
            spike_width = int(12 + 18 * pulse)
            pygame.draw.line(overlay, (*SWORD_MANIA_TINT, int(38 + 64 * pulse)), (0, offset), (spike_width, offset + 22), width=2)
            pygame.draw.line(overlay, (*SWORD_MANIA_ACCENT, int(54 + 52 * ratio)), (w, offset), (w - spike_width, offset + 22), width=2)
        surface.blit(overlay, (0, 0))

    def activate_steel_guard(self) -> bool:
        self.player.temporary_shield = max(self.player.temporary_shield, 100)
        self.player.shield_timer = max(self.player.shield_timer, STEEL_GUARD_DURATION)
        self.steel_guard_timer = max(self.steel_guard_timer, STEEL_GUARD_DURATION)
        self.emit_minor_particles(self.player.center(), STEEL_GUARD_TINT, STEEL_GUARD_ACCENT, 22, radius=24.0, upward_bias=18.0)
        self.impact_bursts.append(
            ImpactBurst(
                center=self.player.center(),
                life=0.34,
                max_life=0.34,
                tint=STEEL_GUARD_TINT,
                accent_tint=STEEL_GUARD_ACCENT,
                radius=96.0,
                spoke_count=20,
            )
        )
        return True

    def try_activate_minor_skill(self) -> None:
        if self.minor_skill_cooldown > 0.0:
            self.set_message("Minor active on cooldown", ACCENT_COLOR, 0.35)
            return
        triggered: list[str] = []
        if self.minor_tier("sword") >= 4 and self.activate_sword_mania():
            triggered.append("Sword Mania")
        oppression_hits = 0
        if self.minor_tier("control") >= 4:
            oppression_hits = self.activate_oppression_field()
            if oppression_hits > 0:
                triggered.append("Oppression Field")
        if self.minor_tier("shield") >= 4 and self.activate_steel_guard():
            triggered.append("Steel Guard")
        if not triggered:
            self.set_message("No T4 minor active ready", ACCENT_COLOR, 0.4)
            return
        self.minor_skill_cooldown = MINOR_SKILL_COOLDOWN
        if oppression_hits > 0:
            self.set_message("  |  ".join(triggered) + f" x{oppression_hits}", SUCCESS_COLOR, 0.7)
        else:
            self.set_message("  |  ".join(triggered), SUCCESS_COLOR, 0.7)

    def spawn_pickup(self, position: Vec2, slot: str, item_id: str | None, hidden_item_id: str | None = None) -> EquipmentPickup:
        return EquipmentPickup(
            position=Vec2(position),
            slot=slot,
            fixture_kind="altar",
            item_id=item_id,
            hidden_item_id=hidden_item_id,
            reveal_progress=1.0 if item_id is not None else 0.0,
        )

    def has_active_major(self, slot: str) -> bool:
        heart_id = self.equipment.equipped["heart"]
        slot_id = self.equipment.equipped[slot]
        if slot_id is None:
            return False
        if slot == "heart" or heart_id is None:
            return True
        return get_equipment(heart_id).series == get_equipment(slot_id).series

    def change_sanity(self, delta: float) -> None:
        self.sanity = max(0.0, min(SANITY_MAX, self.sanity + delta))

    def sanity_reward_for_kill(self, kill_method: str, enemy: Enemy) -> float:
        reward_map = {
            "melee": 3.0,
            "dash": 4.0,
            "blink_cut": 6.0,
            "execution": 8.0,
            "halo_wave": 2.0,
            "blade_combo": 4.0,
            "rain": 3.0,
            "judgement": 5.0,
            "fusion": 4.0,
            "reflect": 3.0,
        }
        reward = reward_map.get(kill_method, 2.0)
        if enemy.is_boss:
            reward *= 2.0
        return reward

    def reward_sanity_for_kill(self, enemy: Enemy, kill_method: str) -> None:
        if not self.player.alive:
            return
        self.change_sanity(self.sanity_reward_for_kill(kill_method, enemy))

    def register_halo_boss_tag(self, enemy: Enemy) -> None:
        if not enemy.alive or not enemy.is_boss or not self.player.has_halo_barrier():
            return
        halo_center = self.player.center()
        halo_radius = self.player.halo_barrier_radius
        tag_radius = halo_radius + max(enemy.rect.width, enemy.rect.height) * 0.45
        if (enemy.center() - halo_center).length() > tag_radius:
            return
        self.player.register_halo_barrier_hit()

    def damage_enemy(self, enemy: Enemy, amount: int, invuln: float, kill_method: str, ignore_invulnerability: bool = False) -> bool:
        if enemy.is_friendly:
            return False
        was_alive = enemy.alive
        if not enemy.take_damage(amount, invuln, ignore_invulnerability):
            return False
        self.register_halo_boss_tag(enemy)
        self.on_player_hits(1)
        if was_alive and not enemy.alive:
            self.reward_sanity_for_kill(enemy, kill_method)
        return True

    def resolve_player_attack_hits(self) -> int:
        attack_rect = self.player.attack_hitbox()
        hits = 0
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            if not attack_rect.colliderect(enemy.rect):
                continue
            if not self.damage_enemy(enemy, self.player_damage_value(PLAYER_ATTACK_DAMAGE + self.player.attack_damage_bonus, "melee"), ENEMY_IFRAMES, "melee"):
                continue
            if not enemy.has_unstoppable_boss_slash():
                enemy.velocity.x = 180.0 * self.player.facing
                enemy.velocity.y = -120.0
            hits += 1
        return hits

    def on_player_hits(self, hits: int) -> None:
        if hits <= 0:
            return
        self.attack_chain_hits += hits
        self.attack_chain_timeout = combo_timeout_seconds(self.attack_chain_hits)
        brain_item = self.equipment.equipped["brain"]
        if not is_knight_brain_sword(brain_item) or not self.has_active_major("brain"):
            self.brain_chain_hits = 0
            return
        brain_tier = max(1, effective_tier_for_slot(self.equipment, "brain"))
        self.brain_chain_hits += hits
        threshold = knight_shield_hit_goal(brain_tier)
        if threshold <= 0 or self.brain_chain_hits < threshold:
            return
        self.brain_chain_hits = 0
        self.player.temporary_shield = max(self.player.temporary_shield, 16 + brain_tier * 5)
        self.player.shield_timer = max(self.player.shield_timer, 5.0)
        self.brain_sword_fx_timer = max(self.brain_sword_fx_timer, SWORD_BRAIN_EFFECT_TIME)
        self.player.flash_timer = max(self.player.flash_timer, 0.18)
        self.add_screen_shake(0.18)
        self.player_afterimages.extend(
            [
                {"rect": self.player.rect.inflate(6, 0), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.82},
                {"rect": self.player.rect.inflate(18, 8), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.58},
            ]
        )
        self.impact_bursts.append(
            ImpactBurst(
                center=self.player.center(),
                life=0.24,
                max_life=0.24,
                tint=(122, 198, 255),
                accent_tint=(218, 244, 255),
                radius=54.0 + brain_tier * 8.0,
                spoke_count=12 + brain_tier,
            )
        )
        self.set_message("Shield Rhythm", PLAYER_PARRY_COLOR, 0.42)

    def try_activate_brain_skill(self) -> None:
        brain_item = self.equipment.equipped["brain"]
        if brain_item is None:
            self.set_message("No brain equipped", ACCENT_COLOR, 0.35)
            return
        if is_knight_brain_sword(brain_item):
            self.set_message("Oathblade is passive", ACCENT_COLOR, 0.35)
            return
        if is_knight_brain_scripture(brain_item):
            self.try_activate_scripture_restore()

    def try_activate_scripture_restore(self) -> bool:
        if not is_knight_brain_scripture(self.equipment.equipped["brain"]) or not self.has_active_major("brain"):
            self.set_message("Scripture inactive", ACCENT_COLOR, 0.35)
            return False
        if self.brain_skill_cooldown > 0.0:
            self.set_message("Scripture on cooldown", ACCENT_COLOR, 0.35)
            return False
        tier = max(1, effective_tier_for_slot(self.equipment, "brain"))
        heal_amount = SCRIPTURE_BRAIN_HEAL_AMOUNT + tier * 4
        sanity_amount = SCRIPTURE_BRAIN_SANITY_RESTORE + tier * 6.0
        self.player.health = min(self.player.max_health, self.player.health + heal_amount)
        self.change_sanity(sanity_amount)
        self.brain_skill_cooldown = PALADIN_SCRIPTURE_COOLDOWN
        self.brain_scripture_fx_timer = max(self.brain_scripture_fx_timer, SCRIPTURE_BRAIN_EFFECT_TIME)
        self.player.flash_timer = max(self.player.flash_timer, 0.3)
        self.add_screen_shake(0.24)
        self.player_afterimages.extend(
            [
                {"rect": self.player.rect.inflate(8, 4), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.95},
                {"rect": self.player.rect.inflate(22, 12), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.72},
                {"rect": self.player.rect.inflate(38, 18), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.5},
            ]
        )
        self.impact_bursts.append(
            ImpactBurst(
                center=self.player.center(),
                life=0.34,
                max_life=0.34,
                tint=SANITY_COLOR,
                accent_tint=(236, 221, 154),
                radius=66.0 + tier * 12.0,
                spoke_count=13 + tier,
            )
        )
        self.set_message("Restoration Rite", SUCCESS_COLOR, 0.55)
        return True

    def apply_sanity_damage(self, amount: int) -> None:
        if amount <= 0:
            return
        self.change_sanity(-amount * SANITY_DAMAGE_LOSS)

    def update_sanity(self, delta_time: float) -> None:
        drain_multiplier = 1.0
        self.change_sanity(-SANITY_PASSIVE_DRAIN * drain_multiplier * delta_time)

        if self.sanity < 20.0 and self.player.alive:
            danger_ratio = max(0.0, min(1.0, (20.0 - self.sanity) / 20.0))
            self.screen_shake = max(self.screen_shake, 0.05 + 0.17 * danger_ratio)

        if self.sanity <= 0.0 and self.player.alive:
            self.player.health = 0
            self.player.action_state = "dead"
            self.player.hurt_timer = 0.0
            self.set_message("Sanity collapsed", DANGER_COLOR, 0.8)
            return

        target_vignette_strength = self.sanity_vignette_strength()
        if target_vignette_strength > self.sanity_vignette_display_strength:
            transition_speed = 1.65 if self.sanity > SANITY_BLUR_START else 3.1
        else:
            transition_speed = 1.9
        step = transition_speed * delta_time
        if self.sanity_vignette_display_strength < target_vignette_strength:
            self.sanity_vignette_display_strength = min(target_vignette_strength, self.sanity_vignette_display_strength + step)
        else:
            self.sanity_vignette_display_strength = max(target_vignette_strength, self.sanity_vignette_display_strength - step)

        if self.sanity <= SANITY_DANGER_THRESHOLD and self.sanity_break_timer <= 0.0 and self.player.alive:
            self.sanity_break_timer = SANITY_BREAK_CHECK_TIME
            self.set_message("Mind frays", DANGER_COLOR, 0.35)

    def handle_equipment_actions(self) -> None:
        if self.app.input.consume_action("interact"):
            pickup = self.overlapping_pickup()
            if pickup is not None and self.try_swap_pickup(pickup):
                return
            portal = self.overlapping_teleport_portal()
            if portal is not None and portal.activated:
                self.open_teleport_map(portal)
                return
            self.try_use_route_gate()
        if self.app.input.consume_action("ultimate"):
            self.try_activate_heart()
        if self.app.input.consume_action("brain_skill"):
            self.try_activate_brain_skill()
        if self.app.input.consume_action("skill_left"):
            self.try_activate_left_skill()
        if self.app.input.consume_action("skill_right"):
            self.try_activate_right_skill()
        if self.app.input.consume_action("minor_skill"):
            self.try_activate_minor_skill()

    def pickup_interaction_rect(self, pickup: EquipmentPickup) -> pygame.FRect:
        return pygame.FRect(pickup.position.x - 26, pickup.position.y - 96, 52, 96)

    def current_route_gates(self) -> list[RouteGate]:
        if self.level.is_embedded_world_map:
            return []
        child_ids = self.level.current_children()
        if len(child_ids) <= 1:
            return []
        room = self.level.current_room
        gate_width = 104.0
        gate_height = 36.0
        gap = 46.0
        start_y = room.world_height - 108.0 - (len(child_ids) - 1) * gap * 0.5
        x = room.world_width - 138.0
        gates: list[RouteGate] = []
        for index, child_id in enumerate(child_ids):
            child_room = self.level.rooms[child_id]
            gates.append(
                RouteGate(
                    target_room_index=child_id,
                    rect=pygame.FRect(x, start_y + index * gap, gate_width, gate_height),
                    label=child_room.name,
                    role=child_room.role,
                )
            )
        return gates

    def overlapping_route_gate(self) -> RouteGate | None:
        player_range = self.player.rect.inflate(28, 18)
        for gate in self.current_route_gates():
            if gate.rect.colliderect(player_range):
                return gate
        return None

    def overlapping_pickup(self) -> EquipmentPickup | None:
        player_range = self.player.rect.inflate(20, 12)
        for pickup in self.pickups:
            if pickup.item_id is None:
                continue
            if self.pickup_interaction_rect(pickup).colliderect(player_range):
                return pickup
        return None

    def auto_collect_pickups(self) -> None:
        player_range = self.player.rect.inflate(20, 12)
        for pickup in list(self.pickups):
            if pickup.item_id is None:
                continue
            if not self.pickup_interaction_rect(pickup).colliderect(player_range):
                continue
            if self.equipment.equipped[pickup.slot] is not None:
                continue
            success, message = self.equipment.auto_equip(pickup.item_id)
            if not success:
                continue
            if pickup.fixture_kind == "jar":
                self.pickups.remove(pickup)
            else:
                pickup.item_id = None
            self.set_message(message, SUCCESS_COLOR, 0.48)
            break

    def awaken_room_pickups(self) -> None:
        awakened = False
        for pickup in self.pickups:
            if pickup.item_id is not None or pickup.hidden_item_id is None:
                continue
            pickup.item_id = pickup.hidden_item_id
            pickup.hidden_item_id = None
            pickup.reveal_timer = 0.58
            pickup.reveal_progress = 0.0
            awakened = True
        if awakened:
            self.altar_awaken_timer = max(self.altar_awaken_timer, 0.7)
            self.add_screen_shake(0.18)
            self.play_sound("altar_awaken")

    def update_pickups(self, delta_time: float) -> None:
        for pickup in self.pickups:
            if pickup.reveal_timer <= 0.0:
                continue
            pickup.reveal_timer = max(0.0, pickup.reveal_timer - delta_time)
            duration = 0.58
            pickup.reveal_progress = 1.0 - (pickup.reveal_timer / duration)
            pickup.reveal_progress = max(0.0, min(1.0, pickup.reveal_progress))

    def find_heart_altar(self) -> EquipmentPickup | None:
        for pickup in self.pickups:
            if pickup.slot == "heart" and pickup.fixture_kind == "altar":
                return pickup
        return None

    def trigger_boss_heart_release(self) -> None:
        if self.level.current_room.role != "boss" or self.heart_flight is not None:
            return
        altar = self.find_heart_altar()
        if altar is None or altar.item_id is not None:
            return
        dead_boss = next((enemy for enemy in self.enemies if enemy.is_boss and enemy.health <= 0), None)
        if dead_boss is None:
            return
        self.heart_flight = HeartFlight(
            start=dead_boss.center(),
            target=Vec2(altar.position.x, altar.position.y - 82.0),
        )
        self.altar_awaken_timer = self.heart_flight.duration + 0.45
        self.play_sound("heart_release")
        self.add_screen_shake(0.24)
        self.set_message("The Sacred Heart returns", PLAYER_PARRY_COLOR, 1.0)

    def update_heart_flight(self, delta_time: float) -> None:
        if self.heart_flight is None:
            return
        self.heart_flight.progress = min(1.0, self.heart_flight.progress + delta_time / max(0.001, self.heart_flight.duration))
        if self.heart_flight.progress < 1.0:
            return
        altar = self.find_heart_altar()
        if altar is not None:
            altar.item_id = "knight_heart"
        self.heart_flight = None
        self.play_sound("altar_awaken")
        self.add_screen_shake(0.18)
        self.set_message("Heart claimed by the altar", SUCCESS_COLOR, 0.9)

    def try_swap_pickup(self, pickup: EquipmentPickup) -> bool:
        if pickup.slot not in self.equipment.equipped or pickup.item_id is None:
            return False
        success, message, previous_item = self.equipment.swap_with_ground(pickup.item_id)
        if not success:
            return False
        pickup.item_id = previous_item
        self.apply_equipment_stats()
        self.pickup_flash_timer = 0.18
        self.set_message(message, ACCENT_COLOR, 0.8)
        return True

    def try_use_route_gate(self) -> None:
        if self.level.is_embedded_world_map:
            return
        gate = self.overlapping_route_gate()
        if gate is None:
            if len(self.level.current_children()) > 1:
                self.set_message("Stand by a route gate to choose a path", ACCENT_COLOR, 0.42)
            return
        self.level.travel_to(gate.target_room_index)
        self.load_current_room(keep_health=True, entry_direction=1)
        self.set_message(f"Entered {self.level.current_room.name}", ACCENT_COLOR, 1.0)

    def try_activate_heart(self) -> None:
        if self.equipment.equipped["heart"] != "knight_heart":
            self.set_message("No heart equipped", ACCENT_COLOR, 0.35)
            return
        if self.fusion_cooldown > 0.0 or self.fusion_timer > 0.0:
            self.set_message("Heart on cooldown", ACCENT_COLOR, 0.35)
            return
        tier = knight_tier(self.equipment)
        self.fusion_timer = PALADIN_FUSION_TIME
        self.fusion_cooldown = PALADIN_FUSION_COOLDOWN
        self.player.temporary_shield = max(self.player.temporary_shield, PALADIN_FUSION_SHIELD)
        self.player.shield_timer = max(self.player.shield_timer, PALADIN_FUSION_TIME)
        self.player.death_ward_available = tier >= 4
        self.set_message("Paladin Fusion", PLAYER_PARRY_COLOR, 0.75)
        self.play_sound("fusion_start")
        self.add_screen_shake(0.42)

    def try_trigger_brain_rescue(self) -> bool:
        if not is_knight_brain_scripture(self.equipment.equipped["brain"]) or not self.has_active_major("brain"):
            return False
        if self.player.hurt_timer <= 0.0 and self.player.last_damage_taken <= 0:
            return False
        tier = max(1, effective_tier_for_slot(self.equipment, "brain"))
        if tier < 4 and self.brain_rescue_cooldown > 0.0:
            return False
        self.player.hurt_timer = 0.0
        self.player.guard_timer = 0.0
        self.player.parry_timer = 0.0
        self.player.block_timer = 0.0
        if tier < 4:
            self.brain_rescue_cooldown = scripture_brain_rescue_cooldown_seconds(tier)
            self.player.invulnerability = max(self.player.invulnerability, 0.3 + tier * 0.06)
            self.player.temporary_shield = max(self.player.temporary_shield, 10.0 + tier * 4.0)
            self.player.shield_timer = max(self.player.shield_timer, 1.4 + tier * 0.2)
        self.player.flash_timer = max(self.player.flash_timer, 0.24)
        self.brain_scripture_fx_timer = max(self.brain_scripture_fx_timer, SCRIPTURE_BRAIN_EFFECT_TIME)
        self.player_afterimages.extend(
            [
                {"rect": self.player.rect.inflate(6, 2), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.8},
                {"rect": self.player.rect.inflate(20, 10), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.56},
            ]
        )
        self.impact_bursts.append(
            ImpactBurst(
                center=self.player.center(),
                life=0.28,
                max_life=0.28,
                tint=SUCCESS_COLOR,
                accent_tint=SANITY_COLOR,
                radius=74.0 + tier * 18.0,
                spoke_count=10 + tier,
            )
        )
        self.add_screen_shake(0.24 + tier * 0.03)
        if tier >= 4:
            self.set_message("Holy Scripture: Unbroken", SUCCESS_COLOR, 0.5)
        else:
            cooldown_seconds = int(scripture_brain_rescue_cooldown_seconds(tier))
            self.set_message(f"Holy Scripture {cooldown_seconds}s", SUCCESS_COLOR, 0.5)
        return True

    def try_activate_left_skill(self) -> None:
        if self.left_skill_cooldown > 0.0:
            self.set_message("Left eye on cooldown", ACCENT_COLOR, 0.35)
            return
        item_id = self.equipment.equipped["left_eye"]
        if item_id == "knight_left_eye_halo":
            tier = max(1, knight_tier(self.equipment))
            self.halo_timer = PALADIN_HALO_TIME
            self.halo_cooldown = PALADIN_HALO_COOLDOWN
            self.halo_cast_tier = tier
            self.halo_pulse_timer = 0.34 if tier >= 4 else 0.0
            self.halo_end_pulse_pending = tier == 3
            self.left_skill_cooldown = PALADIN_HALO_COOLDOWN
            self.player.death_ward_available = False
            if knight_halo_activation_push_px(tier) > 0.0:
                halo_center = self.player.center()
                halo_radius = knight_halo_radius_px(tier)
                for enemy in self.enemies:
                    if not enemy.alive or enemy.is_friendly:
                        continue
                    if (enemy.center() - halo_center).length() >= halo_radius:
                        continue
                    boss_rift_super_armor = enemy.is_boss and (
                        enemy.rift_intent_timer > 0.0
                        or enemy.attack_profile == "rift"
                        or (enemy.action_state in {"attack_windup", "attack", "attack_recovery"} and enemy.attack_profile == "rift")
                        or enemy.movement_state == "invade"
                    )
                    boss_breaking_barrier = enemy.is_boss and (self.player.has_boss_rift_bait() or boss_rift_super_armor)
                    if boss_breaking_barrier:
                        enemy.velocity.x *= 0.88
                        continue
                    self.register_halo_boss_tag(enemy)
                    self.launch_enemy_from_halo(enemy, halo_center, halo_radius, knight_halo_activation_push_px(tier), tier)
            self.set_message("Sanctuary Halo", SUCCESS_COLOR, 0.5)
        elif item_id == "knight_left_eye_blade":
            self.left_skill_cooldown = PALADIN_BLADE_COOLDOWN
            self.cast_light_blade()
        else:
            self.set_message("No left eye equipped", ACCENT_COLOR, 0.35)

    def try_activate_right_skill(self) -> None:
        if self.right_skill_cooldown > 0.0:
            self.set_message("Right eye on cooldown", ACCENT_COLOR, 0.35)
            return
        item_id = self.equipment.equipped["right_eye"]
        if item_id == "knight_right_eye_rain":
            self.right_skill_cooldown = PALADIN_RAIN_COOLDOWN
            self.cast_sword_rain()
        elif item_id == "knight_right_eye_spirit":
            self.right_skill_cooldown = PALADIN_SPIRIT_COOLDOWN
            self.cast_knight_spirit()
        else:
            self.set_message("No right eye equipped", ACCENT_COLOR, 0.35)

    def cast_light_blade(self) -> None:
        tier = max(1, knight_tier(self.equipment))
        reach = knight_blade_reach_px(tier)
        if self.minor_tier("sword") >= 3:
            reach *= 1.3
        height = knight_blade_height_px(tier)
        if tier >= 4:
            targets = self.visible_hostile_enemies(60.0)
            if targets:
                self.radiant_judgement = RadiantJudgement(
                    targets=targets,
                    warmup=0.92,
                    max_warmup=0.92,
                    damage=72,
                    stun_time=PALADIN_BLADE_ROOT_TIME * 0.58,
                    band_height=78.0,
                    max_flash=0.34,
                    max_recovery=0.26,
                )
                self.play_sound("radiant_judgement_charge")
            self.set_message("Radiant Judgement", RIFT_SLASH_ACCENT, 0.55)
            return
        center = self.player.center() + Vec2(self.player.facing * (52.0 + reach * 0.34), -4.0)
        self.slash_effects.append(
            SlashEffect(
                start=center + Vec2(-self.player.facing * (reach * 0.52), -24.0),
                end=center + Vec2(self.player.facing * (reach * 0.60), 18.0),
                center=center,
                life=0.22,
                tint=PLAYER_PARRY_COLOR,
                max_life=0.22,
                accent_tint=ATTACK_COLOR,
                width_scale=1.5,
            )
        )
        strike_rect = pygame.FRect(center.x - reach * 0.5, center.y - height * 0.5, reach, height)
        search_rect = strike_rect.inflate(max(64.0, reach * 0.4), max(32.0, height * 0.35))
        targets: list[Enemy] = []
        for enemy in self.enemies:
            if enemy.alive and search_rect.colliderect(enemy.rect):
                targets.append(enemy)
        if targets:
            self.blade_combos.append(
                BladeCombo(
                    targets=targets,
                    range_px=reach,
                    hits_remaining=knight_blade_combo_hits(tier),
                    hit_interval=0.09,
                    damage=max(10, int(PALADIN_BLADE_DAMAGE * 0.62)),
                    stun_time=PALADIN_BLADE_ROOT_TIME * 0.45,
                    full_screen=False,
                    band_height=0.0,
                )
            )
        self.set_message("Light Blade", PLAYER_PARRY_COLOR, 0.4)

    def cast_sword_rain(self) -> None:
        tier = max(1, knight_tier(self.equipment))
        count = knight_rain_strike_count(tier)
        spacing = knight_rain_spacing_px(tier)
        self.sword_rain_strikes = []
        if tier >= 4:
            room = self.level.current_room
            live_targets = [enemy.center().x for enemy in self.visible_hostile_enemies(60.0)]
            target_xs: list[float] = []
            self.play_sound("meteor_lances_cast")
            if live_targets:
                repeats = max(1, count // max(1, len(live_targets)))
                for enemy_x in live_targets:
                    for _ in range(repeats):
                        target_xs.append(enemy_x + random.uniform(-spacing * 0.24, spacing * 0.24))
                while len(target_xs) < count:
                    enemy_x = random.choice(live_targets)
                    target_xs.append(enemy_x + random.uniform(-spacing * 0.38, spacing * 0.38))
            else:
                bands = [room.world_width * (index + 0.5) / count for index in range(count)]
                random.shuffle(bands)
                for band_x in bands:
                    target_xs.append(self.player.center().x + (band_x - room.world_width * 0.5) * 0.92)

            for index, raw_x in enumerate(target_xs[:count]):
                target = self.sword_rain_target_for_x(raw_x)
                angle_deg = random.uniform(80.0, 110.0)
                angle_rad = math.radians(angle_deg)
                direction = Vec2(math.cos(angle_rad), math.sin(angle_rad))
                distance = max(WINDOW_HEIGHT * 2.2, 1100.0)
                origin = target - direction * distance
                self.sword_rain_strikes.append(
                    FallingSwordStrike(
                        origin=origin,
                        target=target,
                        life=0.84 + index * 0.04,
                        tint=RIFT_SLASH_ACCENT,
                        accent_tint=RIFT_SLASH_COLOR,
                        explosion_radius=140.0,
                    )
                )
        else:
            base = self.player.center() + Vec2(self.player.facing * knight_rain_forward_px(tier), 0.0)
            half = (count - 1) * 0.5
            for index in range(count):
                offset = index - half
                target_x = base.x + offset * spacing
                target = Vec2(target_x, self.sword_rain_plane_y_for_x(target_x))
                origin = target + Vec2(0.0, -(320.0 + tier * 36.0))
                self.sword_rain_strikes.append(
                    FallingSwordStrike(
                        origin=origin,
                        target=target,
                        life=0.68 + index * 0.06,
                        tint=ATTACK_COLOR,
                        accent_tint=PLAYER_PARRY_COLOR,
                        explosion_radius=0.0,
                    )
                )
        self.set_message("Meteor Lances" if tier >= 4 else "Sword Rain", PLAYER_PARRY_COLOR, 0.45)

    def cast_knight_spirit(self) -> None:
        tier = effective_tier_for_slot(self.equipment, "right_eye")
        if tier <= 0:
            return
        if tier >= 4:
            summoned = self.summon_knight_elites(2)
            self.set_message("Bound Elite Knights" if summoned else "No summon space", SUCCESS_COLOR if summoned else ACCENT_COLOR, 0.55)
            return
        range_px = knight_spirit_range_px(tier)
        converted = 0
        for enemy in self.enemies:
            if not enemy.alive or enemy.is_friendly:
                continue
            if enemy.is_boss:
                continue
            delta = enemy.center() - self.player.center()
            forward_distance = delta.x * self.player.facing
            if forward_distance < -enemy.rect.width * 0.2 or forward_distance > range_px:
                continue
            if abs(delta.y) > max(TILE_SIZE * 3.0, enemy.rect.height * 1.6):
                continue
            enemy.is_friendly = True
            enemy.friendly_role = "controlled"
            enemy.summon_timer = 0.0
            enemy.invulnerability = max(enemy.invulnerability, 0.18)
            enemy.contact_cooldown = max(enemy.contact_cooldown, 0.18)
            enemy.velocity.x = 0.0
            enemy.attack_startup_timer = 0.0
            enemy.attack_timer = 0.0
            enemy.attack_recovery_timer = 0.0
            enemy.attack_has_hit = False
            enemy.hurt_timer = 0.0
            enemy.stun_timer = max(enemy.stun_timer, 0.16)
            enemy.action_state = "ally"
            enemy.movement_state = "escort"
            enemy.facing = self.player.facing
            enemy.ally_platform_target = None
            enemy.ally_platform_jump_start = None
            enemy.ally_platform_snap_timer = 0.0
            enemy.ally_jump_grace_timer = 0.0
            enemy.health = max(1, int(enemy.max_health * (0.25 + 0.15 * max(0, tier - 1))))
            converted += 1
        self.set_message("Knight Spirit" if converted else "No target converted", SUCCESS_COLOR if converted else ACCENT_COLOR, 0.5)

    def summon_knight_elites(self, summon_count: int) -> int:
        existing_elites = [enemy for enemy in self.enemies if enemy.alive and enemy.is_friendly and enemy.enemy_type == "elite_knight"]
        for elite in existing_elites[:ELITE_KNIGHT_SUMMON_CAP]:
            elite.friendly_role = "summon"
            elite.health = elite.max_health
            elite.summon_timer = ELITE_KNIGHT_SUMMON_DURATION
            elite.invulnerability = max(elite.invulnerability, 0.2)
        if len(existing_elites) >= ELITE_KNIGHT_SUMMON_CAP:
            return ELITE_KNIGHT_SUMMON_CAP

        summoned = 0
        room = self.level.current_room
        candidate_offsets = [128.0, -128.0, 224.0, -224.0, 320.0, -320.0, 416.0, -416.0]
        used_xs: list[float] = [enemy.rect.centerx for enemy in existing_elites]
        for offset in candidate_offsets:
            if len(existing_elites) + summoned >= min(summon_count, ELITE_KNIGHT_SUMMON_CAP):
                break
            world_x = max(48.0, min(room.world_width - 48.0, self.player.center().x + offset))
            if any(abs(world_x - used_x) < 56.0 for used_x in used_xs):
                continue
            plane_y = self.nearest_plane_y_for_x(world_x, self.player.center().y)
            spawn_position = Vec2(world_x - 16.0, plane_y - 42.0)
            elite = self.spawn_enemy_instance(spawn_position, "elite_knight", None)
            candidate_rect = elite.rect.inflate(12, 8)
            if candidate_rect.colliderect(self.player.rect.inflate(24, 12)):
                continue
            if any(candidate_rect.colliderect(other.rect.inflate(12, 8)) for other in self.enemies if other.alive and other.is_friendly and other.enemy_type == "elite_knight"):
                continue
            elite.is_friendly = True
            elite.friendly_role = "summon"
            elite.health = elite.max_health
            elite.invulnerability = max(elite.invulnerability, 0.3)
            elite.ally_jump_grace_timer = 0.28
            elite.facing = 1 if offset >= 0.0 else -1
            elite.ally_formation_offset_x = 52.0 if offset >= 0.0 else -52.0
            elite.patrol_origin_x = elite.rect.x
            elite.summon_timer = ELITE_KNIGHT_SUMMON_DURATION
            self.enemies.append(elite)
            self.impact_bursts.append(
                ImpactBurst(
                    center=elite.center(),
                    life=0.34,
                    max_life=0.34,
                    tint=(138, 228, 204),
                    accent_tint=(226, 248, 236),
                    radius=58.0,
                    spoke_count=12,
                )
            )
            used_xs.append(world_x)
            summoned += 1
        return len(existing_elites) + summoned

    def resolve_friendly_enemy_hits(self) -> None:
        for ally in self.enemies:
            if not ally.alive or not ally.is_friendly:
                continue
            if ally.attack_timer <= 0.0 or ally.attack_has_hit or ally.current_attack_is_ranged():
                continue
            strike = ally.attack_hitbox()
            for hostile in self.enemies:
                if hostile is ally or hostile.is_friendly or not hostile.alive:
                    continue
                if not strike.colliderect(hostile.rect):
                    continue
                ally.attack_has_hit = True
                if self.damage_enemy(hostile, int(ally.attack_stats()["damage"]), 0.18, "ally_melee"):
                    if not hostile.has_unstoppable_boss_slash():
                        hostile.velocity.x = 180.0 * ally.facing
                        hostile.velocity.y = -120.0
                        hostile.stun_timer = max(hostile.stun_timer, 0.28)
                break

    def update_active_skill_effects(self, delta_time: float) -> None:
        self.update_minor_passives(delta_time)
        if self.halo_timer > 0.0:
            tier = max(1, self.halo_cast_tier if self.halo_cast_tier > 0 else knight_tier(self.equipment))
            halo_radius = knight_halo_radius_px(tier)
            self.player.set_halo_barrier(halo_radius, max(delta_time * 2.0, 0.12))
            self.regen_bank += PALADIN_HALO_HEAL_RATE * delta_time * (1.2 if self.equipment.equipped["left_eye"] == "knight_left_eye_halo" else 1.0)
            while self.regen_bank >= 1.0 and self.player.health < self.player.max_health:
                self.player.health += 1
                self.regen_bank -= 1.0
            halo_center = self.player.center()
            if tier >= 4:
                self.halo_pulse_timer = max(0.0, self.halo_pulse_timer - delta_time)
                if self.halo_pulse_timer <= 0.0:
                    self.halo_pulse_timer = 0.42
                    self.emit_halo_shockwave(tier, knight_halo_wave_damage(tier), knight_halo_wave_push_px(tier), radius_scale=1.08, life=0.30, width=6)
            for enemy in self.enemies:
                if not enemy.alive or enemy.is_friendly:
                    continue
                delta = enemy.center() - halo_center
                if delta.length() < halo_radius:
                    if enemy.has_unstoppable_boss_slash():
                        continue
                    boss_rift_super_armor = enemy.is_boss and (
                        enemy.rift_intent_timer > 0.0
                        or enemy.attack_profile == "rift"
                        or (enemy.action_state in {"attack_windup", "attack", "attack_recovery"} and enemy.attack_profile == "rift")
                        or enemy.movement_state == "invade"
                    )
                    boss_breaking_barrier = enemy.is_boss and (self.player.has_boss_rift_bait() or boss_rift_super_armor)
                    if boss_breaking_barrier:
                        enemy.velocity.x *= 0.88
                    else:
                        enemy.velocity.x = self.player.facing * 180.0
                        enemy.stun_timer = max(enemy.stun_timer, 0.25)
            for projectile in self.projectiles:
                if (Vec2(projectile.rect.centerx, projectile.rect.centery) - halo_center).length() < halo_radius:
                    projectile.reflected = True
                    projectile.tint = PLAYER_PARRY_COLOR
        else:
            self.player.clear_halo_barrier()
            if self.halo_end_pulse_pending and self.halo_cast_tier == 3:
                self.emit_halo_shockwave(self.halo_cast_tier, 0, knight_halo_wave_push_px(self.halo_cast_tier), radius_scale=1.14, life=0.34, width=5, finisher=True)
            self.halo_end_pulse_pending = False
            self.halo_pulse_timer = 0.0
            self.halo_cast_tier = 0

        alive_rain: list[FallingSwordStrike] = []
        for strike in self.sword_rain_strikes:
            strike.life = max(0.0, strike.life - delta_time)
            if not strike.triggered and strike.life <= 0.26:
                strike.triggered = True
                tier = max(1, knight_tier(self.equipment))
                if tier >= 4:
                    self.play_sound("meteor_lance_impact")
                rain_half_width = knight_rain_hit_width_px(tier)
                rain_half_height = knight_rain_hit_height_px(tier)
                direction = strike.target - strike.origin
                if direction.length_squared() <= 0.001:
                    direction = Vec2(0.0, 1.0)
                else:
                    direction = direction.normalize()
                self.slash_effects.append(
                    SlashEffect(
                        start=strike.origin,
                        end=strike.target + direction * 26.0,
                        center=strike.target,
                        life=0.20,
                        tint=strike.tint,
                        max_life=0.20,
                        accent_tint=strike.accent_tint,
                        width_scale=2.3 if tier >= 4 else 1.3,
                    )
                )
                for enemy in self.enemies:
                    if enemy.alive and abs(enemy.center().x - strike.target.x) < rain_half_width and abs(enemy.center().y - strike.target.y) < rain_half_height:
                        strike_damage = PALADIN_RAIN_DAMAGE + 14 if tier >= 4 else PALADIN_RAIN_DAMAGE
                        if self.damage_enemy(enemy, strike_damage, 0.20, "rain"):
                            enemy.stun_timer = max(enemy.stun_timer, PALADIN_RAIN_STUN_TIME * self.control_duration_multiplier)
                if strike.explosion_radius > 0.0:
                    self.impact_bursts.append(
                        ImpactBurst(
                            center=strike.target,
                            life=0.26,
                            max_life=0.26,
                            tint=RIFT_SLASH_COLOR,
                            accent_tint=RIFT_SLASH_ACCENT,
                            radius=strike.explosion_radius,
                            spoke_count=16,
                        )
                    )
                    for enemy in self.enemies:
                        if not enemy.alive:
                            continue
                        if (enemy.center() - strike.target).length() <= strike.explosion_radius:
                            splash_damage = 18 if tier >= 4 else max(8, int(PALADIN_RAIN_DAMAGE * 0.65))
                            if self.damage_enemy(enemy, splash_damage, 0.12, "rain"):
                                enemy.velocity.x = 120.0 if enemy.center().x >= strike.target.x else -120.0
                                enemy.velocity.y = -120.0
            if strike.life > 0.0:
                alive_rain.append(strike)
        self.sword_rain_strikes = alive_rain

        if self.radiant_judgement is not None:
            self.radiant_judgement.warmup = max(0.0, self.radiant_judgement.warmup - delta_time)
            if not self.radiant_judgement.released:
                self.bullet_time_timer = max(self.bullet_time_timer, 0.14)
                if not self.radiant_judgement.prep_played and self.radiant_judgement.warmup <= self.radiant_judgement.max_warmup * 0.16:
                    self.radiant_judgement.prep_played = True
                    self.play_sound("radiant_judgement_prep", 0.92)
            if self.radiant_judgement.warmup <= 0.0 and not self.radiant_judgement.released:
                self.radiant_judgement.released = True
                self.radiant_judgement.flash_timer = self.radiant_judgement.max_flash
                self.radiant_judgement.recovery = self.radiant_judgement.max_recovery
                self.play_sound("radiant_judgement_release", 1.0)
                center = self.player.center()
                room_width = self.level.current_room.world_width
                self.radiant_judgement.slash_start = Vec2(-80.0, center.y + 300.0)
                self.radiant_judgement.slash_end = Vec2(room_width + 80.0, center.y - 300.0)
                self.impact_bursts.append(
                    ImpactBurst(
                        center=center,
                        life=0.20,
                        max_life=0.20,
                        tint=(255, 224, 118),
                        accent_tint=RIFT_SLASH_ACCENT,
                        radius=180.0,
                        spoke_count=18,
                    )
                )
                self.add_screen_shake(0.72)
                self.set_hitstop(0.06)
            elif self.radiant_judgement.released:
                self.radiant_judgement.flash_timer = max(0.0, self.radiant_judgement.flash_timer - delta_time)
                self.radiant_judgement.recovery = max(0.0, self.radiant_judgement.recovery - delta_time)
                if not self.radiant_judgement.damage_applied and self.radiant_judgement.recovery <= self.radiant_judgement.max_recovery * 0.35:
                    applied_hits = 0
                    camera_rect = pygame.FRect(self.camera.x, self.camera.y, WINDOW_WIDTH, WINDOW_HEIGHT)
                    for enemy in [enemy for enemy in self.enemies if enemy.alive and not enemy.is_friendly]:
                        if not camera_rect.colliderect(enemy.rect):
                            continue
                        if self.damage_enemy(enemy, self.player_damage_value(self.radiant_judgement.damage, "judgement"), 0.12, "judgement"):
                            enemy.velocity.x = self.player.facing * 180.0
                            enemy.velocity.y = -120.0
                            enemy.stun_timer = max(enemy.stun_timer, self.radiant_judgement.stun_time)
                            applied_hits += 1
                    self.radiant_judgement.damage_applied = True
            if self.radiant_judgement.released and self.radiant_judgement.flash_timer <= 0.0 and self.radiant_judgement.recovery <= 0.0:
                self.radiant_judgement = None

        alive_blade_combos: list[BladeCombo] = []
        for combo in self.blade_combos:
            combo.timer = max(0.0, combo.timer - delta_time)
            valid_targets = [enemy for enemy in combo.targets if enemy.alive]
            if not valid_targets or combo.hits_remaining <= 0:
                continue
            if combo.timer > 0.0:
                alive_blade_combos.append(combo)
                continue
            target = valid_targets[combo.sequence_index % len(valid_targets)]
            target_center = target.center()
            angle = -1 if combo.sequence_index % 2 == 0 else 1
            if combo.full_screen:
                room_width = self.level.current_room.world_width
                start = Vec2(-60.0, target_center.y - combo.band_height * 0.45 * angle)
                end = Vec2(room_width + 60.0, target_center.y + combo.band_height * 0.45 * angle)
                strike_box = pygame.FRect(0.0, target_center.y - combo.band_height * 0.5, room_width, combo.band_height)
                tint = RIFT_SLASH_ACCENT
                accent = RIFT_SLASH_COLOR
                width_scale = 2.75
            else:
                start = target_center + Vec2(-self.player.facing * 86.0, -58.0 * angle)
                end = target_center + Vec2(self.player.facing * 90.0, 52.0 * angle)
                strike_box = pygame.FRect(target_center.x - 72.0, target_center.y - 68.0, 144.0, 136.0)
                tint = PLAYER_PARRY_COLOR
                accent = ATTACK_COLOR
                width_scale = 1.28
            self.slash_effects.append(
                SlashEffect(
                    start=start,
                    end=end,
                    center=target_center,
                    life=0.18 if combo.full_screen else 0.16,
                    tint=tint,
                    max_life=0.18 if combo.full_screen else 0.16,
                    accent_tint=accent,
                    width_scale=width_scale,
                )
            )
            impacted = 0
            for enemy in valid_targets:
                if not strike_box.colliderect(enemy.rect):
                    continue
                if self.damage_enemy(enemy, self.player_damage_value(combo.damage, "blade_combo"), 0.10, "blade_combo"):
                    enemy.velocity.x = self.player.facing * (160.0 if combo.full_screen else 120.0)
                    enemy.velocity.y = -110.0 if combo.full_screen else -90.0
                    enemy.stun_timer = max(enemy.stun_timer, combo.stun_time)
                    impacted += 1
            combo.hits_remaining -= 1
            combo.sequence_index += 1
            combo.timer = combo.hit_interval
            if combo.hits_remaining > 0:
                alive_blade_combos.append(combo)
        self.blade_combos = alive_blade_combos

        if self.fusion_timer > 0.0:
            tier = knight_tier(self.equipment)
            stun_time = knight_stun_seconds(tier)
            impact_targets = [
                enemy
                for enemy in self.enemies
                if enemy.alive and enemy.dash_hit_cooldown <= 0.0 and self.player.rect.inflate(14, -6).colliderect(enemy.rect)
            ]
            impact_count = len(impact_targets)
            for enemy in impact_targets:
                if self.damage_enemy(enemy, FUSION_COLLISION_DAMAGE, 0.18, "fusion"):
                    enemy.dash_hit_cooldown = 0.35
                    enemy.stun_timer = max(enemy.stun_timer, stun_time)
                    enemy.velocity.x = self.player.facing * 320.0
                    enemy.velocity.y = -180.0
                    self.trigger_fusion_impact(enemy, impact_count)

    def trigger_fusion_impact(self, enemy: Enemy, impact_count: int = 1) -> None:
        contact = (self.player.center() + enemy.center()) * 0.5
        rush = Vec2(self.player.facing * 132.0, 0.0)
        speed_ratio = min(1.0, abs(self.player.velocity.x) / max(1.0, PALADIN_FUSION_SPEED))
        impact_scale = min(1.0, 0.62 + speed_ratio * 0.22 + min(impact_count, 4) * 0.08)
        self.play_sound("fusion_crash", impact_scale)
        self.slash_effects.append(
            SlashEffect(
                start=contact - rush + Vec2(0.0, -18.0),
                end=contact + rush + Vec2(0.0, 14.0),
                center=contact,
                life=0.18,
                tint=ATTACK_COLOR,
                max_life=0.18,
                accent_tint=PLAYER_PARRY_COLOR,
                width_scale=1.8,
            )
        )

    def trigger_boss_rift_effect(self, enemy: Enemy) -> None:
        center = enemy.center() + Vec2(enemy.facing * 34.0, 0.0)
        vertical_span = max(96.0, enemy.rect.height * 1.45)
        horizontal_span = max(118.0, enemy.rect.width * 2.3)
        self.slash_effects.append(
            SlashEffect(
                start=center + Vec2(-enemy.facing * 28.0, -vertical_span * 0.70),
                end=center + Vec2(enemy.facing * 32.0, vertical_span * 0.72),
                center=center,
                life=0.26,
                tint=RIFT_SLASH_COLOR,
                max_life=0.26,
                accent_tint=RIFT_SLASH_ACCENT,
                width_scale=2.1,
            )
        )
        self.slash_effects.append(
            SlashEffect(
                start=center + Vec2(-horizontal_span * 0.55, -18.0),
                end=center + Vec2(horizontal_span * 0.55, 18.0),
                center=center,
                life=0.18,
                tint=RIFT_SLASH_ACCENT,
                max_life=0.18,
                accent_tint=RIFT_SLASH_SHADE,
                width_scale=1.7,
            )
        )
        self.impact_bursts.append(
            ImpactBurst(
                center=center,
                life=0.20,
                max_life=0.20,
                tint=RIFT_SLASH_COLOR,
                accent_tint=RIFT_SLASH_ACCENT,
                radius=52.0,
                spoke_count=14,
            )
        )

    def update_afterimages(self, delta_time: float) -> None:
        alive_images: list[dict[str, object]] = []
        for image in self.player_afterimages:
            life = max(0.0, float(image["life"]) - delta_time)
            if life <= 0.0:
                continue
            image["life"] = life
            alive_images.append(image)
        self.player_afterimages = alive_images

        self.afterimage_timer = max(0.0, self.afterimage_timer - delta_time)
        if self.player.is_empowered_dash_active() and self.afterimage_timer <= 0.0:
            self.afterimage_timer = PLAYER_AFTERIMAGE_INTERVAL
            self.player_afterimages.append({"rect": self.player.rect.copy(), "life": PLAYER_AFTERIMAGE_LIFETIME})
        elif is_knight_brain_sword(self.equipment.equipped["brain"]) and abs(self.player.velocity.x) > 185.0 and self.afterimage_timer <= 0.0:
            self.afterimage_timer = PLAYER_AFTERIMAGE_INTERVAL * 1.4
            self.player_afterimages.append({"rect": self.player.rect.inflate(4, 0), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.62})

    def update_slash_effects(self, delta_time: float) -> None:
        alive_effects: list[SlashEffect] = []
        for effect in self.slash_effects:
            effect.life = max(0.0, effect.life - delta_time)
            if effect.life > 0.0:
                alive_effects.append(effect)
        self.slash_effects = alive_effects

    def update_impact_bursts(self, delta_time: float) -> None:
        alive_bursts: list[ImpactBurst] = []
        for burst in self.impact_bursts:
            burst.life = max(0.0, burst.life - delta_time)
            if burst.life > 0.0:
                alive_bursts.append(burst)
        self.impact_bursts = alive_bursts

    def update_halo_shockwaves(self, delta_time: float) -> None:
        alive_waves: list[HaloShockwave] = []
        for wave in self.halo_shockwaves:
            wave.life = max(0.0, wave.life - delta_time)
            if wave.life > 0.0:
                alive_waves.append(wave)
        self.halo_shockwaves = alive_waves

    def update_finisher_overlay(self, delta_time: float) -> None:
        if self.finisher_overlay is None:
            return
        self.finisher_overlay.life = max(0.0, self.finisher_overlay.life - delta_time)
        if self.finisher_overlay.life <= 0.0:
            self.finisher_overlay = None

    def start_parry_clash(self, enemy: Enemy) -> None:
        self.parry_clash_enemy = enemy
        self.parry_clash_timer = PARRY_CLASH_TIME
        self.parry_clash_direction = 1 if enemy.rect.centerx >= self.player.rect.centerx else -1
        self.parry_clash_center = (self.player.center() + enemy.center()) * 0.5
        self.parry_clash_player_origin = Vec2(self.player.rect.x, self.player.rect.y)
        self.parry_clash_enemy_origin = Vec2(enemy.rect.x, enemy.rect.y)
        self.player.velocity.xy = (0.0, 0.0)
        enemy.velocity.xy = (0.0, 0.0)
        self.player.action_state = "parry"
        self.player.movement_state = "idle"
        enemy.action_state = "stunned"
        enemy.movement_state = "stagger"

    def update_parry_clash(self, delta_time: float) -> None:
        if self.parry_clash_enemy is None:
            self.parry_clash_timer = 0.0
            return

        enemy = self.parry_clash_enemy
        if not enemy.alive:
            self.parry_clash_enemy = None
            self.parry_clash_timer = 0.0
            return

        progress = 1.0 - (self.parry_clash_timer / PARRY_CLASH_TIME if PARRY_CLASH_TIME > 0.0 else 1.0)
        direction = self.parry_clash_direction
        self.player.facing = direction
        enemy.facing = -direction

        contact_phase = min(1.0, progress / 0.24)
        lock_phase = max(0.0, min(1.0, (progress - 0.24) / 0.26))
        repel_phase = max(0.0, min(1.0, (progress - 0.50) / 0.50))
        brace = math.sin(lock_phase * math.pi)
        player_target = self.parry_clash_player_origin.copy()
        player_target.x += direction * (18.0 * contact_phase - 7.0 * repel_phase)
        player_target.y -= 8.0 * contact_phase + 4.0 * brace

        enemy_target = self.parry_clash_enemy_origin.copy()
        if enemy.enemy_type == "blade":
            enemy_target.x += direction * (8.0 * contact_phase + 28.0 * repel_phase)
            enemy_target.y -= 4.0 * contact_phase - 2.0 * brace - 10.0 * repel_phase
        elif enemy.enemy_type == "lancer":
            enemy_target.x += direction * (10.0 * contact_phase + 34.0 * repel_phase)
            enemy_target.y -= 6.0 * contact_phase + 12.0 * repel_phase
        else:
            enemy_target.x += direction * (6.0 * contact_phase + 22.0 * repel_phase)
            enemy_target.y -= 10.0 * contact_phase - 6.0 * brace - 8.0 * repel_phase
        self.player.rect.x = player_target.x
        self.player.rect.y = player_target.y
        enemy.rect.x = enemy_target.x
        enemy.rect.y = enemy_target.y
        self.player.velocity.xy = (0.0, 0.0)
        enemy.velocity.xy = (0.0, 0.0)
        self.player.action_state = "parry"
        self.player.movement_state = "idle"
        enemy.action_state = "stunned"
        enemy.movement_state = "stagger"
        self.parry_clash_center = self.get_parry_contact_point(enemy)

        target = Vec2((self.player.rect.centerx + enemy.rect.centerx) * 0.5 - WINDOW_WIDTH * 0.5, self.player.rect.centery - WINDOW_HEIGHT * 0.55)
        target = self.level.current_room.clamp_camera(target)
        self.camera = self.camera.lerp(target, 1.0 - math.exp(-CAMERA_SMOOTHING * delta_time * 1.6))

        if self.parry_clash_timer <= 0.0:
            self.parry_clash_enemy = None
            self.start_execution(enemy)

    def update_parry_overlay(self, delta_time: float) -> None:
        if self.parry_overlay is None:
            return
        self.parry_overlay.life = max(0.0, self.parry_overlay.life - delta_time)
        if self.parry_overlay.life <= 0.0:
            self.parry_overlay = None

    def parry_clash_progress(self) -> float:
        if self.parry_clash_enemy is None or PARRY_CLASH_TIME <= 0.0:
            return 0.0
        return max(0.0, min(1.0, self.parry_clash_timer / PARRY_CLASH_TIME))

    def get_parry_contact_point(self, enemy: Enemy) -> Vec2:
        progress = self.parry_clash_progress() if self.parry_clash_enemy is enemy else 0.0
        rect = enemy.rect
        direction = enemy.facing
        if enemy.enemy_type == "blade":
            return Vec2(rect.centerx + direction * (2.0 - 18.0 * progress), rect.y + 26.0 - 18.0 * progress)
        if enemy.enemy_type == "lancer":
            return Vec2(rect.centerx - direction * (10.0 + 24.0 * progress), rect.centery - 10.0 - 22.0 * progress)
        return Vec2(rect.centerx + direction * (6.0 - 16.0 * progress), rect.y + 22.0 - 14.0 * progress)

    def try_trigger_perfect_dodge(self) -> str | None:
        melee_grace_window = 0.07
        for enemy in self.enemies:
            if enemy.is_ranged:
                if enemy.action_state != "attack" or enemy.attack_timer <= 0.0:
                    continue
                active_hitbox = enemy.attack_hitbox().inflate(18, 10)
                player_window = self.player.rect.inflate(10, 6)
            else:
                melee_window_open = (
                    (enemy.action_state == "attack" and enemy.attack_timer > 0.0)
                    or (enemy.action_state == "attack_windup" and enemy.attack_startup_timer <= melee_grace_window)
                )
                if not melee_window_open:
                    continue
                active_hitbox = enemy.attack_hitbox().inflate(6, 4)
                player_window = self.player.rect.inflate(-2, -2)
            if active_hitbox.colliderect(player_window):
                self.bullet_time_timer = max(self.bullet_time_timer, PERFECT_DODGE_SLOW_TIME)
                self.player.begin_empowered_dash()
                self.player_afterimages.clear()
                self.afterimage_timer = 0.0
                if enemy.health / max(1, enemy.max_health) <= 0.6:
                    original_center = self.player.center()
                    self.teleport_behind_enemy(enemy)
                    self.apply_teleport_slash(enemy, original_center)
                    return "blink_cut"
                self.apply_perfect_dodge_slash(enemy)
                return "perfect_dodge"
        return None

    def apply_perfect_dodge_slash(self, enemy: Enemy) -> None:
        enemy_center = enemy.center()
        slash_a_start = enemy_center + Vec2(-self.player.facing * 52.0, -34.0)
        slash_a_end = enemy_center + Vec2(self.player.facing * 44.0, 28.0)
        slash_b_start = enemy_center + Vec2(-self.player.facing * 40.0, 30.0)
        slash_b_end = enemy_center + Vec2(self.player.facing * 58.0, -22.0)
        slash_c_start = enemy_center + Vec2(-self.player.facing * 66.0, -4.0)
        slash_c_end = enemy_center + Vec2(self.player.facing * 72.0, -2.0)
        self.slash_effects.append(
            SlashEffect(
                start=slash_a_start,
                end=slash_a_end,
                center=enemy_center,
                life=PERFECT_DODGE_SLASH_LIFETIME,
                tint=ATTACK_COLOR,
                max_life=PERFECT_DODGE_SLASH_LIFETIME,
                accent_tint=PLAYER_PARRY_COLOR,
                width_scale=1.35,
            )
        )
        self.slash_effects.append(
            SlashEffect(
                start=slash_b_start,
                end=slash_b_end,
                center=enemy_center,
                life=PERFECT_DODGE_SLASH_LIFETIME * 0.92,
                tint=PLAYER_PARRY_COLOR,
                max_life=PERFECT_DODGE_SLASH_LIFETIME * 0.92,
                accent_tint=ATTACK_COLOR,
                width_scale=1.08,
            )
        )
        self.slash_effects.append(
            SlashEffect(
                start=slash_c_start,
                end=slash_c_end,
                center=enemy_center,
                life=PERFECT_DODGE_SLASH_LIFETIME * 0.82,
                tint=PLAYER_PARRY_COLOR,
                max_life=PERFECT_DODGE_SLASH_LIFETIME * 0.82,
                accent_tint=ATTACK_COLOR,
                width_scale=1.65,
            )
        )
        self.impact_bursts.append(
            ImpactBurst(
                center=enemy_center,
                life=PERFECT_DODGE_RING_LIFETIME,
                max_life=PERFECT_DODGE_RING_LIFETIME,
                tint=PLAYER_PARRY_COLOR,
                accent_tint=ATTACK_COLOR,
                radius=116.0,
                spoke_count=12,
            )
        )
        self.perfect_dodge_flash_timer = max(self.perfect_dodge_flash_timer, PERFECT_DODGE_FLASH_TIME)
        self.perfect_dodge_zoom_timer = max(self.perfect_dodge_zoom_timer, PERFECT_DODGE_FLASH_TIME)
        self.player_afterimages.extend(
            [
                {"rect": self.player.rect.inflate(10, 0), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.95},
                {"rect": self.player.rect.inflate(22, 8), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.7},
                {"rect": self.player.rect.inflate(34, 14), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.45},
            ]
        )
        self.play_sound("perfect_dodge_impact")
        slash_sound = enemy.enemy_type if enemy.enemy_type in {"blade", "lancer", "archer"} else "blade"
        self.play_sound(f"perfect_dodge_slash_{slash_sound}")
        self.add_screen_shake(0.52)
        self.set_hitstop(PERFECT_DODGE_SLASH_HITSTOP + 0.015)

    def apply_teleport_slash(self, enemy: Enemy, from_center: Vec2) -> None:
        did_damage = self.damage_enemy(enemy, self.player_damage_value(TELEPORT_SLASH_DAMAGE, "blink_cut"), 0.12, "blink_cut")
        lethal = did_damage and not enemy.alive
        if did_damage:
            enemy.velocity.x = self.player.facing * 320.0
            enemy.velocity.y = -210.0
        enemy_center = enemy.center()
        slash_end = enemy_center + Vec2(self.player.facing * 22.0, -8.0)
        cross_start = from_center + Vec2(-self.player.facing * 20.0, -22.0)
        back_cut_start = enemy_center + Vec2(-self.player.facing * 84.0, -36.0)
        back_cut_end = enemy_center + Vec2(self.player.facing * 90.0, 32.0)
        self.slash_effects.append(
            SlashEffect(
                start=cross_start,
                end=slash_end,
                center=enemy_center,
                life=TELEPORT_SLASH_LIFETIME,
                tint=ATTACK_COLOR,
                max_life=TELEPORT_SLASH_LIFETIME,
                accent_tint=PLAYER_PARRY_COLOR,
                width_scale=1.45,
            )
        )
        self.slash_effects.append(
            SlashEffect(
                start=back_cut_start,
                end=back_cut_end,
                center=enemy_center,
                life=TELEPORT_SLASH_LIFETIME * 0.9,
                tint=PLAYER_PARRY_COLOR,
                max_life=TELEPORT_SLASH_LIFETIME * 0.9,
                accent_tint=ATTACK_COLOR,
                width_scale=1.85 if lethal else 1.35,
            )
        )
        self.impact_bursts.append(
            ImpactBurst(
                center=enemy_center,
                life=PERFECT_DODGE_RING_LIFETIME * (1.1 if lethal else 0.9),
                max_life=PERFECT_DODGE_RING_LIFETIME * (1.1 if lethal else 0.9),
                tint=ATTACK_COLOR,
                accent_tint=PLAYER_PARRY_COLOR,
                radius=144.0 if lethal else 108.0,
                spoke_count=16 if lethal else 12,
            )
        )
        self.player_afterimages.extend(
            [
                {"rect": self.player.rect.inflate(12, 2), "life": PLAYER_AFTERIMAGE_LIFETIME * 1.05},
                {"rect": self.player.rect.inflate(28, 10), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.78},
                {"rect": self.player.rect.inflate(46, 18), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.52},
            ]
        )
        self.play_sound("dash_slice")
        if lethal:
            self.trigger_teleport_finisher(enemy_center)
            self.play_sound("blink_cut_finish")
            self.add_screen_shake(0.78)
            self.set_hitstop(TELEPORT_SLASH_HITSTOP + 0.05)
        else:
            self.add_screen_shake(0.52)
            self.set_hitstop(TELEPORT_SLASH_HITSTOP + 0.015)

    def trigger_teleport_finisher(self, center: Vec2) -> None:
        self.finisher_overlay = FinisherOverlay(
            center=center.copy(),
            life=TELEPORT_FINISHER_TIME,
            max_life=TELEPORT_FINISHER_TIME,
            flash_color=TELEPORT_FINISHER_FLASH_COLOR,
            shade_color=TELEPORT_FINISHER_SHADE_COLOR,
            line_color=ATTACK_COLOR,
            spoke_count=22,
        )
        self.perfect_dodge_flash_timer = max(self.perfect_dodge_flash_timer, PERFECT_DODGE_FLASH_TIME * 1.45)
        self.perfect_dodge_zoom_timer = max(self.perfect_dodge_zoom_timer, TELEPORT_FINISHER_TIME)

    def apply_empowered_dash_hits(self) -> int:
        if not self.player.is_empowered_dash_active():
            return 0
            self.auto_collect_pickups()

        strike_rect = self.player.rect.inflate(12, -8)
        hits = 0
        for enemy in self.enemies:
            if not enemy.alive or enemy.dash_hit_cooldown > 0.0:
                continue
            if not strike_rect.colliderect(enemy.rect):
                continue
            if not self.damage_enemy(enemy, self.player_damage_value(DASH_STRIKE_DAMAGE, "dash"), 0.18, "dash"):
                continue

            enemy.dash_hit_cooldown = DASH_STRIKE_HIT_COOLDOWN
            enemy.velocity.x = self.player.dash_direction * 260.0
            enemy.velocity.y = -180.0
            self.player.sustain_empowered_dash()
            hits += 1

        return hits

    def spawn_projectile(self, spawn: EnemyProjectileSpawn) -> None:
        radius = max(4.0, spawn.radius)
        projectile = CombatProjectile(
            rect=pygame.FRect(spawn.position.x - radius, spawn.position.y - radius, radius * 2.0, radius * 2.0),
            velocity=spawn.velocity.copy(),
            damage=spawn.damage,
            tint=spawn.tint,
            source_enemy=spawn.source_enemy,
        )
        self.projectiles.append(projectile)

    def teleport_behind_enemy(self, enemy: Enemy) -> None:
        target_x = enemy.rect.x - self.player.rect.width - 14 if enemy.facing > 0 else enemy.rect.right + 14
        target_x = max(0.0, min(target_x, self.level.current_room.world_width - self.player.rect.width))
        original_rect = self.player.rect.copy()
        self.player.rect.x = target_x
        self.player.rect.bottom = enemy.rect.bottom
        for solid in self.level.current_room.solids:
            if self.player.rect.colliderect(solid):
                self.player.rect = original_rect
                break
        self.player.facing = -enemy.facing
        self.player.dash_direction = self.player.facing

    def reflect_projectile(self, projectile: CombatProjectile, guard_result: str) -> None:
        projectile.reflected = True
        projectile.orbit_duration = 0.36 if guard_result == "guard" else 0.30
        projectile.orbit_timer = projectile.orbit_duration
        projectile.orbit_side = -1 if projectile.rect.centery <= self.player.rect.centery else 1
        projectile.curve_phase = 0.0
        projectile.tint = PLAYER_PARRY_COLOR if guard_result == "parry" else PLAYER_BLOCK_COLOR
        projectile.velocity = Vec2(0.0, 0.0)
        self.play_sound("parry" if guard_result == "parry" else "guard")
        if guard_result == "parry":
            self.trigger_parry_impact(Vec2(projectile.rect.centerx, projectile.rect.centery))
        self.set_message("Redirect", PLAYER_PARRY_COLOR if guard_result == "parry" else PLAYER_BLOCK_COLOR, 0.22)

    def trigger_parry_impact(self, center: Vec2) -> None:
        self.parry_overlay = FinisherOverlay(
            center=center.copy(),
            life=PARRY_IMPACT_TIME,
            max_life=PARRY_IMPACT_TIME,
            flash_color=PARRY_FLASH_COLOR,
            shade_color=PARRY_SHADE_COLOR,
            line_color=PLAYER_PARRY_COLOR,
            spoke_count=16,
        )
        self.impact_bursts.append(
            ImpactBurst(
                center=center.copy(),
                life=PERFECT_DODGE_RING_LIFETIME * 0.82,
                max_life=PERFECT_DODGE_RING_LIFETIME * 0.82,
                tint=PLAYER_PARRY_COLOR,
                accent_tint=ATTACK_COLOR,
                radius=104.0,
                spoke_count=14,
            )
        )
        self.player_afterimages.extend(
            [
                {"rect": self.player.rect.inflate(8, 0), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.72},
                {"rect": self.player.rect.inflate(18, 8), "life": PLAYER_AFTERIMAGE_LIFETIME * 0.48},
            ]
        )
        self.parry_full_flash_timer = max(self.parry_full_flash_timer, PARRY_FULL_FLASH_TIME)
        self.play_sound("parry_blade_clash")
        self.play_sound("parry_blade_click")
        self.perfect_dodge_flash_timer = max(self.perfect_dodge_flash_timer, PERFECT_DODGE_FLASH_TIME * 0.92)
        self.perfect_dodge_zoom_timer = max(self.perfect_dodge_zoom_timer, PARRY_IMPACT_TIME)
        self.add_screen_shake(0.44)
        self.set_hitstop(PARRY_HITSTOP + 0.02)

    def update_projectiles(self, delta_time: float) -> int:
        total_damage = 0
        alive_projectiles: list[CombatProjectile] = []
        for projectile in self.projectiles:
            projectile.life_timer = max(0.0, projectile.life_timer - delta_time)
            if projectile.life_timer <= 0.0:
                continue

            projectile.trail.append(Vec2(projectile.rect.centerx, projectile.rect.centery))
            if len(projectile.trail) > 10:
                projectile.trail.pop(0)

            remove_projectile = False
            if projectile.reflected and projectile.orbit_timer > 0.0:
                projectile.orbit_timer = max(0.0, projectile.orbit_timer - delta_time)
                orbit_progress = 1.0 - (projectile.orbit_timer / projectile.orbit_duration if projectile.orbit_duration > 0.0 else 1.0)
                rear_angle = math.pi if self.player.facing > 0 else 0.0
                projectile.curve_phase = rear_angle + projectile.orbit_side * (math.pi * 0.75 + orbit_progress * math.tau)
                orbit_radius = 34.0 + 38.0 * orbit_progress
                orbit_offset = Vec2(math.cos(projectile.curve_phase), math.sin(projectile.curve_phase)) * orbit_radius
                orbit_offset.x -= self.player.facing * (24.0 - 10.0 * orbit_progress)
                player_center = self.player.center()
                projectile.rect.centerx = player_center.x + orbit_offset.x
                projectile.rect.centery = player_center.y + orbit_offset.y
            else:
                if projectile.reflected:
                    target = projectile.source_enemy.center() if projectile.source_enemy.alive else self.player.center() + Vec2(self.player.facing * 240.0, 0.0)
                    direction = target - Vec2(projectile.rect.centerx, projectile.rect.centery)
                    if direction.length_squared() > 0.001:
                        projectile.velocity = direction.normalize() * 620.0
                projectile.rect.x += projectile.velocity.x * delta_time
                projectile.rect.y += projectile.velocity.y * delta_time

            center = Vec2(projectile.rect.centerx, projectile.rect.centery)
            if self.level.point_in_solid(center):
                if projectile.reflected:
                    remove_projectile = False
                else:
                    guard_result = self.player.try_guard(projectile.rect.centerx)
                    if guard_result is not None:
                        self.reflect_projectile(projectile, guard_result)
                        if guard_result == "parry":
                            self.set_hitstop(PARRY_HITSTOP)
                        else:
                            self.set_hitstop(GUARD_HITSTOP)
                        self.add_screen_shake(0.12)
                        remove_projectile = False
                    else:
                        remove_projectile = True

            if not remove_projectile and projectile.reflected:
                if projectile.source_enemy.alive and projectile.rect.colliderect(projectile.source_enemy.rect):
                    if self.damage_enemy(projectile.source_enemy, projectile.damage + 14, 0.16, "reflect"):
                        projectile.source_enemy.velocity.x = self.player.facing * 240.0
                        projectile.source_enemy.velocity.y = -140.0
                    self.add_screen_shake(0.24)
                    self.set_hitstop(GUARD_HITSTOP)
                    remove_projectile = True
            elif not remove_projectile and projectile.source_enemy.is_friendly:
                for hostile in self.enemies:
                    if hostile is projectile.source_enemy or hostile.is_friendly or not hostile.alive:
                        continue
                    if not projectile.rect.colliderect(hostile.rect.inflate(-6, -6)):
                        continue
                    if self.damage_enemy(hostile, projectile.damage, 0.20, "ally_shot"):
                        hostile.velocity.x = 180.0 * projectile.source_enemy.facing
                        hostile.velocity.y = -120.0
                    remove_projectile = True
                    break
            elif not remove_projectile and projectile.rect.colliderect(self.player.rect.inflate(-6, -6)):
                guard_result = self.player.try_guard(projectile.rect.centerx)
                if guard_result is not None:
                    self.reflect_projectile(projectile, guard_result)
                    if guard_result == "parry":
                        self.set_hitstop(PARRY_HITSTOP)
                    else:
                        self.set_hitstop(GUARD_HITSTOP)
                    self.add_screen_shake(0.12)
                else:
                    if self.player.take_damage(projectile.damage, 0.30):
                        total_damage += self.player.last_damage_taken
                    remove_projectile = True

            if not remove_projectile:
                if projectile.rect.right < -40 or projectile.rect.left > self.level.current_room.world_width + 40:
                    remove_projectile = True
                elif projectile.rect.bottom < -40 or projectile.rect.top > self.level.current_room.world_height + 40:
                    remove_projectile = True

            if not remove_projectile:
                alive_projectiles.append(projectile)

        self.projectiles = alive_projectiles
        return total_damage

    def play_sound(self, cue: str, volume_scale: float = 1.0) -> None:
        audio = getattr(self.app, "audio", None)
        if audio is not None:
            audio.play(cue, volume_scale)

    def add_screen_shake(self, amount: float) -> None:
        self.screen_shake = max(self.screen_shake, min(1.0, amount))

    def set_hitstop(self, duration: float) -> None:
        self.impact_freeze_timer = max(self.impact_freeze_timer, duration)

    def camera_shake_offset(self) -> Vec2:
        amplitude = CAMERA_SHAKE_MAX * (self.screen_shake ** 2)
        return Vec2(random.uniform(-amplitude, amplitude), random.uniform(-amplitude * 0.75, amplitude * 0.75))

    def current_zoom(self) -> float:
        zoom = 1.0
        if self.finisher_overlay is not None and self.finisher_overlay.max_life > 0.0:
            progress = self.finisher_overlay.life / self.finisher_overlay.max_life
            zoom += (TELEPORT_FINISHER_ZOOM - 1.0) * (progress ** 0.6)
        elif self.parry_clash_enemy is not None and PARRY_CLASH_TIME > 0.0:
            progress = self.parry_clash_timer / PARRY_CLASH_TIME
            zoom += (PARRY_IMPACT_ZOOM - 1.0) * max(0.0, min(1.0, progress ** 0.5))
        elif self.parry_overlay is not None and self.parry_overlay.max_life > 0.0:
            progress = self.parry_overlay.life / self.parry_overlay.max_life
            zoom += (PARRY_IMPACT_ZOOM - 1.0) * (progress ** 0.65)
        elif self.perfect_dodge_zoom_timer > 0.0:
            progress = self.perfect_dodge_zoom_timer / PERFECT_DODGE_FLASH_TIME if PERFECT_DODGE_FLASH_TIME > 0.0 else 0.0
            zoom += (PERFECT_DODGE_ZOOM - 1.0) * (progress ** 0.55)

        if self.execution_enemy is None:
            return zoom

        progress = 1.0 - (self.execution_timer / EXECUTION_TIME if EXECUTION_TIME > 0.0 else 1.0)
        if progress < 0.24:
            weight = 0.45 * (progress / 0.24)
        elif progress < 0.58:
            weight = 0.45 + 0.55 * ((progress - 0.24) / 0.34)
        else:
            weight = 1.0 - 0.45 * ((progress - 0.58) / 0.42)

        zoom += (EXECUTION_CAMERA_ZOOM - 1.0) * max(0.0, min(1.0, weight))
        if self.impact_freeze_timer > 0.0:
            zoom += 0.018
        return zoom

    def start_execution(self, enemy: Enemy) -> None:
        self.execution_timer = EXECUTION_TIME
        self.execution_enemy = enemy
        self.execution_strike_applied = False
        self.execution_direction = 1 if enemy.rect.centerx >= self.player.rect.centerx else -1
        self.execution_style = enemy.enemy_type
        self.execution_player_origin = Vec2(self.player.rect.x, self.player.rect.y)
        self.execution_enemy_origin = Vec2(enemy.rect.x, enemy.rect.y)
        self.player.action_state = "execute"
        self.player.invulnerability = max(self.player.invulnerability, EXECUTION_TIME)
        enemy.action_state = "executed"
        enemy.velocity.xy = (0.0, 0.0)
        self.play_sound("execution_pull")
        self.add_screen_shake(0.24)

    def execution_strike_damage(self, enemy: Enemy) -> int:
        damage = 0
        if enemy.is_boss:
            damage = min(enemy.health, max(36, int(enemy.max_health * 0.18)))
        else:
            damage = enemy.health
        return self.player_damage_value(damage, "execution")

    def update_execution(self, delta_time: float) -> None:
        if self.execution_enemy is None:
            self.execution_timer = 0.0
            self.execution_strike_applied = False
            return

        enemy = self.execution_enemy
        self.execution_timer = max(0.0, self.execution_timer - delta_time)
        progress = 1.0 - (self.execution_timer / EXECUTION_TIME if EXECUTION_TIME > 0.0 else 1.0)
        direction = self.execution_direction
        self.player.facing = direction

        anchor_x = self.execution_enemy_origin.x - direction * (self.player.rect.width + 12)
        phase_pull = min(1.0, progress / 0.24)
        phase_strike = max(0.0, min(1.0, (progress - 0.24) / 0.34))
        phase_finish = max(0.0, min(1.0, (progress - 0.58) / 0.42))

        if self.execution_style == "lancer":
            rear_x = self.execution_enemy_origin.x - direction * (self.player.rect.width + 22)
            vault_x = self.execution_enemy_origin.x + direction * (enemy.rect.width * 0.85)
            finish_x = self.execution_enemy_origin.x + direction * (enemy.rect.width + 52)
            if progress < 0.24:
                self.player.rect.x = self.execution_player_origin.x + (rear_x - self.execution_player_origin.x) * phase_pull
                self.player.rect.y = self.execution_player_origin.y - 4 * phase_pull
                enemy.rect.x = self.execution_enemy_origin.x
                enemy.rect.y = self.execution_enemy_origin.y
            elif progress < 0.58:
                self.player.rect.x = rear_x + (vault_x - rear_x) * phase_strike
                self.player.rect.y = self.execution_player_origin.y - 18 - 32 * math.sin(phase_strike * math.pi)
                enemy.rect.x = self.execution_enemy_origin.x + direction * 12 * phase_strike
                enemy.rect.y = self.execution_enemy_origin.y - 8 * math.sin(phase_strike * math.pi)
            else:
                self.player.rect.x = vault_x + (finish_x - vault_x) * phase_finish
                self.player.rect.y = self.execution_player_origin.y - 8 * (1.0 - phase_finish)
                enemy.rect.x = self.execution_enemy_origin.x + direction * 26
                enemy.rect.y = self.execution_enemy_origin.y + 26 * phase_finish
        elif self.execution_style == "archer":
            side_x = self.execution_enemy_origin.x - direction * (self.player.rect.width + 6)
            sweep_x = self.execution_enemy_origin.x + direction * (enemy.rect.width * 0.25)
            finish_x = self.execution_enemy_origin.x + direction * 18
            if progress < 0.24:
                self.player.rect.x = self.execution_player_origin.x + (side_x - self.execution_player_origin.x) * phase_pull
                self.player.rect.y = self.execution_player_origin.y - 10 * phase_pull
                enemy.rect.x = self.execution_enemy_origin.x + direction * 8 * phase_pull
                enemy.rect.y = self.execution_enemy_origin.y
            elif progress < 0.58:
                self.player.rect.x = side_x + (sweep_x - side_x) * phase_strike
                self.player.rect.y = self.execution_player_origin.y - 6 - 10 * math.sin(phase_strike * math.pi)
                enemy.rect.x = self.execution_enemy_origin.x + direction * 24 * phase_strike
                enemy.rect.y = self.execution_enemy_origin.y - 20 * math.sin(phase_strike * math.pi)
            else:
                self.player.rect.x = sweep_x + (finish_x - sweep_x) * phase_finish
                self.player.rect.y = self.execution_player_origin.y - 6 * (1.0 - phase_finish)
                enemy.rect.x = self.execution_enemy_origin.x + direction * 18
                enemy.rect.y = self.execution_enemy_origin.y + 24 * phase_finish
        else:
            pull_x = self.execution_player_origin.x + (anchor_x - self.execution_player_origin.x) * phase_pull
            strike_target_x = self.execution_enemy_origin.x + direction * (enemy.rect.width * 0.55)
            finish_target_x = self.execution_enemy_origin.x + direction * (enemy.rect.width + 34)

            if progress < 0.24:
                self.player.rect.x = pull_x
                self.player.rect.y = self.execution_player_origin.y - 8 * phase_pull
                enemy.rect.x = self.execution_enemy_origin.x - direction * 10 * phase_pull
                enemy.rect.y = self.execution_enemy_origin.y
            elif progress < 0.58:
                self.player.rect.x = anchor_x + (strike_target_x - anchor_x) * phase_strike
                self.player.rect.y = self.execution_player_origin.y - 10 - 18 * math.sin(phase_strike * math.pi)
                enemy.rect.x = self.execution_enemy_origin.x + direction * 18 * phase_strike
                enemy.rect.y = self.execution_enemy_origin.y - 14 * math.sin(phase_strike * math.pi)
            else:
                self.player.rect.x = strike_target_x + (finish_target_x - strike_target_x) * phase_finish
                self.player.rect.y = self.execution_player_origin.y - 10 * (1.0 - phase_finish)
                enemy.rect.x = self.execution_enemy_origin.x + direction * 18
                enemy.rect.y = self.execution_enemy_origin.y + 18 * phase_finish
        self.player.velocity.xy = (0.0, 0.0)
        enemy.velocity.xy = (0.0, 0.0)
        self.player.movement_state = "idle"
        self.player.action_state = "execute"
        enemy.movement_state = "stagger"
        enemy.action_state = "executed"

        if not self.execution_strike_applied and self.execution_timer <= EXECUTION_TIME * 0.45:
            strike_damage = self.execution_strike_damage(enemy)
            enemy.health = max(0, enemy.health - strike_damage)
            enemy.invulnerability = 0.0
            enemy.flash_timer = 0.14
            if enemy.health <= 0:
                enemy.action_state = "dead"
                self.reward_sanity_for_kill(enemy, "execution")
            else:
                enemy.hurt_timer = max(enemy.hurt_timer, 0.52)
                enemy.stun_timer = max(enemy.stun_timer, 0.72)
                enemy.action_state = "hurt"
                enemy.movement_state = "stagger"
            self.execution_strike_applied = True
            self.play_sound("execution_strike")
            self.add_screen_shake(0.38 if enemy.is_boss else 0.82)
            self.set_hitstop(EXECUTION_HITSTOP * (0.65 if enemy.is_boss else 1.0))
            if enemy.is_boss and enemy.health > 0:
                self.set_message("Boss staggered", ACCENT_COLOR, 0.45)

        target = Vec2((self.player.rect.centerx + enemy.rect.centerx) * 0.5 - WINDOW_WIDTH * 0.5, self.player.rect.centery - WINDOW_HEIGHT * 0.55)
        target = self.level.current_room.clamp_camera(target)
        self.camera = self.camera.lerp(target, 1.0 - math.exp(-CAMERA_SMOOTHING * delta_time))

        if self.execution_timer <= 0.0:
            if enemy.is_boss and enemy.health <= 0:
                self.trigger_boss_heart_release()
            elif enemy.health > 0:
                enemy.action_state = "hurt"
                enemy.movement_state = "stagger"
            self.execution_enemy = None
            self.execution_strike_applied = False
            self.execution_style = "blade"
            self.player.action_state = "neutral"
            self.enemies = [enemy_item for enemy_item in self.enemies if enemy_item.alive]

    def update_room_intro(self, delta_time: float) -> None:
        self.room_intro_hold_timer = max(0.0, self.room_intro_hold_timer - delta_time)
        if self.room_intro_hold_timer <= 0.0:
            self.room_intro_player_visible = True
        if self.room_intro_hold_timer <= 0.0 and self.room_intro_door_timer > 0.0:
            self.room_intro_door_timer = max(0.0, self.room_intro_door_timer - delta_time)
        self.player.rect.x = self.room_intro_target_x
        self.player.rect.y = self.room_intro_target_y
        self.player.velocity.xy = (0.0, 0.0)
        self.player.movement_state = "idle"
        self.player.action_state = "enter"
        self.camera = self.camera.lerp(self.room_intro_camera, 1.0 - math.exp(-CAMERA_SMOOTHING * delta_time))

        if self.room_intro_hold_timer <= 0.0 and self.room_intro_door_timer <= 0.0:
            self.player.rect.x = self.room_intro_target_x
            self.player.rect.y = self.room_intro_target_y
            self.room_intro_active = False
            self.room_intro_player_visible = True
            self.player.on_ground = True
            self.player.movement_state = "idle"
            self.player.action_state = "neutral"

    def draw_room_intro_door(self, surface: pygame.Surface) -> None:
        if not self.room_intro_active and self.room_intro_door_timer <= 0.0:
            return
        door_rect = self.room_intro_door_rect()
        draw_rect = pygame.Rect(int(door_rect.x - self.camera.x), int(door_rect.y - self.camera.y), int(door_rect.width), int(door_rect.height))
        if draw_rect.right < -8 or draw_rect.left > surface.get_width() + 8:
            return
        overlay = self.get_effect_surface((draw_rect.width + 18, draw_rect.height + 22), "room_intro_door")
        overlay.fill((0, 0, 0, 0))
        arch_rect = pygame.Rect(9, 10, draw_rect.width, draw_rect.height)
        inner_rect = arch_rect.inflate(-10, -12)
        fade_ratio = 1.0
        if self.room_intro_hold_timer > 0.0:
            hold_duration = 1.20
            appear_progress = 1.0 - max(0.0, min(1.0, self.room_intro_hold_timer / hold_duration))
            eased_progress = 1.0 - (1.0 - appear_progress) ** 3
            draw_rect.y = int(draw_rect.y - (1.0 - eased_progress) * 132.0)
        elif self.room_intro_door_duration > 0.0:
            fade_ratio = max(0.0, min(1.0, self.room_intro_door_timer / self.room_intro_door_duration))
        arch_fill = (40, 22, 18, int(228 * fade_ratio))
        arch_edge = (168, 124, 82, int(224 * fade_ratio))
        inner_fill = (12, 10, 16, int(196 * fade_ratio))
        pygame.draw.rect(overlay, arch_fill, arch_rect, border_radius=14)
        pygame.draw.rect(overlay, inner_fill, inner_rect, border_radius=10)
        pygame.draw.rect(overlay, arch_edge, arch_rect, width=4, border_radius=14)
        surface.blit(overlay, (draw_rect.x - 9, draw_rect.y - 10))

    def update_room_progression(self, delta_time: float) -> None:
        if self.level.is_embedded_world_map:
            room = self.level.current_room
            room_region = self.level.room_regions.get(self.level.current_room_index)
            if room_region is None:
                return
            if room.role != "boss":
                return
            if self.boss_room_locked():
                self.reset_boss_exit_door()
                return
            self.update_boss_exit_door(delta_time)
            return
        room = self.level.current_room
        boss_locked = room.role == "boss" and any(enemy.is_boss and enemy.alive for enemy in self.enemies)
        if room.role == "boss" and not boss_locked:
            self.update_boss_exit_door(delta_time)
            return
        if not self.player.on_ground:
            return
        child_ids = self.level.current_children()
        parent_id = self.level.current_parent()

        if self.player.rect.right >= room.world_width:
            if boss_locked:
                self.player.rect.right = room.world_width - 8
                return
            if not child_ids:
                if room.role == "boss":
                    self.rebuild_level_state(floor_number=1, preserve_health=True)
                    self.set_message("进入下一张 1 号地图", ACCENT_COLOR, 1.2)
                    return
                self.player.rect.right = room.world_width - 8
                return
            if len(child_ids) == 1:
                self.level.travel_to(child_ids[0])
                self.load_current_room(keep_health=True, entry_direction=1)
                self.invalidate_route_map()
                self.set_message(f"进入 {self.level.current_room.name}", ACCENT_COLOR, 1.0)
            else:
                self.player.rect.right = room.world_width - 8
                self.set_message("前方有多条路线，请在路标处按 E", ACCENT_COLOR, 0.48)
            return

        if self.player.rect.left <= 0.0:
            if boss_locked:
                self.player.rect.left = 8
                return
            if parent_id is None:
                self.player.rect.left = 8
                return
            self.level.travel_to(parent_id)
            self.load_current_room(keep_health=True, entry_direction=-1)
            self.invalidate_route_map()
            self.set_message(f"进入 {self.level.current_room.name}", ACCENT_COLOR, 1.0)

    def sanity_blur_scale(self) -> float:
        if self.sanity >= SANITY_BLUR_START:
            return 1.0
        ratio = 1.0 - (self.sanity / max(0.001, SANITY_BLUR_START))
        return max(SANITY_BLUR_MAX_SCALE, 1.0 - ratio * (1.0 - SANITY_BLUR_MAX_SCALE))

    def sanity_vignette_strength(self) -> float:
        if self.sanity >= SANITY_BLUR_START + 1.0:
            return 0.0
        if self.sanity > SANITY_BLUR_START:
            return 0.10 * (SANITY_BLUR_START + 1.0 - self.sanity)
        if self.sanity <= SANITY_DANGER_THRESHOLD:
            return 1.0
        collapse_ratio = max(0.0, min(1.0, 1.0 - ((self.sanity - SANITY_DANGER_THRESHOLD) / max(0.001, SANITY_BLUR_START - SANITY_DANGER_THRESHOLD))))
        return 0.10 + (collapse_ratio ** 1.22) * 0.90

    def sanity_vignette_state(self, surface_size: tuple[int, int]) -> tuple[Vec2, float, float, float]:
        width, height = surface_size
        vignette_strength = self.sanity_vignette_display_strength
        pulse_strength = max(0.0, min(1.0, (vignette_strength - 0.55) / 0.45))
        pulse = math.sin(pygame.time.get_ticks() * 0.0046) * pulse_strength
        center_point = self.player.center() - self.camera
        center_point.x = max(width * 0.08, min(width * 0.92, center_point.x))
        center_point.y = max(height * 0.08, min(height * 0.92, center_point.y))
        minimum_radius = TILE_SIZE + 36.0
        base_radius = min(width, height) * (0.44 - 0.43 * vignette_strength - 0.05 * pulse)
        visible_radius = max(minimum_radius, base_radius)
        feather_radius = 38.0 + 52.0 * vignette_strength
        onset_ratio = max(0.0, min(1.0, vignette_strength / 0.12))
        visible_radius *= 1.72 - 0.72 * onset_ratio
        feather_radius *= 1.58 - 0.42 * onset_ratio
        return center_point, visible_radius, feather_radius, pulse

    def enemy_darkness_factor(self, enemy: Enemy, surface_size: tuple[int, int]) -> float:
        if self.sanity_vignette_display_strength <= 0.0:
            return 0.0
        center_point, visible_radius, feather_radius, _ = self.sanity_vignette_state(surface_size)
        enemy_screen_center = enemy.center() - self.camera
        distance = (enemy_screen_center - center_point).length()
        if distance <= visible_radius:
            return 0.0
        falloff = max(0.0, min(1.0, (distance - visible_radius) / max(1.0, feather_radius)))
        return min(0.82, (0.26 + 0.74 * falloff) * self.sanity_vignette_display_strength)

    def draw_pickups(self, surface: pygame.Surface) -> None:
        for pickup in self.visible_render_pickups():
            draw_pos = Vec2(pickup.position.x - self.camera.x, pickup.position.y - self.camera.y)
            shadow_rect = pygame.Rect(int(draw_pos.x - 20), int(draw_pos.y - 4), 40, 8)
            pygame.draw.ellipse(surface, (0, 0, 0, 86), shadow_rect)
            if pickup.fixture_kind == "altar":
                glow_strength = min(1.0, self.altar_awaken_timer / 1.1) if self.altar_awaken_timer > 0.0 else 0.0
                if glow_strength > 0.0:
                    altar_glow = self.get_effect_surface((180, 180), "altar_glow")
                    pygame.draw.circle(altar_glow, (255, 196, 128, int(44 * glow_strength)), (90, 106), 52)
                    pygame.draw.circle(altar_glow, (255, 236, 188, int(28 * glow_strength)), (90, 90), 30)
                    surface.blit(altar_glow, (draw_pos.x - 90, draw_pos.y - 120))
                base_rect = pygame.Rect(int(draw_pos.x - 28), int(draw_pos.y - 14), 56, 12)
                stem_rect = pygame.Rect(int(draw_pos.x - 8), int(draw_pos.y - 46), 16, 30)
                dish_outer = pygame.Rect(int(draw_pos.x - 34), int(draw_pos.y - 62), 68, 16)
                dish_inner = dish_outer.inflate(-8, -6)
                pygame.draw.rect(surface, (72, 64, 78), base_rect, border_radius=6)
                pygame.draw.rect(surface, (116, 104, 126), base_rect, width=2, border_radius=6)
                pygame.draw.rect(surface, (90, 82, 104), stem_rect, border_radius=6)
                pygame.draw.rect(surface, (138, 128, 150), stem_rect, width=2, border_radius=6)
                pygame.draw.ellipse(surface, (112, 106, 132), dish_outer)
                pygame.draw.ellipse(surface, (190, 184, 214), dish_outer, width=2)
                pygame.draw.ellipse(surface, (64, 82, 96), dish_inner)
                if pickup.hidden_item_id is not None and pickup.item_id is None:
                    pygame.draw.ellipse(surface, (92, 118, 132), dish_inner.inflate(-8, -2), width=2)
                glyph_y = draw_pos.y - 72
                if pickup.reveal_progress < 1.0:
                    glyph_y += (1.0 - pickup.reveal_progress) * 44.0
                glyph_center = (int(draw_pos.x), int(glyph_y))
            else:
                jar_body = pygame.Rect(int(draw_pos.x - 22), int(draw_pos.y - 54), 44, 46)
                jar_lid = pygame.Rect(int(draw_pos.x - 18), int(draw_pos.y - 62), 36, 8)
                jar_base = pygame.Rect(int(draw_pos.x - 18), int(draw_pos.y - 8), 36, 8)
                fluid = pygame.Rect(jar_body.x + 4, jar_body.y + 16, jar_body.width - 8, jar_body.height - 20)
                pygame.draw.rect(surface, (38, 56, 62), fluid, border_radius=10)
                pygame.draw.rect(surface, (108, 166, 182), jar_body, width=2, border_radius=14)
                pygame.draw.rect(surface, (176, 214, 220), jar_lid, border_radius=5)
                pygame.draw.rect(surface, (130, 154, 164), jar_base, border_radius=3)
                gloss = self.get_effect_surface((52, 64), "pickup_jar_gloss")
                pygame.draw.ellipse(gloss, (230, 246, 252, 28), (8, 10, 14, 34))
                surface.blit(gloss, (draw_pos.x - 26, draw_pos.y - 62))
                glyph_center = (int(draw_pos.x), int(draw_pos.y - 30))

            if pickup.item_id is not None:
                item = get_equipment(pickup.item_id)
                glow = self.get_effect_surface((52, 52), "pickup_item_glow")
                pygame.draw.circle(glow, (*EQUIPMENT_GLOW, 20), (26, 26), 18)
                surface.blit(glow, (glyph_center[0] - 26, glyph_center[1] - 26))
                self.draw_pickup_series_aura(surface, glyph_center, pickup.item_id)
                draw_slot_glyph(surface, item.slot, pickup.item_id, glyph_center, 11)

        if self.heart_flight is not None:
            t = self.heart_flight.progress
            arc = math.sin(t * math.pi) * 92.0
            position = self.heart_flight.start.lerp(self.heart_flight.target, t) + Vec2(0.0, -arc)
            draw_pos = position - self.camera
            glow = self.get_effect_surface((64, 64), "heart_flight_glow")
            pygame.draw.circle(glow, (*EQUIPMENT_GLOW, 40), (32, 32), 20)
            surface.blit(glow, (draw_pos.x - 32, draw_pos.y - 32))
            trail = self.get_overlay_surface(surface, "heart_flight_trail")
            for step in range(4):
                trail_t = max(0.0, t - step * 0.08)
                trail_pos = self.heart_flight.start.lerp(self.heart_flight.target, trail_t) + Vec2(0.0, -math.sin(trail_t * math.pi) * 92.0)
                alpha = max(0, 90 - step * 18)
                pygame.draw.circle(trail, (255, 204, 154, alpha), (int(trail_pos.x - self.camera.x), int(trail_pos.y - self.camera.y)), 8 - step)
            surface.blit(trail, (0, 0))

    def draw_route_gates(self, surface: pygame.Surface) -> None:
        gates = self.current_route_gates()
        if not gates:
            return
        title_font = self.app.get_font(15, bold=True)
        body_font = self.app.get_font(13)
        for gate in gates:
            draw_rect = pygame.Rect(int(gate.rect.x - self.camera.x), int(gate.rect.y - self.camera.y), int(gate.rect.width), int(gate.rect.height))
            glow = self.get_effect_surface((draw_rect.width + 28, draw_rect.height + 28), "route_gate_glow")
            glow_color = (120, 196, 255, 56) if gate.role == "shop" else (255, 214, 138, 56)
            pygame.draw.ellipse(glow, glow_color, glow.get_rect())
            surface.blit(glow, (draw_rect.x - 14, draw_rect.y - 14))
            pygame.draw.rect(surface, (26, 32, 44), draw_rect, border_radius=10)
            pygame.draw.rect(surface, ACCENT_COLOR, draw_rect, width=2, border_radius=10)
            role_label = gate.role.upper()
            title = title_font.render(role_label, True, TEXT_COLOR)
            hint = body_font.render("E", True, SUCCESS_COLOR)
            surface.blit(title, (draw_rect.x + 10, draw_rect.y + 5))
            surface.blit(hint, (draw_rect.right - 18, draw_rect.y + 5))

    def draw_teleport_portals(self, surface: pygame.Surface) -> None:
        for portal in self.teleport_portals:
            center = (int(portal.position.x - self.camera.x), int(portal.position.y - self.camera.y))
            overlay = self.get_overlay_surface(surface, f"teleport_portal_{portal.portal_id}")
            pulse = 0.56 + 0.44 * math.sin(pygame.time.get_ticks() * 0.009 + center[0] * 0.01)
            radius = max(14, int(TELEPORT_PORTAL_RADIUS * (0.72 + 0.08 * pulse)))
            glow_alpha = 88 if portal.activated else 32
            core_color = (94, 182, 255) if portal.activated else (88, 98, 118)
            edge_color = (236, 248, 255) if portal.activated else (144, 152, 170)
            pygame.draw.circle(overlay, (*core_color, glow_alpha), center, radius + 10)
            pygame.draw.circle(overlay, (*edge_color, 186 if portal.activated else 92), center, radius, width=3)
            pygame.draw.circle(overlay, (10, 14, 20, 210), center, max(6, radius - 10))
            if portal.portal_id == self.teleport_anchor_portal_id:
                marker = pygame.Rect(center[0] - radius - 10, center[1] - radius - 10, (radius + 10) * 2, (radius + 10) * 2)
                pygame.draw.rect(overlay, (255, 238, 168, 172), marker, width=2, border_radius=8)
            surface.blit(overlay, (0, 0))

    def draw_teleport_transition(self, surface: pygame.Surface) -> None:
        if self.teleport_transition is None:
            return
        portal = self.portal_by_id(self.teleport_transition.source_portal_id if self.teleport_transition.phase == "depart" else self.teleport_transition.target_portal_id)
        if portal is None:
            return
        overlay = self.get_overlay_surface(surface, "teleport_transition")
        center = (int(portal.position.x - self.camera.x), int(portal.position.y - self.camera.y))
        progress = 1.0 - (self.teleport_transition.timer / max(0.001, self.teleport_transition.max_timer))
        progress = max(0.0, min(1.0, progress))
        base_radius = TELEPORT_PORTAL_RADIUS * 1.5
        for ring_index in range(5):
            swirl_phase = progress + ring_index * 0.12
            ring_radius = base_radius * ((1.0 - swirl_phase * 0.68) if self.teleport_transition.phase == "depart" else (0.34 + swirl_phase * 0.76))
            ring_radius = max(6.0, ring_radius)
            angle = swirl_phase * math.tau * (1.7 if self.teleport_transition.phase == "depart" else -1.7)
            offset = Vec2(math.cos(angle), math.sin(angle)) * (4.0 + ring_index * 3.0)
            pygame.draw.circle(overlay, (124, 216, 255, max(18, 132 - ring_index * 18)), (int(center[0] + offset.x), int(center[1] + offset.y)), int(ring_radius), width=2)
        pygame.draw.circle(overlay, (242, 250, 255, 182), center, max(4, int(base_radius * (0.18 + progress * 0.12))))
        surface.blit(overlay, (0, 0))

    def draw_active_skill_effects(self, surface: pygame.Surface) -> None:
        if self.oppression_field_timer > 0.0 and self.oppression_field_radius > 0.0:
            overlay = self.get_overlay_surface(surface, "oppression_minor")
            ratio = self.oppression_field_timer / self.oppression_field_duration if self.oppression_field_duration > 0.0 else 0.0
            center = self.oppression_field_center - self.camera
            ground_y = int(center.y + 4)
            start_x = int(center.x - self.oppression_field_radius)
            end_x = int(center.x + self.oppression_field_radius)
            pygame.draw.line(overlay, (*OPPRESSION_TINT, int(126 * ratio)), (start_x, ground_y), (end_x, ground_y), width=4)
            pygame.draw.line(overlay, (*OPPRESSION_ACCENT, int(92 * ratio)), (start_x, ground_y - 3), (end_x, ground_y - 3), width=2)
            branch_count = 7
            for index in range(branch_count):
                branch_ratio = index / max(1, branch_count - 1)
                branch_x = int(start_x + (end_x - start_x) * branch_ratio)
                branch_length = int(18 + 28 * math.sin(branch_ratio * math.pi))
                direction = -1 if index % 2 == 0 else 1
                pygame.draw.line(overlay, (*OPPRESSION_TINT, int(108 * ratio)), (branch_x, ground_y), (branch_x + direction * branch_length, ground_y - 12 - (index % 3) * 7), width=3)
                pygame.draw.line(overlay, (*OPPRESSION_ACCENT, int(68 * ratio)), (branch_x, ground_y + 1), (branch_x + direction * (branch_length // 2), ground_y + 7 + (index % 2) * 5), width=2)
            surface.blit(overlay, (0, 0))

        if self.oppression_lifts:
            overlay = self.get_overlay_surface(surface, "oppression_columns")
            for lift in self.oppression_lifts:
                enemy = lift.enemy
                ground_y = int(lift.ground_bottom - self.camera.y)
                center_x = int(enemy.rect.centerx - self.camera.x)
                stripe_height = int(54 + 18 * math.sin((lift.elapsed / max(0.001, lift.duration)) * math.pi))
                for offset in (-22, -8, 8, 22):
                    pygame.draw.line(overlay, (*OPPRESSION_TINT, 110), (center_x + offset, ground_y), (center_x + offset, ground_y - stripe_height), width=3)
                ring_rect = pygame.Rect(center_x - 26, int(enemy.rect.bottom - self.camera.y - enemy.rect.height * 0.34), 52, 18)
                pygame.draw.ellipse(overlay, (*OPPRESSION_ACCENT, 136), ring_rect, width=3)
            surface.blit(overlay, (0, 0))

        if self.minor_particles:
            overlay = self.get_overlay_surface(surface, "minor_particles")
            for particle in self.minor_particles:
                life_ratio = particle.life / particle.max_life if particle.max_life > 0.0 else 0.0
                alpha = max(0, min(188, int(188 * life_ratio)))
                center = (int(particle.position.x - self.camera.x), int(particle.position.y - self.camera.y))
                pygame.draw.circle(overlay, (*particle.tint, alpha), center, max(1, int(particle.radius)))
                pygame.draw.circle(overlay, (*particle.accent_tint, max(0, alpha - 54)), center, max(1, int(particle.radius * 0.52)))
            surface.blit(overlay, (0, 0))

        if self.radiant_judgement is not None:
            if not self.radiant_judgement.released:
                progress = 1.0 - (self.radiant_judgement.warmup / self.radiant_judgement.max_warmup if self.radiant_judgement.max_warmup > 0.0 else 1.0)
                progress = max(0.0, min(1.0, progress))
            else:
                progress = 1.0
            overlay = self.get_overlay_surface(surface, "radiant_judgement")
            if self.radiant_judgement.released:
                flash_ratio = self.radiant_judgement.flash_timer / self.radiant_judgement.max_flash if self.radiant_judgement.max_flash > 0.0 else 0.0
                white_alpha = int(150 * flash_ratio)
            else:
                white_alpha = int(36 + 190 * (progress ** 1.4))
            overlay.fill((255, 252, 246, white_alpha))
            beam_y = int(surface.get_height() * (0.46 + 0.08 * progress))
            beam_width = max(4, int(10 + 22 * progress))
            pygame.draw.line(overlay, (255, 220, 92, int(160 + 90 * progress)), (-80, beam_y + 164), (surface.get_width() + 80, beam_y - 164), width=beam_width)
            if self.radiant_judgement.released:
                pygame.draw.line(overlay, (255, 228, 112, int(220 * flash_ratio)), (-80, beam_y + 164), (surface.get_width() + 80, beam_y - 164), width=max(6, beam_width + 2))
            surface.blit(overlay, (0, 0))

        if self.halo_timer > 0.0:
            tier = max(1, knight_tier(self.equipment))
            halo_radius = knight_halo_radius_px(tier)
            halo_center = self.player.center() - self.camera
            ratio = self.halo_timer / PALADIN_HALO_TIME if PALADIN_HALO_TIME > 0.0 else 0.0
            halo_overlay = self.get_overlay_surface(surface, "halo_overlay")
            ring_width = 6 if tier >= 4 else 4
            pygame.draw.circle(halo_overlay, (*PLAYER_PARRY_COLOR, int(52 + 48 * ratio)), (int(halo_center.x), int(halo_center.y)), int(halo_radius), width=ring_width)
            pygame.draw.circle(halo_overlay, (*ATTACK_COLOR, int(30 + 22 * ratio)), (int(halo_center.x), int(halo_center.y)), int(halo_radius * 0.72), width=2)
            if tier >= 4:
                outer_radius = halo_radius * (0.92 + 0.16 * (1.0 - ratio))
                inner_radius = halo_radius * (0.46 + 0.14 * (1.0 - ratio))
                pygame.draw.circle(halo_overlay, (*HALO_WAVE_COLOR, int(46 + 58 * ratio)), (int(halo_center.x), int(halo_center.y)), int(outer_radius), width=3)
                pygame.draw.circle(halo_overlay, (*HALO_WAVE_ACCENT, int(26 + 42 * ratio)), (int(halo_center.x), int(halo_center.y)), int(inner_radius), width=2)

            for enemy in self.enemies:
                if not enemy.alive or not enemy.is_boss or enemy.movement_state != "invade":
                    continue
                to_enemy = enemy.center() - self.player.center()
                distance = to_enemy.length()
                if distance <= 0.001:
                    continue
                direction = to_enemy.normalize()
                contact = halo_center + direction * halo_radius
                ripple_alpha = max(36, min(132, int(132 - max(0.0, distance - halo_radius) * 0.55)))
                ripple_radius = 18 + int((1.0 - min(1.0, ratio)) * 6)
                pygame.draw.circle(halo_overlay, (255, 244, 214, ripple_alpha), (int(contact.x), int(contact.y)), ripple_radius, width=3)
                pygame.draw.circle(halo_overlay, (*PLAYER_PARRY_COLOR, max(24, ripple_alpha - 26)), (int(contact.x), int(contact.y)), ripple_radius + 10, width=2)
                inner = contact - direction * 16.0
                outer = contact + direction * 22.0
                pygame.draw.line(halo_overlay, (255, 248, 226, ripple_alpha), inner, outer, width=3)
            surface.blit(halo_overlay, (0, 0))

        for wave in self.halo_shockwaves:
            progress = 1.0 - (wave.life / wave.max_life if wave.max_life > 0.0 else 1.0)
            progress = max(0.0, min(1.0, progress))
            radius = wave.start_radius + (wave.end_radius - wave.start_radius) * progress
            alpha = max(0, min(210, int(210 * ((1.0 - progress) ** 0.62))))
            accent_alpha = max(0, min(255, int(255 * ((1.0 - progress) ** 0.44))))
            center = (int(wave.center.x - self.camera.x), int(wave.center.y - self.camera.y))
            overlay = self.get_overlay_surface(surface, "halo_shockwave")
            pygame.draw.circle(overlay, (*wave.tint, alpha), center, int(radius), width=wave.width)
            pygame.draw.circle(overlay, (*wave.accent_tint, max(0, accent_alpha - 48)), center, int(radius * 0.82), width=max(2, wave.width - 2))
            pygame.draw.circle(overlay, (*wave.accent_tint, max(0, accent_alpha - 116)), center, int(radius * 0.54), width=2)
            if wave.finisher:
                edge_radius = radius + 14.0 * (1.0 - progress)
                ground_center = (center[0], center[1] + int(self.player.rect.height * 0.34))
                ground_width = max(26, int(radius * 1.24))
                ground_height = max(10, int(18 + radius * 0.12))
                pygame.draw.circle(overlay, (255, 255, 255, max(0, accent_alpha - 10)), center, int(edge_radius), width=max(3, wave.width + 1))
                pygame.draw.ellipse(
                    overlay,
                    (255, 248, 232, max(0, accent_alpha - 38)),
                    pygame.Rect(ground_center[0] - ground_width, ground_center[1] - ground_height // 2, ground_width * 2, ground_height),
                    width=3,
                )
                pygame.draw.ellipse(
                    overlay,
                    (*HALO_WAVE_COLOR, max(0, alpha - 34)),
                    pygame.Rect(ground_center[0] - int(ground_width * 0.74), ground_center[1] - max(4, ground_height // 3), int(ground_width * 1.48), max(8, int(ground_height * 0.66))),
                    width=2,
                )
            surface.blit(overlay, (0, 0))

        for strike in self.sword_rain_strikes:
            center = strike.target - self.camera
            overlay = self.get_overlay_surface(surface, "sword_rain")
            if not strike.triggered:
                origin = strike.origin - self.camera
                beam_width = 28 if strike.explosion_radius > 0.0 else 3
                pygame.draw.line(overlay, (*strike.tint, 132), (int(origin.x), int(origin.y)), (int(center.x), int(center.y)), width=beam_width)
                if strike.explosion_radius > 0.0:
                    pygame.draw.line(overlay, (*strike.accent_tint, 96), (int(origin.x), int(origin.y)), (int(center.x), int(center.y)), width=max(10, beam_width // 2))
                pygame.draw.circle(overlay, (*strike.accent_tint, 96), (int(center.x), int(center.y)), 24, width=2)
            surface.blit(overlay, (0, 0))

    def render(self, surface: pygame.Surface) -> None:
        passive_summary = build_passive_summary(self.equipment)
        cooldown_icons = [
            {
                "slot": "heart",
                "item_id": self.equipment.equipped["heart"],
                "key": "Q",
                "cooldown": max(self.fusion_cooldown, self.fusion_timer),
                "max_cooldown": max_cooldown_for_item(self.equipment.equipped["heart"], PALADIN_FUSION_COOLDOWN),
            },
            {
                "slot": "brain",
                "item_id": self.equipment.equipped["brain"],
                "key": "R",
                "cooldown": self.brain_skill_cooldown,
                "max_cooldown": max_cooldown_for_item(self.equipment.equipped["brain"], PALADIN_SCRIPTURE_COOLDOWN),
            },
            {
                "slot": "left_eye",
                "item_id": self.equipment.equipped["left_eye"],
                "key": "U",
                "cooldown": self.left_skill_cooldown,
                "max_cooldown": max_cooldown_for_item(self.equipment.equipped["left_eye"], PALADIN_HALO_COOLDOWN),
            },
            {
                "slot": "right_eye",
                "item_id": self.equipment.equipped["right_eye"],
                "key": "I",
                "cooldown": self.right_skill_cooldown,
                "max_cooldown": max_cooldown_for_item(self.equipment.equipped["right_eye"], PALADIN_RAIN_COOLDOWN),
            },
        ]
        if self.scene_surface_cache is None or self.scene_surface_cache.get_size() != surface.get_size():
            self.scene_surface_cache = pygame.Surface(surface.get_size()).convert()
        scene_surface = self.scene_surface_cache
        scene_surface.fill((0, 0, 0))
        base_camera = self.camera.copy()
        self.camera = base_camera + self.camera_shake_offset()
        if self.heart_flight is not None:
            focus_target = Vec2(self.heart_flight.target.x - WINDOW_WIDTH * 0.5, self.heart_flight.target.y - WINDOW_HEIGHT * 0.55)
            self.camera = self.camera.lerp(self.level.current_room.clamp_camera(focus_target), 0.18)
        room = self.level.current_room
        room.draw(
            scene_surface,
            self.camera,
            background_blend_from=self.previous_room_role,
            background_blend=self.room_role_transition,
        )
        self.draw_teleport_portals(scene_surface)
        self.draw_pickups(scene_surface)
        self.draw_player_afterimages(scene_surface)
        self.draw_slash_effects(scene_surface)
        self.draw_projectiles(scene_surface)
        self.draw_active_skill_effects(scene_surface)

        visible_render_enemies = self.visible_render_enemies()
        for enemy in visible_render_enemies:
            self.draw_enemy_vision(scene_surface, enemy)
            self.draw_enemy_attack_telegraph(scene_surface, enemy)

        for enemy in visible_render_enemies:
            self.draw_actor(scene_surface, enemy, ENEMY_DRAW_COLORS)
            self.draw_enemy_health(scene_surface, enemy)

        player_alpha = 255
        if self.boss_exit_door_entering and BOSS_EXIT_DOOR_ENTER_TIME > 0.0:
            player_alpha = int(255 * max(0.0, min(1.0, self.boss_exit_door_enter_timer / BOSS_EXIT_DOOR_ENTER_TIME)))
        if not self.room_intro_active or self.room_intro_player_visible:
            self.draw_actor(scene_surface, self.player, PLAYER_DRAW_COLORS, alpha=player_alpha)
        self.draw_room_intro_door(scene_surface)
        self.draw_boss_exit_door(scene_surface)
        if self.player.attack_timer > 0.0:
            self.draw_attack(scene_surface)
        if self.parry_clash_enemy is not None:
            self.draw_parry_clash_effect(scene_surface)
        if self.execution_enemy is not None:
            self.draw_execution_effect(scene_surface)
        self.draw_teleport_transition(scene_surface)
        self.draw_impact_bursts(scene_surface)
        self.draw_boss_room_barrier(scene_surface)
        self.draw_route_gates(scene_surface)

        self.camera = base_camera
        blur_scale = self.sanity_blur_scale()
        fast_scale = pygame.transform.scale if self.app.screen.get_flags() & pygame.FULLSCREEN else pygame.transform.smoothscale
        if blur_scale < 0.999:
            scaled_size = (max(1, int(scene_surface.get_width() * blur_scale)), max(1, int(scene_surface.get_height() * blur_scale)))
            blurred = fast_scale(scene_surface, scaled_size)
            scene_surface = fast_scale(blurred, surface.get_size())
        zoom = self.current_zoom()
        if zoom > 1.001:
            scaled_size = (int(surface.get_width() * zoom), int(surface.get_height() * zoom))
            scaled = fast_scale(scene_surface, scaled_size)
            offset = ((scaled_size[0] - surface.get_width()) // 2, (scaled_size[1] - surface.get_height()) // 2)
            surface.blit(scaled, (-offset[0], -offset[1]))
        else:
            surface.blit(scene_surface, (0, 0))

        self.draw_parry_full_flash(surface)
        self.draw_parry_overlay(surface)
        self.draw_finisher_overlay(surface)
        self.draw_perfect_dodge_flash(surface)
        self.draw_sword_mania_border(surface)
        self.refresh_route_map_if_needed(delta_time=0.0)

        draw_hud(
            surface=surface,
            app=self.app,
            room_name=room.name,
            room_index=self.level.current_room_index + 1,
            room_total=len(self.level.rooms),
            player_health=self.player.health,
            player_max_health=self.player.max_health,
            player_movement_state=self.player.movement_state,
            player_action_state=self.player.action_state,
            enemy_count=len([enemy for enemy in self.current_room_enemies() if enemy.alive and not enemy.is_friendly]),
            sanity=self.sanity,
            sanity_max=SANITY_MAX,
            temporary_shield=self.player.temporary_shield,
            equipment_tier=passive_summary.tier_label,
            message=self.message if self.message_timer > 0.0 else "",
            message_color=self.message_color,
            player_dead=self.player.health <= 0,
            cooldown_icons=cooldown_icons,
            status_bars=[bar.__dict__ for bar in self.hud_status_bars()],
            equipped_items=self.equipment.equipped,
            combo_hits=self.attack_chain_hits,
            combo_goal=knight_shield_hit_goal(max(1, effective_tier_for_slot(self.equipment, "brain"))) if is_knight_brain(self.equipment.equipped["brain"]) and self.has_active_major("brain") else 0,
            brain_cooldown=self.brain_skill_cooldown,
            brain_max_cooldown=PALADIN_SCRIPTURE_COOLDOWN,
            route_map=self.route_map,
        )

        self.draw_sanity_vignette(surface)

        if self.route_map_open:
            map_focus = None if self.route_map_focus is None else (float(self.route_map_focus.x), float(self.route_map_focus.y))
            draw_world_map_overlay(surface, self.app, self.route_map, self.route_map_zoom, focus=map_focus)

        if self.inventory_open:
            nearby_item_id = None
            pickup = self.overlapping_pickup()
            if pickup is not None:
                nearby_item_id = pickup.item_id
            draw_equipment_panel(surface, self.app, self.equipment, passive_summary, nearby_item_id=nearby_item_id)

    def draw_sanity_vignette(self, surface: pygame.Surface) -> None:
        vignette_strength = self.sanity_vignette_display_strength
        if vignette_strength <= 0.0:
            return

        overlay = self.get_overlay_surface(surface, "sanity_vignette")
        center_point, visible_radius, feather_radius, pulse = self.sanity_vignette_state(surface.get_size())
        pulse_strength = max(0.0, min(1.0, (vignette_strength - 0.55) / 0.45))
        darkness = vignette_strength ** 1.42
        base_alpha = max(0, min(255, int(18 + 237 * darkness + 26 * pulse_strength * max(0.0, pulse))))
        overlay.fill((4, 5, 9, base_alpha))

        gradient_steps = 11
        for step_index in range(gradient_steps, 0, -1):
            progress = step_index / gradient_steps
            ring_radius = visible_radius + feather_radius * progress
            ring_alpha = max(0, min(255, int(base_alpha * (progress ** 1.85) * 0.98)))
            pygame.draw.circle(overlay, (4, 5, 9, ring_alpha), (int(center_point.x), int(center_point.y)), int(ring_radius))

        clear_radius = max(6, int(visible_radius))
        pygame.draw.circle(overlay, (0, 0, 0, 0), (int(center_point.x), int(center_point.y)), clear_radius)
        surface.blit(overlay, (0, 0))

    def draw_parry_overlay(self, surface: pygame.Surface) -> None:
        if self.parry_overlay is None or self.parry_overlay.max_life <= 0.0:
            return

        progress = self.parry_overlay.life / self.parry_overlay.max_life
        center = (int(self.parry_overlay.center.x - self.camera.x), int(self.parry_overlay.center.y - self.camera.y))
        overlay = self.get_overlay_surface(surface, "parry_overlay")
        shade_alpha = max(0, min(self.parry_overlay.shade_color[3], int(self.parry_overlay.shade_color[3] * (progress ** 0.88))))
        overlay.fill((*self.parry_overlay.shade_color[:3], shade_alpha))

        flash_radius = max(surface.get_width(), surface.get_height()) * (0.10 + (1.0 - progress) * 0.54)
        pygame.draw.circle(overlay, (0, 0, 0, 0), center, int(flash_radius))

        line_alpha = max(0, min(210, int(210 * (progress ** 0.72))))
        for index in range(self.parry_overlay.spoke_count):
            angle = (math.tau * index / self.parry_overlay.spoke_count) + (1.0 - progress) * 0.18
            direction = Vec2(math.cos(angle), math.sin(angle))
            inner = Vec2(center) + direction * (38.0 + 22.0 * (1.0 - progress))
            outer = Vec2(center) + direction * (240.0 + 150.0 * (1.0 - progress))
            pygame.draw.line(overlay, (*self.parry_overlay.line_color, line_alpha), inner, outer, width=max(2, int(5 * progress)))

        ring_radius = 82.0 + (1.0 - progress) * 110.0
        pygame.draw.circle(overlay, (*ATTACK_COLOR, max(0, line_alpha - 56)), center, int(ring_radius), width=max(2, int(8 * progress)))
        flash_alpha = max(0, min(self.parry_overlay.flash_color[3], int(self.parry_overlay.flash_color[3] * (progress ** 0.68))))
        pygame.draw.circle(overlay, (*self.parry_overlay.flash_color[:3], flash_alpha), center, int(28.0 + (1.0 - progress) * 18.0))
        surface.blit(overlay, (0, 0))

    def draw_parry_full_flash(self, surface: pygame.Surface) -> None:
        if self.parry_full_flash_timer <= 0.0:
            return

        progress = self.parry_full_flash_timer / PARRY_FULL_FLASH_TIME if PARRY_FULL_FLASH_TIME > 0.0 else 0.0
        alpha = max(0, min(PARRY_FULL_FLASH_COLOR[3], int(PARRY_FULL_FLASH_COLOR[3] * progress)))
        overlay = self.get_overlay_surface(surface, "parry_full_flash")
        overlay.fill((*PARRY_FULL_FLASH_COLOR[:3], alpha))
        surface.blit(overlay, (0, 0))

    def draw_parry_clash_effect(self, surface: pygame.Surface) -> None:
        if self.parry_clash_enemy is None or PARRY_CLASH_TIME <= 0.0:
            return

        progress = self.parry_clash_timer / PARRY_CLASH_TIME
        clash_point = self.get_parry_contact_point(self.parry_clash_enemy)
        center = (int(clash_point.x - self.camera.x), int(clash_point.y - self.camera.y))
        overlay = self.get_overlay_surface(surface, "parry_clash")
        radius = int(30.0 + (1.0 - progress) * 34.0)
        alpha = max(0, min(240, int(240 * (progress ** 0.62))))
        slash_span = 54.0 + (1.0 - progress) * 28.0
        pygame.draw.circle(overlay, (*PLAYER_PARRY_COLOR, max(0, alpha - 24)), center, radius, width=max(2, int(10 * progress)))
        pygame.draw.line(
            overlay,
            (*ATTACK_COLOR, alpha),
            (center[0] - self.parry_clash_direction * slash_span, center[1] - 30),
            (center[0] + self.parry_clash_direction * slash_span, center[1] + 30),
            width=max(3, int(8 * progress)),
        )
        pygame.draw.line(
            overlay,
            (*PLAYER_PARRY_COLOR, max(0, alpha - 40)),
            (center[0] - self.parry_clash_direction * (slash_span - 10), center[1] + 26),
            (center[0] + self.parry_clash_direction * (slash_span - 10), center[1] - 26),
            width=max(2, int(5 * progress)),
        )
        spark_alpha = max(0, min(255, int(255 * (progress ** 0.48))))
        spark_radius = max(4, int(12 * progress))
        pygame.draw.circle(overlay, (255, 255, 255, spark_alpha), center, spark_radius)
        pygame.draw.circle(overlay, (255, 248, 220, max(0, spark_alpha - 36)), center, spark_radius + 10, width=max(2, int(5 * progress)))
        pygame.draw.circle(overlay, (255, 255, 255, max(0, spark_alpha - 12)), center, max(2, spark_radius // 2))
        for angle in (-0.9, -0.25, 0.45, 1.15):
            direction = Vec2(math.cos(angle), math.sin(angle))
            if self.parry_clash_enemy.enemy_type == "lancer":
                direction = direction.rotate(28 * self.parry_clash_direction)
            elif self.parry_clash_enemy.enemy_type == "archer":
                direction = direction.rotate(-22 * self.parry_clash_direction)
            start = Vec2(center) - direction * (8.0 + 4.0 * (1.0 - progress))
            end = Vec2(center) + direction * (24.0 + 20.0 * (1.0 - progress))
            pygame.draw.line(overlay, (255, 255, 255, max(0, spark_alpha - 10)), start, end, width=max(1, int(4 * progress)))
        if progress > 0.72:
            full_flash = self.get_overlay_surface(surface, "parry_clash_flash")
            full_flash.fill((255, 255, 255, int(78 * ((progress - 0.72) / 0.28))))
            overlay.blit(full_flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(overlay, (0, 0))

    def draw_actor(
        self,
        surface: pygame.Surface,
        actor,
        colors: tuple[tuple[int, int, int], tuple[int, int, int]],
        alpha: int = 255,
    ) -> None:
        draw_surface = surface
        draw_alpha = max(0, min(255, int(alpha)))
        if draw_alpha < 255:
            draw_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA).convert_alpha()
        rect = pygame.Rect(int(actor.rect.x - self.camera.x), int(actor.rect.y - self.camera.y), int(actor.rect.width), int(actor.rect.height))
        enemy_launch_ratio = 0.0
        enemy_launch_spin = 0.0
        enemy_darkness = 0.0
        if actor is self.player and self.player_size_bonus > 0:
            inflate_x = int(rect.width * (self.player_size_bonus / 100.0) * 0.6)
            inflate_y = int(rect.height * (self.player_size_bonus / 100.0) * 0.6)
            rect.inflate_ip(inflate_x, inflate_y)
            rect.center = (int(actor.rect.centerx - self.camera.x), int(actor.rect.centery - self.camera.y))
        if isinstance(actor, Enemy) and actor.halo_launch_timer > 0.0:
            enemy_launch_ratio = min(1.0, actor.halo_launch_timer / 0.42)
            enemy_launch_spin = actor.halo_launch_spin * enemy_launch_ratio
            rect.move_ip(int(enemy_launch_spin * 6.0), int(-4.0 * enemy_launch_ratio))
            rect.inflate_ip(int(8.0 * enemy_launch_ratio), int(-10.0 * enemy_launch_ratio))
        if actor.action_state == "dash":
            rect.inflate_ip(12, -8)
        elif actor.action_state == "attack":
            rect.inflate_ip(6, 0)
        elif actor.action_state == "parry":
            rect.inflate_ip(12, 2)
        elif actor.action_state == "guard":
            rect.inflate_ip(10, 2)
        elif actor.action_state == "enter":
            rect.inflate_ip(2, 0)
        elif actor.action_state == "execute":
            rect.inflate_ip(16, 8)
        shadow_rect = pygame.Rect(rect.x + 4, rect.bottom - 6, rect.width - 8, 10)
        if enemy_launch_ratio > 0.0:
            shadow_rect.width = max(10, int(shadow_rect.width * (1.0 - 0.28 * enemy_launch_ratio)))
            shadow_rect.height = max(5, int(shadow_rect.height * (1.0 - 0.22 * enemy_launch_ratio)))
            shadow_rect.centerx = rect.centerx
        pygame.draw.ellipse(draw_surface, SHADOW_COLOR, shadow_rect)
        actor_key = "player"
        actor_states = [actor.action_state, actor.movement_state, "default"]
        if isinstance(actor, Enemy):
            actor_key = actor.enemy_type
        base_color = actor.current_color(*colors)
        sprite_drawn = False
        if isinstance(actor, Enemy):
            enemy_darkness = self.enemy_darkness_factor(actor, surface.get_size())
            base_color = actor.current_color(ALLY_COLOR if actor.is_friendly else actor.body_color, colors[1])
            if self.radiant_judgement is not None and actor.alive and not actor.is_friendly:
                shade = 0.14 if self.radiant_judgement.released else 0.22
                base_color = tuple(max(12, int(channel * shade)) for channel in base_color)
            if actor.is_boss and actor.movement_state == "invade":
                pulse = 0.55 + 0.45 * math.sin(pygame.time.get_ticks() * 0.016)
                base_color = tuple(min(255, int(channel + boost * pulse)) for channel, boost in zip(base_color, (44, 30, 18)))
            if actor.is_boss and actor.attack_profile == "rift" and actor.action_state in {"attack_windup", "attack"}:
                pulse = 0.6 + 0.4 * math.sin(pygame.time.get_ticks() * 0.022)
                base_color = tuple(min(255, int(channel * 0.68 + glow * pulse)) for channel, glow in zip(base_color, (112, 154, 170)))
            if enemy_darkness > 0.0:
                base_color = tuple(max(14, int(channel * (1.0 - enemy_darkness * 0.82))) for channel in base_color)
            if enemy_launch_ratio > 0.0:
                trail = self.get_overlay_surface(draw_surface, "enemy_launch_trail")
                trail_start = (rect.centerx - int(enemy_launch_spin * 18.0), rect.centery + int(3.0 * enemy_launch_ratio))
                trail_end = (rect.centerx, rect.centery)
                pygame.draw.line(trail, (*HALO_WAVE_COLOR, int(92 * enemy_launch_ratio)), trail_start, trail_end, width=max(2, int(5 * enemy_launch_ratio)))
                pygame.draw.line(trail, (*HALO_WAVE_ACCENT, int(62 * enemy_launch_ratio)), (trail_start[0], trail_start[1] - 8), (trail_end[0], trail_end[1] - 4), width=max(1, int(3 * enemy_launch_ratio)))
                draw_surface.blit(trail, (0, 0))
        if actor is self.player and self.fusion_timer > 0.0:
            base_color = tuple(min(255, channel + boost) for channel, boost in zip(base_color, (18, 12, 24)))
        if actor is self.player and self.sword_mania_timer > 0.0:
            pulse = 0.42 + 0.58 * math.sin(pygame.time.get_ticks() * 0.022)
            base_color = (
                max(6, int(16 + 14 * pulse)),
                max(4, int(8 + 10 * pulse)),
                max(4, int(8 + 10 * pulse)),
            )
        if actor is self.player and self.steel_guard_timer > 0.0:
            steel_ratio = min(1.0, self.steel_guard_timer / STEEL_GUARD_DURATION if STEEL_GUARD_DURATION > 0.0 else 1.0)
            base_color = tuple(min(255, int(channel * (1.08 + steel_ratio * 0.24) + 44 * steel_ratio)) for channel in base_color)
        if hasattr(self.app, "resources"):
            sprite_drawn = self.app.resources.draw_actor_sprite(draw_surface, actor_key, actor_states, rect, actor.facing, alpha=255)
        if not sprite_drawn:
            pygame.draw.rect(draw_surface, base_color, rect, border_radius=8)
        if actor is self.player and self.steel_guard_timer > 0.0:
            shine_ratio = 0.45 + 0.55 * math.sin(pygame.time.get_ticks() * 0.012)
            shine_color = tuple(min(255, int(channel * 0.78 + 92 * shine_ratio)) for channel in STEEL_GUARD_ACCENT)
            pygame.draw.line(draw_surface, shine_color, (rect.x + 6, rect.y + 8), (rect.right - 6, rect.y + 18), width=3)
            pygame.draw.line(draw_surface, shine_color, (rect.x + 10, rect.y + 22), (rect.right - 10, rect.y + 30), width=2)
        if enemy_launch_ratio > 0.0:
            pygame.draw.rect(draw_surface, (*HALO_WAVE_ACCENT,), rect.inflate(4, 2), width=max(2, int(3 * enemy_launch_ratio)), border_radius=10)
        if actor is self.player and not sprite_drawn:
            self.draw_player_details(draw_surface, rect)
        if actor.action_state == "block":
            pygame.draw.rect(draw_surface, PLAYER_BLOCK_COLOR, rect.inflate(8, 4), width=3, border_radius=10)
        elif actor.action_state == "parry":
            pygame.draw.rect(draw_surface, PLAYER_PARRY_COLOR, rect.inflate(12, 8), width=4, border_radius=12)
        elif actor.action_state == "guard":
            pygame.draw.rect(draw_surface, PLAYER_BLOCK_COLOR, rect.inflate(14, 6), width=4, border_radius=14)
        if actor is self.player and self.parry_clash_enemy is not None:
            contact = self.get_parry_contact_point(self.parry_clash_enemy)
            hand = (rect.centerx + actor.facing * 6, rect.y + 16)
            blade_tip = (int(contact.x - self.camera.x), int(contact.y - self.camera.y))
            pygame.draw.line(draw_surface, ATTACK_COLOR, hand, blade_tip, width=5)
            guard = (hand[0] + actor.facing * 8, hand[1] + 4)
            pygame.draw.line(draw_surface, PLAYER_PARRY_COLOR, (guard[0], guard[1] - 5), (guard[0], guard[1] + 5), width=3)
        if isinstance(actor, Enemy) and not sprite_drawn:
            self.draw_enemy_details(draw_surface, actor, rect, enemy_darkness)
        if not sprite_drawn:
            eye_x = rect.centerx + actor.facing * 7
            eye_color = (18, 22, 28)
            if isinstance(actor, Enemy) and enemy_darkness > 0.0:
                eye_color = tuple(max(10, int(channel * (1.0 - enemy_darkness * 0.72))) for channel in eye_color)
            pygame.draw.circle(draw_surface, eye_color, (eye_x, rect.y + 16), 3)
        if draw_surface is not surface:
            draw_surface.set_alpha(draw_alpha)
            surface.blit(draw_surface, (0, 0))

    def draw_player_details(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        chest = pygame.Rect(rect.x + 5, rect.y + 8, rect.width - 10, rect.height // 2)
        chest_color = (206, 187, 122)
        if self.sword_mania_timer > 0.0:
            pulse = 0.4 + 0.6 * math.sin(pygame.time.get_ticks() * 0.016)
            chest_color = (max(10, int(22 + 18 * pulse)), 0, 0)
        pygame.draw.rect(surface, chest_color, chest, border_radius=6)
        self.draw_player_brain_relic(surface, rect)
        if self.fusion_timer > 0.0:
            halo_rect = pygame.Rect(rect.centerx - 16, rect.y - 10, 32, 10)
            pygame.draw.ellipse(surface, PLAYER_PARRY_COLOR, halo_rect, width=3)
            cape = [(rect.x + 3, rect.y + 18), (rect.x - 10, rect.bottom - 4), (rect.x + 10, rect.bottom - 1)]
            cape += [(rect.right - 10, rect.bottom - 1), (rect.right + 10, rect.bottom - 4), (rect.right - 3, rect.y + 18)]
            pygame.draw.polygon(surface, (110, 96, 156), cape)
        self.draw_player_weapon(surface, rect)

    def draw_pickup_series_aura(self, surface: pygame.Surface, center: tuple[int, int], item_id: str | None) -> None:
        if item_id is None:
            return
        item = get_equipment(item_id)
        if item.series != "knight":
            return

        overlay = self.get_overlay_surface(surface, "player_knight_auras")
        ticks = pygame.time.get_ticks() * 0.01
        pulse = 0.56 + 0.44 * math.sin(ticks * 1.8 + center[0] * 0.01)
        soft_pulse = 0.5 + 0.5 * math.sin(ticks * 1.2 + center[1] * 0.02)
        outer_color = (248, 226, 164, int(58 + 42 * pulse))
        inner_color = (*item.icon_color, int(44 + 30 * soft_pulse))
        cross_color = (255, 244, 228, int(62 + 34 * soft_pulse))
        outer_rect = pygame.Rect(center[0] - 20, center[1] - 20, 40, 40)
        inner_rect = outer_rect.inflate(-10, -10)
        pygame.draw.ellipse(overlay, outer_color, outer_rect, width=3)
        pygame.draw.ellipse(overlay, inner_color, inner_rect, width=2)
        pygame.draw.line(overlay, cross_color, (center[0] - 16, center[1]), (center[0] + 16, center[1]), width=1)
        pygame.draw.line(overlay, cross_color, (center[0], center[1] - 16), (center[0], center[1] + 16), width=1)
        pygame.draw.circle(overlay, (255, 252, 244, int(38 + 20 * pulse)), center, 6)

        surface.blit(overlay, (0, 0))

    def draw_player_brain_relic(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        brain_item = self.equipment.equipped["brain"]
        ticks = pygame.time.get_ticks() * 0.01
        if is_knight_brain_sword(brain_item):
            if self.player.temporary_shield > 0 or self.brain_sword_fx_timer > 0.0:
                pulse = 0.55 + 0.45 * math.sin(ticks * 1.9)
                glow_rect = rect.inflate(16, 10)
                pygame.draw.ellipse(surface, (120, 198, 255), glow_rect, width=max(2, int(2 + pulse * 2)))
        elif is_knight_brain_scripture(brain_item):
            pulse = 0.5 + 0.5 * math.sin(ticks * 1.6)
            glyph_color = (236, 221, 154)
            aura_color = (168, 140, 255)
            book_glow = pygame.Rect(rect.centerx - 16, rect.y - 8, 18, 12)
            pygame.draw.ellipse(surface, aura_color, book_glow, width=max(1, int(2 + pulse)))
            if self.brain_scripture_fx_timer > 0.0:
                ring_rect = rect.inflate(22, 16)
                pygame.draw.ellipse(surface, glyph_color, ring_rect, width=3)
                pygame.draw.line(surface, glyph_color, (rect.centerx - 16, rect.y - 6), (rect.centerx + 14, rect.y + 4), width=2)
                pygame.draw.line(surface, aura_color, (rect.centerx - 12, rect.y + 2), (rect.centerx + 10, rect.y - 4), width=2)

    def draw_player_weapon(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        hand = (rect.centerx + self.player.facing * 8, rect.y + 20)
        brain_item = self.equipment.equipped["brain"]
        if is_knight_brain_sword(brain_item):
            blade_start = (hand[0] + self.player.facing * 4, hand[1] + 5)
            blade_end = (blade_start[0] + self.player.facing * 24, blade_start[1] - 16)
            pygame.draw.line(surface, (226, 231, 238), blade_start, blade_end, width=4)
            guard = (hand[0] + self.player.facing * 5, hand[1] + 8)
            pygame.draw.line(surface, ACCENT_COLOR, (guard[0], guard[1] - 5), (guard[0], guard[1] + 5), width=3)
            pommel = (hand[0] - self.player.facing * 2, hand[1] + 10)
            pygame.draw.circle(surface, PLAYER_PARRY_COLOR if self.fusion_timer > 0.0 else ACCENT_COLOR, pommel, 3)
            return
        if is_knight_brain_scripture(brain_item):
            book = pygame.Rect(0, 0, 14, 18)
            book.center = (hand[0] - self.player.facing * 10, hand[1] + 2)
            pygame.draw.rect(surface, (207, 181, 104), book, border_radius=3)
            pygame.draw.rect(surface, (100, 72, 36), book, width=2, border_radius=3)
            pygame.draw.line(surface, TEXT_COLOR, (book.centerx, book.y + 3), (book.centerx, book.bottom - 3), width=1)
            ribbon = (book.centerx + self.player.facing * 2, book.bottom + 5)
            pygame.draw.line(surface, PLAYER_PARRY_COLOR, (book.centerx, book.bottom - 1), ribbon, width=2)
            return

    def draw_enemy_details(self, surface: pygame.Surface, enemy: Enemy, rect: pygame.Rect, darkness: float = 0.0) -> None:
        detail_color = enemy.detail_color
        weapon_color = enemy.weapon_color
        if darkness > 0.0:
            detail_color = tuple(max(18, int(channel * (1.0 - darkness * 0.78))) for channel in detail_color)
            weapon_color = tuple(max(20, int(channel * (1.0 - darkness * 0.74))) for channel in weapon_color)

        chest = pygame.Rect(rect.x + 4, rect.y + 8, rect.width - 8, rect.height // 2)
        pygame.draw.rect(surface, detail_color, chest, border_radius=6)

        clash_progress = 0.0
        if self.parry_clash_enemy is enemy and PARRY_CLASH_TIME > 0.0:
            clash_progress = max(0.0, min(1.0, self.parry_clash_timer / PARRY_CLASH_TIME))

        if enemy.enemy_type == "boss":
            mantle = pygame.Rect(rect.x + 3, rect.y + 6, rect.width - 6, 18)
            pygame.draw.rect(surface, detail_color, mantle, border_radius=8)
            if enemy.movement_state == "invade":
                invade_glow = self.get_effect_surface((rect.width + 32, rect.height + 28), "boss_invade_glow")
                pygame.draw.ellipse(invade_glow, (255, 224, 156, 52), invade_glow.get_rect(), width=4)
                pygame.draw.ellipse(invade_glow, (255, 248, 220, 24), invade_glow.get_rect().inflate(-14, -12), width=2)
                surface.blit(invade_glow, (rect.x - 16, rect.y - 14))
            rift_ready = enemy.attack_profile == "rift" and enemy.action_state in {"attack_windup", "attack"}
            if rift_ready:
                rift_glow = self.get_effect_surface((rect.width + 36, rect.height + 34), "boss_rift_glow")
                pygame.draw.ellipse(rift_glow, (92, 138, 154, 54), rift_glow.get_rect(), width=4)
                pygame.draw.ellipse(rift_glow, (232, 244, 246, 38), rift_glow.get_rect().inflate(-16, -14), width=2)
                surface.blit(rift_glow, (rect.x - 18, rect.y - 16))
            horn_left = [(rect.centerx - 10, rect.y - 8), (rect.centerx - 4, rect.y + 4), (rect.centerx - 16, rect.y + 2)]
            horn_right = [(rect.centerx + 10, rect.y - 8), (rect.centerx + 4, rect.y + 4), (rect.centerx + 16, rect.y + 2)]
            pygame.draw.polygon(surface, detail_color, horn_left)
            pygame.draw.polygon(surface, detail_color, horn_right)
            weapon_start = (rect.centerx + enemy.facing * 10, rect.y + 26)
            if rift_ready:
                weapon_end = (weapon_start[0] - enemy.facing * (12 + 10 * clash_progress), weapon_start[1] - (24 + 10 * clash_progress))
                rift_weapon_color = tuple(max(22, int(channel * (1.0 - darkness * 0.62))) for channel in (222, 236, 240))
                pygame.draw.line(surface, rift_weapon_color, weapon_start, weapon_end, width=5)
                cleaver_tip = (weapon_end[0] - enemy.facing * (6 + 6 * clash_progress), weapon_end[1] - 18)
                pygame.draw.line(surface, PLAYER_PARRY_COLOR, weapon_end, cleaver_tip, width=4)
                pygame.draw.line(surface, (74, 108, 124), (weapon_start[0] + enemy.facing * 2, weapon_start[1] + 5), (weapon_end[0] + enemy.facing * 2, weapon_end[1] + 5), width=2)
            else:
                weapon_end = (weapon_start[0] - enemy.facing * (22 + 22 * clash_progress), weapon_start[1] - (18 + 14 * clash_progress))
                pygame.draw.line(surface, weapon_color, weapon_start, weapon_end, width=6)
                cleaver_tip = (weapon_end[0] - enemy.facing * (12 + 8 * clash_progress), weapon_end[1] + 8)
                pygame.draw.line(surface, detail_color, weapon_end, cleaver_tip, width=8)
            if clash_progress > 0.0:
                flare = (weapon_start[0] - enemy.facing * 10, weapon_start[1] + 4)
                flare_color = PLAYER_PARRY_COLOR if rift_ready else ATTACK_COLOR
                pygame.draw.circle(surface, flare_color, (int(flare[0]), int(flare[1])), max(3, int(9 * clash_progress)))
        elif enemy.enemy_type == "blade":
            cape = [(rect.x + 4, rect.y + 16), (rect.x - 6, rect.bottom - 4), (rect.x + 10, rect.bottom - 2)]
            pygame.draw.polygon(surface, detail_color, cape)
            weapon_start = (rect.centerx + enemy.facing * (7 - 5 * clash_progress), rect.y + 20 - 10 * clash_progress)
            weapon_end = (
                weapon_start[0] - enemy.facing * (12 + 34 * clash_progress),
                weapon_start[1] - (8 + 32 * clash_progress),
            )
            pygame.draw.line(surface, weapon_color, weapon_start, weapon_end, width=4)
            if clash_progress > 0.0:
                guard = (weapon_start[0] - enemy.facing * 7, weapon_start[1] + 5)
                pygame.draw.circle(surface, ATTACK_COLOR, (int(guard[0]), int(guard[1])), max(2, int(7 * clash_progress)))
        elif enemy.enemy_type == "lancer":
            plume = [(rect.centerx, rect.y - 8), (rect.centerx + 7, rect.y + 4), (rect.centerx - 7, rect.y + 4)]
            pygame.draw.polygon(surface, detail_color, plume)
            shaft_start = (rect.centerx - enemy.facing * (4 + 10 * clash_progress), rect.centery - 8 * clash_progress)
            shaft_end = (
                shaft_start[0] - enemy.facing * (18 + 54 * clash_progress),
                shaft_start[1] - (18 + 34 * clash_progress),
            )
            pygame.draw.line(surface, weapon_color, shaft_start, shaft_end, width=3)
            tip = (shaft_end[0] - enemy.facing * (6 + 12 * clash_progress), shaft_end[1] - (2 + 10 * clash_progress))
            pygame.draw.line(surface, detail_color, shaft_end, tip, width=4)
            if clash_progress > 0.0:
                butt = (shaft_start[0] + enemy.facing * 5, shaft_start[1] + 10)
                pygame.draw.circle(surface, ATTACK_COLOR, (int(butt[0]), int(butt[1])), max(2, int(6 * clash_progress)))
        elif enemy.enemy_type == "elite_knight":
            crest = [(rect.centerx, rect.y - 7), (rect.centerx + 8, rect.y + 5), (rect.centerx - 8, rect.y + 5)]
            mantle = pygame.Rect(rect.x + 2, rect.y + 6, rect.width - 4, 14)
            shoulder = pygame.Rect(rect.x + 2, rect.y + 12, rect.width - 4, 10)
            pygame.draw.rect(surface, detail_color, mantle, border_radius=7)
            pygame.draw.rect(surface, weapon_color, shoulder, width=2, border_radius=6)
            pygame.draw.polygon(surface, weapon_color, crest)

            summon_ratio = max(0.0, min(1.0, enemy.summon_timer / ELITE_KNIGHT_SUMMON_DURATION)) if enemy.summon_timer > 0.0 else 0.0
            if summon_ratio > 0.0:
                sigil = self.get_effect_surface((rect.width + 28, rect.height + 34), "elite_knight_sigil")
                pulse = 0.45 + 0.55 * math.sin(pygame.time.get_ticks() * 0.012)
                pygame.draw.ellipse(sigil, (138, 228, 204, int((44 + 36 * pulse) * summon_ratio)), sigil.get_rect(), width=3)
                pygame.draw.ellipse(sigil, (226, 248, 236, int((26 + 28 * pulse) * summon_ratio)), sigil.get_rect().inflate(-12, -12), width=2)
                surface.blit(sigil, (rect.x - 14, rect.y - 17))

            hand = (rect.centerx + enemy.facing * (8 - 4 * clash_progress), rect.y + 19 - 8 * clash_progress)
            if enemy.current_attack_is_ranged():
                staff_end = (hand[0] - enemy.facing * (16 + 20 * clash_progress), hand[1] - (10 + 16 * clash_progress))
                pygame.draw.line(surface, weapon_color, hand, staff_end, width=4)
                focus = (staff_end[0] - enemy.facing * 4, staff_end[1] - 6)
                pygame.draw.circle(surface, ACCENT_COLOR, (int(focus[0]), int(focus[1])), 4)
                pygame.draw.circle(surface, detail_color, (int(focus[0]), int(focus[1])), 7, width=2)
            else:
                weapon_end = (hand[0] - enemy.facing * (18 + 30 * clash_progress), hand[1] - (10 + 24 * clash_progress))
                blade_tip = (weapon_end[0] - enemy.facing * (10 + 8 * clash_progress), weapon_end[1] - 10)
                guard = (hand[0] - enemy.facing * 6, hand[1] + 4)
                pygame.draw.line(surface, weapon_color, hand, weapon_end, width=5)
                pygame.draw.line(surface, ACCENT_COLOR, weapon_end, blade_tip, width=4)
                pygame.draw.line(surface, detail_color, (guard[0], guard[1] - 5), (guard[0], guard[1] + 5), width=3)
        else:
            hood = pygame.Rect(rect.x + 6, rect.y + 2, rect.width - 12, 12)
            pygame.draw.rect(surface, detail_color, hood, border_radius=6)
            bow_rect = pygame.Rect(int(rect.centerx + enemy.facing * (6 - 16 * clash_progress) - 7), int(rect.y + 12 - 14 * clash_progress), 14, 24)
            start_angle = -1.2 - 1.25 * clash_progress * enemy.facing
            end_angle = 1.2 - 0.55 * clash_progress * enemy.facing
            pygame.draw.arc(surface, weapon_color, bow_rect, start_angle, end_angle, width=3)
            quiver = pygame.Rect(rect.x + (3 if enemy.facing > 0 else rect.width - 9), rect.y + 10, 6, 18)
            pygame.draw.rect(surface, weapon_color, quiver, border_radius=3)
            if clash_progress > 0.0:
                string_start = (bow_rect.centerx - enemy.facing * 6, bow_rect.top + 1)
                string_end = (bow_rect.centerx - enemy.facing * 2, bow_rect.bottom - 3)
                pygame.draw.line(surface, ATTACK_COLOR, string_start, string_end, width=max(1, int(3 * clash_progress)))

    def draw_player_afterimages(self, surface: pygame.Surface) -> None:
        for image in self.player_afterimages:
            rect = image["rect"]
            life = float(image["life"])
            alpha = max(0, min(140, int(140 * (life / PLAYER_AFTERIMAGE_LIFETIME))))
            draw_rect = pygame.Rect(int(rect.x - self.camera.x), int(rect.y - self.camera.y), int(rect.width), int(rect.height))
            ghost = self.get_effect_surface(draw_rect.size, "player_afterimage")
            ghost.fill((*PLAYER_PARRY_COLOR, alpha))
            surface.blit(ghost, draw_rect.topleft)

    def draw_projectiles(self, surface: pygame.Surface) -> None:
        for projectile in self.projectiles:
            if len(projectile.trail) >= 2:
                overlay = self.get_overlay_surface(surface, "projectile_trail")
                for index, point in enumerate(projectile.trail[:-1]):
                    alpha = max(18, int(110 * (index + 1) / len(projectile.trail)))
                    radius = max(2, int(projectile.rect.width * 0.35))
                    pygame.draw.circle(overlay, (*projectile.tint, alpha), (int(point.x - self.camera.x), int(point.y - self.camera.y)), radius)
                surface.blit(overlay, (0, 0))

            draw_rect = pygame.Rect(int(projectile.rect.x - self.camera.x), int(projectile.rect.y - self.camera.y), int(projectile.rect.width), int(projectile.rect.height))
            pygame.draw.ellipse(surface, projectile.tint, draw_rect)
            outline = PLAYER_PARRY_COLOR if projectile.reflected else (28, 30, 36)
            pygame.draw.ellipse(surface, outline, draw_rect, width=2)

    def draw_slash_effects(self, surface: pygame.Surface) -> None:
        for effect in self.slash_effects:
            life_ratio = effect.life / effect.max_life if effect.max_life > 0.0 else 0.0
            alpha = max(0, min(220, int(220 * life_ratio)))
            overlay = self.get_overlay_surface(surface, "slash_effect")
            start = (int(effect.start.x - self.camera.x), int(effect.start.y - self.camera.y))
            end = (int(effect.end.x - self.camera.x), int(effect.end.y - self.camera.y))
            width = max(3, int(9 * effect.width_scale * life_ratio))
            pygame.draw.line(overlay, (*effect.tint, alpha), start, end, width=width)
            pygame.draw.line(overlay, (*effect.accent_tint, max(0, alpha - 34)), (start[0], start[1] + 14), (end[0], end[1] - 14), width=max(2, width // 2))
            pygame.draw.circle(overlay, (*effect.tint, max(0, alpha - 20)), (int(effect.center.x - self.camera.x), int(effect.center.y - self.camera.y)), max(6, int(20 * effect.width_scale * life_ratio)), width=2)
            surface.blit(overlay, (0, 0))

    def draw_impact_bursts(self, surface: pygame.Surface) -> None:
        for burst in self.impact_bursts:
            life_ratio = burst.life / burst.max_life if burst.max_life > 0.0 else 0.0
            if life_ratio <= 0.0:
                continue
            overlay = self.get_overlay_surface(surface, "impact_burst")
            center = (int(burst.center.x - self.camera.x), int(burst.center.y - self.camera.y))
            ring_radius = max(10, int(burst.radius * (1.0 - life_ratio * 0.2)))
            ring_width = max(2, int(7 * life_ratio))
            glow_radius = max(18, int(ring_radius * 0.55))
            alpha = max(0, min(200, int(200 * life_ratio)))
            pygame.draw.circle(overlay, (*burst.tint, alpha), center, ring_radius, width=ring_width)
            pygame.draw.circle(overlay, (*burst.accent_tint, max(0, alpha - 36)), center, glow_radius, width=max(1, ring_width - 2))
            for index in range(burst.spoke_count):
                angle = (math.tau * index / burst.spoke_count) + (1.0 - life_ratio) * 0.35
                direction = Vec2(math.cos(angle), math.sin(angle))
                inner = Vec2(center) + direction * (ring_radius * 0.48)
                outer = Vec2(center) + direction * (ring_radius + 12.0 + 20.0 * (1.0 - life_ratio))
                pygame.draw.line(overlay, (*burst.tint, max(0, alpha - 20)), inner, outer, width=max(1, ring_width - 1))
            surface.blit(overlay, (0, 0))

    def draw_perfect_dodge_flash(self, surface: pygame.Surface) -> None:
        if self.perfect_dodge_flash_timer <= 0.0:
            return

        progress = self.perfect_dodge_flash_timer / PERFECT_DODGE_FLASH_TIME if PERFECT_DODGE_FLASH_TIME > 0.0 else 0.0
        alpha = max(0, min(132, int(PERFECT_DODGE_FLASH_COLOR[3] * (progress ** 0.7))))
        overlay = self.get_overlay_surface(surface, "perfect_dodge_flash")
        overlay.fill((*PERFECT_DODGE_FLASH_COLOR[:3], alpha))
        surface.blit(overlay, (0, 0))

    def draw_finisher_overlay(self, surface: pygame.Surface) -> None:
        if self.finisher_overlay is None or self.finisher_overlay.max_life <= 0.0:
            return

        progress = self.finisher_overlay.life / self.finisher_overlay.max_life
        center = (int(self.finisher_overlay.center.x - self.camera.x), int(self.finisher_overlay.center.y - self.camera.y))
        overlay = self.get_overlay_surface(surface, "finisher_overlay")
        shade_alpha = max(0, min(self.finisher_overlay.shade_color[3], int(self.finisher_overlay.shade_color[3] * (progress ** 0.92))))
        overlay.fill((*self.finisher_overlay.shade_color[:3], shade_alpha))

        flash_radius = max(surface.get_width(), surface.get_height()) * (0.18 + (1.0 - progress) * 0.82)
        pygame.draw.circle(overlay, (0, 0, 0, 0), center, int(flash_radius))

        line_alpha = max(0, min(220, int(220 * (progress ** 0.7))))
        for index in range(self.finisher_overlay.spoke_count):
            angle = (math.tau * index / self.finisher_overlay.spoke_count) + (1.0 - progress) * 0.12
            direction = Vec2(math.cos(angle), math.sin(angle))
            inner = Vec2(center) + direction * (56.0 + 48.0 * (1.0 - progress))
            outer = Vec2(center) + direction * (420.0 + 240.0 * (1.0 - progress))
            pygame.draw.line(overlay, (*self.finisher_overlay.line_color, line_alpha), inner, outer, width=max(2, int(7 * progress)))

        ring_radius = 120.0 + (1.0 - progress) * 180.0
        pygame.draw.circle(overlay, (*PLAYER_PARRY_COLOR, max(0, line_alpha - 50)), center, int(ring_radius), width=max(2, int(10 * progress)))
        flash_alpha = max(0, min(self.finisher_overlay.flash_color[3], int(self.finisher_overlay.flash_color[3] * (progress ** 0.6))))
        pygame.draw.circle(overlay, (*self.finisher_overlay.flash_color[:3], flash_alpha), center, int(44.0 + (1.0 - progress) * 34.0))
        surface.blit(overlay, (0, 0))

    def draw_enemy_vision(self, surface: pygame.Surface, enemy: Enemy) -> None:
        if not enemy.alive or enemy.action_state in {"hurt", "executed", "dead", "stunned"}:
            return

        eye = enemy.eye_position()
        center = eye - self.camera
        distance = enemy.view_distance
        spread = enemy.view_spread
        far_center = pygame.Vector2(center.x + enemy.facing * distance, center.y)
        top = pygame.Vector2(far_center.x, far_center.y - spread)
        bottom = pygame.Vector2(far_center.x, far_center.y + spread)
        polygon = [(int(center.x), int(center.y)), (int(top.x), int(top.y)), (int(bottom.x), int(bottom.y))]

        overlay = self.get_overlay_surface(surface, "enemy_vision")
        if enemy.enemy_type == "boss":
            base_color = (196, 104, 150, 58)
            alert_color = (255, 172, 212, 88)
        elif enemy.enemy_type == "archer":
            base_color = (126, 214, 168, 54)
            alert_color = (168, 255, 208, 78)
        elif enemy.enemy_type == "lancer":
            base_color = (138, 168, 255, 46)
            alert_color = (194, 212, 255, 76)
        else:
            base_color = ENEMY_VISION_COLOR
            alert_color = ENEMY_VISION_ALERT_COLOR
        color = alert_color if enemy.movement_state in {"chase", "search", "aim", "reposition", "retreat"} else base_color
        pygame.draw.polygon(overlay, color, polygon)
        surface.blit(overlay, (0, 0))

    def draw_enemy_attack_telegraph(self, surface: pygame.Surface, enemy: Enemy) -> None:
        if enemy.action_state not in {"attack_windup", "attack"}:
            return

        hitbox = enemy.attack_hitbox()
        draw_rect = pygame.Rect(int(hitbox.x - self.camera.x), int(hitbox.y - self.camera.y), int(hitbox.width), int(hitbox.height))
        if enemy.attack_profile == "rift":
            color = RIFT_SLASH_COLOR if enemy.action_state == "attack_windup" else RIFT_SLASH_ACCENT
            width = 4 if enemy.action_state == "attack_windup" else 6
            fill = self.get_effect_surface((draw_rect.width, draw_rect.height), "rift_attack_fill")
            fill.fill((*RIFT_SLASH_SHADE, 48 if enemy.action_state == "attack_windup" else 72))
            surface.blit(fill, draw_rect.topleft)
        else:
            color = ENEMY_TELEGRAPH_COLOR if enemy.action_state == "attack_windup" else ENEMY_ATTACK_COLOR
            width = 3 if enemy.action_state == "attack_windup" else 5
        pygame.draw.rect(surface, color, draw_rect, width=width, border_radius=8)

        if enemy.action_state == "attack_windup":
            marker_x = draw_rect.centerx
            marker_y = draw_rect.y - 14
            pygame.draw.circle(surface, color, (marker_x, marker_y), 8)
            if enemy.attack_profile == "jab":
                pygame.draw.line(surface, color, (draw_rect.left, draw_rect.centery), (draw_rect.right, draw_rect.centery), width=3)
            elif enemy.attack_profile == "lunge":
                pygame.draw.line(surface, color, (draw_rect.left, draw_rect.centery), (draw_rect.right + enemy.facing * 22, draw_rect.centery), width=4)
                pygame.draw.circle(surface, color, (draw_rect.right if enemy.facing > 0 else draw_rect.left, draw_rect.centery), 6)
            elif enemy.attack_profile == "rift":
                pygame.draw.line(surface, color, (draw_rect.centerx, draw_rect.top - 10), (draw_rect.centerx, draw_rect.bottom + 10), width=4)
                pygame.draw.line(surface, color, (draw_rect.centerx - 18, draw_rect.top + 10), (draw_rect.centerx + 18, draw_rect.bottom - 10), width=3)
                pygame.draw.line(surface, color, (draw_rect.centerx + 18, draw_rect.top + 10), (draw_rect.centerx - 18, draw_rect.bottom - 10), width=3)
                pygame.draw.circle(surface, color, (draw_rect.centerx, draw_rect.centery), 9, width=3)
            elif enemy.attack_profile == "shot":
                pygame.draw.line(surface, color, (draw_rect.left, draw_rect.centery), (draw_rect.right, draw_rect.centery), width=2)
                aim_rect = pygame.Rect(draw_rect.right - 22 if enemy.facing > 0 else draw_rect.left + 6, draw_rect.centery - 10, 20, 20)
                pygame.draw.ellipse(surface, color, aim_rect, width=3)
            else:
                pygame.draw.arc(surface, color, draw_rect.inflate(16, 20), math.pi * 0.1, math.pi * 0.9, width=3)

    def draw_attack(self, surface: pygame.Surface) -> None:
        hitbox = self.player.attack_hitbox()
        draw_rect = pygame.Rect(int(hitbox.x - self.camera.x), int(hitbox.y - self.camera.y), int(hitbox.width), int(hitbox.height))
        pygame.draw.rect(surface, ATTACK_COLOR, draw_rect, width=4, border_radius=8)

    def draw_execution_effect(self, surface: pygame.Surface) -> None:
        if self.execution_enemy is None:
            return

        overlay = self.get_overlay_surface(surface, "execution_effect")
        overlay.fill(EXECUTION_FLASH_COLOR)
        surface.blit(overlay, (0, 0))

        enemy_center = pygame.Vector2(self.execution_enemy.rect.centerx - self.camera.x, self.execution_enemy.rect.centery - self.camera.y)
        player_center = pygame.Vector2(self.player.rect.centerx - self.camera.x, self.player.rect.centery - self.camera.y)
        if self.execution_style == "lancer":
            pygame.draw.line(surface, ATTACK_COLOR, (player_center.x - self.execution_direction * 10, player_center.y - 28), (enemy_center.x + self.execution_direction * 18, enemy_center.y + 28), width=8)
            pygame.draw.line(surface, PLAYER_PARRY_COLOR, (player_center.x, player_center.y - 36), (enemy_center.x, enemy_center.y + 36), width=4)
            pygame.draw.circle(surface, PLAYER_PARRY_COLOR, (int(enemy_center.x), int(enemy_center.y)), 22, width=3)
        elif self.execution_style == "archer":
            sweep_rect = pygame.Rect(int(min(player_center.x, enemy_center.x)) - 20, int(min(player_center.y, enemy_center.y)) - 24, int(abs(player_center.x - enemy_center.x)) + 40, 60)
            pygame.draw.arc(surface, ATTACK_COLOR, sweep_rect, math.pi * 0.2, math.pi * 0.92, width=8)
            pygame.draw.line(surface, PLAYER_PARRY_COLOR, (player_center.x, player_center.y - 16), (enemy_center.x, enemy_center.y - 26), width=4)
        else:
            pygame.draw.line(surface, ATTACK_COLOR, player_center, enemy_center, width=10)
            pygame.draw.line(surface, PLAYER_PARRY_COLOR, (player_center.x, player_center.y - 24), (enemy_center.x, enemy_center.y + 24), width=5)
            pygame.draw.circle(surface, PLAYER_PARRY_COLOR, (int(enemy_center.x), int(enemy_center.y)), 18, width=4)

    def draw_enemy_health(self, surface: pygame.Surface, enemy: Enemy) -> None:
        if enemy.health >= enemy.max_health:
            return
        ratio = max(0.0, min(1.0, enemy.health / enemy.max_health))
        if enemy.is_boss:
            bar = pygame.Rect(int(enemy.rect.centerx - self.camera.x - 72), int(enemy.rect.y - self.camera.y - 18), 144, 9)
            label = self.app.get_font(14, bold=True).render("BOSS", True, ATTACK_COLOR)
            surface.blit(label, (bar.x, bar.y - 16))
        else:
            bar = pygame.Rect(int(enemy.rect.centerx - self.camera.x - 20), int(enemy.rect.y - self.camera.y - 10), 40, 5)
        pygame.draw.rect(surface, PANEL_BORDER, bar, border_radius=3)
        fill = bar.copy()
        fill.width = max(1, int(fill.width * ratio))
        pygame.draw.rect(surface, DANGER_COLOR, fill, border_radius=3)