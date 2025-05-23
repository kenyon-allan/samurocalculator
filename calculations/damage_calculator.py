from calculations.dataclasses_and_enums import Enemycounters, SamuroCounters, OneTalents, SevenTalents, SixteenTalents
from calculations.global_values import (
    AA_RESET_TIME,
    BASE_W_CD,
    BURNING_BLADE_MODIFIER,
    CRIT_MULTIPLIER,
    CRUSHING_BLOWS_MAX_STACKS,
    CRUSHING_BLOWS_MODIFIER,
    CRUSHING_BLOWS_W_REDUCTION,
    DEFAULT_LEVEL_SCALING,
    MAXIMUM_CLONE_COUNT,
    MAXIMUM_LEVEL,
    PTA_MAX_STACKS,
    PTA_STACK_SCALING,
    SAM_BASE_AA_SPEED,
    SAM_BASE_ATTACK_CADENCE,
    SAM_BASE_DAMAGE_0,
    WAY_OF_ILLUSION_DAMAGE_BONUS,
    WOTB_ARMOR_REDUCTION,
    WOTB_MAX_STACKS,
)


def raise_for_invalid_inputs(
    one_talent: OneTalents,
    seven_talent: SevenTalents,
    sixteen_talent: SixteenTalents,
    level: int,
    total_time: int,
    num_clones: int,
    num_clones_attacking: int,
) -> None:
    """Raises for invalid inputs."""
    if total_time < 0:
        raise ValueError("total_time must be a non-negative number")
    if level < 0 or level > MAXIMUM_LEVEL:
        raise ValueError("level must be a valid hots level between 0 and 30.")
    if (one_talent != OneTalents.NONE) and level == 0:
        raise ValueError("Cannot have Way of Illusion or Way of the Blade active at level 0.")
    if (seven_talent != SevenTalents.NONE) and level < 7:
        raise ValueError("Cannot have a level 7 talent without being at least level 7.")
    if (sixteen_talent != SixteenTalents.NONE) and level < 16:
        raise ValueError("Cannot have a level 16 talent without being at least level 16.")
    if num_clones < 0 or num_clones > MAXIMUM_CLONE_COUNT:
        raise ValueError("Invalid number of clones. Must be 0, 1, or 2")
    if num_clones_attacking > num_clones:
        raise ValueError("Cannot have more clones attacking than you have clones.")


def apply_crit(
    summed_damage: float,
    precb_aa_damage: float,
    counters: SamuroCounters,
    enemy_counters: Enemycounters,
    one_talent: OneTalents,
    seven_talent: SevenTalents,
    sixteen_talent: SixteenTalents,
    num_clones: int = 0,
    w_triggered: bool = False,
) -> float:
    """Applies a critical strike and returns the result."""

    # Burning Blade
    bb_damage = BURNING_BLADE_MODIFIER * counters.aa_damage

    if not counters.clone:
        if w_triggered:
            counters.remaining_w_cd = BASE_W_CD

        # Account for crushing blows' damage increase.
        if seven_talent == SevenTalents.CRUSHINGBLOWS:
            if counters.cb_counter < CRUSHING_BLOWS_MAX_STACKS:
                counters.cb_counter += 1

        # Account for phantom pain.
        if seven_talent == SevenTalents.PHANTOMPAIN:
            counters.crit_damage = counters.aa_damage * (CRIT_MULTIPLIER + (0.35 * num_clones))

    counters.crit_counter = 0
    summed_damage += counters.crit_damage + (counters.crit_damage * 0.05 * enemy_counters.wotb_stacks)

    # CB no longer applies to the auto attack that triggers it.
    if not counters.clone and seven_talent == SevenTalents.CRUSHINGBLOWS:
        counters.aa_damage = precb_aa_damage * (1 + (CRUSHING_BLOWS_MODIFIER * counters.cb_counter))
        counters.crit_damage = precb_aa_damage * (CRIT_MULTIPLIER + (CRUSHING_BLOWS_MODIFIER * counters.cb_counter))

    if one_talent == OneTalents.WAYOFTHEBLADE and enemy_counters.wotb_stacks < WOTB_MAX_STACKS:
        enemy_counters.wotb_stacks += 1

    # Burning blade is a separate damage instance as to not benefit from wotb (physical vs spell)
    if seven_talent == SevenTalents.BURNINGBLADE:
        summed_damage += bb_damage

    if sixteen_talent == SixteenTalents.PRESSTHEATTACK and counters.pta_count < PTA_MAX_STACKS:
        counters.pta_count += 1

    if w_triggered:
        print(summed_damage, "CRIT", "-W", "clone" if counters.clone else "samuro")
    else:
        print(summed_damage, "CRIT", "clone" if counters.clone else "samuro")
    return summed_damage


def apply_attack(
    summed_damage: float,
    counters: SamuroCounters,
    enemy_counters: Enemycounters,
    sixteen_talent: SixteenTalents,
) -> float:
    """Applies a normal attack and returns the result."""

    counters.crit_counter += 1
    summed_damage += counters.aa_damage + (counters.aa_damage * WOTB_ARMOR_REDUCTION * enemy_counters.wotb_stacks)
    if sixteen_talent == SixteenTalents.PRESSTHEATTACK and counters.pta_count < PTA_MAX_STACKS:
        counters.pta_count += 1
    print(summed_damage, "AA", "clone" if counters.clone else "samuro")
    return summed_damage


def damage_calc(
    level: int,
    total_time: int,
    num_clones: int = 0,
    num_clones_attacking: int = 0,
    one_talent: OneTalents = OneTalents.NONE,
    seven_talent: SevenTalents = SevenTalents.NONE,
    sixteen_talent: SixteenTalents = SixteenTalents.NONE,
) -> tuple[list[float], list[float]]:
    """Calculates a list of times and damage values for a given length of time"""

    # check for invalid inputs
    raise_for_invalid_inputs(
        one_talent, seven_talent, sixteen_talent, level, total_time, num_clones, num_clones_attacking
    )

    # Setup our Looping Variables
    passed_time = 0  # total time passed in the simulation
    summed_damage = 0  # total damage dealt
    crit_threshold = 2 if one_talent == OneTalents.WAYOFTHEBLADE else 3  # crit every 3rd attack with WOTB
    times = []  # Array of timestamps
    damages = []  # assume pre-loaded crit, array of damages

    # Initialize our counters
    # Recalculate our AA and Crit Damage based on talents and level
    samuro = SamuroCounters.basic_initialize(level, crit_threshold)
    enemy_counters = Enemycounters()
    if one_talent == OneTalents.WAYOFILLUSION:
        samuro.aa_damage += WAY_OF_ILLUSION_DAMAGE_BONUS
        samuro.crit_damage = samuro.aa_damage * CRIT_MULTIPLIER

    # For CB to not calculate badly, we preserve the original damage number.
    precb_aa_damage = samuro.aa_damage

    # Set up our clones
    bodies = [samuro.create_clone(level) for _ in range(num_clones_attacking)]
    bodies.append(samuro)  # Samuro should be the last body to attack for WoTB math.

    # Main Loop
    while passed_time < total_time:

        # Time passes
        samuro.remaining_w_cd -= samuro.attack_cadence
        times.append(passed_time)

        # Apply our damage - either a crit or an AA
        for body in bodies:
            if body.crit_counter == crit_threshold or sixteen_talent == SixteenTalents.MERCILESS:
                summed_damage = apply_crit(
                    summed_damage,
                    precb_aa_damage,
                    body,
                    enemy_counters,
                    one_talent,
                    seven_talent,
                    sixteen_talent,
                    num_clones,
                )
            else:
                summed_damage = apply_attack(summed_damage, body, enemy_counters, sixteen_talent)
        damages.append(summed_damage)

        if seven_talent == SevenTalents.CRUSHINGBLOWS:
            samuro.remaining_w_cd -= CRUSHING_BLOWS_W_REDUCTION

        # Check if we can use W before we run out of time
        if (passed_time + AA_RESET_TIME) > total_time:
            break

        # Apply W if we can and AA reset attack
        if samuro.remaining_w_cd <= 0 and samuro.crit_counter != crit_threshold:
            for body in bodies:
                summed_damage = apply_crit(
                    summed_damage,
                    precb_aa_damage,
                    body,
                    enemy_counters,
                    one_talent,
                    seven_talent,
                    sixteen_talent,
                    num_clones,
                    True,
                )
            damages.append(summed_damage)

            passed_time += AA_RESET_TIME
            times.append(passed_time)

            # Apply PTA Stacks
            if sixteen_talent == SixteenTalents.PRESSTHEATTACK:
                for body in bodies:
                    body.aa_speed = body.base_aa_speed * (1 + (PTA_STACK_SCALING * body.pta_count))
                    body.attack_cadence = 1 / body.aa_speed

            if seven_talent == SevenTalents.CRUSHINGBLOWS:
                samuro.remaining_w_cd -= CRUSHING_BLOWS_W_REDUCTION

        # Increment time
        passed_time += samuro.attack_cadence

        # Apply PTA Stacks
        if sixteen_talent == SixteenTalents.PRESSTHEATTACK:
            for body in bodies:
                body.aa_speed = body.base_aa_speed * (1 + (PTA_STACK_SCALING * body.pta_count))
                body.attack_cadence = 1 / body.aa_speed

    return times, damages


def damage_calc_for_target_damage(
    level: int,
    target_damage: int,
    num_clones: int = 0,
    num_clones_attacking: int = 0,
    one_talent: OneTalents = OneTalents.NONE,
    seven_talent: SevenTalents = SevenTalents.NONE,
    sixteen_talent: SixteenTalents = SixteenTalents.NONE,
) -> tuple[list[float], list[float]]:
    """Calculates a list of times and damage values for a given length of time"""

    times, damages = damage_calc(
        level, 10000, num_clones, num_clones_attacking, one_talent, seven_talent, sixteen_talent
    )
    final_times = []
    final_damages = []
    for time, damage in zip(times, damages):
        if damage <= target_damage:
            final_times.append(time)
            final_damages.append(damage)
            continue
        # Go one over to guarantee kill
        else:
            if final_damages[len(final_damages) - 1] < target_damage:
                final_times.append(time)
                final_damages.append(damage)
            break
    return final_times, final_damages
