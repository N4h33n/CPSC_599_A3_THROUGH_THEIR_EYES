# demo sped up version of the clock to see how the clock acts when in motion

import serial
import time
import threading

serial_port = "/dev/cu.usbmodem101"

def thread_task(city, ser):
    while True:
        sun_pos = 180
        moon_pos = 0
        ser.write(f"{sun_pos},{moon_pos}\n".encode())
        time.sleep(0.1)
        while sun_pos >= 0:
            sun_pos -= 1
            ser.write(f"{sun_pos},{moon_pos}\n".encode())
            time.sleep(0.1)
        sun_pos = 180
        ser.write(f"{sun_pos},{moon_pos}\n".encode())
        time.sleep(0.1)
        while moon_pos <= 180:
            moon_pos += 1
            ser.write(f"{sun_pos},{moon_pos}\n".encode())
            time.sleep(0.1)

def main():
    ser = serial.Serial(serial_port, 9600, timeout=1)
    time.sleep(2)
    background_thread = threading.Thread(target=thread_task, args=("", ser))
    background_thread.daemon = True
    background_thread.start()
    background_thread.join()
    ser.close()

main()