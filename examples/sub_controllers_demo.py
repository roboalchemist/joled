# Sub-Controllers Demo - Using disp, btns, and rgb as sub-elements

from oled_controller import OLEDController, DisplayController, ButtonController, RGBController
import time

def main():
    # Initialize JOLED controller
    controller = OLEDController.create_joled()
    
    print("Sub-Controllers Demo")
    print("Access via: controller.disp, controller.btns, controller.rgb")
    
    # Get references to sub-controllers
    disp = controller.disp
    btns = controller.btns
    rgb = controller.rgb
    
    # Demo 1: Display sub-controller
    disp.clear()
    disp.center_text("Display Demo", 10)
    disp.center_text("Sub-Controller", 25)
    disp.show()
    time.sleep(2)
    
    # Graphics via display sub-controller
    disp.clear()
    disp.text("Graphics Demo:", 0, 0)
    disp.line(0, 10, 127, 10)  # Horizontal line
    disp.rect(10, 15, 30, 20)  # Rectangle
    disp.fill_rect(50, 20, 20, 15)  # Filled rectangle
    disp.pixel(80, 25, 1)  # Single pixel
    disp.show()
    time.sleep(2)
    
    # Demo 2: Button sub-controller
    disp.clear()
    disp.center_text("Button Demo", 10)
    disp.center_text("Press buttons", 25)
    disp.show()
    
    print("Button demo - press some buttons...")
    start_time = time.time()
    while time.time() - start_time < 5:
        btns.update()
        
        # Get all pressed buttons at once
        pressed = btns.get_pressed_buttons()
        just_pressed = btns.get_just_pressed_buttons()
        
        disp.clear()
        disp.text("Pressed:", 0, 0)
        disp.text(str(pressed), 0, 10)
        disp.text("Just pressed:", 0, 25)
        disp.text(str(just_pressed), 0, 35)
        
        # Individual button checks
        for i in range(8):
            if btns.is_pressed(i):
                disp.text(f"B{i}", 10 + i*10, 50)
        
        disp.show()
        time.sleep(0.05)
    
    # Demo 3: RGB sub-controller
    if rgb:
        disp.clear()
        disp.center_text("RGB Demo", 10)
        disp.center_text("Color Sequence", 25)
        disp.show()
        
        colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white']
        for color in colors:
            disp.clear()
            disp.center_text("RGB Demo", 0)
            disp.center_text(f"Color: {color.upper()}", 20)
            disp.show()
            
            rgb.color(color)
            time.sleep(1)
        
        rgb.off()
        
        # RGB pulsing demo
        disp.clear()
        disp.center_text("RGB Pulsing", 15)
        disp.center_text("Blue x3", 30)
        disp.show()
        
        def pulse_done():
            print("RGB pulsing completed!")
        
        rgb.pulse('blue', speed=0.08, count=3, callback=pulse_done)
        
        while rgb.is_pulsing():
            time.sleep(0.1)
    
    # Demo 4: Interactive mode using all sub-controllers
    disp.clear()
    disp.center_text("Interactive Demo", 0)
    disp.text("Up: Display test", 0, 15)
    disp.text("Down: RGB pulse", 0, 25)
    disp.text("Left: RGB flash", 0, 35)
    disp.text("Right: RGB color", 0, 45)
    disp.text("Center: Exit", 0, 55)
    disp.show()
    
    print("Interactive mode:")
    print("  Up: Display test")
    print("  Down: RGB pulse") 
    print("  Left: RGB flash")
    print("  Right: RGB color")
    print("  Center: Exit")
    
    color_index = 0
    colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white']
    
    while True:
        btns.update()
        
        if btns.was_pressed(6):  # Up - Display test
            for i in range(5):
                disp.clear()
                disp.center_text("Display Test", 10)
                disp.center_text(f"Frame {i+1}/5", 30)
                disp.rect(20 + i*5, 40, 10, 10)
                disp.show()
                time.sleep(0.5)
            
        elif btns.was_pressed(4):  # Down - RGB pulse
            if rgb:
                rgb.pulse('blue', speed=0.1, count=2)
                
        elif btns.was_pressed(5):  # Left - RGB flash
            if rgb:
                rgb.flash('red', count=3, on_time=100, off_time=100)
                
        elif btns.was_pressed(3):  # Right - RGB color cycle
            if rgb:
                rgb.color(colors[color_index])
                color_index = (color_index + 1) % len(colors)
                
        elif btns.was_pressed(7):  # Center - Exit
            break
        
        # Update display with current state
        disp.clear()
        disp.center_text("Interactive Demo", 0)
        
        # Show pressed buttons
        pressed = btns.get_pressed_buttons()
        if pressed:
            disp.text(f"Pressed: {pressed}", 0, 15)
        
        # Show RGB state
        if rgb:
            if rgb.is_animating():
                disp.text("RGB: Animating", 0, 25)
            else:
                disp.text("RGB: Static", 0, 25)
        
        disp.text("Try buttons above", 0, 40)
        disp.text("Center to exit", 0, 50)
        disp.show()
        
        time.sleep(0.05)
    
    # Final cleanup
    disp.clear()
    disp.center_text("Sub-Controllers", 15)
    disp.center_text("Demo Complete!", 30)
    disp.show()
    
    if rgb:
        rgb.off()

def standalone_demo():
    """Demo showing standalone sub-controller usage"""
    from machine import I2C, Pin
    
    print("Standalone Sub-Controllers Demo")
    
    # Create I2C bus
    i2c = I2C(0, sda=Pin(6), scl=Pin(7), freq=400000)
    
    # Create standalone controllers
    disp = DisplayController(i2c, width=128, height=64, addr=0x3C)
    btns = ButtonController(i2c, addr=0x20, num_buttons=8, is_joled=True)
    rgb = RGBController(i2c, addr=0x20)
    
    print("Standalone controllers initialized")
    
    # Test display
    disp.clear()
    disp.center_text("Standalone", 10)
    disp.center_text("Controllers", 30)
    disp.show()
    time.sleep(2)
    
    # Test RGB
    if rgb.has_expander:
        colors = ['red', 'green', 'blue']
        for color in colors:
            disp.clear()
            disp.center_text(f"RGB: {color.upper()}", 20)
            disp.show()
            rgb.color(color)
            time.sleep(1)
        rgb.off()
    
    # Test buttons
    disp.clear()
    disp.center_text("Press buttons", 15)
    disp.center_text("for 3 seconds", 30)
    disp.show()
    
    start_time = time.time()
    while time.time() - start_time < 3:
        btns.update()
        pressed = btns.get_pressed_buttons()
        if pressed:
            print(f"Standalone buttons pressed: {pressed}")
        time.sleep(0.1)
    
    disp.clear()
    disp.center_text("Standalone Demo", 15)
    disp.center_text("Complete!", 30)
    disp.show()
    time.sleep(2)

if __name__ == "__main__":
    # Run main demo
    main()
    
    # Uncomment to run standalone demo
    # standalone_demo()