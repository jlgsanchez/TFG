import sys
import serial
import time

puerto = sys.argv[1]
lista = sys.argv[2:]

try:
    serial_port = serial.Serial(port=puerto, baudrate=9600, timeout=None, parity="N", bytesize=8, stopbits=1, xonxoff=False)
    serial_port.flushInput()

    apg = "1110"

    for s in lista:
        sock_bin = format(int(s), '04b')
        final = apg + sock_bin + "\n"

        serial_port.write(final.encode())

        time.sleep(0.5)

    serial_port.close()

    outcome = "ok"

except:
    outcome = "Error"


print(outcome)
