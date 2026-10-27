import numpy as np
import pytest

from solar_and_storage import SolarAndStorage
from solar_and_storage.solar_and_storage import SolarAndStorage as SolarAndStorageImpl


def test_package_exports_solar_and_storage():
    assert SolarAndStorage is SolarAndStorageImpl


def test_solar_and_storage():

    hours_per_day = 24

    # make prices
    prices = np.zeros(hours_per_day) + 30
    prices[6:19] = 40
    prices[9] = 50
    prices[12:14] = 30
    prices[16:18] = 50
    prices[17] = 60

    # make solar profile
    solar = np.zeros(hours_per_day)
    solar[8:16] = 2.0
    solar[10:14] = 4.0

    solar_and_storage = SolarAndStorage(prices=prices, solar_generation=solar)
    solar_and_storage.run_optimization()
    result_df = solar_and_storage.get_results()

    # run plot resutls
    e_soc = result_df["e_soc"]
    solar_power_to_grid = result_df["solar_power_to_grid"]

    # assert
    assert e_soc[6] == 1
    assert e_soc[10] == 0

    # charge from solar
    assert e_soc[13] == 0
    assert solar_power_to_grid[13] == 3
    assert e_soc[14] == 1
    assert solar_power_to_grid[14] == 2
    assert e_soc[18] == 0

    # TODO add more checks and scenarios


def test_current_soc_sets_initial_battery_state():
    hours_per_day = 24

    prices = np.zeros(hours_per_day)
    prices[0] = 100
    solar = np.zeros(hours_per_day)

    solar_and_storage = SolarAndStorage(
        prices=prices,
        solar_generation=solar,
        current_soc=0.5,
        battery_eta_charge=1,
        battery_eta_discharge=1,
    )

    result_df = solar_and_storage.get_results()

    assert result_df.attrs["status"] == "optimal"
    assert result_df["e_soc"][0] == 0.5
    assert result_df["power"][0] == 0.5
    assert result_df["e_soc"][1] == 0
    assert solar_and_storage.get_total_profit() == 50


def test_quarter_hour_block_scales_battery_energy_and_profit():
    solar_and_storage = SolarAndStorage(
        prices=[0, 100],
        solar_generation=[1, 0],
        battery_eta_charge=1.0,
        battery_eta_discharge=0.92,
        block_duration_mins=15,
    )

    result_df = solar_and_storage.get_results()

    assert result_df.attrs["status"] == "optimal"
    assert result_df["e_soc"][0] == 0
    assert result_df["power"][0] == -1
    assert result_df["e_soc"][1] == 0.25
    assert result_df["power"][1] == 0.92
    assert solar_and_storage.get_total_profit() == 23


def test_block_duration_must_be_positive_and_finite():
    for block_duration_mins in (0, -15, np.inf, np.nan):
        with pytest.raises(
            ValueError,
            match="block_duration_mins must be a positive finite number",
        ):
            SolarAndStorage(
                prices=[0],
                solar_generation=[0],
                block_duration_mins=block_duration_mins,
            )


def test_optimization_uses_input_profile_length():
    hours = 25
    solar_and_storage = SolarAndStorage(
        prices=np.zeros(hours),
        solar_generation=np.zeros(hours),
    )

    result_df = solar_and_storage.get_results()

    assert len(result_df) == hours
    assert len(solar_and_storage.get_figure().data[0].y) == hours
