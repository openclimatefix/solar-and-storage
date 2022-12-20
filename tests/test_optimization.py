import numpy as np

from solar_and_storage.solar_and_storage import SolarAndStorage


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
