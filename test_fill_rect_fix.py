# Test script to verify fill_rect fix works
from oled_controller import OLEDController

# Test the fix
controller = OLEDController.create()

# Test fill_rect with proper parameters
controller.disp.clear()
controller.disp.center_text("Fill Rect Test", 10)

# These should all work now (with color parameter)
controller.disp.fill_rect(10, 20, 20, 10, 1)  # Small rectangle
controller.disp.fill_rect(40, 25, 15, 5, 1)   # Another rectangle
controller.disp.fill_rect(70, 22, 8, 8, 1)    # Square

controller.disp.show()
print("fill_rect test completed successfully!")