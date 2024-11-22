""" Run a battery only simulation for one day """

import numpy as np

from solar_and_storage.solar_and_storage import SolarAndStorage
from solar_and_storage.example import prices, no_solar

HTML_OUTPUT = "" # set path or empty will skip writing HTML
PNG_OUTPUT = "examples/images/battery_only.png" # empty will skip writing PNG

# use example prices and no generation profile
solar_and_storage = SolarAndStorage(prices=prices, solar_generation=list(no_solar))
result_df = solar_and_storage.get_results()

# data is available for direct access
power = result_df["power"]
e_soc = result_df["e_soc"]
solar_power_to_grid = result_df["solar_power_to_grid"]
profit = result_df["profit"]

# plot
fig = solar_and_storage.get_figure()

fig.show(rendered="browser")
if HTML_OUTPUT:
    fig.write_html(HTML_OUTPUT)
if PNG_OUTPUT:
    fig.write_image(PNG_OUTPUT, format="png")
print(result_df.attrs["message"])
total_profit = solar_and_storage.get_total_profit()
print(f'total profit: {total_profit}')
