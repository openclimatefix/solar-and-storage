""" Run a battery and solar site only simulation for one day"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from solar_and_storage.solar_and_storage import SolarAndStorage

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

solar_and_storage = SolarAndStorage(prices=prices, solar_generation=list(solar))
solar_and_storage.run_optimization()
result_df = solar_and_storage.get_results()

# run plot resutls
power = result_df["power"]
e_soc = result_df["e_soc"]
solar_power_to_grid = result_df["solar_power_to_grid"]

# plot
fig = make_subplots(rows=3, cols=1, subplot_titles=["Solar profile", "Price", "SOC"])
fig.add_trace(go.Scatter(y=e_soc[:24], name="SOC"), row=3, col=1)
fig.add_trace(go.Scatter(y=solar, name="solar", line_shape="hv"), row=1, col=1)
fig.add_trace(
    go.Scatter(y=solar_power_to_grid, name="solar to gird", line_shape="hv"), row=1, col=1
)
fig.add_trace(go.Scatter(y=prices, name="price", line_shape="hv"), row=2, col=1)


fig.show(rendered="browser")
