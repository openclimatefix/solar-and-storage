"""Run a battery simulation that starts with stored energy."""

import numpy as np

from solar_and_storage.solar_and_storage import SolarAndStorage

PNG_OUTPUT = "examples/images/current_soc.png"

prices = np.zeros(24)
prices[0] = 100
solar = np.zeros(24)

solar_and_storage = SolarAndStorage(
    prices=prices,
    solar_generation=list(solar),
    current_soc=0.5,
    battery_eta_charge=1,
    battery_eta_discharge=1,
)
result_df = solar_and_storage.get_results()

fig = solar_and_storage.get_figure()
fig.write_image(PNG_OUTPUT, format="png")

print(result_df.head(3))
print(f"total profit: {solar_and_storage.get_total_profit()}")
