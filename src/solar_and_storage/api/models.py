"""Pydantic models for FastAPI request/response validation."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from solar_and_storage.solar_and_storage import HOURS_PER_DAY


class OptimizationRequest(BaseModel):
    """Request model for battery optimization.

    Attributes:
        prices: List of 24 hourly electricity prices.
        solar_generation: List of 24 hourly solar generation values.
        battery_soc_min: Minimum battery state of charge (0-1).
        battery_soc_max: Maximum battery state of charge (0-1).
        battery_capacity: Battery capacity in kWh.
        power_rating: Battery power rating in kW.
        battery_eta_discharge: Battery discharge efficiency (0-1).
        battery_eta_charge: Battery charge efficiency (0-1).
        grid_connection_capacity: Maximum power to grid in kW.
        current_soc: Initial battery state of charge (0-1).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prices": [30, 30, 30, 30, 30, 30, 40, 40, 40, 50, 40, 40, 30, 30, 40, 40, 50, 60, 40, 30, 30, 30, 30, 30],  # noqa: E501
                "solar_generation": [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 4, 4, 4, 4, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0],  # noqa: E501
            },
        },
    )

    prices: list[float] = Field(
        ...,
        title="Electricity Prices",
        description="List of 24 hourly electricity prices for the day",
    )
    solar_generation: list[float] = Field(
        ...,
        title="Solar Generation",
        description="List of 24 hourly solar generation values in kW for the day",
    )
    battery_soc_min: float = Field(
        default=0,
        ge=0,
        le=1,
        title="Minimum SOC",
        description="Minimum battery state of charge as fraction (0.0 = empty, 1.0 = full)",
    )
    battery_soc_max: float = Field(
        default=1,
        ge=0,
        le=1,
        title="Maximum SOC",
        description="Maximum battery state of charge as fraction (0.0 = empty, 1.0 = full)",
    )
    battery_capacity: float = Field(
        default=1,
        gt=0,
        title="Battery Capacity",
        description="Total energy storage capacity of the battery in kWh",
    )
    power_rating: float = Field(
        default=1,
        gt=0,
        title="Power Rating",
        description="Maximum charge/discharge power of the battery in kW",
    )
    battery_eta_discharge: float = Field(
        default=0.95,
        gt=0,
        le=1,
        title="Discharge Efficiency",
        description="Round-trip efficiency when discharging (0.95 = 95% efficient)",
    )
    battery_eta_charge: float = Field(
        default=0.95,
        gt=0,
        le=1,
        title="Charge Efficiency",
        description="Round-trip efficiency when charging (0.95 = 95% efficient)",
    )
    grid_connection_capacity: float = Field(
        default=4,
        gt=0,
        title="Grid Connection Capacity",
        description="Maximum power that can be exported to the grid in kW",
    )
    current_soc: float = Field(
        default=0,
        ge=0,
        le=1,
        title="Initial SOC",
        description="Starting battery state of charge as fraction (0.0 = empty, 1.0 = full)",
    )

    @field_validator("prices", "solar_generation")
    @classmethod
    def validate_list_length(cls, v: list[float]) -> list[float]:
        """Validate that lists have exactly one item per hour of the day.

        Args:
            v: The list to validate.

        Returns:
            The validated list.

        Raises:
            ValueError: If list length is not HOURS_PER_DAY.
        """
        if len(v) != HOURS_PER_DAY:
            raise ValueError(f"List must have exactly {HOURS_PER_DAY} items, got {len(v)}")
        return v

    @model_validator(mode="after")
    def validate_soc_bounds(self) -> Self:
        """Validate that the SOC bounds are ordered and contain the starting SOC.

        Either violation would otherwise reach the solver as an infeasible problem.

        Returns:
            The validated request.

        Raises:
            ValueError: If battery_soc_min exceeds battery_soc_max, or current_soc lies
                outside the [battery_soc_min, battery_soc_max] range.
        """
        if self.battery_soc_min > self.battery_soc_max:
            raise ValueError(
                f"battery_soc_min ({self.battery_soc_min}) must not exceed "
                f"battery_soc_max ({self.battery_soc_max})",
            )
        if not self.battery_soc_min <= self.current_soc <= self.battery_soc_max:
            raise ValueError(
                f"current_soc ({self.current_soc}) must lie between battery_soc_min "
                f"({self.battery_soc_min}) and battery_soc_max ({self.battery_soc_max})",
            )
        return self


class ScheduleItem(BaseModel):
    """Single timestep in the optimization schedule.

    Attributes:
        hour: Hour index (0-23).
        power: Battery power from the grid (positive=charge, negative=discharge) in kW.
        battery_soc: Battery state of charge in kWh at the start of the hour.
        solar_power_to_grid: Solar power exported to grid in kW.
        profit: Battery profit for this hour, solar revenue not included.
    """

    hour: int = Field(
        ...,
        ge=0,
        le=HOURS_PER_DAY - 1,
        title="Hour",
        description="Hour of the day (0-23)",
    )
    power: float = Field(
        ...,
        title="Battery Power",
        description=(
            "Battery power exchanged with the grid in kW (positive = charging from the grid, "
            "negative = discharging). Charging from solar is not included."
        ),
    )
    battery_soc: float = Field(
        ...,
        title="Battery State of Charge",
        description="Battery energy level in kWh at the start of this hour",
    )
    solar_power_to_grid: float = Field(
        ...,
        title="Solar to Grid",
        description="Solar power exported to grid in kW (after battery charging)",
    )
    profit: float = Field(
        ...,
        title="Profit",
        description=(
            "Battery profit for this hour: price * (discharge - charge). "
            "Solar revenue is not included."
        ),
    )


class OptimizationResponse(BaseModel):
    """Response model for battery optimization.

    Attributes:
        status: Optimization status (optimal/infeasible/unbounded/error).
        message: Human-readable message about the result.
        total_profit: Total profit from optimization (null if not optimal).
        schedule: Hourly optimization schedule (null if not optimal).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "optimal",
                "message": "Optimization successful",
                "total_profit": 72.92,
                "schedule": [
                    {
                        "hour": 5,
                        "power": 1.0,
                        "battery_soc": 0.05,
                        "solar_power_to_grid": 0.0,
                        "profit": -30.0,
                    },
                    {
                        "hour": 9,
                        "power": -0.95,
                        "battery_soc": 1.0,
                        "solar_power_to_grid": 2.0,
                        "profit": 47.5,
                    },
                ],
            },
        },
    )

    status: Literal["optimal", "infeasible", "unbounded", "error"] = Field(
        ...,
        title="Status",
        description="Optimization result: 'optimal' (success), 'infeasible' (no solution), 'unbounded', or 'error'",  # noqa: E501
    )
    message: str = Field(
        ...,
        title="Message",
        description="Human-readable description of the optimization result",
    )
    total_profit: float | None = Field(
        default=None,
        title="Total Profit",
        description=(
            "Sum of the hourly battery profits, solar revenue not included "
            "(null if optimization failed)"
        ),
    )
    schedule: list[ScheduleItem] | None = Field(
        default=None,
        title="Schedule",
        description="Hour-by-hour optimization results for the 24-hour period (null if optimization failed)",  # noqa: E501
    )
