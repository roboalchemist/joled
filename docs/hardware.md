SCL - Pin 7
SDA - Pin 6

joled follows the QWIIC standard: https://www.sparkfun.com/qwiic

There is a 128x64 ssd1306 OLED Display (400khz) on the i2c ports.

There is a PCF8575 port expander on the i2c port (400khz) at address 0x20. There are several devices on the port expander.
There is a 5 way Dpad (pins pulled low, high when depressed):
Up - P6
Down - P4
Left - P5
Right - P3
Center - P7

3 Buttons (pins pulled low, high when depressed):
B1 - P2
B2 - P1
B3 - P0

There is an RGB LED on the ports as well. The color LEDs are active low.
Red - P8
Green - P9
Blue - P10

Writing 0x0007 first establishes the proper baseline state. Buttons are low, but LEDs are pulled high (we don't want them on at the start, and they are active low)


JOLED Controller:
        ------------------------------------------
        |                              [RGB]     |
[qwiic]<|    ----------------        U           |>[qwiic]
        |    |    128x64    |     L  C  R        |
        |    | SSD1306 OLED |        D           |
[qwiic]<|    ----------------                    |>[qwiic]
        |                       B1   B2  B3      |
        ------------------------------------------

