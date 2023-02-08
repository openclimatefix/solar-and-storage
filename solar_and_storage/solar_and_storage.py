""" File containing main solar and storage class """
from typing import List

import cvxpy as cp
import numpy as np
import pandas as pd

HOURS_PER_DAY = 24


class SolarAndStorage:
    """main solar and storage class"""

    def __init__(
        self,
        prices: List,
        solar_generation: List,
        battery_soc_min: float = 0,
        battery_soc_max: float = 1,
        battery_capacity: float = 1,
        power_rating: float = 1,
        battery_eta_discharge: float = 0.95,
        battery_eta_charge: float = 0.95,
        grid_connection_capacity: float = 4,
    ):
        """
        Set up class with various solar and battery parameters

        :param prices: list of prices
        :param solar_generation: list of solar generations
        :param battery_soc_min: the battery mininum soc
        :param battery_soc_max: the battery maximum soc
        :param battery_capacity: the capacity of the battery [KWh]
        :param power_rating: the power raying of the battery [KW]
        :param battery_eta_discharge: the efficiency of the battery discharge,
            should be between 0 and 1.
        :param battery_eta_charge: the efficiency of the battery charge,
            should be between 0 and 1.
        :param grid_connection_capacity: the amount of power that can be delivered to the grid
        """
        self.battery_soc_min = battery_soc_min
        self.battery_soc_max = battery_soc_max
        self.battery_capacity = battery_capacity
        self.power_rating = power_rating
        self.eta_charge = battery_eta_charge
        self.eta_discharge = battery_eta_discharge
        self.grid_connection_capacity = grid_connection_capacity

        # todo set these up as parameters
        self.solar_generation = solar_generation
        self.prices = prices

        # ## Setup Variables #####
        # the amount of power going into the battery
        self.battery_power_charge_cp_variable = cp.Variable(HOURS_PER_DAY)
        # the amount of power going out of the battery
        self.power_discharge_cp_variable = cp.Variable(HOURS_PER_DAY)
        # the battery soc level
        self.battery_soc_cp_variable = cp.Variable(HOURS_PER_DAY + 1)
        # if the battery is charging or discharging, cant be both
        self.charging_cp_variable = cp.Variable(
            HOURS_PER_DAY, boolean=True
        )  # variable to say if the battery charging or discharging
        # the amount of power flowing from the solar site to the battery
        self.power_solar_to_battery = cp.Variable(HOURS_PER_DAY)

        # ## Setup objectives #####
        prices_matrix = np.expand_dims(self.prices, 0)
        # Maximise the battery revenue
        objectives = prices_matrix @ (
            self.power_discharge_cp_variable - self.battery_power_charge_cp_variable
        )
        # Maximise the solar revenue
        objectives += prices_matrix @ (solar_generation - self.power_solar_to_battery)

        objective_function = cp.Maximize(objectives)

        # ## Setup contraints #####
        constraints = []
        constraints += [
            self.battery_soc_min * self.battery_capacity <= self.battery_soc_cp_variable,
            self.battery_soc_cp_variable <= self.battery_soc_max * self.battery_capacity,
        ]
        constraints += [
            0 <= self.battery_power_charge_cp_variable,
            self.battery_power_charge_cp_variable <= self.power_rating,
        ]
        constraints += [
            0 <= self.power_discharge_cp_variable,
            self.power_discharge_cp_variable <= self.power_rating,
        ]
        constraints += [self.battery_soc_cp_variable[0] == 0]

        for i in range(HOURS_PER_DAY):
            constraints += [0 <= self.battery_power_charge_cp_variable[i]]
            constraints += [
                self.battery_power_charge_cp_variable[i]
                <= self.power_rating * self.charging_cp_variable[i]
            ]
            constraints += [0 <= self.power_discharge_cp_variable[i]]
            constraints += [
                self.power_discharge_cp_variable[i]
                <= (1 - self.charging_cp_variable[i]) * self.power_rating
            ]

            # solar to battery
            constraints += [0 <= self.power_solar_to_battery[i]]
            constraints += [self.power_solar_to_battery[i] <= solar_generation[i]]
            constraints += [
                self.power_solar_to_battery[i] + self.battery_power_charge_cp_variable[i]
                <= self.power_rating * self.charging_cp_variable[i]
            ]

            # grid constraints
            constraints += [
                solar_generation[i] + self.power_discharge_cp_variable[i]
                <= self.grid_connection_capacity
            ]

            # battery soc
            power_charge = (
                self.eta_charge * self.battery_power_charge_cp_variable[i]
            ) + self.power_solar_to_battery[i]
            power_discharge = self.power_discharge_cp_variable[i] / self.eta_discharge
            constraints += [
                self.battery_soc_cp_variable[i + 1]
                == self.battery_soc_cp_variable[i] + power_charge - power_discharge
            ]

        self.constraints = constraints
        self.objective_function = objective_function

    def run_optimization(self):
        """
        Run optimization problem
        """

        # form the problem and solve.
        self.prob = cp.Problem(self.objective_function, self.constraints)

        # run optimization
        self.prob.solve(verbose=False, options={"glpk": {"msg_lev": "GLP_MSG_OFF"}})

    def get_results(self) -> pd.DataFrame:
        """Get optimization results (after running)"""
        # run plot resutls
        power = np.round(
            self.battery_power_charge_cp_variable.value - self.power_discharge_cp_variable.value, 2
        )
        e_soc = np.round(self.battery_soc_cp_variable.value, 2)
        profit = self.prices * (
            self.power_discharge_cp_variable.value - self.battery_power_charge_cp_variable.value
        )
        solar_power_to_grid = self.solar_generation - self.power_solar_to_battery.value

        data = np.array([power, e_soc[:HOURS_PER_DAY], solar_power_to_grid, profit]).transpose()

        return pd.DataFrame(
            data=data,
            columns=["power", "e_soc", "solar_power_to_grid", "profit"],
        )
