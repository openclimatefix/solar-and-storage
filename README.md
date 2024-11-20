# Solar and Storage
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

A Python Library to run solar and storage optimization.
This uses mixed integer linear programming and maximises revenue made by charging and discharging the battery.
The model uses variable prices and a solar generation profile.

## Installation

```
pip install solar-and-storage
```


## Example

Import the packages
```python
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from solar_and_storage.solar_and_storage import SolarAndStorage

```
Make the fake price and solar data
```python
# make prices
prices = np.zeros(24) + 30
prices[6:19] = 40
prices[9] = 50
prices[12:14] = 30
prices[16:18] = 50
prices[17] = 60

# make solar profile
solar = np.zeros(24)
solar[8:16] = 2.0
solar[10:14] = 4.0
```

Then run optimization
```python
solar_and_storage = SolarAndStorage(prices=prices, solar_generation=list(solar))
solar_and_storage.run_optimization()
result_df = solar_and_storage.get_results()
```



Now plot the data
```python
fig = solar_and_storage.get_fig()

fig.show(rendered="browser")
```


![Example1](https://raw.githubusercontent.com/openclimatefix/solar-and-storage/main/examples/solar_and_storage.png)
The first plot shows the solar profile, the second shows the prices that day. The third shows the battery profile.
You can see that the battery charged from the solar site at the end of the solar maximum



## Thanks

Thanks you to the follow repos for inspiration
- https://github.com/ADGEfficiency/energy-py-linear
- https://github.com/wzyfrank/battery/
- https://github.com/greysonchung/Battery-Optimisation/
- https://github.com/edu230991/battery-optimization/
sdk-python-ci.yml

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/peterdudfield"><img src="https://avatars.githubusercontent.com/u/34686298?v=4?s=100" width="100px;" alt="Peter Dudfield"/><br /><sub><b>Peter Dudfield</b></sub></a><br /><a href="https://github.com/openclimatefix/solar-and-storage/commits?author=peterdudfield" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/gilbertgong"><img src="https://avatars.githubusercontent.com/u/5944694?v=4?s=100" width="100px;" alt="gilbertgong"/><br /><sub><b>gilbertgong</b></sub></a><br /><a href="https://github.com/openclimatefix/solar-and-storage/commits?author=gilbertgong" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!