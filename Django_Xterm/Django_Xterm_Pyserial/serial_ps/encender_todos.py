import sys
import serial

puerto = sys.argv[1]

try:
    serial_port = serial.Serial(port=puerto, baudrate=9600, timeout=None, parity="N", bytesize=8, stopbits=1, xonxoff=False)
    serial_port.flushInput()

    serial_port.write("11111111\n".encode())

    serial_port.close()
    
    outcome = "ok"

except:
    outcome = "Error"

print(outcome)