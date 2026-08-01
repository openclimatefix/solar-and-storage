"""API routers for solar-and-storage optimization endpoints."""

import logging

from fastapi import APIRouter, HTTPException

from solar_and_storage.api.models import (
    OptimizationRequest,
    OptimizationResponse,
    ScheduleItem,
)
from solar_and_storage.solar_and_storage import SolarAndStorage

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/optimize", response_model=OptimizationResponse)
def optimize(request: OptimizationRequest) -> OptimizationResponse:
    """Run battery optimization with given parameters.

    Args:
        request: Optimization request with prices, solar generation, and battery parameters.

    Returns:
        Optimization response with status, profit, and schedule.

    Raises:
        HTTPException: If an unexpected error occurs during optimization.
    """
    try:
        # Create SolarAndStorage instance with request parameters
        optimizer = SolarAndStorage(
            prices=request.prices,
            solar_generation=request.solar_generation,
            battery_soc_min=request.battery_soc_min,
            battery_soc_max=request.battery_soc_max,
            battery_capacity=request.battery_capacity,
            power_rating=request.power_rating,
            battery_eta_discharge=request.battery_eta_discharge,
            battery_eta_charge=request.battery_eta_charge,
            grid_connection_capacity=request.grid_connection_capacity,
            current_soc=request.current_soc,
        )

        # Run optimization
        results_df = optimizer.get_results()
        status = results_df.attrs["status"]
        message = results_df.attrs["message"]

        # Handle non-optimal status (not a client error, so return 200)
        if status != "optimal":
            logger.warning(f"Optimization failed with status: {status}")
            # Status from cvxpy can be "infeasible", "unbounded", etc.
            response_status = status if status in {"infeasible", "unbounded"} else "error"
            return OptimizationResponse(
                status=response_status,  # type: ignore[arg-type]
                message=message,
                total_profit=None,
                schedule=None,
            )

        # Convert DataFrame to schedule items
        schedule = [
            ScheduleItem(
                hour=i,
                power=float(results_df.iloc[i]["power"]),
                battery_soc=float(results_df.iloc[i]["e_soc"]),
                solar_power_to_grid=float(results_df.iloc[i]["solar_power_to_grid"]),
                profit=float(results_df.iloc[i]["profit"]),
            )
            for i in range(24)
        ]

        # Calculate total profit
        total_profit = float(optimizer.get_total_profit())

        return OptimizationResponse(
            status="optimal",
            message=message,
            total_profit=total_profit,
            schedule=schedule,
        )

    except Exception as e:
        logger.exception("Unexpected error during optimization")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {e!s}",
        ) from e
