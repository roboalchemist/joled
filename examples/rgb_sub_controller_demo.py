# RGB Sub-Controller Demo - Using rgb as a sub-element

from oled_controller import OLEDController, RGBController
import time

def main():
    # Initialize JOLED controller
    controller = OLEDController.create()
    
    print("RGB Sub-Controller Demo")
    print("RGB is accessible as controller.rgb")
    
    # Demo 1: Direct RGB sub-controller access
    controller.clear()
    controller.center_text("RGB Sub-Controller", 10)
    controller.center_text("Demo", 25)
    controller.show()
    
    # Access RGB as a sub-element
    rgb = controller.rgb
    
    if rgb:
        # Test basic colors
        colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white']
        
        for color in colors:
            controller.clear()
            controller.center_text("Direct RGB Access", 0)
            controller.center_text(f"rgb.color('{color}')", 20)
            controller.center_text(color.upper(), 35)
            controller.show()
            
            # Use RGB sub-controller directly
            rgb.color(color)
            time.sleep(1)
        
        # Turn off
        rgb.off()
        time.sleep(0.5)
        
        # Demo 2: RGB pulsing with sub-controller
        controller.clear()
        controller.center_text("RGB Pulsing", 15)
        controller.center_text("rgb.pulse()", 30)
        controller.show()
        
        def pulse_done():
            print("Pulse completed via callback!")
        
        # Direct pulse call on sub-controller
        rgb.pulse('blue', speed=0.08, count=3, callback=pulse_done)
        
        # Wait for pulsing to complete
        while rgb.is_pulsing():
            time.sleep(0.1)
        
        time.sleep(1)
        
        # Demo 3: RGB flashing with sub-controller  
        controller.clear()
        controller.center_text("RGB Flashing", 15)
        controller.center_text("rgb.flash()", 30)
        controller.show()
        
        def flash_done():
            print("Flash completed via callback!")
        
        # Direct flash call on sub-controller
        rgb.flash('red', count=5, on_time=150, off_time=100, callback=flash_done)
        
        time.sleep(3)
        
        # Demo 4: Manual RGB control with individual colors
        controller.clear()
        controller.center_text("Manual RGB", 10)
        controller.center_text("Individual Colors", 25)
        controller.show()
        
        # Set individual RGB components
        rgb.set(red=True, green=False, blue=False)  # Red only
        time.sleep(1)
        
        rgb.set(red=True, green=True, blue=False)   # Red + Green = Yellow
        time.sleep(1)
        
        rgb.set(red=False, green=True, blue=True)   # Green + Blue = Cyan
        time.sleep(1)
        
        rgb.set(red=True, green=True, blue=True)    # All = White
        time.sleep(1)
        
        rgb.off()  # Turn off
        
        # Demo 5: Interactive RGB control
        controller.clear()
        controller.center_text("Interactive RGB", 0)
        controller.text("Up: Pulse red", 0, 15)
        controller.text("Down: Flash blue", 0, 25)
        controller.text("Left: Set green", 0, 35)
        controller.text("Right: RGB off", 0, 45)
        controller.text("Center: Exit", 0, 55)
        controller.show()
        
        print("Interactive mode:")
        print("  Up: Pulse red")
        print("  Down: Flash blue")
        print("  Left: Set green")
        print("  Right: RGB off")
        print("  Center: Exit")
        
        while True:
            controller.update_buttons()
            
            if controller.button_just_pressed(6):  # Up
                rgb.stop_animation()
                rgb.pulse('red', speed=0.1, count=-1)
                
            elif controller.button_just_pressed(4):  # Down
                rgb.stop_animation()
                rgb.flash('blue', count=10, on_time=100, off_time=100)
                
            elif controller.button_just_pressed(5):  # Left
                rgb.stop_animation()
                rgb.color('green')
                
            elif controller.button_just_pressed(3):  # Right
                rgb.stop_animation()
                rgb.off()
                
            elif controller.button_just_pressed(7):  # Center
                rgb.stop_animation()
                break
            
            # Update display with current RGB state
            controller.clear()
            controller.center_text("Interactive RGB", 0)
            
            if rgb.is_animating():
                controller.center_text("RGB: ANIMATING", 20)
            else:
                controller.center_text("RGB: STATIC", 20)
            
            controller.text("Try the buttons above", 0, 35)
            controller.text("Center to exit", 0, 45)
            controller.show()
            
            time.sleep(0.05)
    
    else:
        controller.clear()
        controller.center_text("RGB Controller", 15)
        controller.center_text("Not Available", 30)
        controller.show()
        time.sleep(3)
    
    # Final cleanup
    controller.clear()
    controller.center_text("RGB Sub-Controller", 15)
    controller.center_text("Demo Complete!", 30)
    controller.show()

def standalone_rgb_demo():
    """Demo showing standalone RGBController usage"""
    from machine import I2C, Pin
    
    print("Standalone RGB Controller Demo")
    
    # Create I2C bus
    i2c = I2C(0, sda=Pin(6), scl=Pin(7), freq=400000)
    
    # Create standalone RGB controller
    rgb = RGBController(i2c, addr=0x20)
    
    if rgb.has_expander:
        print("Standalone RGB controller initialized")
        
        # Test colors
        colors = ['red', 'green', 'blue', 'white']
        for color in colors:
            print(f"Setting color: {color}")
            rgb.color(color)
            time.sleep(1)
        
        # Test pulsing
        print("Pulsing cyan...")
        rgb.pulse('cyan', speed=0.1, count=3)
        
        while rgb.is_pulsing():
            time.sleep(0.1)
        
        print("Standalone demo complete")
    else:
        print("RGB controller not available")

if __name__ == "__main__":
    # Run main demo
    main()
    
    # Uncomment to run standalone demo
    # standalone_rgb_demo()