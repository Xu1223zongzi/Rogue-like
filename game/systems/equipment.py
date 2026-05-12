from __future__ import annotations

from dataclasses import dataclass, field


SLOT_ORDER = ("heart", "brain", "left_eye", "right_eye")
SLOT_LABELS = {
    "heart": "Heart",
    "brain": "Brain",
    "left_eye": "Left Eye",
    "right_eye": "Right Eye",
}

SERIES_LABELS = {
    "knight": "Knight Series",
}

SET_TIER_LABELS = {
    1: "T1",
    2: "T2",
    3: "T3",
    4: "T4",
}


@dataclass(frozen=True)
class EquipmentDefinition:
    item_id: str
    name: str
    slot: str
    series: str
    icon_color: tuple[int, int, int]
    major_name: str
    major_description: str
    minor_name: str | None = None
    minor_description: str | None = None


@dataclass
class PassiveSummary:
    main_passive: str
    active_passives: list[str]
    inactive_passives: list[str]
    series_label: str
    series_count: int
    tier_label: str
    major_passive_card: PassiveCardSummary | None
    minor_passive_cards: list[PassiveCardSummary]


@dataclass(frozen=True)
class PassiveCardSummary:
    key: str
    title: str
    subtitle: str
    description: str
    tier_label: str
    item_id: str | None
    visible: bool


def active_series(state: EquipmentState) -> str:
    heart_id = state.equipped["heart"]
    if heart_id is not None:
        return EQUIPMENT_DEFS[heart_id].series
    for item_id in state.equipped.values():
        if item_id is not None:
            return EQUIPMENT_DEFS[item_id].series
    return "knight"


def major_is_active(state: EquipmentState, slot: str) -> bool:
    item_id = state.equipped[slot]
    if item_id is None:
        return False
    if slot == "heart":
        return True
    heart_id = state.equipped["heart"]
    if heart_id is None:
        return True
    return EQUIPMENT_DEFS[item_id].series == EQUIPMENT_DEFS[heart_id].series


def effective_tier_for_slot(state: EquipmentState, slot: str) -> int:
    item_id = state.equipped.get(slot)
    if item_id is None:
        return 0
    if slot == "heart":
        return knight_tier(state)
    heart_id = state.equipped["heart"]
    if heart_id is None:
        return 1
    if EQUIPMENT_DEFS[item_id].series != EQUIPMENT_DEFS[heart_id].series:
        return 0
    return max(1, knight_tier(state))


def is_knight_brain(item_id: str | None) -> bool:
    return item_id in {"knight_brain_sword", "knight_brain_scripture"}


def is_knight_brain_sword(item_id: str | None) -> bool:
    return item_id == "knight_brain_sword"


def is_knight_brain_scripture(item_id: str | None) -> bool:
    return item_id == "knight_brain_scripture"


MINOR_ARCHETYPE_ITEMS: dict[str, set[str]] = {
    "sword": {"knight_brain_sword", "knight_left_eye_blade"},
    "control": {"knight_right_eye_rain"},
    "shield": {"knight_brain_scripture", "knight_left_eye_halo"},
    "summon": {"knight_right_eye_spirit"},
}


def knight_minor_tier(state: EquipmentState, archetype: str) -> int:
    item_ids = MINOR_ARCHETYPE_ITEMS.get(archetype, set())
    equipped_count = 0
    for item_id in state.equipped.values():
        if item_id not in item_ids:
            continue
        if EQUIPMENT_DEFS[item_id].series != "knight":
            continue
        equipped_count += 1

    return min(4, equipped_count)


def passive_tier_details(state: EquipmentState, tier: int) -> list[str]:
    series = active_series(state)
    series_label = SERIES_LABELS.get(series, series.title())
    lines = [
        f"{series_label}: size +{knight_size_bonus_percent(tier)}%, defense +{knight_defense_bonus_percent(tier)}%",
    ]

    for slot in SLOT_ORDER:
        item_id = state.equipped[slot]
        if item_id is None:
            continue
        item = EQUIPMENT_DEFS[item_id]
        if item.series != series:
            continue
        slot_tier = tier if slot == "heart" else effective_tier_for_slot(state, slot)
        if item_id == "knight_heart":
            line = "Armor Communion: fusion grants a holy crash shield"
            if tier >= 1:
                line += f", body impact stun {knight_stun_seconds(tier):.0f}s"
            if tier >= 4:
                line += ", one death ward while fusion lasts"
            lines.append(line)
        elif is_knight_brain_sword(item_id):
            lines.append("Shield Rhythm: T1 unlocks block while the knight brain is equipped")
            lines.append(f"Shield Rhythm: gain shield every {knight_shield_hit_goal(slot_tier)} hits")
            lines.append("Blade March: move faster while the sword is equipped")
        elif is_knight_brain_scripture(item_id):
            lines.append("Sacred Cleansing: T1 unlocks block while the knight brain is equipped")
            lines.append("Sacred Cleansing: purge stagger and restore combat posture when you are hit")
            lines.append("Restoration Rite: press R to restore health and sanity")
        elif item_id == "knight_left_eye_halo":
            line = f"Sanctuary Ring: halo radius {int(knight_halo_radius_px(slot_tier))} px, pushes enemies, reflects shots, and heals"
            if slot_tier >= 3:
                line += ", releases a knockback wave when it ends"
            if slot_tier >= 4:
                line += ", and emits damaging holy shockwaves while active"
            lines.append(line)
        elif item_id == "knight_left_eye_blade":
            lines.append(f"Radiant Slash: chain {knight_blade_combo_hits(slot_tier)} locking slashes within {int(knight_blade_reach_px(slot_tier))} px")
        elif item_id == "knight_right_eye_rain":
            lines.append(f"Sky Spear Barrage: call down {knight_rain_strike_count(slot_tier)} falling blades over {int(knight_rain_spacing_px(slot_tier) * (knight_rain_strike_count(slot_tier) - 1))} px")
        elif item_id == "knight_right_eye_spirit":
            if slot_tier >= 4:
                lines.append("Conversion Oath: summon 2 bound elite knights at full health")
            else:
                lines.append(f"Conversion Oath: convert targets in front within {int(knight_spirit_range_px(slot_tier))} px")

        if item.minor_name and item.minor_description:
            lines.append(f"{item.minor_name}: {item.minor_description}")

    return lines


def compact_major_summary(item_id: str, tier: int) -> str:
    if item_id == "knight_heart":
        summary = f"Fusion shield, crash stun {knight_stun_seconds(tier):.0f}s"
        if tier >= 4:
            summary += ", death ward"
        return summary
    if is_knight_brain_sword(item_id):
        return f"T1 block, shield every {knight_shield_hit_goal(tier)} hits, faster movement"
    if is_knight_brain_scripture(item_id):
        return "T1 block, cleanse stagger on hit, R restores health and sanity"
    if item_id == "knight_left_eye_halo":
        summary = f"Halo {int(knight_halo_radius_px(tier))} px, reflect, heal"
        if tier >= 3:
            summary += ", end wave"
        if tier >= 4:
            summary += ", pulse damage"
        return summary
    if item_id == "knight_left_eye_blade":
        return f"{knight_blade_combo_hits(tier)} slashes within {int(knight_blade_reach_px(tier))} px"
    if item_id == "knight_right_eye_rain":
        return f"{knight_rain_strike_count(tier)} falling blades"
    if item_id == "knight_right_eye_spirit":
        if tier >= 4:
            return "Summon 2 bound elite knights"
        return f"Convert targets within {int(knight_spirit_range_px(tier))} px"
    return EQUIPMENT_DEFS[item_id].major_name


def compact_minor_summary(item_id: str) -> str | None:
    item = EQUIPMENT_DEFS[item_id]
    if item_id == "knight_brain_sword":
        return "Faster movement and shield bursts"
    if item_id == "knight_brain_scripture":
        return "Rescue on hit and quick prayer restore"
    if item_id == "knight_left_eye_halo":
        return "Stronger healing"
    if item_id == "knight_left_eye_blade":
        return "Longer reach"
    if item_id == "knight_right_eye_rain":
        return "Shorter cooldowns"
    if item_id == "knight_right_eye_spirit":
        return "Safer parry timing"
    if item.minor_name is None:
        return None
    return item.minor_name


def dominant_major_item_id(state: EquipmentState) -> str | None:
    grouped_counts: dict[str, int] = {}
    grouped_order: dict[str, int] = {}
    grouped_item: dict[str, str] = {}

    for index, slot in enumerate(SLOT_ORDER):
        item_id = state.equipped[slot]
        if item_id is None:
            continue
        item = EQUIPMENT_DEFS[item_id]
        key = item.major_name
        grouped_counts[key] = grouped_counts.get(key, 0) + 1
        if key not in grouped_order:
            grouped_order[key] = index
            grouped_item[key] = item_id

    if not grouped_counts:
        return None

    dominant_key = max(grouped_counts, key=lambda key: (grouped_counts[key], -grouped_order[key]))
    return grouped_item[dominant_key]


def build_major_passive_card(state: EquipmentState) -> PassiveCardSummary | None:
    item_id = dominant_major_item_id(state)
    if item_id is None:
        return None

    item = EQUIPMENT_DEFS[item_id]
    tier = knight_tier(state) if item.slot == "heart" else effective_tier_for_slot(state, item.slot)
    return PassiveCardSummary(
        key="major",
        title=item.major_name,
        subtitle=short_slot_label(item.slot),
        description=compact_major_summary(item_id, max(1, tier)),
        tier_label=SET_TIER_LABELS.get(max(1, tier), "T1"),
        item_id=item_id,
        visible=True,
    )


def build_minor_passive_cards(state: EquipmentState) -> list[PassiveCardSummary]:
    cards: list[PassiveCardSummary] = []
    minor_meta = (
        ("sword", "Sword Passive"),
        ("shield", "Shield Passive"),
        ("control", "Control Passive"),
        ("summon", "Summon Passive"),
    )

    for archetype, title in minor_meta:
        tier = knight_minor_tier(state, archetype)
        equipped_item_id = next(
            (
                item_id
                for item_id in state.equipped.values()
                if item_id is not None and item_id in MINOR_ARCHETYPE_ITEMS[archetype]
            ),
            None,
        )
        description = ""
        subtitle = "No classified organ"
        if equipped_item_id is not None:
            summary = compact_minor_summary(equipped_item_id)
            item = EQUIPMENT_DEFS[equipped_item_id]
            subtitle = item.minor_name or item.name
            description = summary or item.minor_description or ""
        cards.append(
            PassiveCardSummary(
                key=archetype,
                title=title,
                subtitle=subtitle,
                description=description,
                tier_label=SET_TIER_LABELS.get(tier, "T0"),
                item_id=equipped_item_id,
                visible=equipped_item_id is not None,
            )
        )

    return cards


def short_slot_label(slot: str) -> str:
    return SLOT_LABELS[slot]


@dataclass
class EquipmentState:
    equipped: dict[str, str | None] = field(default_factory=lambda: {slot: None for slot in SLOT_ORDER})

    def has_item(self, item_id: str) -> bool:
        return item_id in self.equipped.values()

    def auto_equip(self, item_id: str) -> tuple[bool, str]:
        if item_id not in EQUIPMENT_DEFS:
            return False, "Unknown equipment"
        if self.has_item(item_id):
            return False, f"{EQUIPMENT_DEFS[item_id].name} already connected"

        definition = EQUIPMENT_DEFS[item_id]
        if self.equipped[definition.slot] is not None:
            return False, f"{SLOT_LABELS[definition.slot]} already occupied"

        self.equipped[definition.slot] = item_id
        return True, f"Equipped {definition.name}"

    def swap_with_ground(self, item_id: str) -> tuple[bool, str, str | None]:
        if item_id not in EQUIPMENT_DEFS:
            return False, "Unknown equipment", None

        definition = EQUIPMENT_DEFS[item_id]
        equipped_id = self.equipped[definition.slot]

        if equipped_id == item_id:
            return False, f"{definition.name} already equipped", None

        self.equipped[definition.slot] = item_id
        if equipped_id is None:
            return True, f"Equipped {definition.name}", None

        old_item = EQUIPMENT_DEFS[equipped_id]
        return True, f"Swapped {old_item.name} for {definition.name}", equipped_id


EQUIPMENT_DEFS: dict[str, EquipmentDefinition] = {
    "knight_heart": EquipmentDefinition(
        item_id="knight_heart",
        name="Knight Heart: Sacred Nail",
        slot="heart",
        series="knight",
        icon_color=(220, 86, 86),
        major_name="Armor Communion",
        major_description="Q triggers Paladin Fusion. At T4, fusion prevents death once and turns every hit into holy impact.",
    ),
    "knight_brain_sword": EquipmentDefinition(
        item_id="knight_brain_sword",
        name="Knight Brain: Oathblade",
        slot="brain",
        series="knight",
        icon_color=(226, 228, 235),
        major_name="Shield Rhythm",
        major_description="T1 unlocks block. Hits grant barrier rhythm, and every few strikes the sword brain forges a fresh shield around you.",
        minor_name="Blade March",
        minor_description="Movement speed rises while the sword is equipped.",
    ),
    "knight_brain_scripture": EquipmentDefinition(
        item_id="knight_brain_scripture",
        name="Knight Brain: War Scripture",
        slot="brain",
        series="knight",
        icon_color=(203, 177, 106),
        major_name="Sacred Cleansing",
        major_description="T1 unlocks block. When you are hit, the scripture purges stagger and restores combat posture.",
        minor_name="Restoration Rite",
        minor_description="Press R to quickly restore health and sanity.",
    ),
    "knight_left_eye_halo": EquipmentDefinition(
        item_id="knight_left_eye_halo",
        name="Left Eye: Sanctuary Halo",
        slot="left_eye",
        series="knight",
        icon_color=(255, 235, 164),
        major_name="Sanctuary Ring",
        major_description="U creates a halo that blocks enemies and attacks, while slowly healing.",
        minor_name="Soft Light",
        minor_description="Healing received improves.",
    ),
    "knight_left_eye_blade": EquipmentDefinition(
        item_id="knight_left_eye_blade",
        name="Left Eye: Light Blade",
        slot="left_eye",
        series="knight",
        icon_color=(165, 240, 255),
        major_name="Radiant Slash",
        major_description="U locks onto enemies in range and carves them with repeated light slashes.",
        minor_name="Edge Length",
        minor_description="Attack reach improves.",
    ),
    "knight_right_eye_rain": EquipmentDefinition(
        item_id="knight_right_eye_rain",
        name="Right Eye: Sword Rain",
        slot="right_eye",
        series="knight",
        icon_color=(190, 218, 255),
        major_name="Sky Spear Barrage",
        major_description="I calls down holy swords in a widening strike zone; at T4 they dive in like meteors from both sides.",
        minor_name="Battle Tempo",
        minor_description="Skill cooldowns shorten slightly.",
    ),
    "knight_right_eye_spirit": EquipmentDefinition(
        item_id="knight_right_eye_spirit",
        name="Right Eye: Knight Spirit",
        slot="right_eye",
        series="knight",
        icon_color=(171, 255, 214),
        major_name="Conversion Oath",
        major_description="I converts enemies in front into allies; at T4 it instead summons two bound elite knights at full health.",
        minor_name="Steadfast Gaze",
        minor_description="Parry stability improves slightly.",
    ),
}


def get_equipment(item_id: str) -> EquipmentDefinition:
    return EQUIPMENT_DEFS[item_id]


def knight_series_count(state: EquipmentState) -> int:
    return sum(1 for item_id in state.equipped.values() if item_id is not None and EQUIPMENT_DEFS[item_id].series == "knight")


def knight_tier(state: EquipmentState) -> int:
    if state.equipped["heart"] is None:
        return 0
    return min(4, knight_series_count(state))


def knight_size_bonus_percent(tier: int) -> int:
    return (0, 0, 20, 30, 40)[tier]


def knight_defense_bonus_percent(tier: int) -> int:
    return (0, 0, 20, 60, 100)[tier]


def knight_shield_hit_goal(tier: int) -> int:
    return (99, 15, 10, 8, 5)[tier]

def knight_stun_seconds(tier: int) -> float:
    return (0.0, 1.0, 2.0, 3.0, 4.0)[tier]


def knight_halo_radius_px(tier: int) -> float:
    return (0.0, 132.0, 156.0, 182.0, 210.0)[tier]


def knight_blade_reach_px(tier: int) -> float:
    return (0.0, 184.0, 228.0, 292.0, 420.0)[tier]


def knight_blade_height_px(tier: int) -> float:
    return (0.0, 68.0, 76.0, 84.0, 92.0)[tier]


def knight_blade_combo_hits(tier: int) -> int:
    return (0, 3, 4, 6, 10)[tier]


def knight_rain_forward_px(tier: int) -> float:
    return (0.0, 236.0, 276.0, 320.0, 0.0)[tier]


def knight_rain_spacing_px(tier: int) -> float:
    return (0.0, 84.0, 102.0, 122.0, 146.0)[tier]


def knight_rain_hit_width_px(tier: int) -> float:
    return (0.0, 66.0, 78.0, 94.0, 118.0)[tier]


def knight_rain_hit_height_px(tier: int) -> float:
    return (0.0, 118.0, 136.0, 156.0, 184.0)[tier]


def knight_rain_strike_count(tier: int) -> int:
    return (0, 5, 6, 8, 12)[tier]


def knight_spirit_range_px(tier: int) -> float:
    return (0.0, 220.0, 320.0, 460.0, 640.0)[tier]


def build_passive_summary(state: EquipmentState) -> PassiveSummary:
    heart_id = state.equipped["heart"]
    series = active_series(state)
    series_count = sum(1 for item_id in state.equipped.values() if item_id is not None and EQUIPMENT_DEFS[item_id].series == series)
    tier = min(4, series_count)
    set_tier = knight_tier(state)
    tier_label = SET_TIER_LABELS.get(set_tier, "T0")
    size_bonus = knight_size_bonus_percent(set_tier)
    defense_bonus = knight_defense_bonus_percent(set_tier)

    main_passive = "Equip a heart to define the active series"
    if heart_id is not None:
        heart = EQUIPMENT_DEFS[heart_id]
        main_passive = compact_major_summary(heart_id, set_tier)

    active = [f"Set {tier_label}: size +{size_bonus}%  |  defense +{defense_bonus}%"]
    inactive: list[str] = []

    for slot in SLOT_ORDER:
        item_id = state.equipped[slot]
        if item_id is None:
            continue
        item = EQUIPMENT_DEFS[item_id]
        minor_summary = compact_minor_summary(item_id)
        if minor_summary is not None:
            active.append(f"{item.minor_name}: {minor_summary}" if item.minor_name is not None else minor_summary)
        if slot == "heart":
            continue
        slot_tier = effective_tier_for_slot(state, slot)
        if major_is_active(state, slot):
            active.append(f"{item.major_name}: {compact_major_summary(item_id, max(1, slot_tier))}")
        else:
            inactive.append(f"{item.major_name}: dormant until heart matches")

    has_any_organs = any(item_id is not None for item_id in state.equipped.values())
    major_passive_card = build_major_passive_card(state) if has_any_organs else None
    minor_passive_cards = build_minor_passive_cards(state) if has_any_organs else []

    return PassiveSummary(
        main_passive=main_passive,
        active_passives=active,
        inactive_passives=inactive,
        series_label=SERIES_LABELS.get(series, series.title()),
        series_count=set_tier,
        tier_label=tier_label,
        major_passive_card=major_passive_card,
        minor_passive_cards=minor_passive_cards,
    )