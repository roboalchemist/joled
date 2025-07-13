# JOLED RGB LED Pulsing and Animation Demo

from oled_controller import OLEDController
import time

def pulse_complete_callback():
    """Callback function called when pulsing completes"""
    print("Pulse sequence completed!")

def flash_complete_callback():
    """Callback function called when flashing completes"""
    print("Flash sequence completed!")

def main():
    # Initialize JOLED controller with RGB support
    controller = OLEDController.create()
    
    print("JOLED RGB Pulse Demo Starting...")
    
    # Demo 1: Basic pulsing
    controller.clear()
    controller.center_text("Pulse Demo", 0)
    controller.center_text("Basic Red Pulse", 20)
    controller.center_text("5 seconds", 35)
    controller.show()
    
    # Start red pulsing for 5 seconds
    controller.rgb_pulse('red', speed=0.1, pulses=-1)  # Infinite pulsing
    time.sleep(5)
    controller.rgb_stop_animation()
    
    time.sleep(1)
    
    # Demo 2: Pulse with specific count and callback
    controller.clear()
    controller.center_text("Counted Pulse", 0)
    controller.center_text("Blue - 5 pulses", 20)
    controller.center_text("With callback", 35)
    controller.show()
    
    controller.rgb_pulse('blue', speed=0.08, pulses=5, callback=pulse_complete_callback)
    
    # Wait for pulsing to complete
    while controller.rgb_is_animating():
        time.sleep(0.1)
    
    time.sleep(1)
    
    # Demo 3: Fast vs Slow pulsing
    controller.clear()
    controller.center_text("Speed Demo", 0)
    controller.center_text("Fast Green", 20)
    controller.show()
    
    controller.rgb_pulse('green', speed=0.05, pulses=3)  # Fast
    while controller.rgb_is_animating():
        time.sleep(0.1)
    
    time.sleep(0.5)
    
    controller.clear()
    controller.center_text("Speed Demo", 0)
    controller.center_text("Slow Yellow", 20)
    controller.show()
    
    controller.rgb_pulse('yellow', speed=0.3, pulses=3)  # Slow
    while controller.rgb_is_animating():
        time.sleep(0.1)
    
    time.sleep(1)
    
    # Demo 4: Flashing patterns
    controller.clear()
    controller.center_text("Flash Demo", 0)
    controller.center_text("Quick Red Flash", 20)
    controller.show()
    
    controller.rgb_flash('red', count=5, on_time=100, off_time=100, callback=flash_complete_callback)
    time.sleep(2)
    
    controller.clear()
    controller.center_text("Flash Demo", 0)
    controller.center_text("Slow White Flash", 20)
    controller.show()
    
    controller.rgb_flash('white', count=3, on_time=500, off_time=300)
    time.sleep(3)
    
    # Demo 5: Interactive control
    controller.clear()
    controller.center_text("Interactive Mode", 0)
    controller.text("Controls:", 0, 15)
    controller.text("Up: Start red pulse", 0, 25)
    controller.text("Down: Start blue flash", 0, 35)
    controller.text("Left: Stop animation", 0, 45)
    controller.text("Center: Exit demo", 0, 55)
    controller.show()
    
    print("Interactive mode - use JOLED buttons:")
    print("  Up: Start red pulsing")
    print("  Down: Start blue flashing")
    print("  Left: Stop any animation")
    print("  Center: Exit demo")
    
    while True:
        controller.update_buttons()
        
        if controller.button_just_pressed(6):  # Up
            controller.rgb_stop_animation()
            controller.rgb_pulse('red', speed=0.1, pulses=-1)
            
        elif controller.button_just_pressed(4):  # Down
            controller.rgb_stop_animation()
            controller.rgb_flash('blue', count=10, on_time=150, off_time=150)
            
        elif controller.button_just_pressed(5):  # Left
            controller.rgb_stop_animation()
            
        elif controller.button_just_pressed(7):  # Center
            controller.rgb_stop_animation()
            break
        
        # Update display with current state
        controller.clear()
        controller.center_text("Interactive Mode", 0)
        
        if controller.rgb_is_animating():
            controller.center_text("RGB: ANIMATING", 20)
        else:
            controller.center_text("RGB: IDLE", 20)
        
        controller.text("Up:Pulse Down:Flash", 0, 35)
        controller.text("Left:Stop Center:Exit", 0, 45)
        controller.show()
        
        time.sleep(0.05)
    
    # Demo 6: Color sequence with callbacks
    colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan']
    color_index = 0
    
    def next_color_callback():
        nonlocal color_index
        color_index += 1
        if color_index < len(colors):
            controller.clear()
            controller.center_text("Color Sequence", 0)
            controller.center_text(f"{colors[color_index].upper()}", 20)
            controller.center_text(f"{color_index+1}/{len(colors)}", 35)
            controller.show()
            controller.rgb_pulse(colors[color_index], speed=0.08, pulses=2, callback=next_color_callback)
        else:
            # Sequence complete
            controller.clear()
            controller.center_text("Sequence", 15)
            controller.center_text("Complete!", 30)
            controller.show()
    
    controller.clear()
    controller.center_text("Color Sequence", 0)
    controller.center_text("RED", 20)
    controller.center_text("1/6", 35)
    controller.show()
    
    # Start the sequence
    controller.rgb_pulse(colors[0], speed=0.08, pulses=2, callback=next_color_callback)
    
    # Wait for sequence to complete
    time.sleep(15)  # Should be enough time for all colors
    
    # Final cleanup
    controller.rgb_stop_animation()
    controller.clear()
    controller.center_text("Pulse Demo", 20)
    controller.center_text("Complete!", 35)
    controller.show()

if __name__ == "__main__":
    main()