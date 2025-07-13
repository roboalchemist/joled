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

# Initialize controller (default I2C pins and addresses)
controller = OLEDController()

# Clear display and show text
controller.clear()
controller.text("Hello World!", 0, 0)
controller.center_text("Centered", 20)
controller.show()

# Check button input
controller.update_buttons()
if controller.button_just_pressed(0):
    controller.clear()
    controller.text("Button 0 pressed!", 0, 0)
    controller.show()
```

## Hardware Setup

### I2C OLED Display
- **SDA**: Connect to your microcontroller's SDA pin (default: GPIO 4)
- **SCL**: Connect to your microcontroller's SCL pin (default: GPIO 5)
- **VCC**: 3.3V or 5V (depending on display)
- **GND**: Ground
- **Default I2C Address**: 0x3C

### Button Controller (Optional)
- I2C GPIO expander for button input
- **Default I2C Address**: 0x20
- Supports up to 4 buttons by default

## API Reference

### OLEDController Class

#### Initialization
```python
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

#### Utility Methods
```python
controller.scan_i2c()               # Scan I2C bus for devices
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

### Button Input
```python
from oled_controller import OLEDController
import time

controller = OLEDController()

while True:
    controller.update_buttons()
    
    controller.clear()
    controller.text("Press buttons:", 0, 0)
    
    for i in range(4):
        if controller.button_pressed(i):
            controller.text(f"Button {i}: ON", 0, 10 + i*10)
        else:
            controller.text(f"Button {i}: OFF", 0, 10 + i*10)
    
    controller.show()
    time.sleep(0.1)
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

### Custom I2C Pins
```python
# Use different I2C pins
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

### Common I2C Addresses
- **OLED Display**: 0x3C or 0x3D
- **GPIO Expanders**: 0x20-0x27 (MCP23017), 0x38-0x3F (PCF8574)

## Hardware Compatibility

### Tested Microcontrollers
- ESP32
- ESP8266
- Raspberry Pi Pico (RP2040)

### Tested OLED Displays
- 128x64 SSD1306
- 128x32 SSD1306

### GPIO Expanders
- MCP23017 (16-bit)
- PCF8574 (8-bit)
- Generic I2C GPIO expanders

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please submit issues and pull requests on GitHub.

## Version History

- **1.0.0**: Initial release with OLED and button support