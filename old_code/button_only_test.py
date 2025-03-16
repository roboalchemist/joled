from machine import I2C, Pin
import time

# Define I2C bus with SDA on pin 6 and SCL on pin 7
i2c = I2C(0, scl=Pin(7), sda=Pin(6))

# Define the PCF8575 address (0x20 is a common address; modify as needed)
PCF8575_ADDR = 0x20

# Function to set all pins as inputs (write 0xFFFF to PCF8575)
def set_all_pins_as_inputs():
    data = bytearray(2)
    data[0] = 0x00  # Lower byte
    data[1] = 0xFF  # Upper byte
    i2c.writeto(PCF8575_ADDR, data)

# Function to read the PCF8575 pins and invert the bitmask
def read_pcf8575():
    data = i2c.readfrom(PCF8575_ADDR, 2)  # Read 2 bytes (16 bits) from the PCF8575
    value =  0xFF & data[0]  # Combine the two bytes into a 16-bit number
    return value # Invert the value and mask it to 16 bits

# Set all pins as inputs at the beginning
set_all_pins_as_inputs()

# Main loop to constantly check buttons and update the LEDs
while True:
    value = read_pcf8575()

    up_pressed =  bool(value & 0x0040)  # P6: UP
    down_pressed =  bool(value & 0x0010)  # P4: DOWN
    left_pressed =  bool(value & 0x0020)  # P5: LEFT
    right_pressed =  bool(value & 0x0008)  # P3: RIGHT
    center_pressed =  bool(value & 0x0080)  # P7: CENTER
    b1_pressed =  bool(value & 0x0004)  # P2: B1 (Green)
    b2_pressed =  bool(value & 0x0002)  # P1: B2 (Red)
    b3_pressed =  bool(value & 0x0001)  # P0: B3 (Blue)

    # Print statements for button presses
    if up_pressed:
        print("UP button pressed")
    if down_pressed:
        print("DOWN button pressed")
    if left_pressed:
        print("LEFT button pressed")
    if right_pressed:
        print("RIGHT button pressed")
    if center_pressed:
        print("CENTER button pressed")
    if b1_pressed:
        print("B1 (Green) button pressed")
    if b2_pressed:
        print("B2 (Red) button pressed")
    if b3_pressed:
        print("B3 (Blue) button pressed")

    # Print the inverted bitmask value in hexadecimal format
    print(f"bitmask: {hex(value)}")
    
    time.sleep(0.1)  # Add a small delay to debounce the buttons
