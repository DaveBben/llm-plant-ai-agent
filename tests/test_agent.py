import pytest
from unittest.mock import patch
from main import user_proxy, plant_agent


@pytest.mark.parametrize(
    "soil_moisture, should_water",
    [
        ("dry", True),  # Dry soil → Water needed
        ("moist", False),  # Moist soil → No watering
        ("wet", False),  # Wet soil → No watering
    ],
)
@patch("main.my_plant.get_moisture_level")
@patch("main.my_plant.water")
def test_agent_watering_flow(
    mock_water_plant, mock_get_moisture, soil_moisture, should_water
):
    """
    Test if the agent correctly decides to water the plant based on soil moisture.
    """

    # ARRANGE
    mock_get_moisture.return_value = soil_moisture

    # ACT
    res = user_proxy.initiate_chat(
        plant_agent,
        message="Does my plant need water?",
        cache=None,
        max_turns=10,
        summary_method="last_msg",
    )

    # ASSERT
    # Verify `get_moisture_level()` was called
    assert (
        mock_get_moisture.call_count >= 1
    ), "Expected `my_plant.get_moisture_level()` to be called at least once."

    # Check if agent decided to water the plant
    if should_water:
        assert (
            mock_water_plant.call_count >= 1
        ), f"For soil='{soil_moisture}', expected watering!"
    else:
        assert (
            mock_water_plant.call_count == 0
        ), f"For soil='{soil_moisture}', did NOT expect watering!"
