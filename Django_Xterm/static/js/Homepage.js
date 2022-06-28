//Se pierde Internet
function Lost_internet() {
    $('#modal-alert-lost').modal({ backdrop: 'static', keyboard: false });
    $('#modal-alert-lost').modal('show');
};

//Vuelve
function Internet_back() {
    $('#modal-alert-lost').modal('hide');
};


// Mostrar boton cuando el usuario haga scroll hacia abajo
function Show_totop() {
    let mybutton = document.getElementById("to-top");

    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        mybutton.style.display = "block";
    } else {
        mybutton.style.display = "none";
    }
};

function topFunction() { //Boton hacia arriba
    document.body.scrollTop = 0; // Para Safari
    document.documentElement.scrollTop = 0; // Para Chrome, Firefox, IE y Opera
}


//Cambio de temas cuando se pulsa el boton dentro del nombre del usuario
function initTheme() {
    var darkThemeSelected = localStorage.getItem("darkSwitch") !== null && localStorage.getItem("darkSwitch") === "dark";
    darkSwitch.checked = darkThemeSelected;
    darkThemeSelected ? document.body.setAttribute("data-theme", "dark") : document.body.removeAttribute("data-theme");
}

function resetTheme() {
    if (darkSwitch.checked) {
        document.body.setAttribute("data-theme", "dark");
        localStorage.setItem("darkSwitch", "dark");
    } else {
        document.body.removeAttribute("data-theme");
        localStorage.removeItem("darkSwitch");
    }
}

function Change_theme(darkSwitch) {
    if (darkSwitch) {
        initTheme();
        darkSwitch.addEventListener("change", function() {
            resetTheme();
        });
    }
};


//Scroll cuando viene de groups
function Hover_device(deviceName, user) {
    if (user == "True") {
        if (deviceName != "None") {
            hover = document.getElementById("card_" + deviceName);
            if (hover != null)
                hover.scrollIntoView();
        }
    }
}


//Modal para las alertas y, en el caso que sea necessario, actualizar pagina
function Alert_modal(text, address) {
    let modal_body = document.getElementById('modal-body-alert');
    while (modal_body.firstChild) {
        modal_body.removeChild(modal_body.firstChild);
    }

    let modal_message = document.createElement("p");
    modal_message.setAttribute('id', 'p-modal-alert')
    modal_message.innerHTML = text;
    modal_body.appendChild(modal_message);
    $('#modal-alert').modal('show');

    if (address.length !== 0) {
        $('#modal-alert').on('hidden.bs.modal', function() {
            window.location.href = address;
        })
    }
}


//Para variar la altura de las cards, ya que si se pone fija, cuando desaparece los selects queda hueco blanco
function Cards_height(card) {
    let device = card.id.slice(5);
    let sel = document.getElementById("ps_" + device);
    if (sel != null) {
        document.getElementById("card_" + device).style.height = "268px"
    }
}


// Comportamiento de los selects para elegir el Power strip
function Selects_ps_behaviour(select_ps, token, url_send, url_recieve) {
    if (select_ps.selectedIndex.value != "None") {
        select_ps.style.width = "402px"
    }

    select_ps.onfocus = function() {
        this.size = 3;
    }

    select_ps.onblur = function() {
        this.size = 1;
    }

    select_ps.onchange = function() {
        this.size = 1;
        this.blur()

        //Por spacios delante y atras del string. No puedo coger el valor poque en nombre son espacios lo reconoce mal
        PowerStripN = this[this.selectedIndex].innerHTML;
        if (PowerStripN == " No Power Strip ") {
            PowerStripName = "None"
        } else {
            Withoutlastsapce = PowerStripN.slice(0, -1);
            PowerStripName = Withoutlastsapce.slice(1);
        }

        DeviceName = this.id.slice(3);

        $.ajax({
            type: "POST",
            url: url_send,
            data: { "csrfmiddlewaretoken": token, 'DeviceName': DeviceName, 'PowerStripName': PowerStripName },

            beforeSend: function() {
                $("#loading-overlay").show();
            },

            success: function(data) {
                if (data.response == 'ok') {
                    $("#loading-overlay").hide();
                    Alert_modal("Associated power strip and device.", url_recieve);
                } else if (data.response == "oktonone") {
                    $("#loading-overlay").hide();
                    Alert_modal("The device is not associated with the power strip anymore.", url_recieve);
                }
            },

            error: function(data) {
                $("#loading-overlay").hide();
                Alert_modal("An error occurred.", "");
            }
        });
    }
}

// Comportamiento de los selects para elegir el socket
function Selects_sk_behaviour(select_sk, token, url_send, url_recieve) {

    select_sk.onfocus = function() {
        this.size = 3;
    }

    select_sk.onblur = function() {
        this.size = 1;
    }

    select_sk.onchange = function() {
        this.size = 1;
        this.blur()

        sk = this[this.selectedIndex].value;
        DeviceName = this.id.slice(10);

        $.ajax({
            type: "POST",
            url: url_send,
            data: { "csrfmiddlewaretoken": token, 'DeviceName': DeviceName, 'sk': sk },

            beforeSend: function() {
                $("#loading-overlay").show();
            },

            success: function(data) {
                if (data.response == 'ok') {
                    $("#loading-overlay").hide();
                    Alert_modal("Associated socket and device.", url_recieve);
                } else if (data.response == "skexist") {
                    $("#loading-overlay").hide();
                    Alert_modal("There is already a device associated to that socket.", url_recieve);
                } else if (data.response == "oktonone") {
                    $("#loading-overlay").hide();
                    Alert_modal("The device is not associated with the socket anymore.", url_recieve);
                }
            },

            error: function(data) {
                Alert_modal("An error occurred.", "");
            }
        });

    };
}


//Boton mostrar el modal para añadir regletas y variar si tiene wifi o no
function Add_powestrip_modal() {
    $('#AddPowerstipModal').modal('show');

    $('.ip_powerstrip').hide();
    $('.device_powerstrip').show();
    $('#device_powerstrip').attr('required', '');


    $('#type_connect').click(function() {
        $('.ip_powerstrip')[this.checked ? "show" : "hide"]();
        $('.device_powerstrip')[this.checked ? "hide" : "show"]();
        if (this.checked) {
            $('#ip_powerstrip').attr('required', '');
            $('#pin').attr('required', '');
            $('#device_powerstrip').removeAttr('required');
        } else {
            $('#ip_powerstrip').removeAttr('required');
            $('#pin').removeAttr('required');
            $('#device_powerstrip').attr('required', '');
        }
    });
}

//Funcion añadir regletas
function Add_ps(e, token, url_send, url_recieve) {
    e.preventDefault();
    $.ajax({
        type: "POST",
        url: url_send,
        data: {
            "csrfmiddlewaretoken": token,
            'name': $('#name').val(),
            'sockets': $('#sockets').val(),
            'type_connect': document.getElementById("type_connect").checked,
            'ip_powerstrip': $('#ip_powerstrip').val(),
            'pin': $('#pin').val(),
            'device_powerstrip': $('#device_powerstrip').val()
        },

        success: function(data) {
            if (data.response == 'ok') {
                $('#AddPowerstipModal').modal('hide');
                Alert_modal("Added power strip", url_recieve);
            } else if (data.response == "existname") {
                Alert_modal("Detected a power strip with the same name.<br/> Impossible to have 2 power strips with the same name.", "");
            } else if (data.response == "existip") {
                Alert_modal("Detected a power strip with the same Ip.<br/> Impossible to have 2 power strips with the same Ip.", "");
            } else if (data.response == "existdevice") {
                Alert_modal("Detected a power strip connected in the same device.<br/> Impossible to have 2 power strips connected to the same device.", "");
            }
        },

        error: function(data) {
            $('#AddPowerstipModal').modal('hide');
            Alert_modal("An error occurred.", "");
        }
    });
}


//Show modal delete
function Delete_powestrip_modal(token, url_send, List) { // Obtener PS y mostrar en el modal
    $.ajax({
        type: "GET",
        url: url_send,
        data: { "csrfmiddlewaretoken": token },

        success: function(data) {
            let ps_list = data.ps; //Power strips base datos
            $('#psm').empty(); //Desplegable
            $('#psList').empty(); //mostrar
            List = []


            ps_list.map(ps => {
                $('#psm').append($('<option>', {
                    value: ps,
                    text: ps
                }));
            });

            $('#DeletePowerstipModal').modal('show');
        },

        error: function(data) {
            Alert_modal("An error occurred", "", "");
        }
    });
}

//Funciones botones dentro del modal
function Add_list_delete(List) {
    $('#psm').val() != 'None' && !List.includes($('#psm').val()) ? List.push($('#psm').val()) : null;

    $('#psList').html(''); //Meter en prelista ps

    List.map((ps) => {
        $('#psList').append('<li class="list-group-item">' + ps + '</li>');
    });
}

function removeItemList(arr, value) {
    var index = arr.indexOf(value);
    if (index > -1) {
        arr.splice(index, 1);
    }
    return arr;
}

function Delete_list_delete(List) {
    $('#psm').val() != 'None' && List.includes($('#psm').val()) ? removeItemList(List, $('#psm').val()) : null;

    $('#psList').html(''); //Sacar en prelista ps
    List.map((ps) => {
        $('#psList').append('<li class="list-group-item">' + ps + '</li>');
    });

}

//Boton borrar dentro del modal
function Delete_ps(e, token, url_send, url_recieve, List) {
    e.preventDefault();
    if (List.length === 0) {
        Alert_modal("There are 0 power strips seleccted.<br/> Nothing to delete.", "");
    } else {
        $.ajax({
            type: "POST",
            url: url_send,
            data: { "csrfmiddlewaretoken": token, 'psList': List },

            beforeSend: function() {
                $("#loading-overlay").show();
                $('#DeletePowerstipModal').modal('hide');
            },

            success: function(data) {
                if (data.response == 'ok') {
                    $("#loading-overlay").hide();
                    Alert_modal("Deleted power strips", url_recieve);
                }
            },

            error: function(data) {
                $("#loading-overlay").hide();
                Alert_modal("An error occurred.", "");
            }
        });
    }
}


//Boton encender todos (boton On) Si ya esta encendido lo deja
function On_all(token, url_send, url_recieve) {
    $.ajax({
        type: "POST",
        url: url_send,
        data: { "csrfmiddlewaretoken": token, 'state': "on" },

        beforeSend: function() {
            $("#loading-overlay").show();
        },

        success: function(data) {

            if (data.response == "empty") {
                $("#loading-overlay").hide();
                Alert_modal('No devices detected.', "");
            } else {
                elements = ""
                for (let s in data.dict_ps) {
                    if (data.dict_ps[s] != "ok") {
                        elements = elements + "- " + s + ": " + data.dict_ps[s] + ".<br/>";
                    }
                }
                $("#loading-overlay").hide();

                if (elements === "") {
                    Alert_modal('All devices were turn on.', url_recieve);
                } else {
                    Alert_modal('All possible devices were turn on but:<br/>' + elements, url_recieve);
                }
            }
        },

        error: function(data) {
            $("#loading-overlay").hide();
            Alert_modal("Some power strip may be off, the sockets could not be turned on.", "");
        }
    });

}

//Boton encender todos (boton On) Si ya esta encendido lo deja
function Off_all(token, url_send, url_recieve) {
    $.ajax({
        type: "POST",
        url: url_send,
        data: { "csrfmiddlewaretoken": token, 'state': "off" },

        beforeSend: function() {
            $("#loading-overlay").show();
        },

        success: function(data) {

            if (data.response == "empty") {
                $("#loading-overlay").hide();
                Alert_modal('No devices detected.', "");
            } else {
                elements = ""
                for (let s in data.dict_ps) {
                    if (data.dict_ps[s] != "ok") {
                        elements = elements + "- " + s + ": " + data.dict_ps[s] + ".<br/>";
                    }
                }
                $("#loading-overlay").hide();

                if (elements === "") {
                    Alert_modal('All devices were turn off.', url_recieve);
                } else {
                    Alert_modal('All possible devices were turn off but:<br/>' + elements, url_recieve);
                }
            }
        },

        error: function(data) {
            $("#loading-overlay").hide();
            Alert_modal("Some power strip may be off, the sockets could not be turned off.", "");
        }
    });

}


// boton apagar y encender de cada device (boton On/off) onclick="On_Off_Single(this)"
function On_Off_Single(device, token, url_send, url_recieve) {
    $.ajax({
        type: "POST",
        url: url_send,
        data: { "csrfmiddlewaretoken": token, 'device': device },

        beforeSend: function() {
            $("#loading-overlay").show();
        },

        success: function(data) {
            if (data.response == "ok") {
                $("#loading-overlay").hide();
                window.location.href = url_recieve;
            } else {
                $("#loading-overlay").hide();
                Alert_modal("" + data.response, "");
            }
        },

        error: function(data) {
            $("#loading-overlay").hide();
            Alert_modal("The power strip may be off, the socket could not be turned.", "");
        }
    });
}


// Boton para comprobar si esta siendo usado o apagado individualmente (Boton connect individual)
function Connect(device, DeviceName, token, url_send, url_recieve) {
    $.ajax({
        type: "GET",
        url: url_send,
        data: { "csrfmiddlewaretoken": token, 'PortName': device },

        success: function(data) {
            if (data.response == "OK") {
                $('#ModalLabelConnect').html('Connecting to ' + DeviceName + ' with:');
                document.getElementById("Portnamehidden").value = device;
                document.getElementById("Devicenamehidden").value = DeviceName;

                $('#ConnectModal').modal('show');

            } else {
                if (data.response == "FOUND ACTIVE") {
                    Alert_modal("An attempt was made to connect to the " + DeviceName + " but:<br/><br/>" + "Another User (" + data.email_user + ") is connected to this device.<br/>The connection has been open for " + data.time_elapsed + " of 1 hour maximum.", "");
                } else if (data.response == "Device is off") {
                    Alert_modal("An attempt was made to connect to the " + DeviceName + " but:<br/><br/>" + data.response, url_recieve);
                } else if (data.response == "Device is None") {
                    Alert_modal("An attempt was made to connect to the " + DeviceName + " but:<br/><br/> The state of the device is unknown.", url_recieve);
                }
            }
        },

        error: function(data) {
            Alert_modal("Error checking access (Busy or off).", "");
        }
    });
};