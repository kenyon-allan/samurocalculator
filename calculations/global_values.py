"""Defines regularly accessed global values throughout the code."""

# Constraints
MAXIMUM_LEVEL = 30
MAXIMUM_CLONE_COUNT = 2
DEFAULT_LEVEL_SCALING = 1.04  # For most* heroes, they gain 4% AA damage per level.

# Samuro Damage Constants
CRIT_MULTIPLIER = 1.5  # Critical strikes do 1.5x Samuro's normal basic attack damage
BASE_W_CD = 10  # in seconds
CRUSHING_BLOWS_MODIFIER = 0.1  # Each stack of crushing blows increases Samuro's basic attack damage by 10%
BURNING_BLADE_MODIFIER = 0.5  # Burning blade deals an extra 50% of basic attack damage on crit.
AA_RESET_TIME = 3 / 16  # Seconds, approximately 3 game ticks where 1 tick is 1/16th of a second
WAY_OF_ILLUSION_DAMAGE_BONUS = 40  # Assuming quest complete.
PTA_STACK_SCALING = 0.1  # Each stack of press the attack increases attack speed by 10% up to 40%
WOTB_ARMOR_REDUCTION = 0.05  # Each stack of way of the blade reduces enemy armor by 5, up to 15.

# Samuro Level 0 Constants
SAM_BASE_DAMAGE_0 = 102.0
SAM_BASE_AA_SPEED = 1.67
SAM_BASE_ATTACK_CADENCE = 1 / SAM_BASE_AA_SPEED

# Samuro Constraints
WOTB_MAX_STACKS = 3
PTA_MAX_STACKS = 4
CRUSHING_BLOWS_MAX_STACKS = 3
