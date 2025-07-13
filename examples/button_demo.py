# Button Input Demo Example

from oled_controller import OLEDController
import time

def main():
    # Initialize controller
    controller = OLEDController()
    
    print("Button Demo Starting...")
    print("Press buttons to see them light up on display")
    
    button_count = [0, 0, 0, 0]  # Counter for each button
    
    while True:
        # Update button states
        controller.update_buttons()
        
        # Clear display
        controller.clear()
        
        # Title
        controller.center_text("Button Demo", 0)
        controller.line(0, 10, 127, 10)
        
        # Show button states
        y_pos = 15
        for i in range(4):
            if controller.button_pressed(i):
                # Button is pressed - show filled indicator
                controller.fill_rect(5, y_pos, 10, 8)
                controller.text(f"BTN{i}: PRESSED", 20, y_pos)
            else:
                # Button not pressed - show empty indicator  
                controller.rect(5, y_pos, 10, 8)
                controller.text(f"BTN{i}: Released", 20, y_pos)
            
            # Check for button press events
            if controller.button_just_pressed(i):
                button_count[i] += 1
            
            # Show press count
            controller.text(f"({button_count[i]})", 100, y_pos)
            
            y_pos += 12
        
        # Show instructions
        controller.text("Press any button", 5, 57)
        
        controller.show()
        time.sleep(0.05)  # 20 FPS update rate

if __name__ == "__main__":
    main()