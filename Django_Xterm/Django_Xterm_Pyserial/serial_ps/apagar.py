import sys
import serial

puerto = sys.argv[1]
socket = sys.argv[2]

try:
    serial_port = serial.Serial(port=puerto, baudrate=9600, timeout=None, parity="N", bytesize=8, stopbits=1, xonxoff=False)
    serial_port.flushInput()

    apg = "1110"
    sock_bin = format(int(socket), '04b')
    final = apg + sock_bin + "\n"

    serial_port.write(final.encode())

    serial_port.close()

    outcome = "ok"

except:
    outcome = "Error"

print(outcome)
