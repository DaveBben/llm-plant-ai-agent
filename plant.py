from typing import Literal, Optional
from sensors import SoilSensor, MotorControl
import time
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Plant:
    """
    Represents a plant with a soil sensor and motor-based watering system.
    Responsible for tracking the plant's name/type,
    soil moisture, and last watering date.
    """

    def __init__(
        self,
        plant_name: str,
        plant_type: str,
        soil_sensor: SoilSensor,
        motor_controller: MotorControl,
    ):
        """
        Initialize the Plant instance.

        :param plant_name: A unique name to identify the plant.
        :param plant_type: The plant species/type (e.g., 'pothos', 'snake plant').
        :param soil_sensor: A SoilSensor object for reading moisture voltage.
        :param motor_controller: A MotorControl object for turning the water motor on/off.
        """
        self._plant_name = plant_name
        self._plant_type = plant_type
        self._soil_sensor = soil_sensor
        self._motor_crtl = motor_controller
        self._file_name = f"{self._plant_name}_water_data.txt"
        self._date_last_watered: Optional[datetime] = None

        self._load_last_watered()

    def _load_last_watered(self):
        """
        Load the date the plant was last watered from a file.
        """
        script_directory = Path(__file__).parent.resolve()
        water_file = Path(script_directory / self._file_name)
        if water_file.exists():
            try:
                with open(water_file, "r") as w_file:
                    watered_date = w_file.readline().strip()
                    self._date_last_watered = datetime.strptime(
                        watered_date, "%m/%d/%Y"
                    )
            except ValueError as e:
                logging.warning(f"Water file format error: {e}")

        else:
            logging.info(
                "Water file does not exist. This plant may never have been watered."
            )

    def _save_last_watered(self):
        """
        Save the date the plant was last watered to a file.
        """
        script_directory = Path(__file__).parent.resolve()
        water_file = Path(script_directory / self._file_name)
        if self._date_last_watered is not None:
            with open(water_file, "w") as w_file:
                w_file.write(self._date_last_watered.strftime("%m/%d/%Y"))

    @property
    def plant_type(self):
        """
        Return the type of the plant (e.g., 'pothos').
        """
        return self._plant_type

    @property
    def last_watered(self):
        """
        Return the string date when the plant was last watered, or 'NEVER' if unknown.
        """
        if self._date_last_watered is None:
            return "NEVER"
        else:
            return self._date_last_watered.strftime("%m/%d/%Y")

    @property
    def days_since_last_watered(self) -> int:
        """
        Return the number of days since the plant was last watered.
        Returns -1 if the plant has never been watered.
        """
        if self._date_last_watered is None:
            return -1
        return (datetime.now() - self._date_last_watered).days

    def water(self) -> None:
        """
        Activate the water motor, wait a few seconds, and then shut it off.
        Update the last-watered date and store it to disk.
        """
        logging.info("Starting watering process.")
        self._motor_crtl.turn_on()
        time.sleep(5)
        self._motor_crtl.turn_off()
        self._date_last_watered = datetime.now()
        self._save_last_watered()
        logging.info("Watering complete. Updated last watered date saved.")

    def get_moisture_level(self) -> Literal["WET", "DRY", "MOIST"]:
        """
        Return the moisture level based on sensor voltage.

        :returns: 'DRY', 'MOIST', or 'WET'
        :raises RuntimeError: If the reading is out of an expected range.
        """
        voltage = self._soil_sensor.get_voltage()
        # refer to notebook on how I got this linear calibration equation
        pred_meter = int((-8.3 * voltage) + 19.84)
        if pred_meter < 5:
            return "DRY"
        elif 5 <= pred_meter < 8:
            return "MOIST"
        elif pred_meter >= 8:
            return "WET"
        else:
            raise RuntimeError(f"Unexpected sensor value: {pred_meter}")
