import time
import board
import adafruit_ads7830.ads7830
from adafruit_ads7830.analog_in import AnalogIn

i2c = board.I2C()

# Initialize ADS7830
adc = adafruit_ads7830.ads7830.ADS7830(i2c, adc_power_down=True)
analog_inputs = []
for i in range(8):
    c = AnalogIn(adc, i)
    analog_inputs.append(c)

while True:
    for i in range(8):
        print(f"ADC input {i} = {analog_inputs[i].value}")
    time.sleep(0.1)