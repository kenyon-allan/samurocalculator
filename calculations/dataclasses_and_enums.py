from enum import StrEnum
from dataclasses import dataclass
from typing import Self

from calculations.global_values import (
    CLONE_BASE_DAMAGE,
    CRIT_MULTIPLIER,
    DEFAULT_LEVEL_SCALING,
    SAM_BASE_AA_SPEED,
    SAM_BASE_ATTACK_CADENCE,
    SAM_BASE_DAMAGE_0,
)


class SevenTalents(StrEnum):
    """Level 7 talent options."""

    BURNINGBLADE = "Burning Blade"
    CRUSHINGBLOWS = "Crushing Blows"
    PHANTOMPAIN = "Phantom Pain"
    NONE = "None"


class OneTalents(StrEnum):
    """Level 1 talent options (That Matter)."""

    WAYOFILLUSION = "Way of Illusion"
    WAYOFTHEBLADE = "Way of the Blade"
    WAYOFTHEWIND = "Way of the Wind"
    NONE = "None"


class SixteenTalents(StrEnum):
    """Level 16 talent options."""

    MERCILESS = "Merciless Strikes"
    HARSHWINDS = "Harsh Winds"
    PRESSTHEATTACK = "Press the Attack"
    NONE = "None"


@dataclass
class SamuroCounters:
    """Mutable class to store counter information."""

    aa_damage: float
    crit_damage: float
    base_aa_speed: float
    aa_speed: float
    attack_cadence: float
    remaining_w_cd: int = 0  # remaining W cooldown, defaults to 10 seconds
    crit_counter: int = 0  # counter for crits - we crit every 4th attack by default and every 3rd with WOTB
    cb_counter: int = 0  # Stacks of crushing blows. We start at 1 because we began with a preloaded crit.
    pta_count: int = 0  # Stacks of Press the Attack.
    clone: bool = (
        False  # Clones don't benefit from crushing blows, and can't trigger w, so we need to explicitly track them.
    )

    @staticmethod
    def basic_initialize(level: int, crit_threshold: int) -> "SamuroCounters":
        """Performs a basic initialization for default values."""
        return SamuroCounters(
            aa_damage=SAM_BASE_DAMAGE_0 * (DEFAULT_LEVEL_SCALING**level),
            crit_damage=SAM_BASE_DAMAGE_0 * (DEFAULT_LEVEL_SCALING**level) * CRIT_MULTIPLIER,
            crit_counter=crit_threshold,  # We assume we start with a crit loaded for optimal damage.
            base_aa_speed=SAM_BASE_AA_SPEED,
            aa_speed=SAM_BASE_AA_SPEED,
            attack_cadence=SAM_BASE_ATTACK_CADENCE,
        )

    def create_clone(self: Self, level: int) -> "SamuroCounters":
        """Simulates a clone of Samuro which has fractions of his damage, but maintain crit stacks."""
        clone = SamuroCounters(
            aa_damage=CLONE_BASE_DAMAGE * (DEFAULT_LEVEL_SCALING**level),
            crit_damage=CLONE_BASE_DAMAGE * (DEFAULT_LEVEL_SCALING**level) * CRIT_MULTIPLIER,
            base_aa_speed=self.aa_speed,
            aa_speed=self.aa_speed,
            attack_cadence=self.attack_cadence,
            remaining_w_cd=0,
            crit_counter=self.crit_counter,
            cb_counter=0,
            clone=True,
        )
        return clone


@dataclass
class Enemycounters:
    """Mutable class to store information on the enemy."""

    wotb_stacks: int = 0  # Stacks of Way of the Blade's armor reduction active.
    harsh_winds_timer: float = 0  # Timer for Harsh Winds.
    ccd: bool = False  # Is the enemy currently crowd controlled? Needed for Merciless.
