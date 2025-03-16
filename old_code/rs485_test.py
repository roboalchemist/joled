from machine import UART, Pin, I2C
import ssd1306
import time

# UART setup
uart = UART(1, baudrate=9600, tx=21, rx=20)

# I2C setup for OLED display
i2c = I2C(0, scl=Pin(9), sda=Pin(8))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Variables to store the last message and the last received time
last_message = ''
last_received_time = time.time()

def display_message(msg):
    oled.fill(0)  # Clear the display
    oled.text("Message:", 0, 0)  # Display label
    oled.text(msg, 0, 10)  # Display last message
    elapsed_time = time.time() - last_received_time
    oled.text("Time since msg:", 0, 30)  # Display label
    oled.text("{:.1f} sec".format(elapsed_time), 0, 40)  # Display elapsed time
    oled.show()  # Update the display

while True:
    #display_message('hello\n')
    #if uart.any():
        # Read incoming character
    char = uart.read(1)  # Read one character
    if char is not None:
        display_message(char)
    print(char)

    time.sleep(0.1)
    # Add a small delay to avoid busy-waiting
    #uart.write('hello world\r\n')
    #time.sleep(0.1)
