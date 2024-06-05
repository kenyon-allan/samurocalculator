from calculations.dataclasses_and_enums import Counters, OneTalents, SevenTalents


def raise_for_invalid_inputs(one_talent: OneTalents, seven_talent: SevenTalents, level: int, total_time: int) -> None:
    """Raises for invalid inputs."""
    if seven_talent == SevenTalents.PHANTOMPAIN:
        raise ValueError("cmon, really?")
    if total_time < 0:
        raise ValueError("total_time must be a non-negative number")
    if level < 0 or level > 30:
        raise ValueError("level must be a valid hots level between 0 and 30.")
    if (one_talent != OneTalents.NONE) and level == 0:
        raise ValueError("Cannot have Way of Illusion or Way of the Blade active at level 0.")
    if seven_talent != SevenTalents.NONE and level < 7:
        raise ValueError("Cannot have a level 7 talent without being at least level 7.")


def apply_crit(
    summed_damage: float,
    precb_aa_damage: float,
    counters: Counters,
    one_talent: OneTalents,
    seven_talent: SevenTalents,
    w_triggered: bool = False,
) -> float:
    """Applies a critical strike and returns the result."""
    # Critical Strike
    critModifier = 1.5
    base_w_cd = 10

    # Crushing Blows
    cbModifier = 0.1

    # Burning Blade
    bb_damage = 0.5 * counters.aa_damage

    if w_triggered:
        counters.remaining_w_cd = base_w_cd

    # Account for crushing blows' damage increase. CB applies to the auto attack that triggers it.
    if seven_talent == SevenTalents.CRUSHINGBLOWS:
        if counters.cb_counter < 3:
            counters.cb_counter += 1
            counters.aa_damage = precb_aa_damage * (1 + (cbModifier * counters.cb_counter))
            counters.crit_damage = precb_aa_damage * (critModifier + (cbModifier * counters.cb_counter))

    counters.crit_counter = 0
    summed_damage += counters.crit_damage + (counters.crit_damage * 0.05 * counters.wotb_stacks)
    if one_talent == OneTalents.WAYOFTHEBLADE and counters.wotb_stacks < 3:
        counters.wotb_stacks += 1
    if seven_talent == SevenTalents.BURNINGBLADE:
        summed_damage += bb_damage
    if w_triggered:
        print(summed_damage, "CRIT", "-W")
    else:
        print(summed_damage, "CRIT")
    return summed_damage


def damage_calc(
    level: int,
    total_time: int,
    one_talent: OneTalents = OneTalents.NONE,
    seven_talent: SevenTalents = SevenTalents.NONE,
) -> tuple[list[float], list[float]]:
    """Calculates a list of times and damage values for a given length of time"""

    # check for invalid inputs
    raise_for_invalid_inputs(one_talent, seven_talent, level, total_time)

    # # Globals
    aa_damage = 102.0  # level 0
    aa_speed = 1.67  # attacks per second
    attack_cadence = 1 / aa_speed  # seconds per attack
    aa_reset_time = 3 / 16  # seconds, approximately 3 game ticks.
    crit_modifier = 1.5

    # Way of Illusion
    woi_damage_increase = 40  # full stacks

    # Setup our Looping Variables
    passed_time = 0  # total time passed in the simulation
    summed_damage = 0  # total damage dealt
    crit_threshold = 2 if one_talent == OneTalents.WAYOFTHEBLADE else 3  # crit every 3rd attack with WOTB
    times = []  # Array of timestamps
    damages = []  # assume pre-loaded crit, array of damages

    # Initialize our counters
    # Recalculate our AA and Crit Damage based on talents and level
    counters = Counters(
        aa_damage=aa_damage * (1.04**level),
        crit_damage=aa_damage * (1.04**level) * 1.5,
        crit_counter=crit_threshold,
        aa_speed=aa_speed,
        attack_cadence=attack_cadence,
    )
    if one_talent == OneTalents.WAYOFILLUSION:
        counters.aa_damage += woi_damage_increase
        counters.crit_damage = counters.aa_damage * crit_modifier

    # We start with a pre-loaded crit, so CB will activate immediately.
    # For CB to not calculate badly, we preserve the original damage number.
    precb_aa_damage = counters.aa_damage

    # Main Loop
    while passed_time < total_time:

        # Time passes
        counters.remaining_w_cd -= counters.attack_cadence
        times.append(passed_time)

        # Apply our damage - either a crit or an AA
        if counters.crit_counter == crit_threshold:
            summed_damage = apply_crit(summed_damage, precb_aa_damage, counters, one_talent, seven_talent)
        else:
            counters.crit_counter += 1
            summed_damage += counters.aa_damage + (counters.aa_damage * 0.05 * counters.wotb_stacks)
            print(summed_damage, "AA")
        damages.append(summed_damage)

        if seven_talent == SevenTalents.CRUSHINGBLOWS:
            counters.remaining_w_cd -= 2

        # Check if we can use W before we run out of time
        if (passed_time + aa_reset_time) > total_time:
            break

        # Apply W if we can and AA reset attack
        if counters.remaining_w_cd <= 0 and counters.crit_counter != crit_threshold:
            summed_damage = apply_crit(summed_damage, precb_aa_damage, counters, one_talent, seven_talent, True)
            damages.append(summed_damage)

            passed_time += aa_reset_time
            times.append(passed_time)

            if seven_talent == SevenTalents.CRUSHINGBLOWS:
                counters.remaining_w_cd -= 2

        # Increment time
        passed_time += counters.attack_cadence

    return times, damages
