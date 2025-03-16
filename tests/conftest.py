import sys
from unittest.mock import MagicMock
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

mock_sensors = MagicMock()
mock_sensors.SoilSensor.return_value.get_voltage.return_value = 3.0
mock_sensors.MotorControl.return_value.turn_on.return_value = None
mock_sensors.MotorControl.return_value.turn_off.return_value = None

sys.modules["sensors"] = mock_sensors
