# JOLED Full Feature Demo - Complete Menu System
# Uses all 8 buttons (5-way D-pad + 3 buttons), RGB LED, and all OLED features

from oled_controller import OLEDController
import time

class JOLEDMenu:
    def __init__(self):
        # Initialize JOLED controller
        self.controller = OLEDController.create()
        self.disp = self.controller.disp
        self.btns = self.controller.btns
        self.rgb = self.controller.rgb
        
        # Menu state
        self.main_menu_items = [
            "Display Tests",
            "RGB LED Demo", 
            "Button Mapping",
            "Graphics Showcase",
            "Animation Demo",
            "Settings",
            "About",
            "Exit"
        ]
        self.current_menu = "main"
        self.selected_item = 0
        self.rgb_color_index = 0
        self.colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white']
        
        # Button names for JOLED
        self.button_names = ["B3", "B2", "B1", "Right", "Down", "Left", "Up", "Center"]
        
    def show_startup(self):
        """Show startup animation with RGB"""
        self.disp.clear()
        self.disp.center_text("JOLED", 15)
        self.disp.center_text("Full Demo", 30)
        self.disp.show()
        
        if self.rgb:
            # Startup animation
            for color in ['red', 'green', 'blue']:
                self.rgb.color(color)
                time.sleep(0.3)
            self.rgb.off()
        
        time.sleep(1)
        
        # Show controls
        self.disp.clear()
        self.disp.center_text("Controls:", 0)
        self.disp.text("D-pad: Navigate", 0, 15)
        self.disp.text("Center: Select", 0, 25)
        self.disp.text("B1/B2/B3: Actions", 0, 35)
        self.disp.text("Hold B3: Quick exit", 0, 45)
        self.disp.center_text("Press Center to start", 55)
        self.disp.show()
        
        # Wait for center button
        while True:
            self.btns.update()
            if self.btns.was_pressed(7):  # Center
                break
            time.sleep(0.05)
    
    def draw_main_menu(self):
        """Draw the main menu with RGB indicator"""
        self.disp.clear()
        self.disp.center_text("JOLED Menu", 0)
        self.disp.line(0, 8, 127, 8)
        
        # Show current RGB status
        if self.rgb:
            self.disp.text("RGB:", 85, 0)
            self.disp.fill_rect(110, 0, 8, 7, 1)
        
        # Draw menu items (show 5 at a time)
        start_idx = max(0, self.selected_item - 2)
        end_idx = min(len(self.main_menu_items), start_idx + 5)
        
        for i in range(start_idx, end_idx):
            y_pos = 12 + (i - start_idx) * 10
            item = self.main_menu_items[i]
            
            if i == self.selected_item:
                # Highlight selected item
                self.disp.fill_rect(0, y_pos - 1, 128, 9, 1)
                self.disp.text(f">{item}", 2, y_pos, 0)  # Black text on white
                
                # Update RGB to match selection
                if self.rgb:
                    color_idx = i % len(self.colors)
                    self.rgb.color(self.colors[color_idx])
            else:
                self.disp.text(f" {item}", 2, y_pos)
        
        self.disp.show()
    
    def handle_main_menu_input(self):
        """Handle input for main menu"""
        self.btns.update()
        
        # Navigation
        if self.btns.was_pressed(6):  # Up
            self.selected_item = (self.selected_item - 1) % len(self.main_menu_items)
        elif self.btns.was_pressed(4):  # Down
            self.selected_item = (self.selected_item + 1) % len(self.main_menu_items)
        elif self.btns.was_pressed(7):  # Center - Select
            self.execute_menu_item()
        elif self.btns.was_pressed(0):  # B3 - Quick exit
            return False
        
        # Quick RGB controls
        elif self.btns.was_pressed(1):  # B2 - Cycle RGB color
            if self.rgb:
                self.rgb_color_index = (self.rgb_color_index + 1) % len(self.colors)
                self.rgb.color(self.colors[self.rgb_color_index])
        elif self.btns.was_pressed(2):  # B1 - RGB off
            if self.rgb:
                self.rgb.off()
        
        return True
    
    def execute_menu_item(self):
        """Execute the selected menu item"""
        item = self.main_menu_items[self.selected_item]
        
        if item == "Display Tests":
            self.display_tests()
        elif item == "RGB LED Demo":
            self.rgb_demo()
        elif item == "Button Mapping":
            self.button_mapping()
        elif item == "Graphics Showcase":
            self.graphics_showcase()
        elif item == "Animation Demo":
            self.animation_demo()
        elif item == "Settings":
            self.settings_menu()
        elif item == "About":
            self.about_screen()
        elif item == "Exit":
            return False
        return True
    
    def display_tests(self):
        """Display test submenu"""
        tests = ["Contrast Test", "Invert Test", "Text Demo", "Pixel Test"]
        selected = 0
        
        while True:
            self.disp.clear()
            self.disp.center_text("Display Tests", 0)
            self.disp.line(0, 8, 127, 8)
            
            for i, test in enumerate(tests):
                y_pos = 15 + i * 10
                if i == selected:
                    self.disp.fill_rect(0, y_pos - 1, 128, 9, 1)
                    self.disp.text(f">{test}", 2, y_pos, 0)
                else:
                    self.disp.text(f" {test}", 2, y_pos)
            
            self.disp.text("B3: Back", 0, 55)
            self.disp.show()
            
            self.btns.update()
            if self.btns.was_pressed(6):  # Up
                selected = (selected - 1) % len(tests)
            elif self.btns.was_pressed(4):  # Down
                selected = (selected + 1) % len(tests)
            elif self.btns.was_pressed(7):  # Center
                if selected == 0:  # Contrast Test
                    self.contrast_test()
                elif selected == 1:  # Invert Test
                    self.invert_test()
                elif selected == 2:  # Text Demo
                    self.text_demo()
                elif selected == 3:  # Pixel Test
                    self.pixel_test()
            elif self.btns.was_pressed(0):  # B3 - Back
                break
            
            time.sleep(0.05)
    
    def contrast_test(self):
        """Test display contrast levels"""
        self.disp.clear()
        self.disp.center_text("Contrast Test", 10)
        self.disp.center_text("Running...", 30)
        self.disp.show()
        
        for contrast in [50, 100, 150, 200, 255, 200, 150, 100, 255]:
            self.controller.contrast(contrast)
            self.disp.clear()
            self.disp.center_text("Contrast Test", 0)
            self.disp.center_text(f"Level: {contrast}", 15)
            
            # Draw test pattern
            for i in range(0, 128, 8):
                self.disp.vline(i, 25, 20)
            self.disp.rect(10, 25, 108, 20)
            
            self.disp.show()
            time.sleep(0.5)
    
    def invert_test(self):
        """Test display inversion"""
        for invert in [False, True, False]:
            self.controller.invert(invert)
            self.disp.clear()
            self.disp.center_text("Invert Test", 15)
            self.disp.center_text("Inverted" if invert else "Normal", 30)
            self.disp.show()
            time.sleep(1)
        self.controller.invert(False)  # Reset
    
    def text_demo(self):
        """Demonstrate text rendering"""
        self.disp.clear()
        self.disp.text("Font Demo:", 0, 0)
        self.disp.text("ABCDEFGHIJKLMNOPQR", 0, 10)
        self.disp.text("abcdefghijklmnopqr", 0, 20)
        self.disp.text("0123456789!@#$%^&", 0, 30)
        self.disp.text("Special: äöü°€→←", 0, 40)
        self.disp.center_text("Centered Text", 50)
        self.disp.show()
        self.wait_for_button()
    
    def pixel_test(self):
        """Test individual pixel control"""
        self.disp.clear()
        self.disp.center_text("Pixel Test", 0)
        
        # Draw pixel pattern
        for x in range(0, 128, 4):
            for y in range(10, 64, 4):
                if (x + y) % 8 == 0:
                    self.disp.pixel(x, y, 1)
        
        self.disp.show()
        self.wait_for_button()
    
    def rgb_demo(self):
        """RGB LED demonstration"""
        if not self.rgb:
            self.show_message("RGB LED", "Not Available", 2)
            return
        
        demos = ["Color Cycle", "Pulse Demo", "Flash Demo", "Interactive"]
        selected = 0
        
        while True:
            self.disp.clear()
            self.disp.center_text("RGB LED Demo", 0)
            self.disp.line(0, 8, 127, 8)
            
            for i, demo in enumerate(demos):
                y_pos = 15 + i * 10
                if i == selected:
                    self.disp.fill_rect(0, y_pos - 1, 128, 9, 1)
                    self.disp.text(f">{demo}", 2, y_pos, 0)
                else:
                    self.disp.text(f" {demo}", 2, y_pos)
            
            self.disp.text("B3: Back", 0, 55)
            self.disp.show()
            
            self.btns.update()
            if self.btns.was_pressed(6):  # Up
                selected = (selected - 1) % len(demos)
            elif self.btns.was_pressed(4):  # Down
                selected = (selected + 1) % len(demos)
            elif self.btns.was_pressed(7):  # Center
                if selected == 0:  # Color Cycle
                    self.rgb_color_cycle()
                elif selected == 1:  # Pulse Demo
                    self.rgb_pulse_demo()
                elif selected == 2:  # Flash Demo
                    self.rgb_flash_demo()
                elif selected == 3:  # Interactive
                    self.rgb_interactive()
            elif self.btns.was_pressed(0):  # B3 - Back
                self.rgb.off()
                break
            
            time.sleep(0.05)
    
    def rgb_color_cycle(self):
        """Cycle through RGB colors"""
        for color in self.colors:
            self.disp.clear()
            self.disp.center_text("Color Cycle", 15)
            self.disp.center_text(color.upper(), 30)
            self.disp.show()
            self.rgb.color(color)
            time.sleep(1)
        self.rgb.off()
    
    def rgb_pulse_demo(self):
        """Demonstrate RGB pulsing"""
        self.disp.clear()
        self.disp.center_text("RGB Pulsing", 15)
        self.disp.center_text("Blue x3", 30)
        self.disp.show()
        
        self.rgb.pulse('blue', speed=0.08, count=3)
        while self.rgb.is_pulsing():
            time.sleep(0.1)
    
    def rgb_flash_demo(self):
        """Demonstrate RGB flashing"""
        self.disp.clear()
        self.disp.center_text("RGB Flashing", 15)
        self.disp.center_text("Red x5", 30)
        self.disp.show()
        
        self.rgb.flash('red', count=5, on_time=200, off_time=200)
        time.sleep(3)
    
    def rgb_interactive(self):
        """Interactive RGB control"""
        self.disp.clear()
        self.disp.center_text("RGB Interactive", 0)
        self.disp.text("Up/Down: Colors", 0, 15)
        self.disp.text("Left: Pulse", 0, 25)
        self.disp.text("Right: Flash", 0, 35)
        self.disp.text("Center: Off", 0, 45)
        self.disp.text("B3: Back", 0, 55)
        self.disp.show()
        
        color_idx = 0
        
        while True:
            self.btns.update()
            
            if self.btns.was_pressed(6):  # Up - Next color
                color_idx = (color_idx + 1) % len(self.colors)
                self.rgb.color(self.colors[color_idx])
                self.show_temp_message(f"Color: {self.colors[color_idx]}")
            elif self.btns.was_pressed(4):  # Down - Prev color  
                color_idx = (color_idx - 1) % len(self.colors)
                self.rgb.color(self.colors[color_idx])
                self.show_temp_message(f"Color: {self.colors[color_idx]}")
            elif self.btns.was_pressed(5):  # Left - Pulse
                self.rgb.pulse(self.colors[color_idx], count=2)
                self.show_temp_message("Pulsing...")
            elif self.btns.was_pressed(3):  # Right - Flash
                self.rgb.flash(self.colors[color_idx], count=3)
                self.show_temp_message("Flashing...")
            elif self.btns.was_pressed(7):  # Center - Off
                self.rgb.off()
                self.show_temp_message("RGB Off")
            elif self.btns.was_pressed(0):  # B3 - Back
                break
            
            time.sleep(0.05)
    
    def button_mapping(self):
        """Show live button mapping and states"""
        self.disp.clear()
        self.disp.center_text("Button Mapping", 0)
        self.disp.text("Press buttons to test", 0, 10)
        self.disp.text("B3: Back", 0, 55)
        self.disp.show()
        
        button_press_counts = [0] * 8
        
        while True:
            self.btns.update()
            
            # Check for exit
            if self.btns.was_pressed(0):  # B3
                break
            
            # Count button presses
            for i in range(8):
                if self.btns.was_pressed(i):
                    button_press_counts[i] += 1
            
            # Draw button states
            self.disp.clear()
            self.disp.center_text("Button Mapping", 0)
            
            for i in range(8):
                y_pos = 12 + (i % 6) * 8
                x_pos = 0 if i < 6 else 70
                
                status = "ON " if self.btns.is_pressed(i) else "OFF"
                self.disp.text(f"{self.button_names[i]}:{status}({button_press_counts[i]})", x_pos, y_pos)
            
            self.disp.show()
            time.sleep(0.05)
    
    def graphics_showcase(self):
        """Showcase graphics capabilities"""
        demos = ["Lines", "Rectangles", "Patterns", "Animation"]
        selected = 0
        
        while True:
            self.disp.clear()
            self.disp.center_text("Graphics Demo", 0)
            self.disp.line(0, 8, 127, 8)
            
            for i, demo in enumerate(demos):
                y_pos = 15 + i * 10
                if i == selected:
                    self.disp.fill_rect(0, y_pos - 1, 128, 9, 1)
                    self.disp.text(f">{demo}", 2, y_pos, 0)
                else:
                    self.disp.text(f" {demo}", 2, y_pos)
            
            self.disp.text("B3: Back", 0, 55)
            self.disp.show()
            
            self.btns.update()
            if self.btns.was_pressed(6):  # Up
                selected = (selected - 1) % len(demos)
            elif self.btns.was_pressed(4):  # Down
                selected = (selected + 1) % len(demos)
            elif self.btns.was_pressed(7):  # Center
                if selected == 0:  # Lines
                    self.lines_demo()
                elif selected == 1:  # Rectangles
                    self.rectangles_demo()
                elif selected == 2:  # Patterns
                    self.patterns_demo()
                elif selected == 3:  # Animation
                    self.graphics_animation()
            elif self.btns.was_pressed(0):  # B3 - Back
                break
            
            time.sleep(0.05)
    
    def lines_demo(self):
        """Demonstrate line drawing"""
        self.disp.clear()
        self.disp.center_text("Lines Demo", 0)
        
        # Draw various lines
        for i in range(0, 64, 8):
            self.disp.line(0, 10 + i, 127, 10 + i)
        
        for i in range(0, 128, 16):
            self.disp.line(i, 10, i, 63)
        
        # Diagonal lines
        self.disp.line(0, 10, 127, 63)
        self.disp.line(127, 10, 0, 63)
        
        self.disp.show()
        self.wait_for_button()
    
    def rectangles_demo(self):
        """Demonstrate rectangle drawing"""
        self.disp.clear()
        self.disp.center_text("Rectangles", 0)
        
        # Nested rectangles
        for i in range(5):
            self.disp.rect(10 + i*5, 15 + i*3, 108 - i*10, 45 - i*6)
        
        # Filled rectangles
        self.disp.fill_rect(5, 50, 20, 10, 1)
        self.disp.fill_rect(30, 52, 15, 6, 1)
        self.disp.fill_rect(50, 54, 10, 2, 1)
        
        self.disp.show()
        self.wait_for_button()
    
    def patterns_demo(self):
        """Demonstrate pattern drawing"""
        self.disp.clear()
        self.disp.center_text("Patterns", 0)
        
        # Checkerboard pattern
        for x in range(0, 128, 8):
            for y in range(10, 64, 8):
                if (x + y) % 16 == 0:
                    self.disp.fill_rect(x, y, 4, 4, 1)
        
        self.disp.show()
        self.wait_for_button()
    
    def graphics_animation(self):
        """Simple graphics animation"""
        for frame in range(30):
            self.disp.clear()
            self.disp.center_text("Animation", 0)
            
            # Moving rectangle
            x = frame * 3 % 108
            self.disp.rect(x, 20, 20, 15)
            
            # Rotating line
            center_x, center_y = 64, 40
            angle = frame * 0.2
            import math
            end_x = int(center_x + 20 * math.cos(angle))
            end_y = int(center_y + 20 * math.sin(angle))
            self.disp.line(center_x, center_y, end_x, end_y)
            
            self.disp.show()
            time.sleep(0.1)
            
            # Check for early exit
            self.btns.update()
            if self.btns.is_pressed(0):
                break
    
    def animation_demo(self):
        """RGB and display animation demo"""
        self.disp.clear()
        self.disp.center_text("Animation Demo", 15)
        self.disp.center_text("RGB + Display", 30)
        self.disp.show()
        
        if self.rgb:
            # Start RGB pulsing
            self.rgb.pulse('blue', speed=0.1, count=-1)  # Infinite
        
        # Animated display
        for frame in range(50):
            self.disp.clear()
            self.disp.center_text("Animation Demo", 0)
            
            # Moving dots
            for i in range(5):
                x = (frame * 2 + i * 25) % 128
                y = 20 + i * 8
                self.disp.fill_rect(x, y, 4, 4)
            
            self.disp.show()
            time.sleep(0.1)
            
            # Check for early exit
            self.btns.update()
            if self.btns.is_pressed(0):
                break
        
        if self.rgb:
            self.rgb.stop_animation()
            self.rgb.off()
    
    def settings_menu(self):
        """Settings and configuration"""
        self.disp.clear()
        self.disp.center_text("Settings", 15)
        self.disp.text("Contrast: Adjustable", 0, 30)
        self.disp.text("RGB: Available" if self.rgb else "RGB: Not available", 0, 40)
        self.disp.text("Buttons: 8 detected", 0, 50)
        self.disp.text("Press any button", 0, 55)
        self.disp.show()
        self.wait_for_button()
    
    def about_screen(self):
        """About screen with system info"""
        self.disp.clear()
        self.disp.center_text("JOLED Demo v1.0", 0)
        self.disp.line(0, 8, 127, 8)
        self.disp.text("MicroPython Library", 0, 15)
        self.disp.text("128x64 OLED Display", 0, 25)
        self.disp.text("8 Buttons + RGB LED", 0, 35)
        self.disp.text("I2C Interface", 0, 45)
        self.disp.text("Press any button", 0, 55)
        self.disp.show()
        self.wait_for_button()
    
    def show_message(self, title, message, duration=1):
        """Show a temporary message"""
        self.disp.clear()
        self.disp.center_text(title, 15)
        self.disp.center_text(message, 30)
        self.disp.show()
        time.sleep(duration)
    
    def show_temp_message(self, message):
        """Show temporary message in corner"""
        # Save current display area
        self.disp.fill_rect(0, 55, 128, 9, 1)
        self.disp.text(message, 2, 56, 0)
        self.disp.show()
        time.sleep(0.5)
    
    def wait_for_button(self):
        """Wait for any button press"""
        while True:
            self.btns.update()
            for i in range(8):
                if self.btns.was_pressed(i):
                    return
            time.sleep(0.05)
    
    def run(self):
        """Main menu loop"""
        self.show_startup()
        
        while True:
            self.draw_main_menu()
            if not self.handle_main_menu_input():
                break
            time.sleep(0.05)
        
        # Exit sequence
        if self.rgb:
            self.rgb.off()
        
        self.disp.clear()
        self.disp.center_text("JOLED Demo", 20)
        self.disp.center_text("Complete!", 35)
        self.disp.show()
        time.sleep(2)
        
        self.disp.clear()
        self.disp.show()

def main():
    print("JOLED Full Feature Demo Starting...")
    print("Controls:")
    print("  D-pad: Navigate menus")
    print("  Center: Select")
    print("  B1/B2: RGB controls")
    print("  B3: Back/Exit")
    
    demo = JOLEDMenu()
    demo.run()

if __name__ == "__main__":
    main()