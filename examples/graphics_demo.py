# Graphics and Animation Demo

from oled_controller import OLEDController
import time
import math

def main():
    controller = OLEDController()
    
    print("Graphics Demo Starting...")
    
    # Bouncing ball animation
    ball_x = 20
    ball_y = 20
    vel_x = 2
    vel_y = 1
    
    controller.clear()
    controller.center_text("Bouncing Ball", 0)
    controller.show()
    time.sleep(2)
    
    for frame in range(200):
        controller.clear()
        
        # Update ball position
        ball_x += vel_x
        ball_y += vel_y
        
        # Bounce off edges
        if ball_x <= 2 or ball_x >= 124:
            vel_x = -vel_x
        if ball_y <= 12 or ball_y >= 60:
            vel_y = -vel_y
        
        # Draw border
        controller.rect(0, 10, 128, 54)
        
        # Draw ball (3x3 filled rectangle)
        controller.fill_rect(ball_x-1, ball_y-1, 3, 3)
        
        # Show frame counter
        controller.text(f"Frame: {frame}", 2, 2)
        
        controller.show()
        time.sleep(0.05)
    
    # Sine wave animation
    controller.clear()
    controller.center_text("Sine Wave", 25)
    controller.show()
    time.sleep(2)
    
    for phase in range(100):
        controller.clear()
        
        # Draw sine wave
        for x in range(128):
            y = int(32 + 20 * math.sin((x + phase * 2) * 0.1))
            controller.pixel(x, y)
        
        # Draw cosine wave
        for x in range(128):
            y = int(32 + 15 * math.cos((x + phase * 3) * 0.08))
            if 0 <= y < 64:
                controller.pixel(x, y)
        
        controller.text("Sine & Cosine", 0, 0)
        controller.show()
        time.sleep(0.1)
    
    # Rotating line
    controller.clear()
    controller.center_text("Rotating Line", 25)
    controller.show()
    time.sleep(2)
    
    center_x = 64
    center_y = 32
    
    for angle in range(0, 360, 5):
        controller.clear()
        
        # Calculate line endpoints
        rad = math.radians(angle)
        end_x = int(center_x + 25 * math.cos(rad))
        end_y = int(center_y + 25 * math.sin(rad))
        
        # Draw center point
        controller.fill_rect(center_x-1, center_y-1, 3, 3)
        
        # Draw rotating line
        controller.line(center_x, center_y, end_x, end_y)
        
        # Draw angle text
        controller.text(f"Angle: {angle:3d}", 0, 0)
        
        controller.show()
        time.sleep(0.05)
    
    # Pattern drawing
    controller.clear()
    controller.center_text("Patterns", 25)
    controller.show()
    time.sleep(2)
    
    # Checkerboard pattern
    for step in range(20):
        controller.clear()
        
        for x in range(0, 128, 8):
            for y in range(0, 64, 8):
                if ((x//8) + (y//8) + step) % 2:
                    controller.fill_rect(x, y, 8, 8)
        
        controller.text("Checkerboard", 0, 0)
        controller.show()
        time.sleep(0.2)
    
    # Spiral pattern
    controller.clear()
    controller.center_text("Spiral", 25)
    controller.show()
    time.sleep(2)
    
    for t in range(500):
        if t % 50 == 0:
            controller.clear()
        
        # Calculate spiral coordinates
        angle = t * 0.2
        radius = t * 0.1
        x = int(64 + radius * math.cos(angle))
        y = int(32 + radius * math.sin(angle))
        
        if 0 <= x < 128 and 0 <= y < 64:
            controller.pixel(x, y)
        
        if t % 10 == 0:
            controller.show()
            time.sleep(0.02)
    
    # Final message
    controller.clear()
    controller.center_text("Graphics Demo", 20)
    controller.center_text("Complete!", 35)
    controller.show()

if __name__ == "__main__":
    main()