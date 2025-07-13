# Button Input Demo Example

from oled_controller import OLEDController
import time

def main():
    # Initialize JOLED controller with all 8 buttons
    controller = OLEDController.create()
    
    print("Button Demo Starting...")
    print("Press buttons to see them light up on display")
    
    button_count = [0] * 8  # Counter for each button
    button_names = ["B3", "B2", "B1", "Right", "Down", "Left", "Up", "Center"]
    
    while True:
        # Update button states
        controller.update_buttons()
        
        # Clear display
        controller.clear()
        
        # Title
        controller.center_text("Button Demo", 0)
        controller.line(0, 10, 127, 10)
        
        # Show button states (display 8 buttons in two columns)
        for i in range(8):
            col = i // 4
            row = i % 4
            x_pos = col * 64
            y_pos = 15 + row * 12
            
            if controller.button_pressed(i):
                # Button is pressed - show filled indicator
                controller.fill_rect(x_pos + 2, y_pos, 8, 8)
                controller.text(f"{button_names[i]}: ON", x_pos + 12, y_pos)
            else:
                # Button not pressed - show empty indicator  
                controller.rect(x_pos + 2, y_pos, 8, 8)
                controller.text(f"{button_names[i]}:off", x_pos + 12, y_pos)
            
            # Check for button press events
            if controller.button_just_pressed(i):
                button_count[i] += 1
        
        # Show instructions
        controller.text("Press any button", 5, 57)
        
        controller.show()
        time.sleep(0.05)  # 20 FPS update rate

if __name__ == "__main__":
    main()