import pcf8575
import ssd1306
from machine import I2C, Pin
import os
import time

font5x7 = {
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],  # Space
    '!': [0x00, 0x00, 0x1F, 0x00, 0x00],  # !
    '"': [0x00, 0x03, 0x00, 0x03, 0x00],  # "
    '#': [0x0A, 0x1F, 0x0A, 0x1F, 0x0A],  # #
    '$': [0x12, 0x15, 0x1F, 0x15, 0x09],  # $
    '%': [0x19, 0x1D, 0x06, 0x13, 0x13],  # %
    '&': [0x0A, 0x15, 0x1A, 0x10, 0x0A],  # &
    '\'': [0x00, 0x03, 0x00, 0x00, 0x00],  # '
    '(': [0x00, 0x0E, 0x11, 0x00, 0x00],  # (
    ')': [0x00, 0x00, 0x11, 0x0E, 0x00],  # )
    '*': [0x05, 0x02, 0x0F, 0x02, 0x05],  # *
    '+': [0x04, 0x04, 0x1F, 0x04, 0x04],  # +
    ',': [0x00, 0x10, 0x08, 0x00, 0x00],  # ,
    '-': [0x04, 0x04, 0x04, 0x04, 0x04],  # -
    '.': [0x00, 0x10, 0x00, 0x00, 0x00],  # .
    '/': [0x10, 0x0C, 0x03, 0x00, 0x00],  # /
    ':': [0x00, 0x00, 0x0A, 0x00, 0x00],  # :
    ';': [0x00, 0x10, 0x0A, 0x00, 0x00],  # ;
    '<': [0x04, 0x0A, 0x11, 0x00, 0x00],  # <
    '=': [0x0A, 0x0A, 0x0A, 0x0A, 0x00],  # =
    '>': [0x11, 0x0A, 0x04, 0x00, 0x00],  # >
    '?': [0x02, 0x01, 0x15, 0x05, 0x02],  # ?
    '@': [0x0E, 0x15, 0x15, 0x05, 0x02],  # @
    
    '[': [0x00, 0x1F, 0x11, 0x00, 0x00],  # [
    '\\': [0x00, 0x03, 0x0C, 0x10, 0x00], # \
    ']': [0x00, 0x00, 0x11, 0x1F, 0x00],  # ]
    '^': [0x04, 0x02, 0x01, 0x02, 0x04],  # ^
    '_': [0x10, 0x10, 0x10, 0x10, 0x10],  # _
    '`': [0x01, 0x02, 0x00, 0x00, 0x00],  # `


    '0': [0x0E, 0x11, 0x11, 0x11, 0x0E],  # 0
    '1': [0x00, 0x12, 0x1F, 0x10, 0x00],  # 1
    '2': [0x12, 0x19, 0x15, 0x12, 0x00],  # 2
    '3': [0x11, 0x15, 0x15, 0x1F, 0x00],  # 3
    '4': [0x07, 0x04, 0x04, 0x1F, 0x04],  # 4
    '5': [0x17, 0x15, 0x15, 0x15, 0x09],  # 5
    '6': [0x0E, 0x15, 0x15, 0x15, 0x08],  # 6
    '7': [0x01, 0x01, 0x1D, 0x07, 0x01],  # 7
    '8': [0x0A, 0x15, 0x15, 0x15, 0x0A],  # 8
    '9': [0x02, 0x15, 0x15, 0x15, 0x0E],  # 9

    'A': [0x1E, 0x05, 0x05, 0x05, 0x1E],  # A
    'B': [0x1F, 0x15, 0x15, 0x15, 0x0A],  # B
    'C': [0x0E, 0x11, 0x11, 0x11, 0x0A],  # C
    'D': [0x1F, 0x11, 0x11, 0x11, 0x0E],  # D
    'E': [0x1F, 0x15, 0x15, 0x15, 0x11],  # E
    'F': [0x1F, 0x05, 0x05, 0x05, 0x01],  # F
    'G': [0x0E, 0x11, 0x15, 0x15, 0x0D],  # G
    'H': [0x1F, 0x04, 0x04, 0x04, 0x1F],  # H
    'I': [0x00, 0x11, 0x1F, 0x11, 0x00],  # I
    'J': [0x08, 0x10, 0x11, 0x11, 0x0F],  # J
    'K': [0x1F, 0x04, 0x0A, 0x11, 0x00],  # K
    'L': [0x1F, 0x10, 0x10, 0x10, 0x00],  # L
    'M': [0x1F, 0x02, 0x04, 0x02, 0x1F],  # M
    'N': [0x1F, 0x02, 0x04, 0x08, 0x1F],  # N
    'O': [0x0E, 0x11, 0x11, 0x11, 0x0E],  # O
    'P': [0x1F, 0x05, 0x05, 0x05, 0x02],  # P
    'Q': [0x0E, 0x11, 0x19, 0x11, 0x1E],  # Q
    'R': [0x1F, 0x05, 0x0D, 0x15, 0x12],  # R
    'S': [0x12, 0x15, 0x15, 0x15, 0x09],  # S
    'T': [0x01, 0x01, 0x1F, 0x01, 0x01],  # T
    'U': [0x0F, 0x10, 0x10, 0x10, 0x0F],  # U
    'V': [0x07, 0x08, 0x10, 0x08, 0x07],  # V
    'W': [0x0F, 0x10, 0x08, 0x10, 0x0F],  # W
    'X': [0x11, 0x0A, 0x04, 0x0A, 0x11],  # X
    'Y': [0x01, 0x02, 0x1C, 0x02, 0x01],  # Y
    'Z': [0x11, 0x19, 0x15, 0x13, 0x11],  # Z
}

class InterfaceBoard:
    btns = {
        "UP" : 6,
        "DOWN" : 4,
        "LEFT" : 5,
        "RIGHT" : 3,
        "CENTER": 7,
        "B3": 0,
        "B2": 1,
        "B1": 2,
    }

    leds = {
        "RED": 10,
        "GREEN": 11,
        "BLUE": 12,
        }

    def __init__(self, i2c=None):
        # setup i2c for interface
        info = os.uname()
        if i2c is None:
            if "ESP32C3" in info.machine:
                SDA_PIN = 6
                SCL_PIN = 7
            else:
                SDA_PIN = 0
                SCL_PIN = 1

            self.i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))

        else:
            self.i2c = i2c
            
        # setup GPIO
        self.pcf = pcf8575.PCF8575(self.i2c, 0x20)
        self.pcf.port = 0xFF00 # setup high pins as output, low pins as interface
    
        # setup OLED
        self.oled_width = 128
        self.oled_height = 64
        self.oled = ssd1306.SSD1306_I2C(self.oled_width, self.oled_height, self.i2c)
    
        # Dictionary to store button callbacks
        self.button_callbacks = {}
    
    
    def getBtn(self, btn):
        return self.pcf.pin(self.btns[btn])
    
    def register_button_callback(self, btn, callback):
        """
        Register a callback function for a specific button.
        
        :param btn: The button name (e.g., "UP", "DOWN", etc.)
        :param callback: The function to be called when the button is pressed
        """
        if btn not in self.btns:
            raise ValueError(f"Invalid button name: {btn}")
        
        self.button_callbacks[btn] = callback
        
        # Set up an interrupt for the button
        pin_number = self.btns[btn]
        self.pcf.pin(pin_number, mode=self.pcf.IN)
        self.pcf.irq(pin_number, trigger=self.pcf.IRQ_FALLING, handler=lambda p: self._button_handler(btn))

    def _button_handler(self, btn):
        """
        Internal method to handle button presses and call the appropriate callback.
        """
        if btn in self.button_callbacks:
            self.button_callbacks[btn]()

    def readbtns(self):
        for btn in self.btns:
            print(f"{btn}: {self.pcf.pin(self.btns[btn])}")
        print("-"*20)
        

    def draw_small_char(self, char, x, y, c=1):
        """Draw a single 5x7 character at position (x, y) on the OLED display."""
        if char in font5x7:
            char_data = font5x7[char]
            print(f"printing: {font5x7[char]}")
            for col in range(5):  # Each character is 5 pixels wide
                byte = char_data[col]
                
                for row in range(7):  # Each character is 7 pixels tall
                    # Draw pixel if the corresponding bit in the byte is set
                    if byte & (1 << row):
                        self.oled.pixel(x + col, y + row, c)
             
             
    def sprint(self, text, x, y, c=1):
        """Draw a string of text on the OLED display starting at position (x, y) with the specified color."""
        for i, char in enumerate(text.upper()):
            self.draw_small_char(char, x + i * 6, y, c)  # Move 6 pixels to the right for each character (5 for width + 1 for spacing)
                 
    # Helper function to determine if a point is inside a triangle
    def point_in_triangle(self, px, py, x0, y0, x1, y1, x2, y2):
        dX = px - x2
        dY = py - y2
        dX21 = x2 - x1
        dY12 = y1 - y2
        D = dY12 * (x0 - x2) + dX21 * (y0 - y2)
        s = dY12 * dX + dX21 * dY
        t = (y2 - y0) * dX + (x0 - x2) * dY
        return (D < 0 and s <= 0 and t <= 0 and s + t >= D) or (D > 0 and s >= 0 and t >= 0 and s + t <= D)
            
    # Custom function to draw a triangle
    def draw_triangle(self, x0, y0, x1, y1, x2, y2, c):
        self.oled.line(x0, y0, x1, y1, c)
        self.oled.line(x1, y1, x2, y2, c)
        self.oled.line(x2, y2, x0, y0, c)

    # Custom function to fill a triangle
    def fill_triangle(self, x0, y0, x1, y1, x2, y2, c):
        min_x = min(x0, x1, x2)
        max_x = max(x0, x1, x2)
        for x in range(min_x, max_x + 1):
            min_y = min(y0, y1, y2)
            max_y = max(y0, y1, y2)
            for y in range(min_y, max_y + 1):
                if self.point_in_triangle(x, y, x0, y0, x1, y1, x2, y2):
                    self.oled.pixel(x, y, c)
    
    # Custom function to draw a circle
    def draw_circle(self, x0, y0, r, c):
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r
        self.oled.pixel(x0, y0 + r, c)
        self.oled.pixel(x0, y0 - r, c)
        self.oled.pixel(x0 + r, y0, c)
        self.oled.pixel(x0 - r, y0, c)
        while x < y:
            if f >= 0:
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x
            self.oled.pixel(x0 + x, y0 + y, c)
            self.oled.pixel(x0 - x, y0 + y, c)
            self.oled.pixel(x0 + x, y0 - y, c)
            self.oled.pixel(x0 - x, y0 - y, c)
            self.oled.pixel(x0 + y, y0 + x, c)
            self.oled.pixel(x0 - y, y0 + x, c)
            self.oled.pixel(x0 + y, y0 - x, c)
            self.oled.pixel(x0 - y, y0 - x, c)

    # Custom function to fill a circle
    def fill_circle(self, x0, y0, r, c):
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                if x * x + y * y <= r * r:
                    self.oled.pixel(x0 + x, y0 + y, c)

    def set_led(self, R=0, G=0, B=0):
        self.pcf.pin(self.leds["RED"], R)
        self.pcf.pin(self.leds["GREEN"], G)
        self.pcf.pin(self.leds["BLUE"], B)
        
    def clear(self, fill=0):
        self.oled.fill(fill)
        
    def show(self):
        self.oled.show()
        
            

    
