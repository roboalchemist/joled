from machine import I2C, Pin
import ssd1306
import time

# Define I2C bus with SDA on pin 0 and SCL on pin 1
i2c = I2C(0, scl=Pin(7), sda=Pin(6))


SOLENOID_PIN_NUM = 0
#solenoid
solenoid_pin = Pin(SOLENOID_PIN_NUM, Pin.OUT)
solenoid_pin.value(0)


def solenoid_on():
    solenoid_pin.value(1)
    
def solenoid_off():
    solenoid_pin.value(0)


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

# Initialize the SSD1306 display
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Define constants for the offsets
CENTER_X = oled_width // 3        # X position of the center of the graphic
CENTER_Y = oled_height // 3       # Y position of the center of the graphic
UP_DOWN_OFFSET = 20               # Vertical offset for up/down arrows from the center
LEFT_RIGHT_OFFSET = 20            # Horizontal offset for left/right arrows from the center

# Define constants for the B1, B2, B3 button positions and sizes
B1_X_OFFSET = -40                 # X offset from the center for B1 button
B1_Y_OFFSET = 30                 # Y offset from the center for B1 button

B2_X_OFFSET = -15                   # X offset from the center for B2 button
B2_Y_OFFSET = 30                 # Y offset from the center for B2 button

B3_X_OFFSET = 10                  # X offset from the center for B3 button
B3_Y_OFFSET = 30                 # Y offset from the center for B3 button

BUTTON_WIDTH = 20                 # Width of the buttons
BUTTON_HEIGHT = 10                # Height of the buttons

# Small 5x7 font data for "B1", "B2", "B3"
small_font = {
    'B1': [0x1F, 0x15, 0x15, 0x15, 0x0A, 0x00, 0x12, 0x1F, 0x10, 0x00],  # B
    'B2': [0x1F, 0x15, 0x15, 0x15, 0x0A, 0x12, 0x19, 0x15, 0x12, 0x00],  # B
    'B3': [0x1F, 0x15, 0x15, 0x15, 0x0A, 0x11, 0x15, 0x15, 0x1F, 0x00],  # B
}

# Function to read the PCF8575 pins
def read_pcf8575():
    data = i2c.readfrom(PCF8575_ADDR, 2)  # Read 2 bytes (16 bits) from the PCF8575
    value = data[1] << 8 | data[0]  # Combine the two bytes into a 16-bit number
    return value

# Function to write to PCF8575 pins
def write_pcf8575(value):
    data = bytearray(2)
    data[0] = value & 0x00       # Lower byte
    data[1] = (value >> 8) & 0xFF # Upper byte
    i2c.writeto(PCF8575_ADDR, data)

# Function to draw a small character at a given position
def draw_small_char(oled, char, x, y):
    if char in small_font:
        data = small_font[char]
        for col, line in enumerate(data):
            for row in range(8):
                if line & (1 << row):
                    oled.pixel(x + col, y + row, 1)

# Custom function to draw a triangle
def draw_triangle(oled, x0, y0, x1, y1, x2, y2, c):
    oled.line(x0, y0, x1, y1, c)
    oled.line(x1, y1, x2, y2, c)
    oled.line(x2, y2, x0, y0, c)

# Custom function to fill a triangle
def fill_triangle(oled, x0, y0, x1, y1, x2, y2, c):
    min_x = min(x0, x1, x2)
    max_x = max(x0, x1, x2)
    for x in range(min_x, max_x + 1):
        min_y = min(y0, y1, y2)
        max_y = max(y0, y1, y2)
        for y in range(min_y, max_y + 1):
            if point_in_triangle(x, y, x0, y0, x1, y1, x2, y2):
                oled.pixel(x, y, c)

# Helper function to determine if a point is inside a triangle
def point_in_triangle(px, py, x0, y0, x1, y1, x2, y2):
    dX = px - x2
    dY = py - y2
    dX21 = x2 - x1
    dY12 = y1 - y2
    D = dY12 * (x0 - x2) + dX21 * (y0 - y2)
    s = dY12 * dX + dX21 * dY
    t = (y2 - y0) * dX + (x0 - x2) * dY
    return (D < 0 and s <= 0 and t <= 0 and s + t >= D) or (D > 0 and s >= 0 and t >= 0 and s + t <= D)

# Custom function to draw a circle
def draw_circle(oled, x0, y0, r, c):
    f = 1 - r
    ddF_x = 1
    ddF_y = -2 * r
    x = 0
    y = r
    oled.pixel(x0, y0 + r, c)
    oled.pixel(x0, y0 - r, c)
    oled.pixel(x0 + r, y0, c)
    oled.pixel(x0 - r, y0, c)
    while x < y:
        if f >= 0:
            y -= 1
            ddF_y += 2
            f += ddF_y
        x += 1
        ddF_x += 2
        f += ddF_x
        oled.pixel(x0 + x, y0 + y, c)
        oled.pixel(x0 - x, y0 + y, c)
        oled.pixel(x0 + x, y0 - y, c)
        oled.pixel(x0 - x, y0 - y, c)
        oled.pixel(x0 + y, y0 + x, c)
        oled.pixel(x0 - y, y0 + x, c)
        oled.pixel(x0 + y, y0 - x, c)
        oled.pixel(x0 - y, y0 - x, c)

# Custom function to fill a circle
def fill_circle(oled, x0, y0, r, c):
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            if x * x + y * y <= r * r:
                oled.pixel(x0 + x, y0 + y, c)

# Function to draw the D-pad with triangles, center circle, and B1, B2, B3 buttons with small labels
def draw_dpad(up, down, left, right, center, b1_btn, b2_btn, b3_btn):
    oled.fill(0)  # Clear the display

    # Draw smaller triangles for the directional buttons
    if up:
        fill_triangle(oled, CENTER_X, CENTER_Y - UP_DOWN_OFFSET, 
                      CENTER_X - 8, CENTER_Y - UP_DOWN_OFFSET + 8, 
                      CENTER_X + 8, CENTER_Y - UP_DOWN_OFFSET + 8, 1)  # Filled up triangle
    else:
        draw_triangle(oled, CENTER_X, CENTER_Y - UP_DOWN_OFFSET, 
                      CENTER_X - 8, CENTER_Y - UP_DOWN_OFFSET + 8, 
                      CENTER_X + 8, CENTER_Y - UP_DOWN_OFFSET + 8, 1)  # Hollow up triangle

    if down:
        fill_triangle(oled, CENTER_X, CENTER_Y + UP_DOWN_OFFSET, 
                      CENTER_X - 8, CENTER_Y + UP_DOWN_OFFSET - 8, 
                      CENTER_X + 8, CENTER_Y + UP_DOWN_OFFSET - 8, 1)  # Filled down triangle
    else:
        draw_triangle(oled, CENTER_X, CENTER_Y + UP_DOWN_OFFSET, 
                      CENTER_X - 8, CENTER_Y + UP_DOWN_OFFSET - 8, 
                      CENTER_X + 8, CENTER_Y + UP_DOWN_OFFSET - 8, 1)  # Hollow down triangle

    if left:
        fill_triangle(oled, CENTER_X - LEFT_RIGHT_OFFSET, CENTER_Y, 
                      CENTER_X - LEFT_RIGHT_OFFSET + 8, CENTER_Y - 8, 
                      CENTER_X - LEFT_RIGHT_OFFSET + 8, CENTER_Y + 8, 1)  # Filled left triangle
    else:
        draw_triangle(oled, CENTER_X - LEFT_RIGHT_OFFSET, CENTER_Y, 
                      CENTER_X - LEFT_RIGHT_OFFSET + 8, CENTER_Y - 8, 
                      CENTER_X - LEFT_RIGHT_OFFSET + 8, CENTER_Y + 8, 1)  # Hollow left triangle

    if right:
        fill_triangle(oled, CENTER_X + LEFT_RIGHT_OFFSET, CENTER_Y, 
                      CENTER_X + LEFT_RIGHT_OFFSET - 8, CENTER_Y - 8, 
                      CENTER_X + LEFT_RIGHT_OFFSET - 8, CENTER_Y + 8, 1)  # Filled right triangle
    else:
        draw_triangle(oled, CENTER_X + LEFT_RIGHT_OFFSET, CENTER_Y, 
                      CENTER_X + LEFT_RIGHT_OFFSET - 8, CENTER_Y - 8, 
                      CENTER_X + LEFT_RIGHT_OFFSET - 8, CENTER_Y + 8, 1)  # Hollow right triangle

    # Draw a smaller circle for the center button
    if center:
        fill_circle(oled, CENTER_X, CENTER_Y, 6, 1)  # Filled center circle
    else:
        draw_circle(oled, CENTER_X, CENTER_Y, 6, 1)  # Hollow center circle

    # Draw the B1 button as a rectangle with "B1" label
    b1_x = CENTER_X + B1_X_OFFSET
    b1_y = CENTER_Y + B1_Y_OFFSET
    if b1_btn:
        oled.fill_rect(b1_x, b1_y, BUTTON_WIDTH, BUTTON_HEIGHT, 1)  # Filled B1 button
        draw_small_char(oled, 'B1', b1_x + 2, b1_y + 2)
    else:
        oled.rect(b1_x, b1_y, BUTTON_WIDTH, BUTTON_HEIGHT, 1)  # Hollow B1 button
        draw_small_char(oled, 'B1', b1_x + 2, b1_y + 2)

    # Draw the B2 button as a rectangle with "B2" label
    b2_x = CENTER_X + B2_X_OFFSET
    b2_y = CENTER_Y + B2_Y_OFFSET
    if b2_btn:
        oled.fill_rect(b2_x, b2_y, BUTTON_WIDTH, BUTTON_HEIGHT, 1)  # Filled B2 button
        draw_small_char(oled, 'B2', b2_x + 2, b2_y + 2)
    else:
        oled.rect(b2_x, b2_y, BUTTON_WIDTH, BUTTON_HEIGHT, 1)  # Hollow B2 button
        draw_small_char(oled, 'B2', b2_x + 2, b2_y + 2)

    # Draw the B3 button as a rectangle with "B3" label
    b3_x = CENTER_X + B3_X_OFFSET
    b3_y = CENTER_Y + B3_Y_OFFSET
    if b3_btn:
        oled.fill_rect(b3_x, b3_y, BUTTON_WIDTH, BUTTON_HEIGHT, 1)  # Filled B3 button
        draw_small_char(oled, 'B3', b3_x + 2, b3_y + 2)
    else:
        oled.rect(b3_x, b3_y, BUTTON_WIDTH, BUTTON_HEIGHT, 1)  # Hollow B3 button
        draw_small_char(oled, 'B3', b3_x + 2, b3_y + 2)

    oled.show()  # Update the display

# Main loop to constantly check buttons and update the display and LEDs
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

    # Update D-pad display based on button presses
    draw_dpad(up_pressed, down_pressed, left_pressed, right_pressed, center_pressed, b1_pressed, b2_pressed, b3_pressed)
    
    # Control RGB LEDs on I2C expander based on button presses
    led_value = 0
    solenoid_state = False
    
    if b1_pressed:
        #led_value |= GREEN_LED_MASK
        solenoid_state = True
    if b2_pressed:
        pass
        #led_value |= RED_LED_MASK
    if b3_pressed:
        led_value |= BLUE_LED_MASK
        
    if solenoid_state:
        led_value |= GREEN_LED_MASK
        solenoid_on()
    else:
        led_value |= RED_LED_MASK
        solenoid_off()

    # Write the LED state to the PCF8575
    write_pcf8575(~led_value)  # Use ~ to invert since PCF8575 uses active-low logic

    time.sleep(0.01)  # Add a small delay to debounce the buttons

