from calculations.damage_calculator import damage_calc
from calculations.dataclasses_and_enums import OneTalents, SevenTalents, SixteenTalents


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
    time_series, damage_series = damage_calc(
        level=7,
        total_time=10,
        num_clones=0,
        num_clones_attacking=0,
        one_talent=OneTalents.WAYOFILLUSION,
        seven_talent=SevenTalents.CRUSHINGBLOWS,
        sixteen_talent=SixteenTalents.NONE,
    )
    actual = {"damage_series": damage_series, "time_series": time_series}
    assert actual == expected


def test_level_thirteen_woi_pp_one_clone():
    """Tests phantom pain."""

    expected = {
        "damage_series": [
            388.1993708294704,
            776.3987416589408,
            986.2362394046005,
            1196.07373715026,
            1405.9112348959197,
            1794.11060572539,
            2003.9481034710498,
            2213.7856012167094,
            2423.623098962369,
            2811.8224697918395,
            3021.659967537499,
            3231.497465283159,
            3441.3349630288185,
            3829.534333858289,
            4039.3718316039485,
            4249.209329349608,
            4459.046827095268,
            4847.246197924738,
        ],
        "time_series": [
            0,
            0.1875,
            0.7863023952095809,
            1.3851047904191618,
            1.9839071856287427,
            2.5827095808383236,
            3.1815119760479043,
            3.780314371257485,
            4.379116766467066,
            4.977919161676646,
            5.576721556886227,
            6.175523952095808,
            6.774326347305388,
            7.373128742514969,
            7.97193113772455,
            8.570733532934131,
            9.169535928143713,
            9.768338323353294,
        ],
    }
    time_series, damage_series = damage_calc(
        level=13,
        total_time=10,
        num_clones=1,
        num_clones_attacking=0,
        one_talent=OneTalents.WAYOFILLUSION,
        seven_talent=SevenTalents.PHANTOMPAIN,
        sixteen_talent=SixteenTalents.NONE,
    )
    actual = {"damage_series": damage_series, "time_series": time_series}
    assert actual == expected
