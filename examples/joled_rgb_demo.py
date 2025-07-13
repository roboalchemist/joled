# JOLED RGB LED Demo Example

from oled_controller import OLEDController
import time

def main():
    # Initialize JOLED controller with RGB support
    controller = OLEDController.create_joled()
    
    print("JOLED RGB LED Demo Starting...")
    print("Press buttons to change LED colors!")
    
    # Available colors
    colors = ['off', 'red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white']
    color_index = 0
    
    # Button mapping for JOLED
    button_names = ["B3", "B2", "B1", "Right", "Down", "Left", "Up", "Center"]
    
    controller.clear()
    controller.center_text("JOLED RGB Demo", 0)
    controller.text("Press any button", 10, 20)
    controller.text("to cycle colors", 10, 30)
    controller.show()
    
    # Demo sequence: cycle through colors automatically
    controller.clear()
    controller.center_text("Color Demo", 10)
    controller.center_text("Auto Cycling", 25)
    controller.show()
    
    for i, color in enumerate(colors):
        controller.rgb_color(color)
        controller.clear()
        controller.center_text("RGB LED Demo", 0)
        controller.center_text(f"Color: {color.upper()}", 20)
        controller.center_text(f"{i+1}/{len(colors)}", 35)
        controller.show()
        time.sleep(1.5)
    
    # Interactive mode
    controller.clear()
    controller.center_text("Interactive Mode", 0)
    controller.text("Buttons change colors:", 0, 15)
    controller.text("Up/Down: Cycle colors", 0, 25)
    controller.text("Left/Right: RGB toggle", 0, 35)
    controller.text("Center: Turn off", 0, 45)
    controller.text("B1-B3: Set colors", 0, 55)
    controller.show()
    time.sleep(3)
    
    rgb_state = [False, False, False]  # [Red, Green, Blue]
    
    while True:
        controller.update_buttons()
        
        # Check for button presses
        if controller.button_just_pressed(6):  # Up
            color_index = (color_index + 1) % len(colors)
            controller.rgb_color(colors[color_index])
            
        elif controller.button_just_pressed(4):  # Down
            color_index = (color_index - 1) % len(colors)
            controller.rgb_color(colors[color_index])
            
        elif controller.button_just_pressed(5):  # Left - Toggle Red
            rgb_state[0] = not rgb_state[0]
            controller.set_rgb(rgb_state[0], rgb_state[1], rgb_state[2])
            
        elif controller.button_just_pressed(3):  # Right - Toggle Green
            rgb_state[1] = not rgb_state[1]
            controller.set_rgb(rgb_state[0], rgb_state[1], rgb_state[2])
            
        elif controller.button_just_pressed(7):  # Center - Turn off
            controller.rgb_off()
            rgb_state = [False, False, False]
            color_index = 0
            
        elif controller.button_just_pressed(2):  # B1 - Red
            controller.rgb_color('red')
            color_index = 1
            
        elif controller.button_just_pressed(1):  # B2 - Green  
            controller.rgb_color('green')
            color_index = 2
            
        elif controller.button_just_pressed(0):  # B3 - Blue
            controller.rgb_color('blue')
            color_index = 3
        
        # Update display
        controller.clear()
        controller.center_text("RGB Control", 0)
        
        # Show current color
        current_color = colors[color_index] if color_index < len(colors) else 'custom'
        controller.text(f"Color: {current_color}", 0, 15)
        
        # Show RGB state
        r_text = "R:ON " if rgb_state[0] else "R:OFF"
        g_text = "G:ON " if rgb_state[1] else "G:OFF"
        b_text = "B:ON " if rgb_state[2] else "B:OFF"
        controller.text(f"{r_text} {g_text} {b_text}", 0, 25)
        
        # Show pressed buttons
        pressed_buttons = []
        for i in range(8):
            if controller.button_pressed(i):
                pressed_buttons.append(button_names[i])
        
        if pressed_buttons:
            controller.text("Pressed:", 0, 40)
            controller.text(" ".join(pressed_buttons), 0, 50)
        else:
            controller.text("Press buttons above", 0, 45)
        
        controller.show()
        time.sleep(0.05)

if __name__ == "__main__":
    main()