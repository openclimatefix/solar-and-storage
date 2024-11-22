""" These are used in the /examples directory as well as (planned) tests """

import numpy as np

# examples use 24 hour day for analysis period
# any granularity should be supported but only 24 hour day has been tested
hours_per_day = 24

prices = np.zeros(hours_per_day) + 30
prices[6:19] = 40
prices[9] = 50
prices[12:14] = 30
prices[16:18] = 50
prices[17] = 60

no_solar = np.zeros(hours_per_day)

with_solar = np.zeros(hours_per_day)
with_solar[8:16] = 2.0
with_solar[10:14] = 4.0

solar_generation = {
    "no_solar": no_solar,
    "with_solar": with_solar,
}
