from machine import I2C, Pin, UART, Timer
import ssd1306
import time
from interface import InterfaceBoard
from bmp390 import BMP390
import _thread
import re

# Version
VERSION = "0.1.0"
DEVICE_TYPE = "hull test sensor"

#solenoid
SOLENOID_PIN_NUM = 0
solenoid_pin = Pin(SOLENOID_PIN_NUM, Pin.OUT)
solenoid_pin.value(0)
solenoid_state = False # False for Off, True for open

def solenoid_on():
    global solenoid_state
    solenoid_pin.value(1)
    solenoid_state = True
    
def solenoid_off():
    global solenoid_state
    solenoid_pin.value(0)
    solenoid_state = False

# Define I2C bus
i2c = I2C(0, scl=Pin(7), sda=Pin(6))

# Initialize BMP390 sensors
bmp_outer = BMP390(i2c, address=0x77)
bmp_inner = BMP390(i2c, address=0x76)

# Initialize Interface Board
iface = InterfaceBoard(i2c)

# setup the sensor polling thread
t_inner = -1
p_inner = -1
t_outer = -1
p_outer = -1

def update_sensors():
    global t_outer
    global p_outer
    global t_inner
    global p_inner
    
    sensor_to_update = 0
    
    while True:
        if sensor_to_update==0:
            t_outer = bmp_outer.temperature
        if sensor_to_update==1:
            p_outer = bmp_outer.pressure
        if sensor_to_update==2:
            t_inner = bmp_inner.temperature
        if sensor_to_update==3:
            p_inner = bmp_inner.pressure
            
        sensor_to_update += 1
        if sensor_to_update==4:
            sensor_to_update=0

_thread.start_new_thread(update_sensors, ())

# Initialize UART for RS485
# UART(id, baudrate=115200, bits=8, parity=None, stop=1, tx=None, rx=None)
uart = UART(1, baudrate=115200, tx=Pin(21), rx=Pin(20))


# setup the UART message handling
DEVICE_ADDRESS = "02"

last_msg = "Waiting for 1st msg"
# Regular expression pattern to match the command format
pattern = re.compile(r"(\d\d):(\d\d):(.*)")

def listen_for_uart():
    buffer = ""
    while True:
        if uart.any():
            char = uart.read(1).decode("ascii")
            buffer += char
            
            if buffer.endswith("\n") or buffer.endswith("\r"):
                buffer.strip()
                match = pattern.match(buffer)
                if match:
                    to_address = match.group(1)                
                    if to_address == DEVICE_ADDRESS:
                        handle_message(match.group(0))
                buffer = ""  # Reset the buffer after processing the message

def respond(msg):
    uart.write(f"00:{DEVICE_ADDRESS}:{msg}\r\n")

last_received = time.time()
last_from = "None"

def handle_message(message):
    global last_received
    global last_msg
    global last_from
    
    last_received = time.time()

    match = pattern.match(message)
    if not match:
        return  # If the message doesn't match the pattern, ignore it

    to_address = match.group(1)
    from_address = match.group(2)
    last_from = from_address
    command = match.group(3).strip()

    last_msg = command
        
    print(f"from '{from_address}' to '{to_address}': '{command}'")
    
    # React to the received command
    if command == "read":
        respond(f"{t_inner:.1f},{p_inner:.2f},{t_outer:.1f},{p_outer:.2f}")
        
    elif command == "open":
        solenoid_on()
        respond("opened")
        
    elif command == "close":
        solenoid_off()
        respond("closed")
        
    elif command == "ping":
        respond("pong")

    elif command == "version":
        respond(f"{VERSION}")

    elif command == "device":
        respond(f"{DEVICE_TYPE}")
    else:
        respond("?")

# Start a new thread for listening to UART messages
_thread.start_new_thread(listen_for_uart, ())




while True:
    iface.clear(0)
    
    iface.sprint(f"Device Address: {DEVICE_ADDRESS}", 0,0,1)
    
    if iface.get_btn("B1"):
        solenoid_state = True
        
    if iface.get_btn("B2"):
        solenoid_state = False
        
    if solenoid_state:
        iface.set_led(G=1)
        iface.sprint("Solenoid Open", 0,9,1)
    else:
        iface.set_led(R=1)
        iface.sprint("Solenoid Closed", 0,9,1)
        
    solenoid_pin.value(solenoid_state)
    
    # printout the inner sensor
    iface.sprint(f"I: {t_inner:.1f}C {p_inner:.2f}hPa", 0, 18)
    # printout the outer sensor
    iface.sprint(f"O: {t_outer:.1f}C {p_outer:.2f}hPa", 0, 27)
    
    # printout the last command
    iface.sprint(f"last msg from: {last_from}", 0, 39)
    iface.sprint(f"{last_msg}", 0, 47)
    iface.sprint(f"{time.time() - last_received} s ago", 0, 58)
    
    
    
    iface.show()
    
    
    time.sleep(0.01)
    
    