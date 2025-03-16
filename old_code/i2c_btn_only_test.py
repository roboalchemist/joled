from machine import I2C, Pin
import time

# Define I2C bus with SDA on pin 0 and SCL on pin 1
i2c = I2C(0, scl=Pin(1), sda=Pin(0))

# Define the PCF8575 address (0x20 is a common address; modify as needed)
PCF8575_ADDR = 0x20

# Define button and LED masks for the PCF8575 pins
B3_MASK = 0x0001       # P0: B3 Button (Blue, Input)
B2_MASK = 0x0002       # P1: B2 Button (Red, Input)
B1_MASK = 0x0004       # P2: B1 Button (Green, Input)
RIGHT_MASK = 0x0008    # P3: RIGHT (Direction, Input)
DOWN_MASK = 0x0010     # P4: DOWN (Direction, Input)
LEFT_MASK = 0x0020     # P5: LEFT (Direction, Input)
UP_MASK = 0x0040       # P6: UP (Direction, Input)
CENTER_MASK = 0x0080   # P7: CENTER (Direction, Input)

# Define RGB LED pins on the PCF8575
RED_LED_MASK = 0x0100   # P8: Red LED (RGB Control, Output)
GREEN_LED_MASK = 0x0200 # P9: Green LED (RGB Control, Output)
BLUE_LED_MASK = 0x0400  # P10: Blue LED (RGB Control, Output)

# Function to read the PCF8575 pins
def read_pcf8575():
    data = i2c.readfrom(PCF8575_ADDR, 2)  # Read 2 bytes (16 bits) from the PCF8575
    value = data[1] << 8 | data[0]  # Combine the two bytes into a 16-bit number
    return value

# Function to write to PCF8575 pins
def write_pcf8575(value):
    data = bytearray(2)
    data[0] = value & 0xFF       # Lower byte
    data[1] = (value >> 8) & 0xFF # Upper byte
    i2c.writeto(PCF8575_ADDR, data)

# Main loop to constantly check buttons and update the LEDs
while True:
    value = read_pcf8575()

    up_pressed = bool(value & UP_MASK)
    down_pressed = bool(value & DOWN_MASK)
    left_pressed = bool(value & LEFT_MASK)
    right_pressed = bool(value & RIGHT_MASK)
    center_pressed = bool(value & CENTER_MASK)
    b1_pressed = bool(value & B1_MASK)
    b2_pressed = bool(value & B2_MASK)
    b3_pressed = bool(value & B3_MASK)

    # Control RGB LEDs on I2C expander based on button presses
    led_value = 0
    if b1_pressed:
        led_value |= GREEN_LED_MASK
    if b2_pressed:
        led_value |= RED_LED_MASK
    if b3_pressed:
        led_value |= BLUE_LED_MASK

    # Write the LED state to the PCF8575
    write_pcf8575(~led_value)  # Use ~ to invert since PCF8575 uses active-low logic

    time.sleep(0.1)  # Add a small delay to debounce the buttons
