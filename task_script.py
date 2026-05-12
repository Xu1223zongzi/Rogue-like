import sys
import os

# Set up path to import from game
sys.path.append(os.getcwd())

from dataclasses import dataclass

@dataclass
class HudStatusBar:
    key: str
    label: str
    ratio: float
    fill_color: tuple
    back_color: tuple
    edge_color: tuple
    value_text: str

# Mocking constants
PALADIN_FUSION_COOLDOWN = 60.0
PALADIN_SCRIPTURE_COOLDOWN = 60.0
PALADIN_HALO_COOLDOWN = 60.0
PALADIN_RAIN_COOLDOWN = 60.0
MINOR_SKILL_COOLDOWN = 60.0
SHIELD_BASTION_INTERVAL = 20.0
SWORD_MANIA_DURATION = 10.0
SHIELD_BASTION_DURATION = 5.0

# Mocking functions
def max_cooldown_for_item(item, default): return default
def is_knight_brain_scripture(item): return True
def is_knight_brain_sword(item): return True
def effective_tier_for_slot(eq, slot): return 3
def scripture_brain_rescue_cooldown_seconds(tier): return 10.0
def knight_shield_hit_goal(tier): return 5

class GameplayScene:
    def __init__(self):
        pass

    def format_status_seconds(self, s):
        return f"{s:.1f}s"

    def has_active_major(self, slot):
        return True
    
    def minor_tier(self, archetype):
        if archetype == "shield": return 3
        return 4

    def hud_status_bars(self):
        # We'll paste the logic here or just rely on the object having it.
        # Since I can't easily import the class logic without its dependencies, 
        # I will redefine the logic here as requested to simulate the scene's behavior.
        bars = []
        if self.player.temporary_shield > 0:
            bars.append(HudStatusBar(key="shield", label="SH", ratio=self.player.temporary_shield/100, fill_color=None, back_color=None, edge_color=None, value_text=str(int(self.player.temporary_shield))))
        
        if self.equipment.equipped["heart"] is not None and max(self.fusion_cooldown, self.fusion_timer) > 0.0:
            heart_cooldown = max(self.fusion_cooldown, self.fusion_timer)
            bars.append(HudStatusBar(key="heart_cd", label="HT", ratio=heart_cooldown/60, fill_color=None, back_color=None, edge_color=None, value_text=self.format_status_seconds(heart_cooldown)))

        if self.equipment.equipped["brain"] is not None and self.brain_skill_cooldown > 0.0:
            bars.append(HudStatusBar(key="brain_cd", label="BR", ratio=self.brain_skill_cooldown/60, fill_color=None, back_color=None, edge_color=None, value_text=self.format_status_seconds(self.brain_skill_cooldown)))

        if is_knight_brain_scripture(self.equipment.equipped["brain"]) and self.brain_rescue_cooldown > 0.0:
            bars.append(HudStatusBar(key="rescue_cd", label="RC", ratio=self.brain_rescue_cooldown/10, fill_color=None, back_color=None, edge_color=None, value_text=self.format_status_seconds(self.brain_rescue_cooldown)))

        if is_knight_brain_sword(self.equipment.equipped["brain"]) and self.has_active_major("brain"):
            hit_goal = knight_shield_hit_goal(3)
            progress_hits = self.brain_chain_hits
            bars.append(HudStatusBar(key="brain_hits", label="BK", ratio=progress_hits/hit_goal, fill_color=None, back_color=None, edge_color=None, value_text=f"{progress_hits}/{hit_goal}"))

        if self.equipment.equipped["left_eye"] is not None and self.left_skill_cooldown > 0.0:
            bars.append(HudStatusBar(key="left_cd", label="LE", ratio=self.left_skill_cooldown/60, fill_color=None, back_color=None, edge_color=None, value_text=self.format_status_seconds(self.left_skill_cooldown)))

        if self.equipment.equipped["right_eye"] is not None and self.right_skill_cooldown > 0.0:
            bars.append(HudStatusBar(key="right_cd", label="RE", ratio=self.right_skill_cooldown/60, fill_color=None, back_color=None, edge_color=None, value_text=self.format_status_seconds(self.right_skill_cooldown)))

        if self.minor_skill_cooldown > 0.0:
            bars.append(HudStatusBar(key="minor_cd", label="CD", ratio=self.minor_skill_cooldown/60, fill_color=None, back_color=None, edge_color=None, value_text=self.format_status_seconds(self.minor_skill_cooldown)))

        if self.minor_tier("shield") >= 3 and self.shield_bastion_timer < SHIELD_BASTION_INTERVAL:
            bars.append(HudStatusBar(key="shield_bastion", label="SB", ratio=self.shield_bastion_timer/SHIELD_BASTION_INTERVAL, fill_color=None, back_color=None, edge_color=None, value_text=self.format_status_seconds(self.shield_bastion_timer)))

        return bars

@dataclass
class Player:
    temporary_shield: float
    max_health: float = 100.0

@dataclass
class Equipment:
    equipped: dict

# Construct the object
scene = GameplayScene.__new__(GameplayScene)

# Set fields
scene.player = Player(temporary_shield=20.0)
scene.equipment = Equipment(equipped={"heart": "item", "brain": "item", "left_eye": "item", "right_eye": "item"})
scene.fusion_cooldown = 12.0
scene.fusion_timer = 0.0
scene.brain_skill_cooldown = 6.0
scene.brain_rescue_cooldown = 4.0
scene.brain_chain_hits = 2
scene.left_skill_cooldown = 3.0
scene.right_skill_cooldown = 5.0
scene.minor_skill_cooldown = 10.0
scene.shield_bastion_timer = 12.0

# Bind methods to the instance (since we didn't call __init__)
scene.format_status_seconds = lambda s: f"{s:.1f}s"
scene.has_active_major = lambda slot: True
scene.minor_tier = lambda archetype: 4 if archetype != "shield" else 3

# Execute and print
bars = scene.hud_status_bars()
for bar in bars:
    print(f"Key: {bar.key}, Label: {bar.label}, Value: {bar.value_text}")

