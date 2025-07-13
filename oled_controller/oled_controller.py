# Main OLED Controller Library
# Supports I2C OLED displays and button input

import time
from machine import Pin, I2C, Timer
from micropython import const
from .font5x7 import Font5x7

# SSD1306 Commands (defined at module level for const to work)
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


class DisplayController:
    """OLED display controller with graphics and text rendering"""
    
    def __init__(self, i2c, width=128, height=64, addr=0x3C, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.font = Font5x7()
        
        # Initialize display
        self.temp = bytearray(2)
        self._poweron()
        self._init_display()
    
    def _init_display(self):
        """Initialize the SSD1306 display"""
        
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
            self._write_cmd(cmd)
        self.fill(0)
        self.show()
    
    def _poweron(self):
        """Power on the display"""
        pass
    
    def poweroff(self):
        """Power off the display"""
        self._write_cmd(SET_DISP | 0x00)
    
    def contrast(self, contrast):
        """Set display contrast (0-255)"""
        self._write_cmd(SET_CONTRAST)
        self._write_cmd(contrast)
    
    def invert(self, invert):
        """Invert display colors"""
        self._write_cmd(SET_NORM_INV | (invert & 1))
    
    def show(self):
        """Update the display with buffer contents"""
        
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self._write_cmd(SET_COL_ADDR)
        self._write_cmd(x0)
        self._write_cmd(x1)
        self._write_cmd(SET_PAGE_ADDR)
        self._write_cmd(0)
        self._write_cmd(self.pages - 1)
        self._write_data(self.buffer)
    
    def fill(self, color):
        """Fill entire display with color (0 or 1)"""
        fill_byte = 0xFF if color else 0x00
        for i in range(len(self.buffer)):
            self.buffer[i] = fill_byte
    
    def clear(self):
        """Clear the display"""
        self.fill(0)
    
    def pixel(self, x, y, color):
        """Set a pixel at (x, y) to color"""
        if 0 <= x < self.width and 0 <= y < self.height:
            index = x + (y // 8) * self.width
            if color:
                self.buffer[index] |= 1 << (y & 7)
            else:
                self.buffer[index] &= ~(1 << (y & 7))
    
    def line(self, x0, y0, x1, y1, color):
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
            self.pixel(x, y, color)
            if error > 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx
    
    def rect(self, x, y, w, h, color):
        """Draw rectangle outline"""
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)
    
    def fill_rect(self, x, y, w, h, color):
        """Draw filled rectangle"""
        for i in range(x, x + w):
            self.vline(i, y, h, color)
    
    def hline(self, x, y, w, color):
        """Draw horizontal line"""
        for i in range(w):
            self.pixel(x + i, y, color)
    
    def vline(self, x, y, h, color):
        """Draw vertical line"""
        for i in range(h):
            self.pixel(x, y + i, color)
    
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
                        self.pixel(cursor_x + col, y + row, color)
            
            cursor_x += self.font.width + 1  # +1 for spacing
    
    def text_width(self, text):
        """Calculate text width in pixels"""
        return self.font.text_width(text)
    
    def center_text(self, text, y, color=1):
        """Draw text centered horizontally"""
        text_w = self.text_width(text)
        x = (self.width - text_w) // 2
        self.text(text, x, y, color)
    
    def _write_cmd(self, cmd):
        """Write command to display"""
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)
    
    def _write_data(self, buf):
        """Write data to display"""
        self.i2c.writeto(self.addr, b'\x40' + buf)


class ButtonController:
    """Button input controller for I2C GPIO expanders"""
    
    def __init__(self, i2c, addr=0x20, num_buttons=4, is_joled=False):
        self.i2c = i2c
        self.addr = addr
        self.num_buttons = num_buttons
        self.button_states = [False] * num_buttons
        self.last_states = [False] * num_buttons
        self.is_joled = is_joled
        self.has_expander = False
        
        # Initialize GPIO expander if present
        try:
            if self.is_joled:
                # JOLED uses 16-bit PCF8575
                self.i2c.readfrom(self.addr, 2)
            else:
                # Generic uses 8-bit expander
                self.i2c.readfrom(self.addr, 1)
            self.has_expander = True
        except:
            print("Warning: Button controller not found at address", hex(self.addr))
    
    def _read_gpio(self):
        """Read GPIO state from expander"""
        if not self.has_expander:
            return 0
        try:
            if self.is_joled:
                # Read 16-bit value from PCF8575
                data = self.i2c.readfrom(self.addr, 2)
                return data[0] | (data[1] << 8)
            else:
                # Read 8-bit value from generic expander
                return self.i2c.readfrom(self.addr, 1)[0]
        except:
            return 0
    
    def update(self):
        """Update button states"""
        if not self.has_expander:
            return
        
        data = self._read_gpio()
        self.last_states = self.button_states.copy()
        
        for i in range(self.num_buttons):
            if self.is_joled:
                # JOLED buttons are active high (pulled low, high when pressed)
                self.button_states[i] = bool(data & (1 << i))
            else:
                # Generic buttons are active low (pulled high, low when pressed)
                self.button_states[i] = not bool(data & (1 << i))
    
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
    
    def get_pressed_buttons(self):
        """Get list of currently pressed button numbers"""
        return [i for i in range(self.num_buttons) if self.button_states[i]]
    
    def get_just_pressed_buttons(self):
        """Get list of buttons that were just pressed"""
        return [i for i in range(self.num_buttons) if self.was_pressed(i)]


class RGBController:
    """RGB LED controller for JOLED hardware with animation support"""
    
    def __init__(self, i2c, addr=0x20):
        self.i2c = i2c
        self.addr = addr
        self.has_expander = False
        self.rgb_state = 0x0700  # Default: LEDs off (active low)
        
        # Animation state
        self.pulse_timer = None
        self.pulse_active = False
        self.pulse_color = [False, False, False]  # [R, G, B]
        self.pulse_brightness = 0.0
        self.pulse_direction = 1
        self.pulse_speed = 0.1
        self.pulse_callback = None
        self.pulse_count = 0
        self.pulse_max = -1  # -1 = infinite
        
        # Check if expander is available
        try:
            self.i2c.readfrom(self.addr, 2)
            self.has_expander = True
            self._init_rgb()
        except:
            print("Warning: RGB controller not available at address", hex(self.addr))
    
    def _init_rgb(self):
        """Initialize RGB LED with baseline state"""
        if self.has_expander:
            self._write_gpio(0x0700)  # LEDs off (active low)
    
    def _write_gpio(self, value):
        """Write 16-bit value to PCF8575"""
        if not self.has_expander:
            return
        try:
            low_byte = value & 0xFF
            high_byte = (value >> 8) & 0xFF
            self.i2c.writeto(self.addr, bytes([low_byte, high_byte]))
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
    
    def set(self, red=False, green=False, blue=False):
        """Set RGB LED colors
        
        Args:
            red: Red LED state (True=on, False=off)
            green: Green LED state (True=on, False=off)  
            blue: Blue LED state (True=on, False=off)
        """
        if not self.has_expander:
            return
        
        # LEDs are active low on P8, P9, P10
        # Keep button state (lower 8 bits), modify LED bits
        new_state = self.rgb_state & 0x00FF
        
        # Set LED bits (active low: 0 = on, 1 = off)
        if not red:
            new_state |= (1 << 8)   # P8 high = red off
        if not green:
            new_state |= (1 << 9)   # P9 high = green off  
        if not blue:
            new_state |= (1 << 10)  # P10 high = blue off
        
        self._write_gpio(new_state)
    
    def off(self):
        """Turn off all RGB LEDs"""
        self.set(False, False, False)
    
    def color(self, color_name):
        """Set RGB LED to predefined color
        
        Args:
            color_name: Color name (red, green, blue, yellow, magenta, cyan, white, off)
        """
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
        
        if color_name.lower() in colors:
            r, g, b = colors[color_name.lower()]
            self.set(r, g, b)
    
    def _pulse_timer_callback(self, timer):
        """Timer callback for RGB pulsing"""
        if not self.pulse_active:
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
        show_color = self.pulse_brightness > 0.5
        if show_color:
            self.set(self.pulse_color[0], self.pulse_color[1], self.pulse_color[2])
        else:
            self.set(False, False, False)
        
        # Check if we've completed the requested number of pulses
        if self.pulse_max > 0 and self.pulse_count >= self.pulse_max:
            self.stop_pulse()
            if self.pulse_callback:
                self.pulse_callback()
    
    def pulse(self, color, speed=0.1, count=-1, callback=None):
        """Start pulsing RGB LED with specified color
        
        Args:
            color: Color to pulse (string or RGB tuple)
            speed: Pulse speed (0.05-0.5, lower = faster)
            count: Number of complete pulses (-1 = infinite)
            callback: Function to call when pulsing completes
        """
        if not self.has_expander:
            return
        
        # Stop any existing animation
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
        self.pulse_max = count
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
        self.off()
    
    def is_pulsing(self):
        """Check if RGB LED is currently pulsing"""
        return self.pulse_active
    
    def flash(self, color, count=3, on_time=200, off_time=200, callback=None):
        """Flash RGB LED a specific number of times
        
        Args:
            color: Color to flash
            count: Number of flashes
            on_time: Time LED is on (ms)
            off_time: Time LED is off (ms)
            callback: Function to call when flashing completes
        """
        if not self.has_expander:
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
            self.set(False, False, False)
            self.flash_state['led_on'] = False
            self.flash_state['remaining'] -= 1
            next_time = self.flash_state['off_time']
        else:
            # Turn LED on
            r, g, b = self.flash_state['color']
            self.set(r, g, b)
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
    
    def stop_animation(self):
        """Stop any RGB LED animation (pulsing/flashing)"""
        self.stop_pulse()
    
    def is_animating(self):
        """Check if RGB LED is currently animating"""
        return self.is_pulsing()

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
        
        # Initialize display sub-controller
        self.disp = DisplayController(self.i2c, width, height, oled_addr)
        
        # Initialize button sub-controller (JOLED uses same address as RGB)
        is_joled = has_rgb  # JOLED has both buttons and RGB on same PCF8575
        self.btns = ButtonController(self.i2c, button_addr, num_buttons, is_joled)
        
        # Initialize RGB sub-controller (if enabled)
        self.rgb = None
        if has_rgb:
            self.rgb = RGBController(self.i2c, button_addr)
        
        # Display properties
        self.width = width
        self.height = height
        self.num_buttons = num_buttons
        self.has_rgb = has_rgb
    
    # Display Methods - Direct access to display sub-controller
    def clear(self):
        """Clear the display"""
        self.disp.clear()
    
    def show(self):
        """Update the display"""
        self.disp.show()
    
    def pixel(self, x, y, color=1):
        """Set a pixel"""
        self.disp.pixel(x, y, color)
    
    def line(self, x0, y0, x1, y1, color=1):
        """Draw a line"""
        self.disp.line(x0, y0, x1, y1, color)
    
    def rect(self, x, y, w, h, color=1):
        """Draw rectangle outline"""
        self.disp.rect(x, y, w, h, color)
    
    def fill_rect(self, x, y, w, h, color=1):
        """Draw filled rectangle"""
        self.disp.fill_rect(x, y, w, h, color)
    
    def text(self, text, x, y, color=1):
        """Draw text using 5x7 font"""
        self.disp.text(text, x, y, color)
    
    def text_width(self, text):
        """Calculate text width in pixels"""
        return self.disp.text_width(text)
    
    def center_text(self, text, y, color=1):
        """Draw text centered horizontally"""
        self.disp.center_text(text, y, color)
    
    # Button Methods - Direct access to button sub-controller
    def update_buttons(self):
        """Update button states"""
        self.btns.update()
    
    def button_pressed(self, button):
        """Check if button is currently pressed"""
        return self.btns.is_pressed(button)
    
    def button_just_pressed(self, button):
        """Check if button was just pressed"""
        return self.btns.was_pressed(button)
    
    def get_pressed_buttons(self):
        """Get list of currently pressed button numbers"""
        return self.btns.get_pressed_buttons()
    
    def get_just_pressed_buttons(self):
        """Get list of buttons that were just pressed"""
        return self.btns.get_just_pressed_buttons()
    
    # Display Control Methods - Direct access to display sub-controller
    def contrast(self, contrast):
        """Set display contrast (0-255)"""
        self.disp.contrast(contrast)
    
    def invert(self, invert=True):
        """Invert display colors"""
        self.disp.invert(invert)
    
    def poweroff(self):
        """Turn off display"""
        self.disp.poweroff()
    
    def scan_i2c(self):
        """Scan I2C bus for devices"""
        devices = self.i2c.scan()
        print("I2C devices found:")
        for device in devices:
            print(f"  0x{device:02X}")
        return devices
    
    # RGB LED Methods (JOLED hardware) - Direct access to rgb sub-controller
    def set_rgb(self, red=False, green=False, blue=False):
        """Set RGB LED colors (JOLED only)"""
        if self.rgb:
            self.rgb.set(red, green, blue)
    
    def rgb_off(self):
        """Turn off RGB LED (JOLED only)"""
        if self.rgb:
            self.rgb.off()
    
    def rgb_color(self, color):
        """Set RGB LED to predefined color (JOLED only)
        
        Available colors: red, green, blue, yellow, magenta, cyan, white, off
        """
        if self.rgb:
            self.rgb.color(color)
    
    def rgb_pulse(self, color, speed=0.1, count=-1, callback=None):
        """Start pulsing RGB LED (JOLED only)
        
        Args:
            color: Color to pulse (string or RGB tuple)
            speed: Pulse speed (0.05-0.5, lower = faster)
            count: Number of complete pulses (-1 = infinite)
            callback: Function to call when pulsing completes
        """
        if self.rgb:
            self.rgb.pulse(color, speed, count, callback)
    
    def rgb_flash(self, color, count=3, on_time=200, off_time=200, callback=None):
        """Flash RGB LED a specific number of times (JOLED only)
        
        Args:
            color: Color to flash
            count: Number of flashes
            on_time: Time LED is on (ms)
            off_time: Time LED is off (ms)
            callback: Function to call when flashing completes
        """
        if self.rgb:
            self.rgb.flash(color, count, on_time, off_time, callback)
    
    def rgb_stop_animation(self):
        """Stop any RGB LED animation (pulsing/flashing) (JOLED only)"""
        if self.rgb:
            self.rgb.stop_animation()
    
    def rgb_is_animating(self):
        """Check if RGB LED is currently animating (JOLED only)"""
        if self.rgb:
            return self.rgb.is_animating()
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
    
    @staticmethod
    def create(sda_pin=6, scl_pin=7):
        """Create OLEDController configured for JOLED hardware (short form)"""
        return OLEDController(
            sda_pin=sda_pin,
            scl_pin=scl_pin,
            num_buttons=8,
            has_rgb=True
        )