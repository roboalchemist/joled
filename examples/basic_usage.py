# Basic OLED Controller Usage Example

from oled_controller import OLEDController
import time

def main():
    # Initialize controller with default settings
    # OLED at 0x3C, buttons at 0x20, 128x64 display
    controller = OLEDController()
    
    print("OLED Controller Basic Usage Example")
    print("Scanning I2C bus...")
    controller.scan_i2c()
    
    # Clear display and show welcome message
    controller.clear()
    controller.center_text("MicroPython", 10)
    controller.center_text("OLED Library", 25)
    controller.center_text("v1.0.0", 40)
    controller.show()
    time.sleep(3)
    
    # Text positioning example
    controller.clear()
    controller.text("Top Left", 0, 0)
    controller.text("Bottom", 0, 57)
    controller.center_text("Centered", 30)
    controller.show()
    time.sleep(2)
    
    # Graphics examples
    controller.clear()
    controller.text("Graphics Demo", 0, 0)
    
    # Draw border
    controller.rect(0, 10, 128, 54)
    
    # Draw some shapes
    controller.fill_rect(5, 15, 20, 10)
    controller.line(30, 15, 50, 25)
    controller.rect(55, 15, 15, 10)
    
    # Draw pixels
    for x in range(75, 85):
        for y in range(15, 25):
            if (x + y) % 2:
                controller.pixel(x, y)
    
    controller.show()
    time.sleep(3)
    
    # Font character demonstration
    controller.clear()
    controller.text("Font Test:", 0, 0)
    controller.text("ABCDEFGHIJKLM", 0, 10)
    controller.text("nopqrstuvwxyz", 0, 20)
    controller.text("0123456789", 0, 30)
    controller.text("!@#$%^&*()", 0, 40)
    controller.text("Äöü €→← °C", 0, 50)
    controller.show()
    time.sleep(3)
    
    # Contrast demonstration
    for contrast in [50, 100, 150, 200, 255]:
        controller.clear()
        controller.text(f"Contrast: {contrast}", 0, 20)
        controller.center_text("Brightness Test", 35)
        controller.contrast(contrast)
        controller.show()
        time.sleep(1)
    
    # Display inversion
    controller.clear()
    controller.center_text("Normal Display", 25)
    controller.show()
    time.sleep(2)
    
    controller.invert(True)
    controller.clear()
    controller.center_text("Inverted Display", 25)
    controller.show()
    time.sleep(2)
    
    controller.invert(False)
    controller.clear()
    controller.center_text("Demo Complete!", 25)
    controller.show()

if __name__ == "__main__":
    main()