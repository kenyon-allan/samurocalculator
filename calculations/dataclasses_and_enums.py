from enum import StrEnum
from dataclasses import dataclass
from typing import Self


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
    NONE = "None"


@dataclass
class SamuroCounters:
    """Mutable class to store counter information."""

    aa_damage: float
    crit_damage: float
    aa_speed: float
    attack_cadence: float
    remaining_w_cd: int = 0  # remaining W cooldown, defaults to 10 seconds
    crit_counter: int = 0  # counter for crits - we crit every 4th attack by default and every 3rd with WOTB
    cb_counter: int = 0  # Stacks of crushing blows. We start at 1 because we began with a preloaded crit.
    clone: bool = (
        False  # Clones don't benefit from crushing blows, and can't trigger w, so we need to explicitly track them.
    )

    def create_clone(self: Self, level: int) -> "SamuroCounters":
        """Simulates a clone of Samuro which has fractions of his damage, but maintain crit stacks."""
        clone_base_damage = 11  # clones suck wow.
        clone = SamuroCounters(
            aa_damage=clone_base_damage * (1.04**level),
            crit_damage=clone_base_damage * (1.04**level) * 1.5,
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
