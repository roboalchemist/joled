from machine import I2C, Pin
import time
from bmp390 import BMP390
from ssd1306 import SSD1306_I2C

# Initialize I2C
i2c = I2C(0, scl=Pin(7), sda=Pin(6))

# Initialize BMP390 sensors
bmp1 = BMP390(i2c, address=0x77)
bmp2 = BMP390(i2c, address=0x76)

# Initialize SSD1306 OLED display
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

def display_sensor_data(sensor_num, temp, pressure):
    oled.text(f"BMP{sensor_num}: {temp:.1f}C", 0, sensor_num * 30 - 30)
    oled.text(f"P: {pressure:.2f}hPa", 0, sensor_num * 30 - 20)

while True:
    # Read data from both BMP390 sensors
    temp1 = bmp1.temperature
    pressure1 = bmp1.pressure
    temp2 = bmp2.temperature
    pressure2 = bmp2.pressure

    # Clear the display
    oled.fill(0)

    # Display data for both sensors
    display_sensor_data(1, temp1, pressure1)
    display_sensor_data(2, temp2, pressure2)

    # Show the display
    oled.show()

    # Optional: Print to console for debugging
    print(f"BMP1 - Temp: {temp1:.2f}°C, Pressure: {pressure1:.2f}hPa")
    print(f"BMP2 - Temp: {temp2:.2f}°C, Pressure: {pressure2:.2f}hPa")
    print("")

    time.sleep(1)