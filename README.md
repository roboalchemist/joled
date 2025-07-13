# MicroPython OLED Controller Library

A MicroPython library for controlling I2C OLED displays with integrated button input support. Features a compact 5x7 bitmap font for clear text rendering on small displays.

## Features

- **I2C OLED Display Support**: Compatible with SSD1306 and similar OLED controllers
- **Button Input**: I2C GPIO expander support for multiple buttons
- **5x7 Bitmap Font**: Includes comprehensive character set with special symbols
- **Graphics Primitives**: Lines, rectangles, pixels, and text rendering
- **Easy Installation**: Install via `mpremote mip install`

## Installation

### Using mpremote (Recommended)

```bash
mpremote mip install github:roboalchemist/joled
```

### Manual Installation

1. Download the library files
2. Copy the `oled_controller` folder to your MicroPython device's lib directory

## Quick Start

```python
from oled_controller import OLEDController

# Initialize JOLED controller with RGB support
controller = OLEDController.create_joled()

# Clear display and show text
controller.clear()
controller.text("Hello World!", 0, 0)
controller.center_text("Centered", 20)
controller.rgb_color('blue')  # Set LED to blue
controller.show()

# Check button input (8 total inputs: 5-way D-pad + 3 buttons)
controller.update_buttons()
if controller.button_just_pressed(7):  # Center button
    controller.clear()
    controller.text("Center pressed!", 0, 0)
    controller.rgb_color('green')  # Change LED to green
    controller.show()
```

## Hardware Setup

### JOLED Controller Specifications

The JOLED controller follows the QWIIC standard (https://www.sparkfun.com/qwiic) for easy connectivity.

**I2C Configuration:**
- **SCL**: Pin 7
- **SDA**: Pin 6  
- **Frequency**: 400kHz

**Components:**

#### 128x64 SSD1306 OLED Display
- **I2C Address**: 0x3C (default)
- **Resolution**: 128x64 pixels
- Connected via I2C bus

#### PCF8575 Port Expander  
- **I2C Address**: 0x20
- **Initialization**: Write 0x0007 to establish baseline state (buttons low, LEDs high/off)

**Controls:**

#### 5-Way D-Pad (Active High, Pulled Low)
- **Up**: P6
- **Down**: P4  
- **Left**: P5
- **Right**: P3
- **Center**: P7

#### 3 Buttons (Active High, Pulled Low)
- **B1**: P2
- **B2**: P1
- **B3**: P0

#### RGB LED (Active Low)
- **Red**: P8
- **Green**: P9
- **Blue**: P10

**Physical Layout:**
```
JOLED Controller:
        ------------------------------------------
        |                              [RGB]     |
[qwiic]<|    ----------------        U           |>[qwiic]
        |    |    128x64    |     L  C  R        |
        |    | SSD1306 OLED |        D           |
[qwiic]<|    ----------------                    |>[qwiic]
        |                       B1   B2  B3      |
        ------------------------------------------
```

### Generic I2C Setup (Other Hardware)
- **SDA**: Connect to your microcontroller's SDA pin (default: GPIO 4)
- **SCL**: Connect to your microcontroller's SCL pin (default: GPIO 5)  
- **VCC**: 3.3V or 5V (depending on display)
- **GND**: Ground

## API Reference

### OLEDController Class

#### Initialization
```python
# JOLED Controller (recommended)
controller = OLEDController.create_joled()  # Pre-configured for JOLED

# Or manually configure JOLED
controller = OLEDController(
    sda_pin=6,          # JOLED SDA pin
    scl_pin=7,          # JOLED SCL pin
    num_buttons=8,      # 5-way D-pad + 3 buttons
    has_rgb=True        # Enable RGB LED support
)

# Generic setup (other hardware)
controller = OLEDController(
    i2c_bus=0,          # I2C bus number (0 or 1)
    sda_pin=4,          # SDA pin number
    scl_pin=5,          # SCL pin number
    oled_addr=0x3C,     # OLED I2C address
    button_addr=0x20,   # Button controller I2C address
    width=128,          # Display width in pixels
    height=64,          # Display height in pixels
    num_buttons=4       # Number of buttons
)
```

#### Display Methods
```python
controller.clear()                    # Clear display
controller.show()                     # Update display
controller.pixel(x, y, color=1)      # Set pixel
controller.line(x0, y0, x1, y1, color=1)  # Draw line
controller.rect(x, y, w, h, color=1)      # Draw rectangle
controller.fill_rect(x, y, w, h, color=1) # Draw filled rectangle
controller.text(text, x, y, color=1)      # Draw text
controller.center_text(text, y, color=1)  # Draw centered text
controller.text_width(text)               # Get text width
controller.contrast(level)                # Set contrast (0-255)
controller.invert(True/False)             # Invert colors
controller.poweroff()                     # Turn off display
```

#### Button Methods
```python
controller.update_buttons()           # Update button states
controller.button_pressed(button)     # Check if button is pressed
controller.button_just_pressed(button) # Check if button was just pressed
```

#### RGB LED Methods (JOLED Only)
```python
controller.set_rgb(red=True, green=False, blue=False)  # Set individual colors
controller.rgb_color('red')                           # Set predefined color
controller.rgb_off()                                  # Turn off RGB LED
```

#### Utility Methods
```python
controller.scan_i2c()               # Scan I2C bus for devices

# JOLED Helper
controller = OLEDController.create_joled()  # Pre-configured for JOLED
```

### Font5x7 Class

```python
from oled_controller import Font5x7

font = Font5x7()
char_data = font.get_char_data('A')   # Get bitmap data for character
width = font.text_width("Hello")      # Calculate text width
exists = font.char_exists('€')        # Check if character exists
```

## Supported Characters

The 5x7 font includes:
- **ASCII**: Letters (A-Z, a-z), numbers (0-9), punctuation
- **Special**: German umlauts (Ä, Ö, Ü, ä, ö, ü)
- **Symbols**: Euro (€), degree (°), arrows (→, ←)

## Examples

### Basic Display
```python
from oled_controller import OLEDController

controller = OLEDController()
controller.clear()
controller.text("MicroPython", 0, 0)
controller.text("OLED Library", 0, 10)
controller.rect(0, 20, 128, 20)
controller.show()
```

### JOLED Button Input
```python
from oled_controller import OLEDController
import time

controller = OLEDController(sda_pin=6, scl_pin=7, num_buttons=8)

# Button mapping for JOLED
button_names = ["B3", "B2", "B1", "Right", "Down", "Left", "Up", "Center"]

while True:
    controller.update_buttons()
    
    controller.clear()
    controller.text("JOLED Controls:", 0, 0)
    
    for i in range(8):
        if controller.button_pressed(i):
            controller.text(f"{button_names[i]}: ON", 0, 10 + (i%6)*8)
        else:
            controller.text(f"{button_names[i]}: OFF", 70, 10 + (i%6)*8)
    
    controller.show()
    time.sleep(0.1)
```

### JOLED RGB LED Demo
```python
from oled_controller import OLEDController
import time

# Initialize JOLED with RGB support
controller = OLEDController.create_joled()

colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white']

for color in colors:
    controller.clear()
    controller.center_text(f"Color: {color}", 20)
    controller.rgb_color(color)
    controller.show()
    time.sleep(1)

controller.rgb_off()
```

### Graphics Demo
```python
from oled_controller import OLEDController

controller = OLEDController()
controller.clear()

# Draw some graphics
controller.line(0, 0, 127, 63)
controller.rect(10, 10, 20, 20)
controller.fill_rect(50, 20, 30, 15)
controller.center_text("Graphics!", 50)

controller.show()
```

## Configuration

### JOLED Controller Setup
```python
# JOLED with RGB LED support
controller = OLEDController.create_joled()
# Or: controller = OLEDController(sda_pin=6, scl_pin=7, num_buttons=8, has_rgb=True)
```

### Custom I2C Pins (Other Hardware)
```python
# Use different I2C pins for generic hardware
controller = OLEDController(sda_pin=21, scl_pin=22)
```

### Different Display Size
```python
# 128x32 display
controller = OLEDController(width=128, height=32)
```

### Existing I2C Bus
```python
from machine import I2C, Pin

# Use existing I2C instance
i2c = I2C(0, sda=Pin(4), scl=Pin(5))
controller = OLEDController(i2c_bus=i2c)
```

## Troubleshooting

### Display Not Working
1. Check I2C connections (SDA, SCL, VCC, GND)
2. Verify I2C address: `controller.scan_i2c()`
3. Try different contrast: `controller.contrast(255)`
4. Check power supply voltage

### Button Input Not Working
1. Verify button controller I2C address
2. Check GPIO expander connections
3. The library will work without buttons if no GPIO expander is found

### JOLED Button Mapping
```python
# JOLED button mapping (PCF8575 pins P0-P7)
BUTTON_MAP = {
    0: "B3",     # P0 - Button 3
    1: "B2",     # P1 - Button 2  
    2: "B1",     # P2 - Button 1
    3: "Right",  # P3 - D-pad Right
    4: "Down",   # P4 - D-pad Down
    5: "Left",   # P5 - D-pad Left
    6: "Up",     # P6 - D-pad Up
    7: "Center"  # P7 - D-pad Center
}
```

### JOLED RGB LED Control
```python
# Initialize JOLED with RGB support
controller = OLEDController.create_joled()

# Set individual colors
controller.set_rgb(red=True, green=False, blue=False)  # Red only
controller.set_rgb(red=True, green=True, blue=False)   # Yellow

# Use predefined colors
controller.rgb_color('red')      # Red
controller.rgb_color('green')    # Green  
controller.rgb_color('blue')     # Blue
controller.rgb_color('yellow')   # Yellow
controller.rgb_color('magenta')  # Magenta
controller.rgb_color('cyan')     # Cyan
controller.rgb_color('white')    # White
controller.rgb_color('off')      # Turn off

# Turn off RGB LED
controller.rgb_off()
```

### Common I2C Addresses
- **OLED Display**: 0x3C or 0x3D
- **JOLED PCF8575**: 0x20
- **GPIO Expanders**: 0x20-0x27 (MCP23017), 0x38-0x3F (PCF8574)

## Hardware Compatibility

### Tested Microcontrollers
- ESP32
- ESP8266
- Raspberry Pi Pico (RP2040)

### Tested OLED Displays
- 128x64 SSD1306
- 128x32 SSD1306

### JOLED Hardware
- PCF8575 (16-bit I2C GPIO expander)
- 128x64 SSD1306 OLED display
- 5-way D-pad navigation
- 3 additional buttons
- RGB LED indicator

### Generic GPIO Expanders  
- MCP23017 (16-bit)
- PCF8574 (8-bit)
- Generic I2C GPIO expanders

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please submit issues and pull requests on GitHub.

## Version History

- **1.0.0**: Initial release with OLED and button support