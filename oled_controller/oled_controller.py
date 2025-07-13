# Main OLED Controller Library
# Supports I2C OLED displays and button input

import time
from machine import Pin, I2C, Timer
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
    """I2C GPIO expander button controller with RGB LED support"""
    
    def __init__(self, i2c, addr=0x20, num_buttons=4, has_rgb=False):
        self.i2c = i2c
        self.addr = addr
        self.num_buttons = num_buttons
        self.button_states = [False] * num_buttons
        self.last_states = [False] * num_buttons
        self.has_rgb = has_rgb
        self.rgb_state = 0x0700  # Default: LEDs off (active low)
        
        # RGB pulsing/animation state
        self.pulse_timer = None
        self.pulse_active = False
        self.pulse_color = [False, False, False]  # [R, G, B]
        self.pulse_brightness = 0.0
        self.pulse_direction = 1
        self.pulse_speed = 0.1
        self.pulse_callback = None
        self.pulse_count = 0
        self.pulse_max = -1  # -1 = infinite
        
        # Initialize GPIO expander if present
        try:
            # Try to read from device to check if it exists
            self.i2c.readfrom(self.addr, 2)
            self.has_expander = True
            self._init_expander()
        except:
            self.has_expander = False
            print("Warning: I2C GPIO expander not found at address", hex(self.addr))
    
    def _init_expander(self):
        """Initialize GPIO expander for button input"""
        if self.has_rgb:
            # For JOLED: Initialize PCF8575 with baseline state
            # Buttons low (P0-P7), LEDs high/off (P8-P10)
            self._write_gpio(0x0700)
    
    def _write_gpio(self, value):
        """Write 16-bit value to PCF8575"""
        if not self.has_expander:
            return
        try:
            # PCF8575 expects LSB first
            low_byte = value & 0xFF
            high_byte = (value >> 8) & 0xFF
            self.i2c.writeto(self.addr, bytes([low_byte, high_byte]))
            if self.has_rgb:
                self.rgb_state = value
        except:
            pass
    
    def _read_gpio(self):
        """Read 16-bit value from PCF8575"""
        if not self.has_expander:
            return 0
        try:
            data = self.i2c.readfrom(self.addr, 2)
            return data[0] | (data[1] << 8)
        except:
            return 0
    
    def update(self):
        """Update button states"""
        if not self.has_expander:
            return
        
        try:
            if self.has_rgb:
                # Read 16-bit value from PCF8575
                data = self._read_gpio()
                # Update button states from lower 8 bits
                self.last_states = self.button_states.copy()
                for i in range(self.num_buttons):
                    self.button_states[i] = bool(data & (1 << i))  # Active high for JOLED
            else:
                # Generic GPIO expander - read 8 bits
                data = self.i2c.readfrom(self.addr, 1)[0]
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
    
    def set_rgb(self, red=False, green=False, blue=False):
        """Set RGB LED colors (for JOLED hardware)"""
        if not self.has_rgb or not self.has_expander:
            return
        
        # LEDs are active low on P8, P9, P10
        # Start with current state but clear LED bits
        new_state = self.rgb_state & 0x00FF  # Keep button state, clear upper bits
        
        # Set LED bits (active low: 0 = on, 1 = off)
        if not red:
            new_state |= (1 << 8)   # P8 high = red off
        if not green:
            new_state |= (1 << 9)   # P9 high = green off  
        if not blue:
            new_state |= (1 << 10)  # P10 high = blue off
        
        self._write_gpio(new_state)
    
    def rgb_off(self):
        """Turn off all RGB LEDs"""
        self.set_rgb(False, False, False)
    
    def rgb_color(self, color):
        """Set RGB LED to predefined color"""
        colors = {
            'red': (True, False, False),
            'green': (False, True, False), 
            'blue': (False, False, True),
            'yellow': (True, True, False),
            'magenta': (True, False, True),
            'cyan': (False, True, True),
            'white': (True, True, True),
            'off': (False, False, False)
        }
        
        if color.lower() in colors:
            r, g, b = colors[color.lower()]
            self.set_rgb(r, g, b)
    
    def _pulse_timer_callback(self, timer):
        """Timer callback for RGB pulsing"""
        if not self.pulse_active or not self.has_rgb:
            return
        
        # Update brightness based on direction
        self.pulse_brightness += self.pulse_direction * self.pulse_speed
        
        # Bounce between 0.0 and 1.0
        if self.pulse_brightness >= 1.0:
            self.pulse_brightness = 1.0
            self.pulse_direction = -1
            self.pulse_count += 1
        elif self.pulse_brightness <= 0.0:
            self.pulse_brightness = 0.0
            self.pulse_direction = 1
        
        # Apply brightness to color (simple on/off for PCF8575)
        # For smoother pulsing, we'd need PWM or rapid switching
        show_color = self.pulse_brightness > 0.5
        if show_color:
            self.set_rgb(self.pulse_color[0], self.pulse_color[1], self.pulse_color[2])
        else:
            self.set_rgb(False, False, False)
        
        # Check if we've completed the requested number of pulses
        if self.pulse_max > 0 and self.pulse_count >= self.pulse_max:
            self.stop_pulse()
            if self.pulse_callback:
                self.pulse_callback()
    
    def start_pulse(self, color, speed=0.1, pulses=-1, callback=None):
        """Start pulsing RGB LED with specified color
        
        Args:
            color: Color to pulse (string or RGB tuple)
            speed: Pulse speed (0.05-0.5, lower = faster)
            pulses: Number of complete pulses (-1 = infinite)
            callback: Function to call when pulsing completes
        """
        if not self.has_rgb or not self.has_expander:
            return
        
        # Stop any existing pulse
        self.stop_pulse()
        
        # Parse color
        if isinstance(color, str):
            colors = {
                'red': (True, False, False),
                'green': (False, True, False), 
                'blue': (False, False, True),
                'yellow': (True, True, False),
                'magenta': (True, False, True),
                'cyan': (False, True, True),
                'white': (True, True, True)
            }
            if color.lower() in colors:
                self.pulse_color = list(colors[color.lower()])
            else:
                self.pulse_color = [True, True, True]  # Default to white
        elif isinstance(color, (list, tuple)) and len(color) >= 3:
            self.pulse_color = [bool(color[0]), bool(color[1]), bool(color[2])]
        else:
            self.pulse_color = [True, True, True]  # Default to white
        
        # Set pulse parameters
        self.pulse_speed = max(0.05, min(0.5, speed))
        self.pulse_max = pulses
        self.pulse_count = 0
        self.pulse_brightness = 0.0
        self.pulse_direction = 1
        self.pulse_callback = callback
        self.pulse_active = True
        
        # Start timer (50ms intervals for smooth animation)
        self.pulse_timer = Timer(-1)
        self.pulse_timer.init(period=50, mode=Timer.PERIODIC, callback=self._pulse_timer_callback)
    
    def stop_pulse(self):
        """Stop RGB LED pulsing"""
        self.pulse_active = False
        if self.pulse_timer:
            self.pulse_timer.deinit()
            self.pulse_timer = None
        # Turn off LED when stopping
        if self.has_rgb:
            self.set_rgb(False, False, False)
    
    def is_pulsing(self):
        """Check if RGB LED is currently pulsing"""
        return self.pulse_active
    
    def pulse_flash(self, color, count=3, on_time=200, off_time=200, callback=None):
        """Flash RGB LED a specific number of times
        
        Args:
            color: Color to flash
            count: Number of flashes
            on_time: Time LED is on (ms)
            off_time: Time LED is off (ms)
            callback: Function to call when flashing completes
        """
        if not self.has_rgb or not self.has_expander:
            return
        
        self.stop_pulse()  # Stop any existing animation
        
        # Parse color
        if isinstance(color, str):
            colors = {
                'red': (True, False, False),
                'green': (False, True, False), 
                'blue': (False, False, True),
                'yellow': (True, True, False),
                'magenta': (True, False, True),
                'cyan': (False, True, True),
                'white': (True, True, True)
            }
            if color.lower() in colors:
                flash_color = colors[color.lower()]
            else:
                flash_color = (True, True, True)
        else:
            flash_color = (True, True, True)
        
        # Flash sequence state
        self.flash_state = {
            'color': flash_color,
            'count': count,
            'remaining': count,
            'on_time': on_time,
            'off_time': off_time,
            'callback': callback,
            'led_on': False,
            'timer': None
        }
        
        # Start flash sequence
        self._flash_step()
    
    def _flash_step(self):
        """Execute one step of the flash sequence"""
        if not hasattr(self, 'flash_state') or self.flash_state['remaining'] <= 0:
            # Flash sequence complete
            if hasattr(self, 'flash_state') and self.flash_state['callback']:
                self.flash_state['callback']()
            return
        
        if self.flash_state['led_on']:
            # Turn LED off
            self.set_rgb(False, False, False)
            self.flash_state['led_on'] = False
            self.flash_state['remaining'] -= 1
            next_time = self.flash_state['off_time']
        else:
            # Turn LED on
            r, g, b = self.flash_state['color']
            self.set_rgb(r, g, b)
            self.flash_state['led_on'] = True
            next_time = self.flash_state['on_time']
        
        # Schedule next step
        if self.flash_state['remaining'] > 0 or self.flash_state['led_on']:
            self.flash_state['timer'] = Timer(-1)
            self.flash_state['timer'].init(
                period=next_time, 
                mode=Timer.ONE_SHOT, 
                callback=lambda t: self._flash_step()
            )


class OLEDController:
    """Combined OLED display and button controller"""
    
    def __init__(self, i2c_bus=0, sda_pin=4, scl_pin=5, 
                 oled_addr=0x3C, button_addr=0x20,
                 width=128, height=64, num_buttons=4, has_rgb=False):
        """
        Initialize OLED controller
        
        Args:
            i2c_bus: I2C bus number (0 or 1) or existing I2C instance
            sda_pin: SDA pin number
            scl_pin: SCL pin number
            oled_addr: I2C address of OLED display
            button_addr: I2C address of button controller
            width: Display width in pixels
            height: Display height in pixels
            num_buttons: Number of buttons
            has_rgb: Whether hardware has RGB LED support (JOLED)
        """
        # Initialize I2C
        if isinstance(i2c_bus, I2C):
            self.i2c = i2c_bus
        else:
            self.i2c = I2C(i2c_bus, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=400000)
        
        # Initialize display
        self.display = SSD1306_I2C(width, height, self.i2c, oled_addr)
        
        # Initialize button controller
        self.buttons = ButtonController(self.i2c, button_addr, num_buttons, has_rgb)
        
        # Initialize font
        self.font = Font5x7()
        
        # Display properties
        self.width = width
        self.height = height
        self.num_buttons = num_buttons
        self.has_rgb = has_rgb
    
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
    
    # RGB LED Methods (JOLED hardware)
    def set_rgb(self, red=False, green=False, blue=False):
        """Set RGB LED colors (JOLED only)"""
        if self.has_rgb:
            self.buttons.set_rgb(red, green, blue)
    
    def rgb_off(self):
        """Turn off RGB LED (JOLED only)"""
        if self.has_rgb:
            self.buttons.rgb_off()
    
    def rgb_color(self, color):
        """Set RGB LED to predefined color (JOLED only)
        
        Available colors: red, green, blue, yellow, magenta, cyan, white, off
        """
        if self.has_rgb:
            self.buttons.rgb_color(color)
    
    def rgb_pulse(self, color, speed=0.1, pulses=-1, callback=None):
        """Start pulsing RGB LED (JOLED only)
        
        Args:
            color: Color to pulse (string or RGB tuple)
            speed: Pulse speed (0.05-0.5, lower = faster)
            pulses: Number of complete pulses (-1 = infinite)
            callback: Function to call when pulsing completes
        """
        if self.has_rgb:
            self.buttons.start_pulse(color, speed, pulses, callback)
    
    def rgb_flash(self, color, count=3, on_time=200, off_time=200, callback=None):
        """Flash RGB LED a specific number of times (JOLED only)
        
        Args:
            color: Color to flash
            count: Number of flashes
            on_time: Time LED is on (ms)
            off_time: Time LED is off (ms)
            callback: Function to call when flashing completes
        """
        if self.has_rgb:
            self.buttons.pulse_flash(color, count, on_time, off_time, callback)
    
    def rgb_stop_animation(self):
        """Stop any RGB LED animation (pulsing/flashing) (JOLED only)"""
        if self.has_rgb:
            self.buttons.stop_pulse()
    
    def rgb_is_animating(self):
        """Check if RGB LED is currently animating (JOLED only)"""
        if self.has_rgb:
            return self.buttons.is_pulsing()
        return False
    
    @staticmethod
    def create_joled(sda_pin=6, scl_pin=7):
        """Create OLEDController configured for JOLED hardware"""
        return OLEDController(
            sda_pin=sda_pin,
            scl_pin=scl_pin,
            num_buttons=8,
            has_rgb=True
        )