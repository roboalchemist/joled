# Simple Menu System Example

from oled_controller import OLEDController
import time

class SimpleMenu:
    def __init__(self, controller):
        self.controller = controller
        self.menu_items = [
            "Display Info",
            "Contrast Test", 
            "Graphics Demo",
            "Button Test",
            "Exit"
        ]
        self.selected_item = 0
        self.in_submenu = False
        
    def draw_menu(self):
        """Draw the main menu"""
        self.controller.clear()
        self.controller.center_text("Main Menu", 0)
        self.controller.line(0, 10, 127, 10)
        
        # Draw menu items
        for i, item in enumerate(self.menu_items):
            y_pos = 15 + i * 10
            if i == self.selected_item:
                # Highlight selected item
                self.controller.fill_rect(0, y_pos-1, 128, 9)
                self.controller.text(f"> {item}", 5, y_pos, 0)  # Black text on white
            else:
                self.controller.text(f"  {item}", 5, y_pos)
        
        self.controller.show()
    
    def handle_input(self):
        """Handle button input for menu navigation"""
        self.controller.update_buttons()
        
        if self.controller.button_just_pressed(0):  # Up
            self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            
        elif self.controller.button_just_pressed(1):  # Down
            self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            
        elif self.controller.button_just_pressed(2):  # Select
            self.execute_menu_item()
            
        elif self.controller.button_just_pressed(3):  # Back/Exit
            return False
            
        return True
    
    def execute_menu_item(self):
        """Execute the selected menu item"""
        item = self.menu_items[self.selected_item]
        
        if item == "Display Info":
            self.show_display_info()
        elif item == "Contrast Test":
            self.contrast_test()
        elif item == "Graphics Demo":
            self.graphics_demo()
        elif item == "Button Test":
            self.button_test()
        elif item == "Exit":
            return False
            
        return True
    
    def show_display_info(self):
        """Show display information"""
        self.controller.clear()
        self.controller.center_text("Display Info", 0)
        self.controller.line(0, 10, 127, 10)
        
        info_lines = [
            f"Size: {self.controller.width}x{self.controller.height}",
            f"Buttons: {self.controller.num_buttons}",
            "Font: 5x7 bitmap",
            "I2C Interface"
        ]
        
        for i, line in enumerate(info_lines):
            self.controller.text(line, 5, 15 + i * 10)
        
        self.controller.text("Press any button", 5, 57)
        self.controller.show()
        
        # Wait for button press
        while True:
            self.controller.update_buttons()
            for i in range(4):
                if self.controller.button_just_pressed(i):
                    return
            time.sleep(0.05)
    
    def contrast_test(self):
        """Test different contrast levels"""
        self.controller.clear()
        self.controller.center_text("Contrast Test", 20)
        self.controller.center_text("Running...", 35)
        self.controller.show()
        
        for contrast in [50, 100, 150, 200, 255, 200, 150, 100]:
            self.controller.contrast(contrast)
            self.controller.clear()
            self.controller.center_text("Contrast Test", 10)
            self.controller.center_text(f"Level: {contrast}", 25)
            self.controller.rect(20, 35, 88, 20)
            for i in range(0, 80, 4):
                self.controller.vline(24 + i, 39, 12)
            self.controller.show()
            time.sleep(0.5)
        
        # Reset to normal contrast
        self.controller.contrast(255)
    
    def graphics_demo(self):
        """Quick graphics demonstration"""
        self.controller.clear()
        self.controller.center_text("Graphics Demo", 0)
        
        # Draw some shapes
        self.controller.rect(10, 15, 30, 20)
        self.controller.fill_rect(50, 15, 20, 20)
        self.controller.line(80, 15, 110, 35)
        
        # Draw pattern
        for x in range(10, 40, 2):
            self.controller.line(x, 40, x + 10, 55)
        
        self.controller.text("Press button", 5, 57)
        self.controller.show()
        
        # Wait for button press
        while True:
            self.controller.update_buttons()
            for i in range(4):
                if self.controller.button_just_pressed(i):
                    return
            time.sleep(0.05)
    
    def button_test(self):
        """Test button responsiveness"""
        start_time = time.time()
        button_presses = [0, 0, 0, 0]
        
        while time.time() - start_time < 10:  # 10 second test
            self.controller.update_buttons()
            
            self.controller.clear()
            self.controller.center_text("Button Test", 0)
            self.controller.line(0, 10, 127, 10)
            
            remaining = int(10 - (time.time() - start_time))
            self.controller.text(f"Time: {remaining}s", 5, 15)
            
            # Show button states and counts
            for i in range(4):
                y_pos = 25 + i * 8
                if self.controller.button_pressed(i):
                    self.controller.text(f"BTN{i}: ON  ({button_presses[i]})", 5, y_pos)
                else:
                    self.controller.text(f"BTN{i}: OFF ({button_presses[i]})", 5, y_pos)
                
                if self.controller.button_just_pressed(i):
                    button_presses[i] += 1
            
            self.controller.show()
            time.sleep(0.02)
        
        # Show results
        self.controller.clear()
        self.controller.center_text("Test Results", 0)
        self.controller.line(0, 10, 127, 10)
        
        total_presses = sum(button_presses)
        self.controller.text(f"Total: {total_presses}", 5, 15)
        
        for i in range(4):
            self.controller.text(f"BTN{i}: {button_presses[i]}", 5, 25 + i * 8)
        
        self.controller.text("Press any button", 5, 57)
        self.controller.show()
        
        # Wait for button press
        while True:
            self.controller.update_buttons()
            for i in range(4):
                if self.controller.button_just_pressed(i):
                    return
            time.sleep(0.05)

def main():
    # Initialize JOLED controller
    controller = OLEDController.create()
    
    print("Menu System Demo Starting...")
    print("Controls:")
    print("  Button 0: Up")
    print("  Button 1: Down") 
    print("  Button 2: Select")
    print("  Button 3: Exit")
    
    # Create and run menu
    menu = SimpleMenu(controller)
    
    # Show welcome screen
    controller.clear()
    controller.center_text("Menu System", 15)
    controller.center_text("Demo", 30)
    controller.center_text("Press Button 2", 45)
    controller.show()
    
    # Wait for start
    while True:
        controller.update_buttons()
        if controller.button_just_pressed(2):
            break
        time.sleep(0.05)
    
    # Main menu loop
    running = True
    while running:
        menu.draw_menu()
        running = menu.handle_input()
        time.sleep(0.05)
    
    # Exit message
    controller.clear()
    controller.center_text("Menu Demo", 20)
    controller.center_text("Complete!", 35)
    controller.show()

if __name__ == "__main__":
    main()