"""Example usage of the Solar and Storage API with Python requests library."""

import requests

# API base URL (change if server is running on a different host/port)
BASE_URL = "http://localhost:8000"


def main() -> None:
    """Demonstrate API usage with example optimization request."""
    # Example 1: Successful optimization
    print("=" * 60)
    print("Example 1: Successful Optimization")
    print("=" * 60)

    optimization_request = {
        "prices": [
            30, 30, 30, 30, 30, 30,  # Night (low prices)
            40, 40, 40,              # Morning
            50,                       # Peak morning
            40, 40,                   # Midday
            30, 30,                   # Afternoon dip
            40, 40,                   # Evening start
            50, 60,                   # Evening peak
            40,                       # Late evening
            30, 30, 30, 30, 30,      # Night (low prices)
        ],
        "solar_generation": [
            0, 0, 0, 0, 0, 0, 0, 0,  # Night (no solar)
            2, 2,                     # Morning sun
            4, 4, 4, 4,              # Midday peak
            2, 2,                     # Afternoon sun
            0, 0, 0, 0, 0, 0, 0, 0,  # Evening/night (no solar)
        ],
        # Optional parameters (using defaults here)
        "battery_capacity": 1.0,
        "power_rating": 1.0,
        "battery_eta_charge": 0.95,
        "battery_eta_discharge": 0.95,
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/optimize",
        json=optimization_request,
        timeout=10,
    )

    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Total Profit: {result['total_profit']:.2f}")
        print(f"\nFirst 5 hours of schedule:")
        for item in result["schedule"][:5]:
            print(f"  Hour {item['hour']}: "
                  f"Power={item['power']:.2f}kW, "
                  f"SOC={item['battery_soc']:.2f}kWh, "
                  f"Profit={item['profit']:.2f}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

    # Example 2: Validation error
    print("\n" + "=" * 60)
    print("Example 2: Validation Error (wrong list length)")
    print("=" * 60)

    invalid_request = {
        "prices": [30, 40, 50],  # Only 3 items (should be 24)
        "solar_generation": [0, 2, 4],  # Only 3 items (should be 24)
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/optimize",
        json=invalid_request,
        timeout=10,
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 422:
        print("Validation error (expected):")
        print(response.json())

    # Example 3: Infeasible optimization
    print("\n" + "=" * 60)
    print("Example 3: Infeasible Optimization")
    print("=" * 60)

    infeasible_request = {
        "prices": [50] * 24,
        "solar_generation": [0] * 24,
        "battery_soc_min": 0.8,  # Min SOC 80%
        "battery_soc_max": 0.2,  # Max SOC 20% (impossible!)
        "current_soc": 0.5,
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/optimize",
        json=infeasible_request,
        timeout=10,
    )

    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Total Profit: {result['total_profit']}")
        print(f"Schedule: {result['schedule']}")


if __name__ == "__main__":
    # First check if the server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("Server is healthy. Running examples...\n")
            main()
        else:
            print("Server is not responding correctly.")
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to server at {BASE_URL}")
        print("Please start the server with:")
        print("  uv run uvicorn solar_and_storage.api.main:app --reload")
