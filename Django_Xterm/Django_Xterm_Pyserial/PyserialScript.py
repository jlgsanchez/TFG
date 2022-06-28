import os
# if os.name == 'nt':
#     os.system('Serial Terminal')

from collections import deque
import sys
import threading

import serial
# from serial.tools import list_ports

def dump_port_settings(ser):
    print("\n--- Settings: {p.name}  {p.baudrate},{p.bytesize},{p.parity},{p.stopbits}\n".format(
        p=ser),end="")
    print('--- RTS: {:8}  DTR: {:8}  BREAK: {:8}\n'.format(
        ('active' if ser.rts else 'inactive'),
        ('active' if ser.dtr else 'inactive'),
        ('active' if ser.break_condition else 'inactive')),end="")
    try:
        print('--- CTS: {:8}  DSR: {:8}  RI: {:8}  CD: {:8}\n'.format(
            ('active' if ser.cts else 'inactive'),
            ('active' if ser.dsr else 'inactive'),
            ('active' if ser.ri else 'inactive'),
            ('active' if ser.cd else 'inactive')),end="")
    except ser.SerialException:
        # Ignorar eror ocurrido en puertos RFC 2217 cuando no hsa sido recibida la notificacion del estado.
        pass
    print('--- software flow control(xonxoff): {}\n'.format('active' if ser.xonxoff else 'inactive'),end="")
    print('--- software flow control(dsrdtr): {}\n'.format('active' if ser.dsrdtr else 'inactive'),end="")
    print('--- software flow control(rtscts): {}\n'.format('active' if ser.rtscts else 'inactive'),end="")

 
def main(port='/dev/ttyUSB0', baudrate=9600,databit=8, stopbit=1,parity='N', dsrdtr=False, rtscts=False,xonxoff=False):
    import argparse

    parser = argparse.ArgumentParser(
        description='Miniterm - A simple terminal program for the serial port.')

    parser.add_argument(
        'port',
        nargs='?',
        help='serial port name ',
        default=port)

    parser.add_argument(
        'baudrate',
        nargs='?',
        type=int,
        help='set baud rate, default: %(default)s',
        default=baudrate)

    group = parser.add_argument_group('port settings')

    group.add_argument(
        '--databit',
        choices=[5,6,7,8],
        type=int,
        help='set databit, one of {5 6 7 8}, default: 8',
        default=databit)

    group.add_argument(
        '--stopbit',
        type=float,
        help='stopbit, one of {1 1.5 2}, default: 1.5',
        default=stopbit)

    group.add_argument(
        '--parity',
        choices=['N', 'E', 'O', 'S', 'M'],
        type=lambda c: c.upper(),
        help='set parity, one of {N E O S M}, default: N',
        default=parity)

    group.add_argument(
        '--xonxoff',
        action='store_true',
        help='enable software flow control (default off)',
        default=xonxoff)
    
    group.add_argument(
        '--dsrdtr',
        action='store_true',
        help=' Enable hardware (DSR/DTR) flow control',
        default=dsrdtr)
    
    group.add_argument(
        '--rtscts',
        action='store_true',
        help=' Enable hardware (RTS/CTS) flow control',
        default=rtscts)

    args = parser.parse_args()
    #print(args)

    try:
        device = serial.Serial(port=args.port,
                                baudrate=args.baudrate,
                                bytesize=args.databit,
                                stopbits=args.stopbit,
                                parity=args.parity,
                                xonxoff=args.xonxoff,
                                dsrdtr=args.dsrdtr, 
                                rtscts=args.rtscts,
                                timeout=0.1)
        #dump_port_settings(device)
    except Exception as e:
        print('Failed to open {} ---'.format(port))
        print(str(e))
        return 0

    #print('Port: {} is connected. Press Ctrl+] to quit ---'.format(args.port))
    print('Press Enter to continue ---')
    queue = deque()
    def read_input():
        if os.name == 'nt':
            from msvcrt import getch
        else:
            import tty
            import termios
            stdin_fd = sys.stdin.fileno()
            tty_attr = termios.tcgetattr(stdin_fd)
            tty.setraw(stdin_fd)
            getch = lambda: sys.stdin.read(1).encode()

        while device.is_open:
            ch = getch()
            if ch == b'\x1d':                   # 'ctrl + ]' to quit
                break
            else:  
                queue.append(ch)

        if os.name != 'nt':
            termios.tcsetattr(stdin_fd, termios.TCSADRAIN, tty_attr)


    thread = threading.Thread(target=read_input)
    thread.start()
    while thread.is_alive():
        try:
            length = len(queue)
            if length > 0:
                device.write(b''.join(queue.popleft() for _ in range(length)))

            line = device.readline()
            if line:
                print(line.decode(errors='replace'), end='', flush=True)
        except IOError:
            print('--- {} is disconnected ---'.format(port))
            break

    device.close()
    if thread.is_alive():
        print('--- Press R to reconnect the device, or press Enter to exit ---')
        thread.join()
        if queue and queue[0] in (b'r', b'R'):
            return 1
    return 0


if __name__ == "__main__":
    main()