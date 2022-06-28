import serial.tools.list_ports
import serial
import traceback

from subprocess import Popen, PIPE
import subprocess

from django.conf import settings

# Obtener todos los puerto serial
def getAllPorts():
	devices = []

	for n, (puerto, descrip, hwid) in enumerate(sorted(serial.tools.list_ports.comports()),1):  #iteracion sobre la lista ordenada de puertos
                                                                		                        #port: /dev/puerto; desc: lsusb; hwid: descripcion tecnica
		devices.append(puerto)											                        #1,2,3 This is also the information returned accessed by index
	
	return devices


# Abrir conexión serial junto a ttyd
def openPort(portName, flowcontrol, parity, baudrate, bytesize, stopbits): 
    try:
        BasePort = 9080
        p = int(portName[11:])
        PuertoSerial = str(BasePort + p)

        if flowcontrol == 'None':
            Popen(["sudo", "ttyd", "--ssl", "--ssl-cert", settings.PATHSSLCRT, "--ssl-key", settings.PATHSSLKEY, "-p", 
                PuertoSerial, "python3", settings.PATHAPP + "/Django_Xterm/Django_Xterm_Pyserial/PyserialScript.py", 
                portName, baudrate, '--databit=' + bytesize, '--parity=' + parity, 
                '--stopbit=' + stopbits])

        else:
            Popen(["sudo", "ttyd", "--ssl", "--ssl-cert", settings.PATHSSLCRT, "--ssl-key", settings.PATHSSLKEY, "-p", 
                PuertoSerial, "python3", settings.PATHAPP + "/Django_Xterm/Django_Xterm_Pyserial/PyserialScript.py", 
                portName, baudrate, '--databit=' + bytesize, '--parity=' + parity, 
                '--stopbit=' + stopbits, '--' + flowcontrol])

    except:
        traceback.print_exc()


# Elimiar proceso que ejecuta la coxión serial
def removePort(portName):
    BasePort = 9080
    p = int(portName[11:])
    PuertoSerial = str(BasePort + p)
    
    arg = 'ttyd --ssl --ssl-cert ' + settings.PATHSSLCRT + ' --ssl-key ' + settings.PATHSSLKEY + ' -p ' + PuertoSerial + ' python3 ' + settings.PATHAPP + '/Django_Xterm/Django_Xterm_Pyserial/PyserialScript.py ' + portName

    p1 = Popen(['pgrep', '-f', arg], stdout=PIPE)

    for pid in p1.stdout:
        try:
            pid_int = int(pid)
            pid_str = str(pid_int)
            Popen(['sudo', "kill", "-9", pid_str])

        except OSError as ex:
            print("Error while killing process by pid")


# Funciones para el control de la regleta por serial.

# Funcion encender individual
def on_serial(portName, socket):
    result = subprocess.run(["sudo", "python3", settings.PATHAPP + "/Django_Xterm/Django_Xterm_Pyserial/serial_ps/encender.py", portName, socket], stdout=subprocess.PIPE,)
    
    return result.stdout.decode('utf-8').rstrip('\n')


# Funcion apagar individual
def off_serial(portName, socket):
    result = subprocess.run(["sudo", "python3", settings.PATHAPP + "/Django_Xterm/Django_Xterm_Pyserial/serial_ps/apagar.py", portName, socket], stdout=subprocess.PIPE,)
    
    return result.stdout.decode('utf-8').rstrip('\n')


# Funcion encender todos
def on_all_serial(portName):
    result = subprocess.run(["sudo", "python3", settings.PATHAPP + "/Django_Xterm/Django_Xterm_Pyserial/serial_ps/encender_todos.py", portName], stdout=subprocess.PIPE,)

    return result.stdout.decode('utf-8').rstrip('\n')


# Funcion apagar todos
def off_all_serial(portName):
    result = subprocess.run(["sudo", "python3", settings.PATHAPP + "/Django_Xterm/Django_Xterm_Pyserial/serial_ps/apagar_todos.py", portName], stdout=subprocess.PIPE,)

    return result.stdout.decode('utf-8').rstrip('\n')


# Funcion encender todos de una lista
def on_list_serial(portName, list):
    result = subprocess.run(["sudo", "python3", settings.PATHAPP + "/Django_Xterm/Django_Xterm_Pyserial/serial_ps/encender_todos_lista.py", portName] + list, stdout=subprocess.PIPE,)

    return result.stdout.decode('utf-8').rstrip('\n')


# Funcion apagar todos de una lista
def off_list_serial(portName, list):
    result = subprocess.run(["sudo", "python3", settings.PATHAPP + "/Django_Xterm/Django_Xterm_Pyserial/serial_ps/apagar_todos_lista.py", portName] + list, stdout=subprocess.PIPE,)

    return result.stdout.decode('utf-8').rstrip('\n')


# Fucnion estado individual
def state_serial(portName, socket):
    result = subprocess.run(["sudo", "python3", settings.PATHAPP + "/Django_Xterm/Django_Xterm_Pyserial/serial_ps/estado.py", portName, socket], stdout=subprocess.PIPE,)

    return result.stdout.decode('utf-8')
