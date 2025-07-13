# Sub-Controllers Demo - Using display, buttons, and rgb as sub-elements

from oled_controller import OLEDController, DisplayController, ButtonController, RGBController
import time

def main():
    # Initialize JOLED controller
    controller = OLEDController.create_joled()
    
    print("Sub-Controllers Demo")
    print("Access via: controller.display, controller.buttons, controller.rgb")
    
    # Get references to sub-controllers
    display = controller.display
    buttons = controller.buttons
    rgb = controller.rgb
    
    # Demo 1: Display sub-controller
    display.clear()
    display.center_text("Display Demo", 10)
    display.center_text("Sub-Controller", 25)
    display.show()
    time.sleep(2)
    
    # Graphics via display sub-controller
    display.clear()
    display.text("Graphics Demo:", 0, 0)
    display.line(0, 10, 127, 10)  # Horizontal line
    display.rect(10, 15, 30, 20)  # Rectangle
    display.fill_rect(50, 20, 20, 15)  # Filled rectangle
    display.pixel(80, 25, 1)  # Single pixel
    display.show()
    time.sleep(2)
    
    # Demo 2: Button sub-controller
    display.clear()
    display.center_text("Button Demo", 10)
    display.center_text("Press buttons", 25)
    display.show()
    
    print("Button demo - press some buttons...")
    start_time = time.time()
    while time.time() - start_time < 5:
        buttons.update()
        
        # Get all pressed buttons at once
        pressed = buttons.get_pressed_buttons()
        just_pressed = buttons.get_just_pressed_buttons()
        
        display.clear()
        display.text("Pressed:", 0, 0)
        display.text(str(pressed), 0, 10)
        display.text("Just pressed:", 0, 25)
        display.text(str(just_pressed), 0, 35)
        
        # Individual button checks
        for i in range(8):
            if buttons.is_pressed(i):
                display.text(f"B{i}", 10 + i*10, 50)
        
        display.show()
        time.sleep(0.05)
    
    # Demo 3: RGB sub-controller
    if rgb:
        display.clear()
        display.center_text("RGB Demo", 10)
        display.center_text("Color Sequence", 25)
        display.show()
        
        colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white']
        for color in colors:
            display.clear()
            display.center_text("RGB Demo", 0)
            display.center_text(f"Color: {color.upper()}", 20)
            display.show()
            
            rgb.color(color)
            time.sleep(1)
        
        rgb.off()
        
        # RGB pulsing demo
        display.clear()
        display.center_text("RGB Pulsing", 15)
        display.center_text("Blue x3", 30)
        display.show()
        
        def pulse_done():
            print("RGB pulsing completed!")
        
        rgb.pulse('blue', speed=0.08, count=3, callback=pulse_done)
        
        while rgb.is_pulsing():
            time.sleep(0.1)
    
    # Demo 4: Interactive mode using all sub-controllers
    display.clear()
    display.center_text("Interactive Demo", 0)
    display.text("Up: Display test", 0, 15)
    display.text("Down: RGB pulse", 0, 25)
    display.text("Left: RGB flash", 0, 35)
    display.text("Right: RGB color", 0, 45)
    display.text("Center: Exit", 0, 55)
    display.show()
    
    print("Interactive mode:")
    print("  Up: Display test")
    print("  Down: RGB pulse") 
    print("  Left: RGB flash")
    print("  Right: RGB color")
    print("  Center: Exit")
    
    color_index = 0
    colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white']
    
    while True:
        buttons.update()
        
        if buttons.was_pressed(6):  # Up - Display test
            for i in range(5):
                display.clear()
                display.center_text("Display Test", 10)
                display.center_text(f"Frame {i+1}/5", 30)
                display.rect(20 + i*5, 40, 10, 10)
                display.show()
                time.sleep(0.5)
            
        elif buttons.was_pressed(4):  # Down - RGB pulse
            if rgb:
                rgb.pulse('blue', speed=0.1, count=2)
                
        elif buttons.was_pressed(5):  # Left - RGB flash
            if rgb:
                rgb.flash('red', count=3, on_time=100, off_time=100)
                
        elif buttons.was_pressed(3):  # Right - RGB color cycle
            if rgb:
                rgb.color(colors[color_index])
                color_index = (color_index + 1) % len(colors)
                
        elif buttons.was_pressed(7):  # Center - Exit
            break
        
        # Update display with current state
        display.clear()
        display.center_text("Interactive Demo", 0)
        
        # Show pressed buttons
        pressed = buttons.get_pressed_buttons()
        if pressed:
            display.text(f"Pressed: {pressed}", 0, 15)
        
        # Show RGB state
        if rgb:
            if rgb.is_animating():
                display.text("RGB: Animating", 0, 25)
            else:
                display.text("RGB: Static", 0, 25)
        
        display.text("Try buttons above", 0, 40)
        display.text("Center to exit", 0, 50)
        display.show()
        
        time.sleep(0.05)
    
    # Final cleanup
    display.clear()
    display.center_text("Sub-Controllers", 15)
    display.center_text("Demo Complete!", 30)
    display.show()
    
    if rgb:
        rgb.off()

def standalone_demo():
    """Demo showing standalone sub-controller usage"""
    from machine import I2C, Pin
    
    print("Standalone Sub-Controllers Demo")
    
    # Create I2C bus
    i2c = I2C(0, sda=Pin(6), scl=Pin(7), freq=400000)
    
    # Create standalone controllers
    display = DisplayController(i2c, width=128, height=64, addr=0x3C)
    buttons = ButtonController(i2c, addr=0x20, num_buttons=8, is_joled=True)
    rgb = RGBController(i2c, addr=0x20)
    
    print("Standalone controllers initialized")
    
    # Test display
    display.clear()
    display.center_text("Standalone", 10)
    display.center_text("Controllers", 30)
    display.show()
    time.sleep(2)
    
    # Test RGB
    if rgb.has_expander:
        colors = ['red', 'green', 'blue']
        for color in colors:
            display.clear()
            display.center_text(f"RGB: {color.upper()}", 20)
            display.show()
            rgb.color(color)
            time.sleep(1)
        rgb.off()
    
    # Test buttons
    display.clear()
    display.center_text("Press buttons", 15)
    display.center_text("for 3 seconds", 30)
    display.show()
    
    start_time = time.time()
    while time.time() - start_time < 3:
        buttons.update()
        pressed = buttons.get_pressed_buttons()
        if pressed:
            print(f"Standalone buttons pressed: {pressed}")
        time.sleep(0.1)
    
    display.clear()
    display.center_text("Standalone Demo", 15)
    display.center_text("Complete!", 30)
    display.show()
    time.sleep(2)

if __name__ == "__main__":
    # Run main demo
    main()
    
    # Uncomment to run standalone demo
    # standalone_demo()