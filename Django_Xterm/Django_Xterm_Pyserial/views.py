from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from .services import getAllPorts, openPort, removePort, on_serial, off_serial, off_all_serial, on_list_serial, off_list_serial, state_serial

from .models import User, Active_Device, Group, Group_NormalUser, PowerStrip, Status_Device, Group_Device
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm

import json

from datetime import datetime, timedelta
import pytz

from .dspW245 import SmartPlug
import sys


# Errores custom
def my_bad_request_found_view(request, exception):
    return render(request, 'Django_Xterm_Pyserial/Errors/400.html', status=400)

def my_not_authorized_view(request, exception):
    return render(request, 'Django_Xterm_Pyserial/Errors/401.html', status=401)

def my_forbidden_view(request, exception):
    return render(request, 'Django_Xterm_Pyserial/Errors/403.html', status=403)

def my_page_not_found_view(request, exception):
    return render(request, 'Django_Xterm_Pyserial/Errors/404.html', status=404)

def my_page_server_error_view(request):
    return render(request, 'Django_Xterm_Pyserial/Errors/500.html', status=500)

def my_service_unavailable_view(request, exception):
    return render(request, 'Django_Xterm_Pyserial/Errors/503.html', status=503)


# View para log_in
def Index(request):
    if(request.method == "POST"):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('ControlPanel')
        else:
            return render(request,'Django_Xterm_Pyserial/Index.html', {'error': 'true'})

    return render(request,'Django_Xterm_Pyserial/Index.html',{})


# Botón log_out
@login_required(login_url='Index')
def Logout_view (request):
    logout(request)

    return redirect('Index')


# Otra manera de poner junto urls.py para cambiar el password
class Change_Password (PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy ('Change_Password_Done')

# Cuando la contraseña se cambia vuelve al log_in
@login_required(login_url='Index')
def Change_Password_Done(request):
    messages.success(request,"Password changed successfully.")
    return redirect('Index')


# Sacar a las regletas connectadas por serial de los serial que se muestran en Control Panel
def network_devices():

    initial_devices = getAllPorts()

    ps_serial = PowerStrip.objects.filter(Connected_In__in = initial_devices)

    l_ps = []
    for device in ps_serial:
        l_ps.append(device.Connected_In)

    net_dev = [i for i in initial_devices if not i in l_ps or l_ps.remove(i)]

    return net_dev


# Actualizar la BD con los network devices que hay en ese momento 
def update_DB_devices(list_devices_moment):

    for item in Status_Device.objects.all():
        if item.Device not in list_devices_moment:
            Status_Device.objects.get(Device = item.Device).delete()

    for d in list_devices_moment:
        # Comprobar si existe ya en la BD
        if not Status_Device.objects.filter(Device = d).exists():
            number = d[11:]
            name = "Device " + number
            Status_Device.objects.create(DeviceName = name, Device = d)

    
# Panel de control tanto para porfessor como para student
@login_required(login_url='Index')
def ControlPanel(request, Name=None):
    current_user = request.user

    initial_devices = network_devices()
    update_DB_devices(initial_devices)

    if current_user.is_professor:
        PowerStrips = PowerStrip.objects.all().order_by('Name')
        status = Status_Device.objects.all()

        return render(request,'Django_Xterm_Pyserial/Homepage.html', {'status' : status, 'powstrps': PowerStrips, 'NameSearch': Name, 'user' : current_user})
    
    else:
        normalUserID = current_user.id
        normalUser = User.objects.get(pk = normalUserID)
        groupsUser = Group_NormalUser.objects.filter(User = normalUser).values('Group')

        groupsDevice = Group_Device.objects.filter(Group__in = groupsUser)

        groupDevicerow = []
        for row in groupsDevice:
            groupDevicerow.append(row.Status_Device)

        status = Status_Device.objects.filter(Device__in = groupDevicerow).distinct()

        return render(request,'Django_Xterm_Pyserial/Homepage.html', {'status' : status, 'NameSearch': Name, 'user' : current_user})


# Añadir Power strip a la DB
@login_required(login_url='Index')
def AddPowerStrip(request):

    if request.method == "POST":
        response = ""
        name = request.POST.get('name')
        sockets = request.POST.get('sockets')
        type_connect = request.POST.get('type_connect')

        try:
            powerstripName = PowerStrip.objects.get(Name = name)
        except ObjectDoesNotExist:
            powerstripName = None

        if powerstripName == None:
            if type_connect == 'true':

                ip_powerstrip = request.POST.get('ip_powerstrip')
                pin = request.POST.get('pin')

                try:
                    powerstripIP = PowerStrip.objects.get(Ip = ip_powerstrip)
                except ObjectDoesNotExist:
                    powerstripIP = None

                if powerstripIP == None:
                    PowerStrip.objects.create(Name = name, Sockets=sockets, Has_wifi=True, Ip=ip_powerstrip, Pin=pin)
                    response = "ok"
                else:
                    response = "existip"
            elif type_connect == 'false':
                device_powerstrip = request.POST.get('device_powerstrip')

                try:
                    powerstripDevice = PowerStrip.objects.get(Connected_In = device_powerstrip)
                except ObjectDoesNotExist:
                    powerstripDevice = None

                if powerstripDevice == None:
                    PowerStrip.objects.create(Name = name, Sockets=sockets, Has_wifi=False, Connected_In=device_powerstrip)
                    response = "ok"
                else:
                    response = "existdevice"
        else:
            response = "existname"
    
    return JsonResponse({'response' : response})


# Todos los power strips de la BD (Para el select del modal de borrar en Control Panel)
@login_required(login_url='Index')
def GetAllPowerStrips(request):

    if request.method == "GET":
        PowerStrips = PowerStrip.objects.all()
        powerstrips = []
        for ps in PowerStrips:
            powerstrips.append(ps.Name)
        
    return JsonResponse({'ps': powerstrips})


# Nueva ventana para mostrar y editar todos los Power strips
@login_required(login_url='Index')
def PowerStrips(request):
    
    if not request.user.is_professor:
        raise PermissionDenied
    else:    
        current_user = request.user
        Ps = PowerStrip.objects.all()
            
        return render(request,'Django_Xterm_Pyserial/Powerstrips.html', { 'PowerStrips' : Ps, 'user' : current_user})


# Editar en la nueva ventana individualmente
@login_required(login_url='Index')
def EditPowerStrip(request): 

    if request.method == "POST":
        response = ""
        ant_name = request.POST.get('ant_name')
        name = request.POST.get('name')
        type_connect = request.POST.get('type_connect')

        powerstripAnt = PowerStrip.objects.get(Name = ant_name)

        if ant_name != name:
            try:
                powerstripName = PowerStrip.objects.get(Name = name)
            except ObjectDoesNotExist:
                powerstripName = None
        else:
            powerstripName = None

        if powerstripName == None:  #No existe otro con el nuevo nombre
            if type_connect == 'true':
                ip_powerstrip = request.POST.get('ip_powerstrip')
                pin = request.POST.get('pin')

                if powerstripAnt.Ip != ip_powerstrip: #No existe otro con la nueva Ip
                    try:
                        powerstripIP = PowerStrip.objects.get(Ip = ip_powerstrip)
                    except ObjectDoesNotExist:
                        powerstripIP = None
                else:
                    powerstripIP = None

                if powerstripIP == None:
                    powerstripAnt.Name = name
                    powerstripAnt.Has_wifi = True 
                    powerstripAnt.Ip = ip_powerstrip 
                    powerstripAnt.Pin = pin
                    powerstripAnt.Connected_In = None
                    powerstripAnt.save()
                    
                    response = "ok"
                else:
                    response = "existip"
            elif type_connect == 'false':
                device_powerstrip = request.POST.get('device_powerstrip')

                if powerstripAnt.Connected_In != device_powerstrip:
                    try:
                        powerstripDevice = PowerStrip.objects.get(Connected_In = device_powerstrip)
                    except ObjectDoesNotExist:
                        powerstripDevice = None
                else:
                    powerstripDevice = None

                if powerstripDevice == None:
                    powerstripAnt.Name = name
                    powerstripAnt.Has_wifi = False 
                    powerstripAnt.Connected_In = device_powerstrip
                    powerstripAnt.Ip = None 
                    powerstripAnt.Pin = None
                    powerstripAnt.save()
                
                    response = "ok"
                else:
                    response = "existdevice"
        else:
            response = "existname"
    
    return JsonResponse({'response' : response})


# Funciones para apagar y encender power strips con wifi (No solo reset)
def turn_off_reset_wifi(ip,key,socket):
    outcome = ""
    try:
        sp = SmartPlug(ip, key)
        sp.set_socket(socket, on=False)
        sp.close()
        outcome = "ok"
    except:
        outcome = "Error - " + str(sys.exc_info()[1]) + "."

    return outcome

def turn_on_reset_wifi(ip,key,socket):
    outcome = ""
    try:
        sp = SmartPlug(ip, key)
        sp.set_socket(socket, on=True)
        sp.close()
        outcome = "ok"
    except:
        outcome = "Error - " + str(sys.exc_info()[1]) + "."

    return outcome

def turn_off_reset_wifi_all(ip,key,sockets):
    outcome = ""
    try:
        sp = SmartPlug(ip, key)
        for i in range(sockets):
            sp.set_socket(i+1, on=False)
        sp.close()
        outcome = "ok"
    except:
        outcome = "Error - " + str(sys.exc_info()[1]) + "."

    return outcome

def turn_on_reset_wifi_all(ip,key,sockets):
    outcome = ""
    try:
        sp = SmartPlug(ip, key)
        for i in range(sockets):
            sp.set_socket(i+1, on=True)
        sp.close()
        outcome = "ok"
    except:
        outcome = "Error - " + str(sys.exc_info()[1]) + "."

    return outcome

def turn_off_reset_wifi_list(ip,key,listsokects):
    outcome = ""
    try:
        sp = SmartPlug(ip, key)
        for i in listsokects:
            sp.set_socket(i, on=False)
        sp.close()
        outcome = "ok"
    except:
        outcome = "Error - " + str(sys.exc_info()[1]) + "."

    return outcome

def turn_on_reset_wifi_list(ip,key,listsokects):
    outcome = ""
    try:
        sp = SmartPlug(ip, key)
        for i in listsokects:
            sp.set_socket(i, on=True)
        sp.close()
        outcome = "ok"
    except:
        outcome = "Error - " + str(sys.exc_info()[1]) + "."

    return outcome

def state_socket_wifi(ip,key,socket):
    outcome = ""
    try:
        sp = SmartPlug(ip, key)
        state = sp.get_state(socket)
        sp.close()
        outcome = state
    except:
        outcome = "Error - " + str(sys.exc_info()[1]) + "."

    return outcome


# Borrar Power strip y apaga
@login_required(login_url='Index')
def DeletePowerStrip(request):  

    if request.method == "POST":
        psList = request.POST.getlist('psList[]') 

        for psele in psList:
            ps = PowerStrip.objects.get(Name = psele)

            if ps.Has_wifi:
                turn_off_reset_wifi_all(ps.Ip, ps.Pin, ps.Sockets)
            else:
                off_all_serial(ps.Connected_In)

            sList = Status_Device.objects.filter(PowerStrip = ps)
            for s in sList:
                s.StatusDevice = None
                s.Socket = None
                s.save()
        
            ps.delete()

        
        response ="ok"
        
    else:
        response ="error"
    
    return JsonResponse({'response' : response})


# Borrar todos los Power strip y los apaga
@login_required(login_url='Index')
def DeleteAllPowerStrip(request):  

    if request.method == "POST":
        psl = PowerStrip.objects.all()

        if psl:
            for ps in psl:

                if ps.Has_wifi:
                    turn_off_reset_wifi_all(ps.Ip, ps.Pin, ps.Sockets)
                else:
                    off_all_serial(ps.Connected_In)

                sList = Status_Device.objects.filter(PowerStrip = ps)
                for s in sList:
                    s.StatusDevice = None
                    s.Socket = None
                    s.save()
                
                ps.delete()
            
            response ="ok"
        else:
            response ="nops"
    else:
        response ="error"
    
    return JsonResponse({'response' : response})


# Asigna Power strip a un device y apaga el socket si estaba en alguno
@login_required(login_url='Index')
def SelectedPowerStrip(request): 

    if request.method == "POST":
        DeviceName = request.POST.get('DeviceName')
        PowerStripName = request.POST.get('PowerStripName')

        s = Status_Device.objects.get(Device = DeviceName)

        if PowerStripName == 'None':
            # Mandar señal de apagado al strip de s al s.socket
            if s.PowerStrip.Has_wifi:
                turn_off_reset_wifi(s.PowerStrip.Ip, s.PowerStrip.Pin, s.Socket)
            else:
                off_serial(s.PowerStrip.Connected_In, str(s.Socket))
            
            s.PowerStrip = None
            s.Socket = None
            s.StatusDevice = None
            s.save()

            response ="oktonone"

        else:
            p = PowerStrip.objects.get(Name = PowerStripName)
            # Mandar señal de apagado al strip de s al s.socket cuando no es el primer caso, cuando ya esta asociado a alguno si no genera error (No hay datos)
            if s.PowerStrip != None:
                if s.PowerStrip.Has_wifi:
                    turn_off_reset_wifi(s.PowerStrip.Ip, s.PowerStrip.Pin, s.Socket)
                else:
                    off_serial(s.PowerStrip.Connected_In, str(s.Socket))

            s.PowerStrip = p
            s.Socket = None
            s.StatusDevice = None
            s.save()

            response = "ok"

    
    return JsonResponse({'response' : response})


# Asigna Socket a un device y apaga el socket si estaba en alguno (Si ya esta cogido, avisa)
@login_required(login_url='Index')
def SelectedSocket(request): 

    if request.method == "POST":
        DeviceName = request.POST.get('DeviceName')
        sk = request.POST.get('sk')

        s = Status_Device.objects.get(Device = DeviceName)

        if sk != 'None':
            #Se busca si existe otro device con el mismo powerstrip y socket ya asignado
            ske = Status_Device.objects.filter(PowerStrip = s.PowerStrip).filter(Socket = sk)

            if ske:
                response = "skexist"
            else:
                #Mandar señal de apagado
                #Comprobar estado del socket al que vamos a cambiar
                if s.PowerStrip.Has_wifi:
                    st = state_socket_wifi(s.PowerStrip.Ip, s.PowerStrip.Pin, int(sk))
                    if st == 0:
                        state = "off"
                    elif st == 1:
                        state = "on"
                    else:
                        state = None
                else:
                    st = state_serial(s.PowerStrip.Connected_In, sk)   #Devuelve string
                    if st[0] == "0":
                        state = "off"
                    elif st[0] == "1":
                        state = "on"
                    else:
                        state = None

                if s.Socket:  # Si pasamos de un socket a otro, apagar en el que estabamos
                    if s.PowerStrip.Has_wifi:
                        turn_off_reset_wifi(s.PowerStrip.Ip, s.PowerStrip.Pin, s.Socket)
                    else:
                        off_serial(s.PowerStrip.Connected_In, str(s.Socket))

                s.Socket = sk
                s.StatusDevice = state
                s.save()
                response = "ok"
        else:
            #Mandar señal de apagado al strip
            if s.PowerStrip.Has_wifi:
                turn_off_reset_wifi(s.PowerStrip.Ip, s.PowerStrip.Pin, s.Socket)
            else:
                off_serial(s.PowerStrip.Connected_In, str(s.Socket))

            s.Socket = None
            s.StatusDevice = None
            s.save()
            response ="oktonone"

    return JsonResponse({'response' : response})


# Apagar y encender individualmente
@login_required(login_url='Index')
def On_Off_Single(request): 

    if request.method == "POST":
        device = request.POST.get('device')

        d = Status_Device.objects.get(Device = device)

        if d.PowerStrip.Has_wifi:
            if d.StatusDevice == "on":
                outcome = turn_off_reset_wifi(d.PowerStrip.Ip, d.PowerStrip.Pin, d.Socket)
                if outcome == "ok":    
                    d.StatusDevice = "off"
                    d.save()
                elif outcome == "Error - None.":
                    outcome = "Error - Invalid device pin." 

            elif d.StatusDevice == "off":
                outcome = turn_on_reset_wifi(d.PowerStrip.Ip, d.PowerStrip.Pin, d.Socket)
                if outcome == "ok":    
                    d.StatusDevice = "on"
                    d.save()
                elif outcome == "Error - None.":
                    outcome = "Error - Invalid device pin." 
        else:
            if d.StatusDevice == "on":
                outcome = off_serial(d.PowerStrip.Connected_In, str(d.Socket))
                if outcome == "ok":    
                    d.StatusDevice = "off"
                    d.save()
                elif outcome == "Error":
                    outcome = "Error - No serial connection" 

            elif d.StatusDevice == "off":
                outcome = on_serial(d.PowerStrip.Connected_In, str(d.Socket))
                if outcome == "ok":    
                    d.StatusDevice = "on"
                    d.save()
                elif outcome == "Error":
                    outcome = "Error - No serial connection" 
    
    return JsonResponse({'response' : outcome})


# Apagar y encender todos los sockets de todas los Power strips
@login_required(login_url='Index')
def On_Off_All(request):

    if request.method == "POST":
        button = request.POST.get('state')
        dict_ps = {}
        dict_response = {}
        listsockets = []
        response = ""

        if Status_Device.objects.exists(): 
            ps = PowerStrip.objects.all()

            for pwst in ps:
                listsockets = []
                status = Status_Device.objects.filter(PowerStrip = pwst)
                if status:
                    for s in status:
                        if s.Socket != None:
                            listsockets.append(s.Socket)
                    if listsockets:
                        dict_ps[pwst] = listsockets
                    else:
                        dict_ps[pwst] = "No sockets"
                else:
                    dict_ps[pwst] = listsockets

            for key in dict_ps:
                if dict_ps[key]:
                    if dict_ps[key] == "No sockets":
                        dict_response[key.Name] = "Power strip with not sockets assigned"
                    else:
                        if key.Has_wifi: #wifi
                            if button == "on":
                                outcome = turn_on_reset_wifi_list(key.Ip, key.Pin, dict_ps[key])
                                if outcome == "ok":
                                    db_status = Status_Device.objects.filter(PowerStrip = key).filter(Socket__in = dict_ps[key])
                                    for s in db_status:
                                        if s.StatusDevice == "off":
                                            s.StatusDevice = "on"
                                            s.save()
                                elif outcome == "Error - None.":
                                    dict_response[key.Name] = "Error - Invalid device pin"        
                                else:
                                    dict_response[key.Name] = outcome

                            elif button == "off":
                                outcome = turn_off_reset_wifi_list(key.Ip, key.Pin, dict_ps[key])
                                if outcome == "ok":
                                    db_status = Status_Device.objects.filter(PowerStrip = key).filter(Socket__in = dict_ps[key])
                                    for s in db_status:
                                        if s.StatusDevice == "on":
                                            s.StatusDevice = "off"
                                            s.save()   
                                elif outcome == "Error - None.":
                                    dict_response[key.Name] = "Error - Invalid device pin" 
                                else:
                                    dict_response[key.Name] = outcome

                        else:  #Serial
                            if button == "on":
                                l_on = []
                                for k in dict_ps[key]:
                                    l_on.append(str(k))
                                    
                                outcome = on_list_serial(key.Connected_In, l_on)
                                
                                if outcome == "ok":
                                    db_status = Status_Device.objects.filter(PowerStrip = key).filter(Socket__in = dict_ps[key])
                                    for s in db_status:
                                        if s.StatusDevice == "off":
                                            s.StatusDevice = "on"
                                            s.save()
                                elif outcome == "Error":
                                    dict_response[key.Name] = "Error - No serial connection"        
                                else:
                                    dict_response[key.Name] = outcome

                            elif button == "off":
                                l_off = []
                                for k in dict_ps[key]:
                                    l_off.append(str(k))
                                    
                                outcome = off_list_serial(key.Connected_In, l_off)
                                
                                if outcome == "ok":
                                    db_status = Status_Device.objects.filter(PowerStrip = key).filter(Socket__in = dict_ps[key])
                                    for s in db_status:
                                        if s.StatusDevice == "on":
                                            s.StatusDevice = "off"
                                            s.save()   
                                elif outcome == "Error":
                                    dict_response[key.Name] = "Error - No serial connection" 
                                else:
                                    dict_response[key.Name] = outcome
                else:
                    dict_response[key.Name] = "Power strip not assigned"
        else:
            response = "empty"

    return JsonResponse({'dict_ps': dict_response, 'response': response})


# Boton para comprobar si esta siendo usado o apagado el device (Contador para borrar de la BD si un usuario pierde conexion y otro quiere conectarse)
@login_required(login_url='Index')
def CheckSerialPort(request):

    if request.method == "GET":
        current_user = request.user
        PortName = request.GET.get('PortName')
        email_user = ""
        time_re = 0

        s = Status_Device.objects.get(Device = PortName)

        try:
            Device = Active_Device.objects.get(ActiveDevicesName = PortName)
        except ObjectDoesNotExist:
            Device = None

        if (Device != None):
            time_elapsed = datetime.now(pytz.utc) - Device.Created_time

            s = time_elapsed.seconds
            hours, remainder = divmod(s, 3600)
            minutes, seconds = divmod(remainder, 60)

            time_re = str(hours) +"H:"+ str(minutes) +"M:"+ str(seconds)+"S"

            # Comprobación si active ya paso una hora y aun no ha sido borrado (2 min por el min que espera por la decision del user, seguir o no)
            if time_elapsed > timedelta(minutes=2, hours=1):
                Device.delete()
                removePort(PortName)
                response = "OK"

            else:
                email_user = Device.User_using
                response = "FOUND ACTIVE"

        elif (s.StatusDevice == "off"):
            response = "Device is off"

        elif (s.StatusDevice == None):
            if current_user.is_professor:
                response = "OK"
            else:
                response = "Device is None"  #"OK" si se deja conectarse en el estado de None (como a professor)

        else:
            response = "OK"

    else:
        response = "NOGET"
    
    return JsonResponse({'response' : response, 'time_elapsed': time_re, 'email_user': email_user})


#Bloquear el acceso directo escribiendo la direccion url en el buscador
def get_referer(r):
    referer = r.META.get('HTTP_REFERER')

    if not referer:
        return None
        
    return referer

# View para la pagina del Terminal
@login_required(login_url='Index')
def Terminal(request):
    
    if not request.user.is_professor:
        if not get_referer(request):
            raise PermissionDenied

    if request.method == "GET":
        PortName = request.GET.get('PortName')
        DeviceName = request.GET.get('DeviceName')
        BaudRate = request.GET.get('BaudRate')
        ByteSize = request.GET.get('ByteSize')
        StopBits = request.GET.get('StopBits')
        Parity = request.GET.get('Parity')
        FlowControl = request.GET.get('FlowControl')

        print(PortName)
        print(DeviceName)

    return render(request,'Django_Xterm_Pyserial/Terminal.html', {'PortName': PortName, 'DeviceName': DeviceName, 'BaudRate' : BaudRate, 'ByteSize' : ByteSize, 'StopBits' : StopBits, 'Parity': Parity, 'FlowControl': FlowControl})


# Funcion para el iframe, creación de la conexión serial
@login_required(login_url='Index')
def ConnectToSerialPort(request):

    if request.method == "POST":
        PortName = request.POST.get('PortName')
        BaudRate = request.POST.get('BaudRate')
        ByteSize = request.POST.get('ByteSize')
        StopBits = request.POST.get('StopBits')
        Parity = request.POST.get('Parity')
        FlowControl = request.POST.get('FlowControl')
        #obtener usuario
        current_user = request.user

        Active_Device.objects.create(ActiveDevicesName = PortName, User_using = current_user.email)   #Poner usuario, el tiempo se pone automat. cuando se crea la entrada
        openPort(portName=PortName, baudrate=BaudRate, bytesize=ByteSize, stopbits=StopBits, 
            parity=Parity, flowcontrol=FlowControl)

        response = "OK"

    else:
        response = "NOGET"
    
    return JsonResponse({'response' : response})


# Quitar de la BD Active_Device y eliminar proceso, de la conexión serial al cerrar
@login_required(login_url='Index')
def RemoveDevice(request):

    if request.method == 'POST':
        PortName = request.POST.get('PortName')

    try:
        Device = Active_Device.objects.get(ActiveDevicesName = PortName)
        Device.delete()
        removePort(PortName)

    except ObjectDoesNotExist:
        Device = None

    return JsonResponse({'data' : 'OK'})


# Vista pagina Groups
@login_required(login_url='Index')
def Groups(request, Name=None):

    if not request.user.is_professor:
        raise PermissionDenied
    else:
        #Mismo que en control panel para poner y quitar de Status.
        initial_devices = network_devices()
        update_DB_devices(initial_devices)

        current_user = request.user
        Groups = Group.objects.filter(User = request.user.id).order_by('Name')
        group_list = []

        for obj in Groups:
            data = {'name': obj.Name, 'pk': obj.id}

            users = obj.group_normaluser_set.all().values_list('User__email')  #email
            users = ','.join([x[0] for x in users.iterator()])
            users = users.split(',')

            devices = obj.group_device_set.all().values_list('Status_Device__Device')
            devices = ','.join([x[0] for x in devices.iterator()])
            devices = devices.split(',')

            data['devices'] = devices
            data['users'] = users

            group_list.append(data)

        return render(request,'Django_Xterm_Pyserial/Groups.html', {'Groups' : group_list, 'user' : current_user, 'NameSearch': Name})


# Students y network devices del momento para los selects del modal de la crecion y edicion 
@login_required(login_url='Index')
def GetAllNormalUsersAndDevices(request):

    if request.method == "GET":
        devices = []
        normalusers = []

        NormalUsers = User.objects.filter(is_professor = False).filter(is_staff = False).order_by("email")

        for user in NormalUsers:
            normalusers.append(user.email)   #email

        devices = network_devices()

        return JsonResponse({'Users': normalusers, 'Devices': devices})


# Cración de un grupo (Ya sea por create o por edit)
@login_required(login_url='Index')
def AddGroup(request):

    if request.method == "POST":
        userList = request.POST.getlist('userList[]')
        devicesList = request.POST.getlist('devicesList[]')
        groupName = request.POST.get('groupName')
        superuser = request.user.id
        to_do = request.POST.get('to_do')

        if to_do == 'edit':
            group = Group.objects.filter(Name = groupName).filter(User = superuser)
            currentGroup = group[0]

            gu = Group_NormalUser.objects.filter(Group = currentGroup)

            # Borrar de la BD los que no esten presentes en la lista de nuevos
            for itemu in gu:
                if itemu.User not in userList:
                    Group_NormalUser.objects.get(User = itemu.User, Group= currentGroup).delete()

            # Añadir a la BD los que no esten en ella y si en la lista de nuevos
            nu = User.objects.filter(email__in=userList)

            for u in nu:
                if not Group_NormalUser.objects.filter(User = u).filter(Group = currentGroup).exists():
                    Group_NormalUser.objects.create(User = u, Group = currentGroup)   


            gd = Group_Device.objects.filter(Group = currentGroup)

            for itemd in gd:
                if itemd.Status_Device not in devicesList:
                    Group_Device.objects.get(Status_Device = itemd.Status_Device, Group= currentGroup).delete()

            nd = Status_Device.objects.filter(Device__in = devicesList)

            for d in nd:
                if not Group_Device.objects.filter(Status_Device = d).filter(Group = currentGroup).exists():
                    Group_Device.objects.create(Status_Device = d, Group = currentGroup)       

            response = "edited"
       
        else:
            try:
                group = Group.objects.get(Name = groupName, User= superuser)
            except ObjectDoesNotExist:
                group = None

            if (group != None):
                response = "group"
            else:
                normalUsers = User.objects.filter(email__in = userList)  #email
                devicesListgroup = Status_Device.objects.filter(Device__in = devicesList)

                Group.objects.create(Name = groupName, User = User.objects.get(pk = request.user.id))
                currentGroup = Group.objects.filter(Name = groupName).filter(User = superuser)
                currentGroup = currentGroup[0]

                for user in normalUsers:
                    Group_NormalUser.objects.create(User = user, Group = currentGroup)

                for device in devicesListgroup:
                    Group_Device.objects.create(Status_Device = device, Group = currentGroup)

                response = "created"
                
    return JsonResponse({'response': response})


# Mezclar grupo nuevo y grupo con el que coincide en el nombre
@login_required(login_url='Index')
def AddGroupMerge(request):

    if request.method == "POST":
        toadduserList = request.POST.getlist('userList[]')
        toadddevicesList = request.POST.getlist('devicesList[]')
        groupName = request.POST.get('groupName')
        superuser = request.user.id

        groups = Group.objects.filter(Name = groupName).filter(User = superuser)
        group = groups[0]

        # Añadir a la BD los que no esten en ella y si en la lista de nuevos
        nu = User.objects.filter(email__in=toadduserList)

        for u in nu:
            if not Group_NormalUser.objects.filter(User = u).filter(Group = group).exists():
                Group_NormalUser.objects.create(User = u, Group = group) 

        nd = Status_Device.objects.filter(Device__in = toadddevicesList)

        for d in nd:
            if not Group_Device.objects.filter(Status_Device = d).filter(Group = group).exists():
                Group_Device.objects.create(Status_Device = d, Group = group)       
            
        response = "OK"
                
    return JsonResponse({'response': response})


# Borrando el grupo existente y guardando el nuevo cuando el nombre coincide
@login_required(login_url='Index')
def AddGroupDelB(request):

    if request.method == "POST":
        userList = request.POST.getlist('userList[]')
        devicesList = request.POST.getlist('devicesList[]')
        groupName = request.POST.get('groupName')
        superuser = request.user.id

        try:
            group = Group.objects.filter(Name = groupName).filter(User = superuser).delete()
            Group_NormalUser.objects.filter(Group = group).delete()
            Group_Device.objects.filter(Group = group).delete()

        except:
            pass

        finally:
            normalUsers = User.objects.filter(email__in = userList)  #email
            devicesListgroup = Status_Device.objects.filter(Device__in = devicesList)

            Group.objects.create(Name = groupName, User = User.objects.get(pk = request.user.id))
            currentGroup = Group.objects.filter(Name = groupName).filter(User = superuser)
            currentGroup = currentGroup[0]

            for user in normalUsers:
                Group_NormalUser.objects.create(User = user, Group = currentGroup)
            for device in devicesListgroup:
                Group_Device.objects.create(Status_Device = device, Group = currentGroup)
                
            return JsonResponse({'data' : 'OK'})
        

# Obtener elementos pertenecientes al grupo
@login_required(login_url='Index')
def EditGroup(request):

    if request.method == "GET":
        groupId = request.GET.get('groupId')
        group = Group.objects.filter(pk=groupId)

        groupNormalUsers = Group_NormalUser.objects.filter(Group = group[0])
        users = []
        normalUsers = {}
        for user in groupNormalUsers:
            users.append(user.User)

        for user in users:
            normalUsers[user.pk] = user.email   #email

        groupDevices = Group_Device.objects.filter(Group = group[0])
        devicesBefore = []
        devices = {}
        for device in groupDevices:
            devicesBefore.append(device.Status_Device)

        for device in devicesBefore:
            devices[device.pk] = device.Device

        return JsonResponse({'devices' : devices, 'normalUsers' : normalUsers})


# Eliminar grupo
@login_required(login_url='Index')
def DeleteGroup(request):

    if request.method == "POST":
        Group.objects.filter(pk = request.POST.get('groupId')).delete()
    return JsonResponse({'data' : 'OK'})


# Añadir grupos desde un json
@login_required(login_url='Index')
def AddGroupsFile(request):

    if request.method == "POST":
        uploaded_file = request.FILES['file']  #Ya abierto, no hace falta with to open y load el json

        try:  #Comprobación si el archivo es json
            jsonObject = json.load(uploaded_file)
        
        except:
            response = "No_json"
            return JsonResponse({'response': response})

        noInGroups = {"groups": []}  #Diccionario con los elemtos no existentes en el caso de que exista alguno


        if "groups" in jsonObject:
            NormalUsers = User.objects.filter(is_professor = False).filter(is_staff = False)
            normalusers = []
            for user in NormalUsers:
                normalusers.append(user.email)  #email

            devices = network_devices()

            duplicateGroupName = []

            for i in jsonObject["groups"]:  #Comprobación si los nombres ya esxiten en la BD
                groupName = i["name"]

                try:
                    group = Group.objects.get(Name = groupName, User = request.user.id)
                except ObjectDoesNotExist:
                    group = None

                if (group != None):
                    duplicateGroupName.append(group.Name)

            if not duplicateGroupName:
                for i in jsonObject["groups"]:
                    no_user = []
                    no_device = []

                    userList = i["users"]
                    devicesList = i["devices"]
                    groupName = i["name"]

                    for u in userList:         # Comprobacion de si existen
                        if u not in normalusers:
                            no_user.append(u)
                            userList.remove(u)

                    for d in devicesList:
                        if d not in devices:
                            no_device.append(d)
                            devicesList.remove(d)

                    if no_user or no_device:
                        noInGroups["groups"].append({
                        "name": groupName,
                        "users": no_user,
                        "devices": no_device})

                    try:
                        group = Group.objects.filter(Name = groupName).filter(User = request.user.id).delete()
                        Group_NormalUser.objects.filter(Group = group).delete()
                        Group_Device.objects.filter(Group = group).delete()

                    except:
                        pass

                    finally:
                        normalUsers = User.objects.filter(email__in = userList)  #email
                        devicesListgroup = Status_Device.objects.filter(Device__in = devicesList)

                        Group.objects.create(Name = groupName, User = User.objects.get(pk = request.user.id))
                        currentGroup = Group.objects.filter(Name = groupName).filter(User = request.user.id)
                        currentGroup = currentGroup[0]

                        for user in normalUsers:
                            Group_NormalUser.objects.create(User = user, Group = currentGroup)
                        for device in devicesListgroup:
                            Group_Device.objects.create(Status_Device = device, Group = currentGroup)
                    
                if noInGroups["groups"]:
                    response = "Not_empty"
                else:
                    response = "Empty"
            else:
                response = "group"
        else:
            response = "Nogroups"

    return JsonResponse({'response': response, 'noexist':noInGroups})


# Añadir grupos desde un json, en el caso de que el user quiera mezclarlos cuando hay nombres iguales
@login_required(login_url='Index')
def Merge_File(request):

    if request.method == "POST":
        uploaded_file = request.FILES['file']  

        try:
            jsonObject = json.load(uploaded_file)
        
        except:
            response = "No_json"
            return JsonResponse({'response': response})

        NormalUsers = User.objects.filter(is_professor = False).filter(is_staff = False)
        normalusers = []
        for user in NormalUsers:
            normalusers.append(user.email)  #email

        devices = network_devices()

        noInGroups = {"groups": []}

        for i in jsonObject["groups"]:
            no_user = []
            no_device = []

            userList = i["users"]
            devicesList = i["devices"]
            groupName = i["name"]

            for u in userList:      
                if u not in normalusers:
                    no_user.append(u)
                    userList.remove(u)

            for d in devicesList:
                if d not in devices:
                    no_device.append(d)
                    devicesList.remove(d)

            if no_user or no_device:
                noInGroups["groups"].append({
                "name": groupName,
                "users": no_user,
                "devices": no_device})

            #Cuando en el json viene uno no duplicado
            groups = Group.objects.filter(Name = groupName).filter(User = request.user.id) 
            if groups: #Duplicado
                group = groups[0]

                # Añadir a la BD los que no esten en ella y si en la lista de nuevos
                nu = User.objects.filter(email__in=userList)

                for u in nu:
                    if not Group_NormalUser.objects.filter(User = u).filter(Group = group).exists():
                        Group_NormalUser.objects.create(User = u, Group = group) 

                nd = Status_Device.objects.filter(Device__in = devicesList)

                for d in nd:
                    if not Group_Device.objects.filter(Status_Device = d).filter(Group = group).exists():
                        Group_Device.objects.create(Status_Device = d, Group = group)    

            else: # No Duplicado
                normalUsers = User.objects.filter(email__in = userList)
                devicesListgroup = Status_Device.objects.filter(Device__in = devicesList)

                Group.objects.create(Name = groupName, User = User.objects.get(pk = request.user.id))
                currentGroup = Group.objects.filter(Name = groupName).filter(User = request.user.id)
                currentGroup = currentGroup[0]

                for user in normalUsers:
                    Group_NormalUser.objects.create(User = user, Group = currentGroup)
                for device in devicesListgroup:
                    Group_Device.objects.create(Status_Device = device, Group = currentGroup)
            
        if noInGroups["groups"]:
            response = "Not_empty"
        else:
            response = "Empty"

    return JsonResponse({'response': response, 'noexist':noInGroups})


# Borrando el grupo existente y guardando el nuevo cuando el nombre coincide, con archivo json
@login_required(login_url='Index')
def Delete_Before_File(request): 

    if request.method == "POST":
        uploaded_file = request.FILES['file']  

        try:  
            jsonObject = json.load(uploaded_file)
        
        except:
            response = "No_json"
            return JsonResponse({'response': response})

        NormalUsers = User.objects.filter(is_professor = False).filter(is_staff = False)
        normalusers = []
        for user in NormalUsers:
            normalusers.append(user.email)  

        devices = network_devices()

        noInGroups = {"groups": []}  

        for i in jsonObject["groups"]:
            no_user = []
            no_device = []

            userList = i["users"]
            devicesList = i["devices"]
            groupName = i["name"]

            for u in userList:        
                if u not in normalusers:
                    no_user.append(u)
                    userList.remove(u)

            for d in devicesList:
                if d not in devices:
                    no_device.append(d)
                    devicesList.remove(d)

            if no_user or no_device:
                noInGroups["groups"].append({
                "name": groupName,
                "users": no_user,
                "devices": no_device})

            try: 
                group = Group.objects.filter(Name = groupName).filter(User = request.user.id).delete()
                Group_NormalUser.objects.filter(Group = group).delete()
                Group_Device.objects.filter(Group = group).delete()

            except:
                pass

            finally:
                normalUsers = User.objects.filter(email__in = userList)  #email
                devicesListgroup = Status_Device.objects.filter(Device__in = devicesList)

                Group.objects.create(Name = groupName, User = User.objects.get(pk = request.user.id))
                currentGroup = Group.objects.filter(Name = groupName).filter(User = request.user.id)
                currentGroup = currentGroup[0]

                for user in normalUsers:
                    Group_NormalUser.objects.create(User = user, Group = currentGroup)
                for device in devicesListgroup:
                    Group_Device.objects.create(Status_Device = device, Group = currentGroup)
            
        if noInGroups["groups"]:
            response = "Not_empty"
        else:
            response = "Empty"

    return JsonResponse({'response': response, 'noexist':noInGroups})


# Borrado de todos los grupos asociados al professor logeado
@login_required(login_url='Index')
def DeleteAllGroups(request):

    if request.method == "POST":
        superuser = request.user.id
        Group.objects.filter(User = superuser).delete()
        
    return JsonResponse({'data' : 'OK'})


# Vista para los usuarios
@login_required(login_url='Index')
def Students(request, Name=None):

    if not request.user.is_professor:
        raise PermissionDenied
    else:   
        current_user = request.user
        students = User.objects.filter(is_professor=False).filter(is_staff=False).order_by("last_name")
        Groups = {"groups": []}
        Using_devices = {"devices_used": []}

        for student in students:
            list_groups_names_student = []
            list_devices_names_student = []
            groups = Group_NormalUser.objects.filter(User = student)
            actives = Active_Device.objects.filter(User_using = student.email)

            for group in groups:
                group = Group.objects.get(id = group.Group_id)
                list_groups_names_student.append(group.Name)

            Groups["groups"].append({ "student": student.email, "group": list_groups_names_student})

            for active in actives:
                device = Status_Device.objects.get(Device = active.ActiveDevicesName)
                list_devices_names_student.append(device.Device)

            Using_devices["devices_used"].append({ "student": student.email, "actives": list_devices_names_student})

        return render(request,'Django_Xterm_Pyserial/Students.html', { 'students' : students, 'Groups': Groups, 'Using_devices': Using_devices, 'NameSearch': Name, 'user' : current_user})


# Creación de un usuario
@login_required(login_url='Index')
def CreateStudent(request):

    if request.method == "POST":
        Email = request.POST.get('email')
        Password = request.POST.get('password')
        First_Name = request.POST.get('first_name')
        Last_Name = request.POST.get('last_name')

        try:
            s = User.objects.get(email = Email)
        except ObjectDoesNotExist:
            s = None

        if (s == None):
            User.objects.create_user(email = Email, password = Password, first_name = First_Name,
                last_name = Last_Name)
            response = "ok"
        else:
            response = "exist"

    else:
        response = "NOPE"
    
    return JsonResponse({'response' : response})


# Upload json, lo lee y añade, devolviendo si hay algun error
@login_required(login_url='Index')
def AddStudentsFile(request):

    if request.method == "POST":
        uploaded_file = request.FILES['file']  #Ya abierto, no hace falta with to open y load el json

        try:  #Check si el archivo es json
            jsonObject = json.load(uploaded_file)
        
        except:
            response = "No_json"
            return JsonResponse({'response': response})

        InUsers = []  # Lista con los usuarios en el caso de que ya existan.

        if "users" in jsonObject: # Comprueba si el json contiene users
            NormalUsers = User.objects.filter(is_professor = False).filter(is_staff = False)
            normalusers = []
            for user in NormalUsers:
                normalusers.append(user.email)  #email

            for i in jsonObject["users"]:
                userEmail = i["email"]
                userPassword = i["password"]
                userFirst_Name = i["first_name"]
                userLast_Name = i["last_name"]

                if userEmail in normalusers:  # Comprueba si el usuario esta en la lista de los que existen
                    InUsers.append(userEmail)
                
                else:
                    User.objects.create_user(email = userEmail, password = userPassword, first_name = userFirst_Name,
                    last_name = userLast_Name)

            if InUsers:
                response = "Not_empty"
            else:
                response = "Empty"
        else:
            response = "Nousers"

    
    return JsonResponse({'response': response, 'noexist':InUsers})


# Borrar students seleccionados 
@login_required(login_url='Index')
def DeleteStudents(request):

    if request.method == "POST":
        list_users = request.POST.getlist("list[]")

        for user_email in list_users:
            User.objects.filter(email = user_email).delete()
        
    return JsonResponse({'data' : 'OK'})
