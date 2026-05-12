from __future__ import annotations

import math
from array import array

import pygame


class CombatAudio:
    def __init__(self) -> None:
        self.enabled = pygame.mixer.get_init() is not None
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        if not self.enabled:
            return

        self.sounds = {
            "enemy_jab": self._create_tone(660, 45, 0.20, wave="square", falloff=0.90),
            "enemy_cleave": self._create_tone(320, 95, 0.28, wave="sine", falloff=0.86),
            "enemy_lunge": self._create_sweep(540, 240, 110, 0.26),
            "enemy_shot": self._create_sweep(920, 520, 75, 0.18),
            "enemy_rift": self._create_sweep(180, 48, 150, 0.30),
            "halo_shockwave": self._create_halo_shockwave(0.40),
            "radiant_judgement_charge": self._create_radiant_judgement_charge(0.44),
            "radiant_judgement_prep": self._create_radiant_judgement_prep(0.42),
            "radiant_judgement_release": self._create_radiant_judgement_release(0.56),
            "meteor_lances_cast": self._create_meteor_lances_cast(0.42),
            "meteor_lance_impact": self._create_meteor_lance_impact(0.46),
            "guard": self._create_tone(240, 70, 0.24, wave="square", falloff=0.84),
            "parry": self._create_sweep(1180, 760, 90, 0.24),
            "parry_blade_clash": self._create_glass_clash(0.50),
            "parry_blade_click": self._create_crystal_click(0.34),
            "parry_impact": self._create_sweep(2260, 980, 58, 0.10),
            "dash_slice": self._create_sweep(980, 420, 85, 0.20),
            "perfect_dodge_impact": self._create_tone(118, 150, 0.34, wave="square", falloff=0.78),
            "blink_cut_finish": self._create_sweep(2100, 180, 180, 0.34),
            "perfect_dodge_slash_blade": self._create_sweep(1520, 560, 105, 0.27),
            "perfect_dodge_slash_lancer": self._create_sweep(1360, 460, 115, 0.26),
            "perfect_dodge_slash_archer": self._create_sweep(1680, 700, 90, 0.24),
            "execution_pull": self._create_sweep(220, 140, 120, 0.20),
            "execution_strike": self._create_tone(150, 160, 0.34, wave="square", falloff=0.80),
            "fusion_start": self._create_sweep(180, 520, 180, 0.26),
            "fusion_crash": self._create_fusion_crash(0.54),
            "heart_release": self._create_sweep(420, 1180, 220, 0.24),
            "altar_awaken": self._create_altar_awaken(0.42),
        }

    def play(self, name: str, volume_scale: float = 1.0) -> None:
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is None:
            return
        try:
            channel = sound.play()
            if channel is not None:
                channel.set_volume(max(0.0, min(1.0, volume_scale)))
        except pygame.error:
            self.enabled = False

    def _create_tone(self, frequency: float, duration_ms: int, volume: float, wave: str = "sine", falloff: float = 0.88) -> pygame.mixer.Sound:
        sample_rate, _, channels = pygame.mixer.get_init()
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        samples = array("h")
        for index in range(sample_count):
            progress = index / sample_count
            angle = 2.0 * math.pi * frequency * progress * duration_ms / 1000.0
            if wave == "square":
                raw = 1.0 if math.sin(angle) >= 0.0 else -1.0
            else:
                raw = math.sin(angle)
            envelope = ((1.0 - progress) ** 2) * falloff + (1.0 - falloff)
            value = int(max(-1.0, min(1.0, raw * envelope * volume)) * 32767)
            for _ in range(channels):
                samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _create_sweep(self, start_frequency: float, end_frequency: float, duration_ms: int, volume: float) -> pygame.mixer.Sound:
        sample_rate, _, channels = pygame.mixer.get_init()
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        samples = array("h")
        phase = 0.0
        for index in range(sample_count):
            progress = index / sample_count
            frequency = start_frequency + (end_frequency - start_frequency) * progress
            phase += 2.0 * math.pi * frequency / sample_rate
            raw = math.sin(phase)
            envelope = (1.0 - progress) ** 2
            value = int(max(-1.0, min(1.0, raw * envelope * volume)) * 32767)
            for _ in range(channels):
                samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _create_glass_clash(self, volume: float) -> pygame.mixer.Sound:
        sample_rate, _, channels = pygame.mixer.get_init()
        duration_ms = 68
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        samples = array("h")
        phase_a = 0.0
        phase_b = 0.0
        phase_c = 0.0
        phase_d = 0.0
        for index in range(sample_count):
            progress = index / sample_count
            phase_a += 2.0 * math.pi * (4180.0 - 1180.0 * progress) / sample_rate
            phase_b += 2.0 * math.pi * (5660.0 - 1620.0 * progress) / sample_rate
            phase_c += 2.0 * math.pi * (7120.0 - 2080.0 * progress) / sample_rate
            phase_d += 2.0 * math.pi * (2480.0 - 760.0 * progress) / sample_rate
            chime = math.sin(phase_a) * 0.28 + math.sin(phase_b) * 0.31 + math.sin(phase_c) * 0.29 + math.sin(phase_d) * 0.04
            shard = (1.0 if math.sin(phase_c * 0.88) >= 0.0 else -1.0) * 0.18
            click = math.exp(-progress * 84.0) * math.sin(phase_b * 1.62) * 0.44
            air = math.exp(-progress * 48.0) * math.sin(phase_c * 0.53) * 0.06
            envelope = ((1.0 - progress) ** 5.2) * (1.0 if progress < 0.022 else 0.70)
            value = int(max(-1.0, min(1.0, (chime + shard + click + air) * envelope * volume)) * 32767)
            for _ in range(channels):
                samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _create_crystal_click(self, volume: float) -> pygame.mixer.Sound:
        sample_rate, _, channels = pygame.mixer.get_init()
        duration_ms = 28
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        samples = array("h")
        phase_a = 0.0
        phase_b = 0.0
        for index in range(sample_count):
            progress = index / sample_count
            phase_a += 2.0 * math.pi * (7420.0 - 1880.0 * progress) / sample_rate
            phase_b += 2.0 * math.pi * (9160.0 - 2360.0 * progress) / sample_rate
            ping = math.sin(phase_a) * 0.54 + math.sin(phase_b) * 0.36
            snap = (1.0 if math.sin(phase_b * 0.92) >= 0.0 else -1.0) * 0.18
            envelope = math.exp(-progress * 18.0) * ((1.0 - progress) ** 3.6)
            value = int(max(-1.0, min(1.0, (ping + snap) * envelope * volume)) * 32767)
            for _ in range(channels):
                samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _create_fusion_crash(self, volume: float) -> pygame.mixer.Sound:
        sample_rate, _, channels = pygame.mixer.get_init()
        duration_ms = 190
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        samples = array("h")
        phase_low = 0.0
        phase_mid = 0.0
        phase_hi = 0.0
        phase_ring = 0.0
        phase_body = 0.0
        for index in range(sample_count):
            progress = index / sample_count
            phase_low += 2.0 * math.pi * (82.0 - 26.0 * progress) / sample_rate
            phase_mid += 2.0 * math.pi * (246.0 - 84.0 * progress) / sample_rate
            phase_hi += 2.0 * math.pi * (1640.0 - 680.0 * progress) / sample_rate
            phase_ring += 2.0 * math.pi * (2160.0 - 1160.0 * progress) / sample_rate
            phase_body += 2.0 * math.pi * (128.0 - 36.0 * progress) / sample_rate
            slam = math.sin(phase_low) * 0.64 + math.sin(phase_mid) * 0.24 + math.sin(phase_body) * 0.20
            crack = (1.0 if math.sin(phase_hi) >= 0.0 else -1.0) * 0.22
            ring = math.sin(phase_ring) * 0.16
            tail = math.exp(-progress * 6.2) * (math.sin(phase_mid * 0.62) * 0.16 + math.sin(phase_ring * 0.47) * 0.10)
            envelope = math.exp(-progress * 4.9) * ((1.0 - progress) ** 1.55)
            if progress < 0.06:
                envelope *= 1.38
            value = int(max(-1.0, min(1.0, (slam + crack + ring + tail) * envelope * volume)) * 32767)
            for _ in range(channels):
                samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _create_altar_awaken(self, volume: float) -> pygame.mixer.Sound:
        sample_rate, _, channels = pygame.mixer.get_init()
        duration_ms = 260
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        samples = array("h")
        phase_low = 0.0
        phase_mid = 0.0
        phase_hi = 0.0
        for index in range(sample_count):
            progress = index / sample_count
            phase_low += 2.0 * math.pi * (180.0 + 60.0 * progress) / sample_rate
            phase_mid += 2.0 * math.pi * (620.0 + 180.0 * progress) / sample_rate
            phase_hi += 2.0 * math.pi * (1460.0 + 360.0 * progress) / sample_rate
            hum = math.sin(phase_low) * 0.30 + math.sin(phase_mid) * 0.22
            shine = math.sin(phase_hi) * 0.18
            envelope = (progress ** 0.45) * ((1.0 - progress) ** 1.2)
            value = int(max(-1.0, min(1.0, (hum + shine) * envelope * volume * 2.2)) * 32767)
            for _ in range(channels):
                samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _create_halo_shockwave(self, volume: float) -> pygame.mixer.Sound:
        sample_rate, _, channels = pygame.mixer.get_init()
        duration_ms = 170
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        samples = array("h")
        phase_low = 0.0
        phase_mid = 0.0
        phase_high = 0.0
        for index in range(sample_count):
            progress = index / sample_count
            phase_low += 2.0 * math.pi * (126.0 - 28.0 * progress) / sample_rate
            phase_mid += 2.0 * math.pi * (540.0 - 240.0 * progress) / sample_rate
            phase_high += 2.0 * math.pi * (1880.0 - 920.0 * progress) / sample_rate
            body = math.sin(phase_low) * 0.42 + math.sin(phase_mid) * 0.24
            flare = math.sin(phase_high) * 0.12
            burst = math.exp(-progress * 11.5) * 0.34
            envelope = math.exp(-progress * 5.1) * ((1.0 - progress) ** 1.18)
            if progress < 0.08:
                envelope *= 1.22
            value = int(max(-1.0, min(1.0, (body + flare + burst) * envelope * volume)) * 32767)
            for _ in range(channels):
                samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _create_radiant_judgement_charge(self, volume: float) -> pygame.mixer.Sound:
        sample_rate, _, channels = pygame.mixer.get_init()
        duration_ms = 420
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        samples = array("h")
        phase_low = 0.0
        phase_mid = 0.0
        phase_high = 0.0
        for index in range(sample_count):
            progress = index / sample_count
            phase_low += 2.0 * math.pi * (140.0 + 52.0 * progress) / sample_rate
            phase_mid += 2.0 * math.pi * (620.0 + 420.0 * progress) / sample_rate
            phase_high += 2.0 * math.pi * (1280.0 + 860.0 * progress) / sample_rate
            hum = math.sin(phase_low) * 0.26
            rise = math.sin(phase_mid) * (0.18 + 0.12 * progress)
            sheen = math.sin(phase_high) * 0.12
            envelope = (0.22 + progress * 0.78) * ((1.0 - progress) ** 0.3)
            value = int(max(-1.0, min(1.0, (hum + rise + sheen) * envelope * volume)) * 32767)
            for _ in range(channels):
                samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _create_radiant_judgement_prep(self, volume: float) -> pygame.mixer.Sound:
        sample_rate, _, channels = pygame.mixer.get_init()
        duration_ms = 120
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        samples = array("h")
        phase_low = 0.0
        phase_mid = 0.0
        phase_hi = 0.0
        for index in range(sample_count):
            progress = index / sample_count
            phase_low += 2.0 * math.pi * (240.0 - 160.0 * progress) / sample_rate
            phase_mid += 2.0 * math.pi * (920.0 - 580.0 * progress) / sample_rate
            phase_hi += 2.0 * math.pi * (1880.0 - 1380.0 * progress) / sample_rate
            suction = -math.sin(phase_low) * 0.34 - math.sin(phase_mid) * 0.20
            hiss = math.sin(phase_hi) * 0.10
            envelope = (progress ** 0.25) * math.exp(-progress * 8.8)
            if progress < 0.18:
                envelope *= 1.24
            value = int(max(-1.0, min(1.0, (suction + hiss) * envelope * volume)) * 32767)
            for _ in range(channels):
                samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _create_radiant_judgement_release(self, volume: float) -> pygame.mixer.Sound:
        sample_rate, _, channels = pygame.mixer.get_init()
        duration_ms = 210
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        samples = array("h")
        phase_a = 0.0
        phase_b = 0.0
        phase_c = 0.0
        phase_d = 0.0
        phase_e = 0.0
        for index in range(sample_count):
            progress = index / sample_count
            phase_a += 2.0 * math.pi * (2860.0 - 1320.0 * progress) / sample_rate
            phase_b += 2.0 * math.pi * (1380.0 - 360.0 * progress) / sample_rate
            phase_c += 2.0 * math.pi * (92.0 - 18.0 * progress) / sample_rate
            phase_d += 2.0 * math.pi * (204.0 - 46.0 * progress) / sample_rate
            phase_e += 2.0 * math.pi * (3640.0 - 2100.0 * progress) / sample_rate
            slash = math.sin(phase_a) * 0.32 + math.sin(phase_b) * 0.26
            body = math.sin(phase_c) * 0.42 + math.sin(phase_d) * 0.18
            crack = (1.0 if math.sin(phase_e) >= 0.0 else -1.0) * 0.20
            shock = math.exp(-progress * 14.0) * 0.34
            envelope = math.exp(-progress * 6.6) * ((1.0 - progress) ** 1.05)
            if progress < 0.05:
                envelope *= 1.46
            value = int(max(-1.0, min(1.0, (slash + body + crack + shock) * envelope * volume)) * 32767)
            for _ in range(channels):
                samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _create_meteor_lances_cast(self, volume: float) -> pygame.mixer.Sound:
        sample_rate, _, channels = pygame.mixer.get_init()
        duration_ms = 190
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        samples = array("h")
        phase_a = 0.0
        phase_b = 0.0
        for index in range(sample_count):
            progress = index / sample_count
            phase_a += 2.0 * math.pi * (420.0 + 620.0 * progress) / sample_rate
            phase_b += 2.0 * math.pi * (860.0 + 1240.0 * progress) / sample_rate
            whoosh = math.sin(phase_a) * 0.24 + math.sin(phase_b) * 0.18
            envelope = (progress ** 0.35) * ((1.0 - progress) ** 0.85)
            value = int(max(-1.0, min(1.0, whoosh * envelope * volume * 2.1)) * 32767)
            for _ in range(channels):
                samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _create_meteor_lance_impact(self, volume: float) -> pygame.mixer.Sound:
        sample_rate, _, channels = pygame.mixer.get_init()
        duration_ms = 180
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        samples = array("h")
        phase_low = 0.0
        phase_mid = 0.0
        phase_high = 0.0
        for index in range(sample_count):
            progress = index / sample_count
            phase_low += 2.0 * math.pi * (86.0 - 22.0 * progress) / sample_rate
            phase_mid += 2.0 * math.pi * (280.0 - 110.0 * progress) / sample_rate
            phase_high += 2.0 * math.pi * (1760.0 - 920.0 * progress) / sample_rate
            slam = math.sin(phase_low) * 0.46 + math.sin(phase_mid) * 0.18
            flare = (1.0 if math.sin(phase_high) >= 0.0 else -1.0) * 0.16
            envelope = math.exp(-progress * 5.8) * ((1.0 - progress) ** 1.6)
            value = int(max(-1.0, min(1.0, (slam + flare) * envelope * volume)) * 32767)
            for _ in range(channels):
                samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())