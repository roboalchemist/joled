from machine import I2C, Pin
import ssd1306
import time

# Define I2C bus with SDA on pin 0 and SCL on pin 1
#i2c = I2C(0, scl=Pin(6), sda=Pin(7)) # previous usage 
#i2c = I2C(0, scl=Pin(9), sda=Pin(8)) # super mini standard, used in all new oled control boards

# Initialize the SSD1306 OLED display
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)




# Define the PCF8575 address (0x20 is a common address; modify as needed)
PCF8575_ADDR = 0x20

# Define input masks for the buttons (B1 - P2, B2 - P1, B3 - P0)
B1_MASK = 0x0004   # P2 - Green
B2_MASK = 0x0002   # P1 - Red
B3_MASK = 0x0001   # P0 - Blue

# Define input masks for directional controls (UP, DOWN, LEFT, RIGHT, CENTER)
UP_MASK = 0x0040   # P6
DOWN_MASK = 0x0010 # P4
LEFT_MASK = 0x0020 # P5
RIGHT_MASK = 0x0008 # P3
CENTER_MASK = 0x0080 # P7

# Define RGB LED masks (outputs)
RED_MASK = 0x0100   # P8 for Red
GREEN_MASK = 0x0200 # P9 for Green
BLUE_MASK = 0x0400  # P10 for Blue

# Function to read the PCF8575 pins and invert the bitmask
def read_pcf8575():
    data = i2c.readfrom(PCF8575_ADDR, 2)  # Read 2 bytes (16 bits) from the PCF8575
    value =  0xFF & data[0]  # Combine the two bytes into a 16-bit number
    return value # Invert the value and mask it to 16 bits

# Function to write to the PCF8575 pins (for RGB control)
def write_pcf8575(value):
    data = bytearray(2)
    data[0] = value & 0xFF  # Lower byte
    data[1] = (value >> 8) & 0xFF  # Upper byte
    i2c.writeto(PCF8575_ADDR, data)

# Function to display button states on the OLED
def display_on_oled(message, value):
    oled.fill(0)  # Clear the display
    oled.text(message, 0, 0)  # Display message
    oled.text(f"Value: {value:016b}", 0, 10)  # Display the binary representation of the value
    oled.show()

# Function to set RGB LEDs based on the active color
def set_rgb_color(red, green, blue):
    # Start with all pins off (active low logic)
    rgb_state = 0xFF00
    
    # Set each color based on the parameters (active low, so 0 means on)
    if red:
        rgb_state &= ~RED_MASK
    if green:
        rgb_state &= ~GREEN_MASK
    if blue:
        rgb_state &= ~BLUE_MASK
    
    write_pcf8575(rgb_state)  # Update the PCF8575 pins

# Function to set all pins as inputs (write 0xFFFF to PCF8575)
def set_all_pins_as_inputs():
    data = bytearray(2)
    data[0] = 0x00  # Lower byte
    data[1] = 0xFF  # Upper byte
    i2c.writeto(PCF8575_ADDR, data)


# Set all pins as inputs at the beginning
set_all_pins_as_inputs()

# Main loop to check inputs and update OLED display and RGB LEDs
while True:
    # Read the current state of the PCF8575 pins
    value = read_pcf8575()

    # Print the raw value to the console for debugging
    print(f"PCF8575 Value: {value:016b}")  # Print as a 16-bit binary number

    # Check button presses and display corresponding messages and colors on RGB LEDs
    if value & B1_MASK:
        display_on_oled("B1 Pressed", value)  # Show message on OLED
        set_rgb_color(0, 1, 0)  # Green on P9
    elif value & B2_MASK:
        display_on_oled("B2 Pressed", value)  # Show message on OLED
        set_rgb_color(1, 0, 0)  # Red on P8
    elif value & B3_MASK:
        display_on_oled("B3 Pressed", value)  # Show message on OLED
        set_rgb_color(0, 0, 1)  # Blue on P10
    else:
        set_rgb_color(0, 0, 0)  # Turn off all RGB LEDs when no button is pressed

    # Check for directional button presses and display messages on OLED (no RGB for these)
    if value & UP_MASK:
        display_on_oled("UP Pressed", value)
    elif value & DOWN_MASK:
        display_on_oled("DOWN Pressed", value)
    elif value & LEFT_MASK:
        display_on_oled("LEFT Pressed", value)
    elif value & RIGHT_MASK:
        display_on_oled("RIGHT Pressed", value)
    elif value & CENTER_MASK:
        display_on_oled("CENTER Pressed", value)
    
    time.sleep(0.1)  # Add a small delay to debounce the buttons
