import sys
import time

import serial
from serial import SerialException

puerto = sys.argv[1]
socket = sys.argv[2]

try:
    serial_port = serial.Serial(port=puerto, baudrate=9600, timeout=None, parity="N", bytesize=8, stopbits=1, xonxoff=False)
    serial_port.flushInput()

    st = "1000"
    sock_bin = format(int(socket), '04b')
    final = st + sock_bin + "\n"

    serial_port.write(final.encode())

    time.sleep(1) # Esperar para que se ejecute el comando en la regleta
    byte_to_read = serial_port.inWaiting()

    state = serial_port.read(byte_to_read).decode()

    print(state)

    serial_port.close()

except SerialException:
    print("No device")
