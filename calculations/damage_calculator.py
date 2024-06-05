from calculations.dataclasses_and_enums import Enemycounters, SamuroCounters, OneTalents, SevenTalents, SixteenTalents


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
    if level < 0 or level > 30:
        raise ValueError("level must be a valid hots level between 0 and 30.")
    if (one_talent != OneTalents.NONE) and level == 0:
        raise ValueError("Cannot have Way of Illusion or Way of the Blade active at level 0.")
    if (seven_talent != SevenTalents.NONE) and level < 7:
        raise ValueError("Cannot have a level 7 talent without being at least level 7.")
    if (sixteen_talent != SixteenTalents.NONE) and level < 16:
        raise ValueError("Cannot have a level 16 talent without being at least level 16.")
    if num_clones < 0 or num_clones > 2:
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
    # Critical Strike
    critModifier = 1.5
    base_w_cd = 10

    # Crushing Blows
    cbModifier = 0.1

    # Burning Blade
    bb_damage = 0.5 * counters.aa_damage

    if not counters.clone:
        if w_triggered:
            counters.remaining_w_cd = base_w_cd

        # Account for crushing blows' damage increase. CB applies to the auto attack that triggers it.
        if seven_talent == SevenTalents.CRUSHINGBLOWS:
            if counters.cb_counter < 3:
                counters.cb_counter += 1
                counters.aa_damage = precb_aa_damage * (1 + (cbModifier * counters.cb_counter))
                counters.crit_damage = precb_aa_damage * (critModifier + (cbModifier * counters.cb_counter))

        # Account for phantom pain.
        if seven_talent == SevenTalents.PHANTOMPAIN:
            counters.crit_damage = counters.aa_damage * (critModifier + (0.35 * num_clones))

    counters.crit_counter = 0
    summed_damage += counters.crit_damage + (counters.crit_damage * 0.05 * enemy_counters.wotb_stacks)
    if one_talent == OneTalents.WAYOFTHEBLADE and enemy_counters.wotb_stacks < 3:
        enemy_counters.wotb_stacks += 1

    # Burning blade is a separate damage instance as to not benefit from wotb (physical vs spell)
    if seven_talent == SevenTalents.BURNINGBLADE:
        summed_damage += bb_damage

    if w_triggered:
        print(summed_damage, "CRIT", "-W", counters.clone)
    else:
        print(summed_damage, "CRIT", counters.clone)
    return summed_damage


def apply_attack(
    summed_damage: float,
    counters: SamuroCounters,
    enemy_counters: Enemycounters,
    sixteen_talent: SixteenTalents,
) -> float:
    """Applies a normal attack and returns the result."""

    counters.crit_counter += 1
    summed_damage += counters.aa_damage + (counters.aa_damage * 0.05 * enemy_counters.wotb_stacks)
    print(summed_damage, "AA", counters.clone)
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
    counters = SamuroCounters(
        aa_damage=aa_damage * (1.04**level),
        crit_damage=aa_damage * (1.04**level) * 1.5,
        crit_counter=crit_threshold,
        aa_speed=aa_speed,
        attack_cadence=attack_cadence,
    )
    enemy_counters = Enemycounters()
    if one_talent == OneTalents.WAYOFILLUSION:
        counters.aa_damage += woi_damage_increase
        counters.crit_damage = counters.aa_damage * crit_modifier

    # For CB to not calculate badly, we preserve the original damage number.
    precb_aa_damage = counters.aa_damage

    # Set up our clones
    clones = [counters.create_clone(level) for _ in range(num_clones_attacking)]
    bodies = clones + [counters]  # Samuro should be the last body to attack for WoTB math.

    # Main Loop
    while passed_time < total_time:

        # Time passes
        counters.remaining_w_cd -= counters.attack_cadence
        times.append(passed_time)

        # Apply our damage - either a crit or an AA
        for body in bodies:
            if body.crit_counter == crit_threshold:
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
            counters.remaining_w_cd -= 2

        # Check if we can use W before we run out of time
        if (passed_time + aa_reset_time) > total_time:
            break

        # Apply W if we can and AA reset attack
        if counters.remaining_w_cd <= 0 and counters.crit_counter != crit_threshold:
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

            passed_time += aa_reset_time
            times.append(passed_time)

            if seven_talent == SevenTalents.CRUSHINGBLOWS:
                counters.remaining_w_cd -= 2

        # Increment time
        passed_time += counters.attack_cadence

    return times, damages
