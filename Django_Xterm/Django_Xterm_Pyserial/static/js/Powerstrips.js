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


//Modal para las alertas y, en el caso que sea necessario, actualizar pagina
function Alert_modal(text, address, close) {
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
    } else if (close === "close") {
        $('#modal-alert').on('hidden.bs.modal', function() {
            window.close();
        })
    }
}


//Eliminar todos los Power Strips
function Delete_All_powestrip_modal(token, url_send) {
    $.ajax({
        type: "POST",
        url: url_send,
        data: { "csrfmiddlewaretoken": token },

        beforeSend: function() {
            $("#loading-overlay").show();
        },

        success: function(data) {
            if (data.response == 'ok') {
                $("#loading-overlay").hide();
                window.opener.location.reload(false); //Actualizar ventan principal
                Alert_modal("Deleted all power strips.", "", "close");
            } else if (data.response == 'nops') {
                $("#loading-overlay").hide();
                Alert_modal("There are no power strips.", "", "");
            }
        },

        error: function(data) {
            $("#loading-overlay").hide();
            Alert_modal("An error occurred.", "", "");
        }
    });
}


//Mostrar modal edit
function Show_modal_edit() {
    let row = this.parentNode.parentNode;
    let name = row.getElementsByTagName("td")[1].textContent;
    let sockets = row.getElementsByTagName("td")[2].textContent;
    let wifi = row.getElementsByTagName("td")[3].textContent;
    let connected = row.getElementsByTagName("td")[4].textContent;
    let Ip = row.getElementsByTagName("td")[5].textContent;
    let Pin = row.getElementsByTagName("td")[6].textContent;

    $('#name').val(name);
    $('#sockets').val(sockets);
    if (wifi == "True") {
        $("#type_connect").prop("checked", true);
        $('#ip_powerstrip').val(Ip);
        $('#pin').val(Pin);

        $('.device_powerstrip').hide();
        $('.ip_powerstrip').show();

        $('#ip_powerstrip').attr('required', '');
        $('#pin').attr('required', '');
        $('#device_powerstrip').removeAttr('required');
    } else {
        $('#device_powerstrip').val(connected);
        $('.ip_powerstrip').hide();
        $('.device_powerstrip').show();

        $('#ip_powerstrip').removeAttr('required');
        $('#pin').removeAttr('required');
        $('#device_powerstrip').attr('required', '');
    }

    $('#EditPowerstipModal').modal('show');
    $('#ModalLabel').html('Editing power strip ' + name);

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

    return false; // Para que no siga al enlace
}

//Boton del modal para editar regletas
function Edit_ps(e, token, url_send, url_recieve) {
    e.preventDefault();
    $.ajax({
        type: "POST",
        url: url_send,
        data: {
            "csrfmiddlewaretoken": token,
            'ant_name': document.getElementById('ModalLabel').innerHTML.slice(20),
            'name': $('#name').val(),
            'type_connect': document.getElementById("type_connect").checked,
            'ip_powerstrip': $('#ip_powerstrip').val(),
            'pin': $('#pin').val(),
            'device_powerstrip': $('#device_powerstrip').val()
        },

        success: function(data) {
            if (data.response == 'ok') {
                $('#EditPowerstipModal').modal('hide');
                window.opener.location.reload(false); //Actualizar ventana principal
                Alert_modal("Edited power strip", url_recieve, "");
            } else if (data.response == "existname") {
                Alert_modal("Detected a power strip with the same name.<br/> Impossible to have 2 power strips with the same name.", "", "");
            } else if (data.response == "existip") {
                Alert_modal("Detected a power strip with the same Ip.<br/> Impossible to have 2 power strips with the same Ip.", "", "");
            } else if (data.response == "existdevice") {
                Alert_modal("Detected a power strip connected in the same device.<br/> Impossible to have 2 power strips connected to the same device.", "", "");
            }
        },

        error: function(data) {
            $('#EditPowerstipModal').modal('hide');
            Alert_modal("An error occurred.", "", "");
        }
    });
}