""" Run a battery only simulation for one day """

import numpy as np

from solar_and_storage.solar_and_storage import SolarAndStorage

HTML_OUTPUT = "examples/battery_only.html"  # Change this to your desired path or leave as an empty string

hours_per_day = 24


# make prices
prices = np.zeros(hours_per_day) + 30
prices[6:19] = 40
prices[9] = 50
prices[12:14] = 30
prices[16:18] = 50
prices[17] = 60

# make zero solar profile
solar = np.zeros(hours_per_day)

solar_and_storage = SolarAndStorage(prices=prices, solar_generation=list(solar))
solar_and_storage.run_optimization()
result_df = solar_and_storage.get_results()

# data is available for direct access
power = result_df["power"]
e_soc = result_df["e_soc"]
solar_power_to_grid = result_df["solar_power_to_grid"]

# plot
fig = solar_and_storage.get_fig()

fig.show(rendered="browser")
if HTML_OUTPUT:
    fig.write_html(HTML_OUTPUT)
