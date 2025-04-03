from sensors import SoilSensor, MotorControl
import time
water_motor = MotorControl(pin_number=23)
soil_sensor = SoilSensor()

#test turn on
time.sleep(3)
water_motor.turn_on()
time.sleep(3)
water_motor.turn_off()

#Leave soil in air, should by somewhere along 2.2-2.3v
print(soil_sensor.get_voltage())
