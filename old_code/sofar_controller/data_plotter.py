import serial
import time
import csv
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime
import serial.tools.list_ports
from matplotlib.ticker import MaxNLocator

def find_ft232r_port():

    for port in serial.tools.list_ports.comports():
        if port is not None:
            print(port.description, port.product)
            if port.product is not None:
                if "FT232R" in port.product:
                    return port.device
                if "FT232R" in port.description:
                    return port.device

    return None

# Find the serial port for FT232R
serial_port = find_ft232r_port()
if not serial_port:
    print("FT232R device not found.")
    exit()

# Set up the serial connection
ser = serial.Serial(serial_port, 115200, timeout=1)

# Create the CSV file with the current timestamp in the filename
timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
csv_filename = f'pressure data - {timestamp_str}.csv'
csv_file = open(csv_filename, 'a', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Timestamp', 'Temperature1', 'Pressure1', 'Temperature2', 'Pressure2'])

# Initialize lists to store data for plotting
timestamps = []
temperature1_data = []
pressure1_data = []
temperature2_data = []
pressure2_data = []

# Set up the plot
plt.style.use('seaborn-darkgrid')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Adjust the layout to reduce wasted space
plt.tight_layout(pad=4)


def animate(i):
    # Send the command to the serial port
    ser.write(b"02:00:read\n")
    time.sleep(1)

    # Read the reply
    line = ser.readline().decode('utf-8').strip()
    if line.startswith("00:02:"):
        data = line[6:].split(',')
        if len(data) == 4:

            print(f"Temperature1: {float(data[0])}, Pressure1: {float(data[1])}, Temperature2: {float(data[2])}, Pressure2: {float(data[3])}")


            timestamp = datetime.datetime.now().strftime("%Y-%m-%d\n%H:%M:%S")
            temperature1 = float(data[0])
            pressure1 = float(data[1])
            temperature2 = float(data[2])
            pressure2 = float(data[3])

            # Append data to CSV
            csv_writer.writerow([timestamp, temperature1, pressure1, temperature2, pressure2])
            csv_file.flush()

            # Append data for plotting
            timestamps.append(timestamp)
            temperature1_data.append(temperature1)
            pressure1_data.append(pressure1)
            temperature2_data.append(temperature2)
            pressure2_data.append(pressure2)

            # Limit lists to last 50 points for better real-time performance
            # timestamps[:] = timestamps[-50:]
            # temperature1_data[:] = temperature1_data[-50:]
            # pressure1_data[:] = pressure1_data[-50:]
            # temperature2_data[:] = temperature2_data[-50:]
            # pressure2_data[:] = pressure2_data[-50:]

            # Plot temperatures
            ax1.clear()
            ax1.plot(timestamps, temperature1_data, label='Temperature1', color='blue')
            ax1.plot(timestamps, temperature2_data, label='Temperature2', color='red')
            ax1.set_ylim(15, 30)
            ax1.set_ylabel('Temperature (°C)')
            ax1.legend(loc='upper left')

            ax1.xaxis.set_major_locator(MaxNLocator(nbins=10))
            ax1.tick_params(axis='x', rotation=90, labelsize=7)

            # Plot pressures
            ax2.clear()
            ax2.plot(timestamps, pressure1_data, label='Pressure1', color='blue')
            ax2.plot(timestamps, pressure2_data, label='Pressure2', color='red')
            ax2.set_ylim(400, 1300)
            ax2.set_ylabel('Pressure (hPa)')
            ax2.set_xlabel('Time')
            ax2.legend(loc='upper left')
            ax2.xaxis.set_major_locator(MaxNLocator(nbins=10))

            ax2.tick_params(axis='x', rotation=90, labelsize=7)

# Set up the animation
ani = FuncAnimation(fig, animate, interval=1000)

# Show the plot
plt.show()

# Clean up
ser.close()
csv_file.close()
