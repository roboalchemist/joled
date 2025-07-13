# Main OLED Controller Library
# Supports I2C OLED displays and button input

import time
from machine import Pin, I2C
from micropython import const
from .font5x7 import Font5x7

# SSD1306 OLED Commands
SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)


class SSD1306_I2C:
    """SSD1306 OLED display driver for I2C interface"""
    
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.poweron()
        self.init_display()
    
    def init_display(self):
        """Initialize the display"""
        for cmd in (
            SET_DISP | 0x00,  # off
            # address setting
            SET_MEM_ADDR,
            0x00,  # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01,  # column addr 127 mapped to SEG0
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,  # scan from COM[N] to COM0
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x02 if self.width > 2 * self.height else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV,
            0x80,
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,
            0x30,  # 0.83*Vcc
            # display
            SET_CONTRAST,
            0xFF,  # maximum
            SET_ENTIRE_ON,  # output follows RAM contents
            SET_NORM_INV,  # not inverted
            # charge pump
            SET_CHARGE_PUMP,
            0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,
        ):  # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()
    
    def poweron(self):
        """Power on the display"""
        pass
    
    def poweroff(self):
        """Power off the display"""
        self.write_cmd(SET_DISP | 0x00)
    
    def contrast(self, contrast):
        """Set display contrast (0-255)"""
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)
    
    def invert(self, invert):
        """Invert display colors"""
        self.write_cmd(SET_NORM_INV | (invert & 1))
    
    def show(self):
        """Update the display with buffer contents"""
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)
    
    def fill(self, col):
        """Fill entire display with color (0 or 1)"""
        self.buffer[:] = [0xFF if col else 0x00] * len(self.buffer)
    
    def pixel(self, x, y, col):
        """Set a pixel at (x, y) to color col"""
        if 0 <= x < self.width and 0 <= y < self.height:
            index = x + (y // 8) * self.width
            if col:
                self.buffer[index] |= 1 << (y & 7)
            else:
                self.buffer[index] &= ~(1 << (y & 7))
    
    def line(self, x0, y0, x1, y1, col):
        """Draw a line from (x0, y0) to (x1, y1)"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        n = 1 + dx + dy
        x_inc = 1 if x1 > x0 else -1
        y_inc = 1 if y1 > y0 else -1
        error = dx - dy
        
        dx *= 2
        dy *= 2
        
        for _ in range(n):
            self.pixel(x, y, col)
            if error > 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx
    
    def rect(self, x, y, w, h, col):
        """Draw rectangle outline"""
        self.hline(x, y, w, col)
        self.hline(x, y + h - 1, w, col)
        self.vline(x, y, h, col)
        self.vline(x + w - 1, y, h, col)
    
    def fill_rect(self, x, y, w, h, col):
        """Draw filled rectangle"""
        for i in range(x, x + w):
            self.vline(i, y, h, col)
    
    def hline(self, x, y, w, col):
        """Draw horizontal line"""
        for i in range(w):
            self.pixel(x + i, y, col)
    
    def vline(self, x, y, h, col):
        """Draw vertical line"""
        for i in range(h):
            self.pixel(x, y + i, col)
    
    def write_cmd(self, cmd):
        """Write command to display"""
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)
    
    def write_data(self, buf):
        """Write data to display"""
        self.i2c.writeto(self.addr, b'\x40' + buf)


class ButtonController:
    """I2C GPIO expander button controller"""
    
    def __init__(self, i2c, addr=0x20, num_buttons=4):
        self.i2c = i2c
        self.addr = addr
        self.num_buttons = num_buttons
        self.button_states = [False] * num_buttons
        self.last_states = [False] * num_buttons
        
        # Initialize GPIO expander if present
        try:
            # Try to read from device to check if it exists
            self.i2c.readfrom(self.addr, 1)
            self.has_expander = True
            self._init_expander()
        except:
            self.has_expander = False
            print("Warning: I2C GPIO expander not found at address", hex(self.addr))
    
    def _init_expander(self):
        """Initialize GPIO expander for button input"""
        # Configure all pins as inputs with pull-ups
        # This is generic - specific implementation depends on GPIO expander type
        pass
    
    def update(self):
        """Update button states"""
        if not self.has_expander:
            return
        
        try:
            # Read button states from GPIO expander
            data = self.i2c.readfrom(self.addr, 1)[0]
            
            # Update button states
            self.last_states = self.button_states.copy()
            for i in range(self.num_buttons):
                self.button_states[i] = not bool(data & (1 << i))  # Invert for pull-up
        except:
            pass
    
    def is_pressed(self, button):
        """Check if button is currently pressed"""
        if 0 <= button < self.num_buttons:
            return self.button_states[button]
        return False
    
    def was_pressed(self, button):
        """Check if button was just pressed (rising edge)"""
        if 0 <= button < self.num_buttons:
            return self.button_states[button] and not self.last_states[button]
        return False


class OLEDController:
    """Combined OLED display and button controller"""
    
    def __init__(self, i2c_bus=0, sda_pin=4, scl_pin=5, 
                 oled_addr=0x3C, button_addr=0x20,
                 width=128, height=64, num_buttons=4):
        """
        Initialize OLED controller
        
        Args:
            i2c_bus: I2C bus number (0 or 1)
            sda_pin: SDA pin number
            scl_pin: SCL pin number
            oled_addr: I2C address of OLED display
            button_addr: I2C address of button controller
            width: Display width in pixels
            height: Display height in pixels
            num_buttons: Number of buttons
        """
        # Initialize I2C
        if isinstance(i2c_bus, I2C):
            self.i2c = i2c_bus
        else:
            self.i2c = I2C(i2c_bus, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=400000)
        
        # Initialize display
        self.display = SSD1306_I2C(width, height, self.i2c, oled_addr)
        
        # Initialize button controller
        self.buttons = ButtonController(self.i2c, button_addr, num_buttons)
        
        # Initialize font
        self.font = Font5x7()
        
        # Display properties
        self.width = width
        self.height = height
        self.num_buttons = num_buttons
    
    def clear(self):
        """Clear the display"""
        self.display.fill(0)
    
    def show(self):
        """Update the display"""
        self.display.show()
    
    def pixel(self, x, y, color=1):
        """Set a pixel"""
        self.display.pixel(x, y, color)
    
    def line(self, x0, y0, x1, y1, color=1):
        """Draw a line"""
        self.display.line(x0, y0, x1, y1, color)
    
    def rect(self, x, y, w, h, color=1):
        """Draw rectangle outline"""
        self.display.rect(x, y, w, h, color)
    
    def fill_rect(self, x, y, w, h, color=1):
        """Draw filled rectangle"""
        self.display.fill_rect(x, y, w, h, color)
    
    def text(self, text, x, y, color=1):
        """Draw text using 5x7 font"""
        cursor_x = x
        for char in text:
            if cursor_x + self.font.width > self.width:
                break  # Text goes off screen
            
            char_data = self.font.get_char_data(char)
            for col in range(self.font.width):
                byte_data = char_data[col]
                for row in range(self.font.height):
                    if byte_data & (1 << row):
                        self.display.pixel(cursor_x + col, y + row, color)
            
            cursor_x += self.font.width + 1  # +1 for spacing
    
    def text_width(self, text):
        """Calculate text width in pixels"""
        return self.font.text_width(text)
    
    def center_text(self, text, y, color=1):
        """Draw text centered horizontally"""
        text_w = self.text_width(text)
        x = (self.width - text_w) // 2
        self.text(text, x, y, color)
    
    def update_buttons(self):
        """Update button states"""
        self.buttons.update()
    
    def button_pressed(self, button):
        """Check if button is currently pressed"""
        return self.buttons.is_pressed(button)
    
    def button_just_pressed(self, button):
        """Check if button was just pressed"""
        return self.buttons.was_pressed(button)
    
    def contrast(self, contrast):
        """Set display contrast (0-255)"""
        self.display.contrast(contrast)
    
    def invert(self, invert=True):
        """Invert display colors"""
        self.display.invert(invert)
    
    def poweroff(self):
        """Turn off display"""
        self.display.poweroff()
    
    def scan_i2c(self):
        """Scan I2C bus for devices"""
        devices = self.i2c.scan()
        print("I2C devices found:")
        for device in devices:
            print(f"  0x{device:02X}")
        return devices