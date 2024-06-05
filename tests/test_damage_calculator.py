from calculations.damage_calculator import damage_calc
from calculations.dataclasses_and_enums import OneTalents, SevenTalents


def test_level_seven_woi_cb():
    """Test that our calcs for level 7 with Way of Illusion and Crushing Blows are good."""
    # Expected results:
    expected = {
        "damage_series": [
            278.76006637128916,
            574.9426368907839,
            784.0126866692507,
            993.0827364477175,
            1202.1527862261844,
            1515.7578608938848,
            1829.362935561585,
            2055.8554894882573,
            2282.3480434149296,
            2508.840597341602,
            2822.445672009302,
            3136.0507466770023,
            3362.5433006036747,
            3589.035854530347,
            3815.5284084570194,
            4129.1334831247195,
            4442.73855779242,
            4669.231111719092,
            4895.723665645764,
            5122.216219572437,
        ],
        "time_series": [
            0,
            0.1875,
            0.7863023952095809,
            1.3851047904191618,
            1.9839071856287427,
            2.5827095808383236,
            2.7702095808383236,
            3.3690119760479043,
            3.967814371257485,
            4.566616766467066,
            5.165419161676646,
            5.352919161676646,
            5.951721556886227,
            6.550523952095808,
            7.149326347305388,
            7.748128742514969,
            7.935628742514969,
            8.53443113772455,
            9.133233532934131,
            9.732035928143713,
        ],
    }
    # Actual results:
    time_series, damage_series = damage_calc(7, 10, OneTalents.WAYOFILLUSION, SevenTalents.CRUSHINGBLOWS)
    actual = {"damage_series": damage_series, "time_series": time_series}
    assert actual == expected
