import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO
import logging
import time

logger = logging.getLogger(__name__)


class SoilSensor:
    """
    Soil sensor that reads analog voltage from an ADS1115 ADC
    over I2C. Higher voltage usually implies a dryer medium.
    """

    def __init__(self):
        """
        Initialize I2C connection and ADS1115 channel.
        """
        self._i2c = busio.I2C(board.SCL, board.SDA)
        self._ads = ADS.ADS1115(self._i2c)
        self._channel = AnalogIn(self._ads, ADS.P0)

    def get_voltage(self) -> float:
        """
        Read and return the voltage from the soil sensor.
        """
        # Get average of readings
        readings = []
        max_readings = 50
        while len(readings) < max_readings:
            readings.append(self._channel.voltage)
            time.sleep(0.2)
        voltage = sum(readings)/max_readings
        logging.info(f"Soil sensor reading: {voltage:.3f} V")
        return voltage


class MotorControl:
    """
    Controls the water motor via a GPIO pin on a Raspberry Pi.
    """

    def __init__(self, pin_number: int = 23):
        """
        Initialize the GPIO pin for motor control.

        :param pin_number: The GPIO pin to control the motor.
        """
        logging.info("Initializing MotorControl.")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_number, GPIO.OUT)
        self._pin_number = pin_number

    def turn_on(self) -> None:
        """
        Set the GPIO pin high to turn the motor on.
        """
        GPIO.output(self._pin_number, GPIO.HIGH)
        logging.debug("Motor activated")

    def turn_off(self) -> None:
        """
        Set the GPIO pin low to turn the motor off.
        """
        GPIO.output(self._pin_number, GPIO.LOW)
        logging.debug("Motor de-activated")
